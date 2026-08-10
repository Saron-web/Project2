import requests
from flask import request, redirect
import jwt
import datetime

client_id = "your_github_client_id"
client_secret = "your_github_client_secret"
 # redirect_uri = 
secret = "your_jwt_secret"

def github_login():
    url = (
        # github authorization URL
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&scope=user:email"
    )
    return redirect(url)

def github_callback():
    code = request.args.get("code")
   # github token URL
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri
    }
    headers = {"Accept": "application/json"}
    r = requests.post(token_url, data=data, headers=headers).json()
    access_token = r.get("access_token")

    user_info = requests.get(
       # github user info URL
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    email = user_info.get("email")
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, secret, algorithm="HS256")
