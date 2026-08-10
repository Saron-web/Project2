from flask import Flask
from auth.auth_routes import auth
from api_endpoints import api

app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(api, url_prefix="/api")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
