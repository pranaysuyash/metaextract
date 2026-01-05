/**
 * Accessibility Configuration
 * 
 * Central configuration for accessibility features, WCAG compliance levels,
 * and accessibility-related constants used throughout the application.
 * 
 * @module accessibility-config
 * @validates Requirements 1.1, 1.2, 1.3, 1.5 - Accessibility standards and configuration
 */

// ============================================================================
// WCAG Compliance Configuration
// ============================================================================

export const WCAG_LEVELS = {
  A: 'A',
  AA: 'AA',
  AAA: 'AAA',
} as const;

export type WCAGLevel = typeof WCAG_LEVELS[keyof typeof WCAG_LEVELS];

export const ACCESSIBILITY_CONFIG = {
  // Target compliance level
  complianceLevel: WCAG_LEVELS.AA,
  
  // Color contrast requirements
  colorContrast: {
    // Normal text (under 18pt or under 14pt bold)
    normalText: {
      AA: 4.5,
      AAA: 7.0,
    },
    // Large text (18pt+ or 14pt+ bold)
    largeText: {
      AA: 3.0,
      AAA: 4.5,
    },
    // Non-text elements (icons, borders, etc.)
    nonTextElements: {
      AA: 3.0,
      AAA: 3.0,
    },
  },
  
  // Touch target sizes (in pixels)
  touchTargets: {
    minimum: 44, // WCAG AA requirement
    recommended: 48, // Better UX
    spacing: 8, // Minimum spacing between targets
  },
  
  // Animation and motion preferences
  motion: {
    respectReducedMotion: true,
    maxDuration: 5000, // 5 seconds max for auto-playing animations
    providePauseControls: true,
    defaultEasing: 'ease-in-out',
  },
  
  // Keyboard navigation
  keyboard: {
    skipLinksEnabled: true,
    focusIndicatorsVisible: true,
    customKeyBindings: {
      skipToMain: 'Alt+1',
      skipToNav: 'Alt+2',
      skipToFooter: 'Alt+3',
    },
  },
  
  // Screen reader preferences
  screenReader: {
    announcePageChanges: true,
    announceFormErrors: true,
    announceProgressUpdates: true,
    liveRegionPoliteDelay: 100, // ms
    liveRegionAssertiveDelay: 0, // ms
  },
  
  // Focus management
  focus: {
    trapInModals: true,
    returnAfterClose: true,
    visibleIndicators: true,
    skipHiddenElements: true,
  },
} as const;

// ============================================================================
// ARIA Constants
// ============================================================================

export const ARIA_ROLES = {
  // Landmark roles
  banner: 'banner',
  navigation: 'navigation',
  main: 'main',
  complementary: 'complementary',
  contentinfo: 'contentinfo',
  search: 'search',
  
  // Widget roles
  button: 'button',
  checkbox: 'checkbox',
  dialog: 'dialog',
  menuitem: 'menuitem',
  option: 'option',
  progressbar: 'progressbar',
  slider: 'slider',
  tab: 'tab',
  tabpanel: 'tabpanel',
  textbox: 'textbox',
  
  // Document structure roles
  article: 'article',
  heading: 'heading',
  img: 'img',
  list: 'list',
  listitem: 'listitem',
  table: 'table',
  
  // Live region roles
  alert: 'alert',
  log: 'log',
  status: 'status',
  
  // Abstract roles (for reference)
  widget: 'widget',
  composite: 'composite',
  
  // Application-specific
  application: 'application',
  document: 'document',
  presentation: 'presentation',
  none: 'none',
} as const;

export const ARIA_PROPERTIES = {
  // Labels and descriptions
  label: 'aria-label',
  labelledby: 'aria-labelledby',
  describedby: 'aria-describedby',
  
  // States
  expanded: 'aria-expanded',
  selected: 'aria-selected',
  checked: 'aria-checked',
  disabled: 'aria-disabled',
  hidden: 'aria-hidden',
  pressed: 'aria-pressed',
  
  // Properties
  required: 'aria-required',
  invalid: 'aria-invalid',
  readonly: 'aria-readonly',
  multiline: 'aria-multiline',
  
  // Live regions
  live: 'aria-live',
  atomic: 'aria-atomic',
  relevant: 'aria-relevant',
  busy: 'aria-busy',
  
  // Relationships
  controls: 'aria-controls',
  owns: 'aria-owns',
  flowto: 'aria-flowto',
  
  // Values
  valuenow: 'aria-valuenow',
  valuemin: 'aria-valuemin',
  valuemax: 'aria-valuemax',
  valuetext: 'aria-valuetext',
  
  // Modal
  modal: 'aria-modal',
  
  // Grid/Table
  rowcount: 'aria-rowcount',
  colcount: 'aria-colcount',
  rowindex: 'aria-rowindex',
  colindex: 'aria-colindex',
} as const;

export const LIVE_REGION_TYPES = {
  off: 'off',
  polite: 'polite',
  assertive: 'assertive',
} as const;

// ============================================================================
// Keyboard Navigation Constants
// ============================================================================

export const KEYBOARD_KEYS = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End',
  PAGE_UP: 'PageUp',
  PAGE_DOWN: 'PageDown',
} as const;

export const FOCUSABLE_SELECTORS = [
  'button:not([disabled])',
  '[href]',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
  '[contenteditable="true"]',
  'audio[controls]',
  'video[controls]',
  'details > summary',
] as const;

// ============================================================================
// Skip Link Configuration
// ============================================================================

export const SKIP_LINKS = [
  {
    id: 'skip-to-main',
    text: 'Skip to main content',
    target: 'main-content',
    key: '1',
  },
  {
    id: 'skip-to-nav',
    text: 'Skip to navigation',
    target: 'main-navigation',
    key: '2',
  },
  {
    id: 'skip-to-footer',
    text: 'Skip to footer',
    target: 'main-footer',
    key: '3',
  },
] as const;

// ============================================================================
// Error Messages
// ============================================================================

export const ACCESSIBILITY_ERRORS = {
  MISSING_LABEL: 'Interactive element is missing an accessible label',
  MISSING_ALT_TEXT: 'Image is missing alternative text',
  LOW_CONTRAST: 'Text does not meet minimum color contrast requirements',
  MISSING_FOCUS_INDICATOR: 'Focusable element lacks visible focus indicator',
  INVALID_HEADING_HIERARCHY: 'Heading levels are not in logical order',
  MISSING_SKIP_LINKS: 'Page is missing skip navigation links',
  FOCUS_TRAP_FAILED: 'Focus trap could not be established',
  LIVE_REGION_MISSING: 'Required live region for announcements is missing',
  KEYBOARD_TRAP: 'Keyboard focus is trapped without escape mechanism',
  MISSING_FORM_LABELS: 'Form inputs are missing proper labels',
} as const;

// ============================================================================
// Testing Configuration
// ============================================================================

export const ACCESSIBILITY_TESTING = {
  // Automated testing rules
  axeRules: {
    // Enable all WCAG 2.1 AA rules
    tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
    
    // Custom rule configuration
    rules: {
      'color-contrast': { enabled: true },
      'keyboard-navigation': { enabled: true },
      'focus-order-semantics': { enabled: true },
      'aria-required-attr': { enabled: true },
      'aria-valid-attr-value': { enabled: true },
      'button-name': { enabled: true },
      'form-field-multiple-labels': { enabled: true },
      'heading-order': { enabled: true },
      'image-alt': { enabled: true },
      'label': { enabled: true },
      'link-name': { enabled: true },
      'skip-link': { enabled: true },
    },
  },
  
  // Manual testing checklist
  manualTests: [
    'Screen reader navigation',
    'Keyboard-only navigation',
    'High contrast mode',
    'Zoom to 200%',
    'Focus management in modals',
    'Form error handling',
    'Live region announcements',
    'Skip link functionality',
  ],
  
  // Performance thresholds
  performance: {
    maxFocusDelay: 100, // ms
    maxAnnouncementDelay: 200, // ms
    maxContrastCalculationTime: 50, // ms
  },
} as const;

// ============================================================================
// CSS Classes for Accessibility
// ============================================================================

export const ACCESSIBILITY_CLASSES = {
  // Screen reader only content
  srOnly: 'sr-only',
  
  // Focus indicators
  focusVisible: 'focus-visible',
  focusWithin: 'focus-within',
  
  // Skip links
  skipLink: 'skip-link',
  skipLinkVisible: 'skip-link-visible',
  
  // High contrast mode
  highContrast: 'high-contrast',
  
  // Reduced motion
  reducedMotion: 'reduced-motion',
  
  // Touch targets
  touchTarget: 'touch-target',
  touchTargetLarge: 'touch-target-large',
  
  // Live regions
  liveRegion: 'live-region',
  liveRegionPolite: 'live-region-polite',
  liveRegionAssertive: 'live-region-assertive',
  
  // Focus traps
  focusTrap: 'focus-trap',
  focusTrapActive: 'focus-trap-active',
} as const;

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Gets the minimum contrast ratio for the current compliance level
 */
export function getMinimumContrastRatio(isLargeText: boolean = false): number {
  const level = ACCESSIBILITY_CONFIG.complianceLevel;
  return isLargeText 
    ? ACCESSIBILITY_CONFIG.colorContrast.largeText[level]
    : ACCESSIBILITY_CONFIG.colorContrast.normalText[level];
}

/**
 * Gets the minimum touch target size
 */
export function getMinimumTouchTargetSize(): number {
  return ACCESSIBILITY_CONFIG.touchTargets.minimum;
}

/**
 * Checks if reduced motion is preferred
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Checks if high contrast is preferred
 */
export function prefersHighContrast(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-contrast: high)').matches;
}

/**
 * Gets the appropriate ARIA live region type for a message priority
 */
export function getLiveRegionType(priority: 'low' | 'medium' | 'high'): string {
  switch (priority) {
    case 'high':
      return LIVE_REGION_TYPES.assertive;
    case 'medium':
    case 'low':
    default:
      return LIVE_REGION_TYPES.polite;
  }
}

export default ACCESSIBILITY_CONFIG;