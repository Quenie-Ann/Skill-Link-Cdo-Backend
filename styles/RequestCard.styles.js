// styles/RequestCard.styles.js
// All styles for components/RequestCard.js

import { StyleSheet } from 'react-native';
import Colors from './colors';

const RequestCardStyles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.cardBg,
    borderRadius: 16,
    padding: 14,
    marginBottom: 10,
    gap: 12,
    borderWidth: 1,
    borderColor: Colors.borderBase,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  iconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  info:     { flex: 1 },
  title:    { fontSize: 14, fontWeight: '700', color: Colors.textDark, marginBottom: 4 },
  metaRow:  { flexDirection: 'row', alignItems: 'center', gap: 4 },
  metaText: { fontSize: 11, color: Colors.textMuted },
  metaDot:  { fontSize: 11, color: Colors.textLight },
});

export default RequestCardStyles;

