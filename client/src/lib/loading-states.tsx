/**
 * Professional Loading States System
 * 
 * Provides comprehensive loading states, skeleton loaders, and progress indicators
 * for a polished user experience during async operations.
 * 
 * @module loading-states
 * @validates Requirements 1.3 - Professional loading states and animations
 */

import React, { useState, useEffect, useCallback } from 'react';
import { cn } from './utils';

// ============================================================================
// Types
// ============================================================================

export interface LoadingStateConfig {
  /** Type of loading indicator */
  type: 'spinner' | 'skeleton' | 'progress' | 'dots' | 'pulse' | 'shimmer';
  /** Size variant */
  size?: 'sm' | 'md' | 'lg' | 'xl';
  /** Optional message to display */
  message?: string;
  /** Progress value (0-100) for progress type */
  progress?: number;
  /** Whether to show estimated time */
  showEstimate?: boolean;
  /** Estimated time in seconds */
  estimatedTime?: number;
}

export interface SkeletonConfig {
  /** Type of content being loaded */
  contentType: 'text' | 'card' | 'list' | 'table' | 'image' | 'avatar' | 'button' | 'input';
  /** Number of items to show */
  count?: number;
  /** Animation style */
  animation?: 'pulse' | 'wave' | 'shimmer' | 'none';
}

// ============================================================================
// Loading Spinner Component
// ============================================================================

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  color?: 'primary' | 'white' | 'muted';
}

export function Spinner({ size = 'md', className, color = 'primary' }: SpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };
  
  const colorClasses = {
    primary: 'text-primary',
    white: 'text-white',
    muted: 'text-muted-foreground',
  };
  
  return (
    <svg
      className={cn(
        'animate-spin',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

// ============================================================================
// Loading Dots Component
// ============================================================================

interface LoadingDotsProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function LoadingDots({ size = 'md', className }: LoadingDotsProps) {
  const sizeClasses = {
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-3 h-3',
  };
  
  return (
    <div className={cn('flex items-center gap-1', className)}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            'rounded-full bg-primary animate-bounce',
            sizeClasses[size]
          )}
          style={{
            animationDelay: `${i * 0.15}s`,
            animationDuration: '0.6s',
          }}
        />
      ))}
    </div>
  );
}

// ============================================================================
// Progress Bar Component
// ============================================================================

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  animated?: boolean;
  className?: string;
}

export function ProgressBar({
  value,
  max = 100,
  size = 'md',
  showLabel = false,
  animated = true,
  className,
}: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };
  
  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'w-full bg-white/10 rounded-full overflow-hidden',
          sizeClasses[size]
        )}
      >
        <div
          className={cn(
            'h-full bg-primary rounded-full transition-all duration-300 ease-out',
            animated && 'relative overflow-hidden'
          )}
          style={{ width: `${percentage}%` }}
        >
          {animated && (
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
          )}
        </div>
      </div>
      {showLabel && (
        <div className="mt-1 text-xs text-muted-foreground text-right">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Skeleton Components
// ============================================================================

interface SkeletonBaseProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
  animation?: 'pulse' | 'wave' | 'shimmer' | 'none';
}

export function SkeletonBase({ className, animation = 'pulse', ...props }: SkeletonBaseProps) {
  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-wave',
    shimmer: 'relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-shimmer before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent',
    none: '',
  };
  
  return (
    <div
      className={cn(
        'bg-white/10 rounded',
        animationClasses[animation],
        className
      )}
      {...props}
    />
  );
}

export function SkeletonText({ lines = 3, animation = 'pulse' }: { lines?: number; animation?: 'pulse' | 'wave' | 'shimmer' | 'none' }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonBase
          key={i}
          animation={animation}
          className={cn(
            'h-4',
            i === lines - 1 ? 'w-3/4' : 'w-full'
          )}
        />
      ))}
    </div>
  );
}

export function SkeletonAvatar({ size = 'md', animation = 'pulse' }: { size?: 'sm' | 'md' | 'lg'; animation?: 'pulse' | 'wave' | 'shimmer' | 'none' }) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };
  
  return (
    <SkeletonBase
      animation={animation}
      className={cn('rounded-full', sizeClasses[size])}
    />
  );
}

export function SkeletonButton({ size = 'md', animation = 'pulse' }: { size?: 'sm' | 'md' | 'lg'; animation?: 'pulse' | 'wave' | 'shimmer' | 'none' }) {
  const sizeClasses = {
    sm: 'h-8 w-20',
    md: 'h-9 w-24',
    lg: 'h-10 w-32',
  };
  
  return (
    <SkeletonBase
      animation={animation}
      className={cn('rounded-md', sizeClasses[size])}
    />
  );
}

export function SkeletonInput({ animation = 'pulse' }: { animation?: 'pulse' | 'wave' | 'shimmer' | 'none' }) {
  return (
    <SkeletonBase
      animation={animation}
      className="h-9 w-full rounded-md"
    />
  );
}

export function SkeletonImage({ aspectRatio = '16/9', animation = 'pulse' }: { aspectRatio?: string; animation?: 'pulse' | 'wave' | 'shimmer' | 'none' }) {
  return (
    <SkeletonBase
      animation={animation}
      className="w-full rounded-lg"
      style={{ aspectRatio }}
    />
  );
}

// ============================================================================
// Loading Overlay Component
// ============================================================================

interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  blur?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function LoadingOverlay({
  isLoading,
  message,
  blur = true,
  children,
  className,
}: LoadingOverlayProps) {
  return (
    <div className={cn('relative', className)}>
      {children}
      {isLoading && (
        <div
          className={cn(
            'absolute inset-0 flex flex-col items-center justify-center bg-background/80 z-50',
            blur && 'backdrop-blur-sm'
          )}
        >
          <Spinner size="lg" />
          {message && (
            <p className="mt-4 text-sm text-muted-foreground animate-pulse">
              {message}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Full Page Loading Component
// ============================================================================

interface FullPageLoadingProps {
  message?: string;
  showProgress?: boolean;
  progress?: number;
}

export function FullPageLoading({
  message = 'Loading...',
  showProgress = false,
  progress = 0,
}: FullPageLoadingProps) {
  return (
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-background z-50">
      <div className="flex flex-col items-center gap-6">
        {/* Logo placeholder */}
        <div className="w-16 h-16 bg-primary/20 rounded-xl flex items-center justify-center animate-pulse">
          <span className="text-2xl font-bold text-primary">M</span>
        </div>
        
        {/* Spinner */}
        <Spinner size="xl" />
        
        {/* Message */}
        <p className="text-muted-foreground animate-pulse">{message}</p>
        
        {/* Progress bar */}
        {showProgress && (
          <div className="w-64">
            <ProgressBar value={progress} showLabel animated />
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================================
// Inline Loading Component
// ============================================================================

interface InlineLoadingProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

export function InlineLoading({ size = 'sm', message, className }: InlineLoadingProps) {
  return (
    <div className={cn('inline-flex items-center gap-2', className)}>
      <Spinner size={size} />
      {message && (
        <span className="text-sm text-muted-foreground">{message}</span>
      )}
    </div>
  );
}

// ============================================================================
// Button Loading State
// ============================================================================

interface ButtonLoadingProps {
  isLoading: boolean;
  loadingText?: string;
  children: React.ReactNode;
}

export function ButtonLoading({ isLoading, loadingText, children }: ButtonLoadingProps) {
  if (isLoading) {
    return (
      <>
        <Spinner size="sm" className="mr-2" />
        {loadingText || 'Loading...'}
      </>
    );
  }
  return <>{children}</>;
}

// ============================================================================
// Estimated Time Display
// ============================================================================

interface EstimatedTimeProps {
  seconds: number;
  className?: string;
}

export function EstimatedTime({ seconds, className }: EstimatedTimeProps) {
  const formatTime = (s: number): string => {
    if (s < 60) return `${s}s`;
    const minutes = Math.floor(s / 60);
    const remainingSeconds = s % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  };
  
  return (
    <span className={cn('text-xs text-muted-foreground', className)}>
      Est. {formatTime(seconds)} remaining
    </span>
  );
}

// ============================================================================
// Hook: useLoadingState
// ============================================================================

interface UseLoadingStateOptions {
  initialLoading?: boolean;
  minDuration?: number;
}

export function useLoadingState(options: UseLoadingStateOptions = {}) {
  const { initialLoading = false, minDuration = 0 } = options;
  const [isLoading, setIsLoading] = useState(initialLoading);
  const [startTime, setStartTime] = useState<number | null>(null);
  
  const startLoading = useCallback(() => {
    setIsLoading(true);
    setStartTime(Date.now());
  }, []);
  
  const stopLoading = useCallback(() => {
    if (minDuration > 0 && startTime) {
      const elapsed = Date.now() - startTime;
      const remaining = minDuration - elapsed;
      
      if (remaining > 0) {
        setTimeout(() => setIsLoading(false), remaining);
      } else {
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
    setStartTime(null);
  }, [minDuration, startTime]);
  
  return { isLoading, startLoading, stopLoading };
}

// ============================================================================
// Hook: useProgressSimulation
// ============================================================================

interface UseProgressSimulationOptions {
  duration?: number;
  onComplete?: () => void;
}

export function useProgressSimulation(options: UseProgressSimulationOptions = {}) {
  const { duration = 3000, onComplete } = options;
  const [progress, setProgress] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  
  const start = useCallback(() => {
    setProgress(0);
    setIsRunning(true);
  }, []);
  
  const stop = useCallback(() => {
    setIsRunning(false);
  }, []);
  
  const complete = useCallback(() => {
    setProgress(100);
    setIsRunning(false);
    onComplete?.();
  }, [onComplete]);
  
  useEffect(() => {
    if (!isRunning) return;
    
    const interval = setInterval(() => {
      setProgress((prev) => {
        // Slow down as we approach 90%
        const increment = prev < 30 ? 5 : prev < 60 ? 3 : prev < 90 ? 1 : 0.5;
        const next = Math.min(95, prev + increment);
        return next;
      });
    }, duration / 20);
    
    return () => clearInterval(interval);
  }, [isRunning, duration]);
  
  return { progress, isRunning, start, stop, complete };
}

// ============================================================================
// Export all loading state utilities
// ============================================================================

export const loadingStates = {
  Spinner,
  LoadingDots,
  ProgressBar,
  SkeletonBase,
  SkeletonText,
  SkeletonAvatar,
  SkeletonButton,
  SkeletonInput,
  SkeletonImage,
  LoadingOverlay,
  FullPageLoading,
  InlineLoading,
  ButtonLoading,
  EstimatedTime,
  useLoadingState,
  useProgressSimulation,
};

export default loadingStates;
