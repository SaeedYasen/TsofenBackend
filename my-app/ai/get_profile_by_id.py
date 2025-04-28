import os
import json
import requests
from dotenv import load_dotenv
from ai.get_network_data import get_business_ids_from_network

# --- تحميل المتغيرات ---
load_dotenv()
GBOOKING_TOKEN = os.getenv("GBOOKING_TOKEN")
GBOOKING_USER = os.getenv("GBOOKING_USER")


# --- دالة تعرض الخدمات والأطباء بشكل مطبوع ---
def get_business_profiles():
    url = "https://apiv2.gbooking.ru/rpc"
    headers = {'Content-Type': 'application/json'}

    business_ids = get_business_ids_from_network()

    for business_id in business_ids:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "cred": {
                "token": GBOOKING_TOKEN,
                "user": GBOOKING_USER
            },
            "method": "business.get_profile_by_id",
            "params": {
                "business": {
                    "id": business_id
                },
                "with_networks": True,
                "worker_sorting_type": "workload"
            }
        })

        response = requests.post(url, headers=headers, data=payload)
        data = response.json()

        if "result" not in data:
            print(f"\n❌ Failed to fetch profile for Business ID: {business_id}")
            continue

        result = data.get("result", {})
        business_name = result.get("business", {}).get("general_info", {}).get("name", "فرع بدون اسم")

        print(f"\n==============================")
        print(f"🏥 Business Name: {business_name}")
        print(f"🆔 Business ID: {business_id}")

        services = result.get("business", {}).get("taxonomies", [])
        workers = result.get("business", {}).get("resources", [])

        if not services:
            print("🚫 No services found.")
            continue

        service_map = {}
        for service in services:
            if service.get("active"):
                service_name = service.get("alias", {}).get("he-il") or service.get("alias", {}).get("en-us") or "بدون اسم"
                sid = service.get("id")
                service_map[sid] = service_name

        service_doctors = {}
        for doc in workers:
            if (
                not doc.get("name") or
                doc.get("status") != "ACTIVE" or
                not doc.get("timetable", {}).get("active")
            ):
                continue
            worker_name = f"{doc.get('name', '')} {doc.get('surname', '')}".strip()
            for sid in doc.get("taxonomies", []):
                service_name = service_map.get(sid)
                if service_name:
                    if service_name not in service_doctors:
                        service_doctors[service_name] = []
                    service_doctors[service_name].append(worker_name)

        for service_name, doctor_list in service_doctors.items():
            print(f"\n🛎️ الخدمة: {service_name}")
            print("👨‍⚕️ الأطباء:")
            for doc_name in doctor_list:
                print(" -", doc_name)

        print(f"==============================")


# --- دالة تستخدم للذكاء الاصطناعي: ترجع كل الخدمات والأطباء بصيغة قابلة للبحث ---
def get_all_services_and_doctors():
    url = "https://apiv2.gbooking.ru/rpc"
    headers = {'Content-Type': 'application/json'}
    business_ids = get_business_ids_from_network()
    all_data = []

    for business_id in business_ids:
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "cred": {
                "token": GBOOKING_TOKEN,
                "user": GBOOKING_USER
            },
            "method": "business.get_profile_by_id",
            "params": {
                "business": {
                    "id": business_id
                },
                "with_networks": True,
                "worker_sorting_type": "workload"
            }
        })

        response = requests.post(url, headers=headers, data=payload)
        data = response.json()

        if "result" not in data:
            continue

        result = data["result"]
        services = result.get("business", {}).get("taxonomies", [])
        workers = result.get("business", {}).get("resources", [])
        business_name = result.get("business", {}).get("general_info", {}).get("name", "")

        service_map = {}
        for service in services:
            if service.get("active"):
                sid = service.get("id")
                name = service.get("alias", {}).get("he-il") or service.get("alias", {}).get("en-us")
                service_map[sid] = name

        for doc in workers:
            if (
                not doc.get("name") or
                doc.get("status") != "ACTIVE" or
                not doc.get("timetable", {}).get("active")
            ):
                continue

            doc_name = f"{doc.get('nickname', '')} {doc.get('name', '')} {doc.get('surname', '')}".strip()
            for sid in doc.get("taxonomies", []):
                service_name = service_map.get(sid)
                if service_name:
                    all_data.append({
                        "business_id": business_id,
                        "service_id": sid,
                        "service_name": service_name,
                        "doctor_name": doc_name,
                        "resource_id": doc["id"],
                        "clinic": business_name
                    })

    return all_data


# --- للتجربة فقط ---
if __name__ == "__main__":
    get_business_profiles()
    # data = get_all_services_and_doctors()
    # print(json.dumps(data, indent=2, ensure_ascii=False))
