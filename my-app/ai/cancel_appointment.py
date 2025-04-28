# ai/cancel_appointment.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GBOOKING_TOKEN = os.getenv("GBOOKING_TOKEN")
GBOOKING_USER = os.getenv("GBOOKING_USER")

def cancel_appointment_by_client(appointment_id, client_id):
    url = "https://apiv2.gbooking.ru/rpc"
    headers = {"Content-Type": "application/json"}

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "cred": {
            "token": GBOOKING_TOKEN,
            "user": GBOOKING_USER
        },
        "method": "appointment.cancel_appointment_by_client",
        "params": {
            "appointment": {
                "id": appointment_id
            },
            "client": {
                "clientID": client_id
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
