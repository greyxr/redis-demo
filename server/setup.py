import asyncio
import time
import redis
from dotenv import load_dotenv
import os
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TagField, TextField, NumericField

from redis_util import loadRedis
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
skins_url = "https://api.guildwars2.com/v2/skins"
import httpx

async def paginatedLoad(url, auth=None):
    itemArray = []
    i = 0
    async with httpx.AsyncClient() as client:
        while True:
            params = {
                "page": i,
                "page_size": 200
            }
            if auth is not None:
                params["access_token"] = auth
            fullUrl = url + f'?page={i}&page_size=200'
            response = await client.get(fullUrl)
            # response.raise_for_status()
            items = response.json()
            if len(items) == 0 or len(items) == 1:
                break
            itemArray.extend(items)
            i += 1
    return itemArray

async def drop_keys(client=None):
    if client is None:
        client = redis.from_url(redis_url)
    client.flushdb()

async def create_index(client=None):
    if client is None:
        client = redis.from_url(redis_url)
    # Define the fields to index
    schema = (
        TextField("$.name", as_name="name"),
        TextField("$.type", as_name="type"), 
        TextField("$.description", as_name="description"),
        TextField("$.rarity", as_name="rarity"),      # Index 'rarity' as text
        NumericField("$.id", as_name="id"),           # Index 'id' as a number
        TextField("$.details.type", as_name="details_type"),  # Index nested field
        TextField("$.details.damage_type", as_name="damage_type"),
        TextField("$.details.weight_class", as_name="weight_class"),
        TextField("$.details.description", as_name="details_description")
    )

    # Define the index
    client.ft("itemIdx").create_index(
        schema,
        definition=IndexDefinition(prefix=["items:"], index_type=IndexType.JSON)
    )

async def setup_db():
    client = redis.from_url(redis_url)
    try:
        print("Deleting keys:")
        await drop_keys(client)
        print("Done")

        print("Creating index")
        await create_index(client)

        print("Done")

        start_time = time.time()
        array = await paginatedLoad(skins_url)
        end_time = time.time()
        print('Loaded ' + str(len(array)) + ' items in ' + str(end_time - start_time) + ' seconds.')

        # array  = [{"id": i, "name": f"User {i}"} for i in range(10000)]

        load_start = time.time()
        await loadRedis('items', array, client)
        load_end = time.time()
        print('Loaded redis in ' + str(load_end - load_start) + ' seconds.')
    finally:
        client.close()

asyncio.run(setup_db())