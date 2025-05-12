from fastapi import APIRouter, UploadFile, File, HTTPException, status,Depends
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.docstore import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from uuid import uuid4
import whisper
import torch
import faiss
import os
from dotenv import load_dotenv
import asyncio
import tempfile
from pydantic import BaseModel, HttpUrl
from typing import Optional, List

load_dotenv()

video_router = APIRouter(
    prefix="/video-qa",
    tags=["Video Question Answering"]
)

# Initialize models and embeddings
model_name = "sentence-transformers/all-mpnet-base-v2"
device = "cuda" if torch.cuda.is_available() else "cpu"
embeddings = HuggingFaceEmbeddings(
    model_name=model_name, 
    model_kwargs={"device": device}, 
    encode_kwargs={"normalize_embeddings": False}
)

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0.8,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY"),
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200, 
    chunk_overlap=200
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert explainer of video content. Context: {context}"""),
    ("user", "{question}")
])

# Pydantic models
class VideoInput(BaseModel):
    url: Optional[HttpUrl] = None

class VideoQARequest(BaseModel):
    question: str
    video_id: str

class VideoQAResponse(BaseModel):
    answer: str
    context: Optional[List[str]] = None

class VideoUploadResponse(BaseModel):
    video_id: str
    transcript: str
    message: str

# Global store for video vectors
video_stores = {}

async def transcribe_video(file_path: str) -> str:
    model = whisper.load_model("small").to(device)
    result = model.transcribe(file_path)
    return result["text"]

@video_router.post("/upload", response_model=VideoUploadResponse,dependencies=[Depends(SupabaseAuthBearer())])
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.endswith((".mp4", ".mov", ".avi")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported formats: mp4, mov, avi"
        )

    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        # Transcribe
        transcript = await transcribe_video(temp_path)
        os.remove(temp_path)

        # Process transcript
        docs = [Document(page_content=transcript)]
        chunks = text_splitter.split_documents(docs)

        # Create vector store
        index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

        video_id = str(uuid4())
        ids = [str(uuid4()) for _ in range(len(chunks))]
        vector_store.add_documents(documents=chunks, ids=ids)
        
        video_stores[video_id] = vector_store

        return VideoUploadResponse(
            video_id=video_id,
            transcript=transcript,
            message="Video processed successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing video: {str(e)}"
        )

@video_router.post("/process-youtube", response_model=VideoUploadResponse,dependencies=[Depends(SupabaseAuthBearer())])
async def process_youtube(video_input: VideoInput):
    if not video_input.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="YouTube URL is required"
        )

    try:
        # Load YouTube transcript
        loader = YoutubeLoader.from_youtube_url(
            str(video_input.url), 
            add_video_info=False
        )
        transcript = loader.load()
        docs = [Document(page_content=entry.page_content) for entry in transcript]
        chunks = text_splitter.split_documents(docs)

        # Create vector store
        index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )

        video_id = str(uuid4())
        ids = [str(uuid4()) for _ in range(len(chunks))]
        vector_store.add_documents(documents=chunks, ids=ids)
        
        video_stores[video_id] = vector_store

        return VideoUploadResponse(
            video_id=video_id,
            transcript="\n".join(doc.page_content for doc in docs),
            message="YouTube video processed successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing YouTube video: {str(e)}"
        )

@video_router.post("/ask", response_model=VideoQAResponse,dependencies=[Depends(SupabaseAuthBearer())])
async def ask_video(request: VideoQARequest):
    if request.video_id not in video_stores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    try:
        vector_store = video_stores[request.video_id]
        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 2}
        )

        # Retrieve context
        retrieved_docs = retriever.invoke(request.question)
        context = "\n".join(doc.page_content for doc in retrieved_docs)

        # Create chain and execute
        chain = prompt | llm | StrOutputParser()
        answer = await chain.ainvoke({
            "question": request.question,
            "context": context
        })

        return VideoQAResponse(
            answer=answer,
            context=[doc.page_content for doc in retrieved_docs]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating answer: {str(e)}"
        )