import os 

from pylate import models 
from huggingface_hub import login

from dotenv import load_dotenv

load_dotenv()

login(token=os.getenv("HUGGINGFACE_TOKEN"))

model = models.ColBERT(model_name_or_path="lightonai/GTE-ModernColBERT-v1")


