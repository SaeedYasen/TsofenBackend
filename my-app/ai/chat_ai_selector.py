# chat_ai_selector.py

import os
import json
import difflib
from dotenv import load_dotenv
from openai import OpenAI
from ai.get_profile_by_id import get_all_services_and_doctors

# تحميل المفاتيح
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


# --- جلب البيانات من GBooking API ---
def build_search_index():
    return get_all_services_and_doctors()

# --- دالة للبحث الذكي ---
def fuzzy_find(query, options, key):
    names = [opt[key] for opt in options]
    matches = difflib.get_close_matches(query, names, n=1, cutoff=0.4)
    if matches:
        for opt in options:
            if opt[key] == matches[0]:
                return opt
    return None


# --- الدالة الرئيسية للتحدث مع AI وتحديد الطبيب والخدمة ---
def ai_conversation_with_patient(message):
    index = build_search_index()

    # تحليل نية المستخدم باستخدام GPT
    prompt = f"""
    من الجملة التالية، استخرج فقط اسم الخدمة المطلوبة واسم الطبيب إن وُجد، بدون شرح.
    الجملة: "{message}"
    الرد يجب أن يكون بصيغة JSON مثل: 
    {{
      "service": "تنظيف أسنان",
      "doctor": "د. ساهر عابد"
    }}
    إذا لم يتم ذكر دكتور، اجعل doctor = null.
    وإذا طلب المستخدم أقرب موعد بدون تحديد طبيب، أضف الحقل "auto_select_doctor": true
    """
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    content = completion.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)
        service_query = parsed.get("service")
        doctor_query = parsed.get("doctor")
        auto_select = parsed.get("auto_select_doctor", False)
    except:
        return {"error": "❌ فشل في تحليل الرد من الذكاء الاصطناعي."}

    # البحث في البيانات
    matched_service = fuzzy_find(service_query, index, "service_name")
    if not matched_service:
        return {"error": "🚫 لم يتم العثور على الخدمة المطلوبة."}

    if doctor_query:
        matched_doctor = fuzzy_find(doctor_query, [i for i in index if i["service_name"] == matched_service["service_name"]], "doctor_name")
        if matched_doctor:
            return {
                "business_id": matched_doctor["business_id"],
                "service_id": matched_doctor["service_id"],
                "resource_id": matched_doctor["resource_id"]
            }
        else:
            return {"error": "⚠️ تم العثور على الخدمة ولكن لم يتم العثور على الطبيب المحدد."}
    else:
        # المستخدم لم يحدد طبيب
        matching_doctors = [i for i in index if i["service_id"] == matched_service["service_id"]]
        
        if len(matching_doctors) == 1 or auto_select:
            selected = matching_doctors[0]
            return {
                "business_id": selected["business_id"],
                "service_id": selected["service_id"],
                "resource_id": selected["resource_id"],
                "note": "✅ تم اختيار الطبيب تلقائيًا لأن المستخدم لم يحدد طبيبًا."
            }
        else:
            # نطلب منه يختار طبيب
            doctor_names = list(set(doc["doctor_name"] for doc in matching_doctors))
            return {
                "business_id": matched_service["business_id"],
                "service_id": matched_service["service_id"],
                "doctors": doctor_names,
                "message": "🩺 هل تود اختيار طبيب من القائمة أم أختار لك أول طبيب متاح؟"
            }




# --- مثال للتجربة ---
if __name__ == "__main__":
    msg = input("🗣️ اكتب رسالتك (مثال: بدي تنظيف أسنان عند د. ساهر):\n")
    result = ai_conversation_with_patient(msg)
    print("✅ النتيجة:", result)
