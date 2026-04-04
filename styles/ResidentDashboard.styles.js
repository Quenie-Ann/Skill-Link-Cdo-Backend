// styles/ResidentDashboard.styles.js
// All styles for screens/Resident/ResidentDashboard.js

import { StyleSheet, Dimensions } from 'react-native';
import Colors from './colors';

const { width } = Dimensions.get('window');

export default StyleSheet.create({

  // Page 
  root:   { flex: 1, backgroundColor: Colors.pageBg },
  scroll: { paddingHorizontal: 20 },

  // Header 
  header: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'flex-start', marginBottom: 20,
  },
  greeting: { fontSize: 13, color: Colors.textMuted, fontWeight: '500' },
  userName: { fontSize: 22, fontWeight: '800', color: Colors.skillDark, marginTop: 2 },
  roleBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 6,
    backgroundColor: Colors.emerald100, paddingHorizontal: 10, paddingVertical: 4,
    borderRadius: 20, alignSelf: 'flex-start', borderWidth: 1, borderColor: Colors.borderMid,
  },
  roleText: { fontSize: 10, fontWeight: '700', color: Colors.skillDark, letterSpacing: 0.5 },
  logoutBtn: {
    padding: 10, backgroundColor: Colors.cardBg, borderRadius: 12,
    borderWidth: 1, borderColor: Colors.borderBase,
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06, shadowRadius: 3, elevation: 2,
  },

  // Hero card 
  heroCard: {
    borderRadius: 22, padding: 20, marginBottom: 16,
    overflow: 'hidden', position: 'relative',
  },
  heroCircle1: {
    position: 'absolute',
    width: width * 0.5, height: width * 0.5, borderRadius: 999,
    backgroundColor: 'rgba(255,255,255,0.06)',
    top: -(width * 0.18), right: -(width * 0.12),
  },
  heroCircle2: {
    position: 'absolute',
    width: width * 0.35, height: width * 0.35, borderRadius: 999,
    backgroundColor: 'rgba(255,255,255,0.04)',
    bottom: -(width * 0.1), left: -(width * 0.06),
  },
  heroPill: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: 'rgba(16,185,129,0.2)',
    paddingHorizontal: 10, paddingVertical: 4,
    borderRadius: 20, alignSelf: 'flex-start', marginBottom: 12,
  },
  heroPillText: { fontSize: 10, color: '#6ee7b7', fontWeight: '700', letterSpacing: 0.3 },
  heroTitle:    { fontSize: 20, fontWeight: '800', color: '#fff', marginBottom: 6, lineHeight: 26 },
  heroSub:      { fontSize: 12, color: 'rgba(255,255,255,0.72)', lineHeight: 18, marginBottom: 18 },
  heroBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    backgroundColor: Colors.skillLight, paddingVertical: 12, borderRadius: 14,
  },
  heroBtnText: { color: Colors.skillDark, fontWeight: '800', fontSize: 14 },

  // Stats row 
  statsRow: { flexDirection: 'row', gap: 10, marginBottom: 24 },
  statCard: {
    flex: 1, borderRadius: 16, padding: 14,
    alignItems: 'center', gap: 4, borderWidth: 1,
    shadowColor: '#000', shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05, shadowRadius: 3, elevation: 1,
  },
  statValue: { fontSize: 22, fontWeight: '800' },
  statLabel: {
    fontSize: 10, color: Colors.textMuted, fontWeight: '600',
    textTransform: 'uppercase', letterSpacing: 0.3,
  },

  // Section headers 
  sectionHeader: {
    flexDirection: 'row', justifyContent: 'space-between',
    alignItems: 'center', marginBottom: 12,
  },
  sectionTitle: { fontSize: 15, fontWeight: '800', color: Colors.skillDark },
  seeAll:       { fontSize: 12, color: Colors.skillPrimary, fontWeight: '700' },
  countBadge: {
    backgroundColor: Colors.emerald100,
    paddingHorizontal: 10, paddingVertical: 3,
    borderRadius: 20, borderWidth: 1, borderColor: Colors.borderMid,
  },
  countText: { fontSize: 11, fontWeight: '700', color: Colors.skillDark },

  // Popular services horizontal scroll 
  servicesScroll: { paddingBottom: 4, paddingRight: 4, marginBottom: 24 },
  serviceChip: {
    alignItems: 'center', paddingHorizontal: 16, paddingVertical: 12,
    borderRadius: 16, marginRight: 10, borderWidth: 1,
    gap: 8, minWidth: 80,
  },
  serviceChipIcon: {
    width: 40, height: 40, borderRadius: 12,
    alignItems: 'center', justifyContent: 'center',
  },
  serviceChipLabel: { fontSize: 12, fontWeight: '700' },

  // Empty state 
  emptyState: {
    alignItems: 'center', paddingVertical: 40, gap: 8,
    backgroundColor: Colors.cardBg, borderRadius: 16,
    borderWidth: 1, borderColor: Colors.borderBase,
  },
  emptyText:    { fontSize: 14, fontWeight: '700', color: Colors.textBody },
  emptySubText: { fontSize: 12, color: Colors.textMuted, textAlign: 'center' },
});