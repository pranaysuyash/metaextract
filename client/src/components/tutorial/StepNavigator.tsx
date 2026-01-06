/**
 * Step Navigator - Progress stepper for tutorials
 */

import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StepNavigatorProps {
  steps: Array<{
    id: string;
    title: string;
    completed?: boolean;
    current?: boolean;
  }>;
  currentStep: number;
  onStepClick?: (stepIndex: number) => void;
  className?: string;
}

export function StepNavigator({
  steps,
  currentStep,
  onStepClick,
  className,
}: StepNavigatorProps) {
  return (
    <nav
      className={cn('flex items-center gap-2', className)}
      aria-label="Tutorial steps"
    >
      {steps.map((step, index) => (
        <React.Fragment key={step.id}>
          {/* Step indicator */}
          <button
            onClick={() => onStepClick?.(index)}
            disabled={index > currentStep && !step.completed}
            className={cn(
              'flex items-center justify-center w-10 h-10 rounded-full border-2 font-medium text-sm transition-all',
              step.completed && 'bg-green-500 border-green-500 text-white',
              step.current &&
                'bg-blue-500 border-blue-500 text-white scale-110',
              !step.completed &&
                !step.current &&
                'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400',
              onStepClick &&
                !step.completed &&
                !step.current &&
                'hover:border-blue-500 cursor-pointer'
            )}
            aria-label={step.title}
            aria-current={step.current ? 'step' : undefined}
          >
            {step.completed ? <Check size={16} /> : index + 1}
          </button>

          {/* Connector line */}
          {index < steps.length - 1 && (
            <div
              className={cn(
                'flex-1 h-0.5 min-w-8',
                step.completed && 'bg-green-500',
                !step.completed && 'bg-gray-300 dark:bg-gray-600'
              )}
              aria-hidden="true"
            />
          )}
        </React.Fragment>
      ))}
    </nav>
  );
}

interface StepNavigatorVerticalProps {
  steps: Array<{
    id: string;
    title: string;
    completed?: boolean;
    current?: boolean;
  }>;
  currentStep: number;
  onStepClick?: (stepIndex: number) => void;
  className?: string;
}

export function StepNavigatorVertical({
  steps,
  currentStep,
  onStepClick,
  className,
}: StepNavigatorVerticalProps) {
  return (
    <nav
      className={cn('flex flex-col gap-4', className)}
      aria-label="Tutorial steps"
    >
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center gap-4">
          {/* Step indicator */}
          <button
            onClick={() => onStepClick?.(index)}
            disabled={index > currentStep && !step.completed}
            className={cn(
              'flex items-center justify-center w-10 h-10 rounded-full border-2 font-medium text-sm transition-all flex-shrink-0',
              step.completed && 'bg-green-500 border-green-500 text-white',
              step.current &&
                'bg-blue-500 border-blue-500 text-white scale-110',
              !step.completed &&
                !step.current &&
                'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400',
              onStepClick &&
                !step.completed &&
                !step.current &&
                'hover:border-blue-500 cursor-pointer'
            )}
            aria-label={step.title}
            aria-current={step.current ? 'step' : undefined}
          >
            {step.completed ? <Check size={16} /> : index + 1}
          </button>

          {/* Step title */}
          <span
            className={cn(
              'text-sm font-medium',
              step.current && 'text-blue-600 dark:text-blue-400',
              !step.completed &&
                !step.current &&
                'text-gray-600 dark:text-gray-400'
            )}
          >
            {step.title}
          </span>
        </div>
      ))}
    </nav>
  );
}
