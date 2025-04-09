from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import openai
import requests
from auth import auth  # Ensure you have an auth.py that defines your authentication blueprint

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure JWT for authentication
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "supersecretkey")
jwt = JWTManager(app)

# Set up MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
app.db = client["mydatabase"]

# Get external API keys from environment variables
GBOOKING_API_KEY = os.getenv("GBOOKING_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

# Register the auth blueprint with a URL prefix
app.register_blueprint(auth, url_prefix="/auth")

# ------------------------------------------------------------------------------
# Endpoint for ChatGPT interaction
# ------------------------------------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Call OpenAI's ChatGPT API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}],
        )
        reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------------------------
# Endpoint to retrieve available appointments from the GBooking API
# ------------------------------------------------------------------------------
@app.route("/appointments", methods=["GET"])
def appointments():
    try:
        headers = {
            "Authorization": f"Bearer {GBOOKING_API_KEY}",
            "Content-Type": "application/json"
        }
        url = "https://sandbox.gbooking.com/api/appointments"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return jsonify({
                "error": "Failed to fetch appointments",
                "details": response.text
            }), response.status_code

        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------------------------
# Endpoint to book an appointment via the GBooking API
# ------------------------------------------------------------------------------
@app.route("/book", methods=["POST"])
def book():
    try:
        data = request.json
        patient_name = data.get("patientName")
        doctor_id = data.get("doctorId")
        time_slot = data.get("timeSlot")

        if not all([patient_name, doctor_id, time_slot]):
            return jsonify({"error": "Missing required booking details"}), 400

        headers = {
            "Authorization": f"Bearer {GBOOKING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "patient": patient_name,
            "doctor_id": doctor_id,
            "time": time_slot
        }
        url = "https://sandbox.gbooking.com/api/book"
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code not in (200, 201):
            return jsonify({
                "error": "Booking failed",
                "details": response.text
            }), response.status_code

        return jsonify({"confirmation": response.json()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------------------------
# (Optional) Endpoint to cancel an appointment via the GBooking API
# ------------------------------------------------------------------------------
@app.route("/cancel", methods=["POST"])
def cancel():
    try:
        data = request.json
        appointment_id = data.get("appointmentId")
        if not appointment_id:
            return jsonify({"error": "Missing appointment ID"}), 400

        headers = {
            "Authorization": f"Bearer {GBOOKING_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"appointment_id": appointment_id}
        url = "https://sandbox.gbooking.com/api/cancel"
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            return jsonify({
                "error": "Cancellation failed",
                "details": response.text
            }), response.status_code

        return jsonify({"cancellation": response.json()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

