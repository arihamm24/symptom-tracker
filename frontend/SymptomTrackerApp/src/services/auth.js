import api from './api';
import * as SecureStore from 'expo-secure-store';

export const login = async (username, password) => {
  try {
    const response = await api.post('auth/login/', { username, password });
    return response.data;
  } catch (error) {
    console.error('Login error:', error.response?.data || error.message);
    throw error;
  }
};

export const register = async (userData) => {
  try {
    const response = await api.post('auth/register/', userData);
    return response.data;
  } catch (error) {
    console.error('Registration error:', error.response?.data || error.message);
    throw error;
  }
};

export const logout = async () => {
  try {
    const refreshToken = await SecureStore.getItemAsync('refresh_token');
    if (refreshToken) {
      await api.post('auth/logout/', { refresh: refreshToken });
    }
    
    // Clear all stored tokens and data
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
    await SecureStore.deleteItemAsync('user_data');
  } catch (error) {
    console.error('Logout error:', error);
    // Still delete the tokens even if the API call fails
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
    await SecureStore.deleteItemAsync('user_data');
    throw error;
  }
};

export const isAuthenticated = async () => {
  const token = await SecureStore.getItemAsync('access_token');
  return !!token;
};