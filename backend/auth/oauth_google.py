import requests
from flask import request, redirect
import jwt
import datetime

client_id = "your_google_client_id"
client_secret = "your_google_client_secret"
redirect_uri = "http://localhost:5000/auth/google/callback"
secret = "your_jwt_secret"

def google_login():
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&scope=email%20profile"
    )
    return redirect(url)

def google_callback():
    code = request.args.get("code")
    #   token_url = add the link here
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    r = requests.post(token_url, data=data).json()
    access_token = r.get("access_token")

    user_info = requests.get(
       # add the link here 
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    email = user_info.get("email")
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, secret, algorithm="HS256")
