
from pymongo.mongo_client import MongoClient, UpdateOne
from dotenv import load_dotenv
import os
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
db_name = 'gw2_data'
collection_name = 'data'
uri = f"mongodb+srv://{username}:{password}@260cluster.req6phj.mongodb.net/?retryWrites=true&w=majority&appName=260cluster"

def create_update_object(item):
    return {
            "filter": { "_id": item["_id"]},
            "update": {"$set": item},
            "upsert": True
    }
def update_mongo(data):
    # Create a new client and connect to the server
    client = MongoClient(uri)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        db = client.get_database('gw2_data')
        collection = db[collection_name]
        formatted_data = [{**item, "_id": item["id"]} for item in data]
        bulkOps = [UpdateOne(**create_update_object(item)) for item in formatted_data]
        collection.bulk_write(bulkOps)
    except Exception as e:
        print(e)

def get_mongo():
    client = MongoClient(uri)