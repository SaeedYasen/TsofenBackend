# gbooking_utils.py

import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
GBOOKING_TOKEN = os.getenv("GBOOKING_TOKEN")
GBOOKING_USER = os.getenv("GBOOKING_USER")
GBOOKING_NETWORK_ID = os.getenv("GBOOKING_NETWORK_ID")
def get_business_ids_from_network():
    url = "https://apiv2.gbooking.ru/rpc"
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "cred": {
            "token": GBOOKING_TOKEN,
            "user": GBOOKING_USER
        },
        "method": "business.get_network_data",
        "params": {
            "networkID": int(GBOOKING_NETWORK_ID)
        }
    })

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()

        if "result" in data and "businesses" in data["result"]:
            business_ids = [b["businessID"] for b in data["result"]["businesses"]]
            print("✅ Business IDs found:", business_ids)
            return business_ids
        else:
            print("❌ Could not find businesses in the response.")
            return []

    except Exception as e:
        print("❌ Error while fetching business IDs:", e)
        return []
