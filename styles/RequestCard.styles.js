// styles/RequestCard.styles.js
// All styles for components/resident/RequestCard.js

import { StyleSheet } from 'react-native';
import Colors from './colors';

export default StyleSheet.create({

  card: {
    backgroundColor: Colors.cardBg,
    borderRadius: 16,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: Colors.borderBase,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 1,
  },

  // Title + status badge row
  topRow:    { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  title:     { fontSize: 14, fontWeight: '700', color: Colors.textDark, flex: 1, marginRight: 8 },
  badge:     { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20 },
  badgeText: { fontSize: 10, fontWeight: '700', letterSpacing: 0.4 },

  // Progress dots row: ● — ● — ● — ●
  dotsRow:     { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  dot:         { width: 10, height: 10, borderRadius: 5 },
  dotFilled:   { backgroundColor: Colors.skillPrimary },
  dotEmpty:    { backgroundColor: Colors.borderBase },
  line:        { flex: 1, height: 2, marginHorizontal: 3 },
  lineFilled:  { backgroundColor: Colors.skillPrimary },
  lineEmpty:   { backgroundColor: Colors.borderBase },

  // Date / rate / rate-now meta row
  metaRow:     { flexDirection: 'row', alignItems: 'center', gap: 8 },
  metaText:    { fontSize: 12, color: Colors.textMuted },
  ratePill:    {
    backgroundColor: Colors.skillLight,
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10,
  },
  rateText:    { fontSize: 11, color: Colors.skillDark, fontWeight: '600' },
  rateBtn:     { flexDirection: 'row', alignItems: 'center', gap: 4, marginLeft: 'auto' },
  rateBtnText: { fontSize: 12, color: Colors.amber, fontWeight: '700' },
});