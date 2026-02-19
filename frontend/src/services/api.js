import axios from 'axios';
import { toast } from 'react-hot-toast';

const API_BASE_URL = 'http://192.168.56.1:8000';

console.log('🔌 Connecting to backend at:', API_BASE_URL);

// Cache for API responses
const cache = {
  trending: { data: null, timestamp: null },
  topics: { data: null, timestamp: null },
  search: {}
};

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

class NewsAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json',
      }
    });

    // Request interceptor for logging
    this.client.interceptors.request.use(
      config => {
        console.log(`📤 ${config.method.toUpperCase()} ${config.url}`, config.params || '');
        return config;
      },
      error => {
        console.error('📤 Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for logging
    this.client.interceptors.response.use(
      response => {
        console.log(`📥 ${response.status} ${response.config.url}`);
        return response;
      },
      error => {
        if (error.code === 'ECONNABORTED') {
          console.error('📥 Timeout Error:', error.message);
          toast.error('Request timeout. Please try again.');
        } else if (error.response) {
          console.error(`📥 ${error.response.status} Error:`, error.response.data);
          
          // Handle specific status codes
          switch (error.response.status) {
            case 404:
              toast.error('API endpoint not found');
              break;
            case 500:
              toast.error('Server error. Please try again later.');
              break;
            default:
              toast.error(`Error: ${error.response.status}`);
          }
        } else if (error.request) {
          console.error('📥 No Response:', error.message);
          toast.error('Cannot connect to server. Check if backend is running.');
        } else {
          console.error('📥 Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // Helper method to check cache
  isCacheValid(cacheEntry) {
    return cacheEntry.data && 
           cacheEntry.timestamp && 
           (Date.now() - cacheEntry.timestamp) < CACHE_DURATION;
  }

  async getTrendingNews(limit = 10, forceRefresh = false) {
    try {
      // Check cache first
      if (!forceRefresh && this.isCacheValid(cache.trending)) {
        console.log('📦 Using cached trending news');
        return cache.trending.data;
      }

      console.log('🔄 Fetching fresh trending news');
      const response = await this.client.get('/trending-news', {
        params: { limit }
      });
      
      // Update cache
      cache.trending = {
        data: response.data,
        timestamp: Date.now()
      };
      
      return response.data;
    } catch (error) {
      console.error('Error in getTrendingNews:', error);
      
      // Return cached data if available
      if (cache.trending.data) {
        console.log('📦 Returning cached data due to error');
        toast.info('Using cached data');
        return cache.trending.data;
      }
      
      throw error;
    }
  }

  async getRecommendations(userId = 1, limit = 10) {
    try {
      console.log('Fetching recommendations for user:', userId);
      const response = await this.client.get('/recommendations', {
        params: { user_id: userId, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error in getRecommendations:', error);
      
      // Fallback to trending news
      console.log('Falling back to trending news');
      toast.info('Showing trending news instead');
      return this.getTrendingNews(limit);
    }
  }

  async searchNews(query, limit = 10, forceRefresh = false) {
    try {
      if (!query || query.trim() === '') {
        throw new Error('Search query is required');
      }

      // Create cache key
      const cacheKey = `${query}_${limit}`;
      
      // Check cache first
      if (!forceRefresh && cache.search[cacheKey]) {
        const cached = cache.search[cacheKey];
        if (this.isCacheValid(cached)) {
          console.log(`📦 Using cached search results for "${query}"`);
          return cached.data;
        }
      }

      console.log(`🔄 Searching for: "${query}"`);
      const response = await this.client.get('/search', {
        params: { query: query.trim(), limit }
      });
      
      console.log(`✅ Found ${response.data?.length || 0} results`);
      
      // Update cache
      cache.search[cacheKey] = {
        data: response.data,
        timestamp: Date.now()
      };
      
      return response.data;
    } catch (error) {
      console.error('Error in searchNews:', error);
      
      // Return cached data if available
      const cacheKey = `${query}_${limit}`;
      if (cache.search[cacheKey]?.data) {
        console.log('📦 Returning cached search results due to error');
        toast.info('Using cached results');
        return cache.search[cacheKey].data;
      }
      
      throw error;
    }
  }

  async updateUserPreferences(userId, preferences) {
    try {
      if (!Array.isArray(preferences)) {
        throw new Error('Preferences must be an array');
      }

      console.log('Updating preferences for user:', userId, preferences);
      const response = await this.client.post(`/user/${userId}/preferences`, preferences);
      
      console.log('Preferences updated successfully');
      toast.success('Preferences saved!');
      
      // Clear cache that depends on preferences
      cache.recommendations = { data: null, timestamp: null };
      
      return response.data;
    } catch (error) {
      console.error('Error in updateUserPreferences:', error);
      
      if (error.response?.status === 404) {
        toast.error('User not found');
      } else {
        toast.error('Failed to save preferences');
      }
      
      throw error;
    }
  }

  async getTrendingTopics(forceRefresh = false) {
    try {
      // Check cache first
      if (!forceRefresh && this.isCacheValid(cache.topics)) {
        console.log('📦 Using cached trending topics');
        return cache.topics.data;
      }

      console.log('🔄 Fetching fresh trending topics');
      const response = await this.client.get('/trending-topics');
      
      // Default topics if response is empty
      const topics = response.data?.length > 0 
        ? response.data 
        : ['Technology', 'Science', 'Health', 'Climate', 'Business', 'AI'];
      
      // Update cache
      cache.topics = {
        data: topics,
        timestamp: Date.now()
      };
      
      return topics;
    } catch (error) {
      console.error('Error in getTrendingTopics:', error);
      
      // Return cached or default topics
      if (cache.topics.data) {
        return cache.topics.data;
      }
      
      return ['Technology', 'Science', 'Health', 'Climate', 'Business', 'AI'];
    }
  }

  // Clear all cache
  clearCache() {
    cache.trending = { data: null, timestamp: null };
    cache.topics = { data: null, timestamp: null };
    cache.search = {};
    cache.recommendations = { data: null, timestamp: null };
    console.log('🧹 Cache cleared');
    toast.success('Cache cleared');
  }

  // Check backend health
  async checkHealth() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      return null;
    }
  }
}

// Create and export instance
export const api = new NewsAPI();

// Also export as default
export default api;