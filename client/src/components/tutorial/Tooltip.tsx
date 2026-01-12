/**
 * Tooltip - Contextual tooltip component
 */

import React, { useState, useRef, useEffect } from 'react';
import { Info, AlertCircle, HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';
export type TooltipVariant = 'info' | 'warning' | 'help' | 'custom';

interface TooltipProps {
  content: React.ReactNode;
  position?: TooltipPosition;
  variant?: TooltipVariant;
  children: React.ReactElement;
  delay?: number;
  trigger?: 'hover' | 'click' | 'focus';
  className?: string;
  maxWidth?: string;
}

export function Tooltip({
  content,
  position = 'top',
  variant = 'info',
  children,
  delay = 200,
  trigger = 'hover',
  className,
  maxWidth = '300px',
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isClicked, setIsClicked] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const handleMouseEnter = () => {
    if (trigger === 'hover') {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => {
        setIsVisible(true);
      }, delay);
    }
  };

  const handleMouseLeave = () => {
    if (trigger === 'hover') {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      setIsVisible(false);
    }
  };

  const handleClick = () => {
    if (trigger === 'click') {
      setIsClicked(!isClicked);
    }
  };

  const handleFocus = () => {
    if (trigger === 'focus') {
      setIsVisible(true);
    }
  };

  const handleBlur = () => {
    if (trigger === 'focus') {
      setIsVisible(false);
    }
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const shouldShow = trigger === 'click' ? isClicked : isVisible;

  const getIcon = () => {
    switch (variant) {
      case 'warning':
        return <AlertCircle size={16} />;
      case 'help':
        return <HelpCircle size={16} />;
      case 'info':
      case 'custom':
      default:
        return <Info size={16} />;
    }
  };

  const getPositionClasses = () => {
    const baseClasses = 'absolute z-50';
    switch (position) {
      case 'top':
        return `${baseClasses} bottom-full left-1/2 -translate-x-1/2 mb-2`;
      case 'bottom':
        return `${baseClasses} top-full left-1/2 -translate-x-1/2 mt-2`;
      case 'left':
        return `${baseClasses} right-full top-1/2 -translate-y-1/2 mr-2`;
      case 'right':
        return `${baseClasses} left-full top-1/2 -translate-y-1/2 ml-2`;
    }
  };

  const getArrowClasses = () => {
    switch (position) {
      case 'top':
        return 'absolute -bottom-1 left-1/2 -translate-x-1/2 border-l border-r border-t border-gray-900 border-b-transparent transform rotate-45 w-2 h-2';
      case 'bottom':
        return 'absolute -top-1 left-1/2 -translate-x-1/2 border-l border-r border-b border-gray-900 border-t-transparent transform rotate-45 w-2 h-2';
      case 'left':
        return 'absolute -right-1 top-1/2 -translate-y-1/2 border-t border-b border-l border-gray-900 border-r-transparent transform rotate-45 w-2 h-2';
      case 'right':
        return 'absolute -left-1 top-1/2 -translate-y-1/2 border-t border-b border-r border-gray-900 border-l-transparent transform rotate-45 w-2 h-2';
    }
  };

  return (
    <div className={cn('relative inline-flex', className)}>
      {/* Trigger */}
      <div
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        onFocus={handleFocus}
        onBlur={handleBlur}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleClick(); } }}
        className="inline-flex items-center"
      >
        {children}
      </div>

      {/* Tooltip */}
      {shouldShow && (
        <div
          ref={tooltipRef}
          className={cn(
            getPositionClasses(),
            'bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg',
            'text-sm leading-relaxed',
            'animate-in fade-in zoom-in duration-200'
          )}
          style={{ maxWidth }}
          role="tooltip"
          aria-live="polite"
        >
          {/* Icon */}
          <div className="flex items-start gap-2">
            <span className="mt-0.5 flex-shrink-0 text-blue-400">
              {getIcon()}
            </span>
            <span className="flex-1">{content}</span>
          </div>

          {/* Arrow */}
          <div className={getArrowClasses()} />

          {/* Close button for click-triggered tooltips */}
          {trigger === 'click' && (
            <button
              onClick={() => setIsClicked(false)}
              type="button"
              className="absolute top-1 right-1 text-gray-400 hover:text-white"
              aria-label="Close tooltip"
            >
              <span className="sr-only">Close</span>
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * QuickTooltip - Simplified tooltip for inline help
 */

interface QuickTooltipProps {
  text: string;
  children: React.ReactNode;
  side?: 'top' | 'bottom';
}

export function QuickTooltip({
  text,
  children,
  side = 'top',
}: QuickTooltipProps) {
  return (
    <Tooltip
      content={text}
      position={side}
      variant="help"
      trigger="hover"
      delay={100}
    >
      <span className="inline-flex items-center gap-1 text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 cursor-help">
        {children}
      </span>
    </Tooltip>
  );
}
