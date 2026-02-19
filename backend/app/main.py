import os
import nltk

# Download NLTK data for production
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Get PORT from environment (Render assigns this automatically)
PORT = int(os.getenv("PORT", 8000))

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
import random
import os

from . import models, schemas, crud
from .database import engine, get_db
from .core.config import settings
from .core.agentic_ai import AgenticAI

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agent
ai_agent = AgenticAI()

# Try to import NewsAPI if available
try:
    from .core.news_api import NewsAPIService
    news_api = NewsAPIService()
    NEWS_API_AVAILABLE = True
    print("✅ NewsAPI service loaded")
except ImportError as e:
    print(f"⚠️ NewsAPI not available: {e}")
    NEWS_API_AVAILABLE = False
    news_api = None

   
# Sample data for demo
SAMPLE_ARTICLES = [
    {
        "title": "AI Breakthrough: New Model Achieves Human-Level Reasoning",
        "description": "Researchers have developed a new AI model that demonstrates human-level reasoning capabilities in complex problem-solving tasks.",
        "content": "In a groundbreaking development, scientists at the AI Research Lab have created a neural network architecture that mimics human cognitive processes. The model, named 'Cogito-1', successfully solved complex reasoning problems that previously required human intervention. This breakthrough could lead to more sophisticated AI assistants and autonomous systems. The team trained the model on a diverse dataset of logical puzzles, scientific papers, and real-world scenarios. Early results show 95% accuracy in reasoning tasks, matching human performance levels.",
        "url": "https://example.com/ai-breakthrough",
        "image_url": "https://via.placeholder.com/300x200?text=AI+Breakthrough",
        "source": "Tech Daily",
        "category": "technology",
        "published_at": datetime.now() - timedelta(hours=2)
    },
    {
        "title": "Global Climate Summit Reaches Historic Agreement",
        "description": "World leaders have agreed to unprecedented measures to combat climate change at the annual Climate Summit.",
        "content": "The 2024 Global Climate Summit concluded with a landmark agreement among 150 nations to reduce carbon emissions by 50% by 2030. The accord includes provisions for renewable energy investment, deforestation prevention, and climate adaptation funding for developing nations. Environmental groups have praised the agreement as a 'historic turning point' in the fight against climate change. Key provisions include a global carbon trading system and technology sharing agreements for clean energy solutions.",
        "url": "https://example.com/climate-summit",
        "image_url": "https://via.placeholder.com/300x200?text=Climate+Summit",
        "source": "World News",
        "category": "environment",
        "published_at": datetime.now() - timedelta(hours=5)
    },
    {
        "title": "Revolutionary Quantum Computer Achieves Quantum Supremacy",
        "description": "Tech giant unveils quantum computer that solves complex calculations in seconds, outperforming traditional supercomputers.",
        "content": "In a major milestone for computing, QuantumTech Inc. has demonstrated a 1000-qubit quantum processor that achieves quantum supremacy across multiple benchmarks. The system solved a complex optimization problem in 200 seconds that would take the world's fastest supercomputer 10,000 years to complete. This breakthrough opens new possibilities in drug discovery, materials science, and cryptography. The company plans to make the technology available through cloud services starting next year.",
        "url": "https://example.com/quantum-computer",
        "image_url": "https://via.placeholder.com/300x200?text=Quantum+Computing",
        "source": "Tech Review",
        "category": "technology",
        "published_at": datetime.now() - timedelta(hours=8)
    },
    {
        "title": "Breakthrough in Cancer Research: New Treatment Shows Promise",
        "description": "Clinical trials reveal new immunotherapy treatment with 80% success rate in treating previously incurable cancer types.",
        "content": "Medical researchers at the National Cancer Institute have developed a novel immunotherapy approach that shows remarkable results in treating aggressive forms of cancer. The treatment, which uses modified T-cells to target cancer cells, achieved an 80% remission rate in phase III clinical trials. Unlike traditional chemotherapy, patients experienced minimal side effects. The FDA has granted breakthrough therapy designation, potentially accelerating approval for widespread use.",
        "url": "https://example.com/cancer-breakthrough",
        "image_url": "https://via.placeholder.com/300x200?text=Cancer+Research",
        "source": "Health News",
        "category": "health",
        "published_at": datetime.now() - timedelta(hours=12)
    },
    {
        "title": "Space Tourism Takes Off: First Commercial Flight to Orbit",
        "description": "Space exploration company successfully launches first all-civilian mission to Earth's orbit, marking new era in space travel.",
        "content": "Space Horizon's Dragon spacecraft successfully completed its historic mission, carrying four civilian passengers to low Earth orbit. The three-day journey included spectacular views of Earth and conducted microgravity experiments. This marks the beginning of regular commercial space flights, with tickets starting at $50 million. The company plans to establish a space hotel by 2028 and lunar tourism by 2030.",
        "url": "https://example.com/space-tourism",
        "image_url": "https://via.placeholder.com/300x200?text=Space+Tourism",
        "source": "Space Today",
        "category": "science",
        "published_at": datetime.now() - timedelta(hours=15)
    },
    {
        "title": "Electric Vehicle Sales Surge as Prices Drop",
        "description": "EV adoption accelerates globally as battery costs fall and new affordable models enter the market.",
        "content": "Global electric vehicle sales have increased by 60% this year, driven by falling battery prices and government incentives. Major automakers have introduced affordable EV models under $30,000, making electric transportation accessible to mainstream consumers. Charging infrastructure has also expanded rapidly, with fast-charging stations now available along major highways. Industry analysts predict EVs will comprise 50% of new car sales by 2028.",
        "url": "https://example.com/ev-surge",
        "image_url": "https://via.placeholder.com/300x200?text=Electric+Vehicles",
        "source": "Auto World",
        "category": "business",
        "published_at": datetime.now() - timedelta(hours=18)
    },
    {
        "title": "Breakthrough in Nuclear Fusion: Net Energy Gain Achieved",
        "description": "Scientists achieve net energy gain in nuclear fusion experiment, bringing clean energy dreams closer to reality.",
        "content": "Researchers at the National Ignition Facility have achieved a historic milestone in fusion energy production. The experiment produced more energy from a fusion reaction than was used to initiate it, a crucial step toward practical fusion power. The breakthrough used laser-based inertial confinement to compress hydrogen fuel to extreme temperatures and pressures. Commercial fusion power plants could be operational within a decade, potentially revolutionizing global energy production.",
        "url": "https://example.com/fusion-breakthrough",
        "image_url": "https://via.placeholder.com/300x200?text=Nuclear+Fusion",
        "source": "Science Daily",
        "category": "science",
        "published_at": datetime.now() - timedelta(hours=20)
    }
]

@app.on_event("startup")
async def startup_event():
    """Initialize database with real news from API"""
    db = next(get_db())
    
    # Check if we already have articles
    existing = crud.get_articles(db, limit=1)
    
    # If no articles, fetch from API
    if not existing:
        if NEWS_API_AVAILABLE and news_api:
            print("📰 Fetching real news from NewsAPI...")
            try:
                # Fetch trending news from API
                api_articles = await news_api.fetch_trending_news(page_size=20)
                
                if api_articles and len(api_articles) > 0:
                    # Save to database
                    for article_data in api_articles:
                        try:
                            article = schemas.ArticleCreate(**article_data)
                            crud.create_article(db, article)
                        except Exception as e:
                            print(f"Error saving article: {e}")
                            continue
                    print(f"✅ Added {len(api_articles)} real articles from NewsAPI")
                else:
                    # Fallback to sample data
                    print("⚠️ No articles from API, using sample data")
                    for article_data in SAMPLE_ARTICLES:
                        article = schemas.ArticleCreate(**article_data)
                        crud.create_article(db, article)
                    print(f"✅ Added {len(SAMPLE_ARTICLES)} sample articles")
            except Exception as e:
                print(f"❌ Error fetching from API: {e}")
                # Use sample data
                for article_data in SAMPLE_ARTICLES:
                    article = schemas.ArticleCreate(**article_data)
                    crud.create_article(db, article)
                print(f"✅ Added {len(SAMPLE_ARTICLES)} sample articles (fallback)")
        else:
            # No API key, use sample data
            print("📋 No API key found or NewsAPI not available, using sample data")
            for article_data in SAMPLE_ARTICLES:
                article = schemas.ArticleCreate(**article_data)
                crud.create_article(db, article)
            print(f"✅ Added {len(SAMPLE_ARTICLES)} sample articles")
    
    # Create a demo user
    demo_user = crud.get_user_by_username(db, "demo_user")
    if not demo_user:
        demo_user = schemas.UserCreate(
            username="demo_user",
            email="demo@example.com",
            preferences=["technology", "science"]
        )
        crud.create_user(db, demo_user)
        print("✅ Demo user created")
    
    print("✅ Startup complete!")
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if NEWS_API_AVAILABLE and news_api:
        await news_api.close()
        print("👋 NewsAPI connection closed")

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI News Aggregator API", 
        "version": settings.VERSION,
        "status": "running",
        "news_api": "available" if NEWS_API_AVAILABLE else "not available"
    }

@app.get("/trending-news", response_model=List[schemas.ArticleWithAI])
async def get_trending_news(
    limit: int = Query(10, ge=1, le=50),
    refresh: bool = Query(False, description="Force refresh from API"),
    db: Session = Depends(get_db)
):
    """Get trending news articles with AI enhancements"""
    try:
        # If refresh is True, fetch from API
        if refresh and NEWS_API_AVAILABLE and news_api:
            print("🔄 Refreshing news from API...")
            api_articles = await news_api.fetch_trending_news(page_size=limit)
            
            if api_articles and len(api_articles) > 0:
                # Save to database
                for article_data in api_articles:
                    try:
                        article = schemas.ArticleCreate(**article_data)
                        crud.create_article(db, article)
                    except:
                        pass
                
                # Enhance with AI
                enhanced = ai_agent.enhance_articles_with_ai(api_articles)
                
                # Convert to response model
                result = []
                for i, article_data in enumerate(enhanced):
                    article_with_ai = schemas.ArticleWithAI(
                        id=i,
                        title=article_data["title"],
                        description=article_data["description"],
                        content=article_data.get("content", ""),
                        url=article_data["url"],
                        image_url=article_data.get("image_url"),
                        source=article_data["source"],
                        category=article_data["category"],
                        published_at=article_data["published_at"],
                        created_at=datetime.now(),
                        summary=article_data.get("summary", ""),
                        related_topics=article_data.get("related_topics", []),
                        trending_score=article_data.get("trending_score", 0.5)
                    )
                    result.append(article_with_ai)
                return result
        
        # Get from database
        articles = crud.get_trending_articles(db, limit=limit)
        
        # If no articles in database, try API
        if not articles and NEWS_API_AVAILABLE and news_api:
            return await get_trending_news(limit=limit, refresh=True, db=db)
        
        # If still no articles, use sample
        if not articles:
            # Return sample articles with AI enhancements
            sample_with_ai = []
            for i, article_data in enumerate(SAMPLE_ARTICLES[:limit]):
                enhanced = ai_agent.enhance_articles_with_ai([article_data])[0]
                article_with_ai = schemas.ArticleWithAI(
                    id=i,
                    title=enhanced["title"],
                    description=enhanced["description"],
                    content=enhanced.get("content", ""),
                    url=enhanced["url"],
                    image_url=enhanced.get("image_url"),
                    source=enhanced["source"],
                    category=enhanced["category"],
                    published_at=enhanced["published_at"],
                    created_at=datetime.now(),
                    summary=enhanced.get("summary", ""),
                    related_topics=enhanced.get("related_topics", []),
                    trending_score=enhanced.get("trending_score", 0.5)
                )
                sample_with_ai.append(article_with_ai)
            return sample_with_ai
        
        # Process database articles
        all_articles = crud.get_articles(db, limit=100)
        
        articles_dict = [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "content": a.content,
                "url": a.url,
                "image_url": a.image_url,
                "source": a.source,
                "category": a.category,
                "published_at": a.published_at.isoformat() if a.published_at else None
            }
            for a in articles
        ]
        
        all_dict = [
            {
                "title": a.title,
                "description": a.description,
                "content": a.content,
                "category": a.category,
                "published_at": a.published_at.isoformat() if a.published_at else None
            }
            for a in all_articles
        ]
        
        enhanced = ai_agent.enhance_articles_with_ai(articles_dict, all_dict)
        
        result = []
        for i, article in enumerate(articles):
            article_with_ai = schemas.ArticleWithAI(
                id=article.id,
                title=article.title,
                description=article.description,
                content=article.content,
                url=article.url,
                image_url=article.image_url,
                source=article.source,
                category=article.category,
                published_at=article.published_at,
                created_at=article.created_at,
                summary=enhanced[i].get("summary", "") if i < len(enhanced) else "",
                related_topics=enhanced[i].get("related_topics", []) if i < len(enhanced) else [],
                trending_score=enhanced[i].get("trending_score", 0.5) if i < len(enhanced) else 0.5
            )
            result.append(article_with_ai)
        
        return result
    except Exception as e:
        print(f"Error in get_trending_news: {e}")
        import traceback
        traceback.print_exc()
        return []
@app.get("/recommendations", response_model=List[schemas.ArticleWithAI])
async def get_recommendations(
    user_id: int = Query(1, description="User ID"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get personalized news recommendations for a user"""
    try:
        articles = crud.get_recommendations_for_user(db, user_id, limit=limit)
        
        # Agar koi recommendations nahi hain toh trending do
        if not articles:
            return await get_trending_news(limit=limit, db=db)
        
        all_articles = crud.get_articles(db, limit=100)
        
        # Convert to dict for AI processing
        articles_dict = [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "content": a.content,
                "url": a.url,
                "image_url": a.image_url,
                "source": a.source,
                "category": a.category,
                "published_at": a.published_at.isoformat() if a.published_at else None
            }
            for a in articles
        ]
        
        all_dict = [
            {
                "title": a.title,
                "description": a.description,
                "content": a.content,
                "category": a.category,
                "published_at": a.published_at.isoformat() if a.published_at else None
            }
            for a in all_articles
        ]
        
        # Enhance with AI
        enhanced = ai_agent.enhance_articles_with_ai(articles_dict, all_dict)
        
        # Convert back
        result = []
        for i, article in enumerate(articles):
            article_with_ai = schemas.ArticleWithAI(
                id=article.id,
                title=article.title,
                description=article.description,
                content=article.content,
                url=article.url,
                image_url=article.image_url,
                source=article.source,
                category=article.category,
                published_at=article.published_at,
                created_at=article.created_at,
                summary=enhanced[i].get("summary", ""),
                related_topics=enhanced[i].get("related_topics", []),
                trending_score=enhanced[i].get("trending_score", 0.5)
            )
            result.append(article_with_ai)
        
        return result
    except Exception as e:
        print(f"Error in get_recommendations: {e}")
        return await get_trending_news(limit=limit, db=db)

# ============================================
# SEARCH ENDPOINT - UPDATED WITH API SUPPORT
# ============================================
@app.get("/search", response_model=List[schemas.ArticleWithAI])
async def search_news(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    use_api: bool = Query(True, description="Use NewsAPI for search"),
    db: Session = Depends(get_db)
):
    """Search news articles - with API fallback"""
    try:
        print(f"🔍 Searching for: '{query}' (use_api={use_api})")
        
        # Try API first if enabled and available
        if use_api and NEWS_API_AVAILABLE and news_api:
            try:
                print(f"📡 Fetching from NewsAPI for: {query}")
                api_articles = await news_api.search_news(query, page_size=limit)
                
                if api_articles and len(api_articles) > 0:
                    print(f"✅ Found {len(api_articles)} results from API")
                    
                    # Save to database for future
                    for article_data in api_articles:
                        try:
                            # Check if article already exists
                            existing = crud.search_articles(db, article_data["title"], limit=1)
                            if not existing:
                                article = schemas.ArticleCreate(**article_data)
                                crud.create_article(db, article)
                        except Exception as e:
                            print(f"Error saving article: {e}")
                            continue
                    
                    # Enhance with AI
                    enhanced = ai_agent.enhance_articles_with_ai(api_articles)
                    
                    # Convert to response model
                    result = []
                    for i, article_data in enumerate(enhanced):
                        article_with_ai = schemas.ArticleWithAI(
                            id=i,
                            title=article_data["title"],
                            description=article_data["description"],
                            content=article_data.get("content", ""),
                            url=article_data["url"],
                            image_url=article_data.get("image_url"),
                            source=article_data["source"],
                            category=article_data["category"],
                            published_at=article_data["published_at"],
                            created_at=datetime.now(),
                            summary=article_data.get("summary", ""),
                            related_topics=article_data.get("related_topics", []),
                            trending_score=article_data.get("trending_score", 0.5)
                        )
                        result.append(article_with_ai)
                    
                    return result
            except Exception as e:
                print(f"API search error: {e}")
                # Fall through to database search
        
        # Try database search
        print(f"📋 Searching in database for: {query}")
        articles = crud.search_articles(db, query, limit=limit)
        
        # If results found in database
        if articles and len(articles) > 0:
            print(f"✅ Found {len(articles)} results in database")
            all_articles = crud.get_articles(db, limit=100)
            
            articles_dict = [
                {
                    "id": a.id,
                    "title": a.title,
                    "description": a.description,
                    "content": a.content,
                    "url": a.url,
                    "image_url": a.image_url,
                    "source": a.source,
                    "category": a.category,
                    "published_at": a.published_at.isoformat() if a.published_at else None
                }
                for a in articles
            ]
            
            all_dict = [
                {
                    "title": a.title,
                    "description": a.description,
                    "content": a.content,
                    "category": a.category,
                    "published_at": a.published_at.isoformat() if a.published_at else None
                }
                for a in all_articles
            ]
            
            enhanced = ai_agent.enhance_articles_with_ai(articles_dict, all_dict)
            
            result = []
            for i, article in enumerate(articles):
                article_with_ai = schemas.ArticleWithAI(
                    id=article.id,
                    title=article.title,
                    description=article.description,
                    content=article.content,
                    url=article.url,
                    image_url=article.image_url,
                    source=article.source,
                    category=article.category,
                    published_at=article.published_at,
                    created_at=article.created_at,
                    summary=enhanced[i].get("summary", ""),
                    related_topics=enhanced[i].get("related_topics", []),
                    trending_score=enhanced[i].get("trending_score", 0.5)
                )
                result.append(article_with_ai)
            
            return result
        
        # Finally, search in sample articles
        print(f"📋 Searching in sample articles for: {query}")
        sample_results = []
        for article_data in SAMPLE_ARTICLES:
            if (query.lower() in article_data["title"].lower() or 
                query.lower() in article_data["description"].lower()):
                sample_results.append(article_data)
        
        if sample_results:
            print(f"✅ Found {len(sample_results)} results in sample data")
            enhanced = ai_agent.enhance_articles_with_ai(sample_results)
            result = []
            for i, article_data in enumerate(enhanced[:limit]):
                article_with_ai = schemas.ArticleWithAI(
                    id=i,
                    title=article_data["title"],
                    description=article_data["description"],
                    content=article_data.get("content", ""),
                    url=article_data["url"],
                    image_url=article_data.get("image_url"),
                    source=article_data["source"],
                    category=article_data["category"],
                    published_at=article_data["published_at"],
                    created_at=datetime.now(),
                    summary=article_data.get("summary", ""),
                    related_topics=article_data.get("related_topics", []),
                    trending_score=article_data.get("trending_score", 0.5)
                )
                result.append(article_with_ai)
            return result
        
        print(f"❌ No results found for '{query}'")
        return []
        
    except Exception as e:
        print(f"Error in search_news: {e}")
        import traceback
        traceback.print_exc()
        return []

# ============================================
# USER PREFERENCES ENDPOINT
# ============================================
@app.post("/user/{user_id}/preferences")
async def update_preferences(
    user_id: int,
    preferences: List[str],
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    try:
        print(f"Updating preferences for user {user_id}: {preferences}")
        user = crud.update_user_preferences(db, user_id, preferences)
        if not user:
            # Agar user nahi mila toh naya bana do
            demo_user = schemas.UserCreate(
                username=f"user_{user_id}",
                email=f"user{user_id}@example.com",
                preferences=preferences
            )
            user = crud.create_user(db, demo_user)
            if not user:
                raise HTTPException(status_code=500, detail="Failed to create user")
        
        return {"message": "Preferences updated", "preferences": preferences}
    except Exception as e:
        print(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# TRENDING TOPICS ENDPOINT
# ============================================
@app.get("/trending-topics", response_model=List[str])
async def get_trending_topics(
    db: Session = Depends(get_db)
):
    """Get trending topics from recent news"""
    try:
        articles = crud.get_trending_articles(db, limit=50)
        
        # Agar koi articles nahi hain toh default topics do
        if not articles:
            return ["Technology", "Science", "Health", "Climate", "Business", "AI", "Space", "Fusion"]
        
        articles_dict = []
        for a in articles:
            try:
                articles_dict.append({
                    "title": a.title,
                    "description": a.description,
                    "content": a.content
                })
            except:
                continue
        
        trending = ai_agent.predict_trending_topics(articles_dict)
        result = trending[:8] if trending else ["Technology", "Science", "Health", "Climate", "Business", "AI"]
        
        # Capitalize topics
        result = [topic.capitalize() if topic.islower() else topic for topic in result]
        return result
    except Exception as e:
        print(f"Error in get_trending_topics: {e}")
        return ["Technology", "Science", "Health", "Climate", "Business", "AI", "Space"]

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION,
        "news_api": "available" if NEWS_API_AVAILABLE else "not available"
    }

# ============================================
# DEBUG ENDPOINT - List all routes (optional)
# ============================================
@app.get("/routes")
async def list_routes():
    """List all available routes (for debugging)"""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") else []
        })
    return routes