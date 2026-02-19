import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';
import NewsCard from './NewsCard';
import { ThreeDots } from 'react-loader-spinner';
import { FiSearch, FiX, FiTrendingUp, FiClock, FiAlertCircle } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

const Search = () => {
  const [query, setQuery] = useState('');
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);
  const [recentSearches, setRecentSearches] = useState(
    JSON.parse(localStorage.getItem('recentSearches') || '[]')
  );
  const [trendingTopics, setTrendingTopics] = useState([]);

  // Fetch trending topics on mount
  useEffect(() => {
    fetchTrendingTopics();
  }, []);

  const fetchTrendingTopics = async () => {
    try {
      const topics = await api.getTrendingTopics();
      setTrendingTopics(topics.slice(0, 6));
    } catch (error) {
      console.error('Error fetching trending topics:', error);
      setTrendingTopics(['AI', 'Technology', 'Climate', 'Health', 'Space', 'Business']);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search term');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setArticles([]);
      
      console.log('🔍 Searching for:', query);
      const data = await api.searchNews(query, 20);
      console.log('📦 Search results:', data);
      
      // Ensure data is array
      const results = Array.isArray(data) ? data : [];
      setArticles(results);
      setSearched(true);
      
      // Save to recent searches if results found
      if (results.length > 0) {
        const updated = [query, ...recentSearches.filter(s => s !== query)].slice(0, 5);
        setRecentSearches(updated);
        localStorage.setItem('recentSearches', JSON.stringify(updated));
        toast.success(`Found ${results.length} results for "${query}"`);
      } else {
        toast.error(`No results found for "${query}"`);
      }
      
    } catch (error) {
      console.error('❌ Search failed:', error);
      setError(error.message || 'Search failed. Please try again.');
      toast.error('Search failed. Please check your connection.');
      setArticles([]);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setQuery('');
    setArticles([]);
    setSearched(false);
    setError(null);
  };

  const useRecentSearch = (search) => {
    setQuery(search);
    // Small delay to ensure state updates
    setTimeout(() => {
      document.querySelector('form').requestSubmit();
    }, 100);
  };

  const useTrendingTopic = (topic) => {
    setQuery(topic);
    setTimeout(() => {
      document.querySelector('form').requestSubmit();
    }, 100);
  };

  return (
    <div className="search-container">
      <div className="search-header">
        <motion.h2 
          className="section-title"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <FiSearch className="title-icon" />
          Search News
        </motion.h2>
      </div>

      <motion.form 
        onSubmit={handleSearch} 
        className="search-form"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="search-input-wrapper">
          <FiSearch className="search-icon" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for news articles..."
            className="search-input"
            disabled={loading}
          />
          {query && (
            <motion.button
              type="button"
              className="clear-btn"
              onClick={clearSearch}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              disabled={loading}
            >
              <FiX />
            </motion.button>
          )}
        </div>
        
        <motion.button 
          type="submit" 
          className="btn btn-primary search-btn"
          disabled={loading || !query.trim()}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {loading ? 'Searching...' : 'Search'}
        </motion.button>
      </motion.form>

      {/* Recent Searches */}
      {!searched && !loading && recentSearches.length > 0 && (
        <motion.div 
          className="recent-searches"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h3>
            <FiClock /> Recent Searches
          </h3>
          <div className="recent-list">
            {recentSearches.map((search, index) => (
              <motion.button
                key={index}
                className="recent-item"
                onClick={() => useRecentSearch(search)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={loading}
              >
                <FiSearch /> {search}
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Trending Suggestions */}
      {!searched && !loading && trendingTopics.length > 0 && (
        <motion.div 
          className="trending-suggestions"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h3>
            <FiTrendingUp /> Trending Topics
          </h3>
          <div className="suggestions-list">
            {trendingTopics.map((topic, index) => (
              <motion.button
                key={index}
                className="suggestion-item"
                onClick={() => useTrendingTopic(topic)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={loading}
              >
                #{topic}
              </motion.button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Results */}
      <AnimatePresence mode="wait">
        {loading && (
          <motion.div 
            key="loading"
            className="loading-container"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <ThreeDots color="#8b5cf6" height={80} width={80} />
            <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>
              Searching for "{query}"...
            </p>
          </motion.div>
        )}

        {!loading && searched && error && (
          <motion.div 
            key="error"
            className="error-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <FiAlertCircle size={48} color="#ef4444" />
            <h3>Search Failed</h3>
            <p>{error}</p>
            <motion.button 
              className="btn btn-primary"
              onClick={() => {
                setError(null);
                setSearched(false);
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Try Again
            </motion.button>
          </motion.div>
        )}

        {!loading && searched && !error && (
          <motion.div 
            key="results"
            className="search-results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="results-header">
              <h3>
                Results for "{query}"
                <span className="result-count">{articles.length} articles</span>
              </h3>
            </div>

            {articles.length === 0 ? (
              <motion.div 
                className="empty-results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <img 
                  src="https://cdn-icons-png.flaticon.com/512/7486/7486754.png" 
                  alt="No results" 
                  style={{ width: '100px', opacity: 0.5, marginBottom: '1rem' }}
                />
                <h3>No articles found</h3>
                <p>We couldn't find any results for "{query}"</p>
                <p className="suggestion">Try different keywords or check spelling</p>
                <motion.button 
                  className="btn btn-secondary"
                  onClick={() => {
                    setSearched(false);
                    setQuery('');
                  }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  style={{ marginTop: '1rem' }}
                >
                  Search Again
                </motion.button>
              </motion.div>
            ) : (
              <motion.div 
                className="news-grid"
                initial="hidden"
                animate="visible"
                variants={{
                  hidden: { opacity: 0 },
                  visible: {
                    opacity: 1,
                    transition: {
                      staggerChildren: 0.1
                    }
                  }
                }}
              >
                {articles.map((article, index) => (
                  <motion.div
                    key={article.id || index}
                    variants={{
                      hidden: { opacity: 0, y: 20 },
                      visible: { opacity: 1, y: 0 }
                    }}
                  >
                    <NewsCard article={article} />
                  </motion.div>
                ))}
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Search;