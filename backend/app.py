from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)
CORS(app)

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = None
try:
    client = MongoClient(MONGO_URI)
    client.server_info()  # Validate the connection
    print("Connected to MongoDB successfully.")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    client = None

# Import Blueprints
from module8 import module8_bp  # Import module 8 blueprint
from module9 import module9_bp  # Import module 9 blueprint

# Register Blueprints
app.register_blueprint(module8_bp, url_prefix='/api/module8')
app.register_blueprint(module9_bp, url_prefix='/api/module9')

# Root Route
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Data Clean AI API",
        "modules": {
            "module8": "/api/module8",
            "module9": "/api/module9"
        }
    }), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
