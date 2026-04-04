// hooks/resident/useResidentDashboard.js
// Custom hook — all state and logic for ResidentDashboard.js.
// ResidentDashboard.js imports this and is a pure render component.
//
// Returns:
//   requests          — current request list (seeded + newly submitted)
//   modalOpen         — boolean controlling BookingModal visibility
//   preselected       — category object passed to BookingModal (or null)
//   pendingCount      — derived count for stats row
//   activeCount       — derived count for stats row
//   doneCount         — derived count for stats row
//   openModal(cat?)   — opens modal, optionally with a preselected category
//   closeModal()      — closes modal
//   handleNewRequest  — prepends submitted request + navigates to FindWorkers

import { useState } from 'react';
import { INITIAL_REQUESTS } from '../../data/residentRequests.data';

export function useResidentDashboard(navigation) {

  const [requests,    setRequests]    = useState(INITIAL_REQUESTS);
  const [modalOpen,   setModalOpen]   = useState(false);
  const [preselected, setPreselected] = useState(null);

  // Derived stats
  const pendingCount = requests.filter(r => r.status === 'pending').length;
  const activeCount  = requests.filter(r => ['matched', 'in_progress'].includes(r.status)).length;
  const doneCount    = requests.filter(r => r.status === 'completed').length;

  function openModal(category = null) {
    setPreselected(category);
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
  }

  function handleNewRequest(data) {
    setRequests(prev => [data, ...prev]);
    setModalOpen(false);
    // Navigate to ML match results after booking
    navigation.navigate('FindWorkers', { request: data });
  }

  return {
    requests,
    modalOpen,
    preselected,
    pendingCount,
    activeCount,
    doneCount,
    openModal,
    closeModal,
    handleNewRequest,
  };
}