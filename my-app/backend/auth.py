from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    db = current_app.db
    if db.users.find_one({"username": username}):
        return jsonify({"msg": "Username already exists"}), 400

    db.users.insert_one({"username": username, "password": password})
    return jsonify({"msg": "User created successfully"}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    

    db = current_app.db
    user = db.users.find_one({"username": username})
    if user and user["password"] == password:
        access_token = create_access_token(identity=username, expires_delta=timedelta(hours=1))
        return jsonify({"token": access_token}), 200

    return jsonify({"msg": "Invalid credentials"}), 401

@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"msg": f"Welcome {current_user}!"}), 200
