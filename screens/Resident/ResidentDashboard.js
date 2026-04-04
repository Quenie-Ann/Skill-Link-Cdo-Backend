// screens/Resident/ResidentDashboard.js
// State + logic:  hooks/resident/useResidentDashboard.js
// Static data:    data/services.data.js (service categories for popular services strip)
// Components:     components/resident/RequestCard.js, BookingModal.js
// Styles:         styles/ResidentDashboard.styles.js

import React, { useRef, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Animated } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useResidentDashboard } from '../../hooks/resident/useResidentDashboard';
import { SERVICE_CATEGORIES }   from '../../data/services.data';
import RequestCard               from '../../components/resident/RequestCard';
import BookingModal              from '../../components/resident/BookingModal';
import styles                    from '../../styles/ResidentDashboard.styles';
import Colors                    from '../../styles/colors';

export default function ResidentDashboard({ route, navigation }) {
  const insets = useSafeAreaInsets();
  const user   = route.params?.user ?? { full_name: 'Maria Santos', role: 'resident' };

  const db = useResidentDashboard(navigation);

  // Entrance animations
  const headerAnim = useRef(new Animated.Value(0)).current;
  const cardAnim   = useRef(new Animated.Value(0)).current;
  const listAnim   = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.stagger(100, [
      Animated.spring(headerAnim, { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
      Animated.spring(cardAnim,   { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
      Animated.spring(listAnim,   { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
    ]).start();
  }, []);

  const makeSlide = anim => ({
    opacity: anim,
    transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }],
  });

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={[styles.scroll, { paddingTop: insets.top + 16, paddingBottom: insets.bottom + 32 }]}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <Animated.View style={[styles.header, makeSlide(headerAnim)]}>
          <View>
            <Text style={styles.greeting}>Good day,</Text>
            <Text style={styles.userName}>{user.full_name}</Text>
            <View style={styles.roleBadge}>
              <Ionicons name="shield-checkmark-outline" size={10} color={Colors.skillDark} />
              <Text style={styles.roleText}>RESIDENT</Text>
            </View>
          </View>
          <TouchableOpacity onPress={() => navigation.replace('Login')} style={styles.logoutBtn} activeOpacity={0.75}>
            <Ionicons name="log-out-outline" size={18} color={Colors.textMuted} />
          </TouchableOpacity>
        </Animated.View>

        {/* Hero card */}
        <Animated.View style={makeSlide(cardAnim)}>
          <LinearGradient colors={[Colors.skillDark, '#054d38']} style={styles.heroCard} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}>
            <View style={styles.heroCircle1} />
            <View style={styles.heroCircle2} />
            <View style={styles.heroPill}>
              <Ionicons name="shield-checkmark-outline" size={10} color="#6ee7b7" />
              <Text style={styles.heroPillText}>BARANGAY VERIFIED WORKERS</Text>
            </View>
            <Text style={styles.heroTitle}>How can we help{'\n'}you today?</Text>
            <Text style={styles.heroSub}>Connect with barangay-verified workers{'\n'}for all your household needs.</Text>
            <TouchableOpacity onPress={() => db.openModal()} style={styles.heroBtn} activeOpacity={0.85}>
              <Ionicons name="add-circle-outline" size={16} color={Colors.skillDark} />
              <Text style={styles.heroBtnText}>Book a New Service</Text>
            </TouchableOpacity>
          </LinearGradient>
        </Animated.View>

        {/* Stats row*/}
        <Animated.View style={[styles.statsRow, makeSlide(cardAnim)]}>
          {[
            { value: db.pendingCount, label: 'Pending',   color: Colors.amber,        bg: Colors.amberBg    },
            { value: db.activeCount,  label: 'Active',    color: Colors.skillPrimary, bg: Colors.emerald100 },
            { value: db.doneCount,    label: 'Completed', color: Colors.skillDark,    bg: Colors.skillLight },
          ].map(stat => (
            <View key={stat.label} style={[styles.statCard, { backgroundColor: stat.bg, borderColor: Colors.borderBase }]}>
              <Text style={[styles.statValue, { color: stat.color }]}>{stat.value}</Text>
              <Text style={styles.statLabel}>{stat.label}</Text>
            </View>
          ))}
        </Animated.View>

        {/* Popular services */}
        <Animated.View style={makeSlide(listAnim)}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Popular Services</Text>
            <TouchableOpacity activeOpacity={0.7}>
              <Text style={styles.seeAll}>Browse all</Text>
            </TouchableOpacity>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.servicesScroll}>
            {SERVICE_CATEGORIES.map(cat => (
              <TouchableOpacity
                key={cat.value}
                style={[styles.serviceChip, { backgroundColor: cat.bg, borderColor: cat.color + '40' }]}
                onPress={() => db.openModal(cat)}
                activeOpacity={0.75}
              >
                <View style={[styles.serviceChipIcon, { backgroundColor: cat.color + '25' }]}>
                  <Ionicons name={cat.icon} size={20} color={cat.color} />
                </View>
                <Text style={[styles.serviceChipLabel, { color: cat.color }]}>{cat.label}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </Animated.View>

        {/* My Requests */}
        <Animated.View style={makeSlide(listAnim)}>
          <View style={[styles.sectionHeader, { marginTop: 8 }]}>
            <Text style={styles.sectionTitle}>My Requests</Text>
            <TouchableOpacity activeOpacity={0.7} onPress={() => navigation.navigate('MyRequests', { user })}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>

          {db.requests.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="clipboard-outline" size={32} color={Colors.borderBase} />
              <Text style={styles.emptyText}>No requests yet</Text>
              <Text style={styles.emptySubText}>Tap "Book a New Service" to get started</Text>
            </View>
          ) : (
            db.requests.slice(0, 3).map(req => (
              <RequestCard key={req.id} req={req} />
            ))
          )}
        </Animated.View>
      </ScrollView>

      {/* Booking Modal */}
      <BookingModal
        visible={db.modalOpen}
        preselectedCategory={db.preselected}
        onClose={db.closeModal}
        onSubmit={db.handleNewRequest}
      />
    </View>
  );
}