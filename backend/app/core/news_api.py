import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class NewsAPIService:
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = os.getenv("NEWS_API_URL", "https://newsapi.org/v2")
        self.client = httpx.AsyncClient(timeout=15.0)
        
        if self.api_key:
            print(f"✅ NewsAPI key loaded: {self.api_key[:5]}...{self.api_key[-5:]}")
        else:
            print("❌ No NewsAPI key found in .env file")
            
        # Image fallback mapping
        self.category_images = {
            "technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=300",
            "science": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=300",
            "health": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=300",
            "business": "https://images.unsplash.com/photo-1664575602276-acd073f104c1?w=300",
            "environment": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=300",
            "sports": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=300",
            "entertainment": "https://images.unsplash.com/photo-1603190287605-e6ade32fa852?w=300",
            "politics": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=300",
            "general": "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=300"
        }
        
    async def fetch_trending_news(self, country: str = "us", page_size: int = 20) -> List[Dict[str, Any]]:
        """Fetch trending news from NewsAPI with retry logic"""
        if not self.api_key:
            print("⚠️ No API key found. Using sample data.")
            return self.get_sample_news()
        
        # Try multiple countries if one fails
        countries = [country, "us", "gb", "ca", "au"]
        
        for attempt, try_country in enumerate(countries[:3]):  # Try first 3 countries
            try:
                url = f"{self.base_url}/top-headlines"
                params = {
                    "country": try_country,
                    "pageSize": page_size,
                    "apiKey": self.api_key
                }
                
                print(f"📡 Fetching news from NewsAPI (country: {try_country})...")
                response = await self.client.get(url, params=params)
                
                if response.status_code == 429:
                    print(f"⚠️ Rate limit hit, waiting 1 second...")
                    await asyncio.sleep(1)
                    continue
                    
                data = response.json()
                
                if data.get("status") == "ok":
                    articles = data.get("articles", [])
                    if articles:
                        print(f"✅ Found {len(articles)} articles from NewsAPI ({try_country})")
                        return self.format_articles(articles)
                    else:
                        print(f"⚠️ No articles from {try_country}, trying next...")
                else:
                    error_msg = data.get('message', 'Unknown error')
                    print(f"❌ API Error ({try_country}): {error_msg}")
                    
            except Exception as e:
                print(f"❌ Error fetching news from {try_country}: {e}")
            
            await asyncio.sleep(1)  # Wait between attempts
        
        print("⚠️ All API attempts failed. Using sample data.")
        return self.get_sample_news()
    
    async def search_news(self, query: str, page_size: int = 20) -> List[Dict[str, Any]]:
        """Search news by query with pagination"""
        if not self.api_key:
            return self.get_sample_news(query)
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "searchIn": "title,description",
                "pageSize": min(page_size, 100),  # API max is 100
                "sortBy": "relevancy",
                "language": "en",
                "apiKey": self.api_key
            }
            
            print(f"📡 Searching NewsAPI for: '{query}'")
            response = await self.client.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                total = data.get("totalResults", 0)
                print(f"✅ Found {len(articles)} articles for '{query}' (total: {total})")
                
                if articles:
                    return self.format_articles(articles)
                else:
                    print(f"⚠️ No results for '{query}', trying sample...")
                    return self.get_sample_news(query)
            else:
                error_msg = data.get('message', 'Unknown error')
                print(f"❌ Search Error: {error_msg}")
                return self.get_sample_news(query)
                
        except Exception as e:
            print(f"❌ Error searching news: {e}")
            return self.get_sample_news(query)
    
    def format_articles(self, articles: List[Dict]) -> List[Dict]:
        """Format NewsAPI articles to match our schema with better images"""
        formatted = []
        for article in articles:
            # Skip articles without title
            if not article.get("title") or article.get("title") == "[Removed]":
                continue
            
            # Guess category
            category = self.guess_category(article)
            
            # Get image URL with multiple fallbacks
            image_url = article.get("urlToImage", "")
            
            # Clean image URL
            if image_url and isinstance(image_url, str):
                # Remove any query parameters that might cause issues
                image_url = image_url.split('?')[0]
            
            # Check if image is valid
            if not image_url or image_url == "null" or "placeholder" in image_url.lower():
                # Use category-based image
                image_url = self.category_images.get(category, self.category_images["general"])
            
            # Truncate content if too long
            content = article.get("content", article.get("description", ""))
            if content and len(content) > 500:
                content = content[:500] + "..."
            
            formatted.append({
                "title": article.get("title", "No Title").strip(),
                "description": article.get("description", "").strip(),
                "content": content,
                "url": article.get("url", ""),
                "image_url": image_url,
                "source": article.get("source", {}).get("name", "Unknown"),
                "category": category,
                "published_at": self.parse_date(article.get("publishedAt"))
            })
        
        # Remove duplicates by title
        seen = set()
        unique_articles = []
        for article in formatted:
            if article["title"] not in seen:
                seen.add(article["title"])
                unique_articles.append(article)
        
        return unique_articles
    
    def guess_category(self, article: Dict) -> str:
        """Guess category based on keywords with better matching"""
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        text = title + " " + description
        
        # Expanded keyword lists
        categories = {
            "technology": [
                "tech", "ai", "software", "digital", "computer", "internet", "app", 
                "cyber", "data", "quantum", "robot", "coding", "programming", 
                "smartphone", "gadget", "innovation", "startup", "silicon valley"
            ],
            "science": [
                "science", "research", "study", "scientist", "discovery", "space", 
                "nasa", "fusion", "nuclear", "physics", "chemistry", "biology", 
                "laboratory", "experiment", "scientific", "dna", "genetic"
            ],
            "health": [
                "health", "medical", "doctor", "hospital", "virus", "covid", 
                "vaccine", "cancer", "treatment", "disease", "patient", "medicine",
                "wellness", "fitness", "nutrition", "healthcare", "cure"
            ],
            "business": [
                "business", "stock", "market", "economy", "company", "startup", 
                "profit", "sales", "industry", "finance", "investment", "bank",
                "ceo", "corporate", "merger", "acquisition", "trade", "commerce"
            ],
            "environment": [
                "climate", "environment", "green", "energy", "pollution", 
                "sustainable", "summit", "emissions", "carbon", "renewable",
                "solar", "wind", "fossil", "global warming", "eco", "conservation"
            ],
            "sports": [
                "sport", "game", "match", "player", "tournament", "championship", 
                "football", "cricket", "soccer", "basketball", "tennis", "golf",
                "olympic", "athlete", "coach", "team", "league", "score"
            ],
            "entertainment": [
                "movie", "film", "music", "celebrity", "hollywood", "entertainment",
                "actor", "actress", "singer", "concert", "award", "netflix",
                "streaming", "series", "show", "broadway", "theater"
            ],
            "politics": [
                "politics", "government", "election", "president", "minister", 
                "parliament", "vote", "senate", "congress", "democrat", "republican",
                "policy", "law", "legislation", "diplomacy", "foreign affairs"
            ]
        }
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(2 if keyword in title else 1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "general"
    
    def parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse date string to datetime with multiple formats"""
        if not date_str:
            return datetime.now()
        
        # Common date formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        
        for fmt in formats:
            try:
                # Remove 'Z' if present
                if date_str.endswith('Z') and fmt == "%Y-%m-%dT%H:%M:%SZ":
                    date_str = date_str.replace('Z', '+00:00')
                    return datetime.fromisoformat(date_str)
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        try:
            # Try ISO format
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now()
    
    def get_sample_news(self, query: str = "") -> List[Dict]:
        """Return enhanced sample data with better images if API fails"""
        current_time = datetime.now()
        
        sample_articles = [
            {
                "title": f"AI Breakthrough: New Model Achieves Human-Level Reasoning",
                "description": "Researchers have developed a new AI model that demonstrates human-level reasoning capabilities in complex problem-solving tasks.",
                "content": "In a groundbreaking development, scientists at the AI Research Lab have created a neural network architecture that mimics human cognitive processes. The model, named 'Cogito-1', successfully solved complex reasoning problems that previously required human intervention. This breakthrough could lead to more sophisticated AI assistants and autonomous systems.",
                "url": "https://example.com/ai-breakthrough",
                "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=300&q=80",
                "source": "Tech Daily",
                "category": "technology",
                "published_at": current_time - timedelta(hours=2)
            },
            {
                "title": f"Global Climate Summit Reaches Historic Agreement",
                "description": "World leaders have agreed to unprecedented measures to combat climate change at the annual Climate Summit.",
                "content": "The 2024 Global Climate Summit concluded with a landmark agreement among 150 nations to reduce carbon emissions by 50% by 2030. The accord includes provisions for renewable energy investment, deforestation prevention, and climate adaptation funding for developing nations.",
                "url": "https://example.com/climate-summit",
                "image_url": "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=300&q=80",
                "source": "World News",
                "category": "environment",
                "published_at": current_time - timedelta(hours=5)
            },
            {
                "title": f"Revolutionary Quantum Computer Achieves Quantum Supremacy",
                "description": "Tech giant unveils quantum computer that solves complex calculations in seconds, outperforming traditional supercomputers.",
                "content": "In a major milestone for computing, QuantumTech Inc. has demonstrated a 1000-qubit quantum processor that achieves quantum supremacy across multiple benchmarks. The system solved a complex optimization problem in 200 seconds that would take the world's fastest supercomputer 10,000 years.",
                "url": "https://example.com/quantum-computer",
                "image_url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=300&q=80",
                "source": "Tech Review",
                "category": "technology",
                "published_at": current_time - timedelta(hours=8)
            },
            {
                "title": f"Breakthrough in Cancer Research: New Treatment Shows Promise",
                "description": "Clinical trials reveal new immunotherapy treatment with 80% success rate in treating previously incurable cancer types.",
                "content": "Medical researchers at the National Cancer Institute have developed a novel immunotherapy approach that shows remarkable results in treating aggressive forms of cancer. The treatment, which uses modified T-cells to target cancer cells, achieved an 80% remission rate.",
                "url": "https://example.com/cancer-research",
                "image_url": "https://images.unsplash.com/photo-1576086213366-97f3000c3c4b?w=300&q=80",
                "source": "Health News",
                "category": "health",
                "published_at": current_time - timedelta(hours=12)
            },
            {
                "title": f"Space Tourism Takes Off: First Commercial Flight to Orbit",
                "description": "Space exploration company successfully launches first all-civilian mission to Earth's orbit, marking new era in space travel.",
                "content": "Space Horizon's Dragon spacecraft successfully completed its historic mission, carrying four civilian passengers to low Earth orbit. The three-day journey included spectacular views of Earth and conducted microgravity experiments.",
                "url": "https://example.com/space-tourism",
                "image_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=300&q=80",
                "source": "Space Today",
                "category": "science",
                "published_at": current_time - timedelta(hours=15)
            }
        ]
        
        # If query provided, filter and modify titles
        if query and query.strip():
            filtered = []
            for article in sample_articles:
                if query.lower() in article["title"].lower() or query.lower() in article["description"].lower():
                    article_copy = article.copy()
                    article_copy["title"] = f"{query}: {article['title']}"
                    filtered.append(article_copy)
            return filtered if filtered else sample_articles[:2]
        
        return sample_articles
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()