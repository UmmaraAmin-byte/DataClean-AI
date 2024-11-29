from pymongo import MongoClient
from config import Config

# MongoDB Client
client = MongoClient(Config.MONGO_URI)
db = client.datafiles  # Use the `datafiles` database

# FileUpload model
class FileUpload:
    def __init__(self, filename, file_path, upload_time):
        self.filename = filename
        self.file_path = file_path
        self.upload_time = upload_time

    def save_to_db(self):
        collection = db.dataimport  # Use the `dataimport` collection
        file_data = {
            "filename": self.filename,
            "file_path": self.file_path,
            "upload_time": self.upload_time
        }
        # Handle duplicates based on filename
        if not collection.find_one({"filename": self.filename}):
            collection.insert_one(file_data)
            return {"status": "success", "message": "File uploaded successfully"}
        else:
            return {"status": "error", "message": "Duplicate record detected"}

    @staticmethod
    def get_all_files():
        collection = db.dataimport
        return list(collection.find({}, {"_id": 0, "filename": 1, "file_path": 1, "upload_time": 1}))
