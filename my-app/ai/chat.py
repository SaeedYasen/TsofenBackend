from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv
from flask_jwt_extended import jwt_required
from ai.chat_ai_selector import ai_conversation_with_patient, fuzzy_find
from ai.get_profile_by_id import get_all_services_and_doctors
from ai.get_closest_date import get_closest_available_date
from ai.get_available_slots_on_day import get_available_slots_on_day, get_all_available_slots_on_day,is_booking_confirmed_by_patient
from ai.appointment_reserve_appointment import reserve_appointment
from ai.add_client import add_client
from ai.confirm_appointment import client_confirm_appointment
from ai.cancel_appointment import cancel_appointment_by_client

import os
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

chat_bp = Blueprint('chat_bp', __name__)
chat_session = {}  # لكل session_id نخزن بيانات مؤقتة
def is_cancellation_intent(message):
    prompt = f"""
    هل الجملة التالية تعني أن المستخدم يريد إلغاء موعد؟ أجب فقط نعم أو لا.
    الجملة: "{message}"
    """
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    reply = completion.choices[0].message.content.strip().lower()
    return reply.startswith("نعم")

@chat_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze_message():
    data = request.get_json()
    message = data.get("message", "")
    session_id = data.get("session_id", "default")

    if not message:
        return jsonify({"error": "❌ يرجى إدخال رسالة."}), 400
    # --- مرحلة فحص إذا نية المريض هي الإلغاء ---
    if session_id in chat_session and "appointment_id" in chat_session[session_id] and "client_id" in chat_session[session_id]:
        if is_cancellation_intent(message):
            session = chat_session.pop(session_id)
            cancel_response = cancel_appointment_by_client(session["appointment_id"], session["client_id"])
            if "result" in cancel_response:
                return jsonify({"message": "✅ تم إلغاء الموعد بنجاح."})
            else:
                return jsonify({"error": "❌ فشل في إلغاء الموعد.", "details": cancel_response})

    # =====================
    # 🧠 المرحلة 3: التعامل مع تأكيد الحجز أو تغيير التاريخ
    # =====================
    if session_id in chat_session and "date" in chat_session[session_id] and "time" in chat_session[session_id]:
        session = chat_session[session_id]

        # المستخدم طلب تاريخ جديد
        if session.get("awaiting_date_input") or (":" in message and "date" in session):
            from datetime import datetime

            selected_input = message.strip()

# لو كتب ساعة وليس تاريخ
            if ":" in selected_input:
                selected_time = selected_input
                if "date" not in session or not session["date"]:
                    return jsonify({"message": "❌ لم يتم تحديد تاريخ. الرجاء كتابة تاريخ أولاً."})

                available_slots = get_all_available_slots_on_day(
                    session["business_id"],
                    session["service_id"],
                    session["resource_id"],
                    session["date"].split("T")[0]
                )

                if selected_time in available_slots:
                    from flask_jwt_extended import get_jwt_identity
                    current_user = get_jwt_identity()
                    db = current_app.db
                    user = db.users.find_one({"username": current_user})
                    if not user:
                        return jsonify({"error": "⚠️ لم يتم العثور على بيانات المستخدم"}), 404

                    client_response = add_client(
                        business_id=session["business_id"],
                        name=user.get("name", ""),
                        surname=user.get("surname", ""),
                        country_code=user.get("country_code", ""),
                        area_code=user.get("area_code", ""),
                        number=user.get("number", ""),
                        email=user.get("email", "")
                    )
                    client_id = client_response.get("result", {}).get("client", {}).get("id")
                    if not client_id:
                        return jsonify({"error": "❌ فشل في إنشاء العميل", "details": client_response})

                    booking_response = reserve_appointment(
                        session["business_id"],
                        session["service_id"],
                        session["resource_id"],
                        session["date"].split("T")[0],
                        selected_time
                    )
                    if not booking_response or "result" not in booking_response:
                        return jsonify({"error": "❌ فشل في حجز الموعد", "details": booking_response})

                    appointment_id = booking_response["result"]["appointment"]["id"]

                    confirm_response = client_confirm_appointment(appointment_id, client_id)
                    chat_session.pop(session_id)

                    if "result" in confirm_response:
                        return jsonify({
                            "message": "✅ تم حجز الموعد بنجاح.",
                            "appointment_id": appointment_id,
                            "client_id": client_id
                        })
                    else:
                        return jsonify({
                            "message": "⚠️ تم حجز الموعد ولكن فشل تأكيد الحجز.",
                            "details": confirm_response
                        })
                else:
                    return jsonify({
                        "message": "❌ هذه الساعة غير متاحة، الرجاء اختيار ساعة من القائمة."
                    })

# لو كتب تاريخ
            try:
                if "-" in selected_input:
                    parts = selected_input.split("-")
                    if len(parts[0]) != 4:
                        selected_input = datetime.strptime(selected_input, "%d-%m-%Y").strftime("%Y-%m-%d")
            except Exception as e:
                return jsonify({"error": f"⚠️ صيغة التاريخ غير صحيحة. الرجاء كتابة التاريخ بشكل صحيح (مثال: 2025-05-05).", "details": str(e)})

            available_slots = get_all_available_slots_on_day(
                session["business_id"],
                session["service_id"],
                session["resource_id"],
                selected_input
            )

            if available_slots:
                chat_session[session_id]["date"] = f"{selected_input}T00:00:00Z"
                chat_session[session_id]["time"] = available_slots[0]
                chat_session[session_id].pop("awaiting_date_input", None)

                formatted_slots = []
                for slot in available_slots:
                    if isinstance(slot, str) and ":" in slot:
                        formatted_slots.append(slot)
                    else:
                        try:
                            hour = int(slot)
                            formatted_slots.append(f"{hour:02d}:00")
                        except:
                            pass

                return jsonify({
                    "message": f"🕑 هذه المواعيد المتاحة يوم {selected_input}:\n- " + "\n- ".join(formatted_slots) + "\n\n❓ أي ساعة تناسبك؟ اكتبها كما هي."
                })
            else:
                return jsonify({
                    "message": "❌ لا توجد ساعات متاحة في هذا اليوم. الرجاء اختيار يوم آخر."
                })


        # المستخدم وافق أو رفض الموعد المقترح
        if is_booking_confirmed_by_patient(message):
            data = chat_session.pop(session_id)

            # إضافة العميل
            from flask_jwt_extended import get_jwt_identity
            current_user = get_jwt_identity()
            db = current_app.db
            user = db.users.find_one({"username": current_user})
            if not user:
                return jsonify({"error": "⚠️ لم يتم العثور على بيانات المستخدم"}), 404

            client_response = add_client(
                business_id=data["business_id"],
                name=user.get("name", ""),
                surname=user.get("surname", ""),
                country_code=user.get("country_code", ""),
                area_code=user.get("area_code", ""),
                number=user.get("number", ""),
                email=user.get("email", "")
            )
            client_id = client_response.get("result", {}).get("client", {}).get("id")
            if not client_id:
                return jsonify({"error": "❌ فشل في إنشاء العميل", "details": client_response})

            # حجز الموعد
            booking_response = reserve_appointment(
                data["business_id"],
                data["service_id"],
                data["resource_id"],
                data["date"].split("T")[0],
                data["time"]
            )
            if not booking_response or "result" not in booking_response:
                return jsonify({"error": "❌ فشل في حجز الموعد", "details": booking_response})

            appointment_id = booking_response["result"]["appointment"]["id"]

            # تأكيد الموعد
            confirm_response = client_confirm_appointment(appointment_id, client_id)
            if "result" in confirm_response:
                return jsonify({
                    "message": "✅ تم تأكيد حجز الموعد بنجاح.",
                    "appointment_id": appointment_id,
                    "client_id": client_id
                })
            else:
                return jsonify({
                    "message": "⚠️ تم حجز الموعد لكن فشل تأكيد الحجز.",
                    "details": confirm_response
                })
        else:
            # لم يوافق، نطلب منه اختيار تاريخ
            chat_session[session_id]["awaiting_date_input"] = True
            return jsonify({
                "message": "📅 الرجاء كتابة تاريخ يناسبك بالشكل (yyyy-mm-dd). مثال: 2025-05-01"
            })

    # =====================
    # 🧠 المرحلة 2: اختيار الطبيب
    # =====================
    if session_id in chat_session and "service_id" in chat_session[session_id] and "doctors" in chat_session[session_id]:
        doctor_name = message.strip()
        index = get_all_services_and_doctors()
        options = [doc for doc in index if doc["service_id"] == chat_session[session_id]["service_id"]]
        matched_doc = fuzzy_find(doctor_name, options, "doctor_name")
        if matched_doc:
            closest_date = get_closest_date = get_closest_available_date(
                matched_doc["business_id"],
                matched_doc["service_id"],
                matched_doc["resource_id"]
            )
            first_slot = None
            if closest_date:
                day = closest_date.split("T")[0]
                first_slot = get_available_slots_on_day(
                    matched_doc["business_id"],
                    matched_doc["service_id"],
                    matched_doc["resource_id"],
                    day
                )

            chat_session[session_id] = {
                **matched_doc,
                "date": closest_date,
                "time": first_slot
            }

            return jsonify({
                "business_id": matched_doc["business_id"],
                "service_id": matched_doc["service_id"],
                "resource_id": matched_doc["resource_id"],
                "doctor_name": matched_doc["doctor_name"],
                "closest_available_date": closest_date or "❌ لا يوجد مواعيد متاحة حاليًا",
                "first_available_slot": first_slot or "❌ لا يوجد ساعات متاحة",
                "message": f"❓ هل ترغب بحجز موعد مع {matched_doc['doctor_name']} يوم {day} الساعة {first_slot}؟ (نعم/لا)"
            })
        return jsonify({"error": "⚠️ الطبيب غير موجود في القائمة."})

    # =====================
    # 🧠 المرحلة 1: تحليل الطبيب والخدمة
    # =====================
    result = ai_conversation_with_patient(message)

    if "doctors" in result:
        doctors_list = result["doctors"]
        if len(doctors_list) == 1:
            doctor = doctors_list[0]
            closest_date = get_closest_available_date(
                doctor["business_id"],
                doctor["service_id"],
                doctor["resource_id"]
            )
            first_slot = None
            if closest_date:
                day = closest_date.split("T")[0]
                first_slot = get_available_slots_on_day(
                    doctor["business_id"],
                    doctor["service_id"],
                    doctor["resource_id"],
                    day
                )

            chat_session[session_id] = {
                **doctor,
                "date": closest_date,
                "time": first_slot
            }

            return jsonify({
                "business_id": doctor["business_id"],
                "service_id": doctor["service_id"],
                "resource_id": doctor["resource_id"],
                "doctor_name": doctor["doctor_name"],
                "closest_available_date": closest_date or "❌ لا يوجد مواعيد متاحة حاليًا",
                "first_available_slot": first_slot or "❌ لا يوجد ساعات متاحة",
                "message": f"✅ تم اختيار الطبيب: {doctor['doctor_name']}.\n📅 أقرب موعد: يوم {day} الساعة {first_slot}.\n❓ هل يناسبك هذا الموعد؟ (نعم/لا)"
            })

        else:
            chat_session[session_id] = {
                "business_id": result["business_id"],
                "service_id": result["service_id"],
                "doctors": doctors_list
            }
            return jsonify(result)

    elif "resource_id" in result:
        chat_session[session_id] = {
            "business_id": result["business_id"],
            "service_id": result["service_id"],
            "resource_id": result["resource_id"],
            "date": result.get("closest_available_date"),
            "time": get_available_slots_on_day(
                result["business_id"],
                result["service_id"],
                result["resource_id"],
                result.get("closest_available_date", "").split("T")[0] if result.get("closest_available_date") else None
            )
        }
        return jsonify(result)

    return jsonify(result)
