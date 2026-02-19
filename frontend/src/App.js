import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import { Trending, Recommendations, Search } from './components';
import { api } from './services/api';
import { 
  FiSun, FiMoon, FiTrendingUp, FiUser, FiSearch, 
  FiRefreshCw, FiSettings, FiLogOut, FiBell, FiHome 
} from 'react-icons/fi';
import { ThreeDots } from 'react-loader-spinner';
import './App.css';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState('trending');
  const [loading, setLoading] = useState(false);
  const [trendingTopics, setTrendingTopics] = useState([]);
  const [userPreferences, setUserPreferences] = useState(['technology', 'science']);
  const [showPreferences, setShowPreferences] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    checkApiConnection();
    fetchTrendingTopics();
    
    // Auto refresh every 5 minutes
    const interval = setInterval(() => {
      fetchTrendingTopics();
      if (activeTab === 'trending') {
        toast.success('News refreshed!');
      }
    }, 300000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    document.body.className = darkMode ? 'dark-mode' : 'light-mode';
    localStorage.setItem('theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  const checkApiConnection = async () => {
    try {
      const response = await fetch(`http://${window.location.hostname}:8000/health`);
      const data = await response.json();
      setApiStatus('connected');
      toast.success('Connected to server');
    } catch (error) {
      setApiStatus('disconnected');
      toast.error('Cannot connect to server. Please check backend.');
    }
  };

  const fetchTrendingTopics = async () => {
    try {
      const topics = await api.getTrendingTopics();
      setTrendingTopics(topics.slice(0, 8)); // Show top 8
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching trending topics:', error);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    await fetchTrendingTopics();
    setLoading(false);
    toast.success('Content refreshed!');
  };

  const handlePreferenceChange = (pref) => {
    setUserPreferences(prev => {
      if (prev.includes(pref)) {
        return prev.filter(p => p !== pref);
      } else {
        return [...prev, pref];
      }
    });
  };

  const savePreferences = async () => {
    try {
      setLoading(true);
      await api.updateUserPreferences(1, userPreferences);
      setShowPreferences(false);
      toast.success('Preferences saved!');
    } catch (error) {
      toast.error('Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  const availableTopics = [
    { id: 'technology', name: 'Technology', icon: '💻', color: '#3b82f6' },
    { id: 'science', name: 'Science', icon: '🔬', color: '#10b981' },
    { id: 'health', name: 'Health', icon: '🏥', color: '#ef4444' },
    { id: 'business', name: 'Business', icon: '📈', color: '#f59e0b' },
    { id: 'environment', name: 'Environment', icon: '🌍', color: '#22c55e' },
    { id: 'politics', name: 'Politics', icon: '🏛️', color: '#8b5cf6' },
    { id: 'entertainment', name: 'Entertainment', icon: '🎬', color: '#ec4899' },
    { id: 'sports', name: 'Sports', icon: '⚽', color: '#f97316' }
  ];

  const tabs = [
    { id: 'trending', name: 'Trending', icon: FiTrendingUp, color: '#3b82f6' },
    { id: 'recommendations', name: 'For You', icon: FiUser, color: '#10b981' },
    { id: 'search', name: 'Search', icon: FiSearch, color: '#8b5cf6' }
  ];

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: darkMode ? '#1e293b' : '#fff',
            color: darkMode ? '#fff' : '#333',
          },
        }}
      />
      
      {/* Animated Background */}
      <div className="animated-bg">
        <div className="gradient-orb or1"></div>
        <div className="gradient-orb or2"></div>
        <div className="gradient-orb or3"></div>
      </div>

      {/* Header */}
      <motion.header 
        className="header"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 100 }}
      >
        <div className="header-content">
          <motion.div 
            className="logo-container"
            whileHover={{ scale: 1.05 }}
          >
            <div className="logo-icon">🤖</div>
            <h1 className="logo-text">
              <span className="gradient-text">AI News</span>
              <span className="light-text">Aggregator</span>
            </h1>
          </motion.div>

          <div className="header-actions">
            {/* Connection Status */}
            <motion.div 
              className={`connection-status ${apiStatus}`}
              whileHover={{ scale: 1.05 }}
              title={apiStatus === 'connected' ? 'Connected to server' : 'Server disconnected'}
            >
              <span className="status-dot"></span>
              <span className="status-text">
                {apiStatus === 'connected' ? 'Live' : 'Offline'}
              </span>
            </motion.div>

            {/* Last Updated */}
            <motion.div 
              className="last-updated"
              whileHover={{ scale: 1.05 }}
            >
              <FiRefreshCw className={loading ? 'spinning' : ''} />
              <span>{lastUpdated.toLocaleTimeString()}</span>
            </motion.div>

            {/* Refresh Button */}
            <motion.button 
              className="icon-btn"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleRefresh}
              disabled={loading}
            >
              <FiRefreshCw className={loading ? 'spinning' : ''} />
            </motion.button>

            {/* Preferences Button */}
            <motion.button 
              className="icon-btn"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowPreferences(true)}
            >
              <FiSettings />
            </motion.button>

            {/* Theme Toggle */}
            <motion.button 
              className="theme-toggle"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setDarkMode(!darkMode)}
            >
              <motion.div
                animate={{ rotate: darkMode ? 180 : 0 }}
                transition={{ duration: 0.5 }}
              >
                {darkMode ? <FiSun /> : <FiMoon />}
              </motion.div>
            </motion.button>

            {/* Mobile Menu Button */}
            <motion.button 
              className="mobile-menu-btn"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowMobileMenu(!showMobileMenu)}
            >
              <div className={`hamburger ${showMobileMenu ? 'active' : ''}`}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Preferences Modal */}
      <AnimatePresence>
        {showPreferences && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowPreferences(false)}
          >
            <motion.div 
              className="modal-content"
              initial={{ scale: 0.8, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.8, y: 50 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="modal-header">
                <h2>Your Interests</h2>
                <p>Select topics to personalize your news feed</p>
              </div>

              <div className="preferences-grid">
                {availableTopics.map(topic => (
                  <motion.label 
                    key={topic.id} 
                    className={`preference-card ${userPreferences.includes(topic.id) ? 'selected' : ''}`}
                    style={{ borderColor: topic.color }}
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <input
                      type="checkbox"
                      checked={userPreferences.includes(topic.id)}
                      onChange={() => handlePreferenceChange(topic.id)}
                    />
                    <span className="pref-icon">{topic.icon}</span>
                    <span className="pref-name">{topic.name}</span>
                    {userPreferences.includes(topic.id) && (
                      <motion.div 
                        className="check-mark"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                      >
                        ✓
                      </motion.div>
                    )}
                  </motion.label>
                ))}
              </div>

              <div className="modal-actions">
                <motion.button 
                  className="btn btn-primary"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={savePreferences}
                  disabled={loading}
                >
                  {loading ? 'Saving...' : 'Save Preferences'}
                </motion.button>
                <motion.button 
                  className="btn btn-secondary"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setShowPreferences(false)}
                >
                  Cancel
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Navigation */}
      <nav className="navigation">
        <div className="nav-container">
          {/* Desktop Tabs */}
          <div className="tabs">
            {tabs.map(tab => (
              <motion.button
                key={tab.id}
                className={`tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
                whileHover={{ y: -2 }}
                whileTap={{ y: 0 }}
              >
                <tab.icon style={{ color: activeTab === tab.id ? tab.color : 'inherit' }} />
                <span>{tab.name}</span>
                {activeTab === tab.id && (
                  <motion.div 
                    className="tab-indicator"
                    layoutId="tabIndicator"
                    style={{ backgroundColor: tab.color }}
                  />
                )}
              </motion.button>
            ))}
          </div>

          {/* Trending Topics Bar */}
          <motion.div 
            className="trending-topics-bar"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="trending-label">
              <FiTrendingUp /> Trending Now
            </div>
            <div className="topics-scroll">
              {trendingTopics.map((topic, index) => (
                <motion.span 
                  key={index} 
                  className="trending-topic"
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    setActiveTab('search');
                    // You can implement search with this topic
                  }}
                >
                  #{topic}
                </motion.span>
              ))}
            </div>
          </motion.div>

          {/* Mobile Menu */}
          <AnimatePresence>
            {showMobileMenu && (
              <motion.div 
                className="mobile-menu"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                {tabs.map(tab => (
                  <motion.button
                    key={tab.id}
                    className={`mobile-tab ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => {
                      setActiveTab(tab.id);
                      setShowMobileMenu(false);
                    }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <tab.icon />
                    <span>{tab.name}</span>
                  </motion.button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </nav>

      {/* Main Content */}
      <motion.main 
        className="main-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'trending' && <Trending />}
            {activeTab === 'recommendations' && (
              <Recommendations userId={1} preferences={userPreferences} />
            )}
            {activeTab === 'search' && <Search />}
          </motion.div>
        </AnimatePresence>
      </motion.main>
    </div>
  );
}

export default App;