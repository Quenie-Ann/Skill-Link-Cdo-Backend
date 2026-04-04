// hooks/resident/useFindWorkers.js
// Custom hook — all state and logic for FindWorkers.js.
// FindWorkers.js imports this and is a pure render component.
//
// Args:
//   request  {object} — submitted request from BookingModal (service, issue, address)
//
// Returns:
//   activeFilter      — currently selected filter tab value
//   setActiveFilter   — setter
//   sentOffers        — { [workerId]: true } map
//   filteredWorkers   — sorted, filtered worker list
//   filterTabs        — computed tab list (All + trades present in pool)
//   bannerService     — display string for ML results banner
//   bannerMeta        — sub-string for ML results banner
//   handleSendOffer   — marks a worker's offer as sent

import { useState, useMemo } from 'react';
import { MOCK_WORKERS }        from '../../data/workerPool.data';
import { SERVICE_CATEGORIES, ALL_FILTER_TAB } from '../../data/services.data';

export function useFindWorkers(request) {

  const [activeFilter, setActiveFilter] = useState('all');
  const [sentOffers,   setSentOffers]   = useState({});

  // Filter pool → sort by ml_score desc
  const filteredWorkers = useMemo(() => {
    const pool = activeFilter === 'all'
      ? MOCK_WORKERS
      : MOCK_WORKERS.filter(w => w.service === activeFilter);
    return [...pool].sort((a, b) => b.ml_score - a.ml_score);
  }, [activeFilter]);

  // Only show filter tabs for trades that have at least one worker in the pool
  const filterTabs = useMemo(() => {
    const tradesInPool = new Set(MOCK_WORKERS.map(w => w.service));
    const tradeTabs    = SERVICE_CATEGORIES.filter(c => tradesInPool.has(c.value));
    return [ALL_FILTER_TAB, ...tradeTabs];
  }, []);

  function handleSendOffer(worker) {
    setSentOffers(prev => ({ ...prev, [worker.id]: true }));
  }

  // ML results banner display strings
  const serviceCat   = SERVICE_CATEGORIES.find(c => c.value === request?.service);
  const bannerService = `${serviceCat?.label ?? request?.service ?? ''} · ${request?.issue ?? ''}`;
  const bannerMeta    = `Workers ranked by ML score · ${request?.address ?? ''}`;

  return {
    activeFilter,
    setActiveFilter,
    sentOffers,
    filteredWorkers,
    filterTabs,
    bannerService,
    bannerMeta,
    handleSendOffer,
  };
}