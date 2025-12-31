/**
 * Tutorial Overlay System
 * 
 * Provides interactive tutorial overlays with spotlight effects, step navigation,
 * and contextual guidance for onboarding users.
 */

import React, { useEffect, useState, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X, ChevronLeft, ChevronRight, SkipForward } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useOnboarding, type OnboardingStep } from '@/lib/onboarding';
import { cn } from '@/lib/utils';

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
    getNextStep,
    getPreviousStep,
    session
  } = useOnboarding();

  const [spotlightPosition, setSpotlightPosition] = useState<SpotlightPosition | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{ top: number; left: number } | null>(null);
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
      height: rect.height + padding * 2
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
  const handleOverlayClick = useCallback((e: React.MouseEvent) => {
    if (e.target === overlayRef.current && currentStep?.skippable) {
      onClose();
    }
  }, [currentStep, onClose]);

  // Navigation handlers
  const handleNext = useCallback(async () => {
    if (!currentStep) return;

    await completeStep(currentStep.id, {
      action: 'next',
      timestamp: new Date().toISOString()
    });
  }, [currentStep, completeStep]);

  const handlePrevious = useCallback(() => {
    // Navigate to previous step (implementation depends on requirements)
    console.log('Navigate to previous step');
  }, []);

  const handleSkip = useCallback(async () => {
    if (!currentStep) return;

    await skipStep(currentStep.id, 'user-skip');
  }, [currentStep, skipStep]);

  const handleComplete = useCallback(async () => {
    if (!currentStep) return;

    await completeStep(currentStep.id, {
      action: 'complete',
      timestamp: new Date().toISOString()
    });
  }, [currentStep, completeStep]);

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
              pointerEvents: 'none'
            }}
          />
        )}
      </div>

      {/* Tutorial tooltip */}
      <Card
        ref={tooltipRef}
        className={cn(
          "absolute w-[400px] shadow-2xl transition-all duration-300 ease-out",
          "bg-[#1F2937] border-[#45A29E] text-white"
        )}
        style={tooltipPosition ? {
          top: tooltipPosition.top,
          left: tooltipPosition.left
        } : {
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)'
        }}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle id="tutorial-title" className="text-lg font-semibold text-white">
                {currentStep.title}
              </CardTitle>
              <CardDescription className="text-sm text-gray-300 mt-1">
                Step {currentStepIndex + 1} of {totalSteps}
              </CardDescription>
            </div>
            {currentStep.skippable && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8 text-gray-400 hover:text-white hover:bg-white/10"
                aria-label="Close tutorial"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardHeader>

        <CardContent className="pb-4">
          <p id="tutorial-description" className="text-sm text-gray-200 leading-relaxed">
            {currentStep.description}
          </p>

          {/* Progress bar */}
          <div className="mt-4 w-full bg-gray-700 rounded-full h-1.5">
            <div
              className="bg-[#45A29E] h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${((currentStepIndex + 1) / totalSteps) * 100}%` }}
              role="progressbar"
              aria-valuenow={currentStepIndex + 1}
              aria-valuemin={0}
              aria-valuemax={totalSteps}
            />
          </div>
        </CardContent>

        <CardFooter className="flex items-center justify-between pt-0">
          <div className="flex gap-2">
            {hasPrevious && (
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrevious}
                className="border-gray-600 text-gray-300 hover:bg-white/10 hover:text-white"
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            {currentStep.skippable && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSkip}
                className="text-gray-400 hover:text-white hover:bg-white/10"
              >
                <SkipForward className="h-4 w-4 mr-1" />
                Skip
              </Button>
            )}
            
            {hasNext ? (
              <Button
                size="sm"
                onClick={handleNext}
                className="bg-[#45A29E] hover:bg-[#45A29E]/90 text-white"
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            ) : (
              <Button
                size="sm"
                onClick={handleComplete}
                className="bg-[#45A29E] hover:bg-[#45A29E]/90 text-white"
              >
                Complete
              </Button>
            )}
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
    toggle
  };
}
