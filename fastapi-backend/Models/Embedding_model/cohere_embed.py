import os 

from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = CohereEmbeddings(
    model="embed-v4.0",
    cohere_api_key=os.getenv("COHERE_API_KEY"),
    )

