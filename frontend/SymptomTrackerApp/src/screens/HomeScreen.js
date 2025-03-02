import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { logout } from '../services/auth';

const HomeScreen = ({ navigation }) => {
  const handleLogout = async () => {
    try {
      await logout();
      navigation.reset({
        index: 0,
        routes: [{ name: 'Login' }],
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to ChronicCare</Text>
      <Text style={styles.subtitle}>You are now logged in!</Text>
      
      <TouchableOpacity 
        style={styles.button}
        onPress={() => navigation.navigate('Settings')}
      >
        <Text style={styles.buttonText}>Go to Settings</Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={[styles.button, styles.logoutButton]}
        onPress={handleLogout}
      >
        <Text style={styles.buttonText}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
};

export default HomeScreen;