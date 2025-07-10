from typing import Optional
from sqlmodel import Field, SQLModel

# 테이블 진짜 만드는 거
class User(SQLModel, table =True):
    # 자동 증가위해 optional
    id: Optional[int] = Field(default=None, primary_key=True)
    username:str 
    # 중복 금지 위해 unique = True, 인덱스로 검색 쉽게
    # nullable=False (기본값)	null 금지, 반드시 값이 있어야 함 / # nullable = True를 주면 null 가능
    email : str = Field(unique=True, index=True)
    hashed_password: str     # DB 저장용
    bio: Optional[str] = None
    profile_image_filename: Optional[str] = None


# 비밀번호 제외해서 테이블 하나 만듦 (내용 우리한테 보여주기 위해)
class UserPublic(SQLModel):
    id: int
    username:str
    email: str
    bio: Optional[str] = None
    profile_image_filename : Optional[str] = None


# 사용자 생성용
class UserCreate(SQLModel):
    username:str
    email:str
    password: str  # plain password 받기
    bio:Optional[str]