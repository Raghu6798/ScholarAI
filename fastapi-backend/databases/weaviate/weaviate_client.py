import weaviate
from weaviate.classes.init import Auth
from langchain_weaviate.vectorstores import WeaviateVectorStore
import os
from dotenv import load_dotenv 

load_dotenv()

weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]


client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,  # Replace with your Weaviate Cloud URL
    auth_credentials=Auth.api_key(weaviate_api_key),  # Replace with your Weaviate Cloud key
)

weaviate_db = WeaviateVectorStore(client=client,index_name="",text_key="")
print(weaviate_db)