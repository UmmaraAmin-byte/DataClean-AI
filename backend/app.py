from flask import Flask, jsonify  # Import jsonify to return JSON responses
from flask_cors import CORS  # Import CORS
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes (allows frontend on port 3000 to make requests)
CORS(app)

# Load environment variables
load_dotenv()

# Get the MongoDB URI from the environment variable
mongo_uri = os.getenv("MONGO_URI")

# Initialize MongoDB client with URI
client = MongoClient(mongo_uri)

# Connect to your database
db = client.get_database("Database1")  # Explicitly set your database name

# Route for the homepage
@app.route('/')
def home():
    return "Hello, World!"

# Route to fetch users from the database
@app.route('/api/users', methods=['GET'])
def get_users():
    collection = db.Users  # Explicitly use your collection name
    users = list(collection.find({}, {"_id": 0}))  # Exclude '_id' from response
    return jsonify({"users": users})  # Convert the result to JSON and return it

# Route to add a new user to the database
@app.route('/add_user')
def add_user():
    collection = db.Users  # Explicitly use your collection name
    new_user = {"name": "John Doe", "email": "johndoe@example.com"}
    collection.insert_one(new_user)  # Insert new user into the database
    return "User added!"

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
