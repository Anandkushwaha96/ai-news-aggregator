import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { FiExternalLink, FiClock, FiTag, FiTrendingUp, FiBookmark, FiShare2 } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

const NewsCard = ({ article }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const {
    title,
    description,
    summary,
    image_url,
    source,
    category,
    published_at,
    related_topics = [],
    trending_score
  } = article;

  const publishedDate = published_at ? new Date(published_at) : new Date();
  const timeAgo = formatDistanceToNow(publishedDate, { addSuffix: true });

  const handleSave = () => {
    setIsSaved(!isSaved);
    toast.success(isSaved ? 'Removed from bookmarks' : 'Saved to bookmarks');
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: title,
        text: description,
        url: article.url
      });
    } else {
      navigator.clipboard.writeText(article.url);
      toast.success('Link copied to clipboard!');
    }
  };

  const getCategoryColor = (cat) => {
    const colors = {
      technology: '#3b82f6',
      science: '#10b981',
      health: '#ef4444',
      business: '#f59e0b',
      environment: '#22c55e',
      politics: '#8b5cf6',
      entertainment: '#ec4899',
      sports: '#f97316'
    };
    return colors[cat] || '#64748b';
  };

  return (
    <motion.article 
      className="news-card"
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{ y: -8 }}
      transition={{ duration: 0.2 }}
    >
      <div className="card-image-container">
        <img 
          src={image_url || 'https://via.placeholder.com/400x250?text=News'} 
          alt={title}
          className="card-image"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/400x250?text=News';
          }}
        />
        
        {/* Category Badge */}
        <span 
          className="category-badge"
          style={{ backgroundColor: getCategoryColor(category) }}
        >
          {category}
        </span>

        {/* Trending Score */}
        {trending_score > 0.7 && (
          <span className="trending-badge">
            <FiTrendingUp /> Trending
          </span>
        )}

        {/* Action Buttons */}
        <div className="card-actions">
          <motion.button 
            className="action-btn"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleSave}
          >
            <FiBookmark className={isSaved ? 'saved' : ''} />
          </motion.button>
          <motion.button 
            className="action-btn"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={handleShare}
          >
            <FiShare2 />
          </motion.button>
        </div>
      </div>

      <div className="card-content">
        {/* Source and Time */}
        <div className="card-meta">
          <span className="source">{source}</span>
          <span className="time">
            <FiClock /> {timeAgo}
          </span>
        </div>

        {/* Title */}
        <h3 className="card-title">{title}</h3>

        {/* Description */}
        <p className="card-description">{description}</p>

        {/* AI Summary */}
        {summary && (
          <motion.div 
            className="ai-summary"
            initial={{ opacity: 0, height: 0 }}
            animate={{ 
              opacity: isHovered ? 1 : 0,
              height: isHovered ? 'auto' : 0
            }}
            transition={{ duration: 0.3 }}
          >
            <div className="summary-label">
              <span className="ai-badge">AI</span> Summary
            </div>
            <p>{summary}</p>
          </motion.div>
        )}

        {/* Related Topics */}
        {related_topics.length > 0 && (
          <div className="related-topics">
            <FiTag className="topics-icon" />
            <div className="topics-list">
              {related_topics.slice(0, 3).map((topic, index) => (
                <span key={index} className="topic">
                  #{topic}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Read More */}
        <motion.a 
          href={article.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="read-more"
          whileHover={{ x: 5 }}
        >
          Read Full Article <FiExternalLink />
        </motion.a>
      </div>
    </motion.article>
  );
};

export default NewsCard;