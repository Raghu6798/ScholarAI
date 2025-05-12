from fastapi import APIRouter, UploadFile, File, HTTPException, status
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.docstore import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from uuid import uuid4
import faiss
import os
from dotenv import load_dotenv
import base64
import httpx
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import mimetypes

load_dotenv()

image_router = APIRouter(
    prefix="/image-qa",
    tags=["Image Question Answering"]
)

model_name = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': False}
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.8,
    verbose=True,
    api_key=os.getenv("GOOGLE_API_KEY")
)

class ImageInput(BaseModel):
    url: Optional[HttpUrl] = None
    base64_image: Optional[str] = None

class ImageQARequest(BaseModel):
    question: str
    image_id: str

class ImageQAResponse(BaseModel):
    answer: str
    context: Optional[List[str]] = None

class ImageUploadResponse(BaseModel):
    image_id: str
    description: str

image_stores = {}

async def process_image(image_data: str, mime_type: str = "image/jpeg") -> str:
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe what is in the image in detail."},
            {"type": "image", "source_type": "base64", "data": image_data, "mime_type": mime_type}
        ]
    }
    response = await llm.ainvoke([message])
    return response.content

@image_router.post("/upload", response_model=ImageUploadResponse,dependencies=[Depends(SupabaseAuthBearer())])
async def upload_image(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = None
):
    try:
        image_data = None
        mime_type = "image/jpeg"

        if file:
            contents = await file.read()
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "image/jpeg"
            image_data = base64.b64encode(contents).decode("utf-8")
        elif url:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                mime_type = response.headers.get("content-type", "image/jpeg")
                image_data = base64.b64encode(response.content).decode("utf-8")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either file or URL must be provided"
            )

        # Process image with Gemini
        description = await process_image(image_data, mime_type)

        knowledge = [Document(page_content=description)]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_documents(knowledge)

        index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

        image_id = str(uuid4())
        ids = [str(uuid4()) for _ in chunks]
        vector_store.add_documents(chunks, ids)

        for idx, doc_id in enumerate(ids):
            vector_store.index_to_docstore_id[idx] = doc_id

        image_stores[image_id] = vector_store

        return ImageUploadResponse(image_id=image_id, description=description)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@image_router.post("/ask", response_model=ImageQAResponse,dependencies=[Depends(SupabaseAuthBearer())])
async def ask_image(request: ImageQARequest):
    if request.image_id not in image_stores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    try:
        vector_store = image_stores[request.image_id]
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})
        retrieved_docs = retriever.invoke(request.question)
        context = "\n".join(doc.page_content for doc in retrieved_docs)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert image analyst. Use this context: {context}"),
            ("human", "{question}")
        ])
        chain = prompt | llm | StrOutputParser()
        answer = await chain.ainvoke({"question": request.question, "context": context})

        return ImageQAResponse(answer=answer, context=[doc.page_content for doc in retrieved_docs])

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating answer: {str(e)}"
        )
