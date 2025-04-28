import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GBOOKING_TOKEN = os.getenv("GBOOKING_TOKEN")
GBOOKING_USER = os.getenv("GBOOKING_USER")

def get_closest_available_date(business_id, service_id, resource_id):
    url = "https://crac-prod3.gbooking.ru/rpc"
    headers = {"Content-Type": "application/json"}
    GBOOKING_TOKEN = os.getenv("GBOOKING_TOKEN")
    GBOOKING_USER = os.getenv("GBOOKING_USER")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "cred": {
        },
        "method": "Crac.CRACResourcesFreeByDateV2",
        "params": [
            {
                "business": {"id": business_id},
                "taxonomy": {"id": service_id},
                "resources": [resource_id],
                "duration": 60,
                "durations": [60, 15],
                "location": "Europe/Moscow"
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if "result" in data and "Free" in data["result"]:
            free_dates = data["result"]["Free"]
            if free_dates:
                return free_dates[0]["date"]

        return None
    except Exception as e:
        return f"❌ فشل في جلب المواعيد: {str(e)}"
