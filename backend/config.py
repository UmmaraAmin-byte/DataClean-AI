import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Ummara:<ummara7860>@datacleanai.oxc3l.mongodb.net/datafiles?retryWrites=true&w=majority&appName=DataCleanAI")
    UPLOAD_FOLDER = './uploads'  # Folder for locally saved uploads
