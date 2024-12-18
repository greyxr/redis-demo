from fastapi import FastAPI
from starlette.background import BackgroundTasks
import redis
from redis_util import send_query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
async def root(query:str,auth:str|None=None, include:bool|None=None, exclude:bool|None=None,limit=500, attributes:str|None=None):
    atribute_array = []
    if (attributes is not None):
        try:
            atribute_array = attributes.split(',')
        except:
            return { 'error': 'Could not parse attribute array' }
    array, elapsed_time = send_query(query, auth, include, exclude, limit, atribute_array, app.client)
    return {"items": array, "metadata": { "time": elapsed_time }}

@app.get("/test")
async def root():
    return {'ping': 'bing'}

@app.on_event("shutdown")
async def shutdown_event():
    app.client.close()