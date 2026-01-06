/**
 * Accessibility Utilities
 *
 * Core utilities for managing ARIA attributes, focus management, and accessibility features.
 * These utilities provide the foundation for all accessibility enhancements.
 *
 * @module accessibility-utils
 * @validates Requirements 1.1, 1.5, 2.2, 2.4, 2.5 - ARIA management and utilities
 */

// ============================================================================
// Types
// ============================================================================

export interface ARIAAttributes {
  // Labels and descriptions
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;

  // States and properties
  'aria-expanded'?: boolean;
  'aria-selected'?: boolean;
  'aria-checked'?: boolean | 'mixed';
  'aria-disabled'?: boolean;
  'aria-required'?: boolean;
  'aria-invalid'?: boolean | 'grammar' | 'spelling';
  'aria-hidden'?: boolean;

  // Live regions
  'aria-live'?: 'off' | 'polite' | 'assertive';
  'aria-atomic'?: boolean;
  'aria-relevant'?: 'additions' | 'removals' | 'text' | 'all';

  // Relationships
  'aria-controls'?: string;
  'aria-owns'?: string;
  'aria-flowto'?: string;

  // Roles
  role?: string;

  // Values
  'aria-valuenow'?: number;
  'aria-valuemin'?: number;
  'aria-valuemax'?: number;
  'aria-valuetext'?: string;

  // Modal
  'aria-modal'?: boolean;

  // Other
  tabIndex?: number;
}

export interface FocusableElement {
  element: HTMLElement;
  tabIndex: number;
  isVisible: boolean;
}

// ============================================================================
// ARIA Utilities
// ============================================================================

/**
 * Generates a unique ID for ARIA relationships
 */
export function generateAriaId(prefix: string = 'aria'): string {
  return `${prefix}-${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Creates ARIA attributes object with proper typing
 */
export function createAriaAttributes(
  attributes: Partial<ARIAAttributes>
): ARIAAttributes {
  const result: ARIAAttributes = {};

  Object.entries(attributes).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      (result as any)[key] = value;
    }
  });

  return result;
}

/**
 * Sets ARIA attributes on an element
 */
export function setAriaAttributes(
  element: HTMLElement,
  attributes: ARIAAttributes
): void {
  Object.entries(attributes).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (key === 'tabIndex') {
        (element as any)[key] = value;
      } else {
        element.setAttribute(key, String(value));
      }
    }
  });
}

/**
 * Creates an accessible button with proper ARIA attributes
 */
export function createAccessibleButton(
  text: string,
  onClick: () => void,
  options: {
    ariaLabel?: string;
    ariaDescribedBy?: string;
    disabled?: boolean;
    className?: string;
  } = {}
): HTMLButtonElement {
  const button = document.createElement('button');
  button.textContent = text;
  button.onclick = onClick;

  const ariaAttrs = createAriaAttributes({
    'aria-label': options.ariaLabel,
    'aria-describedby': options.ariaDescribedBy,
    'aria-disabled': options.disabled,
  });

  setAriaAttributes(button, ariaAttrs);

  if (options.className) {
    button.className = options.className;
  }

  if (options.disabled) {
    button.disabled = true;
  }

  return button;
}

/**
 * Creates an accessible input with proper labeling
 */
export function createAccessibleInput(
  type: string,
  labelText: string,
  options: {
    required?: boolean;
    ariaDescribedBy?: string;
    placeholder?: string;
    value?: string;
    id?: string;
  } = {}
): { input: HTMLInputElement; label: HTMLLabelElement } {
  const id = options.id || generateAriaId('input');

  const input = document.createElement('input');
  input.type = type;
  input.id = id;

  const label = document.createElement('label');
  label.textContent = labelText;
  label.htmlFor = id;

  const ariaAttrs = createAriaAttributes({
    'aria-required': options.required,
    'aria-describedby': options.ariaDescribedBy,
  });

  setAriaAttributes(input, ariaAttrs);

  if (options.placeholder) input.placeholder = options.placeholder;
  if (options.value) input.value = options.value;
  if (options.required) input.required = true;

  return { input, label };
}

// ============================================================================
// Focus Management
// ============================================================================

/**
 * Gets all focusable elements within a container
 */
export function getFocusableElements(
  container: HTMLElement
): FocusableElement[] {
  const focusableSelectors = [
    'button:not([disabled])',
    '[href]',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
  ].join(', ');

  const elements = Array.from(
    container.querySelectorAll(focusableSelectors)
  ) as HTMLElement[];

  return elements
    .map(element => ({
      element,
      tabIndex: element.tabIndex,
      isVisible: isElementVisible(element),
    }))
    .filter(item => item.isVisible)
    .sort((a, b) => {
      // Sort by tab index, then by DOM order
      if (a.tabIndex !== b.tabIndex) {
        if (a.tabIndex === 0) return 1;
        if (b.tabIndex === 0) return -1;
        return a.tabIndex - b.tabIndex;
      }
      return 0;
    });
}

/**
 * Checks if an element is visible and focusable
 */
export function isElementVisible(element: HTMLElement): boolean {
  const style = window.getComputedStyle(element);
  // In JSDOM offsetWidth/offsetHeight are not reliable, so rely on computed styles and absence of 'hidden' attribute
  const hasHiddenAttr = element.hasAttribute('hidden');
  return (
    !hasHiddenAttr &&
    style.display !== 'none' &&
    style.visibility !== 'hidden' &&
    style.opacity !== '0'
  );
}

/**
 * Moves focus to the next focusable element
 */
export function focusNext(container: HTMLElement = document.body): boolean {
  const focusableElements = getFocusableElements(container);
  const currentIndex = focusableElements.findIndex(
    item => item.element === document.activeElement
  );

  const nextIndex = currentIndex + 1;
  if (nextIndex < focusableElements.length) {
    focusableElements[nextIndex].element.focus();
    return true;
  }

  return false;
}

/**
 * Moves focus to the previous focusable element
 */
export function focusPrevious(container: HTMLElement = document.body): boolean {
  const focusableElements = getFocusableElements(container);
  const currentIndex = focusableElements.findIndex(
    item => item.element === document.activeElement
  );

  const prevIndex = currentIndex - 1;
  if (prevIndex >= 0) {
    focusableElements[prevIndex].element.focus();
    return true;
  }

  return false;
}

/**
 * Traps focus within a container
 */
export function trapFocus(container: HTMLElement): () => void {
  const focusableElements = getFocusableElements(container);

  if (focusableElements.length === 0) {
    return () => {};
  }

  const firstElement = focusableElements[0].element;
  const lastElement = focusableElements[focusableElements.length - 1].element;
  const previousActiveElement = document.activeElement as HTMLElement;

  // Focus the first element
  firstElement.focus();

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  };

  container.addEventListener('keydown', handleKeyDown);

  // Return cleanup function
  return () => {
    container.removeEventListener('keydown', handleKeyDown);
    if (
      previousActiveElement &&
      typeof previousActiveElement.focus === 'function'
    ) {
      previousActiveElement.focus();
    }
  };
}

// ============================================================================
// Live Region Management
// ============================================================================

/**
 * Creates or updates an ARIA live region
 */
export function createLiveRegion(
  id: string,
  priority: 'polite' | 'assertive' = 'polite'
): HTMLElement {
  let liveRegion = document.getElementById(id);

  if (!liveRegion) {
    liveRegion = document.createElement('div');
    liveRegion.id = id;
    liveRegion.className = 'sr-only';
    document.body.appendChild(liveRegion);
  }

  liveRegion.setAttribute('aria-live', priority);
  liveRegion.setAttribute('aria-atomic', 'true');

  return liveRegion;
}

/**
 * Announces a message to screen readers
 */
export function announceToScreenReader(
  message: string,
  priority: 'polite' | 'assertive' = 'polite',
  regionId: string = 'accessibility-announcements'
): void {
  const liveRegion = createLiveRegion(regionId, priority);

  // Clear previous content
  liveRegion.textContent = '';

  // Use setTimeout to ensure the change is detected
  setTimeout(() => {
    liveRegion.textContent = message;
  }, 100);

  // Clear after announcement
  setTimeout(() => {
    liveRegion.textContent = '';
  }, 1000);
}

// ============================================================================
// Color Contrast Utilities
// ============================================================================

/**
 * Calculates the contrast ratio between two colors
 */
export function calculateContrastRatio(color1: string, color2: string): number {
  const luminance1 = getRelativeLuminance(color1);
  const luminance2 = getRelativeLuminance(color2);

  const lighter = Math.max(luminance1, luminance2);
  const darker = Math.min(luminance1, luminance2);

  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Gets the relative luminance of a color
 */
function getRelativeLuminance(color: string): number {
  const rgb = hexToRgb(color);
  if (!rgb) return 0;

  const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });

  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/**
 * Converts hex color to RGB
 */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

/**
 * Checks if a color combination meets WCAG contrast requirements
 */
export function meetsContrastRequirement(
  foreground: string,
  background: string,
  level: 'AA' | 'AAA' = 'AA',
  isLargeText: boolean = false
): boolean {
  const ratio = calculateContrastRatio(foreground, background);

  if (level === 'AAA') {
    return isLargeText ? ratio >= 4.5 : ratio >= 7;
  }

  // AA level
  return isLargeText ? ratio >= 3 : ratio >= 4.5;
}

// ============================================================================
// Keyboard Navigation Utilities
// ============================================================================

/**
 * Standard keyboard event handlers
 */
export const keyboardHandlers = {
  /**
   * Handles Enter and Space key activation
   */
  activateOnEnterOrSpace: (callback: () => void) => (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      callback();
    }
  },

  /**
   * Handles Escape key
   */
  closeOnEscape: (callback: () => void) => (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      callback();
    }
  },

  /**
   * Handles arrow key navigation
   */
  arrowNavigation:
    (
      onUp: () => void,
      onDown: () => void,
      onLeft?: () => void,
      onRight?: () => void
    ) =>
    (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault();
          onUp();
          break;
        case 'ArrowDown':
          e.preventDefault();
          onDown();
          break;
        case 'ArrowLeft':
          if (onLeft) {
            e.preventDefault();
            onLeft();
          }
          break;
        case 'ArrowRight':
          if (onRight) {
            e.preventDefault();
            onRight();
          }
          break;
      }
    },
};

// ============================================================================
// Skip Links Utilities
// ============================================================================

/**
 * Creates a skip link element
 */
export function createSkipLink(
  text: string,
  targetId: string,
  className: string = 'skip-link'
): HTMLAnchorElement {
  const skipLink = document.createElement('a');
  skipLink.href = `#${targetId}`;
  skipLink.textContent = text;
  skipLink.className = className;

  skipLink.addEventListener('click', e => {
    e.preventDefault();
    const target = document.getElementById(targetId);
    if (target) {
      target.focus();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });

  return skipLink;
}

// ============================================================================
// Validation Utilities
// ============================================================================

/**
 * Validates that an element has proper accessibility attributes
 */
export function validateAccessibility(element: HTMLElement): {
  isValid: boolean;
  errors: string[];
  warnings: string[];
} {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Check for interactive elements without labels
  const interactiveElements = ['button', 'input', 'select', 'textarea'];
  if (interactiveElements.includes(element.tagName.toLowerCase())) {
    const hasLabel =
      element.getAttribute('aria-label') ||
      element.getAttribute('aria-labelledby') ||
      (element.tagName.toLowerCase() === 'input' &&
        document.querySelector(`label[for="${element.id}"]`));

    if (!hasLabel) {
      errors.push('Interactive element missing accessible label');
    }
  }

  // Check for images without alt text
  if (element.tagName.toLowerCase() === 'img') {
    const hasAlt = element.hasAttribute('alt');
    if (!hasAlt) {
      errors.push('Image missing alt attribute');
    }
  }

  // Check for proper heading hierarchy
  if (element.tagName.match(/^H[1-6]$/)) {
    const level = parseInt(element.tagName.charAt(1));
    const prevHeading = element.previousElementSibling;
    if (prevHeading && prevHeading.tagName.match(/^H[1-6]$/)) {
      const prevLevel = parseInt(prevHeading.tagName.charAt(1));
      if (level > prevLevel + 1) {
        warnings.push(
          'Heading level skipped - may confuse screen reader users'
        );
      }
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
  };
}

export default {
  generateAriaId,
  createAriaAttributes,
  setAriaAttributes,
  createAccessibleButton,
  createAccessibleInput,
  getFocusableElements,
  isElementVisible,
  focusNext,
  focusPrevious,
  trapFocus,
  createLiveRegion,
  announceToScreenReader,
  calculateContrastRatio,
  meetsContrastRequirement,
  keyboardHandlers,
  createSkipLink,
  validateAccessibility,
};
