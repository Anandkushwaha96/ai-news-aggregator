from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import json
from typing import List, Optional
from . import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    try:
        db_user = models.User(
            username=user.username,
            email=user.email,
            preferences=json.dumps(user.preferences)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
        return None

def get_user(db: Session, user_id: int):
    try:
        return db.query(models.User).filter(models.User.id == user_id).first()
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_user_by_username(db: Session, username: str):
    try:
        return db.query(models.User).filter(models.User.username == username).first()
    except Exception as e:
        print(f"Error getting user by username: {e}")
        return None

def update_user_preferences(db: Session, user_id: int, preferences: List[str]):
    try:
        user = get_user(db, user_id)
        if user:
            user.preferences = json.dumps(preferences)
            db.commit()
            db.refresh(user)
        return user
    except Exception as e:
        print(f"Error updating preferences: {e}")
        db.rollback()
        return None

def create_article(db: Session, article: schemas.ArticleCreate):
    try:
        db_article = models.Article(**article.model_dump())
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return db_article
    except Exception as e:
        print(f"Error creating article: {e}")
        db.rollback()
        return None

def get_article(db: Session, article_id: int):
    try:
        return db.query(models.Article).filter(models.Article.id == article_id).first()
    except Exception as e:
        print(f"Error getting article: {e}")
        return None

def get_articles(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.Article).order_by(desc(models.Article.published_at)).offset(skip).limit(limit).all()
    except Exception as e:
        print(f"Error getting articles: {e}")
        return []

def get_trending_articles(db: Session, limit: int = 20):
    try:
        # Get articles from last 7 days, ordered by relevance
        week_ago = datetime.utcnow() - timedelta(days=7)
        return db.query(models.Article).filter(
            models.Article.published_at >= week_ago
        ).order_by(desc(models.Article.published_at)).limit(limit).all()
    except Exception as e:
        print(f"Error getting trending articles: {e}")
        return []

def get_recommendations_for_user(db: Session, user_id: int, limit: int = 20):
    try:
        user = get_user(db, user_id)
        if not user or not user.preferences:
            return get_trending_articles(db, limit)
        
        preferences = json.loads(user.preferences)
        
        # Get articles matching user preferences
        from sqlalchemy import or_
        conditions = [models.Article.category == pref for pref in preferences]
        recommendations = db.query(models.Article).filter(
            or_(*conditions)
        ).order_by(desc(models.Article.published_at)).limit(limit).all()
        
        return recommendations
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return get_trending_articles(db, limit)

def search_articles(db: Session, query: str, limit: int = 20):
    try:
        return db.query(models.Article).filter(
            (models.Article.title.contains(query)) |
            (models.Article.description.contains(query)) |
            (models.Article.content.contains(query))
        ).order_by(desc(models.Article.published_at)).limit(limit).all()
    except Exception as e:
        print(f"Error searching articles: {e}")
        return []

def record_user_view(db: Session, user_id: int, article_id: int):
    try:
        view = models.UserArticle(user_id=user_id, article_id=article_id)
        db.add(view)
        db.commit()
    except Exception as e:
        print(f"Error recording view: {e}")
        db.rollback()