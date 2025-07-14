import os
from dotenv import load_dotenv
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_async_engine(DATABASE_URL)


# 비동기 FastAPI 서버 시작 시 자동으로 DB 테이블을 만들어주는 로직
async def init_db(): # db 연결
    async with engine.begin() as conn: # connection , engine.begin()으로 DB 연결을 시작
        await conn.run_sync(SQLModel.metadata.create_all)  # run_sync(SQLModel.metadata.create_all)로 테이블을 생성
    
    
async def get_session(): # 세션 비동기화
    async with AsyncSession(engine) as session:
        yield session