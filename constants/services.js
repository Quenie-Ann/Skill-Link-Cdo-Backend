// constants/services.js
// Centralized data for all 5 pilot trade categories,
// booking budget options, and preferred start options.
// Import from here instead of defining inline in screens.

import Colors from '../styles/colors';

export const SERVICE_CATEGORIES = [
  {
    value:  'plumbing',
    label:  'Plumbing',
    icon:   'water-outline',
    color:  Colors.blue,
    bg:     Colors.blueBg,
    issues: [
      'Leaking pipe or faucet',
      'Clogged drain',
      'Water heater issue',
      'Low water pressure',
    ],
  },
  {
    value:  'electrical',
    label:  'Electrical',
    icon:   'flash-outline',
    color:  Colors.amber,
    bg:     Colors.amberBg,
    issues: [
      'Tripped circuit breaker',
      'Faulty outlet',
      'Flickering lights',
      'No power in room',
      'Overloaded circuit',
    ],
  },
  {
    value:  'carpentry',
    label:  'Carpentry',
    icon:   'hammer-outline',
    color:  Colors.amber,
    bg:     Colors.amberBg,
    issues: [
      'Broken furniture',
      'Cabinet installation',
      'Door or window repair',
      'Flooring issue',
    ],
  },
  {
    value:  'mason',
    label:  'Mason',
    icon:   'layers-outline',
    color:  Colors.skillDark,
    bg:     Colors.skillLight,
    issues: [
      'Cracked wall or ceiling',
      'Tile repair or installation',
      'Concrete patching',
      'Waterproofing',
    ],
  },
  {
    value:  'welding',
    label:  'Welding',
    icon:   'flame-outline',
    color:  Colors.teal,
    bg:     Colors.tealBg,
    issues: [
      'Gate or fence repair',
      'Metal fabrication',
      'Structural welding',
      'Grille installation',
    ],
  },
];

// Budget tiles — Step 2 of booking modal
// Uses daily-rate framing to match the web app and SRS
export const BUDGET_OPTIONS = [
  { id: 'b1', label: 'Under ₱300/day',    value: 'under_300'  },
  { id: 'b2', label: '₱300 – ₱400/day',  value: '300_400'    },
  { id: 'b3', label: '₱400 – ₱500/day',  value: '400_500'    },
  { id: 'b4', label: '₱500+/day',         value: '500_plus'   },
  { id: 'b5', label: 'Open / Negotiable', value: 'negotiable' },
];

// Preferred start tiles — Step 2 of booking modal
export const PREFERRED_START_OPTIONS = [
  { id: 's1', label: 'Today',         sub: 'Start as soon as possible today',  value: 'today'         },
  { id: 's2', label: 'Within 3 Days', sub: 'Flexible within the next 3 days', value: 'within_3_days' },
  { id: 's3', label: 'This Week',     sub: 'Anytime before the week ends',    value: 'this_week'     },
  { id: 's4', label: 'No Rush',       sub: 'Flexible — no specific deadline', value: 'no_rush'       },
];