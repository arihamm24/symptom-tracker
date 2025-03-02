import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { login } from '../services/auth';
import * as SecureStore from 'expo-secure-store';

const LoginScreen = ({ navigation }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await login(username, password);
      // Store user data and tokens securely
      await SecureStore.setItemAsync('access_token', response.access);
      await SecureStore.setItemAsync('refresh_token', response.refresh);
      await SecureStore.setItemAsync('user_data', JSON.stringify(response.user));
      
      // Navigate to the main app
      navigation.reset({
        index: 0,
        routes: [{ name: 'Home' }],
      });
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
      style={styles.container}
    >
      <View style={styles.innerContainer}>
        <Text style={styles.headerText}>ChronicCare</Text>
        
        <View style={styles.inputContainer}>
          <Text style={styles.labelText}>Username</Text>
          <TextInput
            style={styles.input}
            placeholder="Username"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.labelText}>Password</Text>
          <TextInput
            style={styles.input}
            placeholder="Password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
        </View>

        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        <TouchableOpacity 
          style={styles.button} 
          onPress={handleLogin}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>{isLoading ? 'Signing In...' : 'Sign In'}</Text>
        </TouchableOpacity>

        <View style={styles.signupContainer}>
          <Text style={styles.signupText}>Don't have an account?</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Signup')}>
            <Text style={styles.signupLink}>Create one here</Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1E1E1E',
  },
  innerContainer: {
    flex: 1,
    backgroundColor: '#E6F0FF',
    margin: 0,
    padding: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerText: {
    fontSize: 38,
    fontWeight: 'bold',
    color: '#3F51B5',
    marginBottom: 40,
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  labelText: {
    fontSize: 18,
    color: '#3F51B5',
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    width: '100%',
  },
  button: {
    backgroundColor: '#3F51B5',
    borderRadius: 8,
    padding: 15,
    width: '60%',
    alignItems: 'center',
    marginTop: 20,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  errorText: {
    color: 'red',
    marginTop: 10,
  },
  signupContainer: {
    flexDirection: 'column',
    marginTop: 30,
    alignItems: 'center',
  },
  signupText: {
    fontSize: 16,
    color: '#3F51B5',
  },
  signupLink: {
    fontSize: 16,
    color: '#3F51B5',
    textDecorationLine: 'underline',
    fontWeight: 'bold',
    marginTop: 5,
  },
});

export default LoginScreen;