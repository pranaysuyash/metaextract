/**
 * Tutorial Overlay - Spotlight overlay for tutorials
 */

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ArrowRight, ArrowLeft, Pause, Play, RotateCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import type { OnboardingStep } from '@/lib/onboarding/onboarding-engine';

interface TutorialOverlayProps {
  step: OnboardingStep | null;
  stepIndex: number;
  totalSteps: number;
  isPaused: boolean;
  onComplete: () => void;
  onSkip: () => void;
  onNext: () => void;
  onPrevious: () => void;
  onPause: () => void;
  onResume: () => void;
  onRestart: () => void;
  onDismiss: () => void;
  isLoading?: boolean;
}

export function TutorialOverlay({
  step,
  stepIndex,
  totalSteps,
  isPaused,
  onComplete,
  onSkip,
  onNext,
  onPrevious,
  onPause,
  onResume,
  onRestart,
  onDismiss,
  isLoading = false,
}: TutorialOverlayProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const spotlightRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!step?.target) {
      setTargetRect(null);
      return;
    }

    const targetElement = document.querySelector(step.target);
    if (targetElement) {
      const rect = targetElement.getBoundingClientRect();
      setTargetRect(rect);

      // Scroll element into view
      targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'center',
      });

      // Highlight element
      targetElement.classList.add('tutorial-highlight');
      return () => {
        targetElement.classList.remove('tutorial-highlight');
      };
    } else {
      setTargetRect(null);
    }
  }, [step?.target]);

  if (!step) {
    return null;
  }

  const isCentered = step.position === 'center';
  const showSkip = step.skippable;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
        className="fixed inset-0 z-[9999] pointer-events-none"
      >
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={onDismiss}
        />

        {/* Spotlight */}
        {!isCentered && targetRect && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="absolute"
            style={{
              left: targetRect.left - 8,
              top: targetRect.top - 8,
              width: targetRect.width + 16,
              height: targetRect.height + 16,
              borderRadius: '12px',
              boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.6)',
            }}
          >
            <div className="absolute inset-0 border-2 border-blue-500 rounded-lg animate-pulse" />
          </motion.div>
        )}

        {/* Tooltip Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className={cn(
            'absolute max-w-md bg-white dark:bg-gray-900 rounded-xl shadow-2xl pointer-events-auto',
            'p-6 border border-gray-200 dark:border-gray-700',
            isCentered
              ? 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'
              : '',
            !isCentered &&
              targetRect &&
              step.position &&
              getTooltipPosition(step.position, targetRect)
          )}
          ref={spotlightRef}
        >
          {/* Close button */}
          <button
            onClick={onDismiss}
            type="button"
            className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label="Close tutorial"
          >
            <X size={20} />
          </button>

          {/* Step indicator */}
          <div className="flex items-center gap-2 mb-4">
            <div className="h-1.5 flex-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${((stepIndex + 1) / totalSteps) * 100}%` }}
                transition={{ duration: 0.5 }}
                className="h-full bg-blue-500"
              />
            </div>
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {stepIndex + 1} / {totalSteps}
            </span>
          </div>

          {/* Content */}
          <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">
            {step.title}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
            {step.description}
          </p>

          {/* Actions */}
          <div className="flex items-center justify-between gap-3">
            <div className="flex gap-2">
              {stepIndex > 0 && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onPrevious}
                  disabled={isLoading}
                >
                  <ArrowLeft size={16} className="mr-2" />
                  Back
                </Button>
              )}

              {showSkip && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onSkip}
                  disabled={isLoading}
                >
                  Skip
                </Button>
              )}
            </div>

            <div className="flex gap-2">
              {isPaused ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onResume}
                  disabled={isLoading}
                >
                  <Play size={16} className="mr-2" />
                  Resume
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onPause}
                  disabled={isLoading}
                >
                  <Pause size={16} className="mr-2" />
                  Pause
                </Button>
              )}

              <Button onClick={onNext} disabled={isLoading}>
                {stepIndex === totalSteps - 1 ? 'Finish' : 'Next'}
                {stepIndex < totalSteps - 1 && (
                  <ArrowRight size={16} className="ml-2" />
                )}
              </Button>
            </div>
          </div>

          {/* Restart button (only for multi-step tutorials) */}
          {totalSteps > 3 && stepIndex > 0 && (
            <button
              onClick={onRestart}
              type="button"
              className="mt-4 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 flex items-center gap-1"
            >
              <RotateCcw size={14} />
              Restart tutorial
            </button>
          )}
        </motion.div>
      </motion.div>

      {/* Global styles for highlighting */}
      <style>{`
        .tutorial-highlight {
          animation: tutorialPulse 2s ease-in-out infinite;
        }

        @keyframes tutorialPulse {
          0%, 100% {
            box-shadow: 0 0 0 0px rgba(59, 130, 246, 0.5);
          }
          50% {
            box-shadow: 0 0 0 8px rgba(59, 130, 246, 0);
          }
        }

        * {
          outline: none !important;
        }

        .tutorial-highlight:focus {
          outline: 2px solid #3b82f6 !important;
          outline-offset: 2px;
        }
      `}</style>
    </AnimatePresence>
  );
}

function getTooltipPosition(position: string, targetRect: DOMRect): string {
  const offset = 16;

  switch (position) {
    case 'top':
      return `top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2`;
    case 'bottom':
      return `top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2`;
    case 'left':
      return `top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2`;
    case 'right':
      return `top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2`;
    default:
      return 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2';
  }
}
