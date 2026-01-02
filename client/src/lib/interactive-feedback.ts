/**
 * Interactive Feedback System
 * 
 * Centralized utilities for hover, focus, active states, and micro-interactions.
 * Provides consistent interactive feedback across all UI components.
 * 
 * @module interactive-feedback
 * @validates Requirements 1.2 - Interactive feedback for all components
 */

import { transitions } from './design-tokens';

// ============================================================================
// Interactive State Classes
// ============================================================================

/**
 * Base interactive states that can be applied to any interactive element
 */
export const interactiveStates = {
  // Hover states
  hover: {
    subtle: 'hover:bg-white/5 hover:border-white/20',
    medium: 'hover:bg-white/10 hover:border-white/30',
    strong: 'hover:bg-white/15 hover:border-white/40',
    primary: 'hover:bg-primary/10 hover:border-primary/30',
    glow: 'hover:shadow-[0_0_20px_rgba(99,102,241,0.3)]',
  },
  
  // Focus states (accessibility-compliant)
  focus: {
    ring: 'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-background',
    border: 'focus:outline-none focus:border-primary focus:shadow-[0_0_0_3px_rgba(99,102,241,0.2)]',
    glow: 'focus:outline-none focus:shadow-[0_0_15px_rgba(99,102,241,0.4)]',
    visible: 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2',
  },
  
  // Active/pressed states
  active: {
    scale: 'active:scale-[0.98]',
    opacity: 'active:opacity-80',
    translate: 'active:translate-y-[1px]',
    shadow: 'active:shadow-inner',
    combined: 'active:scale-[0.98] active:opacity-90',
  },
  
  // Disabled states
  disabled: {
    base: 'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
    muted: 'disabled:opacity-40 disabled:grayscale disabled:cursor-not-allowed',
  },
} as const;

// ============================================================================
// Transition Classes
// ============================================================================

/**
 * Transition utilities for smooth state changes
 */
export const transitionClasses = {
  // Duration-based transitions
  fast: 'transition-all duration-150 ease-out',
  normal: 'transition-all duration-200 ease-out',
  slow: 'transition-all duration-300 ease-out',
  slower: 'transition-all duration-500 ease-out',
  
  // Property-specific transitions
  colors: 'transition-colors duration-200 ease-out',
  transform: 'transition-transform duration-200 ease-out',
  opacity: 'transition-opacity duration-200 ease-out',
  shadow: 'transition-shadow duration-200 ease-out',
  
  // Combined transitions
  interactive: 'transition-all duration-200 ease-out',
  hover: 'transition-[background-color,border-color,box-shadow] duration-200 ease-out',
} as const;

// ============================================================================
// Component-Specific Feedback Classes
// ============================================================================

/**
 * Pre-built interactive feedback classes for common components
 */
export const componentFeedback = {
  // Button feedback
  button: {
    default: `
      ${transitionClasses.interactive}
      ${interactiveStates.hover.primary}
      ${interactiveStates.focus.visible}
      ${interactiveStates.active.combined}
      ${interactiveStates.disabled.base}
    `.trim().replace(/\s+/g, ' '),
    
    ghost: `
      ${transitionClasses.interactive}
      ${interactiveStates.hover.subtle}
      ${interactiveStates.focus.visible}
      ${interactiveStates.active.scale}
      ${interactiveStates.disabled.base}
    `.trim().replace(/\s+/g, ' '),
    
    primary: `
      ${transitionClasses.interactive}
      hover:brightness-110 hover:shadow-lg
      ${interactiveStates.focus.glow}
      ${interactiveStates.active.combined}
      ${interactiveStates.disabled.base}
    `.trim().replace(/\s+/g, ' '),
  },
  
  // Input feedback
  input: {
    default: `
      ${transitionClasses.interactive}
      hover:border-white/30
      ${interactiveStates.focus.border}
      ${interactiveStates.disabled.base}
    `.trim().replace(/\s+/g, ' '),
    
    search: `
      ${transitionClasses.interactive}
      hover:bg-white/5 hover:border-white/20
      focus:bg-white/5 focus:border-primary
      ${interactiveStates.disabled.base}
    `.trim().replace(/\s+/g, ' '),
  },
  
  // Card feedback
  card: {
    default: `
      ${transitionClasses.interactive}
      ${interactiveStates.hover.subtle}
    `.trim().replace(/\s+/g, ' '),
    
    interactive: `
      ${transitionClasses.interactive}
      ${interactiveStates.hover.medium}
      hover:shadow-lg hover:-translate-y-0.5
      cursor-pointer
    `.trim().replace(/\s+/g, ' '),
    
    selectable: `
      ${transitionClasses.interactive}
      ${interactiveStates.hover.primary}
      hover:shadow-[0_0_20px_rgba(99,102,241,0.2)]
      cursor-pointer
    `.trim().replace(/\s+/g, ' '),
  },
  
  // Link feedback
  link: {
    default: `
      ${transitionClasses.colors}
      hover:text-primary
      ${interactiveStates.focus.visible}
    `.trim().replace(/\s+/g, ' '),
    
    underline: `
      ${transitionClasses.colors}
      hover:text-primary hover:underline
      ${interactiveStates.focus.visible}
    `.trim().replace(/\s+/g, ' '),
    
    nav: `
      ${transitionClasses.interactive}
      hover:text-white hover:bg-white/5
      ${interactiveStates.focus.visible}
    `.trim().replace(/\s+/g, ' '),
  },
  
  // Icon button feedback
  iconButton: {
    default: `
      ${transitionClasses.interactive}
      hover:bg-white/10 hover:text-white
      ${interactiveStates.focus.ring}
      ${interactiveStates.active.scale}
      ${interactiveStates.disabled.base}
    `.trim().replace(/\s+/g, ' '),
    
    ghost: `
      ${transitionClasses.interactive}
      hover:bg-white/5
      ${interactiveStates.focus.visible}
      ${interactiveStates.active.opacity}
    `.trim().replace(/\s+/g, ' '),
  },
  
  // Tab feedback
  tab: {
    default: `
      ${transitionClasses.interactive}
      hover:bg-white/5 hover:text-white
      data-[state=active]:bg-primary/10 data-[state=active]:text-primary
      ${interactiveStates.focus.visible}
    `.trim().replace(/\s+/g, ' '),
  },
  
  // Dropdown/Select feedback
  dropdown: {
    default: `
      ${transitionClasses.interactive}
      hover:bg-white/5 hover:border-white/20
      ${interactiveStates.focus.border}
      data-[state=open]:border-primary
    `.trim().replace(/\s+/g, ' '),
    
    trigger: `
      ${transitionClasses.interactive}
      hover:bg-white/5 hover:border-white/20
      ${interactiveStates.focus.border}
      data-[state=open]:border-primary
    `.trim().replace(/\s+/g, ' '),
    
    item: `
      ${transitionClasses.fast}
      hover:bg-white/10 hover:text-white
      focus:bg-white/10 focus:text-white
      cursor-pointer
    `.trim().replace(/\s+/g, ' '),
  },
  
  // Checkbox/Radio feedback
  checkbox: {
    default: `
      ${transitionClasses.interactive}
      hover:border-primary/50
      ${interactiveStates.focus.ring}
      data-[state=checked]:bg-primary data-[state=checked]:border-primary
    `.trim().replace(/\s+/g, ' '),
  },
  
  // Toggle/Switch feedback
  toggle: {
    default: `
      ${transitionClasses.interactive}
      hover:bg-white/20
      ${interactiveStates.focus.ring}
      data-[state=checked]:bg-primary
    `.trim().replace(/\s+/g, ' '),
  },
} as const;

// ============================================================================
// Micro-Interaction Animations
// ============================================================================

/**
 * CSS keyframe animation classes for micro-interactions
 */
export const microInteractions = {
  // Pulse effect for attention
  pulse: 'animate-pulse',
  
  // Bounce effect for success/completion
  bounce: 'animate-bounce',
  
  // Spin for loading
  spin: 'animate-spin',
  
  // Ping for notifications
  ping: 'animate-ping',
  
  // Custom micro-interactions (defined in CSS)
  wiggle: 'animate-wiggle',
  shake: 'animate-shake',
  pop: 'animate-pop',
  slideUp: 'animate-slide-up',
  slideDown: 'animate-slide-down',
  fadeIn: 'animate-fade-in',
  fadeOut: 'animate-fade-out',
  scaleIn: 'animate-scale-in',
  scaleOut: 'animate-scale-out',
} as const;

// ============================================================================
// Ripple Effect Utility
// ============================================================================

/**
 * Creates a ripple effect on click
 * @param event - Mouse event from click
 * @param element - Target element for ripple
 */
export function createRipple(event: React.MouseEvent<HTMLElement>, element: HTMLElement): void {
  const rect = element.getBoundingClientRect();
  const ripple = document.createElement('span');
  const size = Math.max(rect.width, rect.height);
  const x = event.clientX - rect.left - size / 2;
  const y = event.clientY - rect.top - size / 2;
  
  ripple.style.cssText = `
    position: absolute;
    width: ${size}px;
    height: ${size}px;
    left: ${x}px;
    top: ${y}px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    transform: scale(0);
    animation: ripple 0.6s ease-out;
    pointer-events: none;
  `;
  
  element.style.position = 'relative';
  element.style.overflow = 'hidden';
  element.appendChild(ripple);
  
  setTimeout(() => ripple.remove(), 600);
}

// ============================================================================
// Focus Management Utilities
// ============================================================================

/**
 * Manages focus states for keyboard navigation
 */
export const focusManagement = {
  /**
   * Trap focus within an element (for modals, dialogs)
   */
  trapFocus: (container: HTMLElement): (() => void) => {
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;
      
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement?.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement?.focus();
      }
    };
    
    container.addEventListener('keydown', handleKeyDown);
    firstElement?.focus();
    
    return () => container.removeEventListener('keydown', handleKeyDown);
  },
  
  /**
   * Restore focus to previous element
   */
  restoreFocus: (previousElement: HTMLElement | null): void => {
    previousElement?.focus();
  },
};

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Combines multiple feedback classes
 */
export function combineFeedback(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
}

/**
 * Gets feedback classes for a component type
 */
export function getFeedbackClasses(
  component: keyof typeof componentFeedback,
  variant: string = 'default'
): string {
  const componentStyles = componentFeedback[component] as Record<string, string>;
  return componentStyles[variant] || componentStyles['default'] || '';
}

/**
 * Creates a hover effect configuration
 */
export function createHoverEffect(options: {
  scale?: number;
  brightness?: number;
  shadow?: boolean;
  glow?: boolean;
}): string {
  const classes: string[] = [transitionClasses.interactive];
  
  if (options.scale) {
    classes.push(`hover:scale-[${options.scale}]`);
  }
  if (options.brightness) {
    classes.push(`hover:brightness-[${options.brightness}]`);
  }
  if (options.shadow) {
    classes.push('hover:shadow-lg');
  }
  if (options.glow) {
    classes.push(interactiveStates.hover.glow);
  }
  
  return classes.join(' ');
}

// ============================================================================
// CSS Custom Properties for Animations
// ============================================================================

/**
 * CSS to be injected for custom animations
 */
export const customAnimationCSS = `
  @keyframes ripple {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
  
  @keyframes wiggle {
    0%, 100% { transform: rotate(-3deg); }
    50% { transform: rotate(3deg); }
  }
  
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
    20%, 40%, 60%, 80% { transform: translateX(2px); }
  }
  
  @keyframes pop {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
  }
  
  @keyframes slide-up {
    from { transform: translateY(10px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
  
  @keyframes slide-down {
    from { transform: translateY(-10px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
  
  @keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  
  @keyframes fade-out {
    from { opacity: 1; }
    to { opacity: 0; }
  }
  
  @keyframes scale-in {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }
  
  @keyframes scale-out {
    from { transform: scale(1); opacity: 1; }
    to { transform: scale(0.95); opacity: 0; }
  }
  
  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
  
  .animate-wiggle { animation: wiggle 0.3s ease-in-out; }
  .animate-shake { animation: shake 0.5s ease-in-out; }
  .animate-pop { animation: pop 0.3s ease-out; }
  .animate-slide-up { animation: slide-up 0.3s ease-out; }
  .animate-slide-down { animation: slide-down 0.3s ease-out; }
  .animate-fade-in { animation: fade-in 0.2s ease-out; }
  .animate-fade-out { animation: fade-out 0.2s ease-in; }
  .animate-scale-in { animation: scale-in 0.2s ease-out; }
  .animate-scale-out { animation: scale-out 0.2s ease-in; }
  .animate-shimmer { animation: shimmer 2s infinite; }
`;

// ============================================================================
// Type Exports
// ============================================================================

export type InteractiveStates = typeof interactiveStates;
export type TransitionClasses = typeof transitionClasses;
export type ComponentFeedback = typeof componentFeedback;
export type MicroInteractions = typeof microInteractions;

export default {
  interactiveStates,
  transitionClasses,
  componentFeedback,
  microInteractions,
  createRipple,
  focusManagement,
  combineFeedback,
  getFeedbackClasses,
  createHoverEffect,
  customAnimationCSS,
};
