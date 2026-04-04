// navigation/ResidentStack.js
// Stack navigator for all resident-role screens.
// Screens registered here:
//   ResidentDashboard — main portal (root of this stack)
//   FindWorkers       — ML match results after booking flow completes  (Phase 2)
//   MyRequests        — full request history with filter tabs           (Phase 3)

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import ResidentDashboard from '../screens/Resident/ResidentDashboard';
import FindWorkers       from '../screens/Resident/FindWorkers';
import MyRequests        from '../screens/Resident/MyRequests';

const Stack = createNativeStackNavigator();

export default function ResidentStack({ route }) {
  const user = route.params?.user;

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen
        name="ResidentDashboard"
        component={ResidentDashboard}
        initialParams={{ user }}
      />
      <Stack.Screen
        name="FindWorkers"
        component={FindWorkers}
      />
      <Stack.Screen
        name="MyRequests"
        component={MyRequests}
        initialParams={{ user }}
      />
    </Stack.Navigator>
  );
}