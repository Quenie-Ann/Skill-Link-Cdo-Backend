// screens/Resident/MyRequests.js
// State + logic:  hooks/resident/useMyRequests.js
// Static data:    data/residentRequests.data.js (filters, detail rows, empty messages)
// Components:     components/resident/RequestCard.js
// Styles:         styles/MyRequests.styles.js

import React, { useRef, useEffect, } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity,
  Animated, FlatList, LayoutAnimation, Platform, UIManager,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useMyRequests } from '../../hooks/resident/useMyRequests';
import {
  MY_REQUESTS_FILTERS,
  REQUEST_DETAIL_ROWS,
  EMPTY_STATE_MESSAGES,
} from '../../data/residentRequests.data';
import RequestCard from '../../components/resident/RequestCard';
import styles      from '../../styles/MyRequests.styles';
import Colors      from '../../styles/colors';

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

export default function MyRequests({ route, navigation }) {
  const insets     = useSafeAreaInsets();
  const user       = route.params?.user ?? { full_name: 'Maria Santos' };
  const newRequest = route.params?.newRequest ?? null;

  const mr = useMyRequests(newRequest);

  // Entrance animation
  const pageAnim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.spring(pageAnim, { toValue: 1, tension: 55, friction: 10, useNativeDriver: true }).start();
  }, []);

  const makeSlide = anim => ({
    opacity: anim,
    transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }],
  });

  // Animated expand toggle
  function handleToggle(id) {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    mr.toggleExpand(id);
  }

  // Render inline detail panel
  function renderDetail(req) {
    return (
      <View style={styles.detailCard}>
        {REQUEST_DETAIL_ROWS.map(row => {
          const val = req[row.key];
          if (!val) return null;
          return (
            <View key={row.key} style={styles.detailRow}>
              <View style={styles.detailIconWrap}>
                <Ionicons name={row.icon} size={14} color={Colors.skillPrimary} />
              </View>
              <View style={styles.detailContent}>
                <Text style={styles.detailLabel}>{row.label}</Text>
                <Text style={styles.detailValue}>{val}</Text>
              </View>
            </View>
          );
        })}

        {/* Worker chip */}
        {req.worker && (
          <View style={styles.detailRow}>
            <View style={styles.detailIconWrap}>
              <Ionicons name="person-outline" size={14} color={Colors.skillPrimary} />
            </View>
            <View style={styles.detailContent}>
              <Text style={styles.detailLabel}>ASSIGNED WORKER</Text>
              <View style={styles.workerChip}>
                <LinearGradient
                  colors={[Colors.skillPrimary, Colors.emerald700]}
                  style={{ width: 24, height: 24, borderRadius: 6, alignItems: 'center', justifyContent: 'center' }}
                >
                  <Text style={{ fontSize: 11, fontWeight: '800', color: '#fff' }}>
                    {req.worker.charAt(0)}
                  </Text>
                </LinearGradient>
                <Text style={styles.workerChipText}>{req.worker}</Text>
                {req.daily_rate && (
                  <Text style={{ fontSize: 11, color: Colors.textMuted, marginLeft: 4 }}>
                    · ₱{req.daily_rate}/day
                  </Text>
                )}
              </View>
            </View>
          </View>
        )}

        {/* Rate Now CTA */}
        {req.status === 'completed' && !req.rated && (
          <TouchableOpacity style={styles.rateNowBtn} activeOpacity={0.75}>
            <Ionicons name="star-outline" size={14} color={Colors.amber} />
            <Text style={styles.rateNowText}>Rate {req.worker ?? 'this job'}</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  // Render per-filter empty state
  function renderEmpty() {
    const m = EMPTY_STATE_MESSAGES[mr.activeFilter];
    return (
      <View style={styles.emptyState}>
        <View style={styles.emptyIconWrap}>
          <Ionicons name={m.icon} size={30} color={Colors.borderBase} />
        </View>
        <Text style={styles.emptyText}>{m.title}</Text>
        <Text style={styles.emptySubText}>{m.sub}</Text>
        {mr.activeFilter === 'all' && (
          <TouchableOpacity style={styles.emptyBtn} onPress={() => navigation.navigate('ResidentDashboard')} activeOpacity={0.85}>
            <LinearGradient
              colors={[Colors.skillPrimary, Colors.emerald700]}
              start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
              style={styles.emptyBtnGrad}
            >
              <Ionicons name="add-circle-outline" size={16} color="#fff" />
              <Text style={styles.emptyBtnText}>Book a Service</Text>
            </LinearGradient>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />

      {/* Header bar */}
      <View style={[styles.headerBar, { paddingTop: insets.top + 8 }]}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()} activeOpacity={0.75}>
          <Ionicons name="chevron-back" size={20} color={Colors.textBody} />
        </TouchableOpacity>
        <View style={styles.headerTextBlock}>
          <Text style={styles.headerTitle}>My Requests</Text>
          <Text style={styles.headerSub}>RECENT ACTIVITY</Text>
        </View>
      </View>

      {/* Stats row */}
      <Animated.View style={[styles.statsWrap, makeSlide(pageAnim)]}>
        <View style={styles.statsRow}>
          {[
            { value: mr.totalCount,     label: 'Total',     color: Colors.skillDark,    bg: Colors.skillLight  },
            { value: mr.activeCount,    label: 'Active',    color: Colors.skillPrimary, bg: Colors.emerald100  },
            { value: mr.completedCount, label: 'Completed', color: Colors.amber,        bg: Colors.amberBg     },
          ].map(stat => (
            <View key={stat.label} style={[styles.statCard, { backgroundColor: stat.bg, borderColor: Colors.borderBase }]}>
              <Text style={[styles.statValue, { color: stat.color }]}>{stat.value}</Text>
              <Text style={styles.statLabel}>{stat.label}</Text>
            </View>
          ))}
        </View>
      </Animated.View>

      {/* Filter tabs */}
      <Animated.View style={[styles.filterWrap, makeSlide(pageAnim)]}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterScroll}>
          {MY_REQUESTS_FILTERS.map(f => {
            const isActive = mr.activeFilter === f.key;
            const count    = mr.countFor(f.key);
            return (
              <TouchableOpacity
                key={f.key}
                style={[styles.filterTab, isActive && styles.filterTabActive]}
                onPress={() => mr.setActiveFilter(f.key)}
                activeOpacity={0.75}
              >
                <Ionicons name={f.icon} size={13} color={isActive ? Colors.skillPrimary : Colors.textMuted} />
                <Text style={[styles.filterTabText, isActive && styles.filterTabTextActive]}>{f.label}</Text>
                <View style={[styles.filterCount, isActive && styles.filterCountActive]}>
                  <Text style={[styles.filterCountText, isActive && styles.filterCountTextActive]}>{count}</Text>
                </View>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </Animated.View>

      {/* Request list */}
      {mr.filteredRequests.length === 0 ? renderEmpty() : (
        <FlatList
          data={mr.filteredRequests}
          keyExtractor={item => String(item.id)}
          contentContainerStyle={[styles.listContent, { paddingBottom: insets.bottom + 32 }]}
          showsVerticalScrollIndicator={false}
          renderItem={({ item }) => (
            <>
              <RequestCard req={item} onPress={() => handleToggle(item.id)} />
              {mr.expandedId === item.id && renderDetail(item)}
            </>
          )}
        />
      )}
    </View>
  );
}