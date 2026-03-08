// screens/Resident/ResidentDashboard.js
import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity,
  Animated, Modal, TextInput,
  ActivityIndicator, KeyboardAvoidingView, Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import RequestCard from '../../components/RequestCard';
import styles from '../../styles/ResidentDashboard.styles';
import Colors from '../../styles/colors';

// Static data 
const INITIAL_REQUESTS = [
  { id: 1, title: 'Electrical Repair',    service: 'electrical', status: 'pending',     date: 'Today, 2:30 PM', worker: null             },
  { id: 2, title: 'Kitchen Plumbing',     service: 'plumbing',   status: 'matched',     date: 'Feb 24, 2026',   worker: 'Juan Dela Cruz' },
  { id: 3, title: 'Ceiling Paint Job',    service: 'painting',   status: 'in_progress', date: 'Feb 20, 2026',   worker: 'Ramon Reyes'    },
  { id: 4, title: 'Cabinet Installation', service: 'carpentry',  status: 'completed',   date: 'Feb 15, 2026',   worker: 'Pedro Santos'   },
];

const SERVICE_CATEGORIES = [
  { value: 'electrical', label: 'Electrical', icon: 'flash-outline',         color: Colors.amber,     bg: Colors.amberBg    },
  { value: 'plumbing',   label: 'Plumbing',   icon: 'water-outline',          color: Colors.blue,      bg: Colors.blueBg     },
  { value: 'carpentry',  label: 'Carpentry',  icon: 'construct-outline',      color: Colors.amber,     bg: Colors.amberBg    },
  { value: 'painting',   label: 'Painting',   icon: 'color-palette-outline',  color: Colors.purple,    bg: Colors.purpleBg   },
  { value: 'cleaning',   label: 'Cleaning',   icon: 'sparkles-outline',       color: Colors.teal,      bg: Colors.tealBg     },
  { value: 'masonry',    label: 'Masonry',    icon: 'layers-outline',         color: Colors.skillDark, bg: Colors.skillLight },
];

export default function ResidentDashboard({ route, navigation }) {
  const insets = useSafeAreaInsets();
  const user   = route.params?.user || { full_name: 'Maria Santos', role: 'resident' };

  const [requests,    setRequests]    = useState(INITIAL_REQUESTS);
  const [modalOpen,   setModalOpen]   = useState(false);
  const [step,        setStep]        = useState(1);
  const [selectedCat, setSelectedCat] = useState(null);
  const [problem,     setProblem]     = useState('');
  const [location,    setLocation]    = useState('');
  const [submitting,  setSubmitting]  = useState(false);
  const [submitted,   setSubmitted]   = useState(false);

  // Entrance animations
  const headerAnim = useRef(new Animated.Value(0)).current;
  const cardAnim   = useRef(new Animated.Value(0)).current;
  const listAnim   = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.stagger(100, [
      Animated.spring(headerAnim, { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
      Animated.spring(cardAnim,   { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
      Animated.spring(listAnim,   { toValue: 1, tension: 60, friction: 10, useNativeDriver: true }),
    ]).start();
  }, []);

  const makeSlide = (anim) => ({
    opacity: anim,
    transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [20, 0] }) }],
  });

  const totalCount   = requests.length;
  const pendingCount = requests.filter((r) => r.status === 'pending').length;
  const doneCount    = requests.filter((r) => r.status === 'completed').length;

  function openModal(preselected = null) {
    setStep(preselected ? 2 : 1);
    setSelectedCat(preselected);
    setProblem('');
    setLocation('');
    setSubmitted(false);
    setModalOpen(true);
  }
  function closeModal() { setModalOpen(false); }

  const canProceed = step === 1 ? !!selectedCat : !!problem.trim() && !!location.trim();

  async function handleSubmitRequest() {
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 900));
    setRequests((prev) => [{
      id: Date.now(),
      title: `${selectedCat.label} Service`,
      service: selectedCat.value,
      status: 'pending',
      date: 'Just now',
      worker: null,
    }, ...prev]);
    setSubmitting(false);
    setSubmitted(true);
    setTimeout(() => closeModal(), 1600);
  }

  return (
    <View style={styles.root}>
      <StatusBar style="dark" />

      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={[styles.scroll, { paddingTop: insets.top + 16, paddingBottom: insets.bottom + 32 }]}
        showsVerticalScrollIndicator={false}
      >

        {/* Header */}
        <Animated.View style={[styles.header, makeSlide(headerAnim)]}>
          <View>
            <Text style={styles.greeting}>Good day,</Text>
            <Text style={styles.userName}>{user.full_name}</Text>
            <View style={styles.roleBadge}>
              <Ionicons name="home-outline" size={11} color={Colors.skillPrimary} />
              <Text style={styles.roleText}>Resident</Text>
            </View>
          </View>
          <TouchableOpacity onPress={() => navigation.replace('Login')} style={styles.logoutBtn} activeOpacity={0.7}>
            <Ionicons name="log-out-outline" size={18} color={Colors.textMuted} />
          </TouchableOpacity>
        </Animated.View>

        {/* Hero card */}
        <Animated.View style={makeSlide(cardAnim)}>
          <LinearGradient colors={[Colors.skillDark, '#054d38']} style={styles.heroCard} start={{ x: 0, y: 0 }} end={{ x: 1, y: 1 }}>
            <View style={styles.heroCircle1} />
            <View style={styles.heroCircle2} />
            <View style={styles.heroContent}>
              <View style={{ flex: 1 }}>
                <View style={styles.heroPill}>
                  <Ionicons name="location-outline" size={11} color={Colors.skillPrimary} />
                  <Text style={styles.heroPillText}>Cagayan de Oro</Text>
                </View>
                <Text style={styles.heroTitle}>Need help at home?</Text>
                <Text style={styles.heroSub}>Connect with verified skilled workers in your barangay.</Text>
              </View>
              <View style={styles.heroIconWrap}>
                <Ionicons name="construct-outline" size={28} color="#fff" />
              </View>
            </View>
            <TouchableOpacity onPress={() => openModal()} style={styles.heroBtn} activeOpacity={0.85}>
              <Ionicons name="add-circle-outline" size={18} color={Colors.skillDark} />
              <Text style={styles.heroBtnText}>New Service Request</Text>
            </TouchableOpacity>
          </LinearGradient>
        </Animated.View>

        {/* Stats */}
        <Animated.View style={[styles.statsRow, makeSlide(cardAnim)]}>
          <StatCard icon="clipboard-outline"        label="Total"     value={totalCount}   color={Colors.skillDark}    bg={Colors.skillLight}  border={Colors.borderLight} />
          <StatCard icon="time-outline"             label="Pending"   value={pendingCount} color={Colors.amber}        bg="#fef9c3"             border="#fde68a"            />
          <StatCard icon="checkmark-circle-outline" label="Completed" value={doneCount}    color={Colors.skillPrimary} bg={Colors.emerald100}   border={Colors.borderLight} />
        </Animated.View>

        {/* Quick services */}
        <Animated.View style={makeSlide(listAnim)}>
          <Text style={styles.sectionTitle}>Quick Services</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 24 }}>
            {SERVICE_CATEGORIES.map((cat) => (
              <TouchableOpacity key={cat.value} style={[styles.chip, { backgroundColor: cat.bg, borderColor: cat.color + '50' }]} onPress={() => openModal(cat)} activeOpacity={0.75}>
                <Ionicons name={cat.icon} size={14} color={cat.color} />
                <Text style={[styles.chipText, { color: cat.color }]}>{cat.label}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </Animated.View>

        {/* Requests */}
        <Animated.View style={makeSlide(listAnim)}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>My Requests</Text>
            <View style={styles.countBadge}>
              <Text style={styles.countText}>{totalCount}</Text>
            </View>
          </View>
          {requests.map((req) => <RequestCard key={req.id} req={req} />)}
        </Animated.View>

      </ScrollView>

      {/* Modal */}
      <Modal visible={modalOpen} animationType="slide" transparent onRequestClose={closeModal}>
        <View style={styles.modalOverlay}>
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ width: '100%' }}>
            <View style={styles.modalSheet}>
              <View style={styles.modalHandle} />

              <View style={styles.modalHeader}>
                <View>
                  <Text style={styles.modalTitle}>{submitted ? 'Request Submitted' : `New Request — Step ${step} of 2`}</Text>
                  <Text style={styles.modalSub}>{submitted ? 'We will match you with a worker shortly.' : step === 1 ? 'Select a service category' : 'Provide problem details'}</Text>
                </View>
                {!submitted && (
                  <TouchableOpacity onPress={closeModal} style={styles.modalCloseBtn}>
                    <Ionicons name="close" size={18} color={Colors.textMuted} />
                  </TouchableOpacity>
                )}
              </View>

              {!submitted && (
                <View style={styles.stepRow}>
                  <View style={[styles.stepBar, step >= 1 && styles.stepBarActive]} />
                  <View style={[styles.stepBar, step >= 2 && styles.stepBarActive]} />
                </View>
              )}

              {submitted && (
                <View style={styles.successBlock}>
                  <Ionicons name="checkmark-circle" size={64} color={Colors.skillPrimary} />
                  <Text style={styles.successTitle}>Request Submitted</Text>
                  <Text style={styles.successSub}>We will find a verified worker for you soon.</Text>
                </View>
              )}

              {!submitted && step === 1 && (
                <View style={styles.catGrid}>
                  {SERVICE_CATEGORIES.map((cat) => {
                    const sel = selectedCat?.value === cat.value;
                    return (
                      <TouchableOpacity key={cat.value} style={[styles.catCard, sel && { borderColor: cat.color, backgroundColor: cat.bg }]} onPress={() => setSelectedCat(cat)} activeOpacity={0.8}>
                        <View style={[styles.catIconWrap, { backgroundColor: sel ? cat.bg : Colors.surfaceAlt }]}>
                          <Ionicons name={cat.icon} size={22} color={cat.color} />
                        </View>
                        <Text style={[styles.catLabel, sel && { color: cat.color, fontWeight: '700' }]}>{cat.label}</Text>
                        {sel && <View style={[styles.catCheck, { backgroundColor: cat.color }]}><Ionicons name="checkmark" size={10} color="#fff" /></View>}
                      </TouchableOpacity>
                    );
                  })}
                </View>
              )}

              {!submitted && step === 2 && (
                <View style={styles.formBlock}>
                  <View style={[styles.selectedBadge, { backgroundColor: selectedCat?.bg }]}>
                    <Ionicons name={selectedCat?.icon} size={13} color={selectedCat?.color} />
                    <Text style={[styles.selectedBadgeText, { color: selectedCat?.color }]}>{selectedCat?.label}</Text>
                  </View>
                  <Text style={styles.inputLabel}>Describe the Problem</Text>
                  <TextInput style={styles.textArea} placeholder="e.g. Leaking pipe under the kitchen sink..." placeholderTextColor={Colors.textLight} multiline numberOfLines={4} value={problem} onChangeText={setProblem} selectionColor={Colors.skillPrimary} />
                  <Text style={styles.inputLabel}>Your Address / Location</Text>
                  <TextInput style={styles.inputField} placeholder="e.g. Purok 4, Brgy. Consolacion, CDO" placeholderTextColor={Colors.textLight} value={location} onChangeText={setLocation} selectionColor={Colors.skillPrimary} />
                </View>
              )}

              {!submitted && (
                <View style={styles.modalFooter}>
                  {step === 2 && (
                    <TouchableOpacity style={styles.backBtn} onPress={() => setStep(1)} activeOpacity={0.7}>
                      <Ionicons name="arrow-back-outline" size={17} color={Colors.textMuted} />
                      <Text style={styles.backBtnText}>Back</Text>
                    </TouchableOpacity>
                  )}
                  <TouchableOpacity style={[styles.nextBtn, !canProceed && { opacity: 0.4 }]} onPress={step === 1 ? () => setStep(2) : handleSubmitRequest} disabled={!canProceed || submitting} activeOpacity={0.85}>
                    <LinearGradient colors={canProceed ? [Colors.skillPrimary, Colors.emerald700] : [Colors.borderBase, Colors.borderBase]} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }} style={styles.nextBtnGrad}>
                      {submitting ? <ActivityIndicator color="#fff" size="small" /> : (
                        <View style={styles.btnRow}>
                          <Text style={[styles.nextBtnText, !canProceed && { color: Colors.textMuted }]}>{step === 1 ? 'Next' : 'Submit Request'}</Text>
                          <Ionicons name={step === 1 ? 'arrow-forward' : 'checkmark-circle-outline'} size={16} color={canProceed ? '#fff' : Colors.textMuted} />
                        </View>
                      )}
                    </LinearGradient>
                  </TouchableOpacity>
                </View>
              )}

            </View>
          </KeyboardAvoidingView>
        </View>
      </Modal>
    </View>
  );
}

// StatCard sub-component 
function StatCard({ icon, label, value, color, bg, border }) {
  return (
    <View style={[styles.statCard, { backgroundColor: bg, borderColor: border }]}>
      <Ionicons name={icon} size={20} color={color} />
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

