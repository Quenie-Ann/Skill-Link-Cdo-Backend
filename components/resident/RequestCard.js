// components/resident/RequestCard.js
// Resident request card with 4-step progress dots and status badge.
// Progress steps: Pending → Matched → In Progress → Done

import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Colors from '../../styles/colors';
import styles from '../../styles/RequestCard.styles';

const PROGRESS_STEPS = ['Pending', 'Matched', 'In Progress', 'Done'];

// Maps req.status → step index, badge label, badge colors
const STATUS_CONFIG = {
  pending:     { stepIndex: 0, label: 'PENDING',        color: Colors.amber,        bg: Colors.amberBg    },
  matched:     { stepIndex: 1, label: 'OFFER ACCEPTED', color: Colors.skillPrimary, bg: Colors.emerald100 },
  in_progress: { stepIndex: 2, label: 'IN PROGRESS',    color: Colors.blue,         bg: Colors.blueBg     },
  completed:   { stepIndex: 3, label: 'COMPLETED',      color: Colors.skillDark,    bg: Colors.skillLight },
};

export default function RequestCard({ req, onPress }) {
  const config = STATUS_CONFIG[req.status] ?? STATUS_CONFIG.pending;

  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.8}>

      {/* ── Title + Badge ── */}
      <View style={styles.topRow}>
        <Text style={styles.title} numberOfLines={1}>{req.title}</Text>
        <View style={[styles.badge, { backgroundColor: config.bg }]}>
          <Text style={[styles.badgeText, { color: config.color }]}>{config.label}</Text>
        </View>
      </View>

      {/* ── Progress dots ── */}
      <View style={styles.dotsRow}>
        {PROGRESS_STEPS.map((step, i) => (
          <React.Fragment key={step}>
            <View style={[styles.dot, i <= config.stepIndex ? styles.dotFilled : styles.dotEmpty]} />
            {i < PROGRESS_STEPS.length - 1 && (
              <View style={[styles.line, i < config.stepIndex ? styles.lineFilled : styles.lineEmpty]} />
            )}
          </React.Fragment>
        ))}
      </View>

      {/* ── Meta: date · rate · rate-now ── */}
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