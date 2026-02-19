from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ArticleBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source: str
    category: str
    published_at: datetime

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ArticleWithAI(Article):
    summary: Optional[str] = None
    related_topics: List[str] = []
    trending_score: Optional[float] = None

class UserBase(BaseModel):
    username: str
    email: str
    preferences: List[str] = []

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str
    user_id: Optional[int] = None

class TrendingTopics(BaseModel):
    topics: List[str]
    articles: List[ArticleWithAI]