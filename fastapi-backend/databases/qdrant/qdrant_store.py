import os 

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("QDRANT_URI")
api_key = os.getenv("QDRANT_API_KEY")
# qdrant_store = QdrantVectorStore.from_documents(
#    [],
#     [],
#     qdrant_client,
#     prefer_grpc=True,
#     collection_name="my_documents" )

qdrant_client = QdrantClient(
    url=url,
    api_key=api_key
)
print(qdrant_client)