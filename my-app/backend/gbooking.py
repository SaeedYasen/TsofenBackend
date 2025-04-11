from flask import Blueprint, request, jsonify
import requests

gbooking = Blueprint('gbooking', __name__)

# بيانات الاعتماد الخاصة بك
USER_ID = "67e16cc60060fd13c16c02af"
API_TOKEN = "2e8540408eb49cb569f21ed52dcc8ae8ad5f8f1b"
NETWORK_ID = 456

# الرؤوس المستخدمة في الطلبات
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# ✅ جلب العيادات
@gbooking.route('/clinics', methods=['GET'])
def get_clinics():
    url = "https://api.gbooking.ru/clinic/get_clinics"
    payload = {
        "user": USER_ID,
        "network_ids": [NETWORK_ID]
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    return jsonify(response.json())

# ✅ جلب الخدمات
@gbooking.route('/services', methods=['POST'])
def get_services():
    data = request.get_json()
    url = "https://api.gbooking.ru/service/get_services"
    payload = {
        "user": USER_ID,
        "clinic_ids": [data.get("clinic_id")]
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    return jsonify(response.json())

# ✅ جلب الموظفين (الأطباء)
@gbooking.route('/staff', methods=['POST'])
def get_staff():
    data = request.get_json()
    url = "https://api.gbooking.ru/staff/get_staffs"
    payload = {
        "user": USER_ID,
        "clinic_id": data.get("clinic_id")
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    return jsonify(response.json())

# ✅ التحقق من المواعيد المتاحة
@gbooking.route('/availability', methods=['POST'])
def get_availability():
    data = request.get_json()
    url = "https://api.gbooking.ru/timeslots/get_available_timeslots"
    payload = {
        "user": USER_ID,
        "clinic_id": data.get("clinic_id"),
        "service_id": data.get("service_id"),
        "staff_id": data.get("staff_id"),
        "from": data.get("from"),
        "to": data.get("to")
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    return jsonify(response.json())

# ✅ إنشاء موعد جديد
@gbooking.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    url = "https://api.gbooking.ru/appointment/create"
    payload = {
        "user": USER_ID,
        "network_id": NETWORK_ID,
        "client": {
            "name": data.get("name"),
            "phone": data.get("phone")
        },
        "appointment": {
            "clinic_id": data.get("clinic_id"),
            "service_id": data.get("service_id"),
            "staff_id": data.get("staff_id"),
            "datetime": data.get("datetime")
        }
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    return jsonify(response.json())

# ✅ إلغاء موعد
@gbooking.route('/appointments/cancel', methods=['POST'])
def cancel_appointment():
    data = request.get_json()
    url = "https://api.gbooking.ru/appointment/cancel"
    payload = {
        "user": USER_ID,
        "appointment_id": data.get("appointment_id")
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    return jsonify(response.json())
# from flask import Blueprint, request, jsonify
# import httpx

# gbooking = Blueprint('gbooking', __name__)

# # بيانات الاعتماد الخاصة بك
# USER_ID = "67e16cc60060fd13c16c02af"
# API_TOKEN = "2e8540408eb49cb569f21ed52dcc8ae8ad5f8f1b"
# NETWORK_ID = 456

# # الرؤوس
# HEADERS = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {API_TOKEN}"
# }

# # 🔁 دالة طلب موحد باستخدام httpx
# def post_to_gbooking(url, payload):
#     try:
#         with httpx.Client(verify=False, http2=True, timeout=15.0) as client:
#             response = client.post(url, json=payload, headers=HEADERS)
#             response.raise_for_status()
#             return jsonify(response.json())
#     except httpx.HTTPStatusError as e:
#         return jsonify({"error": "HTTP error", "details": str(e)}), 500
#     except httpx.RequestError as e:
#         return jsonify({"error": "Connection error", "details": str(e)}), 500

# # ✅ جلب العيادات
# @gbooking.route('/clinics', methods=['GET'])
# def get_clinics():
#     url = "https://api.gbooking.ru/clinic/get_clinics"
#     payload = {
#         "user": USER_ID,
#         "network_ids": [NETWORK_ID]
#     }
#     return post_to_gbooking(url, payload)

# # ✅ جلب الخدمات
# @gbooking.route('/services', methods=['POST'])
# def get_services():
#     data = request.get_json()
#     url = "https://api.gbooking.ru/service/get_services"
#     payload = {
#         "user": USER_ID,
#         "clinic_ids": [data.get("clinic_id")]
#     }
#     return post_to_gbooking(url, payload)

# # ✅ جلب الموظفين
# @gbooking.route('/staff', methods=['POST'])
# def get_staff():
#     data = request.get_json()
#     url = "https://api.gbooking.ru/staff/get_staffs"
#     payload = {
#         "user": USER_ID,
#         "clinic_id": data.get("clinic_id")
#     }
#     return post_to_gbooking(url, payload)

# # ✅ التحقق من توفر المواعيد
# @gbooking.route('/availability', methods=['POST'])
# def get_availability():
#     data = request.get_json()
#     url = "https://api.gbooking.ru/timeslots/get_available_timeslots"
#     payload = {
#         "user": USER_ID,
#         "clinic_id": data.get("clinic_id"),
#         "service_id": data.get("service_id"),
#         "staff_id": data.get("staff_id"),
#         "from": data.get("from"),
#         "to": data.get("to")
#     }
#     return post_to_gbooking(url, payload)

# # ✅ إنشاء موعد
# @gbooking.route('/appointments', methods=['POST'])
# def create_appointment():
#     data = request.get_json()
#     url = "https://api.gbooking.ru/appointment/create"
#     payload = {
#         "user": USER_ID,
#         "network_id": NETWORK_ID,
#         "client": {
#             "name": data.get("name"),
#             "phone": data.get("phone")
#         },
#         "appointment": {
#             "clinic_id": data.get("clinic_id"),
#             "service_id": data.get("service_id"),
#             "staff_id": data.get("staff_id"),
#             "datetime": data.get("datetime")
#         }
#     }
#     return post_to_gbooking(url, payload)

# # ✅ إلغاء موعد
# @gbooking.route('/appointments/cancel', methods=['POST'])
# def cancel_appointment():
#     data = request.get_json()
#     url = "https://api.gbooking.ru/appointment/cancel"
#     payload = {
#         "user": USER_ID,
#         "appointment_id": data.get("appointment_id")
#     }
#     return post_to_gbooking(url, payload)
