/**
 * Images MVP Tour Steps
 * Purpose-driven onboarding for Images MVP (privacy, photography, authenticity)
 */

import type {
  OnboardingTutorial,
  OnboardingStep,
} from '@/lib/onboarding/onboarding-engine';

export const IMAGES_PRIVACY_TUTORIAL: OnboardingTutorial = {
  id: 'images-privacy-tour',
  name: 'Privacy Check',
  description: 'Protect your privacy by checking image metadata',
  uiVersion: 'images-mvp',
  difficulty: 'beginner',
  estimatedDuration: 3,
  steps: [
    {
      id: 'privacy-welcome',
      title: 'Check Your Privacy',
      description: 'See what personal information is in your photos.',
      position: 'center',
      skippable: false,
      duration: 8,
    },
    {
      id: 'privacy-upload',
      title: 'Upload a Photo',
      description:
        'Drop your photo here to check for GPS, timestamps, and camera info.',
      target: '[data-testid="images-upload"]',
      position: 'top',
      action: 'click',
      skippable: false,
      duration: 30,
    },
    {
      id: 'privacy-tab',
      title: 'Privacy Tab',
      description:
        'View all privacy-sensitive metadata like location and timestamps.',
      target: '[data-testid="tab-privacy"]',
      position: 'bottom',
      skippable: false,
      duration: 15,
    },
    {
      id: 'burn-in',
      title: 'Burned-in Text',
      description: 'We check for text burned into image pixels.',
      target: '[data-testid="burned-text"]',
      position: 'left',
      skippable: true,
      duration: 15,
    },
    {
      id: 'privacy-complete',
      title: 'Privacy Check Complete',
      description:
        'You now know what personal data your photos contain. Clean them before sharing!',
      position: 'center',
      skippable: false,
      duration: 8,
    },
  ],
};

export const IMAGES_PHOTOGRAPHY_TUTORIAL: OnboardingTutorial = {
  id: 'images-photography-tour',
  name: 'Photography Insights',
  description: 'Analyze camera settings and photo metadata',
  uiVersion: 'images-mvp',
  difficulty: 'beginner',
  estimatedDuration: 3,
  steps: [
    {
      id: 'photo-welcome',
      title: 'Photography Mode',
      description: 'Explore camera settings and learn from your photos.',
      position: 'center',
      skippable: false,
      duration: 8,
    },
    {
      id: 'photo-upload',
      title: 'Upload a Photo',
      description: 'Drop a photo to see camera settings and lens info.',
      target: '[data-testid="images-upload"]',
      position: 'top',
      action: 'click',
      skippable: false,
      duration: 30,
    },
    {
      id: 'photo-tab',
      title: 'Photography Tab',
      description: 'View camera settings, exposure data, and more.',
      target: '[data-testid="tab-photography"]',
      position: 'bottom',
      skippable: false,
      duration: 15,
    },
    {
      id: 'quality',
      title: 'Quality Score',
      description: "See how complete your photo's metadata is.",
      target: '[data-testid="quality-indicator"]',
      position: 'left',
      skippable: true,
      duration: 15,
    },
    {
      id: 'photo-complete',
      title: 'Photography Mode Complete',
      description:
        'Use this mode to learn about camera settings and improve your photography!',
      position: 'center',
      skippable: false,
      duration: 8,
    },
  ],
};

export const IMAGES_AUTHENTICITY_TUTORIAL: OnboardingTutorial = {
  id: 'images-authenticity-tour',
  name: 'Authenticity Check',
  description: 'Verify if photos have been tampered with',
  uiVersion: 'images-mvp',
  difficulty: 'intermediate',
  estimatedDuration: 4,
  steps: [
    {
      id: 'auth-welcome',
      title: 'Authenticity Mode',
      description: 'Detect if a photo has been edited or tampered with.',
      position: 'center',
      skippable: false,
      duration: 8,
    },
    {
      id: 'auth-upload',
      title: 'Upload a Photo',
      description: 'Upload to check for inconsistencies and tampering signs.',
      target: '[data-testid="images-upload"]',
      position: 'top',
      action: 'click',
      skippable: false,
      duration: 30,
    },
    {
      id: 'auth-tab',
      title: 'Authenticity Tab',
      description: 'View authenticity analysis and warnings.',
      target: '[data-testid="tab-authenticity"]',
      position: 'bottom',
      skippable: false,
      duration: 15,
    },
    {
      id: 'comparison',
      title: 'Metadata Comparison',
      description: 'Compare embedded vs burned-in metadata for tampering.',
      target: '[data-testid="metadata-comparison"]',
      position: 'left',
      skippable: true,
      duration: 20,
    },
    {
      id: 'auth-complete',
      title: 'Authenticity Check Complete',
      description:
        'You can now verify photo authenticity. Great for forensic work!',
      position: 'center',
      skippable: false,
      duration: 8,
    },
  ],
};

export const IMAGES_MVP_TUTORIALS: OnboardingTutorial[] = [
  IMAGES_PRIVACY_TUTORIAL,
  IMAGES_PHOTOGRAPHY_TUTORIAL,
  IMAGES_AUTHENTICITY_TUTORIAL,
];

export function getImagesTutorialByPurpose(
  purpose: 'privacy' | 'photography' | 'authenticity'
): OnboardingTutorial | undefined {
  switch (purpose) {
    case 'privacy':
      return IMAGES_PRIVACY_TUTORIAL;
    case 'photography':
      return IMAGES_PHOTOGRAPHY_TUTORIAL;
    case 'authenticity':
      return IMAGES_AUTHENTICITY_TUTORIAL;
  }
}

export function getAllImagesMvpTutorials(): OnboardingTutorial[] {
  return IMAGES_MVP_TUTORIALS;
}
