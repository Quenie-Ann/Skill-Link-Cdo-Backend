// screens/Resident/FindWorkers.js
// State + logic:  hooks/resident/useFindWorkers.js
// Static data:    data/services.data.js (filter tab icons)
// Components:     components/resident/WorkerCard.js
// Styles:         styles/FindWorkers.styles.js

import React, { useRef, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Animated, FlatList } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useFindWorkers }      from '../../hooks/resident/useFindWorkers';
import { SERVICE_CATEGORIES }  from '../../data/services.data';
import WorkerCard              from '../../components/resident/WorkerCard';
import styles                  from '../../styles/FindWorkers.styles';
import Colors                  from '../../styles/colors';

export default function FindWorkers({ route, navigation }) {
  const insets  = useSafeAreaInsets();
  const request = route.params?.request ?? {
    service: 'plumbing',
    issue:   'Leaking pipe or faucet',
    address: 'Bulua, CDO',
  };

  const fw = useFindWorkers(request);

  // Entrance animations
  const bannerAnim = useRef(new Animated.Value(0)).current;
  const listAnim   = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.stagger(120, [
      Animated.spring(bannerAnim, { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
      Animated.spring(listAnim,   { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
    ]).start();
  }, []);

  const makeSlide = anim => ({
    opacity: anim,
    transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [24, 0] }) }],
  });

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />

      {/* Header bar */}
      <View style={[styles.headerBar, { paddingTop: insets.top + 8 }]}>
        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()} activeOpacity={0.75}>
          <Ionicons name="chevron-back" size={20} color={Colors.textBody} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Matched Workers</Text>
        <View style={styles.workerCountBadge}>
          <Text style={styles.workerCountText}>{fw.filteredWorkers.length} workers</Text>
        </View>
      </View>

      {/* ML results banner */}
      <Animated.View style={[styles.mlBanner, makeSlide(bannerAnim)]}>
        <View style={styles.mlIconWrap}>
          <Ionicons name="sparkles" size={16} color="#fff" />
        </View>
        <View style={styles.mlInfo}>
          <Text style={styles.mlLabel}>ML MATCH RESULTS</Text>
          <Text style={styles.mlServiceStr} numberOfLines={1}>{fw.bannerService}</Text>
          <Text style={styles.mlMeta}>{fw.bannerMeta}</Text>
          <TouchableOpacity style={styles.mlBackLink} onPress={() => navigation.goBack()} activeOpacity={0.7}>
            <Ionicons name="chevron-back" size={13} color={Colors.skillPrimary} />
            <Text style={styles.mlBackText}>Back to My Requests</Text>
          </TouchableOpacity>
        </View>
      </Animated.View>

      {/* Filter tabs */}
      <View style={styles.filterWrap}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterScroll}>
          {fw.filterTabs.map(tab => {
            const isActive = fw.activeFilter === tab.value;
            const cat = SERVICE_CATEGORIES.find(c => c.value === tab.value);
            return (
              <TouchableOpacity
                key={tab.value}
                style={[styles.filterTab, isActive && styles.filterTabActive]}
                onPress={() => fw.setActiveFilter(tab.value)}
                activeOpacity={0.75}
              >
                {cat && <Ionicons name={cat.icon} size={13} color={isActive ? Colors.skillPrimary : Colors.textMuted} />}
                <Text style={[styles.filterTabText, isActive && styles.filterTabTextActive]}>{tab.label}</Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Worker list */}
      <Animated.View style={[{ flex: 1 }, makeSlide(listAnim)]}>
        {fw.filteredWorkers.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="people-outline" size={40} color={Colors.borderBase} />
            <Text style={styles.emptyText}>No workers found</Text>
            <Text style={styles.emptySubText}>Try a different filter.</Text>
          </View>
        ) : (
          <FlatList
            data={fw.filteredWorkers}
            keyExtractor={item => item.id}
            renderItem={({ item }) => (
              <WorkerCard
                worker={item}
                onOffer={fw.handleSendOffer}
                offerSent={!!fw.sentOffers[item.id]}
              />
            )}
            contentContainerStyle={[styles.scroll, { paddingTop: 12, paddingBottom: insets.bottom + 32 }]}
            showsVerticalScrollIndicator={false}
          />
        )}
      </Animated.View>
    </View>
  );
}