# 인증과 관련된 내용은 다 여기 넣음 (비밀번호)
import secrets
from typing import Optional
from passlib.context import CryptContext
from redis.asyncio import Redis

pwd_context = CryptContext(schemes =["bcrypt"],deprecated = "auto")

SESSION_TTL_SECONES = 3600 # 세션 정보 => 브라우저가 가지고 있음 (그래서 딱 필요한 키값만 가지게 해야함 )


def get_password_hash(password:str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password:str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password) 

async def create_session(redis:Redis, user_id:int) -> str: 
    session_id = secrets.token_hex(16)   # 난수를 만드는 것 
    await redis.setex(f"session:{session_id}", SESSION_TTL_SECONES, str(user_id)) # redis에는 key, value로 들어감 세션아이디가 키, user_id가 value
    return session_id


# redis 에서 session을 지우는 것만 할거임 , 서버 쪽 세션 정보 삭제
async def delete_session(redis:Redis, session_id: str):
    await redis.delete(f"session:{session_id}")




async def get_user_id_from_session(redis:Redis, session_id:str) ->Optional[int]:   # 해당 함수의 반환값이 int일 수도 있고 None일 수도 있다는 걸 명시적으로 표현해 주는 타입 힌트
    user_id = await redis.get(f"session:{session_id}")
    return user_id if user_id else None 