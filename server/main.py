import json
from typing import List
from fastapi import FastAPI
from starlette.background import BackgroundTasks
import redis
from redis_util import get_user_ids, putUser, send_query
from fastapi.middleware.cors import CORSMiddleware
from redis_util import loadRedis
from fastapi import FastAPI, Body
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    type: str=''
    rarity: str=''
    name: str=''
    description: str=''
    details: object=''

app = FastAPI()
redis_url = "http://localhost:6379"

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    app.client = redis.from_url("redis://redis:6379")

@app.get("/search")
async def root(query:str,auth:str|None=None, include:bool|None=None, exclude:bool|None=None,limit=500,user=None,attributes:str|None=None):
    atribute_array = []
    if (attributes is not None):
        try:
            atribute_array = attributes.split(',')
        except:
            return { 'error': 'Could not parse attribute array' }
    array, elapsed_time = send_query(query, auth, include, exclude, limit, atribute_array, user, app.client)
    return {"items": array, "metadata": { "time": elapsed_time }}

@app.get("/test")
async def root():
    return {'ping': 'bing'}

@app.get("/putUser")
async def root(api_key, name):
    print('Starting putUser...')
    print(name)
    print(api_key)
    await putUser(name, api_key, app.client)
    return {'user': name}

@app.api_route("/putItem", methods=["POST"])
async def root(items:List[Item]):
    print('Starting putUser...')
    items_json = [item.model_dump() for item in items]
    await loadRedis('items', items_json, app.client)
    return {'items_inserted': len(items)}

@app.get("/user")
async def root(name):
    print('Starting getUser...')
    print(name)
    result = get_user_ids(name, app.client)
    return {'id': result}

@app.on_event("shutdown")
async def shutdown_event():
    app.client.close()