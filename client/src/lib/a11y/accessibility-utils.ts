/**
 * Accessibility utilities and components for WCAG 2.1 AA compliance
 */

import React, { useEffect, useRef, useState } from 'react';

// ARIA utilities
export const generateId = (): string => {
  return `aria-${Math.random().toString(36).substr(2, 9)}-${Date.now()}`;
};

export const useId = (): string => {
  const [id] = useState(() => generateId());
  return id;
};

export interface AriaAttributes {
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-controls'?: string;
  'aria-expanded'?: boolean;
  'aria-selected'?: boolean;
  'aria-hidden'?: boolean;
  'aria-live'?: 'polite' | 'assertive' | 'off';
  'aria-atomic'?: boolean;
  'aria-relevant'?: 'additions' | 'removals' | 'text' | 'all';
  'aria-busy'?: boolean;
  'aria-current'?: 'page' | 'step' | 'location' | 'date' | 'time' | boolean;
  'aria-disabled'?: boolean;
  'aria-invalid'?: boolean | 'grammar' | 'spelling';
  'aria-haspopup'?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog';
  'aria-pressed'?: boolean;
  'aria-checked'?: boolean;
  'aria-sort'?: 'ascending' | 'descending' | 'none' | 'other';
  'aria-valuemin'?: number;
  'aria-valuemax'?: number;
  'aria-valuenow'?: number;
  'aria-valuetext'?: string;
}

// Focus management utilities
export const useFocusTrap = (isActive: boolean = true) => {
  const containerRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const focusableElements = containerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>;

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey && document.activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    // Focus first element when trap activates
    firstElement.focus();

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isActive]);

  return containerRef;
};

export const useFocusManagement = () => {
  const [focusedElement, setFocusedElement] = useState<HTMLElement | null>(null);

  useEffect(() => {
    const handleFocus = (e: FocusEvent) => {
      setFocusedElement(e.target as HTMLElement);
    };

    document.addEventListener('focusin', handleFocus);

    return () => {
      document.removeEventListener('focusin', handleFocus);
    };
  }, []);

  const focusElement = (selector: string) => {
    const element = document.querySelector<HTMLElement>(selector);
    if (element) {
      element.focus();
    }
  };

  return {
    focusedElement,
    focusElement
  };
};

// Color contrast utilities
export const calculateContrastRatio = (color1: string, color2: string): number => {
  const luminance = (color: string) => {
    const rgb = color.match(/\d+/g)?.map(Number) || [];
    const [r, g, b] = rgb.map(val => {
      const srgb = val / 255;
      return srgb <= 0.03928 ? srgb / 12.92 : Math.pow((srgb + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const lum1 = luminance(color1) + 0.05;
  const lum2 = luminance(color2) + 0.05;
  const ratio = Math.max(lum1, lum2) / Math.min(lum1, lum2);

  return Number(ratio.toFixed(2));
};

export const meetsContrastStandard = (
  color1: string, 
  color2: string, 
  level: 'AA' | 'AAA' = 'AA'
): boolean => {
  const ratio = calculateContrastRatio(color1, color2);
  
  if (level === 'AAA') {
    return ratio >= 7.0; // Enhanced contrast
  }
  
  return ratio >= 4.5; // Minimum contrast
};

// Screen reader utilities
export const ScreenReaderOnly: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <span 
      style={{
        position: 'absolute',
        width: '1px',
        height: '1px',
        padding: '0',
        margin: '-1px',
        overflow: 'hidden',
        clip: 'rect(0, 0, 0, 0)',
        whiteSpace: 'nowrap',
        borderWidth: '0'
      }}
      className="sr-only"
    >
      {children}
    </span>
  );
};

export const SkipLink: React.FC<{ target: string; children: string }> = ({ target, children }) => {
  return (
    <a
      href={target}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded focus:shadow-lg"
    >
      {children}
    </a>
  );
};

// Live region utilities
export interface LiveRegionProps {
  children: React.ReactNode;
  priority?: 'polite' | 'assertive';
  className?: string;
}

export const LiveRegion: React.FC<LiveRegionProps> = ({ 
  children, 
  priority = 'polite',
  className = 'sr-only'
}) => {
  return (
    <div
      role="status"
      aria-live={priority}
      aria-atomic="true"
      className={className}
    >
      {children}
    </div>
  );
};

// Focus indicator utilities
export const useFocusVisible = () => {
  const [isUsingKeyboard, setIsUsingKeyboard] = useState(false);

  useEffect(() => {
    const handleMouseDown = () => setIsUsingKeyboard(false);
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') setIsUsingKeyboard(true);
    };

    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return { isUsingKeyboard };
};

// Reduced motion utilities
export const usePrefersReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return prefersReducedMotion;
};

// Focus outline utilities
export const useFocusOutline = () => {
  const [hasFocus, setHasFocus] = useState(false);

  const onFocus = () => setHasFocus(true);
  const onBlur = () => setHasFocus(false);

  return {
    hasFocus,
    onFocus,
    onBlur,
    focusClassName: hasFocus 
      ? 'ring-2 ring-ring ring-offset-2 ring-offset-background' 
      : 'ring-0'
  };
};

// Keyboard navigation utilities
export const useKeyboardNavigation = <T extends HTMLElement>() => {
  const [isNavigatingWithKeyboard, setIsNavigatingWithKeyboard] = useState(false);
  const ref = useRef<T>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        setIsNavigatingWithKeyboard(true);
      }
    };

    const handleMouseDown = () => {
      setIsNavigatingWithKeyboard(false);
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  return {
    ref,
    isNavigatingWithKeyboard
  };
};

// Accessibility checker utilities
export interface AccessibilityCheckResult {
  id: string;
  type: 'error' | 'warning' | 'notice';
  message: string;
  element?: Element;
  impact: 'minor' | 'moderate' | 'serious' | 'critical';
}

export const runAccessibilityCheck = async (
  element: HTMLElement | Document = document.body
): Promise<AccessibilityCheckResult[]> => {
  // In a real implementation, this would run axe-core or similar
  // For now, we'll return an empty array
  return [];
};

// High contrast mode utilities
export const useHighContrastMode = (): boolean => {
  const [isHighContrast, setIsHighContrast] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    setIsHighContrast(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setIsHighContrast(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return isHighContrast;
};

// Reduced transparency utilities
export const usePrefersReducedTransparency = (): boolean => {
  const [prefersReducedTransparency, setPrefersReducedTransparency] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-transparency: reduce)');
    setPrefersReducedTransparency(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedTransparency(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return prefersReducedTransparency;
};

// Dark mode utilities
export const useSystemDarkMode = (): boolean => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setIsDarkMode(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setIsDarkMode(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return isDarkMode;
};

// Focus management for modals
export const useModalFocus = (isOpen: boolean) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Store the currently focused element
      previousActiveElement.current = document.activeElement as HTMLElement;
      
      // Focus the modal container
      if (modalRef.current) {
        modalRef.current.focus();
      }
    } else if (previousActiveElement.current) {
      // Return focus to the element that was focused before the modal opened
      previousActiveElement.current.focus();
    }
  }, [isOpen]);

  return modalRef;
};

// Accessibility context provider
interface AccessibilityContextType {
  isUsingKeyboard: boolean;
  prefersReducedMotion: boolean;
  prefersReducedTransparency: boolean;
  isHighContrast: boolean;
  isDarkMode: boolean;
  focusOutline: string;
  setFocusOutline: (className: string) => void;
}

const AccessibilityContext = React.createContext<AccessibilityContextType | undefined>(undefined);

export const AccessibilityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [focusOutline, setFocusOutline] = useState('focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background');
  
  const isUsingKeyboard = useFocusVisible();
  const prefersReducedMotion = usePrefersReducedMotion();
  const prefersReducedTransparency = usePrefersReducedTransparency();
  const isHighContrast = useHighContrastMode();
  const isDarkMode = useSystemDarkMode();

  const contextValue = {
    isUsingKeyboard: isUsingKeyboard,
    prefersReducedMotion,
    prefersReducedTransparency,
    isHighContrast,
    isDarkMode,
    focusOutline,
    setFocusOutline
  };

  return (
    <AccessibilityContext.Provider value={contextValue}>
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = () => {
  const context = React.useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

// Export all accessibility utilities
export {
  generateId,
  useId,
  useFocusTrap,
  useFocusManagement,
  calculateContrastRatio,
  meetsContrastStandard,
  ScreenReaderOnly,
  SkipLink,
  LiveRegion,
  useFocusVisible,
  usePrefersReducedMotion,
  useFocusOutline,
  useKeyboardNavigation,
  runAccessibilityCheck,
  useHighContrastMode,
  usePrefersReducedTransparency,
  useSystemDarkMode,
  useModalFocus
};