from fastapi import APIRouter, UploadFile, File, HTTPException, status,Depends
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.docstore import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.schema import StrOutputParser
from uuid import uuid4
import faiss
import os
from dotenv import load_dotenv
import asyncio
import tempfile
from pydantic import BaseModel
from auth.middleware import SupabaseAuthBearer
from typing import List, Optional

load_dotenv()

document_router = APIRouter(
    prefix="/document-qa",
    tags=["Document Question Answering"]
)

# Initialize models and embeddings
model_name = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0.8,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY"),
)

# Pydantic models
class DocumentQARequest(BaseModel):
    question: str
    document_id: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    page_count: int
    message: str

class DocumentQAResponse(BaseModel):
    answer: str
    context: Optional[List[str]] = None

# Global store for document vectors (in production use Redis/DB)
document_stores = {}

@document_router.post("/upload", 
    response_model=DocumentUploadResponse, 
    dependencies=[Depends(SupabaseAuthBearer())]
)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        # Process PDF
        loader = PyMuPDFLoader(temp_path)
        documents = loader.load()
        os.remove(temp_path)

        # Split and embed
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n"], 
            chunk_size=1200, 
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        embedding_dim = len(embeddings.embed_query("hello world"))
        index = faiss.IndexFlatL2(embedding_dim)
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        
        doc_id = str(uuid4())
        ids = [str(uuid4()) for _ in range(len(chunks))]
        vector_store.add_documents(chunks, ids=ids)
        
        for idx, chunk_id in enumerate(ids):
            vector_store.index_to_docstore_id[idx] = chunk_id

        document_stores[doc_id] = vector_store

        return DocumentUploadResponse(
            document_id=doc_id,
            page_count=len(documents),
            message="Document processed successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@document_router.post("/ask", response_model=DocumentQAResponse,dependencies=[Depends(SupabaseAuthBearer())])
async def ask_document(request: DocumentQARequest):
    if request.document_id not in document_stores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    try:
        vector_store = document_stores[request.document_id]
        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 3}
        )

        # Retrieve context
        retrieved_docs = retriever.invoke(request.question)
        context = "\n".join(doc.page_content for doc in retrieved_docs)

        # Create prompt and chain
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert document analyst. Answer questions based on: {context}"""),
            ("human", "{question}")
        ])
        
        chain = prompt_template | llm | StrOutputParser()
        
        # Run chain asynchronously
        answer = await chain.ainvoke({
            "question": request.question,
            "context": context
        })

        return DocumentQAResponse(
            answer=answer,
            context=[doc.page_content for doc in retrieved_docs]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating answer: {str(e)}"
        )