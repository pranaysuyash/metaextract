/**
 * Accessibility Context Provider
 * 
 * Provides centralized accessibility state management and utilities for the application.
 * Manages focus, ARIA announcements, keyboard navigation, and user preferences.
 * 
 * @module accessibility-context
 * @validates Requirements 1.1, 1.2, 1.3, 1.5 - Core accessibility infrastructure
 */

import React, { createContext, useContext, useEffect, useState, useCallback, useRef, useMemo } from 'react';

// ============================================================================
// Types
// ============================================================================

export interface AccessibilityState {
  // Motion preferences
  prefersReducedMotion: boolean;
  
  // Focus management
  focusVisible: boolean;
  focusWithin: boolean;
  
  // Screen reader state
  announcements: string[];
  liveRegionContent: string;
  
  // Keyboard navigation
  keyboardNavigation: boolean;
  currentFocusId: string | null;
  
  // High contrast mode
  highContrast: boolean;
  
  // Touch/mobile preferences
  prefersTouchTargets: boolean;
}

export interface AccessibilityActions {
  // Announcements
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  clearAnnouncements: () => void;
  
  // Focus management
  setFocusVisible: (visible: boolean) => void;
  setCurrentFocus: (elementId: string | null) => void;
  trapFocus: (containerId: string) => () => void;
  
  // Keyboard navigation
  setKeyboardNavigation: (enabled: boolean) => void;
  
  // Preferences
  toggleHighContrast: () => void;
  updateMotionPreference: () => void;
}

export interface AccessibilityContextValue extends AccessibilityState, AccessibilityActions {
  // Utility functions
  isReducedMotion: () => boolean;
  shouldShowFocusRing: () => boolean;
  getAriaLiveRegion: () => HTMLElement | null;
}

// ============================================================================
// Context
// ============================================================================

const AccessibilityContext = createContext<AccessibilityContextValue | undefined>(undefined);

// ============================================================================
// Provider Component
// ============================================================================

export interface AccessibilityProviderProps {
  children: React.ReactNode;
}

export function AccessibilityProvider({ children }: AccessibilityProviderProps) {
  // State
  const [state, setState] = useState<AccessibilityState>({
    prefersReducedMotion: false,
    focusVisible: false,
    focusWithin: false,
    announcements: [],
    liveRegionContent: '',
    keyboardNavigation: false,
    currentFocusId: null,
    highContrast: false,
    prefersTouchTargets: false,
  });
  
  // Refs for managing DOM elements
  const liveRegionRef = useRef<HTMLElement | null>(null);
  const focusTrapRef = useRef<{
    container: HTMLElement;
    firstElement: HTMLElement;
    lastElement: HTMLElement;
    returnElement: HTMLElement;
  } | null>(null);
  
  // Initialize accessibility preferences
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const updateMotionPreference = () => {
      setState(prev => ({ ...prev, prefersReducedMotion: mediaQuery.matches }));
    };
    
    updateMotionPreference();
    mediaQuery.addEventListener('change', updateMotionPreference);
    
    // Check for high contrast preference
    const contrastQuery = window.matchMedia('(prefers-contrast: high)');
    const updateContrastPreference = () => {
      setState(prev => ({ ...prev, highContrast: contrastQuery.matches }));
    };
    
    updateContrastPreference();
    contrastQuery.addEventListener('change', updateContrastPreference);
    
    // Check for touch device
    const touchQuery = window.matchMedia('(pointer: coarse)');
    const updateTouchPreference = () => {
      setState(prev => ({ ...prev, prefersTouchTargets: touchQuery.matches }));
    };
    
    updateTouchPreference();
    touchQuery.addEventListener('change', updateTouchPreference);
    
    // Keyboard navigation detection
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        setState(prev => ({ ...prev, keyboardNavigation: true, focusVisible: true }));
      }
    };
    
    const handleMouseDown = () => {
      setState(prev => ({ ...prev, keyboardNavigation: false, focusVisible: false }));
    };
    
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);
    
    return () => {
      mediaQuery.removeEventListener('change', updateMotionPreference);
      contrastQuery.removeEventListener('change', updateContrastPreference);
      touchQuery.removeEventListener('change', updateTouchPreference);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);
  
  // Create or get ARIA live region
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    let liveRegion = document.getElementById('accessibility-live-region');
    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.id = 'accessibility-live-region';
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      document.body.appendChild(liveRegion);
    }
    liveRegionRef.current = liveRegion;
    
    return () => {
      if (liveRegion && liveRegion.parentNode) {
        liveRegion.parentNode.removeChild(liveRegion);
      }
    };
  }, []);
  
  // Actions
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    setState(prev => ({
      ...prev,
      announcements: [...prev.announcements, message],
      liveRegionContent: message,
    }));
    
    if (liveRegionRef.current) {
      liveRegionRef.current.setAttribute('aria-live', priority);
      liveRegionRef.current.textContent = message;
      
      // Clear after announcement
      setTimeout(() => {
        if (liveRegionRef.current) {
          liveRegionRef.current.textContent = '';
        }
      }, 1000);
    }
  }, []);
  
  const clearAnnouncements = useCallback(() => {
    setState(prev => ({ ...prev, announcements: [], liveRegionContent: '' }));
    if (liveRegionRef.current) {
      liveRegionRef.current.textContent = '';
    }
  }, []);
  
  const setFocusVisible = useCallback((visible: boolean) => {
    setState(prev => ({ ...prev, focusVisible: visible }));
  }, []);
  
  const setCurrentFocus = useCallback((elementId: string | null) => {
    setState(prev => ({ ...prev, currentFocusId: elementId }));
  }, []);
  
  const trapFocus = useCallback((containerId: string) => {
    const container = document.getElementById(containerId);
    if (!container) return () => {};
    
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
    const returnElement = document.activeElement as HTMLElement;
    
    focusTrapRef.current = { container, firstElement, lastElement, returnElement };
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;
      
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };
    
    container.addEventListener('keydown', handleKeyDown);
    firstElement?.focus();
    
    return () => {
      container.removeEventListener('keydown', handleKeyDown);
      if (focusTrapRef.current?.returnElement) {
        focusTrapRef.current.returnElement.focus();
      }
      focusTrapRef.current = null;
    };
  }, []);
  
  const setKeyboardNavigation = useCallback((enabled: boolean) => {
    setState(prev => ({ ...prev, keyboardNavigation: enabled }));
  }, []);
  
  const toggleHighContrast = useCallback(() => {
    setState(prev => ({ ...prev, highContrast: !prev.highContrast }));
  }, []);
  
  const updateMotionPreference = useCallback(() => {
    if (typeof window === 'undefined') return;
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setState(prev => ({ ...prev, prefersReducedMotion: mediaQuery.matches }));
  }, []);
  
  // Utility functions
  const isReducedMotion = useCallback(() => state.prefersReducedMotion, [state.prefersReducedMotion]);
  
  const shouldShowFocusRing = useCallback(() => {
    return state.keyboardNavigation && state.focusVisible;
  }, [state.keyboardNavigation, state.focusVisible]);
  
  const getAriaLiveRegion = useCallback(() => liveRegionRef.current, []);
  
  const value = useMemo<AccessibilityContextValue>(() => ({
    ...state,
    announce,
    clearAnnouncements,
    setFocusVisible,
    setCurrentFocus,
    trapFocus,
    setKeyboardNavigation,
    toggleHighContrast,
    updateMotionPreference,
    isReducedMotion,
    shouldShowFocusRing,
    getAriaLiveRegion,
  }), [
    state,
    announce,
    clearAnnouncements,
    setFocusVisible,
    setCurrentFocus,
    trapFocus,
    setKeyboardNavigation,
    toggleHighContrast,
    updateMotionPreference,
    isReducedMotion,
    shouldShowFocusRing,
    getAriaLiveRegion,
  ]);
  
  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

/**
 * Hook to access accessibility context
 * @throws Error if used outside AccessibilityProvider
 */
export function useAccessibility(): AccessibilityContextValue {
  const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
}

// ============================================================================
// Utility Hooks
// ============================================================================

/**
 * Hook for managing focus trapping in modals/dialogs
 */
export function useFocusTrap(isActive: boolean, containerId?: string) {
  const { trapFocus } = useAccessibility();
  
  useEffect(() => {
    if (!isActive || !containerId) return;
    
    const cleanup = trapFocus(containerId);
    return cleanup;
  }, [isActive, containerId, trapFocus]);
}

/**
 * Hook for making announcements to screen readers
 */
export function useAnnounce() {
  const { announce } = useAccessibility();
  return announce;
}

/**
 * Hook for detecting keyboard navigation
 */
export function useKeyboardNavigation() {
  const { keyboardNavigation, shouldShowFocusRing } = useAccessibility();
  return { keyboardNavigation, shouldShowFocusRing };
}

/**
 * Hook for respecting motion preferences
 */
export function useMotionPreference() {
  const { prefersReducedMotion, isReducedMotion } = useAccessibility();
  return { prefersReducedMotion, isReducedMotion };
}

export default AccessibilityProvider;