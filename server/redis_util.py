import time
from redis.commands.json.path import Path
import json
import redis
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TagField, TextField, NumericField
from dotenv import load_dotenv
import os
from api_calls import paginatedLoad, singleLoad

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
skins_url = os.getenv("SKINS_URL")
account_skins_url = os.getenv("ACCOUNT_SKINS_URL")

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

async def putUser(attribute, api_key, client=None):
    if client is None:
        client = redis.from_url(redis_url)
    print("Retrieving ids...")
    item_ids = singleLoad(account_skins_url, api_key)
    print(item_ids)
    print("Retrived ids")
    userObj = {
        "api_key": api_key,
        "id": item_ids
    }
    pipeline = client.pipeline()
    key = f"user:{attribute}"
    pipeline.json().set(key, '$', userObj)
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

def build_query(attributes, searchString, include=None, exclude=None, ids=None):
    if (len(attributes) == 0):
        # Search full index by default
        query = (
        f"(@name:({searchString})) | "
        f"(@type:({searchString})) | "
        f"(@description:({searchString})) | "
        f"(@rarity:({searchString})) | "
        # f"(@id:({searchString})) | "
        f"(@details_type:({searchString})) | "
        f"(@damage_type:({searchString}))"
    )
    else:
        query = ''
        for attr in attributes:
            query += (f"(@{attr}:({searchString})) | ")
        # Remove last or operator
        query = query[:-3]
    if exclude is not None:
        print("Adding exclude")
        query = '(' + query + ')'
        for id in ids:
            query += f' -(@id:[' + str(id) + ' ' + str(id) + '])'
        # query += f' -(@id:[2 2]) -(@id:[8 8])'
    elif include is not None:
        print("Adding include")
        query = '(' + query + '('
        for id in ids:
            query += f' (@id:[' + str(id) + ' ' + str(id) + '])|'
        query = query[:-1]
        query += '))'
    return query

def get_user_ids(user, client=None):
    if client is None:
        client = redis.from_url(redis_url)
    results = client.json().get(f'user:{user}', Path.root_path())
    return results["id"]
    

def send_query(search, auth, include:bool|None, exclude:bool|None, limit, attributes, user=None, client=None):
    if client is None:
        client = redis.from_url(redis_url)
    # Trim quotes from search term to create search string correctly
    searchString = '*' + search.replace("'","").replace('"','') + '*'
    
    query = build_query(attributes, searchString)
    if user is not None:
        ids = get_user_ids(user)
        query = build_query(attributes, searchString, include, exclude, ids)

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