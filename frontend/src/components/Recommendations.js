import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';
import NewsCard from './NewsCard';
import { ThreeDots } from 'react-loader-spinner';
import { FiUser, FiRefreshCw, FiAlertCircle } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

const Recommendations = ({ userId = 1, preferences }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    fetchRecommendations();
  }, [userId, preferences, retryCount]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await api.getRecommendations(userId, 12);
      
      if (data && data.length > 0) {
        setArticles(data);
        toast.success(`Found ${data.length} recommendations for you`);
      } else {
        setError('No recommendations found');
      }
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'Failed to load recommendations');
      toast.error('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <ThreeDots color="#10b981" height={80} width={80} />
      </div>
    );
  }

  if (error) {
    return (
      <motion.div 
        className="error-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="error-content">
          <FiAlertCircle size={48} color="#ef4444" />
          <h3>Unable to load recommendations</h3>
          <p>{error}</p>
          <motion.button 
            className="btn btn-primary"
            onClick={() => setRetryCount(prev => prev + 1)}
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
    <div className="recommendations-container">
      <div className="section-header">
        <motion.h2 
          className="section-title"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <FiUser className="title-icon" />
          Personalized For You
          <span className="title-badge">{articles.length} articles</span>
        </motion.h2>

        {preferences && preferences.length > 0 && (
          <motion.div 
            className="preferences-pills"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {preferences.map(pref => (
              <span key={pref} className="pref-pill">
                {pref}
              </span>
            ))}
          </motion.div>
        )}
      </div>

      <AnimatePresence>
        {articles.length === 0 ? (
          <motion.div 
            className="empty-state"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <p>No recommendations available. Try updating your preferences.</p>
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
      </AnimatePresence>
    </div>
  );
};

export default Recommendations;