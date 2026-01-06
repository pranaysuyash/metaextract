/**
 * Onboarding Configuration - Per-UI-version tutorial configurations
 */

import type { OnboardingTutorial } from './onboarding-engine';

export interface UIOnboardingConfig {
  uiVersion: 'original' | 'v2' | 'images-mvp';
  enabled: boolean;
  autoStart: boolean;
  showSkipButton: boolean;
  allowPauseResume: boolean;
  maxSkipCount: number;
  tutorials: OnboardingTutorial[];
}

/**
 * Original UI - Full feature set, comprehensive onboarding
 */
export const originalUIConfig: UIOnboardingConfig = {
  uiVersion: 'original',
  enabled: true,
  autoStart: true,
  showSkipButton: true,
  allowPauseResume: true,
  maxSkipCount: 3,
  tutorials: [
    {
      id: 'original-basic-tour',
      name: 'Basic Tour',
      description: 'Learn the fundamentals of metadata extraction',
      uiVersion: 'original',
      difficulty: 'beginner',
      estimatedDuration: 5,
      steps: [
        {
          id: 'welcome',
          title: 'Welcome to MetaExtract',
          description:
            "This tour will guide you through extracting metadata from your files. Let's get started!",
          position: 'center',
          skippable: false,
          duration: 10,
        },
        {
          id: 'upload-file',
          title: 'Upload a File',
          description:
            'Click or drag and drop a file here to extract its metadata. We support images, documents, videos, and more.',
          target: '[data-testid="upload-zone"]',
          position: 'top',
          action: 'click',
          skippable: false,
          duration: 30,
        },
        {
          id: 'view-results',
          title: 'View Results',
          description:
            'Your extracted metadata will appear here. We organize it into easy-to-understand sections.',
          target: '[data-testid="results-container"]',
          position: 'top',
          skippable: false,
          duration: 15,
        },
        {
          id: 'explore-gps',
          title: 'GPS Location',
          description:
            'See where your photo was taken. This shows camera location data embedded in your image.',
          target: '[data-testid="gps-section"]',
          position: 'left',
          skippable: true,
          duration: 20,
        },
        {
          id: 'check-exif',
          title: 'Camera Settings',
          description:
            'View camera settings like aperture, ISO, and shutter speed. Great for photographers!',
          target: '[data-testid="exif-section"]',
          position: 'left',
          skippable: true,
          duration: 20,
        },
        {
          id: 'download-results',
          title: 'Download Results',
          description:
            'Save your extracted metadata as JSON or PDF for your records.',
          target: '[data-testid="download-button"]',
          position: 'top',
          skippable: true,
          duration: 15,
        },
        {
          id: 'tour-complete',
          title: "You're All Set!",
          description:
            "You've completed the basic tour. Upload any file to start extracting metadata!",
          position: 'center',
          skippable: false,
          duration: 10,
        },
      ],
    },
    {
      id: 'original-advanced-features',
      name: 'Advanced Features',
      description: 'Learn about powerful features for professionals',
      uiVersion: 'original',
      difficulty: 'intermediate',
      estimatedDuration: 10,
      steps: [
        {
          id: 'burned-metadata',
          title: 'Burned-in Metadata',
          description:
            'We can extract text from image pixels using OCR technology.',
          target: '[data-testid="burned-metadata"]',
          position: 'left',
          skippable: true,
          duration: 20,
        },
        {
          id: 'metadata-comparison',
          title: 'Metadata Comparison',
          description:
            'Compare embedded metadata with burned-in text to detect tampering.',
          target: '[data-testid="metadata-comparison"]',
          position: 'left',
          skippable: true,
          duration: 20,
        },
        {
          id: 'file-integrity',
          title: 'File Integrity',
          description: 'View cryptographic hashes to verify file authenticity.',
          target: '[data-testid="file-integrity"]',
          position: 'left',
          skippable: true,
          duration: 15,
        },
        {
          id: 'advanced-complete',
          title: 'Advanced Complete!',
          description:
            'You now know about advanced forensic features. Great job!',
          position: 'center',
          skippable: false,
          duration: 10,
        },
      ],
    },
  ],
};

/**
 * V2 UI - Streamlined, minimal onboarding
 */
export const v2UIConfig: UIOnboardingConfig = {
  uiVersion: 'v2',
  enabled: true,
  autoStart: true,
  showSkipButton: true,
  allowPauseResume: false,
  maxSkipCount: 1,
  tutorials: [
    {
      id: 'v2-quick-start',
      name: 'Quick Start',
      description: 'Get started with V2 in 2 minutes',
      uiVersion: 'v2',
      difficulty: 'beginner',
      estimatedDuration: 2,
      steps: [
        {
          id: 'welcome',
          title: 'Welcome to MetaExtract V2',
          description: 'A cleaner, faster way to extract metadata.',
          position: 'center',
          skippable: false,
          duration: 5,
        },
        {
          id: 'upload',
          title: 'Upload',
          description: 'Drop a file or click to upload.',
          target: '[data-testid="v2-upload"]',
          position: 'top',
          action: 'click',
          skippable: false,
          duration: 30,
        },
        {
          id: 'results',
          title: 'Your Results',
          description: 'Key findings appear here for quick insights.',
          target: '[data-testid="v2-results"]',
          position: 'top',
          skippable: false,
          duration: 15,
        },
        {
          id: 'done',
          title: 'Ready!',
          description: "You're all set. Start exploring!",
          position: 'center',
          skippable: false,
          duration: 5,
        },
      ],
    },
  ],
};

/**
 * Images MVP - Purpose-driven, tab-based onboarding
 */
export const imagesMVPConfig: UIOnboardingConfig = {
  uiVersion: 'images-mvp',
  enabled: true,
  autoStart: true,
  showSkipButton: true,
  allowPauseResume: true,
  maxSkipCount: 2,
  tutorials: [
    {
      id: 'images-privacy-focus',
      name: 'Privacy Check',
      description: 'Protect your privacy by checking image metadata',
      uiVersion: 'images-mvp',
      difficulty: 'beginner',
      estimatedDuration: 3,
      steps: [
        {
          id: 'welcome',
          title: 'Check Your Privacy',
          description: 'See what personal information is in your photos.',
          position: 'center',
          skippable: false,
          duration: 8,
        },
        {
          id: 'upload',
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
          description: 'We check for text burned into the image pixels.',
          target: '[data-testid="burned-text"]',
          position: 'left',
          skippable: true,
          duration: 15,
        },
        {
          id: 'complete',
          title: 'Privacy Check Complete',
          description:
            'You now know what personal data your photos contain. Clean them before sharing!',
          position: 'center',
          skippable: false,
          duration: 8,
        },
      ],
    },
    {
      id: 'images-photography-focus',
      name: 'Photography Insights',
      description: 'Analyze camera settings and photo metadata',
      uiVersion: 'images-mvp',
      difficulty: 'beginner',
      estimatedDuration: 3,
      steps: [
        {
          id: 'welcome',
          title: 'Photography Mode',
          description: 'Explore camera settings and learn from your photos.',
          position: 'center',
          skippable: false,
          duration: 8,
        },
        {
          id: 'upload',
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
          id: 'complete',
          title: 'Photography Mode Complete',
          description:
            'Use this mode to learn about camera settings and improve your photography!',
          position: 'center',
          skippable: false,
          duration: 8,
        },
      ],
    },
    {
      id: 'images-authenticity-focus',
      name: 'Authenticity Check',
      description: 'Verify if photos have been tampered with',
      uiVersion: 'images-mvp',
      difficulty: 'intermediate',
      estimatedDuration: 4,
      steps: [
        {
          id: 'welcome',
          title: 'Authenticity Mode',
          description: 'Detect if a photo has been edited or tampered with.',
          position: 'center',
          skippable: false,
          duration: 8,
        },
        {
          id: 'upload',
          title: 'Upload a Photo',
          description:
            'Upload to check for inconsistencies and tampering signs.',
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
          id: 'complete',
          title: 'Authenticity Check Complete',
          description:
            'You can now verify photo authenticity. Great for forensic work!',
          position: 'center',
          skippable: false,
          duration: 8,
        },
      ],
    },
  ],
};

/**
 * Get configuration for UI version
 */
export function getUIConfig(
  uiVersion: 'original' | 'v2' | 'images-mvp'
): UIOnboardingConfig {
  switch (uiVersion) {
    case 'original':
      return originalUIConfig;
    case 'v2':
      return v2UIConfig;
    case 'images-mvp':
      return imagesMVPConfig;
  }
}

/**
 * Get tutorial by ID across all UI versions
 */
export function getTutorialById(
  tutorialId: string
): OnboardingTutorial | undefined {
  const allConfigs = [originalUIConfig, v2UIConfig, imagesMVPConfig];
  for (const config of allConfigs) {
    const tutorial = config.tutorials.find(t => t.id === tutorialId);
    if (tutorial) {
      return tutorial;
    }
  }
  return undefined;
}
