/**
 * Error Display Components
 *
 * React components for displaying user-friendly errors with
 * progressive disclosure, actionable suggestions, and retry functionality.
 *
 * @module error-display
 * @validates Requirements 1.4, 3.4 - User-friendly error messaging
 */

import React, { useState, useCallback } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  Info,
  XCircle,
  AlertOctagon,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ExternalLink,
  X,
  CheckCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  UserFriendlyError,
  ErrorSeverity,
  shouldRetry,
} from '@/lib/error-messages';

// ============================================================================
// Icon Components
// ============================================================================

const severityIcons: Record<
  ErrorSeverity,
  React.ComponentType<{ className?: string }>
> = {
  info: Info,
  warning: AlertTriangle,
  error: XCircle,
  critical: AlertOctagon,
};

const severityColors: Record<
  ErrorSeverity,
  { bg: string; border: string; text: string; icon: string }
> = {
  info: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
    text: 'text-blue-400',
    icon: 'text-blue-500',
  },
  warning: {
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/20',
    text: 'text-yellow-400',
    icon: 'text-yellow-500',
  },
  error: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/20',
    text: 'text-red-400',
    icon: 'text-red-500',
  },
  critical: {
    bg: 'bg-red-600/10',
    border: 'border-red-600/20',
    text: 'text-red-300',
    icon: 'text-red-600',
  },
};

// ============================================================================
// Error Alert Component
// ============================================================================

interface ErrorAlertProps {
  error: UserFriendlyError;
  onDismiss?: () => void;
  onRetry?: () => void;
  showSuggestions?: boolean;
  showTechnicalDetails?: boolean;
  className?: string;
}

export function ErrorAlert({
  error,
  onDismiss,
  onRetry,
  showSuggestions = true,
  showTechnicalDetails = false,
  className,
}: ErrorAlertProps) {
  const [expanded, setExpanded] = useState(false);
  const [retrying, setRetrying] = useState(false);
  const [retryAttempt, setRetryAttempt] = useState(0);

  const Icon = severityIcons[error.severity];
  const colors = severityColors[error.severity];

  const handleRetry = useCallback(async () => {
    if (!onRetry || !error.recoverable) return;

    setRetrying(true);
    setRetryAttempt(prev => prev + 1);

    try {
      await onRetry();
    } finally {
      setRetrying(false);
    }
  }, [onRetry, error.recoverable]);

  const canRetry =
    error.recoverable && onRetry && shouldRetry(error, retryAttempt);

  return (
    <div
      className={cn(
        'rounded-lg border p-4',
        colors.bg,
        colors.border,
        className
      )}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <Icon className={cn('w-5 h-5 mt-0.5 flex-shrink-0', colors.icon)} />

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-medium text-white">{error.title}</h3>
              <p className={cn('text-sm mt-1', colors.text)}>{error.message}</p>
            </div>

            {onDismiss && (
              <button
                onClick={onDismiss}
                className="text-slate-300 hover:text-white transition-colors"
                aria-label="Dismiss error"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Suggestions */}
          {showSuggestions && error.suggestions.length > 0 && (
            <div className="mt-3">
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1 text-sm text-slate-300 hover:text-white transition-colors"
              >
                {expanded ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
                {expanded ? 'Hide suggestions' : 'Show suggestions'}
              </button>

              {expanded && (
                <ul className="mt-2 space-y-1.5">
                  {error.suggestions.map((suggestion, index) => (
                    <li
                      key={index}
                      className="flex items-start gap-2 text-sm text-slate-200"
                    >
                      <CheckCircle className="w-4 h-4 mt-0.5 text-slate-500 shrink-0" />
                      {suggestion}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Technical Details (for debugging) */}
          {showTechnicalDetails && error.technicalDetails && (
            <details className="mt-3">
              <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-300">
                Technical details
              </summary>
              <pre className="mt-2 text-xs text-slate-500 bg-black/20 rounded p-2 overflow-x-auto">
                {error.technicalDetails}
              </pre>
            </details>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 mt-4">
            {canRetry && (
              <Button
                size="sm"
                variant="outline"
                onClick={handleRetry}
                disabled={retrying}
                className="border-white/10 hover:bg-white/5"
              >
                <RefreshCw
                  className={cn('w-4 h-4 mr-2', retrying && 'animate-spin')}
                />
                {retrying ? 'Retrying...' : 'Try again'}
              </Button>
            )}

            {error.helpLink && (
              <Button
                size="sm"
                variant="ghost"
                asChild
                className="text-slate-300 hover:text-white"
              >
                <a
                  href={error.helpLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Learn more
                </a>
              </Button>
            )}
          </div>

          {/* Error code for support */}
          <p className="mt-3 text-xs text-slate-600">
            Error code: {error.code}
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Inline Error Component (for form fields)
// ============================================================================

interface InlineErrorProps {
  message: string;
  className?: string;
}

export function InlineError({ message, className }: InlineErrorProps) {
  return (
    <p
      className={cn(
        'text-sm text-red-400 mt-1 flex items-center gap-1',
        className
      )}
      role="alert"
    >
      <AlertCircle className="w-3.5 h-3.5" />
      {message}
    </p>
  );
}

// ============================================================================
// Toast Error Component
// ============================================================================

interface ErrorToastProps {
  error: UserFriendlyError;
  onDismiss: () => void;
  autoHideDuration?: number;
}

export function ErrorToast({
  error,
  onDismiss,
  autoHideDuration = 5000,
}: ErrorToastProps) {
  const Icon = severityIcons[error.severity];
  const colors = severityColors[error.severity];

  React.useEffect(() => {
    if (autoHideDuration > 0) {
      const timer = setTimeout(onDismiss, autoHideDuration);
      return () => clearTimeout(timer);
    }
  }, [autoHideDuration, onDismiss]);

  return (
    <div
      className={cn(
        'fixed bottom-4 right-4 max-w-sm rounded-lg border p-4 shadow-lg',
        'animate-in slide-in-from-bottom-5 fade-in duration-300',
        colors.bg,
        colors.border
      )}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <Icon className={cn('w-5 h-5 shrink-0', colors.icon)} />
        <div className="flex-1">
          <p className="font-medium text-white">{error.title}</p>
          <p className={cn('text-sm mt-1', colors.text)}>{error.message}</p>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="text-slate-300 hover:text-white transition-colors"
          aria-label="Dismiss error"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// Full Page Error Component
// ============================================================================

interface FullPageErrorProps {
  error: UserFriendlyError;
  onRetry?: () => void;
  onGoBack?: () => void;
  onGoHome?: () => void;
}

export function FullPageError({
  error,
  onRetry,
  onGoBack,
  onGoHome,
}: FullPageErrorProps) {
  const Icon = severityIcons[error.severity];
  const colors = severityColors[error.severity];

  return (
    <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        <div
          className={cn(
            'w-16 h-16 rounded-full mx-auto flex items-center justify-center',
            colors.bg
          )}
        >
          <Icon className={cn('w-8 h-8', colors.icon)} />
        </div>

        <h1 className="mt-6 text-2xl font-bold text-white">{error.title}</h1>
        <p className="mt-2 text-slate-300">{error.message}</p>

        {error.suggestions.length > 0 && (
          <ul className="mt-6 space-y-2 text-left">
            {error.suggestions.map((suggestion, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm text-slate-200"
              >
                <CheckCircle className="w-4 h-4 mt-0.5 text-slate-500 shrink-0" />
                {suggestion}
              </li>
            ))}
          </ul>
        )}

        <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
          {onRetry && error.recoverable && (
            <Button
              onClick={onRetry}
              className="bg-primary hover:bg-primary/90 text-black"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try again
            </Button>
          )}
          {onGoBack && (
            <Button
              variant="outline"
              onClick={onGoBack}
              className="border-white/10"
            >
              Go back
            </Button>
          )}
          {onGoHome && (
            <Button
              variant="ghost"
              onClick={onGoHome}
              className="text-slate-300"
            >
              Go to homepage
            </Button>
          )}
        </div>

        <p className="mt-8 text-xs text-slate-600">Error code: {error.code}</p>
      </div>
    </div>
  );
}

// ============================================================================
// Error Context and Hook
// ============================================================================

interface ErrorContextValue {
  errors: UserFriendlyError[];
  addError: (error: UserFriendlyError) => void;
  removeError: (code: string) => void;
  clearErrors: () => void;
}

const ErrorContext = React.createContext<ErrorContextValue | null>(null);

export function ErrorProvider({ children }: { children: React.ReactNode }) {
  const [errors, setErrors] = useState<UserFriendlyError[]>([]);

  const addError = useCallback((error: UserFriendlyError) => {
    setErrors(prev => {
      // Prevent duplicate errors
      if (prev.some(e => e.code === error.code)) {
        return prev;
      }
      return [...prev, error];
    });
  }, []);

  const removeError = useCallback((code: string) => {
    setErrors(prev => prev.filter(e => e.code !== code));
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  return (
    <ErrorContext.Provider
      value={{ errors, addError, removeError, clearErrors }}
    >
      {children}
      {/* Render error toasts */}
      <div className="fixed bottom-4 right-4 space-y-2 z-50">
        {errors.map(error => (
          <ErrorToast
            key={error.code}
            error={error}
            onDismiss={() => removeError(error.code)}
          />
        ))}
      </div>
    </ErrorContext.Provider>
  );
}

export function useErrors() {
  const context = React.useContext(ErrorContext);
  if (!context) {
    throw new Error('useErrors must be used within an ErrorProvider');
  }
  return context;
}

// ============================================================================
// Export All
// ============================================================================

export { severityIcons, severityColors };
