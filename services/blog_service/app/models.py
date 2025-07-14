from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
# 테이블 진짜 만드는 거
class ArticleImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    image_filename:str
    article_id:Optional[int] = Field(default=None, index= True)

class BlogArticle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str= Field(index=True)
    contenct:str
    # timezone.utc
    create_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    owner_id: int
    tags: Optional[str] = Field(default=None)