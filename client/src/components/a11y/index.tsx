/**
 * Accessibility Component Library - Reusable a11y patterns
 */

import React, { useState, useEffect, useRef, createContext, useContext, ReactNode } from 'react';

// Skip Links Component
export const SkipLinks: React.FC = () => {
  return (
    <nav className="skip-links" aria-label="Skip navigation">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <a href="#main-navigation" className="skip-link">
        Skip to navigation
      </a>
      <a href="#search" className="skip-link">
        Skip to search
      </a>
    </nav>
  );
};

// Live Region Component
interface LiveRegionProps {
  children: ReactNode;
  ariaLive?: 'polite' | 'assertive';
  id?: string;
}

export const LiveRegion: React.FC<LiveRegionProps> = ({ 
  children, 
  ariaLive = 'polite', 
  id 
}) => {
  return (
    <div
      id={id}
      role="status"
      aria-live={ariaLive}
      aria-atomic="true"
      className="sr-only"
    >
      {children}
    </div>
  );
};

// Focus Trap Component
interface FocusTrapProps {
  children: ReactNode;
  isActive?: boolean;
  returnFocus?: boolean;
}

export const FocusTrap: React.FC<FocusTrapProps> = ({ 
  children, 
  isActive = true,
  returnFocus = true 
}) => {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isActive) return;

    previousActiveElement.current = document.activeElement as HTMLElement;
    const focusableElements = getFocusableElements(wrapperRef.current);
    
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      const focusableElements = getFocusableElements(wrapperRef.current);
      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.shiftKey && document.activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (returnFocus && previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    };
  }, [isActive, returnFocus]);

  return <div ref={wrapperRef} tabIndex={-1}>{children}</div>;
};

// Helper function to get focusable elements
function getFocusableElements(container: HTMLElement | null): HTMLElement[] {
  if (!container) return [];
  
  return Array.from(
    container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
  ).filter(el => {
    const isVisible = (el as HTMLElement).offsetWidth > 0 || (el as HTMLElement).offsetHeight > 0;
    const isEnabled = !(el as HTMLButtonElement).disabled;
    return isVisible && isEnabled;
  }) as HTMLElement[];
}

// Announcer Component
interface AnnouncerProps {
  children: ReactNode;
  priority?: 'polite' | 'assertive';
}

export const Announcer: React.FC<AnnouncerProps> = ({ children, priority = 'polite' }) => {
  const [announcement, setAnnouncement] = useState<string | null>(null);
  const [id] = useState(() => `announcer-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    if (children) {
      setAnnouncement(children as string);
      
      // Clear announcement after a delay
      const timer = setTimeout(() => {
        setAnnouncement(null);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [children]);

  return (
    <div
      id={id}
      role="alert"
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    >
      {announcement}
    </div>
  );
};

// Accessibility Context
interface AccessibilityContextType {
  reducedMotion: boolean;
  highContrast: boolean;
  fontSize: 'normal' | 'large' | 'larger';
  toggleReducedMotion: () => void;
  toggleHighContrast: () => void;
  setFontSize: (size: 'normal' | 'large' | 'larger') => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const AccessibilityProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [reducedMotion, setReducedMotion] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [fontSize, setFontSize] = useState<'normal' | 'large' | 'larger'>('normal');

  useEffect(() => {
    // Check for user preference for reduced motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const toggleReducedMotion = () => {
    setReducedMotion(prev => !prev);
  };

  const toggleHighContrast = () => {
    setHighContrast(prev => !prev);
  };

  const value: AccessibilityContextType = {
    reducedMotion,
    highContrast,
    fontSize,
    toggleReducedMotion,
    toggleHighContrast,
    setFontSize,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      <div 
        className={`
          ${highContrast ? 'high-contrast' : ''}
          ${fontSize === 'large' ? 'font-size-large' : ''}
          ${fontSize === 'larger' ? 'font-size-larger' : ''}
          ${reducedMotion ? 'reduced-motion' : ''}
        `}
      >
        {children}
      </div>
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within AccessibilityProvider');
  }
  return context;
};

// Accessible Button Component
interface AccessibleButtonProps {
  children: ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  disabled?: boolean;
  ariaLabel?: string;
  className?: string;
}

export const AccessibleButton: React.FC<AccessibleButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  ariaLabel,
  className = ''
}) => {
  const handleClick = () => {
    if (!disabled) {
      onClick();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (!disabled) {
        onClick();
      }
    }
  };

  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
    outline: 'border border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200'
  };

  const disabledClasses = disabled 
    ? 'opacity-50 cursor-not-allowed' 
    : 'cursor-pointer';

  return (
    <button
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      aria-label={ariaLabel}
      aria-disabled={disabled}
      tabIndex={disabled ? -1 : 0}
      className={`
        px-4 py-2 rounded-md font-medium transition-colors
        ${variantClasses[variant]} 
        ${disabledClasses} 
        ${className}
      `}
    >
      {children}
    </button>
  );
};

// Accessible Modal Component
interface AccessibleModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  ariaLabel?: string;
}

export const AccessibleModal: React.FC<AccessibleModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  ariaLabel
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      // Focus the modal when it opens
      modalRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen) {
      // Prevent background scrolling
      document.body.style.overflow = 'hidden';
      
      // Handle escape key
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }
      };
      
      document.addEventListener('keydown', handleEscape);
      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = '';
      };
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <FocusTrap isActive={isOpen}>
      {/* eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50"
        role="button"
        tabIndex={0}
        aria-label="Close modal"
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClose(); } }}
        onKeyUp={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClose(); } }}
        onClick={onClose}
      >
        <div
          ref={modalRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby={ariaLabel ? undefined : "modal-title"}
          aria-describedby="modal-description"
          tabIndex={-1}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md"
          onClick={e => e.stopPropagation()}
        >
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 
                id="modal-title"
                className="text-xl font-bold text-gray-900 dark:text-white"
              >
                {title}
              </h2>
              <button
                onClick={onClose}
                aria-label="Close modal"
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <span className="sr-only">Close</span>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div id="modal-description">
              {children}
            </div>
          </div>
        </div>
      </div>
    </FocusTrap>
  );
};

// Accessible Table Component
interface AccessibleTableProps {
  headers: string[];
  data: unknown[][];
  caption?: string;
  className?: string;
}

export const AccessibleTable: React.FC<AccessibleTableProps> = ({
  headers,
  data,
  caption,
  className = ''
}) => {
  return (
    <div className="overflow-x-auto">
      <table className={`min-w-full divide-y divide-gray-200 dark:divide-gray-700 ${className}`}>
        {caption && (
          <caption className="sr-only">
            {caption}
          </caption>
        )}
        <thead className="bg-gray-50 dark:bg-gray-700">
          <tr>
            {headers.map((header, index) => (
              <th
                key={index}
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          {data.map((row, rowIndex) => (
            <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700'}>
              {row.map((cell, cellIndex) => (
                <td
                  key={cellIndex}
                  className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300"
                >
                  {String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Accessible Form Components
interface AccessibleInputProps {
  id: string;
  label: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  required?: boolean;
  className?: string;
}

export const AccessibleInput: React.FC<AccessibleInputProps> = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  error,
  required = false,
  className = ''
}) => {
  return (
    <div className="mb-4">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
      >
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={`
          w-full px-3 py-2 border rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          ${error ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}
          ${className}
        `}
      />
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
};

// Accessible Select Component
interface AccessibleSelectProps {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  error?: string;
  required?: boolean;
}

export const AccessibleSelect: React.FC<AccessibleSelectProps> = ({
  id,
  label,
  value,
  onChange,
  options,
  error,
  required = false
}) => {
  return (
    <div className="mb-4">
      <label
        htmlFor={id}
        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
      >
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={`
          w-full px-3 py-2 border rounded-md shadow-sm
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
          ${error ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}
        `}
      >
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p id={`${id}-error`} className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
};

// Accessible Checkbox Component
interface AccessibleCheckboxProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  error?: string;
  required?: boolean;
}

export const AccessibleCheckbox: React.FC<AccessibleCheckboxProps> = ({
  id,
  label,
  checked,
  onChange,
  error,
  required = false
}) => {
  return (
    <div className="flex items-start mb-4">
      <div className="flex items-center h-5">
        <input
          id={id}
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          required={required}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
      </div>
      <div className="ml-3 text-sm">
        <label
          htmlFor={id}
          className="font-medium text-gray-700 dark:text-gray-300"
        >
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        {error && (
          <p id={`${id}-error`} className="text-red-600">
            {error}
          </p>
        )}
      </div>
    </div>
  );
};