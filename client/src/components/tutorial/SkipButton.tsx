/**
 * Skip Button - Dismissal UI for tutorials
 */

import React from 'react';
import { X, SkipForward } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SkipButtonProps {
  onSkip: () => void;
  onDismiss?: () => void;
  variant?: 'default' | 'minimal' | 'prominent';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  showDismiss?: boolean;
  className?: string;
  text?: string;
}

export function SkipButton({
  onSkip,
  onDismiss,
  variant = 'default',
  size = 'md',
  disabled = false,
  showDismiss = true,
  className,
  text = 'Skip tutorial',
}: SkipButtonProps) {
  const [dismissedCount, setDismissedCount] = React.useState(0);

  const handleSkip = () => {
    setDismissedCount(prev => prev + 1);
    onSkip();
  };

  const handleDismiss = () => {
    setDismissedCount(prev => prev + 1);
    onDismiss?.();
  };

  // Get button size classes
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-1.5 text-sm';
      case 'lg':
        return 'px-5 py-2.5 text-base';
      case 'md':
      default:
        return 'px-4 py-2 text-sm';
    }
  };

  // Get button variant classes
  const getVariantClasses = () => {
    switch (variant) {
      case 'minimal':
        return 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 bg-transparent hover:bg-transparent';
      case 'prominent':
        return 'text-white bg-amber-600 hover:bg-amber-700 border-transparent';
      case 'default':
      default:
        return 'text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 border-gray-300 dark:border-gray-600';
    }
  };

  if (variant === 'minimal') {
    return (
      <button
        onClick={handleSkip}
        disabled={disabled}
        type="button"
        className={cn(
          'flex items-center gap-2 transition-colors rounded',
          getSizeClasses(),
          getVariantClasses(),
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        aria-label={text}
      >
        <SkipForward size={16} />
        <span>{text}</span>
      </button>
    );
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {showDismiss && dismissedCount === 0 && (
        <button
          onClick={handleDismiss}
          disabled={disabled}
          type="button"
          className={cn(
            'flex items-center gap-2 transition-colors rounded border',
            getSizeClasses(),
            'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 bg-transparent hover:bg-transparent border-transparent hover:underline',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
          aria-label="Close tutorial"
        >
          <X size={16} />
          <span className="sr-only">Close</span>
        </button>
      )}

      <button
        onClick={handleSkip}
        disabled={disabled}
        type="button"
        className={cn(
          'flex items-center gap-2 transition-colors rounded border',
          getSizeClasses(),
          getVariantClasses(),
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        aria-label={text}
      >
        {variant === 'prominent' && <SkipForward size={16} />}
        <span>{text}</span>
      </button>
    </div>
  );
}

interface SkipCountBadgeProps {
  dismissedCount: number;
  maxDismissals?: number;
}

export function SkipCountBadge({
  dismissedCount,
  maxDismissals = 3,
}: SkipCountBadgeProps) {
  if (dismissedCount === 0) {
    return null;
  }

  const remaining = maxDismissals - dismissedCount;
  const isWarning = remaining <= 1;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
        isWarning
          ? 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200'
          : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
      )}
      role="status"
      aria-live="polite"
    >
      <span>
        {remaining} tutorial{remaining !== 1 ? 's' : ''} remaining
      </span>
    </div>
  );
}
