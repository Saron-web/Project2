from azure.cosmos import CosmosClient

#l = "your-cosmos-url"  # replace with your Cosmos DB account URI
key = "your-cosmos-key"
database_name = "dietdb"
container_name = "cleaned_data"

client = CosmosClient(url, credential=key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

def read_clean_data():
    items = list(container.read_all_items())
    return items

def write_clean_data(data):
    for item in data:
        container.upsert_item(item)
