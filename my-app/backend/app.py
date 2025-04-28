# app.py
import os
import sys
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv



# أضف مجلد المشروع للجذر حتى يمكن استيراد ai و auth و gbooking
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth import auth

from ai.chat import chat_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "supersecretkey")
jwt = JWTManager(app)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
app.db = client["mydatabase"]

# Register blueprints
app.register_blueprint(auth, url_prefix="/auth")

app.register_blueprint(chat_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)
