// screens/Resident/ResidentDashboard.js
// Main resident portal screen.
// Displays: greeting header, hero CTA card, stat counters,
// popular services horizontal scroll, and the My Requests list.
// The 3-step BookingModal is extracted into components/resident/BookingModal.js.

import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, Animated,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import RequestCard  from '../../components/resident/RequestCard';
import BookingModal from '../../components/resident/BookingModal';
import { SERVICE_CATEGORIES } from '../../constants/services';
import styles from '../../styles/ResidentDashboard.styles';
import Colors from '../../styles/colors';

// Static seed data — mirrors web app resident mock state
const INITIAL_REQUESTS = [
  {
    id: 1, title: 'Electrical Repair',
    service: 'electrical', status: 'matched',
    date: 'March 21, 2026', daily_rate: 650,
    worker: 'Juan Dela Cruz', rated: false,
  },
  {
    id: 2, title: 'Kitchen Plumbing',
    service: 'plumbing', status: 'completed',
    date: 'Feb 24, 2026', daily_rate: 550,
    worker: 'Pedro Santos', rated: false,
  },
  {
    id: 3, title: 'Roof Carpentry',
    service: 'carpentry', status: 'completed',
    date: 'Feb 18, 2026', daily_rate: 500,
    worker: 'Ramon Reyes', rated: true,
  },
  {
    id: 4, title: 'Cabinet Installation',
    service: 'carpentry', status: 'in_progress',
    date: 'Feb 15, 2026', daily_rate: 600,
    worker: 'Pedro Santos', rated: false,
  },
];

export default function ResidentDashboard({ route, navigation }) {
  const insets = useSafeAreaInsets();
  const user   = route.params?.user ?? { full_name: 'Maria Santos', role: 'resident' };

  const [requests,    setRequests]    = useState(INITIAL_REQUESTS);
  const [modalOpen,   setModalOpen]   = useState(false);
  const [preselected, setPreselected] = useState(null);

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

  // Open booking modal — optional preselected category skips to Step 2
  function openModal(category = null) {
    setPreselected(category);
    setModalOpen(true);
  }

  // Prepend new request submitted from BookingModal
  function handleNewRequest(data) {
    setRequests(prev => [data, ...prev]);
  }

  // Derived stats for the 3 stat cards
  const pendingCount = requests.filter(r => r.status === 'pending').length;
  const activeCount  = requests.filter(r => ['matched', 'in_progress'].includes(r.status)).length;
  const doneCount    = requests.filter(r => r.status === 'completed').length;

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={[
          styles.scroll,
          { paddingTop: insets.top + 16, paddingBottom: insets.bottom + 32 },
        ]}
        showsVerticalScrollIndicator={false}
      >

        {/* ── Greeting header ── */}
        <Animated.View style={[styles.header, makeSlide(headerAnim)]}>
          <View>
            <Text style={styles.greeting}>Good day,</Text>
            <Text style={styles.userName}>{user.full_name}</Text>
            <View style={styles.roleBadge}>
              <Ionicons name="shield-checkmark-outline" size={10} color={Colors.skillDark} />
              <Text style={styles.roleText}>RESIDENT</Text>
            </View>
          </View>
          <TouchableOpacity
            onPress={() => navigation.replace('Login')}
            style={styles.logoutBtn}
            activeOpacity={0.75}
          >
            <Ionicons name="log-out-outline" size={18} color={Colors.textMuted} />
          </TouchableOpacity>
        </Animated.View>

        {/* ── Hero card ── */}
        <Animated.View style={makeSlide(cardAnim)}>
          <LinearGradient
            colors={[Colors.skillDark, '#054d38']}
            style={styles.heroCard}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
          >
            <View style={styles.heroCircle1} />
            <View style={styles.heroCircle2} />

            <View style={styles.heroPill}>
              <Ionicons name="shield-checkmark-outline" size={10} color="#6ee7b7" />
              <Text style={styles.heroPillText}>BARANGAY VERIFIED WORKERS</Text>
            </View>

            <Text style={styles.heroTitle}>How can we help{'\n'}you today?</Text>
            <Text style={styles.heroSub}>
              Connect with barangay-verified workers{'\n'}for all your household needs.
            </Text>

            <TouchableOpacity
              onPress={() => openModal()}
              style={styles.heroBtn}
              activeOpacity={0.85}
            >
              <Ionicons name="add-circle-outline" size={16} color={Colors.skillDark} />
              <Text style={styles.heroBtnText}>Book a New Service</Text>
            </TouchableOpacity>
          </LinearGradient>
        </Animated.View>

        {/* ── Stats row ── */}
        <Animated.View style={[styles.statsRow, makeSlide(cardAnim)]}>
          {[
            { value: pendingCount, label: 'Pending',   color: Colors.amber,        bg: Colors.amberBg    },
            { value: activeCount,  label: 'Active',    color: Colors.skillPrimary, bg: Colors.emerald100 },
            { value: doneCount,    label: 'Completed', color: Colors.skillDark,    bg: Colors.skillLight },
          ].map(stat => (
            <View
              key={stat.label}
              style={[styles.statCard, { backgroundColor: stat.bg, borderColor: Colors.borderBase }]}
            >
              <Text style={[styles.statValue, { color: stat.color }]}>{stat.value}</Text>
              <Text style={styles.statLabel}>{stat.label}</Text>
            </View>
          ))}
        </Animated.View>

        {/* ── Popular services ── */}
        <Animated.View style={makeSlide(listAnim)}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Popular Services</Text>
            <TouchableOpacity activeOpacity={0.7}>
              <Text style={styles.seeAll}>Browse all</Text>
            </TouchableOpacity>
          </View>

          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.servicesScroll}
          >
            {SERVICE_CATEGORIES.map(cat => (
              <TouchableOpacity
                key={cat.value}
                style={[
                  styles.serviceChip,
                  { backgroundColor: cat.bg, borderColor: cat.color + '40' },
                ]}
                onPress={() => openModal(cat)}
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

        {/* ── My Requests ── */}
        <Animated.View style={makeSlide(listAnim)}>
          <View style={[styles.sectionHeader, { marginTop: 8 }]}>
            <Text style={styles.sectionTitle}>My Requests</Text>
            <View style={styles.countBadge}>
              <Text style={styles.countText}>{requests.length}</Text>
            </View>
          </View>

          {requests.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="clipboard-outline" size={32} color={Colors.borderBase} />
              <Text style={styles.emptyText}>No requests yet</Text>
              <Text style={styles.emptySubText}>
                Tap "Book a New Service" to get started
              </Text>
            </View>
          ) : (
            requests.map(req => (
              <RequestCard key={req.id} req={req} />
            ))
          )}
        </Animated.View>

      </ScrollView>

      {/* ── Booking Modal ── */}
      <BookingModal
        visible={modalOpen}
        preselectedCategory={preselected}
        onClose={() => setModalOpen(false)}
        onSubmit={handleNewRequest}
      />

    </View>
  );
}