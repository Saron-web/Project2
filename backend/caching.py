import json
from azure.storage.blob import BlobServiceClient

def load_cached_json():
    connection = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
    )
    container = connection.get_container_client("cleaned")
    blob = container.get_blob_client("clean_data.json")
    data = blob.download_blob().readall().decode("utf-8")
    return json.loads(data)
