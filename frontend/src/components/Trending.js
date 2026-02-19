import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';
import NewsCard from './NewsCard';
import { ThreeDots } from 'react-loader-spinner';
import { FiRefreshCw, FiAlertCircle, FiTrendingUp } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

const Trending = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    fetchTrendingNews();
  }, [retryCount]);

  const fetchTrendingNews = async (forceRefresh = false) => {
  try {
    setLoading(true);
    setError(null);
    
    const data = await api.getTrendingNews(12, forceRefresh);
    
    if (data && data.length > 0) {
      setArticles(data);
      toast.success(`Loaded ${data.length} trending articles`);
    } else {
      setError('No articles found');
    }
  } catch (err) {
    console.error('Error:', err);
    setError(err.message || 'Failed to load trending news');
    toast.error('Failed to load trending news');
  } finally {
    setLoading(false);
  }
};

// Add refresh button
<button onClick={() => fetchTrendingNews(true)}>
  <FiRefreshCw /> Refresh from API
</button>
  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <ThreeDots 
          color="#3b82f6" 
          height={80} 
          width={80} 
          wrapperStyle={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '400px'
          }}
        />
      </div>
    );
  }

  if (error) {
    return (
      <motion.div 
        className="error-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="error-content">
          <FiAlertCircle size={48} color="#ef4444" />
          <h3>Oops! Something went wrong</h3>
          <p>{error}</p>
          <motion.button 
            className="btn btn-primary"
            onClick={handleRetry}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <FiRefreshCw /> Try Again
          </motion.button>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="trending-container">
      <div className="section-header">
        <motion.h2 
          className="section-title"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <FiTrendingUp className="title-icon" />
          Trending Now
          <span className="title-badge">{articles.length} articles</span>
        </motion.h2>
        
        <motion.button 
          className="btn btn-secondary"
          onClick={fetchTrendingNews}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <FiRefreshCw /> Refresh
        </motion.button>
      </div>

      <motion.div 
        className="news-grid"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <AnimatePresence>
          {articles.map((article, index) => (
            <motion.div
              key={article.id || index}
              variants={{
                hidden: { opacity: 0, y: 20 },
                visible: { opacity: 1, y: 0 }
              }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <NewsCard article={article} />
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default Trending;