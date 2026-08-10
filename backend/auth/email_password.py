import bcrypt
import jwt
import datetime

secret = "your_jwt_secret"
users = {}

def register_user(email, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[email] = {"email": email, "password": hashed}
    return True

def login_user(email, password):
    user = users.get(email)
    if not user:
        return None
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return None
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def verify_token(token):
    return jwt.decode(token, secret, algorithms=["HS256"])
