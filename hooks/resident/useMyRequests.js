// hooks/resident/useMyRequests.js
// Custom hook — all state and logic for MyRequests.js.
// MyRequests.js imports this and is a pure render component.
//
// Args:
//   newRequest  {object|null} — freshly submitted request to prepend (from nav param)
//
// Returns:
//   requests          — full request list
//   activeFilter      — currently selected filter key
//   setActiveFilter   — setter (also resets expandedId)
//   expandedId        — id of the currently expanded request card (or null)
//   filteredRequests  — derived list based on activeFilter
//   totalCount        — total requests count
//   activeCount       — matched + in_progress count
//   completedCount    — completed count
//   countFor(key)     — returns count for a given filter key
//   toggleExpand(id)  — toggles the expanded detail panel

import { useState, useMemo } from 'react';
import {
  RESIDENT_REQUESTS,
  FILTER_STATUSES,
} from '../../data/residentRequests.data';

export function useMyRequests(newRequest = null) {

  const [requests, setRequests] = useState(() =>
    newRequest ? [newRequest, ...RESIDENT_REQUESTS] : RESIDENT_REQUESTS
  );

  const [activeFilter, setActiveFilterRaw] = useState('all');
  const [expandedId,   setExpandedId]      = useState(null);

  // Changing the filter collapses any open detail panel
  function setActiveFilter(key) {
    setExpandedId(null);
    setActiveFilterRaw(key);
  }

  // Derived: filtered list
  const filteredRequests = useMemo(() => {
    const allowed = FILTER_STATUSES[activeFilter] ?? FILTER_STATUSES.all;
    return requests.filter(r => allowed.includes(r.status));
  }, [requests, activeFilter]);

  // Derived: stat counts
  const totalCount     = requests.length;
  const activeCount    = requests.filter(r => ['matched', 'in_progress'].includes(r.status)).length;
  const completedCount = requests.filter(r => r.status === 'completed').length;

  // Count for a given filter tab (used for badge pills)
  function countFor(key) {
    const allowed = FILTER_STATUSES[key] ?? [];
    return requests.filter(r => allowed.includes(r.status)).length;
  }

  function toggleExpand(id) {
    setExpandedId(prev => (prev === id ? null : id));
  }

  return {
    requests,
    activeFilter,
    setActiveFilter,
    expandedId,
    filteredRequests,
    totalCount,
    activeCount,
    completedCount,
    countFor,
    toggleExpand,
  };
}