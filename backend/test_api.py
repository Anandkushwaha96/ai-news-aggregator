import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_news_api():
    api_key = os.getenv("NEWS_API_KEY")
    print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
    
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "pageSize": 5,
        "apiKey": api_key
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("status") == "ok":
            print("✅ API is working!")
            articles = data.get("articles", [])
            print(f"Found {len(articles)} articles")
            for i, article in enumerate(articles[:3]):
                print(f"\n{i+1}. {article.get('title')}")
        else:
            print("❌ API Error:")
            print(data)

if __name__ == "__main__":
    asyncio.run(test_news_api())