from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table =True):
    # 자동 증가위해 optional
    id: Optional[int] = Field(default=None, primary_key=True)
    username:str = Field(unique = True, index =True) # 중복 금지 위해 unique = True, 인덱스로 검색 쉽게
    # nullable=False (기본값)	null 금지, 반드시 값이 있어야 함 / # nullable = True를 주면 null 가능
    hashed_password: str                             