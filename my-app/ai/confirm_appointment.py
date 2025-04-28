import os
import requests
from dotenv import load_dotenv

load_dotenv()

def client_confirm_appointment(appointment_id, client_id):
    url = "https://apiv2.gbooking.ru/rpc"
    headers = {"Content-Type": "application/json"}

    payload = {
        "jsonrpc": "2.0",
        "id": 20,
        "cred": {
            "token": os.getenv("GBOOKING_TOKEN"),
            "user": os.getenv("GBOOKING_USER")
        },
        "method": "appointment.client_confirm_appointment",
        "params": {
            "appointment": {"id": appointment_id},
            "client": {"id": client_id}
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
