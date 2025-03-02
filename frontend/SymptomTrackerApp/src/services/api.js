import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// The IP address needs to be your computer's IP address, not localhost
// For Android emulator use: 10.0.2.2 instead of localhost
// For iOS simulator, you can use localhost
const API_URL = 'http://10.0.2.2:8000/api/';  // Adjust this URL based on your setup

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the auth token in requests
api.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is 401 (Unauthorized) and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Get the refresh token
        const refreshToken = await SecureStore.getItemAsync('refresh_token');
        
        if (!refreshToken) {
          // No refresh token, so redirect to login
          throw new Error('No refresh token available');
        }
        
        // Attempt to refresh the token
        const response = await axios.post(`${API_URL}auth/refresh/`, {
          refresh: refreshToken
        });
        
        // Store the new access token
        await SecureStore.setItemAsync('access_token', response.data.access);
        
        // Update the authorization header
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // Clear tokens and redirect to login (will be handled in the app navigation)
        await SecureStore.deleteItemAsync('access_token');
        await SecureStore.deleteItemAsync('refresh_token');
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;