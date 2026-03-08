// App.js
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Auth screen — at screens root, shared across roles
import LoginScreen       from './screens/LoginScreen';

// Role-based screens
import ResidentDashboard from './screens/Resident/ResidentDashboard';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Login"     component={LoginScreen}       />
          <Stack.Screen name="Dashboard" component={ResidentDashboard} />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
