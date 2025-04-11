# chat.py
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from openai import OpenAI

chat_bp = Blueprint("chat", __name__)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def correct_spelling(user_message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "قم فقط بتصحيح الأخطاء الإملائية في الجملة التالية، وأعدها دون أي تغيير في المعنى:"},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content.strip()

def detect_intent(user_message):
    if any(word in user_message.lower() for word in ["حجز", "أريد موعد", "احجز لي"]):
        return "booking"
    elif any(word in user_message.lower() for word in ["إلغاء", "الغي", "الغاء", "إلغاء موعد"]):
        return "cancellation"
    elif any(word in user_message.lower() for word in ["مواعيد متاحة", "أقرب موعد", "ما هي المواعيد"]):
        return "availability"
    else:
        return "general"

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    original_message = data.get("message", "")
    corrected_message = correct_spelling(original_message)
    intent = detect_intent(corrected_message)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"أنت مساعد طبي رقمي. يمكنك تقديم معلومات طبية والإجابة على أسئلة حول المواعيد الطبية"},
            {"role": "user", "content": corrected_message}
        ]
    )

    chat_response = response.choices[0].message.content

    if intent == "booking":
        return jsonify({"response": chat_response, "next_step": "يرجى تحديد الطبيب والخدمة المطلوبة لإتمام الحجز."})
    elif intent == "cancellation":
        return jsonify({"response": chat_response, "next_step": "يرجى تقديم تفاصيل الموعد الذي تريد إلغاؤه."})
    elif intent == "availability":
        return jsonify({"response": chat_response, "next_step": "هل لديك طبيب معين أو خدمة طبية تبحث عنها؟"})
    else:
        return jsonify({"response": chat_response})
