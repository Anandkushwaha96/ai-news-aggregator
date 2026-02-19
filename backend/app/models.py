from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    preferences = Column(Text, default="[]")  # JSON string of preferred topics
    created_at = Column(DateTime, default=datetime.utcnow)
    
    viewed_articles = relationship("UserArticle", back_populates="user")

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    content = Column(Text)
    url = Column(String, unique=True)
    image_url = Column(String)
    source = Column(String)
    category = Column(String, index=True)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    viewed_by = relationship("UserArticle", back_populates="article")

class UserArticle(Base):
    __tablename__ = "user_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    viewed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="viewed_articles")
    article = relationship("Article", back_populates="viewed_by")