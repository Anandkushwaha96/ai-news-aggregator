from typing import List, Dict, Any
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from datetime import datetime, timezone
import json

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class AgenticAI:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.trending_topics_cache = {}
        
    def summarize_article(self, text: str, max_sentences: int = 3) -> str:
        """Generate a summary of the article using extractive summarization"""
        if not text or len(text) < 100:
            return text
        
        try:
            sentences = sent_tokenize(text)
            
            if len(sentences) <= max_sentences:
                return text
            
            scores = []
            for i, sent in enumerate(sentences):
                score = 1.0 / (i + 1)
                words = re.findall(r'\w+', sent.lower())
                score += len([w for w in words if len(w) > 3]) * 0.1
                scores.append(score)
            
            top_indices = np.argsort(scores)[-max_sentences:]
            top_indices.sort()
            
            summary = ' '.join([sentences[i] for i in top_indices])
            return summary
        except Exception as e:
            print(f"Summarization error: {e}")
            return text[:200] + "..."
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []
        
        try:
            words = re.findall(r'\w+', text.lower())
            
            # Extended stop words list
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'are', 'be',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that',
                'these', 'those', 'it', 'its', 'they', 'them', 'their', 'what',
                'which', 'who', 'whom', 'whose', 'when', 'where', 'why', 'how',
                'about', 'above', 'across', 'after', 'against', 'along', 'among',
                'around', 'at', 'before', 'behind', 'below', 'beneath', 'beside',
                'between', 'beyond', 'but', 'by', 'despite', 'down', 'during',
                'except', 'for', 'from', 'in', 'inside', 'into', 'like', 'near',
                'of', 'off', 'on', 'onto', 'out', 'outside', 'over', 'past',
                'since', 'through', 'throughout', 'to', 'toward', 'under',
                'underneath', 'until', 'up', 'upon', 'with', 'within', 'without'
            }
            
            filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
            word_freq = Counter(filtered_words)
            
            # Return top keywords
            keywords = [word for word, _ in word_freq.most_common(top_n)]
            
            # Filter out any remaining common words
            common_tech_words = ['news', 'article', 'read', 'more', 'new', 'year', 'time', 'day', 'week', 'month']
            keywords = [k for k in keywords if k not in common_tech_words]
            
            return keywords[:top_n]
        except Exception as e:
            print(f"Keyword extraction error: {e}")
            return []
    
    def suggest_related_topics(self, article: Dict[str, Any], all_articles: List[Dict[str, Any]], top_n: int = 5) -> List[str]:
        """Suggest related topics based on article content"""
        if not article or not all_articles:
            return []
        
        try:
            article_text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
            keywords = self.extract_keywords(article_text, top_n=10)
            
            related_topics = set()
            for other in all_articles[:20]:
                other_text = f"{other.get('title', '')} {other.get('description', '')}"
                other_keywords = self.extract_keywords(other_text, top_n=5)
                
                if set(keywords) & set(other_keywords):
                    category = other.get('category', '')
                    if category and category not in ['general', '']:
                        related_topics.add(category)
            
            return list(related_topics)[:top_n]
        except Exception as e:
            print(f"Related topics error: {e}")
            return []
    
    def predict_trending_topics(self, articles: List[Dict[str, Any]], min_mentions: int = 2) -> List[str]:
        """Predict trending topics using keyword frequency analysis - FIXED VERSION"""
        if not articles:
            return ["AI", "Technology", "Science", "Health", "Climate", "Business"]
        
        try:
            # Common stop words to filter out
            common_words = {
                'have', 'that', 'this', 'with', 'from', 'they', 'will', 'what',
                'when', 'where', 'which', 'their', 'there', 'about', 'would',
                'could', 'should', 'been', 'were', 'was', 'has', 'had', 'said',
                'says', 'news', 'article', 'read', 'more', 'new', 'year', 'time',
                'after', 'before', 'during', 'while', 'since', 'until', 'just',
                'very', 'also', 'than', 'then', 'than', 'now', 'over', 'into',
                'only', 'other', 'such', 'than', 'then', 'them', 'these', 'those',
                'first', 'last', 'next', 'previous', 'final', 'initial', 'latest'
            }
            
            all_text = ' '.join([
                f"{a.get('title', '')} {a.get('description', '')}" 
                for a in articles
            ])
            
            # Extract keywords but filter out common words
            keywords = self.extract_keywords(all_text, top_n=30)
            
            # Filter keywords
            filtered_keywords = [k for k in keywords if k not in common_words and len(k) > 2]
            
            # Count keyword mentions
            keyword_mentions = Counter()
            
            for article in articles[:50]:
                article_text = f"{article.get('title', '')} {article.get('description', '')}".lower()
                for keyword in filtered_keywords[:20]:
                    if keyword in article_text:
                        keyword_mentions[keyword] += 1
            
            # Get trending keywords with minimum mentions
            trending = [k for k, v in keyword_mentions.items() if v >= min_mentions]
            
            # If no trending topics, return some default categories based on articles
            if not trending:
                # Extract categories from articles
                categories = [a.get('category', '') for a in articles if a.get('category')]
                category_counts = Counter(categories)
                trending = [cat for cat, _ in category_counts.most_common(5)]
            
            # Capitalize first letter and return
            result = [t.capitalize() for t in trending[:8]]
            
            # If still empty, return defaults
            if not result:
                return ["AI", "Technology", "Science", "Health", "Climate", "Business"]
            
            return result
            
        except Exception as e:
            print(f"Trending topics error: {e}")
            return ["AI", "Technology", "Science", "Health", "Climate", "Business"]
    
    def calculate_trending_score(self, article: Dict[str, Any], all_articles: List[Dict[str, Any]]) -> float:
        """
        Calculate a trending score for an article
        """
        score = 0.0
        
        try:
            # Factor 1: Recency (0-1) - FIXED DATETIME ISSUE
            published = article.get('published_at')
            
            if published is None:
                recency_score = 0.5
            else:
                try:
                    # Handle different datetime formats
                    if isinstance(published, str):
                        # Remove 'Z' and convert
                        if published.endswith('Z'):
                            published = published.replace('Z', '+00:00')
                        published = datetime.fromisoformat(published)
                    
                    # Make both timezone-aware
                    from datetime import timezone
                    
                    # If published is naive (no timezone), make it UTC
                    if published.tzinfo is None:
                        published = published.replace(tzinfo=timezone.utc)
                    
                    # Get current time in UTC
                    now = datetime.now(timezone.utc)
                    
                    # Calculate hours difference
                    time_diff = now - published
                    hours_ago = abs(time_diff.total_seconds() / 3600)
                    
                    # Score based on recency (higher for newer articles)
                    recency_score = max(0, 1 - (hours_ago / 72))  # Decay over 3 days
                except Exception as e:
                    print(f"Recency calculation error: {e}")
                    recency_score = 0.5
            
            score += recency_score * 0.4
            
            # Factor 2: Keyword popularity (0-1)
            article_text = f"{article.get('title', '')} {article.get('description', '')}"
            keywords = self.extract_keywords(article_text, top_n=5)
            
            if all_articles and keywords:
                trending_topics = self.predict_trending_topics(all_articles, min_mentions=1)
                keyword_popularity = len([k for k in keywords if k in trending_topics]) / 5
                score += keyword_popularity * 0.3
            
            # Factor 3: Content length and richness (0-1)
            content_length = len(article.get('content', '') or '')
            if content_length > 1000:
                content_score = 1.0
            elif content_length > 500:
                content_score = 0.7
            elif content_length > 200:
                content_score = 0.4
            else:
                content_score = 0.1
            score += content_score * 0.3
            
        except Exception as e:
            print(f"Error in calculate_trending_score: {e}")
            return 0.5
        
        return min(score, 1.0)  # Normalize to 0-1
    
    def enhance_articles_with_ai(self, articles: List[Dict[str, Any]], all_articles: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Enhance articles with AI-generated features"""
        if not articles:
            return []
        
        if all_articles is None:
            all_articles = articles
        
        enhanced_articles = []
        
        for article in articles:
            try:
                enhanced = article.copy()
                
                # Generate summary
                content = article.get('content', '') or article.get('description', '') or ''
                enhanced['summary'] = self.summarize_article(str(content))
                
                # Generate related topics
                enhanced['related_topics'] = self.suggest_related_topics(article, all_articles)
                
                # Calculate trending score
                enhanced['trending_score'] = self.calculate_trending_score(article, all_articles)
                
                enhanced_articles.append(enhanced)
            except Exception as e:
                print(f"Error enhancing article: {e}")
                # Add article without enhancements
                article_with_defaults = article.copy()
                article_with_defaults['summary'] = article.get('description', '')
                article_with_defaults['related_topics'] = []
                article_with_defaults['trending_score'] = 0.5
                enhanced_articles.append(article_with_defaults)
        
        return enhanced_articles