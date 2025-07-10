from fastapi import FastAPI
from database import init_db
from contextlib import asynccontextmanager


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
