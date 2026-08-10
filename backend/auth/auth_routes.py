from flask import Blueprint, request, jsonify
from .email_password import register_user, login_user

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    register_user(email, password)
    return jsonify({"message": "registered"}), 201

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    token = login_user(email, password)
    if not token:
        return jsonify({"error": "invalid"}), 400
    return jsonify({"token": token}), 200
