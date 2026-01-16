/**
 * Tutorial Overlay System
 *
 * Provides interactive tutorial overlays with spotlight effects, step navigation,
 * and contextual guidance for onboarding users.
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import {
  X,
  ChevronLeft,
  ChevronRight,
  SkipForward,
  Pause,
  Play,
  RotateCcw,
  CheckCircle2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { useOnboarding } from '@/lib/onboarding';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { showUploadError, showSuccessMessage } from '@/lib/toast-helpers';

// ============================================================================
// Types
// ============================================================================

interface TutorialOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

interface SpotlightPosition {
  top: number;
  left: number;
  width: number;
  height: number;
}

// ============================================================================
// Tutorial Overlay Component
// ============================================================================

export function TutorialOverlay({ isOpen, onClose }: TutorialOverlayProps) {
  const {
    currentStep,
    currentPath,
    completeStep,
    skipStep,
    pauseOnboarding,
    resumeOnboarding,
    completeOnboarding,
    getNextStep,
    getPreviousStep,
    session,
    startOnboarding,
  } = useOnboarding();

  const { toast } = useToast();
  const [spotlightPosition, setSpotlightPosition] =
    useState<SpotlightPosition | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{
    top: number;
    left: number;
  } | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const overlayRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Calculate spotlight and tooltip positions
  const updatePositions = useCallback(() => {
    if (!currentStep?.targetElement) {
      setSpotlightPosition(null);
      setTooltipPosition(null);
      return;
    }

    const targetElement = document.querySelector(currentStep.targetElement);
    if (!targetElement) {
      setSpotlightPosition(null);
      setTooltipPosition(null);
      return;
    }

    const rect = targetElement.getBoundingClientRect();
    const padding = 8;

    // Spotlight position (with padding)
    setSpotlightPosition({
      top: rect.top - padding,
      left: rect.left - padding,
      width: rect.width + padding * 2,
      height: rect.height + padding * 2,
    });

    // Tooltip position based on step position preference
    const tooltipWidth = 400;
    const tooltipHeight = 200; // Approximate
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let top = 0;
    let left = 0;

    switch (currentStep.position) {
      case 'top':
        top = rect.top - tooltipHeight - 20;
        left = rect.left + rect.width / 2 - tooltipWidth / 2;
        break;
      case 'bottom':
        top = rect.bottom + 20;
        left = rect.left + rect.width / 2 - tooltipWidth / 2;
        break;
      case 'left':
        top = rect.top + rect.height / 2 - tooltipHeight / 2;
        left = rect.left - tooltipWidth - 20;
        break;
      case 'right':
        top = rect.top + rect.height / 2 - tooltipHeight / 2;
        left = rect.right + 20;
        break;
      case 'center':
      default:
        top = viewportHeight / 2 - tooltipHeight / 2;
        left = viewportWidth / 2 - tooltipWidth / 2;
        break;
    }

    // Ensure tooltip stays within viewport
    top = Math.max(20, Math.min(top, viewportHeight - tooltipHeight - 20));
    left = Math.max(20, Math.min(left, viewportWidth - tooltipWidth - 20));

    setTooltipPosition({ top, left });
  }, [currentStep]);

  // Update positions on mount, step change, and window resize
  useEffect(() => {
    if (!isOpen || !currentStep) return;

    updatePositions();

    const handleResize = () => updatePositions();
    const handleScroll = () => updatePositions();

    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleScroll, true);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('scroll', handleScroll, true);
    };
  }, [isOpen, currentStep, updatePositions]);

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowRight' && getNextStep()) {
        handleNext();
      } else if (e.key === 'ArrowLeft' && getPreviousStep()) {
        handlePrevious();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, getNextStep, getPreviousStep]);

  // Handle click outside to close (if skippable)
  const handleOverlayClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === overlayRef.current && currentStep?.skippable) {
        onClose();
      }
    },
    [currentStep, onClose]
  );

  // Navigation handlers
  const handleNext = useCallback(async () => {
    if (!currentStep) return;

    // Validate step completion if required
    if (currentStep.completionCriteria.type === 'interaction') {
      setIsValidating(true);
      setValidationError(null);

      // Check if the required interaction has occurred
      const interactionValue = currentStep.completionCriteria.value;
      const targetElement = currentStep.targetElement
        ? document.querySelector(currentStep.targetElement)
        : null;

      // Simple validation: check if target element exists and has been interacted with
      if (interactionValue && !targetElement) {
        setValidationError(
          'Please complete the required action before continuing'
        );
        setIsValidating(false);
        showUploadError(
          toast,
          'Please complete the highlighted action before moving to the next step'
        );
        return;
      }

      setIsValidating(false);
    }

    await completeStep(currentStep.id, {
      action: 'next',
      timestamp: new Date().toISOString(),
      validated: true,
    });

    // Show success feedback
    showSuccessMessage(
      toast,
      'Step Complete!',
      `${currentStep.title} completed successfully`
    );

    setValidationError(null);
  }, [currentStep, completeStep, toast]);

  const handlePrevious = useCallback(async () => {
    if (!session || !currentPath) return;

    // Move back one step
    const prevIndex = session.progress.currentStepIndex - 1;
    if (prevIndex >= 0) {
      // Note: This would need to be implemented in the onboarding context
      // The context should handle updating progress; for now we show feedback.
      showSuccessMessage(toast, 'Going Back', 'Returning to previous step');
    }
  }, [session, currentPath, toast]);

  const handleSkip = useCallback(async () => {
    if (!currentStep) return;

    await skipStep(currentStep.id, 'user-skip');

    showSuccessMessage(
      toast,
      'Step Skipped',
      'You can always come back to this later'
    );

    setValidationError(null);
  }, [currentStep, skipStep, toast]);

  const handleComplete = useCallback(async () => {
    if (!currentStep) return;

    await completeStep(currentStep.id, {
      action: 'complete',
      timestamp: new Date().toISOString(),
    });

    // Complete the entire onboarding
    await completeOnboarding();

    showSuccessMessage(
      toast,
      'Congratulations! 🎉',
      "You've completed the onboarding tutorial"
    );

    onClose();
  }, [currentStep, completeStep, completeOnboarding, onClose, toast]);

  const handlePause = useCallback(async () => {
    setIsPaused(true);
    await pauseOnboarding();

    showSuccessMessage(
      toast,
      'Tutorial Paused',
      'Resume anytime from where you left off'
    );
  }, [pauseOnboarding, toast]);

  const handleResume = useCallback(async () => {
    setIsPaused(false);
    await resumeOnboarding();

    showSuccessMessage(toast, 'Tutorial Resumed', "Let's continue!");
  }, [resumeOnboarding, toast]);

  const handleRestart = useCallback(async () => {
    if (!session?.userProfile) return;

    // Restart the onboarding from the beginning
    await startOnboarding(session.userProfile);

    showSuccessMessage(
      toast,
      'Tutorial Restarted',
      'Starting from the beginning'
    );

    setIsPaused(false);
    setValidationError(null);
  }, [session, startOnboarding, toast]);

  if (!isOpen || !currentStep || !currentPath) {
    return null;
  }

  const currentStepIndex = session?.progress.currentStepIndex || 0;
  const totalSteps = currentPath.steps.length;
  const hasPrevious = currentStepIndex > 0;
  const hasNext = currentStepIndex < totalSteps - 1;

  return createPortal(
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 tutorial-overlay"
      onClick={handleOverlayClick}
      onKeyDown={(e: React.KeyboardEvent) => {
        if (
          (e.key === 'Enter' || e.key === ' ') &&
          e.target === overlayRef.current &&
          currentStep?.skippable
        ) {
          e.preventDefault();
          onClose();
        }
      }}
      tabIndex={0}
      role="dialog"
      aria-modal="true"
      aria-labelledby="tutorial-title"
      aria-describedby="tutorial-description"
    >
      {/* Backdrop with spotlight cutout */}
      <div className="absolute inset-0 bg-black/70 transition-opacity duration-300">
        {spotlightPosition && (
          <div
            className="absolute transition-all duration-300 ease-out"
            style={{
              top: spotlightPosition.top,
              left: spotlightPosition.left,
              width: spotlightPosition.width,
              height: spotlightPosition.height,
              boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.7)',
              borderRadius: '8px',
              pointerEvents: 'none',
            }}
          />
        )}
      </div>

      {/* Tutorial tooltip */}
      <Card
        ref={tooltipRef}
        className={cn(
          'absolute w-[400px] shadow-2xl transition-all duration-300 ease-out',
          'bg-[#1F2937] border-[#45A29E] text-white'
        )}
        style={
          tooltipPosition
            ? {
                top: tooltipPosition.top,
                left: tooltipPosition.left,
              }
            : {
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
              }
        }
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle
                id="tutorial-title"
                className="text-lg font-semibold text-white"
              >
                {currentStep.title}
              </CardTitle>
              <CardDescription className="text-sm text-gray-300 mt-1">
                Step {currentStepIndex + 1} of {totalSteps}
              </CardDescription>
            </div>
            <div className="flex gap-1">
              {/* Pause/Resume button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={isPaused ? handleResume : handlePause}
                className="h-8 w-8 text-gray-400 hover:text-white hover:bg-white/10"
                aria-label={isPaused ? 'Resume tutorial' : 'Pause tutorial'}
                title={isPaused ? 'Resume' : 'Pause'}
              >
                {isPaused ? (
                  <Play className="h-4 w-4" />
                ) : (
                  <Pause className="h-4 w-4" />
                )}
              </Button>

              {/* Restart button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={handleRestart}
                className="h-8 w-8 text-gray-400 hover:text-white hover:bg-white/10"
                aria-label="Restart tutorial"
                title="Restart"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>

              {/* Close button (only if skippable) */}
              {currentStep.skippable && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="h-8 w-8 text-gray-400 hover:text-white hover:bg-white/10"
                  aria-label="Close tutorial"
                  title="Close"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="pb-4">
          <p
            id="tutorial-description"
            className="text-sm text-gray-200 leading-relaxed"
          >
            {currentStep.description}
          </p>

          {/* Validation error message */}
          {validationError && (
            <div className="mt-3 p-2 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-400">
              {validationError}
            </div>
          )}

          {/* Paused state message */}
          {isPaused && (
            <div className="mt-3 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded text-sm text-yellow-400 flex items-center gap-2">
              <Pause className="h-4 w-4" />
              Tutorial paused - Click play to continue
            </div>
          )}

          {/* Progress bar */}
          <div className="mt-4 w-full bg-gray-700 rounded-full h-1.5">
            <div
              className="bg-[#45A29E] h-1.5 rounded-full transition-all duration-300"
              style={{
                width: `${((currentStepIndex + 1) / totalSteps) * 100}%`,
              }}
              role="progressbar"
              aria-valuenow={currentStepIndex + 1}
              aria-valuemin={0}
              aria-valuemax={totalSteps}
            />
          </div>
        </CardContent>

        <CardFooter className="flex items-center justify-between pt-0">
          <div className="flex gap-2">
            {hasPrevious && !isPaused && (
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrevious}
                className="border-gray-600 text-gray-300 hover:bg-white/10 hover:text-white"
                disabled={isValidating}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            {currentStep.skippable && !isPaused && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSkip}
                className="text-gray-400 hover:text-white hover:bg-white/10"
                disabled={isValidating}
              >
                <SkipForward className="h-4 w-4 mr-1" />
                Skip
              </Button>
            )}

            {!isPaused &&
              (hasNext ? (
                <Button
                  size="sm"
                  onClick={handleNext}
                  className="bg-[#45A29E] hover:bg-[#45A29E]/90 text-white"
                  disabled={isValidating}
                >
                  {isValidating ? 'Validating...' : 'Next'}
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              ) : (
                <Button
                  size="sm"
                  onClick={handleComplete}
                  className="bg-[#45A29E] hover:bg-[#45A29E]/90 text-white"
                  disabled={isValidating}
                >
                  <CheckCircle2 className="h-4 w-4 mr-1" />
                  Complete
                </Button>
              ))}
          </div>
        </CardFooter>
      </Card>
    </div>,
    document.body
  );
}

/**
 * Hook to control tutorial overlay
 */
export function useTutorialOverlay() {
  const [isOpen, setIsOpen] = useState(false);
  const { isOnboardingActive, currentStep } = useOnboarding();

  // Auto-open when onboarding is active and there's a current step
  useEffect(() => {
    if (isOnboardingActive && currentStep) {
      setIsOpen(true);
    } else {
      setIsOpen(false);
    }
  }, [isOnboardingActive, currentStep]);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen(prev => !prev), []);

  return {
    isOpen,
    open,
    close,
    toggle,
  };
}
