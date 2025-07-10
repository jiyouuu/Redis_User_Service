import os
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)  
# 순수하게 문자열을 받아서 쓰기 위해서 decode_responses = True 조건 줌 

async def get_redis():
    yield redis_client