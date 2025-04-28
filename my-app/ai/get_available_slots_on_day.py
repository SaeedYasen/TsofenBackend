import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

GBOOKING_TOKEN = os.getenv("GBOOKING_TOKEN")
GBOOKING_USER = os.getenv("GBOOKING_USER")
def get_available_slots_on_day(business_id, service_id, resource_id, date):
    url = "https://cracslots.gbooking.ru/rpc"
    headers = {"Content-Type": "application/json"}

    GBOOKING_TOKEN = os.getenv("GBOOKING_TOKEN")
    GBOOKING_USER = os.getenv("GBOOKING_USER")

    from datetime import datetime, timedelta
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    next_day = date_obj + timedelta(days=1)

    date_from = date_obj.strftime("%Y-%m-%dT00:00:00.000Z")
    date_to = next_day.strftime("%Y-%m-%dT00:00:00.000Z")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "cred": {
            "token": GBOOKING_TOKEN,
            "user": GBOOKING_USER
        },
        "method": "CracSlots.GetCRACResourcesAndRooms",
        "params": {
            "business": {
                "id": business_id,
                "widget_configuration": {
                    "cracServer": "CRAC_PROD3",
                    "mostFreeEnable": True
                },
                "general_info": {
                    "timezone": "Europe/Moscow"
                }
            },
            "filters": {
                "resources": [
                    {"id": resource_id, "duration": 15}
                ],
                "taxonomies": [service_id],
                "rooms": [],
                "date": {
                    "from": date_from,
                    "to": date_to
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    try:
        slots = data.get("result", {}).get("slots", [])
        for s in slots:
            for r in s.get("resources", []):
                if r.get("resourceId") == resource_id:
                    cut_slots = r.get("cutSlots", [])
                    if cut_slots:
                        # تحويل أول slot إلى وقت (مثلاً 510 دقيقة = 08:30)
                        first_minutes = cut_slots[0]["start"]
                        hour = first_minutes // 60
                        minute = first_minutes % 60
                        return f"{hour:02d}:{minute:02d}"
        return None
    except Exception as e:
        return f"❌ فشل في جلب الساعات المتاحة: {str(e)}"

from openai import OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def is_booking_confirmed_by_patient(message):
    prompt = f"""
    هل الجملة التالية تعني أن المستخدم يريد تأكيد حجز الموعد؟ فقط أجب بنعم أو لا.
    الجملة: "{message}"
    """
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    reply = completion.choices[0].message.content.strip().lower()
    return reply.startswith("نعم")
def get_all_available_slots_on_day(business_id, service_id, resource_id, date):
    url = "https://cracslots.gbooking.ru/rpc"
    headers = {"Content-Type": "application/json"}

    GBOOKING_TOKEN = os.getenv("GBOOKING_TOKEN")
    GBOOKING_USER = os.getenv("GBOOKING_USER")

    date_obj = datetime.strptime(date, "%Y-%m-%d")
    next_day = date_obj + timedelta(days=1)

    date_from = date_obj.strftime("%Y-%m-%dT00:00:00.000Z")
    date_to = next_day.strftime("%Y-%m-%dT00:00:00.000Z")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "cred": {
            "token": GBOOKING_TOKEN,
            "user": GBOOKING_USER
        },
        "method": "CracSlots.GetCRACResourcesAndRooms",
        "params": {
            "business": {
                "id": business_id,
                "widget_configuration": {
                    "cracServer": "CRAC_PROD3",
                    "mostFreeEnable": True
                },
                "general_info": {
                    "timezone": "Europe/Moscow"
                }
            },
            "filters": {
                "resources": [
                    {"id": resource_id, "duration": 15}
                ],
                "taxonomies": [service_id],
                "rooms": [],
                "date": {
                    "from": date_from,
                    "to": date_to
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    try:
        slots = data.get("result", {}).get("slots", [])
        available_times = []

        for s in slots:
            for r in s.get("resources", []):
                if r.get("resourceId") == resource_id:
                    cut_slots = r.get("cutSlots", [])
                    for slot in cut_slots:
                        minutes = slot["start"]
                        hour = minutes // 60
                        minute = minutes % 60
                        formatted_time = f"{hour:02d}:{minute:02d}"
                        available_times.append(formatted_time)

        return available_times if available_times else None

    except Exception as e:
        return f"❌ فشل في جلب جميع الساعات المتاحة: {str(e)}"

