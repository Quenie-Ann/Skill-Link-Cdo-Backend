// components/resident/RequestCard.js
// All config imported from data/residentRequests.data.js.
//
// Props:
//   req      {object}   — request object
//   onPress  {function} — called when card is tapped (toggles detail panel)

import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import {
  REQUEST_PROGRESS_STEPS,
  REQUEST_STATUS_CONFIG,
} from '../../data/residentRequests.data';
import styles from '../../styles/RequestCard.styles';
import Colors from '../../styles/colors';

export default function RequestCard({ req, onPress }) {
  const config = REQUEST_STATUS_CONFIG[req.status] ?? REQUEST_STATUS_CONFIG.pending;

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.8}>

      {/* Title + Badge */}
      <View style={styles.topRow}>
        <Text style={styles.title} numberOfLines={1}>{req.title}</Text>
        <View style={[styles.badge, { backgroundColor: config.bg }]}>
          <Text style={[styles.badgeText, { color: config.color }]}>{config.label}</Text>
        </View>
      </View>

      {/* Progress dots */}
      <View style={styles.dotsRow}>
        {REQUEST_PROGRESS_STEPS.map((step, i) => (
          <React.Fragment key={step}>
            <View style={[styles.dot, i <= config.stepIndex ? styles.dotFilled : styles.dotEmpty]} />
            {i < REQUEST_PROGRESS_STEPS.length - 1 && (
              <View style={[styles.line, i < config.stepIndex ? styles.lineFilled : styles.lineEmpty]} />
            )}
          </React.Fragment>
        ))}
      </View>

      {/* Meta: date · rate · Rate Now */}
      <View style={styles.metaRow}>
        <Text style={styles.metaText}>{req.date}</Text>
        {req.daily_rate != null && (
          <View style={styles.ratePill}>
            <Text style={styles.rateText}>₱{req.daily_rate}/day</Text>
          </View>
        )}
        {req.status === 'completed' && !req.rated && (
          <TouchableOpacity style={styles.rateBtn} activeOpacity={0.7}>
            <Ionicons name="star-outline" size={12} color={Colors.amber} />
            <Text style={styles.rateBtnText}>Rate Now</Text>
          </TouchableOpacity>
        )}
      </View>

    </TouchableOpacity>
  );
}