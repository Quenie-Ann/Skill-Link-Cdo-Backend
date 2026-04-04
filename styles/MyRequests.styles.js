// styles/MyRequests.styles.js
// All styles for screens/Resident/MyRequests.js

import { StyleSheet } from 'react-native';
import Colors from './colors';

export default StyleSheet.create({

  // Page 
  root:   { flex: 1, backgroundColor: Colors.pageBg },

  // Header bar 
  headerBar: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 16, paddingBottom: 12,
    backgroundColor: Colors.pageBg,
    borderBottomWidth: 1, borderBottomColor: Colors.borderBase,
    gap: 12,
  },
  backBtn: {
    width: 36, height: 36, borderRadius: 10,
    backgroundColor: Colors.cardBg,
    borderWidth: 1, borderColor: Colors.borderBase,
    alignItems: 'center', justifyContent: 'center',
  },
  headerTextBlock: { flex: 1 },
  headerTitle:     { fontSize: 17, fontWeight: '800', color: Colors.skillDark },
  headerSub:       { fontSize: 11, color: Colors.textMuted, marginTop: 1 },

  // Summary stats row 
  statsWrap: {
    paddingHorizontal: 16, paddingTop: 16, paddingBottom: 4,
  },
  statsRow: {
    flexDirection: 'row', gap: 10,
  },
  statCard: {
    flex: 1, borderRadius: 16, padding: 14,
    alignItems: 'center', gap: 3,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05, shadowRadius: 3, elevation: 1,
  },
  statValue:    { fontSize: 24, fontWeight: '800' },
  statLabel:    {
    fontSize: 10, fontWeight: '600',
    textTransform: 'uppercase', letterSpacing: 0.3,
    color: Colors.textMuted,
  },

  // Filter tab bar 
  filterWrap:   { paddingHorizontal: 16, paddingVertical: 14 },
  filterScroll: { paddingBottom: 2 },
  filterTab: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 14, paddingVertical: 8,
    borderRadius: 20, marginRight: 8,
    borderWidth: 1.5, borderColor: Colors.borderBase,
    backgroundColor: Colors.cardBg,
  },
  filterTabActive: {
    borderColor: Colors.skillPrimary,
    backgroundColor: Colors.skillLight,
  },
  filterTabText:        { fontSize: 12, fontWeight: '700', color: Colors.textMuted },
  filterTabTextActive:  { color: Colors.skillPrimary },
  filterCount: {
    minWidth: 18, height: 18, borderRadius: 9,
    backgroundColor: Colors.borderBase,
    alignItems: 'center', justifyContent: 'center',
    paddingHorizontal: 4,
  },
  filterCountActive:    { backgroundColor: Colors.skillPrimary },
  filterCountText:      { fontSize: 10, fontWeight: '800', color: Colors.textMuted },
  filterCountTextActive:{ color: '#fff' },

  // List 
  listContent: { paddingHorizontal: 16 },

  // Expanded request detail card 
  // (tapped from RequestCard — expands inline below the card row)
  detailCard: {
    backgroundColor: Colors.skillLight,
    borderRadius: 12, padding: 14,
    marginTop: -4, marginBottom: 10,
    borderWidth: 1, borderColor: Colors.borderMid,
    gap: 8,
  },
  detailRow:   { flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  detailIconWrap: {
    width: 28, height: 28, borderRadius: 8,
    backgroundColor: '#fff',
    alignItems: 'center', justifyContent: 'center',
  },
  detailContent: { flex: 1 },
  detailLabel:   { fontSize: 10, fontWeight: '700', color: Colors.textMuted, letterSpacing: 0.4 },
  detailValue:   { fontSize: 13, fontWeight: '600', color: Colors.textDark, marginTop: 1 },

  // Worker chip inside detail
  workerChip: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: '#fff', borderRadius: 8, paddingHorizontal: 10,
    paddingVertical: 6, alignSelf: 'flex-start', marginTop: 6,
    borderWidth: 1, borderColor: Colors.borderBase,
  },
  workerChipText: { fontSize: 13, fontWeight: '700', color: Colors.skillDark },

  // Rate Now CTA inside detail (for completed + unrated)
  rateNowBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    marginTop: 4, alignSelf: 'flex-start',
    paddingHorizontal: 12, paddingVertical: 8,
    backgroundColor: Colors.amberBg,
    borderRadius: 10, borderWidth: 1,
    borderColor: Colors.amber + '55',
  },
  rateNowText: { fontSize: 13, fontWeight: '700', color: Colors.amber },

  // Empty state 
  emptyState: {
    alignItems: 'center', paddingVertical: 60, gap: 10,
  },
  emptyIconWrap: {
    width: 68, height: 68, borderRadius: 20,
    backgroundColor: Colors.cardBg,
    borderWidth: 1, borderColor: Colors.borderBase,
    alignItems: 'center', justifyContent: 'center',
    marginBottom: 4,
  },
  emptyText:    { fontSize: 15, fontWeight: '700', color: Colors.textBody },
  emptySubText: {
    fontSize: 13, color: Colors.textMuted,
    textAlign: 'center', lineHeight: 19,
  },
  emptyBtn: {
    marginTop: 8, paddingHorizontal: 20, paddingVertical: 12,
    borderRadius: 12, overflow: 'hidden',
  },
  emptyBtnGrad: {
    paddingHorizontal: 20, paddingVertical: 12,
    borderRadius: 12, flexDirection: 'row',
    alignItems: 'center', gap: 6,
  },
  emptyBtnText: { color: '#fff', fontWeight: '800', fontSize: 14 },
});