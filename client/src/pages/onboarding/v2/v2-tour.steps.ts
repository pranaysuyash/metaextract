/**
 * V2 UI Tour Steps
 * Minimalist onboarding for V2 UI
 */

import type {
  OnboardingTutorial,
  OnboardingStep,
} from '@/lib/onboarding/onboarding-engine';

export const V2_QUICK_START: OnboardingTutorial = {
  id: 'v2-quick-start',
  name: 'Quick Start',
  description: 'Get started with V2 in 2 minutes',
  uiVersion: 'v2',
  difficulty: 'beginner',
  estimatedDuration: 2,
  steps: [
    {
      id: 'v2-welcome',
      title: 'Welcome to MetaExtract V2',
      description: 'A cleaner, faster way to extract metadata.',
      position: 'center',
      skippable: false,
      duration: 5,
    },
    {
      id: 'v2-upload',
      title: 'Upload',
      description: 'Drop a file or click to upload.',
      target: '[data-testid="v2-upload"]',
      position: 'top',
      action: 'click',
      skippable: false,
      duration: 30,
    },
    {
      id: 'v2-results',
      title: 'Your Results',
      description: 'Key findings appear here for quick insights.',
      target: '[data-testid="v2-results"]',
      position: 'top',
      skippable: false,
      duration: 15,
    },
    {
      id: 'v2-done',
      title: 'Ready!',
      description: "You're all set. Start exploring!",
      position: 'center',
      skippable: false,
      duration: 5,
    },
  ],
};

export const V2_TUTORIALS: OnboardingTutorial[] = [V2_QUICK_START];
