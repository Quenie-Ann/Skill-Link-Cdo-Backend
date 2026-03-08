// components/RequestCard.js
//tirso
import React from 'react';
import { View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import StatusBadge from './StatusBadge';
import styles from '../styles/RequestCard.styles';
import Colors from '../styles/colors';

const SERVICE_META = {
  electrical: { icon: 'flash-outline',        color: Colors.amber,     bg: Colors.amberBg  },
  plumbing:   { icon: 'water-outline',         color: Colors.blue,      bg: Colors.blueBg   },
  carpentry:  { icon: 'construct-outline',     color: Colors.amber,     bg: Colors.amberBg  },
  painting:   { icon: 'color-palette-outline', color: Colors.purple,    bg: Colors.purpleBg },
  cleaning:   { icon: 'sparkles-outline',      color: Colors.teal,      bg: Colors.tealBg   },
  masonry:    { icon: 'layers-outline',        color: Colors.skillDark, bg: Colors.skillLight },
};

export default function RequestCard({ req }) {
  const meta = SERVICE_META[req.service] || SERVICE_META.electrical;
  return (
    <View style={styles.card}>
      <View style={[styles.iconWrap, { backgroundColor: meta.bg }]}>
        <Ionicons name={meta.icon} size={20} color={meta.color} />
      </View>
      <View style={styles.info}>
        <Text style={styles.title}>{req.title}</Text>
        <View style={styles.metaRow}>
          {req.worker && (
            <>
              <Ionicons name="person-outline" size={11} color={Colors.textMuted} />
              <Text style={styles.metaText}>{req.worker}</Text>
              <Text style={styles.metaDot}>·</Text>
            </>
          )}
          <Ionicons name="calendar-outline" size={11} color={Colors.textMuted} />
          <Text style={styles.metaText}>{req.date}</Text>
        </View>
      </View>
      <StatusBadge status={req.status} />
    </View>
  );
}
