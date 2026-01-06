/**
 * Original UI Tour Steps
 * Comprehensive onboarding for full-featured UI
 */

import type {
  OnboardingTutorial,
  OnboardingStep,
} from '@/lib/onboarding/onboarding-engine';

export const ORIGINAL_BASIC_TOUR: OnboardingTutorial = {
  id: 'original-basic-tour',
  name: 'Basic Tour',
  description: 'Learn fundamentals of metadata extraction',
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
      id: 'explore-filesystem',
      title: 'File System',
      description:
        'View file system metadata like creation and modification dates.',
      target: '[data-testid="filesystem-section"]',
      position: 'left',
      skippable: true,
      duration: 15,
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
};

export const ORIGINAL_ADVANCED_TOUR: OnboardingTutorial = {
  id: 'original-advanced-tour',
  name: 'Advanced Features',
  description: 'Learn about powerful features for professionals',
  uiVersion: 'original',
  difficulty: 'intermediate',
  estimatedDuration: 10,
  steps: [
    {
      id: 'advanced-welcome',
      title: 'Advanced Features',
      description:
        'Discover powerful tools for forensic analysis and professional workflows.',
      position: 'center',
      skippable: false,
      duration: 10,
    },
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
      id: 'filters-and-search',
      title: 'Filters & Search',
      description:
        'Use powerful search and filter tools to find specific metadata.',
      target: '[data-testid="search-bar"]',
      position: 'top',
      skippable: true,
      duration: 15,
    },
    {
      id: 'export-options',
      title: 'Export Options',
      description:
        'Choose from multiple export formats including CSV, JSON, and PDF.',
      target: '[data-testid="export-menu"]',
      position: 'top',
      skippable: true,
      duration: 15,
    },
    {
      id: 'batch-operations',
      title: 'Batch Operations',
      description: 'Process multiple files at once with batch upload.',
      target: '[data-testid="batch-upload"]',
      position: 'top',
      skippable: true,
      duration: 20,
    },
    {
      id: 'advanced-complete',
      title: 'Advanced Complete!',
      description: 'You now know about advanced forensic features. Great job!',
      position: 'center',
      skippable: false,
      duration: 10,
    },
  ],
};

export const ORIGINAL_TUTORIALS: OnboardingTutorial[] = [
  ORIGINAL_BASIC_TOUR,
  ORIGINAL_ADVANCED_TOUR,
];
