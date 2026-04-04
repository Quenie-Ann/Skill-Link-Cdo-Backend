// screens/Resident/MyRequests.js
// Full request history screen for the resident portal.
// Displays:
//   - Summary stats row  (Total, Active, Completed)
//   - Status filter tabs (All | Pending | Active | Completed)
//   - Scrollable list of RequestCards, each expandable for detail
//   - Inline detail panel: issue, budget, preferred start, worker,
//     address, and a Rate Now CTA for unrated completed jobs
//   - Empty state per filter with a Book Now shortcut
//
// Navigation params:
//   user        {object} — authenticated resident (passed from ResidentStack)
//   newRequest  {object} — optional freshly submitted request to prepend

import React, { useState, useRef, useEffect, useMemo } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity,
  Animated, FlatList, LayoutAnimation,
  Platform, UIManager,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import RequestCard from '../../components/resident/RequestCard';
import { RESIDENT_REQUESTS } from '../../constants/residentData';
import { SERVICE_CATEGORIES } from '../../constants/services';
import styles from '../../styles/MyRequests.styles';
import Colors from '../../styles/colors';

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// Filter tab definitions 
const FILTERS = [
  { key: 'all',       label: 'All',       icon: 'list-outline'             },
  { key: 'pending',   label: 'Pending',   icon: 'time-outline'             },
  { key: 'active',    label: 'Active',    icon: 'flash-outline'            },
  { key: 'completed', label: 'Completed', icon: 'checkmark-circle-outline' },
];

// Maps filter key → matching status values
const FILTER_STATUSES = {
  all:       ['pending', 'matched', 'in_progress', 'completed'],
  pending:   ['pending'],
  active:    ['matched', 'in_progress'],
  completed: ['completed'],
};

// Detail row config for the inline expanded panel
const DETAIL_ROWS = [
  { key: 'issue',           label: 'PROBLEM',         icon: 'alert-circle-outline'  },
  { key: 'budget',          label: 'BUDGET',          icon: 'cash-outline'          },
  { key: 'preferred_start', label: 'PREFERRED START', icon: 'time-outline'          },
  { key: 'address',         label: 'ADDRESS',         icon: 'location-outline'      },
];

export default function MyRequests({ route, navigation }) {
  const insets = useSafeAreaInsets();
  const user   = route.params?.user ?? { full_name: 'Maria Santos' };

  // Prepend any freshly submitted request passed from ResidentDashboard
  const [requests, setRequests] = useState(() => {
    const extra = route.params?.newRequest;
    return extra ? [extra, ...RESIDENT_REQUESTS] : RESIDENT_REQUESTS;
  });

  const [activeFilter, setActiveFilter] = useState('all');
  const [expandedId,   setExpandedId]   = useState(null);

  // Entrance animation
  const pageAnim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.spring(pageAnim, { toValue: 1, tension: 55, friction: 10, useNativeDriver: true }).start();
  }, []);

  const makeSlide = anim => ({
    opacity: anim,
    transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }],
  });

  // Derived counts for stat cards 
  const totalCount     = requests.length;
  const activeCount    = requests.filter(r => ['matched', 'in_progress'].includes(r.status)).length;
  const completedCount = requests.filter(r => r.status === 'completed').length;

  // Filtered list 
  const filteredRequests = useMemo(() => {
    const allowed = FILTER_STATUSES[activeFilter];
    return requests.filter(r => allowed.includes(r.status));
  }, [requests, activeFilter]);

  // Count per filter tab (for badge pills)
  const countFor = key => {
    const allowed = FILTER_STATUSES[key];
    return requests.filter(r => allowed.includes(r.status)).length;
  };

  // Toggle expanded detail 
  function toggleExpand(id) {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedId(prev => (prev === id ? null : id));
  }

  // Render inline detail panel 
  function renderDetail(req) {
    const cat = SERVICE_CATEGORIES.find(c => c.value === req.service);
    return (
      <View style={styles.detailCard}>
        {DETAIL_ROWS.map(row => {
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

        {/* Worker chip — shown once matched or beyond */}
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
                  style={{
                    width: 24, height: 24, borderRadius: 6,
                    alignItems: 'center', justifyContent: 'center',
                  }}
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

        {/* Rate Now CTA — completed + unrated only */}
        {req.status === 'completed' && !req.rated && (
          <TouchableOpacity style={styles.rateNowBtn} activeOpacity={0.75}>
            <Ionicons name="star-outline" size={14} color={Colors.amber} />
            <Text style={styles.rateNowText}>Rate {req.worker ?? 'this job'}</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  // Empty state per filter 
  function renderEmpty() {
    const messages = {
      all:       { icon: 'clipboard-outline',        title: 'No requests yet',      sub: 'Book your first service to get started.' },
      pending:   { icon: 'time-outline',             title: 'No pending requests',  sub: 'Pending requests are waiting to be matched.' },
      active:    { icon: 'flash-outline',            title: 'No active jobs',       sub: 'Once a worker accepts your offer, it appears here.' },
      completed: { icon: 'checkmark-circle-outline', title: 'No completed jobs yet',sub: 'Finished requests will show up here.' },
    };
    const m = messages[activeFilter];
    return (
      <View style={styles.emptyState}>
        <View style={styles.emptyIconWrap}>
          <Ionicons name={m.icon} size={30} color={Colors.borderBase} />
        </View>
        <Text style={styles.emptyText}>{m.title}</Text>
        <Text style={styles.emptySubText}>{m.sub}</Text>
        {activeFilter === 'all' && (
          <TouchableOpacity
            style={styles.emptyBtn}
            onPress={() => navigation.navigate('ResidentDashboard')}
            activeOpacity={0.85}
          >
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

      {/* ── Header bar ── */}
      <View style={[styles.headerBar, { paddingTop: insets.top + 8 }]}>
        <TouchableOpacity
          style={styles.backBtn}
          onPress={() => navigation.goBack()}
          activeOpacity={0.75}
        >
          <Ionicons name="chevron-back" size={20} color={Colors.textBody} />
        </TouchableOpacity>
        <View style={styles.headerTextBlock}>
          <Text style={styles.headerTitle}>My Requests</Text>
          <Text style={styles.headerSub}>RECENT ACTIVITY</Text>
        </View>
      </View>

      {/* ── Stats row ── */}
      <Animated.View style={[styles.statsWrap, makeSlide(pageAnim)]}>
        <View style={styles.statsRow}>
          {[
            { value: totalCount,     label: 'Total',     color: Colors.skillDark,    bg: Colors.skillLight  },
            { value: activeCount,    label: 'Active',    color: Colors.skillPrimary, bg: Colors.emerald100  },
            { value: completedCount, label: 'Completed', color: Colors.amber,        bg: Colors.amberBg     },
          ].map(stat => (
            <View
              key={stat.label}
              style={[styles.statCard, { backgroundColor: stat.bg, borderColor: Colors.borderBase }]}
            >
              <Text style={[styles.statValue, { color: stat.color }]}>{stat.value}</Text>
              <Text style={styles.statLabel}>{stat.label}</Text>
            </View>
          ))}
        </View>
      </Animated.View>

      {/* ── Filter tabs ── */}
      <Animated.View style={[styles.filterWrap, makeSlide(pageAnim)]}>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.filterScroll}
        >
          {FILTERS.map(f => {
            const isActive = activeFilter === f.key;
            const count    = countFor(f.key);
            return (
              <TouchableOpacity
                key={f.key}
                style={[styles.filterTab, isActive && styles.filterTabActive]}
                onPress={() => {
                  setExpandedId(null);
                  setActiveFilter(f.key);
                }}
                activeOpacity={0.75}
              >
                <Ionicons
                  name={f.icon}
                  size={13}
                  color={isActive ? Colors.skillPrimary : Colors.textMuted}
                />
                <Text style={[styles.filterTabText, isActive && styles.filterTabTextActive]}>
                  {f.label}
                </Text>
                <View style={[styles.filterCount, isActive && styles.filterCountActive]}>
                  <Text style={[styles.filterCountText, isActive && styles.filterCountTextActive]}>
                    {count}
                  </Text>
                </View>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </Animated.View>

      {/* ── Request list ── */}
      {filteredRequests.length === 0 ? (
        renderEmpty()
      ) : (
        <FlatList
          data={filteredRequests}
          keyExtractor={item => String(item.id)}
          contentContainerStyle={[
            styles.listContent,
            { paddingBottom: insets.bottom + 32 },
          ]}
          showsVerticalScrollIndicator={false}
          renderItem={({ item }) => (
            <>
              <RequestCard
                req={item}
                onPress={() => toggleExpand(item.id)}
              />
              {expandedId === item.id && renderDetail(item)}
            </>
          )}
        />
      )}

    </View>
  );
}