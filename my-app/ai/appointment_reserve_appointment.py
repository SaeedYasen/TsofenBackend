import os
import requests
from dotenv import load_dotenv

load_dotenv()

def reserve_appointment(business_id, service_id, resource_id, date, time, duration=15):
    url = "https://apiv2.gbooking.ru/rpc"
    headers = {"Content-Type": "application/json"}

    # تحويل الوقت إلى صيغة ISO
    start_datetime = f"{date}T{time}:00"

    payload = {
        "jsonrpc": "2.0",
        "id": 19,
        "cred": {
            "token": os.getenv("GBOOKING_TOKEN"),
            "user": os.getenv("GBOOKING_USER")
        },
        "method": "appointment.reserve_appointment",
        "params": {
            "appointment": {
                "start": start_datetime,
                "duration": duration,
                "price": {
                    "amount": 0,
                    "currency": "ILS"
                }
            },
            "source": "chatgpt",
            "business": {
                "id": business_id
            },
            "taxonomy": {
                "id": service_id
            },
            "client_appear": "NONE",
            "resource": {
                "id": resource_id
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
