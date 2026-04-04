// data/residentRequests.data.js
// All resident-side static data and UI config maps:
//   INITIAL_REQUESTS    — dashboard seed (recent activity preview)
//   RESIDENT_REQUESTS   — full history for MyRequests screen
//   REQUEST_STATUS_CONFIG — maps status → badge label + colors + progress step index
//   REQUEST_PROGRESS_STEPS — 4-step progress dot labels
//   MY_REQUESTS_FILTERS — filter tab definitions for MyRequests
//   FILTER_STATUSES     — maps filter key → matching status values
//   REQUEST_DETAIL_ROWS — icon/label config for the expanded inline detail panel

import Colors from '../styles/colors';

// Dashboard seed 
export const INITIAL_REQUESTS = [
  {
    id:              1,
    title:           'Electrical Repair',
    service:         'electrical',
    status:          'matched',
    issue:           'Tripped circuit breaker',
    date:            'March 21, 2026',
    daily_rate:      650,
    worker:          'Juan Dela Cruz',
    address:         'Zone 1, Bulua, CDO',
    budget:          '₱400 – ₱500/day',
    preferred_start: 'Within 3 Days',
    rated:           false,
  },
  {
    id:              2,
    title:           'Kitchen Plumbing',
    service:         'plumbing',
    status:          'completed',
    issue:           'Leaking pipe or faucet',
    date:            'Feb 24, 2026',
    daily_rate:      550,
    worker:          'Pedro Santos',
    address:         'Zone 1, Bulua, CDO',
    budget:          '₱400 – ₱500/day',
    preferred_start: 'Today',
    rated:           false,
  },
  {
    id:              3,
    title:           'Roof Carpentry',
    service:         'carpentry',
    status:          'completed',
    issue:           'Broken furniture',
    date:            'Feb 18, 2026',
    daily_rate:      500,
    worker:          'Ramon Reyes',
    address:         'Zone 1, Bulua, CDO',
    budget:          '₱400 – ₱500/day',
    preferred_start: 'This Week',
    rated:           true,
  },
  {
    id:              4,
    title:           'Cabinet Installation',
    service:         'carpentry',
    status:          'in_progress',
    issue:           'Cabinet installation',
    date:            'Feb 15, 2026',
    daily_rate:      600,
    worker:          'Pedro Santos',
    address:         'Zone 1, Bulua, CDO',
    budget:          '₱500+/day',
    preferred_start: 'Today',
    rated:           false,
  },
];

// Full history seed (MyRequests screen) 
export const RESIDENT_REQUESTS = [
  ...INITIAL_REQUESTS,
  {
    id:              5,
    title:           'Gate Welding',
    service:         'welding',
    status:          'pending',
    issue:           'Gate or fence repair',
    date:            'March 30, 2026',
    daily_rate:      null,
    worker:          null,
    address:         'Zone 1, Bulua, CDO',
    budget:          '₱300 – ₱400/day',
    preferred_start: 'No Rush',
    rated:           false,
  },
  {
    id:              6,
    title:           'Bathroom Tile Repair',
    service:         'mason',
    status:          'completed',
    issue:           'Tile repair or installation',
    date:            'Feb 10, 2026',
    daily_rate:      580,
    worker:          'Mario Bautista',
    address:         'Zone 1, Bulua, CDO',
    budget:          '₱500+/day',
    preferred_start: 'Today',
    rated:           true,
  },
  {
    id:              7,
    title:           'Living Room Plumbing',
    service:         'plumbing',
    status:          'pending',
    issue:           'Clogged drain',
    date:            'April 1, 2026',
    daily_rate:      null,
    worker:          null,
    address:         'Zone 1, Bulua, CDO',
    budget:          'Open / Negotiable',
    preferred_start: 'Within 3 Days',
    rated:           false,
  },
  {
    id:              8,
    title:           'Bedroom Outlet Fix',
    service:         'electrical',
    status:          'completed',
    issue:           'Faulty outlet',
    date:            'Jan 28, 2026',
    daily_rate:      650,
    worker:          'Rosa Lim',
    address:         'Zone 1, Bulua, CDO',
    budget:          '₱400 – ₱500/day',
    preferred_start: 'Today',
    rated:           true,
  },
];

// RequestCard: 4-step progress dot labels 
export const REQUEST_PROGRESS_STEPS = ['Pending', 'Matched', 'In Progress', 'Done'];

// RequestCard: status → badge label + colors + step index 
export const REQUEST_STATUS_CONFIG = {
  pending:     { stepIndex: 0, label: 'PENDING',        color: Colors.amber,        bg: Colors.amberBg    },
  matched:     { stepIndex: 1, label: 'OFFER ACCEPTED', color: Colors.skillPrimary, bg: Colors.emerald100 },
  in_progress: { stepIndex: 2, label: 'IN PROGRESS',    color: Colors.blue,         bg: Colors.blueBg     },
  completed:   { stepIndex: 3, label: 'COMPLETED',      color: Colors.skillDark,    bg: Colors.skillLight },
};

// MyRequests: filter tab definitions 
export const MY_REQUESTS_FILTERS = [
  { key: 'all',       label: 'All',       icon: 'list-outline'             },
  { key: 'pending',   label: 'Pending',   icon: 'time-outline'             },
  { key: 'active',    label: 'Active',    icon: 'flash-outline'            },
  { key: 'completed', label: 'Completed', icon: 'checkmark-circle-outline' },
];

// MyRequests: filter key → matching status values 
export const FILTER_STATUSES = {
  all:       ['pending', 'matched', 'in_progress', 'completed'],
  pending:   ['pending'],
  active:    ['matched', 'in_progress'],
  completed: ['completed'],
};

// MyRequests: expanded detail panel row config 
export const REQUEST_DETAIL_ROWS = [
  { key: 'issue',           label: 'PROBLEM',         icon: 'alert-circle-outline' },
  { key: 'budget',          label: 'BUDGET',          icon: 'cash-outline'         },
  { key: 'preferred_start', label: 'PREFERRED START', icon: 'time-outline'         },
  { key: 'address',         label: 'ADDRESS',         icon: 'location-outline'     },
];

// MyRequests: empty state messages per filter key 
export const EMPTY_STATE_MESSAGES = {
  all:       { icon: 'clipboard-outline',        title: 'No requests yet',       sub: 'Book your first service to get started.'            },
  pending:   { icon: 'time-outline',             title: 'No pending requests',   sub: 'Pending requests are waiting to be matched.'        },
  active:    { icon: 'flash-outline',            title: 'No active jobs',        sub: 'Once a worker accepts your offer, it appears here.' },
  completed: { icon: 'checkmark-circle-outline', title: 'No completed jobs yet', sub: 'Finished requests will show up here.'               },
};