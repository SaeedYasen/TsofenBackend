import os
import requests
from dotenv import load_dotenv

load_dotenv()

def add_client(business_id, name, surname, country_code, area_code, number, email):
    url = "https://apiv2.gbooking.ru/rpc"
    headers = {"Content-Type": "application/json"}

    payload = {
        "jsonrpc": "2.0",
        "id": 18,
        "cred": {
            "token": os.getenv("GBOOKING_TOKEN"),
            "user": os.getenv("GBOOKING_USER")
        },
        "method": "client.add_client",
        "params": {
            "business": {"id": business_id},
            "client": {
                "name": name,
                "surname": surname,
                "phone": [{
                    "country_code": country_code,
                    "area_code": area_code,
                    "number": number
                }],
                "email": [email]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
