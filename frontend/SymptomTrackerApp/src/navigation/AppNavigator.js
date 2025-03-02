import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import * as SecureStore from 'expo-secure-store';

import LoginScreen from '../screens/LoginScreen';
import SignupScreen from '../screens/SignUpScreen';
import HomeScreen from '../screens/HomeScreen';
// Import other screens as needed

const Stack = createStackNavigator();

const AppNavigator = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [userToken, setUserToken] = useState(null);

  useEffect(() => {
    // Check if user is logged in when the app starts
    const bootstrapAsync = async () => {
      let token = null;
      try {
        token = await SecureStore.getItemAsync('access_token');
      } catch (e) {
        console.error('Error getting token:', e);
      }

      setUserToken(token);
      setIsLoading(false);
    };

    bootstrapAsync();
  }, []);

  if (isLoading) {
    // You could return a loading screen here
    return null;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {userToken == null ? (
          // User isn't signed in
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Signup" component={SignupScreen} />
          </>
        ) : (
          // User is signed in
          <>
            <Stack.Screen name="Home" component={HomeScreen} />
            {/* Add more authenticated screens here */}
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;