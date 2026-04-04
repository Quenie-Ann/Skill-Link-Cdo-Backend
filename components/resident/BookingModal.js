// components/resident/BookingModal.js
// 3-step bottom-sheet modal for booking a new service request.
//   Step 1 — Choose Service (list of 5 SRS trade categories)
//   Step 2 — Fill Details  (problem presets + budget tiles + preferred start + address)
//   Step 3 — Confirm       (review summary + "What happens next" box)
//
// Props:
//   visible              {boolean}  — controls Modal visibility
//   preselectedCategory  {object}   — full category object from SERVICE_CATEGORIES; skips to Step 2
//   onClose              {function} — called on cancel / close / after submit animation
//   onSubmit             {function} — called with new request data object on confirm

import React, { useState, useEffect } from 'react';
import {
  View, Text, TouchableOpacity, Modal, ScrollView,
  TextInput, KeyboardAvoidingView, Platform, ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

import { SERVICE_CATEGORIES, BUDGET_OPTIONS, PREFERRED_START_OPTIONS } from '../../constants/services';
import styles from '../../styles/BookingModal.styles';
import Colors from '../../styles/colors';

// Icons for the Step 3 review rows
const REVIEW_ROWS = [
  { key: 'service',        icon: 'construct-outline',   label: 'SERVICE'         },
  { key: 'issue',          icon: 'alert-circle-outline', label: 'PROBLEM'         },
  { key: 'budget',         icon: 'cash-outline',         label: 'BUDGET'          },
  { key: 'preferred_start',icon: 'time-outline',         label: 'PREFERRED START' },
  { key: 'schedule',       icon: 'calendar-outline',     label: 'SCHEDULE'        },
  { key: 'address',        icon: 'location-outline',     label: 'LOCATION'        },
];

export default function BookingModal({ visible, preselectedCategory, onClose, onSubmit }) {

  const [step,            setStep]           = useState(1);
  const [selectedCat,     setSelectedCat]    = useState(null);
  const [selectedIssue,   setSelectedIssue]  = useState(null);
  const [selectedBudget,  setSelectedBudget] = useState(null);
  const [selectedStart,   setSelectedStart]  = useState(null);
  const [address,         setAddress]        = useState('');
  const [submitting,      setSubmitting]     = useState(false);
  const [submitted,       setSubmitted]      = useState(false);

  // Reset state every time the modal opens, and apply preselection
  useEffect(() => {
    if (visible) {
      setSelectedIssue(null);
      setSelectedBudget(null);
      setSelectedStart(null);
      setAddress('');
      setSubmitting(false);
      setSubmitted(false);
      if (preselectedCategory) {
        setSelectedCat(preselectedCategory);
        setStep(2);
      } else {
        setSelectedCat(null);
        setStep(1);
      }
    }
  }, [visible]);

  function handleClose() {
    onClose();
  }

  // Validation guards per step
  const canStep1 = !!selectedCat;
  const canStep2 = !!selectedIssue && !!selectedBudget && !!selectedStart && !!address.trim();

  function handleNext() {
    if (step === 1 && canStep1) setStep(2);
    else if (step === 2 && canStep2) setStep(3);
  }

  async function handleSubmit() {
    setSubmitting(true);
    await new Promise(r => setTimeout(r, 900));

    const budgetLabel = BUDGET_OPTIONS.find(b => b.value === selectedBudget)?.label ?? '';
    const startLabel  = PREFERRED_START_OPTIONS.find(s => s.value === selectedStart)?.label ?? '';

    onSubmit({
      id:              Date.now(),
      title:           `${selectedCat.label} Service`,
      service:         selectedCat.value,
      status:          'pending',
      date:            'Just now',
      worker:          null,
      daily_rate:      null,
      rated:           false,
      issue:           selectedIssue,
      budget:          budgetLabel,
      preferred_start: startLabel,
      address,
    });

    setSubmitting(false);
    setSubmitted(true);
    setTimeout(() => handleClose(), 1600);
  }

  // Data for Step 3 review rows
  const reviewData = {
    service:         selectedCat?.label ?? '',
    issue:           selectedIssue ?? '',
    budget:          BUDGET_OPTIONS.find(b => b.value === selectedBudget)?.label ?? '',
    preferred_start: PREFERRED_START_OPTIONS.find(s => s.value === selectedStart)?.label ?? '',
    schedule:        'Flexible / Any Time',
    address,
  };

  const primaryEnabled = step === 1 ? canStep1 : step === 2 ? canStep2 : true;

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent
      onRequestClose={handleClose}
    >
      <View style={styles.overlay}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.kavWrap}
        >
          <View style={styles.sheet}>
            <View style={styles.handle} />

            {/* ── Header ── */}
            <View style={styles.header}>
              <View style={{ flex: 1 }}>
                {step > 1 && !submitted && (
                  <TouchableOpacity
                    style={styles.backChevron}
                    onPress={() => setStep(s => s - 1)}
                  >
                    <Ionicons name="chevron-back" size={14} color={Colors.skillPrimary} />
                    <Text style={styles.backChevronText}>Back</Text>
                  </TouchableOpacity>
                )}
                <Text style={styles.title}>
                  {submitted ? 'Request Submitted!' : 'Book a Service'}
                </Text>
                {!submitted && (
                  <Text style={styles.stepLabel}>
                    {`STEP ${step} OF 3 — ${['CHOOSE SERVICE', 'FILL DETAILS', 'CONFIRM'][step - 1]}`}
                  </Text>
                )}
              </View>
              {!submitted && (
                <TouchableOpacity onPress={handleClose} style={styles.closeBtn}>
                  <Ionicons name="close" size={18} color={Colors.textMuted} />
                </TouchableOpacity>
              )}
            </View>

            {/* ── Step progress bar ── */}
            {!submitted && (
              <View style={styles.progressRow}>
                {[1, 2, 3].map(s => (
                  <View
                    key={s}
                    style={[styles.progressBar, s <= step && styles.progressBarActive]}
                  />
                ))}
              </View>
            )}

            {/* STEP 1 — Choose Service */}
            {!submitted && step === 1 && (
              <ScrollView style={styles.body} showsVerticalScrollIndicator={false}>
                <Text style={styles.stepQuestion}>What type of service do you need?</Text>

                {SERVICE_CATEGORIES.map(cat => {
                  const isSelected = selectedCat?.value === cat.value;
                  return (
                    <TouchableOpacity
                      key={cat.value}
                      style={[
                        styles.serviceRow,
                        isSelected && styles.serviceRowSelected,
                        isSelected && { borderColor: cat.color },
                      ]}
                      onPress={() => setSelectedCat(cat)}
                      activeOpacity={0.75}
                    >
                      <View style={[styles.serviceIconWrap, { backgroundColor: cat.bg }]}>
                        <Ionicons name={cat.icon} size={20} color={cat.color} />
                      </View>
                      <View style={styles.serviceInfo}>
                        <Text style={styles.serviceName}>{cat.label}</Text>
                        <Text style={styles.serviceIssueCount}>
                          {cat.issues.length} common issues
                        </Text>
                      </View>
                      {isSelected && (
                        <Ionicons name="checkmark-circle" size={20} color={cat.color} />
                      )}
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            )}

            {/* STEP 2 — Fill Details */}
            {!submitted && step === 2 && (
              <ScrollView
                style={styles.body}
                showsVerticalScrollIndicator={false}
                keyboardShouldPersistTaps="handled"
              >
                {/* Problem presets */}
                <Text style={styles.fieldLabel}>WHAT IS THE PROBLEM? *</Text>
                {(selectedCat?.issues ?? []).map(issue => {
                  const isSelected = selectedIssue === issue;
                  return (
                    <TouchableOpacity
                      key={issue}
                      style={[styles.issueRow, isSelected && styles.issueRowSelected]}
                      onPress={() => setSelectedIssue(issue)}
                    >
                      <View style={[styles.radio, isSelected && styles.radioActive]}>
                        {isSelected && <View style={styles.radioDot} />}
                      </View>
                      <Text style={styles.issueText}>{issue}</Text>
                    </TouchableOpacity>
                  );
                })}

                {/* Budget tiles */}
                <Text style={[styles.fieldLabel, { marginTop: 18 }]}>BUDGET *</Text>
                <View style={styles.tileGrid}>
                  {BUDGET_OPTIONS.map(opt => {
                    const isSelected = selectedBudget === opt.value;
                    return (
                      <TouchableOpacity
                        key={opt.id}
                        style={[styles.budgetTile, isSelected && styles.budgetTileSelected]}
                        onPress={() => setSelectedBudget(opt.value)}
                      >
                        <Ionicons
                          name="cash-outline"
                          size={12}
                          color={isSelected ? Colors.skillPrimary : Colors.textMuted}
                        />
                        <Text style={[
                          styles.budgetTileText,
                          isSelected && styles.budgetTileTextSelected,
                        ]}>
                          {opt.label}
                        </Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>

                {/* Preferred start tiles */}
                <Text style={[styles.fieldLabel, { marginTop: 18 }]}>PREFERRED START *</Text>
                <View style={styles.tileGrid}>
                  {PREFERRED_START_OPTIONS.map(opt => {
                    const isSelected = selectedStart === opt.value;
                    return (
                      <TouchableOpacity
                        key={opt.id}
                        style={[styles.startTile, isSelected && styles.startTileSelected]}
                        onPress={() => setSelectedStart(opt.value)}
                      >
                        <Text style={[
                          styles.startTileLabel,
                          isSelected && styles.startTileLabelSel,
                        ]}>
                          {opt.label}
                        </Text>
                        <Text style={[
                          styles.startTileSub,
                          isSelected && styles.startTileSubSel,
                        ]}>
                          {opt.sub}
                        </Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>

                {/* Address */}
                <Text style={[styles.fieldLabel, { marginTop: 18 }]}>YOUR ADDRESS *</Text>
                <TextInput
                  style={styles.input}
                  placeholder="e.g. Zone 1, Bulua, CDO"
                  placeholderTextColor={Colors.textMuted}
                  value={address}
                  onChangeText={setAddress}
                />
              </ScrollView>
            )}

            {/* STEP 3 — Confirm / Review */}
            {!submitted && step === 3 && (
              <ScrollView style={styles.body} showsVerticalScrollIndicator={false}>
                <Text style={styles.confirmIntro}>Review your request before submitting.</Text>

                {REVIEW_ROWS.map(row => (
                  <View key={row.key} style={styles.reviewRow}>
                    <View style={styles.reviewIconWrap}>
                      <Ionicons name={row.icon} size={16} color={Colors.skillPrimary} />
                    </View>
                    <View style={styles.reviewContent}>
                      <Text style={styles.reviewLabel}>{row.label}</Text>
                      <Text style={styles.reviewValue}>{reviewData[row.key]}</Text>
                    </View>
                  </View>
                ))}

                {/* What happens next */}
                <View style={styles.nextBox}>
                  <View style={styles.nextBoxHeader}>
                    <Ionicons name="sparkles-outline" size={14} color={Colors.skillPrimary} />
                    <Text style={styles.nextBoxTitle}>What happens next</Text>
                  </View>
                  {[
                    'ML engine ranks verified workers matching your request',
                    'You review the ranked list and choose your preferred worker',
                    'You send an offer — the worker accepts or declines',
                  ].map((item, i) => (
                    <View key={i} style={styles.nextItem}>
                      <View style={styles.nextNum}>
                        <Text style={styles.nextNumText}>{i + 1}</Text>
                      </View>
                      <Text style={styles.nextItemText}>{item}</Text>
                    </View>
                  ))}
                </View>
              </ScrollView>
            )}

            {/* ── Success state ── */}
            {submitted && (
              <View style={styles.successBlock}>
                <View style={styles.successIconWrap}>
                  <Ionicons name="checkmark-circle" size={48} color={Colors.skillPrimary} />
                </View>
                <Text style={styles.successTitle}>Request Submitted!</Text>
                <Text style={styles.successSub}>
                  Finding matched workers near you…
                </Text>
              </View>
            )}

            {/* ── Footer buttons ── */}
            {!submitted && (
              <View style={styles.footer}>
                {/* Left button: Cancel (step 1) or Back (steps 2–3) */}
                {step === 1 ? (
                  <TouchableOpacity style={styles.cancelBtn} onPress={handleClose}>
                    <Text style={styles.cancelBtnText}>Cancel</Text>
                  </TouchableOpacity>
                ) : (
                  <TouchableOpacity style={styles.backBtn} onPress={() => setStep(s => s - 1)}>
                    <Text style={styles.backBtnText}>Back</Text>
                  </TouchableOpacity>
                )}

                {/* Right button: Continue / Find Matched Workers */}
                <TouchableOpacity
                  style={[styles.primaryBtn, !primaryEnabled && styles.primaryBtnDim]}
                  onPress={step === 3 ? handleSubmit : handleNext}
                  disabled={!primaryEnabled || submitting}
                  activeOpacity={0.85}
                >
                  <LinearGradient
                    colors={
                      primaryEnabled
                        ? [Colors.skillPrimary, Colors.emerald700]
                        : [Colors.borderBase, Colors.borderBase]
                    }
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 0 }}
                    style={styles.primaryBtnGrad}
                  >
                    {submitting ? (
                      <ActivityIndicator color="#fff" size="small" />
                    ) : (
                      <View style={styles.btnRow}>
                        <Text style={styles.primaryBtnText}>
                          {step === 3 ? 'Find Matched Workers' : 'Continue'}
                        </Text>
                        <Ionicons name="arrow-forward" size={16} color="#fff" />
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
  );
}