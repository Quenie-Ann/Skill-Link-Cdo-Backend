// styles/BookingModal.styles.js
// All styles for components/resident/BookingModal.js

import { StyleSheet, Dimensions } from 'react-native';
import Colors from './colors';

const { width } = Dimensions.get('window');

// Tile width for 2-column layouts inside the modal
// 24px padding each side + 8px gap between cols
const TILE_W = (width - 48 - 8) / 2;

export default StyleSheet.create({

  // Overlay & sheet 
  overlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(15,23,42,0.45)' },
  kavWrap: { width: '100%' },
  sheet: {
    backgroundColor: Colors.cardBg,
    borderTopLeftRadius: 28, borderTopRightRadius: 28,
    paddingHorizontal: 24, paddingBottom: 36, paddingTop: 16,
    borderTopWidth: 1, borderTopColor: Colors.borderBase,
    maxHeight: '93%',
  },
  handle: {
    width: 40, height: 4, backgroundColor: '#cbd5e1',
    borderRadius: 2, alignSelf: 'center', marginBottom: 20,
  },

  // Header 
  header:          { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 },
  backChevron:     { flexDirection: 'row', alignItems: 'center', gap: 2, marginBottom: 4 },
  backChevronText: { fontSize: 12, color: Colors.skillPrimary, fontWeight: '600' },
  title:           { fontSize: 18, fontWeight: '800', color: Colors.skillDark },
  stepLabel:       { fontSize: 11, color: Colors.skillPrimary, fontWeight: '700', marginTop: 2, letterSpacing: 0.4 },
  closeBtn:        {
    padding: 8, backgroundColor: Colors.surfaceAlt,
    borderRadius: 10, borderWidth: 1, borderColor: Colors.borderBase,
  },

  // Progress bar 
  progressRow:      { flexDirection: 'row', gap: 6, marginBottom: 20 },
  progressBar:      { height: 4, flex: 1, backgroundColor: Colors.borderBase, borderRadius: 2 },
  progressBarActive: { backgroundColor: Colors.skillPrimary },

  // Scrollable body
  body: { maxHeight: 420 },

  // Step 1 — Choose Service 
  stepQuestion: { fontSize: 13, color: Colors.textBody, fontWeight: '500', marginBottom: 12 },

  serviceRow: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    backgroundColor: Colors.inputBg, borderRadius: 14,
    padding: 14, marginBottom: 8,
    borderWidth: 1.5, borderColor: Colors.borderBase,
  },
  serviceRowSelected: { backgroundColor: Colors.skillLight },
  serviceIconWrap: {
    width: 42, height: 42, borderRadius: 12,
    alignItems: 'center', justifyContent: 'center',
  },
  serviceInfo:       { flex: 1 },
  serviceName:       { fontSize: 14, fontWeight: '700', color: Colors.textDark },
  serviceIssueCount: { fontSize: 12, color: Colors.textMuted, marginTop: 2 },

  // Step 2 — Fill Details 
  fieldLabel: {
    fontSize: 11, fontWeight: '700',
    color: Colors.textBody, letterSpacing: 0.4, marginBottom: 10,
  },

  // Problem preset radio rows
  issueRow: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingVertical: 12, paddingHorizontal: 14,
    backgroundColor: Colors.inputBg, borderRadius: 12,
    marginBottom: 6, borderWidth: 1.5, borderColor: Colors.borderBase,
  },
  issueRowSelected: { backgroundColor: Colors.skillLight, borderColor: Colors.skillPrimary },
  radio:            {
    width: 18, height: 18, borderRadius: 9,
    borderWidth: 2, borderColor: Colors.borderMid,
    alignItems: 'center', justifyContent: 'center',
  },
  radioActive:   { borderColor: Colors.skillPrimary },
  radioDot:      { width: 8, height: 8, borderRadius: 4, backgroundColor: Colors.skillPrimary },
  issueText:     { fontSize: 13, color: Colors.textDark, flex: 1 },

  // Budget + start shared tile grid
  tileGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },

  // Budget tiles — compact, horizontal icon + text
  budgetTile: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingVertical: 10, paddingHorizontal: 12,
    borderRadius: 10, borderWidth: 1.5, borderColor: Colors.borderBase,
    backgroundColor: Colors.inputBg,
  },
  budgetTileSelected: { backgroundColor: Colors.skillLight, borderColor: Colors.skillPrimary },
  budgetTileText:     { fontSize: 12, fontWeight: '600', color: Colors.textBody },
  budgetTileTextSelected: { color: Colors.skillPrimary, fontWeight: '700' },

  // Preferred start tiles — 2-column with sub-label
  startTile: {
    width: TILE_W, padding: 12,
    borderRadius: 10, borderWidth: 1.5, borderColor: Colors.borderBase,
    backgroundColor: Colors.inputBg,
  },
  startTileSelected:  { backgroundColor: Colors.skillPrimary, borderColor: Colors.skillPrimary },
  startTileLabel:     { fontSize: 13, fontWeight: '700', color: Colors.textDark },
  startTileLabelSel:  { color: '#fff' },
  startTileSub:       { fontSize: 11, color: Colors.textMuted, marginTop: 3, lineHeight: 15 },
  startTileSubSel:    { color: 'rgba(255,255,255,0.8)' },

  // Address input
  input: {
    backgroundColor: Colors.inputBg, borderRadius: 14,
    padding: 14, color: Colors.textDark, fontSize: 14,
    height: 52, borderWidth: 1.5, borderColor: Colors.borderBase,
  },

  // Step 3 — Confirm 
  confirmIntro: { fontSize: 13, color: Colors.textMuted, marginBottom: 16 },

  reviewRow: {
    flexDirection: 'row', alignItems: 'flex-start', gap: 12,
    paddingVertical: 12,
    borderBottomWidth: 1, borderBottomColor: Colors.borderBase,
  },
  reviewIconWrap: {
    width: 32, height: 32, borderRadius: 8,
    backgroundColor: Colors.skillLight,
    alignItems: 'center', justifyContent: 'center',
  },
  reviewContent: { flex: 1 },
  reviewLabel:   { fontSize: 10, fontWeight: '700', color: Colors.textMuted, letterSpacing: 0.5, marginBottom: 2 },
  reviewValue:   { fontSize: 14, fontWeight: '600', color: Colors.textDark },

  // "What happens next" info box
  nextBox: {
    backgroundColor: Colors.skillLight,
    borderRadius: 14, padding: 16,
    marginTop: 16, marginBottom: 8,
  },
  nextBoxHeader: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 12 },
  nextBoxTitle:  { fontSize: 13, fontWeight: '800', color: Colors.skillDark },
  nextItem:      { flexDirection: 'row', alignItems: 'flex-start', gap: 10, marginBottom: 8 },
  nextNum: {
    width: 20, height: 20, borderRadius: 10,
    backgroundColor: Colors.skillPrimary,
    alignItems: 'center', justifyContent: 'center',
  },
  nextNumText:   { fontSize: 11, fontWeight: '800', color: '#fff' },
  nextItemText:  { fontSize: 12, color: Colors.skillDark, flex: 1, lineHeight: 18 },

  // Success state 
  successBlock: { alignItems: 'center', paddingVertical: 40, gap: 8 },
  successIconWrap: {
    width: 80, height: 80, borderRadius: 40,
    backgroundColor: Colors.skillLight,
    alignItems: 'center', justifyContent: 'center', marginBottom: 8,
  },
  successTitle: { fontSize: 18, fontWeight: '800', color: Colors.skillDark },
  successSub:   { fontSize: 13, color: Colors.textMuted, textAlign: 'center', lineHeight: 20 },

  // Footer buttons 
  footer:      { flexDirection: 'row', gap: 10, marginTop: 20 },
  cancelBtn: {
    paddingHorizontal: 20, paddingVertical: 14,
    backgroundColor: Colors.surfaceAlt, borderRadius: 14,
    borderWidth: 1, borderColor: Colors.borderBase,
  },
  cancelBtnText:  { color: Colors.textMuted, fontWeight: '600', fontSize: 13 },
  backBtn: {
    paddingHorizontal: 20, paddingVertical: 14,
    backgroundColor: Colors.surfaceAlt, borderRadius: 14,
    borderWidth: 1, borderColor: Colors.borderBase,
  },
  backBtnText:    { color: Colors.textMuted, fontWeight: '600', fontSize: 13 },
  primaryBtn:     { flex: 1, borderRadius: 14, overflow: 'hidden' },
  primaryBtnDim:  { opacity: 0.45 },
  primaryBtnGrad: { paddingVertical: 15, alignItems: 'center', justifyContent: 'center', borderRadius: 14 },
  btnRow:         { flexDirection: 'row', alignItems: 'center', gap: 7 },
  primaryBtnText: { color: '#fff', fontWeight: '800', fontSize: 14 },
});