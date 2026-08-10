import azure.functions as func
import json
import pandas as pd
from io import StringIO
from azure.storage.blob import BlobServiceClient

def main(blob: func.InputStream):
    raw_csv = blob.read().decode("utf-8")
    df = pd.read_csv(StringIO(raw_csv))

    df = df.dropna()
    df["Diet_type"] = df["Diet_type"].str.lower()

    grouped = df.groupby("Diet_type").agg({
        "Protein(g)": "mean",
        "Carbs(g)": "mean",
        "Fat(g)": "mean"
    }).reset_index()

    results = grouped.to_dict(orient="records")
    output_json = json.dumps(results)

    connection = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
    )

    container = connection.get_container_client("cleaned")
    container.upload_blob("clean_data.json", output_json, overwrite=True)
