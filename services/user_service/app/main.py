import os
from typing import Annotated
from fastapi import FastAPI,status, Response, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from database import init_db, get_session
from contextlib import asynccontextmanager

from redis.asyncio import Redis
from models import User, UserCreate, UserPublic 
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession   # sql모델에서 비동기를 사용
from redis_client import get_redis
from auth import get_password_hash, create_session

STATIC_DIR = "/app/static"
PROFILE_IMAGE_DIR = f"{STATIC_DIR}/profiles"

os.makedirs(PROFILE_IMAGE_DIR,exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("🚀 서버 시작 중... DB 초기화 중")
    await init_db()  # 비동기 DB 초기화
    print("✅ DB 초기화 완료")

    yield  # 여기가 실행되면 FastAPI 앱이 본격적으로 실행됨

    # shutdown
    print("🛑 서버 종료!")

app = FastAPI(title = "User Service", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR),name="static")   # app에 static이라는게 들어오면 static_dir로 가는걸로 인식해라고 mount 


# /assets → assets 경로 따로
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

#------------------------------------------------------------------------------------------------------------------------
# User모델로 들어온 것을 , 재구성해서 UserPublic으로 만들겠음!!!! API 응답용으로 클라이언트에 비번 빼고 보내야하니까!!
# 딕셔너리 함수 
def create_user_public(user: User) -> UserPublic: 
    image_url = f"/static/profiles/{user.profile_image_filename}" if user.profile_image_filename else "/assets/ras.jpg"
    user_dict = user.model_dump()  # user 객체를 dict로 변환
    user_dict['profile_image_url'] = image_url   # 이 필드는 원래 user 모델에는 없지만, 프론트엔드나 API 응답에서 유용하기 때문에 별도로 추가
    return UserPublic(**user_dict) # 딕셔너리를 함수에 전달할 때 사용하는 언패킹 연산자, 딕셔너리의 key-value를 하나씩 꺼내서 함수의 인자처럼 전달
#------------------------------------------------------------------------------------------------------------------------------
# /api/auth/register → 즉, 회원가입 요청 URL
# response_model: API가 응답으로 줄 JSON 데이터의 형식을 UserPublic이라는 Pydantic 모델로 제한 
# 즉, 회원가입 후 클라이언트에 보낼 필드를 제어
@app.post('/api/auth/register',response_model=UserPublic, status_code=status.HTTP_201_CREATED)
# response: FastAPI에서 응답 객체를 직접 다루고 싶을 때 사용 (예: 쿠키 설정, 응답 헤더 조작 등 가능.) /session은 mysql연결용
# FastAPI가 UserCreate로 유효성 검사까지 가능

# user_data: UserCreate => 클라이언트가 보낸 회원가입 정보(JSON)를 UserCreate라는 Pydantic 모델로 자동 파싱해서 받음
# Depends(get_session)으로 의존성 주입해서, FastAPI가 알아서 DB 연결을 관리
# Redis 객체를 의존성 주입 받아서 사용 / 이메일 인증 토큰, 캐시 저장, 중복 가입 방지 등 Redis 관련 로직에서 활용 가능
async def register_user(response:Response, user_data: UserCreate, session: Annotated[AsyncSession, Depends(get_session)],
                        redis : Annotated[Redis, Depends(get_redis)]): # 회원가입할 때 세션을 박음
    # 기존에 있는 사람인지 체크
    statement = select(User).where(User.email == user_data.email)
    exist_user_result = await session.exec(statement) # sqlmodel은 비동기때 exec로 실행/ sqlalchemy는 비동기때 excute로 실행

    if exist_user_result.one_or_none():  # one_or_none() : 있을수도 있고 없을 수도 있다. 즉 참과 거짓이 나옴
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 이메일 입니다!")
    
    hashed_password = get_password_hash(user_data.password)  # 받은 평문 비번을 hash 함수로 해시비번 저장 
    new_user = User.model_validate(user_data, update={"hashed_password":hashed_password})  # 들어오는 컬럼과 User 컬럼을 매칭 + password 컬럼은 이름이 다르니 직접 update를 해줌

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)  # new_user를 넣고 refresh는 그 결과값을 받아와 => id가 생기는 것 !! User 모델에 id가 자동증가값이니 불러와지는 것 .


# 사용자 new_user.id에 대해 고유한 세션 ID를 생성하고, 이 세션 ID와 사용자 정보를 Redis에 저장하는 비동기 함수
# 즉, 로그인 후 사용자를 식별하기 위한 세션을 생성하는 과정
    session_id = await create_session(redis, new_user.id)

# 이건 HTTP 응답에 쿠키(Cookie)를 설정하는 부분 / 클라이언트(브라우저)에 아래 정보를 담은 쿠키를 보내는 것 
    response.set_cookie(
        key="session_id", 	# 쿠키 이름을 "session_id"로 지정
        value=session_id,
        httponly=True, # JavaScript에서 쿠키를 접근 못하게 막음 (보안 강화)
        samesite="lax", # CSRF 공격 방지, 같은 사이트 내에서만 쿠키 자동 전송
        max_age = 3600, # 쿠키가 3600초(1시간) 동안 유효함
        path="/" # 사이트 전체 경로에 대해 이 쿠키가 적용됨
        )

    return create_user_public(new_user)


#--------------------------------------------------------------------------------------------------------
@app.get('/api/auth/login',response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def login_user():
    print('e')