/**
 * Accessibility Context Provider - Global accessibility state
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AccessibilityState {
  reducedMotion: boolean;
  highContrast: boolean;
  fontSize: 'normal' | 'large' | 'larger';
  screenReaderOnly: boolean;
  keyboardNavigation: boolean;
  focusVisible: boolean;
  colorBlindMode: boolean;
  dyslexicFont: boolean;
}

interface AccessibilityActions {
  toggleReducedMotion: () => void;
  toggleHighContrast: () => void;
  setFontSize: (size: 'normal' | 'large' | 'larger') => void;
  toggleScreenReaderMode: () => void;
  toggleKeyboardNavigation: () => void;
  toggleFocusVisible: () => void;
  toggleColorBlindMode: () => void;
  toggleDyslexicFont: () => void;
  resetPreferences: () => void;
}

const defaultState: AccessibilityState = {
  reducedMotion: false,
  highContrast: false,
  fontSize: 'normal',
  screenReaderOnly: false,
  keyboardNavigation: true,
  focusVisible: true,
  colorBlindMode: false,
  dyslexicFont: false,
};

const AccessibilityContext = createContext<
  (AccessibilityState & AccessibilityActions) | undefined
>(undefined);

export const AccessibilityProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AccessibilityState>(() => {
    // Load preferences from localStorage or use defaults
    const saved = localStorage.getItem('accessibility-preferences');
    return saved ? JSON.parse(saved) : defaultState;
  });

  // Sync with system preferences
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handleChange = (e: MediaQueryListEvent) => {
      setState(prev => ({
        ...prev,
        reducedMotion: e.matches
      }));
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Save preferences to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('accessibility-preferences', JSON.stringify(state));
  }, [state]);

  // Apply CSS classes based on preferences
  useEffect(() => {
    const root = document.documentElement;
    
    // Clear previous classes
    root.classList.remove(
      'high-contrast',
      'font-size-large',
      'font-size-larger',
      'reduced-motion',
      'color-blind-mode',
      'dyslexic-font'
    );
    
    // Add current classes
    if (state.highContrast) root.classList.add('high-contrast');
    if (state.fontSize === 'large') root.classList.add('font-size-large');
    if (state.fontSize === 'larger') root.classList.add('font-size-larger');
    if (state.reducedMotion) root.classList.add('reduced-motion');
    if (state.colorBlindMode) root.classList.add('color-blind-mode');
    if (state.dyslexicFont) root.classList.add('dyslexic-font');
  }, [state]);

  const toggleReducedMotion = () => {
    setState(prev => ({
      ...prev,
      reducedMotion: !prev.reducedMotion
    }));
  };

  const toggleHighContrast = () => {
    setState(prev => ({
      ...prev,
      highContrast: !prev.highContrast
    }));
  };

  const setFontSize = (size: 'normal' | 'large' | 'larger') => {
    setState(prev => ({
      ...prev,
      fontSize: size
    }));
  };

  const toggleScreenReaderMode = () => {
    setState(prev => ({
      ...prev,
      screenReaderOnly: !prev.screenReaderOnly
    }));
  };

  const toggleKeyboardNavigation = () => {
    setState(prev => ({
      ...prev,
      keyboardNavigation: !prev.keyboardNavigation
    }));
  };

  const toggleFocusVisible = () => {
    setState(prev => ({
      ...prev,
      focusVisible: !prev.focusVisible
    }));
  };

  const toggleColorBlindMode = () => {
    setState(prev => ({
      ...prev,
      colorBlindMode: !prev.colorBlindMode
    }));
  };

  const toggleDyslexicFont = () => {
    setState(prev => ({
      ...prev,
      dyslexicFont: !prev.dyslexicFont
    }));
  };

  const resetPreferences = () => {
    setState(defaultState);
  };

  const value = {
    ...state,
    toggleReducedMotion,
    toggleHighContrast,
    setFontSize,
    toggleScreenReaderMode,
    toggleKeyboardNavigation,
    toggleFocusVisible,
    toggleColorBlindMode,
    toggleDyslexicFont,
    resetPreferences,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      <div className={`
        ${state.highContrast ? 'high-contrast' : ''}
        ${state.fontSize === 'large' ? 'font-size-large' : ''}
        ${state.fontSize === 'larger' ? 'font-size-larger' : ''}
        ${state.reducedMotion ? 'reduced-motion' : ''}
        ${state.colorBlindMode ? 'color-blind-mode' : ''}
        ${state.dyslexicFont ? 'dyslexic-font' : ''}
      `}>
        {children}
      </div>
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

// Accessibility preference hook
export const useAccessibilityPreferences = () => {
  const context = useAccessibility();
  return {
    preferences: {
      reducedMotion: context.reducedMotion,
      highContrast: context.highContrast,
      fontSize: context.fontSize,
      screenReaderOnly: context.screenReaderOnly,
      keyboardNavigation: context.keyboardNavigation,
      focusVisible: context.focusVisible,
      colorBlindMode: context.colorBlindMode,
      dyslexicFont: context.dyslexicFont,
    },
    actions: {
      toggleReducedMotion: context.toggleReducedMotion,
      toggleHighContrast: context.toggleHighContrast,
      setFontSize: context.setFontSize,
      toggleScreenReaderMode: context.toggleScreenReaderMode,
      toggleKeyboardNavigation: context.toggleKeyboardNavigation,
      toggleFocusVisible: context.toggleFocusVisible,
      toggleColorBlindMode: context.toggleColorBlindMode,
      toggleDyslexicFont: context.toggleDyslexicFont,
      resetPreferences: context.resetPreferences,
    }
  };
};

// Accessibility utility functions
export const isScreenReaderOnly = () => {
  return document.body.classList.contains('screen-reader-only');
};

export const applyHighContrast = (enabled: boolean) => {
  if (enabled) {
    document.documentElement.classList.add('high-contrast');
  } else {
    document.documentElement.classList.remove('high-contrast');
  }
};

export const setFontSize = (size: 'normal' | 'large' | 'larger') => {
  document.documentElement.classList.remove('font-size-large', 'font-size-larger');
  if (size !== 'normal') {
    document.documentElement.classList.add(`font-size-${size}`);
  }
};

// CSS classes that should be defined in your CSS
/*
.high-contrast {
  filter: contrast(1.5) brightness(1.1);
}

.font-size-large {
  font-size: 1.2rem;
}

.font-size-larger {
  font-size: 1.4rem;
}

.reduced-motion * {
  animation-duration: 0.01ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.01ms !important;
}

.color-blind-mode {
  filter: url(#deuteranopia) !important; // Example filter
}

.dyslexic-font {
  font-family: 'OpenDyslexic', sans-serif !important;
}
*/