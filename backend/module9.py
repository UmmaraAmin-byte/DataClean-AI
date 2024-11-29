from flask import Blueprint, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
from pymongo import MongoClient
import numpy as np

module9_bp = Blueprint('module9', __name__)
CORS(module9_bp)  # Enable CORS for this blueprint

# MongoDB client setup
client = MongoClient("mongodb://localhost:27017/")
db = client["data_cleaning_db"]
module9_collection = db["module9"]

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def log_action(file_id, action, details):
    module9_collection.update_one(
        {"file_id": file_id},
        {"$push": {"actions_log": {"action": action, "details": details, "timestamp": datetime.now()}}}
    )

def update_progress(file_id, status):
    module9_collection.update_one(
        {"file_id": file_id},
        {"$set": {"status": status, "last_updated": datetime.now()}}
    )

@module9_bp.route('/api/module9/import', methods=['POST'])
def import_data():
    file = request.files.get('file')
    if not file:
        return jsonify({"status": "error", "message": "No file provided."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        data = pd.read_csv(file_path)
        file_id = str(datetime.timestamp(datetime.now()))

        module9_collection.insert_one({
            "file_id": file_id,
            "file_path": file_path,
            "imported_at": datetime.now(),
            "status": "Imported",
            "actions_log": []
        })

        update_progress(file_id, "Imported")
        log_action(file_id, "Import", {"file_name": file.filename})

        return jsonify({"status": "success", "file_id": file_id}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500




# Example route for module 9
@module9_bp.route('/example', methods=['GET'])
# Example route for module 9
@module9_bp.route('/example', methods=['GET'])
def example():
    return jsonify({"message": "Module 9 works!"}), 200


@module9_bp.route('/api/module9/remove_duplicates', methods=['POST'])
def remove_duplicates():
    file_id = request.json.get('file_id')
    if not file_id:
        return jsonify({"status": "error", "message": "File ID is required."}), 400

    file_record = module9_collection.find_one({"file_id": file_id})
    if not file_record:
        return jsonify({"status": "error", "message": "File not found."}), 404

    try:
        data = pd.read_csv(file_record['file_path'])
        before_count = len(data)
        data = data.drop_duplicates()
        after_count = len(data)
        duplicate_count = before_count - after_count

        data.to_csv(file_record['file_path'], index=False)

        update_progress(file_id, "Duplicates Removed")
        log_action(file_id, "Remove Duplicates", {"duplicates_removed": duplicate_count})

        return jsonify({"status": "success", "duplicates_removed": duplicate_count}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@module9_bp.route('/api/module9/fill_missing', methods=['POST'])
def fill_missing():
    file_id = request.json.get('file_id')
    strategy = request.json.get('strategy', 'mean')  # Default to 'mean'

    if not file_id:
        return jsonify({"status": "error", "message": "File ID is required."}), 400

    file_record = module9_collection.find_one({"file_id": file_id})
    if not file_record:
        return jsonify({"status": "error", "message": "File not found."}), 404

    try:
        # Load the dataset
        data = pd.read_csv(file_record['file_path'])

        # Handle missing data based on the strategy
        if strategy == 'mean':
            data.fillna(data.mean(), inplace=True)
        elif strategy == 'median':
            data.fillna(data.median(), inplace=True)
        elif strategy == 'mode':
            data.fillna(data.mode().iloc[0], inplace=True)
        else:
            return jsonify({"status": "error", "message": "Invalid strategy."}), 400

        # Save the updated data
        data.to_csv(file_record['file_path'], index=False)

        # Log the action
        update_progress(file_id, "Missing Data Filled")
        log_action(file_id, "Fill Missing", {"strategy": strategy})

        return jsonify({"status": "success", "message": f"Missing data filled using {strategy} strategy."}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@module9_bp.route('/api/module9/normalize', methods=['POST'])
def normalize_data():
    file_id = request.json.get('file_id')

    if not file_id:
        return jsonify({"status": "error", "message": "File ID is required."}), 400

    file_record = module9_collection.find_one({"file_id": file_id})
    if not file_record:
        return jsonify({"status": "error", "message": "File not found."}), 404

    try:
        data = pd.read_csv(file_record['file_path'])
        numeric_columns = data.select_dtypes(include=['number']).columns
        data[numeric_columns] = (data[numeric_columns] - data[numeric_columns].mean()) / data[numeric_columns].std()

        data.to_csv(file_record['file_path'], index=False)

        update_progress(file_id, "Data Normalized")
        log_action(file_id, "Normalize Data", {"normalized_columns": list(numeric_columns)})

        return jsonify({"status": "success", "normalized_columns": list(numeric_columns)}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@module9_bp.route('/api/module9/detect_outliers', methods=['POST'])
def detect_outliers():
    file_id = request.json.get('file_id')
    if not file_id:
        return jsonify({"status": "error", "message": "File ID is required."}), 400

    file_record = module9_collection.find_one({"file_id": file_id})
    if not file_record:
        return jsonify({"status": "error", "message": "File not found."}), 404

    try:
        data = pd.read_csv(file_record['file_path'])
        numeric_columns = data.select_dtypes(include=['number']).columns
        outlier_info = {}

        for col in numeric_columns:
            z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
            outliers = data[z_scores > 3]
            outlier_info[col] = len(outliers)

        log_action(file_id, "Detect Outliers", {"outliers_detected": outlier_info})
        update_progress(file_id, "Outliers Detected")

        return jsonify({"status": "success", "outliers_detected": outlier_info}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@module9_bp.route('/api/module9/progress', methods=['GET'])
def track_cleaning_progress():
    file_id = request.args.get('file_id')
    if not file_id:
        return jsonify({"status": "error", "message": "File ID is required."}), 400

    progress = module9_collection.find_one({"file_id": file_id})
    if not progress:
        return jsonify({"status": "error", "message": "No progress found for this file."}), 404

    return jsonify({"status": "success", "progress": progress}), 200
