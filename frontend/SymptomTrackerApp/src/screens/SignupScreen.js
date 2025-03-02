import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { register } from '../services/auth';
import * as SecureStore from 'expo-secure-store';

const SignupScreen = ({ navigation }) => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSignup = async () => {
    if (!fullName || !email || !phoneNumber || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);
    setError('');

    // Parse full name into first and last name
    const nameParts = fullName.trim().split(' ');
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';
    
    try {
      // Prepare registration data according to your backend expectations
      const userData = {
        username: email.split('@')[0], // Generate username from email
        email: email,
        first_name: firstName,
        last_name: lastName,
        password: password,
        password2: confirmPassword,
        date_of_birth: new Date().toISOString().split('T')[0], // Default date, you may want to collect this
        profile: {
          phone_number: phoneNumber
        }
      };

      const response = await register(userData);
      
      // If registration is successful, proceed to login
      if (response && response.user) {
        // Store tokens if they are returned from registration
        if (response.access) {
          await SecureStore.setItemAsync('access_token', response.access);
          await SecureStore.setItemAsync('refresh_token', response.refresh);
          await SecureStore.setItemAsync('user_data', JSON.stringify(response.user));
          
          // Navigate to the main app
          navigation.reset({
            index: 0,
            routes: [{ name: 'Home' }],
          });
        } else {
          // Otherwise go to login screen
          navigation.navigate('Login');
        }
      }
    } catch (error) {
      setError(
        error.response?.data?.detail || 
        Object.values(error.response?.data || {}).flat().join(', ') || 
        'Registration failed'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.innerContainer}>
          <Text style={styles.headerText}>Welcome to ChronicCare!</Text>

          <View style={styles.inputContainer}>
            <Text style={styles.labelText}>Name</Text>
            <TextInput
              style={styles.input}
              placeholder="First and Last Name"
              value={fullName}
              onChangeText={setFullName}
            />
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.labelText}>Email Address</Text>
            <TextInput
              style={styles.input}
              placeholder="user@mail.com"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
            />
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.labelText}>Phone Number</Text>
            <TextInput
              style={styles.input}
              placeholder="+1 123-5678"
              value={phoneNumber}
              onChangeText={setPhoneNumber}
              keyboardType="phone-pad"
            />
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.labelText}>Password</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter Password"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.labelText}>Confirm Password</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter Password"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              secureTextEntry
            />
          </View>

          {error ? <Text style={styles.errorText}>{error}</Text> : null}

          <TouchableOpacity 
            style={styles.button} 
            onPress={handleSignup}
            disabled={isLoading}
          >
            <Text style={styles.buttonText}>{isLoading ? 'Creating...' : 'Create Account'}</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

export default SignupScreen;