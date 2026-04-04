// components/resident/BookingModal.js
// All state + logic comes from useBookingModal hook.
// All static lists come from data/services.data.js.
//
// Props:
//   visible               {boolean}
//   preselectedCategory   {object|null}
//   onClose               {function}
//   onSubmit              {function}

import React from 'react';
import {
  View, Text, TouchableOpacity, Modal, ScrollView,
  TextInput, KeyboardAvoidingView, Platform, ActivityIndicator,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

import { useBookingModal } from '../../hooks/resident/useBookingModal';
import {
  SERVICE_CATEGORIES,
  BUDGET_OPTIONS,
  PREFERRED_START_OPTIONS,
  BOOKING_REVIEW_ROWS,
  BOOKING_NEXT_STEPS,
} from '../../data/services.data';
import styles from '../../styles/BookingModal.styles';
import Colors from '../../styles/colors';

export default function BookingModal({ visible, preselectedCategory, onClose, onSubmit }) {
  const bm = useBookingModal(visible, preselectedCategory, onSubmit, onClose);

  const primaryEnabled = bm.step === 1 ? bm.canStep1 : bm.step === 2 ? bm.canStep2 : true;

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.overlay}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.kavWrap}>
          <View style={styles.sheet}>
            <View style={styles.handle} />

            {/* ── Header ── */}
            <View style={styles.header}>
              <View style={{ flex: 1 }}>
                {bm.step > 1 && !bm.submitted && (
                  <TouchableOpacity style={styles.backChevron} onPress={() => bm.setStep(s => s - 1)}>
                    <Ionicons name="chevron-back" size={14} color={Colors.skillPrimary} />
                    <Text style={styles.backChevronText}>Back</Text>
                  </TouchableOpacity>
                )}
                <Text style={styles.title}>
                  {bm.submitted ? 'Request Submitted!' : 'Book a Service'}
                </Text>
                {!bm.submitted && (
                  <Text style={styles.stepLabel}>
                    {`STEP ${bm.step} OF 3 — ${['CHOOSE SERVICE', 'FILL DETAILS', 'CONFIRM'][bm.step - 1]}`}
                  </Text>
                )}
              </View>
              {!bm.submitted && (
                <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
                  <Ionicons name="close" size={18} color={Colors.textMuted} />
                </TouchableOpacity>
              )}
            </View>

            {/* ── Progress bar ── */}
            {!bm.submitted && (
              <View style={styles.progressRow}>
                {[1, 2, 3].map(s => (
                  <View key={s} style={[styles.progressBar, s <= bm.step && styles.progressBarActive]} />
                ))}
              </View>
            )}

            {/* ── Step 1: Choose Service ── */}
            {!bm.submitted && bm.step === 1 && (
              <ScrollView style={styles.body} showsVerticalScrollIndicator={false}>
                <Text style={styles.stepQuestion}>What type of service do you need?</Text>
                {SERVICE_CATEGORIES.map(cat => {
                  const isSelected = bm.selectedCat?.value === cat.value;
                  return (
                    <TouchableOpacity
                      key={cat.value}
                      style={[styles.serviceRow, isSelected && styles.serviceRowSelected, isSelected && { borderColor: cat.color }]}
                      onPress={() => bm.setSelectedCat(cat)}
                      activeOpacity={0.75}
                    >
                      <View style={[styles.serviceIconWrap, { backgroundColor: cat.bg }]}>
                        <Ionicons name={cat.icon} size={20} color={cat.color} />
                      </View>
                      <View style={styles.serviceInfo}>
                        <Text style={styles.serviceName}>{cat.label}</Text>
                        <Text style={styles.serviceIssueCount}>{cat.issues.length} common issues</Text>
                      </View>
                      {isSelected && <Ionicons name="checkmark-circle" size={20} color={cat.color} />}
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            )}

            {/* ── Step 2: Fill Details ── */}
            {!bm.submitted && bm.step === 2 && (
              <ScrollView style={styles.body} showsVerticalScrollIndicator={false} keyboardShouldPersistTaps="handled">
                {/* Problem presets */}
                <Text style={styles.fieldLabel}>WHAT IS THE PROBLEM? *</Text>
                {(bm.selectedCat?.issues ?? []).map(issue => {
                  const isSelected = bm.selectedIssue === issue;
                  return (
                    <TouchableOpacity
                      key={issue}
                      style={[styles.issueRow, isSelected && styles.issueRowSelected]}
                      onPress={() => bm.setSelectedIssue(issue)}
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
                    const isSelected = bm.selectedBudget === opt.value;
                    return (
                      <TouchableOpacity
                        key={opt.id}
                        style={[styles.budgetTile, isSelected && styles.budgetTileSelected]}
                        onPress={() => bm.setSelectedBudget(opt.value)}
                      >
                        <Ionicons name="cash-outline" size={12} color={isSelected ? Colors.skillPrimary : Colors.textMuted} />
                        <Text style={[styles.budgetTileText, isSelected && styles.budgetTileTextSelected]}>
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
                    const isSelected = bm.selectedStart === opt.value;
                    return (
                      <TouchableOpacity
                        key={opt.id}
                        style={[styles.startTile, isSelected && styles.startTileSelected]}
                        onPress={() => bm.setSelectedStart(opt.value)}
                      >
                        <Text style={[styles.startTileLabel, isSelected && styles.startTileLabelSel]}>{opt.label}</Text>
                        <Text style={[styles.startTileSub, isSelected && styles.startTileSubSel]}>{opt.sub}</Text>
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
                  value={bm.address}
                  onChangeText={bm.setAddress}
                />
              </ScrollView>
            )}

            {/* ── Step 3: Confirm ── */}
            {!bm.submitted && bm.step === 3 && (
              <ScrollView style={styles.body} showsVerticalScrollIndicator={false}>
                <Text style={styles.confirmIntro}>Review your request before submitting.</Text>
                {BOOKING_REVIEW_ROWS.map(row => (
                  <View key={row.key} style={styles.reviewRow}>
                    <View style={styles.reviewIconWrap}>
                      <Ionicons name={row.icon} size={16} color={Colors.skillPrimary} />
                    </View>
                    <View style={styles.reviewContent}>
                      <Text style={styles.reviewLabel}>{row.label}</Text>
                      <Text style={styles.reviewValue}>{bm.reviewData[row.key]}</Text>
                    </View>
                  </View>
                ))}

                {/* What happens next */}
                <View style={styles.nextBox}>
                  <View style={styles.nextBoxHeader}>
                    <Ionicons name="sparkles-outline" size={14} color={Colors.skillPrimary} />
                    <Text style={styles.nextBoxTitle}>What happens next</Text>
                  </View>
                  {BOOKING_NEXT_STEPS.map((item, i) => (
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
            {bm.submitted && (
              <View style={styles.successBlock}>
                <View style={styles.successIconWrap}>
                  <Ionicons name="checkmark-circle" size={48} color={Colors.skillPrimary} />
                </View>
                <Text style={styles.successTitle}>Request Submitted!</Text>
                <Text style={styles.successSub}>Finding matched workers near you…</Text>
              </View>
            )}

            {/* ── Footer buttons ── */}
            {!bm.submitted && (
              <View style={styles.footer}>
                {bm.step === 1 ? (
                  <TouchableOpacity style={styles.cancelBtn} onPress={onClose}>
                    <Text style={styles.cancelBtnText}>Cancel</Text>
                  </TouchableOpacity>
                ) : (
                  <TouchableOpacity style={styles.backBtn} onPress={() => bm.setStep(s => s - 1)}>
                    <Text style={styles.backBtnText}>Back</Text>
                  </TouchableOpacity>
                )}

                <TouchableOpacity
                  style={[styles.primaryBtn, !primaryEnabled && styles.primaryBtnDim]}
                  onPress={bm.step === 3 ? bm.handleSubmit : bm.handleNext}
                  disabled={!primaryEnabled || bm.submitting}
                  activeOpacity={0.85}
                >
                  <LinearGradient
                    colors={primaryEnabled ? [Colors.skillPrimary, Colors.emerald700] : [Colors.borderBase, Colors.borderBase]}
                    start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
                    style={styles.primaryBtnGrad}
                  >
                    {bm.submitting ? (
                      <ActivityIndicator color="#fff" size="small" />
                    ) : (
                      <View style={styles.btnRow}>
                        <Text style={styles.primaryBtnText}>
                          {bm.step === 3 ? 'Find Matched Workers' : 'Continue'}
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