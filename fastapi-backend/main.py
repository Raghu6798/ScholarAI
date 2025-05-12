from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Models.Embedding_model.text_embedding_model import model
from loguru import logger
from routes.document_qa_route import document_router
from routes.visual_qa_route import image_router
from routes.video_qa_route import video_router

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(document_router)
app.include_router(image_router)
app.include_router(video_router)