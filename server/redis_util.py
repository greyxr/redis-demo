import time
from redis.commands.json.path import Path
import json
import redis
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TagField, TextField, NumericField
from dotenv import load_dotenv
import os

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
skins_url = os.getenv("SKINS_URL")

async def drop_keys(client=None):
    if client is None:
        client = redis.from_url(redis_url)
    client.flushdb()

async def loadRedis(attribute, array, client=None):
    if client is None:
        client = redis.from_url(redis_url)
    pipeline = client.pipeline()
    for obj in array:
        key = f"{attribute}:{obj['id']}"
        pipeline.json().set(key, '$', obj)
    pipeline.execute()

async def create_index(client=None):
    if client is None:
        client = redis.from_url(redis_url)
    schema = (
        TextField("$.name", as_name="name"),
        TextField("$.type", as_name="type"), 
        TextField("$.description", as_name="description"),
        TextField("$.rarity", as_name="rarity"),
        NumericField("$.id", as_name="id"),
        TextField("$.details.type", as_name="details_type"),
        TextField("$.details.damage_type", as_name="damage_type"),
        TextField("$.details.weight_class", as_name="weight_class"),
        TextField("$.details.description", as_name="details_description")
    )

    client.ft("itemIdx").create_index(
        schema,
        definition=IndexDefinition(prefix=["items:"], index_type=IndexType.JSON)
    )

def build_query(attributes, searchString):
    if (len(attributes) == 0):
        # Search full index by default
        return (
        f"(@name:({searchString})) | "
        f"(@type:({searchString})) | "
        f"(@description:({searchString})) | "
        f"(@rarity:({searchString})) | "
        f"(@id:({searchString})) | "
        f"(@details_type:({searchString})) | "
        f"(@damage_type:({searchString}))"
    )
    else:
        query = ''
        for attr in attributes:
            query += (f"(@{attr}:({searchString})) | ")
        # Remove last or operator
        print(query[:-3])
        return query[:-3]

def get_all(client=None):
    if client is None:
        client = redis.from_url(redis_url)

def send_query(search, auth, include, exclude, limit, attributes, client=None):
    if client is None:
        client = redis.from_url(redis_url)
    # Trim quotes from search term to create search string correctly
    searchString = '*' + search.replace("'","").replace('"','') + '*'
    
    query = build_query(attributes, searchString)

    queryObj = Query(query).paging(0,limit)
    start_time = time.time()
    results = client.ft("itemIdx").search(queryObj)
    end_time = time.time()
    array = []
    for doc in results.docs:
        array.append(json.loads(doc.json))
    return array, end_time - start_time

def query_index(client=None):
    if client is None:
        client = redis.from_url(redis_url)
    query = "@rarity:Basic"
    start_time = time.time()
    results = client.ft("itemIdx").search(query)
    end_time = time.time()
    print('Loaded ' +str(end_time - start_time) + ' seconds.')
    print("Query Results:")
    for doc in results.docs:
        item = json.loads(doc.json)
        print(item["id"], item["name"], item["type"])