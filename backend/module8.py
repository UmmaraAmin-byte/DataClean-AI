from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from datetime import datetime
import csv  # For CSV processing
import json  # Importing json module
from bson import ObjectId  # For ObjectId serialization
from flask import Blueprint

module8_bp = Blueprint('module8', __name__)
CORS(module8_bp)  # Enable CORS for this blueprint
# Load environment variables
load_dotenv()

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Configurations
app.config['UPLOAD_FOLDER'] = './uploads'  # Ensure this folder exists
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'json'}

# MongoDB Client
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Initialize MongoDB client and check the connection
client = None
db = None
files_collection = None

try:
    client = MongoClient(MONGO_URI)
    client.server_info()  # Validate connection on startup
    db = client["dataclean_ai"]  # Database name
    files_collection = db["files"]  # Collection for storing file metadata
    print("Connected to MongoDB successfully.")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    db, files_collection = None, None

# Utility Functions
def allowed_file(filename):
    """Check if file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Custom JSON serializer for ObjectId
class JSONEncoderCustom(json.JSONEncoder):
    def default(self, obj):
        """Convert ObjectId to string for JSON serialization."""
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Set custom JSON encoder globally
app.json_encoder = JSONEncoderCustom


# Example route for module 8
@module8_bp.route('/example', methods=['GET'])
def example():
    return jsonify({"message": "Module 8 works!"}), 200


# M8-UC1: Upload Dataset
@app.route('/api/data/upload', methods=['POST'])
def upload_dataset():
    """Upload and process dataset."""

    # Ensure the database and collection are properly initialized
    if db is None or files_collection is None:
        return jsonify({"status": "error", "message": "Database connection or collection is not initialized."}), 500

    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400

    if allowed_file(file.filename):
        try:
            # Save the file locally
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Parse CSV file and insert data into MongoDB
            rows = []
            if filename.lower().endswith('.csv'):
                with open(filepath, 'r') as csvfile:
                    csvreader = csv.DictReader(csvfile)
                    rows = list(csvreader)  # Read all rows into a list of dictionaries

                    # Debugging: Log parsed rows
                    print("Parsed CSV rows:", rows)

                    # Validate and insert data into MongoDB
                    for row in rows:
                        # Simple validation: Check for required fields
                        if 'Series_reference' not in row or 'Period' not in row:
                            print(f"Invalid row: {row}")
                            continue  # Skip invalid rows

                    # Ensure the collection exists before inserting data
                    if rows:
                        # Make sure db and dataimport collection are valid
                        if db is not None and db.get_collection('dataimport') is not None:
                            db.dataimport.insert_many(rows)
                        else:
                            print("Database or collection is not properly initialized.")
                            return jsonify({"status": "error", "message": "Database or collection is not initialized."}), 500

            # Save file metadata in MongoDB
            file_metadata = {
                "filename": filename,
                "filepath": filepath,
                "uploaded_at": datetime.utcnow(),
                "row_count": len(rows) if filename.lower().endswith('.csv') else 0
            }

            if db is not None:
                result = files_collection.insert_one(file_metadata)
                file_metadata["_id"] = str(result.inserted_id)  # Convert ObjectId to string

            return jsonify({
                "status": "success",
                "message": "File uploaded and data saved successfully",
                "metadata": file_metadata
            }), 200

        except Exception as e:
            return jsonify({"status": "error", "message": f"File upload failed: {str(e)}"}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid file type. Allowed types: csv, xlsx, json."}), 400

# M8-UC2: Connect to External Databases
@app.route('/api/data/connect-database', methods=['POST'])
def connect_to_database():
    """Connect to an external MongoDB database."""
    connection_string = request.json.get('connection_string')
    try:
        # Test connection to the external database
        external_client = MongoClient(connection_string)
        external_client.server_info()  # Validate connection
        return jsonify({"status": "success", "message": "Connected to external database"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# M8-UC3: Track Import Progress
@app.route('/api/data/import-progress', methods=['GET'])
def track_import_progress():
    try:
        if not files_collection:
            raise Exception("Database not initialized.")
        
        total_files = files_collection.count_documents({})
        progress = {
            "status": "complete" if total_files > 0 else "no_import",
            "total_files": total_files
        }
        return jsonify({"status": "success", "data": progress}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error fetching import progress: {str(e)}"}), 500

# M8-UC4: Handle Import Failures
@app.route('/api/data/import-failures', methods=['POST'])
def import_failures():
    failure_details = request.json.get('details', "Unknown error occurred")
    return jsonify({
        "status": "error",
        "message": "Import failed",
        "details": failure_details,
        "suggestions": "Check file format and retry"
    }), 400

# M8-UC5: View Imported Data
@app.route('/api/data/view-imported', methods=['GET'])
def view_imported_data():
    try:
        files = list(files_collection.find({}, {"_id": 0}))  # Fetch all files without MongoDB's _id field
        for file in files:
            file['document_id'] = str(file.get('_id'))  # Convert _id to string manually if not already done
        return jsonify({"status": "success", "data": files}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# M8-UC6: Schedule Imports
@app.route('/api/data/schedule-import', methods=['POST'])
def schedule_import():
    """Schedule a data import."""
    try:
        time = request.json.get('time')
        if not time:
            return jsonify({"status": "error", "message": "Invalid schedule time."}), 400

        schedule_entry = {
            "time": datetime.strptime(time, "%Y-%m-%dT%H:%M:%S"),
            "scheduled_at": datetime.utcnow(),
        }

        if db is not None:
            db.scheduled_imports.insert_one(schedule_entry)  # Save schedule

        return jsonify({"status": "success", "message": "Import scheduled successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to schedule import: {str(e)}"}), 500

# M8-UC7: View Scheduled Imports
@app.route('/api/data/view-scheduled-imports', methods=['GET'])
def view_scheduled_imports():
    """Fetch scheduled imports."""
    try:
        if db is None:
            return jsonify({"status": "error", "message": "Database connection is not initialized."}), 500

        schedules = list(db.scheduled_imports.find())
        return jsonify({"status": "success", "data": schedules}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error fetching schedules: {str(e)}"}), 500

# M8-UC8: Database Connection Status
@app.route('/api/data/database-status', methods=['GET'])
def database_status():
    """Check the database connection status."""
    try:
        if client is None:
            return jsonify({"status": "error", "message": "Database connection is not established."}), 500
        client.server_info()  # Will raise an exception if MongoDB is down
        return jsonify({"status": "success", "message": "Database connection is healthy."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to connect to the database: {str(e)}"}), 500

# Add a Home Route
@app.route('/')
def home():
    return "Welcome to the Data Clean AI API!"