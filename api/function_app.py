import io
import json
import logging
import os
import bcrypt
import jwt
import datetime as dt
import urllib.request
import urllib.parse
from datetime import datetime, timezone

import azure.functions as func
import pandas as pd
import redis
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

app = func.FunctionApp()

# ---------------------------------------------------------------------------
# Configuration — Group 1 (Performance Optimization)
# ---------------------------------------------------------------------------
STORAGE_CONNECTION = os.environ["AzureWebJobsStorage"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_KEY = os.environ["REDIS_KEY"]
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6380"))

DATA_CONTAINER = "data"
RAW_BLOB_NAME = "All_Diets.csv"
CLEAN_BLOB_NAME = "All_Diets_clean.csv"
CACHE_KEY = "insights:latest"

NUMERIC_COLS = ["Protein(g)", "Carbs(g)", "Fat(g)"]
TEXT_COLS = ["Diet_type", "Recipe_name", "Cuisine_type"]


def _redis_client() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_KEY,
        ssl=True,
        decode_responses=True,
        socket_connect_timeout=5,
    )


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip() for c in df.columns]
    for col in TEXT_COLS:
        df[col] = df[col].astype(str).str.strip().str.lower()
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    before = len(df)
    df = df.dropna(subset=NUMERIC_COLS + TEXT_COLS)
    for col in NUMERIC_COLS:
        df = df[df[col] >= 0]
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    logging.info("Cleaning: %d rows in, %d rows out", before, len(df))
    return df


def compute_insights(df: pd.DataFrame) -> dict:
    macro_means = df[NUMERIC_COLS].mean()
    bar_data = {
        "labels": ["Protein", "Carbs", "Fat"],
        "values": [round(float(macro_means[c]), 2) for c in NUMERIC_COLS],
    }
    sample_size = min(300, len(df))
    sample = df.sample(n=sample_size, random_state=42)
    scatter_data = {
        "points": [
            {"x": round(float(r["Protein(g)"]), 2), "y": round(float(r["Carbs(g)"]), 2)}
            for _, r in sample.iterrows()
        ]
    }
    counts = df["Diet_type"].value_counts()
    pie_data = {
        "labels": [str(k) for k in counts.index],
        "values": [int(v) for v in counts.values],
    }
    corr = df[NUMERIC_COLS].corr().round(2)
    heatmap_data = corr.values.tolist()
    return {
        "barData": bar_data,
        "scatterData": scatter_data,
        "pieData": pie_data,
        "heatmapData": heatmap_data,
        "recordCount": int(len(df)),
        "computedAt": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Blob Trigger — fires ONLY when data/All_Diets.csv is created or overwritten
# ---------------------------------------------------------------------------
@app.function_name(name="clean_and_cache_diets")
@app.blob_trigger(arg_name="myblob", path=f"{DATA_CONTAINER}/{RAW_BLOB_NAME}", connection="AzureWebJobsStorage")
def clean_and_cache_diets(myblob: func.InputStream) -> None:
    logging.info("Blob trigger fired for %s (%d bytes)", myblob.name, myblob.length)
    raw_df = pd.read_csv(io.BytesIO(myblob.read()))
    clean_df = clean_dataframe(raw_df)
    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION)
    clean_bytes = clean_df.to_csv(index=False).encode("utf-8")
    blob_service.get_blob_client(container=DATA_CONTAINER, blob=CLEAN_BLOB_NAME).upload_blob(
        clean_bytes, overwrite=True
    )
    logging.info("Wrote %s (%d rows)", CLEAN_BLOB_NAME, len(clean_df))
    insights = compute_insights(clean_df)
    r = _redis_client()
    r.set(CACHE_KEY, json.dumps(insights))
    logging.info("Cached insights to Redis (recordCount=%d)", insights["recordCount"])


# ---------------------------------------------------------------------------
# HTTP Trigger — serves cached insights
# ---------------------------------------------------------------------------
@app.function_name(name="get_nutritional_insights")
@app.route(route="get_nutritional_insights", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_nutritional_insights(req: func.HttpRequest) -> func.HttpResponse:
    start = datetime.now(timezone.utc)
    try:
        r = _redis_client()
        raw = r.get(CACHE_KEY)
        if raw is None:
            raise ValueError("cache empty")
        item = json.loads(raw)
    except Exception as exc:
        logging.warning("Cache read failed: %s", exc)
        return func.HttpResponse(
            json.dumps({"error": "No cached insights yet. Upload All_Diets.csv to trigger the pipeline."}),
            status_code=503,
            mimetype="application/json",
        )
    elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
    response_body = {
        "barData": item["barData"],
        "scatterData": item["scatterData"],
        "pieData": item["pieData"],
        "heatmapData": item["heatmapData"],
        "recordCount": item["recordCount"],
        "cachedAt": item["computedAt"],
        "executionTime": f"{elapsed_ms:.1f}ms (served from cache, no recompute)",
    }
    return func.HttpResponse(json.dumps(response_body), status_code=200, mimetype="application/json")


# ---------------------------------------------------------------------------
# Group 3 — Security & Authentication
# ---------------------------------------------------------------------------
TABLE_NAME = "users"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


def _jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET app setting is not configured")
    return secret


def get_table_client():
    conn_str = os.environ["AzureWebJobsStorage"]
    service = TableServiceClient.from_connection_string(conn_str)
    try:
        service.create_table(TABLE_NAME)
    except ResourceExistsError:
        pass
    return service.get_table_client(TABLE_NAME)


def make_jwt(email: str) -> str:
    now = dt.datetime.utcnow()
    payload = {
        "email": email,
        "iat": now,
        "exp": now + dt.timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def verify_jwt(token: str):
    try:
        return jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_bearer_token(req: func.HttpRequest):
    header = req.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return header.split(" ", 1)[1].strip()


def json_response(payload: dict, status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(payload), status_code=status_code, mimetype="application/json")


@app.route(route="register", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def register(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return json_response({"error": "Invalid JSON body"}, 400)
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not email or "@" not in email:
        return json_response({"error": "a valid email is required"}, 400)
    if len(password) < 8:
        return json_response({"error": "password must be at least 8 characters"}, 400)
    table_client = get_table_client()
    try:
        table_client.get_entity(partition_key="users", row_key=email)
        return json_response({"error": "an account with this email already exists"}, 409)
    except ResourceNotFoundError:
        pass
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    entity = {
        "PartitionKey": "users",
        "RowKey": email,
        "email": email,
        "password_hash": password_hash,
        "auth_provider": "password",
        "created_at": dt.datetime.utcnow().isoformat(),
    }
    table_client.create_entity(entity=entity)
    token = make_jwt(email)
    return json_response({"token": token, "email": email}, 201)


@app.route(route="login", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def login(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return json_response({"error": "Invalid JSON body"}, 400)
    email = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    if not email or not password:
        return json_response({"error": "email and password are required"}, 400)
    table_client = get_table_client()
    try:
        entity = table_client.get_entity(partition_key="users", row_key=email)
    except ResourceNotFoundError:
        return json_response({"error": "invalid email or password"}, 401)
    stored_hash = entity.get("password_hash") or ""
    if not stored_hash or not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return json_response({"error": "invalid email or password"}, 401)
    token = make_jwt(email)
    return json_response({"token": token, "email": email}, 200)


@app.route(route="get_me", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def get_me(req: func.HttpRequest) -> func.HttpResponse:
    token = get_bearer_token(req)
    if not token:
        return json_response({"error": "missing bearer token"}, 401)
    payload = verify_jwt(token)
    if not payload:
        return json_response({"error": "invalid or expired token"}, 401)
    return json_response({"email": payload["email"]}, 200)


@app.route(route="oauth_callback", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def oauth_callback(req: func.HttpRequest) -> func.HttpResponse:
    code = req.params.get("code")
    if not code:
        return json_response({"error": "missing code parameter"}, 400)
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    client_secret = os.environ.get("GITHUB_CLIENT_SECRET")
    if not client_id or not client_secret:
        return json_response({"error": "GitHub OAuth is not configured on the server"}, 500)
    token_req_data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }).encode("utf-8")
    token_req = urllib.request.Request(
        "https://github.com/login/oauth/access_token",
        data=token_req_data,
        headers={"Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(token_req, timeout=10) as resp:
            token_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logging.error(f"GitHub token exchange failed: {e}")
        return json_response({"error": "GitHub token exchange failed"}, 502)
    access_token = token_data.get("access_token")
    if not access_token:
        return json_response({"error": "GitHub did not return an access token"}, 502)
    gh_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "diet-insights-app",
    }
    try:
        with urllib.request.urlopen(urllib.request.Request("https://api.github.com/user", headers=gh_headers), timeout=10) as resp:
            gh_user = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logging.error(f"GitHub user fetch failed: {e}")
        return json_response({"error": "failed to fetch GitHub user"}, 502)
    email = gh_user.get("email")
    if not email:
        try:
            with urllib.request.urlopen(urllib.request.Request("https://api.github.com/user/emails", headers=gh_headers), timeout=10) as resp:
                emails = json.loads(resp.read().decode("utf-8"))
            primary = next((e for e in emails if e.get("primary")), None)
            email = (primary or (emails[0] if emails else {})).get("email")
        except Exception as e:
            logging.error(f"GitHub email fetch failed: {e}")
    if not email:
        gh_login = gh_user.get("login", "githubuser")
        email = f"{gh_login}@users.noreply.github.com"
    email = email.strip().lower()
    table_client = get_table_client()
    try:
        table_client.get_entity(partition_key="users", row_key=email)
    except ResourceNotFoundError:
        entity = {
            "PartitionKey": "users",
            "RowKey": email,
            "email": email,
            "password_hash": "",
            "auth_provider": "github",
            "created_at": dt.datetime.utcnow().isoformat(),
        }
        table_client.create_entity(entity=entity)
    token = make_jwt(email)
    frontend_url = os.environ.get("FRONTEND_URL", "/login.html")
    redirect_url = f"{frontend_url}#token={urllib.parse.quote(token)}&email={urllib.parse.quote(email)}"
    return func.HttpResponse(status_code=302, headers={"Location": redirect_url})