from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from auth import auth  # استيراد ملف المصادقة

# تحميل متغيرات البيئة
load_dotenv()

app = Flask(__name__)

# إعداد مفتاح JWT من .env
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "supersecretkey")  
jwt = JWTManager(app)

# تسجيل Blueprint للمصادقة
app.register_blueprint(auth, url_prefix="/auth")

if __name__ == "__main__":
    app.run(debug=True)