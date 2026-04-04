// hooks/resident/useBookingModal.js
// Custom hook — all state and logic for the 3-step BookingModal.
// BookingModal.js imports this and is a pure render component.
//
// Returns:
//   step, setStep
//   selectedCat, setSelectedCat
//   selectedIssue, setSelectedIssue
//   selectedBudget, setSelectedBudget
//   selectedStart, setSelectedStart
//   address, setAddress
//   submitting, submitted
//   canStep1, canStep2
//   reviewData        — assembled object for Step 3 review rows
//   handleNext        — advances step when guard passes
//   handleSubmit      — async, calls onSubmit(data) then sets submitted

import { useState, useEffect } from 'react';
import {
  BUDGET_OPTIONS,
  PREFERRED_START_OPTIONS,
} from '../../data/services.data';

export function useBookingModal(visible, preselectedCategory, onSubmit, onClose) {

  const [step,           setStep]           = useState(1);
  const [selectedCat,    setSelectedCat]    = useState(null);
  const [selectedIssue,  setSelectedIssue]  = useState(null);
  const [selectedBudget, setSelectedBudget] = useState(null);
  const [selectedStart,  setSelectedStart]  = useState(null);
  const [address,        setAddress]        = useState('');
  const [submitting,     setSubmitting]     = useState(false);
  const [submitted,      setSubmitted]      = useState(false);

  // Reset every time the modal opens; apply preselection if provided
  useEffect(() => {
    if (!visible) return;
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
  }, [visible]);

  // Step guards
  const canStep1 = !!selectedCat;
  const canStep2 = !!selectedIssue && !!selectedBudget && !!selectedStart && !!address.trim();

  function handleNext() {
    if (step === 1 && canStep1) setStep(2);
    else if (step === 2 && canStep2) setStep(3);
  }

  // Resolve display labels for Step 3 summary
  const budgetLabel = BUDGET_OPTIONS.find(b => b.value === selectedBudget)?.label ?? '';
  const startLabel  = PREFERRED_START_OPTIONS.find(s => s.value === selectedStart)?.label ?? '';

  const reviewData = {
    service:         selectedCat?.label ?? '',
    issue:           selectedIssue ?? '',
    budget:          budgetLabel,
    preferred_start: startLabel,
    schedule:        'Flexible / Any Time',
    address,
  };

  async function handleSubmit() {
    setSubmitting(true);
    await new Promise(r => setTimeout(r, 900));

    onSubmit({
      id:              Date.now(),
      title:           `${selectedCat.label} Service`,
      service:         selectedCat.value,
      status:          'pending',
      date:            'Just now',
      daily_rate:      null,
      worker:          null,
      rated:           false,
      issue:           selectedIssue,
      budget:          budgetLabel,
      preferred_start: startLabel,
      address,
    });

    setSubmitting(false);
    setSubmitted(true);
    setTimeout(() => onClose(), 1600);
  }

  return {
    step,          setStep,
    selectedCat,   setSelectedCat,
    selectedIssue, setSelectedIssue,
    selectedBudget,setSelectedBudget,
    selectedStart, setSelectedStart,
    address,       setAddress,
    submitting,    submitted,
    canStep1,      canStep2,
    reviewData,
    handleNext,
    handleSubmit,
  };
}