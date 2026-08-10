import io
import json
import logging
import os
from datetime import datetime, timezone

import azure.functions as func
import pandas as pd
from azure.cosmos import CosmosClient, PartitionKey
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

# ---------------------------------------------------------------------------
# Configuration (all read from Function App Application Settings at runtime)
# ---------------------------------------------------------------------------
STORAGE_CONNECTION = os.environ["AzureWebJobsStorage"]
COSMOS_ENDPOINT = os.environ["COSMOS_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_KEY"]
COSMOS_DB_NAME = os.environ.get("COSMOS_DB_NAME", "DietInsightsDB")
COSMOS_CONTAINER_NAME = os.environ.get("COSMOS_CONTAINER_NAME", "Insights")

DATA_CONTAINER = "data"
RAW_BLOB_NAME = "All_Diets.csv"
CLEAN_BLOB_NAME = "All_Diets_clean.csv"
CACHE_DOC_ID = "latest"

NUMERIC_COLS = ["Protein(g)", "Carbs(g)", "Fat(g)"]
TEXT_COLS = ["Diet_type", "Recipe_name", "Cuisine_type"]


def _cosmos_container():
    """Get (or create) the Cosmos container used to store cached insights."""
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    db = client.create_database_if_not_exists(COSMOS_DB_NAME)
    return db.create_container_if_not_exists(
        id=COSMOS_CONTAINER_NAME,
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400,
    )


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """One-time cleaning pass, run only when All_Diets.csv changes."""
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
    """Result calculation, run only when All_Diets.csv changes. Feeds the
    bar/scatter/pie/heatmap charts on the dashboard."""

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

    # Persist the cleaned CSV back to blob storage
    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION)
    clean_bytes = clean_df.to_csv(index=False).encode("utf-8")
    blob_service.get_blob_client(container=DATA_CONTAINER, blob=CLEAN_BLOB_NAME).upload_blob(
        clean_bytes, overwrite=True
    )
    logging.info("Wrote %s (%d rows)", CLEAN_BLOB_NAME, len(clean_df))

    # Compute chart-ready aggregates once, cache them in Cosmos DB
    insights = compute_insights(clean_df)
    container = _cosmos_container()
    container.upsert_item({"id": CACHE_DOC_ID, **insights})
    logging.info("Cached insights to Cosmos DB (recordCount=%d)", insights["recordCount"])


# ---------------------------------------------------------------------------
# HTTP Trigger — same route the dashboard already calls. Serves from cache;
# never re-reads or re-cleans the raw CSV on a normal request.
# ---------------------------------------------------------------------------
@app.function_name(name="get_nutritional_insights")
@app.route(route="get_nutritional_insights", methods=["GET"])
def get_nutritional_insights(req: func.HttpRequest) -> func.HttpResponse:
    start = datetime.now(timezone.utc)

    try:
        container = _cosmos_container()
        item = container.read_item(item=CACHE_DOC_ID, partition_key=CACHE_DOC_ID)
    except Exception as exc:  # cache empty / Cosmos not reachable yet
        logging.warning("Cache read failed: %s", exc)
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "No cached insights yet. Upload All_Diets.csv to the "
                    "'data' container to trigger the cleaning + calculation pipeline."
                }
            ),
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
