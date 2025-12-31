/**
 * Onboarding Context and State Management
 * 
 * Provides onboarding state, progress tracking, and user profile management
 * throughout the intelligent onboarding experience.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useAuth } from "./auth";

// ============================================================================
// Core Types and Interfaces
// ============================================================================

export interface UserProfile {
  useCase: 'personal' | 'professional' | 'forensic' | 'research' | 'enterprise';
  technicalLevel: 'beginner' | 'intermediate' | 'advanced';
  primaryFileTypes: string[];
  industry?: string;
  goals: string[];
  completedAt?: Date;
}

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  targetElement?: string;
  position: 'top' | 'bottom' | 'left' | 'right' | 'center';
  skippable: boolean;
  completionCriteria: {
    type: 'interaction' | 'time' | 'manual';
    value?: string | number;
  };
}

export interface OnboardingPath {
  id: string;
  name: string;
  description: string;
  steps: OnboardingStep[];
  estimatedDuration: number;
  prerequisites: string[];
}

export interface OnboardingProgress {
  stepsCompleted: string[];
  milestonesAchieved: string[];
  featuresDiscovered: string[];
  samplesProcessed: string[];
  timeSpent: number;
  completionRate: number;
  currentStepIndex: number;
}

export interface UserInteraction {
  timestamp: Date;
  type: 'step-complete' | 'skip' | 'help-request' | 'feature-try' | 'error';
  stepId?: string;
  featureId?: string;
  duration?: number;
  success?: boolean;
  metadata: Record<string, any>;
}

export interface InteractionMetrics {
  averageStepDuration: number;
  successRate: number;
  skipRate: number;
  helpRequestRate: number;
  errorRate: number;
  interactionSpeed: 'slow' | 'normal' | 'fast';
  proficiencyLevel: 'beginner' | 'intermediate' | 'advanced';
}

export interface AdaptivePacing {
  recommendedDelay: number; // milliseconds between steps
  shouldShowExtraHelp: boolean;
  shouldSkipBasicExplanations: boolean;
  complexityLevel: 'basic' | 'intermediate' | 'advanced';
}

export interface AdvancedTutorial {
  id: string;
  title: string;
  description: string;
  prerequisites: string[]; // IDs of features/steps that must be completed
  interestIndicators: string[]; // Feature IDs that indicate interest in this tutorial
  difficulty: 'intermediate' | 'advanced';
  estimatedDuration: number;
  path: OnboardingPath;
}

export interface FeatureInterest {
  featureId: string;
  interactionCount: number;
  lastInteraction: Date;
  completionRate: number;
  timeSpent: number;
}

export interface OnboardingSession {
  id: string;
  startedAt: Date;
  completedAt?: Date;
  currentStep: number;
  pathId: string;
  userProfile: UserProfile;
  progress: OnboardingProgress;
  interactions: UserInteraction[];
  isActive: boolean;
  metrics?: InteractionMetrics;
  adaptivePacing?: AdaptivePacing;
  featureInterests?: FeatureInterest[];
  unlockedTutorials?: string[]; // IDs of unlocked advanced tutorials
}

// ============================================================================
// Context Interface
// ============================================================================

interface OnboardingContextType {
  // Session state
  session: OnboardingSession | null;
  isOnboardingActive: boolean;
  isOnboardingComplete: boolean;
  
  // Current state
  currentPath: OnboardingPath | null;
  currentStep: OnboardingStep | null;
  
  // Actions
  startOnboarding: (userProfile: UserProfile) => Promise<void>;
  completeStep: (stepId: string, metadata?: Record<string, any>) => Promise<void>;
  skipStep: (stepId: string, reason?: string) => Promise<void>;
  pauseOnboarding: () => Promise<void>;
  resumeOnboarding: () => Promise<void>;
  completeOnboarding: () => Promise<void>;
  
  // Progress tracking
  updateProgress: (progress: Partial<OnboardingProgress>) => void;
  trackInteraction: (interaction: Omit<UserInteraction, 'timestamp'>) => void;
  
  // User profile
  updateUserProfile: (profile: Partial<UserProfile>) => void;
  
  // Adaptive learning
  calculateMetrics: () => InteractionMetrics;
  getAdaptivePacing: () => AdaptivePacing;
  shouldModifyPath: () => boolean;
  modifyPathForUser: () => OnboardingPath | null;
  
  // Advanced tutorial unlocking
  detectFeatureInterest: (featureId: string) => void;
  checkPrerequisites: (tutorialId: string) => boolean;
  getRecommendedTutorials: () => AdvancedTutorial[];
  unlockTutorial: (tutorialId: string) => void;
  isAdvancedTutorialUnlocked: (tutorialId: string) => boolean;
  
  // Utilities
  getRecommendedPath: (profile: UserProfile) => OnboardingPath;
  canAccessStep: (stepId: string) => boolean;
  getNextStep: () => OnboardingStep | null;
  getPreviousStep: () => OnboardingStep | null;
}

// ============================================================================
// Default Onboarding Paths
// ============================================================================

const DEFAULT_PATHS: OnboardingPath[] = [
  {
    id: 'personal-basic',
    name: 'Personal User Journey',
    description: 'Perfect for individuals exploring metadata extraction',
    estimatedDuration: 300, // 5 minutes
    prerequisites: [],
    steps: [
      {
        id: 'welcome',
        title: 'Welcome to MetaExtract',
        description: 'Let\'s get you started with metadata extraction',
        position: 'center',
        skippable: false,
        completionCriteria: { type: 'manual' }
      },
      {
        id: 'upload-intro',
        title: 'Upload Your First File',
        description: 'Try uploading an image or document to see what metadata we can extract',
        targetElement: '[data-testid="upload-zone"]',
        position: 'top',
        skippable: true,
        completionCriteria: { type: 'interaction', value: 'file-upload' }
      },
      {
        id: 'results-tour',
        title: 'Understanding Your Results',
        description: 'Learn how to read and interpret the extracted metadata',
        targetElement: '[data-testid="results-panel"]',
        position: 'left',
        skippable: true,
        completionCriteria: { type: 'manual' }
      }
    ]
  },
  {
    id: 'professional-advanced',
    name: 'Professional User Journey',
    description: 'Comprehensive tour for professional users',
    estimatedDuration: 600, // 10 minutes
    prerequisites: [],
    steps: [
      {
        id: 'welcome-pro',
        title: 'Welcome, Professional User',
        description: 'Let\'s explore advanced metadata extraction capabilities',
        position: 'center',
        skippable: false,
        completionCriteria: { type: 'manual' }
      },
      {
        id: 'batch-processing',
        title: 'Batch Processing',
        description: 'Learn how to process multiple files efficiently',
        targetElement: '[data-testid="batch-upload"]',
        position: 'top',
        skippable: true,
        completionCriteria: { type: 'interaction', value: 'batch-upload' }
      },
      {
        id: 'advanced-features',
        title: 'Advanced Analysis',
        description: 'Discover forensic analysis and advanced metadata extraction',
        targetElement: '[data-testid="advanced-panel"]',
        position: 'right',
        skippable: true,
        completionCriteria: { type: 'manual' }
      }
    ]
  }
];

// ============================================================================
// Advanced Tutorials
// ============================================================================

const ADVANCED_TUTORIALS: AdvancedTutorial[] = [
  {
    id: 'forensic-analysis',
    title: 'Forensic Analysis Deep Dive',
    description: 'Learn advanced forensic analysis techniques for digital evidence',
    prerequisites: ['results-tour', 'upload-intro'],
    interestIndicators: ['forensic-feature', 'advanced-analysis', 'timeline-view'],
    difficulty: 'advanced',
    estimatedDuration: 900, // 15 minutes
    path: {
      id: 'forensic-tutorial',
      name: 'Forensic Analysis Tutorial',
      description: 'Master forensic metadata analysis',
      estimatedDuration: 900,
      prerequisites: ['results-tour'],
      steps: [
        {
          id: 'forensic-intro',
          title: 'Introduction to Forensic Analysis',
          description: 'Understand how metadata can be used for digital forensics',
          position: 'center',
          skippable: false,
          completionCriteria: { type: 'manual' }
        },
        {
          id: 'timeline-analysis',
          title: 'Timeline Analysis',
          description: 'Learn to analyze file timelines and detect anomalies',
          targetElement: '[data-testid="timeline-panel"]',
          position: 'right',
          skippable: true,
          completionCriteria: { type: 'manual' }
        }
      ]
    }
  },
  {
    id: 'batch-processing-advanced',
    title: 'Advanced Batch Processing',
    description: 'Process hundreds of files efficiently with advanced filtering',
    prerequisites: ['upload-intro'],
    interestIndicators: ['batch-upload', 'multiple-files'],
    difficulty: 'intermediate',
    estimatedDuration: 600, // 10 minutes
    path: {
      id: 'batch-tutorial',
      name: 'Batch Processing Tutorial',
      description: 'Master batch file processing',
      estimatedDuration: 600,
      prerequisites: ['upload-intro'],
      steps: [
        {
          id: 'batch-intro',
          title: 'Batch Processing Basics',
          description: 'Learn to upload and process multiple files at once',
          targetElement: '[data-testid="batch-upload"]',
          position: 'top',
          skippable: false,
          completionCriteria: { type: 'interaction', value: 'batch-upload' }
        },
        {
          id: 'batch-filtering',
          title: 'Advanced Filtering',
          description: 'Filter and organize batch results efficiently',
          targetElement: '[data-testid="filter-panel"]',
          position: 'left',
          skippable: true,
          completionCriteria: { type: 'manual' }
        }
      ]
    }
  },
  {
    id: 'comparison-analysis',
    title: 'File Comparison Analysis',
    description: 'Compare metadata across multiple files to find patterns',
    prerequisites: ['results-tour'],
    interestIndicators: ['comparison-view', 'multiple-files', 'analysis'],
    difficulty: 'intermediate',
    estimatedDuration: 450, // 7.5 minutes
    path: {
      id: 'comparison-tutorial',
      name: 'Comparison Analysis Tutorial',
      description: 'Learn to compare file metadata',
      estimatedDuration: 450,
      prerequisites: ['results-tour'],
      steps: [
        {
          id: 'comparison-intro',
          title: 'Introduction to Comparison',
          description: 'Learn how to compare metadata across files',
          targetElement: '[data-testid="comparison-panel"]',
          position: 'center',
          skippable: false,
          completionCriteria: { type: 'manual' }
        }
      ]
    }
  }
];

// ============================================================================
// Context Implementation
// ============================================================================

const OnboardingContext = createContext<OnboardingContextType | null>(null);

export function OnboardingProvider({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated } = useAuth();
  const [session, setSession] = useState<OnboardingSession | null>(null);
  const [currentPath, setCurrentPath] = useState<OnboardingPath | null>(null);

  // Initialize onboarding state on mount
  useEffect(() => {
    initializeOnboarding();
  }, [isAuthenticated, user]);

  const initializeOnboarding = useCallback(async () => {
    if (!isAuthenticated || !user) {
      return;
    }

    try {
      // Check if user has completed onboarding
      const response = await fetch('/api/onboarding/status', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.session) {
          setSession(data.session);
          if (data.session.pathId) {
            const path = DEFAULT_PATHS.find(p => p.id === data.session.pathId);
            setCurrentPath(path || null);
          }
        }
      }
    } catch (error) {
      console.error('Failed to initialize onboarding:', error);
    }
  }, [isAuthenticated, user]);

  const startOnboarding = useCallback(async (userProfile: UserProfile) => {
    const recommendedPath = getRecommendedPath(userProfile);
    
    const newSession: OnboardingSession = {
      id: crypto.randomUUID(),
      startedAt: new Date(),
      currentStep: 0,
      pathId: recommendedPath.id,
      userProfile,
      progress: {
        stepsCompleted: [],
        milestonesAchieved: [],
        featuresDiscovered: [],
        samplesProcessed: [],
        timeSpent: 0,
        completionRate: 0,
        currentStepIndex: 0
      },
      interactions: [],
      isActive: true
    };

    try {
      const response = await fetch('/api/onboarding/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(newSession)
      });

      if (response.ok) {
        setSession(newSession);
        setCurrentPath(recommendedPath);
      }
    } catch (error) {
      console.error('Failed to start onboarding:', error);
      // Continue with local state even if API fails
      setSession(newSession);
      setCurrentPath(recommendedPath);
    }
  }, []);

  const completeStep = useCallback(async (stepId: string, metadata?: Record<string, any>) => {
    if (!session || !currentPath) return;

    // Calculate step duration
    const stepStartTime = session.interactions
      .filter(i => i.stepId === stepId)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())[0]?.timestamp;
    
    const duration = stepStartTime 
      ? Date.now() - new Date(stepStartTime).getTime()
      : undefined;

    const interaction: UserInteraction = {
      timestamp: new Date(),
      type: 'step-complete',
      stepId,
      duration,
      success: metadata?.validated !== false,
      metadata: metadata || {}
    };

    const updatedProgress = {
      ...session.progress,
      stepsCompleted: [...session.progress.stepsCompleted, stepId],
      currentStepIndex: session.progress.currentStepIndex + 1,
      completionRate: ((session.progress.stepsCompleted.length + 1) / currentPath.steps.length) * 100,
      timeSpent: session.progress.timeSpent + (duration || 0)
    };

    const updatedSession = {
      ...session,
      progress: updatedProgress,
      interactions: [...session.interactions, interaction]
    };

    setSession(updatedSession);

    try {
      await fetch('/api/onboarding/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ session: updatedSession, interaction })
      });
    } catch (error) {
      console.error('Failed to save onboarding progress:', error);
    }
  }, [session, currentPath]);

  const skipStep = useCallback(async (stepId: string, reason?: string) => {
    if (!session || !currentPath) return;

    const interaction: UserInteraction = {
      timestamp: new Date(),
      type: 'skip',
      stepId,
      metadata: { reason: reason || 'user-skip' }
    };

    const updatedProgress = {
      ...session.progress,
      currentStepIndex: session.progress.currentStepIndex + 1
    };

    const updatedSession = {
      ...session,
      progress: updatedProgress,
      interactions: [...session.interactions, interaction]
    };

    setSession(updatedSession);

    try {
      await fetch('/api/onboarding/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ session: updatedSession, interaction })
      });
    } catch (error) {
      console.error('Failed to save onboarding progress:', error);
    }
  }, [session, currentPath]);

  const pauseOnboarding = useCallback(async () => {
    if (!session) return;

    const updatedSession = {
      ...session,
      isActive: false
    };

    setSession(updatedSession);

    try {
      await fetch('/api/onboarding/pause', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ sessionId: session.id })
      });
    } catch (error) {
      console.error('Failed to pause onboarding:', error);
    }
  }, [session]);

  const resumeOnboarding = useCallback(async () => {
    if (!session) return;

    const updatedSession = {
      ...session,
      isActive: true
    };

    setSession(updatedSession);

    try {
      await fetch('/api/onboarding/resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ sessionId: session.id })
      });
    } catch (error) {
      console.error('Failed to resume onboarding:', error);
    }
  }, [session]);

  const completeOnboarding = useCallback(async () => {
    if (!session) return;

    const updatedSession = {
      ...session,
      completedAt: new Date(),
      isActive: false,
      progress: {
        ...session.progress,
        completionRate: 100
      }
    };

    setSession(updatedSession);

    try {
      await fetch('/api/onboarding/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ sessionId: session.id })
      });
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
    }
  }, [session]);

  const updateProgress = useCallback((progress: Partial<OnboardingProgress>) => {
    if (!session) return;

    const updatedSession = {
      ...session,
      progress: { ...session.progress, ...progress }
    };

    setSession(updatedSession);
  }, [session]);

  const trackInteraction = useCallback((interaction: Omit<UserInteraction, 'timestamp'>) => {
    if (!session) return;

    const fullInteraction: UserInteraction = {
      ...interaction,
      timestamp: new Date()
    };

    const updatedSession = {
      ...session,
      interactions: [...session.interactions, fullInteraction]
    };

    setSession(updatedSession);
  }, [session]);

  const updateUserProfile = useCallback((profile: Partial<UserProfile>) => {
    if (!session) return;

    const updatedSession = {
      ...session,
      userProfile: { ...session.userProfile, ...profile }
    };

    setSession(updatedSession);
  }, [session]);

  const getRecommendedPath = useCallback((profile: UserProfile): OnboardingPath => {
    // Simple path recommendation logic
    if (profile.useCase === 'personal' && profile.technicalLevel === 'beginner') {
      return DEFAULT_PATHS.find(p => p.id === 'personal-basic') || DEFAULT_PATHS[0];
    }
    
    if (profile.useCase === 'professional' || profile.technicalLevel === 'advanced') {
      return DEFAULT_PATHS.find(p => p.id === 'professional-advanced') || DEFAULT_PATHS[1];
    }

    return DEFAULT_PATHS[0];
  }, []);

  const canAccessStep = useCallback((stepId: string): boolean => {
    if (!session || !currentPath) return false;

    const stepIndex = currentPath.steps.findIndex(s => s.id === stepId);
    return stepIndex <= session.progress.currentStepIndex;
  }, [session, currentPath]);

  const getNextStep = useCallback((): OnboardingStep | null => {
    if (!session || !currentPath) return null;

    const nextIndex = session.progress.currentStepIndex;
    return currentPath.steps[nextIndex] || null;
  }, [session, currentPath]);

  const getPreviousStep = useCallback((): OnboardingStep | null => {
    if (!session || !currentPath) return null;

    const prevIndex = session.progress.currentStepIndex - 1;
    return prevIndex >= 0 ? currentPath.steps[prevIndex] : null;
  }, [session, currentPath]);

  // ============================================================================
  // Adaptive Learning Functions
  // ============================================================================

  /**
   * Calculate interaction metrics from user behavior
   */
  const calculateMetrics = useCallback((): InteractionMetrics => {
    if (!session || session.interactions.length === 0) {
      return {
        averageStepDuration: 0,
        successRate: 100,
        skipRate: 0,
        helpRequestRate: 0,
        errorRate: 0,
        interactionSpeed: 'normal',
        proficiencyLevel: 'beginner'
      };
    }

    const interactions = session.interactions;
    const totalInteractions = interactions.length;

    // Calculate step durations
    const stepCompletions = interactions.filter(i => i.type === 'step-complete' && i.duration);
    const averageStepDuration = stepCompletions.length > 0
      ? stepCompletions.reduce((sum, i) => sum + (i.duration || 0), 0) / stepCompletions.length
      : 0;

    // Calculate rates
    const successfulSteps = interactions.filter(i => i.type === 'step-complete' && i.success !== false).length;
    const skippedSteps = interactions.filter(i => i.type === 'skip').length;
    const helpRequests = interactions.filter(i => i.type === 'help-request').length;
    const errors = interactions.filter(i => i.type === 'error').length;

    const successRate = totalInteractions > 0 ? (successfulSteps / totalInteractions) * 100 : 100;
    const skipRate = totalInteractions > 0 ? (skippedSteps / totalInteractions) * 100 : 0;
    const helpRequestRate = totalInteractions > 0 ? (helpRequests / totalInteractions) * 100 : 0;
    const errorRate = totalInteractions > 0 ? (errors / totalInteractions) * 100 : 0;

    // Determine interaction speed (based on average step duration)
    // Fast: < 30 seconds, Normal: 30-90 seconds, Slow: > 90 seconds
    let interactionSpeed: 'slow' | 'normal' | 'fast' = 'normal';
    if (averageStepDuration > 0) {
      if (averageStepDuration < 30000) {
        interactionSpeed = 'fast';
      } else if (averageStepDuration > 90000) {
        interactionSpeed = 'slow';
      }
    }

    // Determine proficiency level based on multiple factors
    let proficiencyLevel: 'beginner' | 'intermediate' | 'advanced' = 'beginner';
    
    // Advanced: high success rate, low skip/help/error rates, fast speed
    if (successRate > 80 && skipRate < 10 && helpRequestRate < 10 && errorRate < 5 && interactionSpeed === 'fast') {
      proficiencyLevel = 'advanced';
    }
    // Intermediate: moderate success, some skips/help, normal speed
    else if (successRate > 60 && skipRate < 30 && helpRequestRate < 30 && errorRate < 15) {
      proficiencyLevel = 'intermediate';
    }

    return {
      averageStepDuration,
      successRate,
      skipRate,
      helpRequestRate,
      errorRate,
      interactionSpeed,
      proficiencyLevel
    };
  }, [session]);

  /**
   * Get adaptive pacing recommendations based on user metrics
   */
  const getAdaptivePacing = useCallback((): AdaptivePacing => {
    const metrics = calculateMetrics();

    // Default pacing
    let recommendedDelay = 1000; // 1 second between steps
    let shouldShowExtraHelp = false;
    let shouldSkipBasicExplanations = false;
    let complexityLevel: 'basic' | 'intermediate' | 'advanced' = 'basic';

    // Adjust based on interaction speed
    if (metrics.interactionSpeed === 'slow') {
      recommendedDelay = 2000; // Give more time
      shouldShowExtraHelp = true;
    } else if (metrics.interactionSpeed === 'fast') {
      recommendedDelay = 500; // Move faster
      shouldSkipBasicExplanations = metrics.proficiencyLevel === 'advanced';
    }

    // Adjust based on error and help request rates
    if (metrics.errorRate > 10 || metrics.helpRequestRate > 20) {
      shouldShowExtraHelp = true;
      complexityLevel = 'basic';
    } else if (metrics.successRate > 80 && metrics.skipRate < 10) {
      complexityLevel = metrics.proficiencyLevel === 'advanced' ? 'advanced' : 'intermediate';
    }

    // Adjust based on proficiency level
    if (metrics.proficiencyLevel === 'advanced') {
      shouldSkipBasicExplanations = true;
      complexityLevel = 'advanced';
    } else if (metrics.proficiencyLevel === 'beginner') {
      shouldShowExtraHelp = true;
      complexityLevel = 'basic';
    }

    return {
      recommendedDelay,
      shouldShowExtraHelp,
      shouldSkipBasicExplanations,
      complexityLevel
    };
  }, [calculateMetrics]);

  /**
   * Determine if the onboarding path should be modified
   */
  const shouldModifyPath = useCallback((): boolean => {
    if (!session || !currentPath) return false;

    const metrics = calculateMetrics();
    const pacing = getAdaptivePacing();

    // Modify path if user is significantly faster or slower than expected
    const expectedDuration = currentPath.estimatedDuration;
    const actualDuration = session.progress.timeSpent;
    const progressRatio = session.progress.currentStepIndex / currentPath.steps.length;

    if (progressRatio > 0.3) { // Only modify after 30% completion
      // User is much faster than expected and showing high proficiency
      if (metrics.proficiencyLevel === 'advanced' && actualDuration < expectedDuration * 0.5) {
        return true;
      }

      // User is struggling (high error rate, many help requests)
      if (metrics.errorRate > 15 || metrics.helpRequestRate > 30) {
        return true;
      }

      // User's complexity level doesn't match path
      if (pacing.complexityLevel === 'advanced' && currentPath.id.includes('basic')) {
        return true;
      }
      if (pacing.complexityLevel === 'basic' && currentPath.id.includes('advanced')) {
        return true;
      }
    }

    return false;
  }, [session, currentPath, calculateMetrics, getAdaptivePacing]);

  /**
   * Modify the onboarding path based on user behavior
   */
  const modifyPathForUser = useCallback((): OnboardingPath | null => {
    if (!session || !currentPath) return null;

    const metrics = calculateMetrics();
    const pacing = getAdaptivePacing();

    // If user is advanced and on basic path, switch to advanced
    if (metrics.proficiencyLevel === 'advanced' && currentPath.id.includes('basic')) {
      const advancedPath = DEFAULT_PATHS.find(p => p.id.includes('advanced'));
      if (advancedPath) {
        return advancedPath;
      }
    }

    // If user is struggling on advanced path, switch to basic
    if ((metrics.errorRate > 15 || metrics.helpRequestRate > 30) && currentPath.id.includes('advanced')) {
      const basicPath = DEFAULT_PATHS.find(p => p.id.includes('basic'));
      if (basicPath) {
        return basicPath;
      }
    }

    // Create a modified version of current path with adjusted steps
    const modifiedSteps = currentPath.steps.map(step => {
      // Skip basic explanations for advanced users
      if (pacing.shouldSkipBasicExplanations && step.id.includes('intro')) {
        return { ...step, skippable: true };
      }

      // Make steps less skippable for struggling users
      if (pacing.shouldShowExtraHelp) {
        return { ...step, skippable: false };
      }

      return step;
    });

    return {
      ...currentPath,
      steps: modifiedSteps,
      estimatedDuration: Math.round(currentPath.estimatedDuration * (pacing.recommendedDelay / 1000))
    };
  }, [session, currentPath, calculateMetrics, getAdaptivePacing]);

  // Update metrics and pacing periodically
  useEffect(() => {
    if (!session || !session.isActive) return;

    const updateMetrics = () => {
      const metrics = calculateMetrics();
      const pacing = getAdaptivePacing();

      const updatedSession = {
        ...session,
        metrics,
        adaptivePacing: pacing
      };

      setSession(updatedSession);

      // Check if path should be modified
      if (shouldModifyPath()) {
        const newPath = modifyPathForUser();
        if (newPath && newPath.id !== currentPath?.id) {
          setCurrentPath(newPath);
          console.log('Onboarding path adapted based on user behavior:', newPath.id);
        }
      }
    };

    // Update metrics every 30 seconds
    const interval = setInterval(updateMetrics, 30000);

    return () => clearInterval(interval);
  }, [session, currentPath, calculateMetrics, getAdaptivePacing, shouldModifyPath, modifyPathForUser]);

  // ============================================================================
  // Advanced Tutorial Unlocking Functions
  // ============================================================================

  /**
   * Detect and track user interest in specific features
   */
  const detectFeatureInterest = useCallback((featureId: string) => {
    if (!session) return;

    const existingInterests = session.featureInterests || [];
    const existingInterest = existingInterests.find(i => i.featureId === featureId);

    let updatedInterests: FeatureInterest[];

    if (existingInterest) {
      // Update existing interest
      updatedInterests = existingInterests.map(interest =>
        interest.featureId === featureId
          ? {
              ...interest,
              interactionCount: interest.interactionCount + 1,
              lastInteraction: new Date()
            }
          : interest
      );
    } else {
      // Add new interest
      updatedInterests = [
        ...existingInterests,
        {
          featureId,
          interactionCount: 1,
          lastInteraction: new Date(),
          completionRate: 0,
          timeSpent: 0
        }
      ];
    }

    const updatedSession = {
      ...session,
      featureInterests: updatedInterests
    };

    setSession(updatedSession);

    // Track interaction
    trackInteraction({
      type: 'feature-try',
      featureId,
      metadata: { action: 'interest-detected' }
    });
  }, [session, trackInteraction]);

  /**
   * Check if user has completed all prerequisites for a tutorial
   */
  const checkPrerequisites = useCallback((tutorialId: string): boolean => {
    if (!session) return false;

    const tutorial = ADVANCED_TUTORIALS.find(t => t.id === tutorialId);
    if (!tutorial) return false;

    // Check if all prerequisite steps have been completed
    const completedSteps = session.progress.stepsCompleted;
    return tutorial.prerequisites.every(prereq => completedSteps.includes(prereq));
  }, [session]);

  /**
   * Get recommended advanced tutorials based on user interests and prerequisites
   */
  const getRecommendedTutorials = useCallback((): AdvancedTutorial[] => {
    if (!session) return [];

    const featureInterests = session.featureInterests || [];
    const unlockedTutorials = session.unlockedTutorials || [];
    const metrics = calculateMetrics();

    // Filter tutorials based on prerequisites and proficiency
    const eligibleTutorials = ADVANCED_TUTORIALS.filter(tutorial => {
      // Must meet prerequisites
      if (!checkPrerequisites(tutorial.id)) return false;

      // Must not already be unlocked
      if (unlockedTutorials.includes(tutorial.id)) return false;

      // Must match proficiency level
      if (tutorial.difficulty === 'advanced' && metrics.proficiencyLevel === 'beginner') {
        return false;
      }

      return true;
    });

    // Score tutorials based on interest indicators
    const scoredTutorials = eligibleTutorials.map(tutorial => {
      let score = 0;

      // Check interest indicators
      tutorial.interestIndicators.forEach(indicator => {
        const interest = featureInterests.find(i => i.featureId === indicator);
        if (interest) {
          score += interest.interactionCount * 10;
          
          // Bonus for recent interactions (within last 5 minutes)
          const timeSinceInteraction = Date.now() - new Date(interest.lastInteraction).getTime();
          if (timeSinceInteraction < 300000) {
            score += 20;
          }
        }
      });

      // Bonus for matching user's technical level
      if (tutorial.difficulty === 'intermediate' && metrics.proficiencyLevel === 'intermediate') {
        score += 15;
      }
      if (tutorial.difficulty === 'advanced' && metrics.proficiencyLevel === 'advanced') {
        score += 25;
      }

      return { tutorial, score };
    });

    // Sort by score and return top recommendations
    return scoredTutorials
      .sort((a, b) => b.score - a.score)
      .filter(item => item.score > 0) // Only return tutorials with some interest
      .slice(0, 3) // Top 3 recommendations
      .map(item => item.tutorial);
  }, [session, calculateMetrics, checkPrerequisites]);

  /**
   * Unlock an advanced tutorial for the user
   */
  const unlockTutorial = useCallback((tutorialId: string) => {
    if (!session) return;

    const unlockedTutorials = session.unlockedTutorials || [];
    
    // Don't unlock if already unlocked
    if (unlockedTutorials.includes(tutorialId)) return;

    // Check prerequisites
    if (!checkPrerequisites(tutorialId)) {
      console.warn(`Cannot unlock tutorial ${tutorialId}: prerequisites not met`);
      return;
    }

    const updatedSession = {
      ...session,
      unlockedTutorials: [...unlockedTutorials, tutorialId]
    };

    setSession(updatedSession);

    // Track milestone
    const updatedProgress = {
      ...session.progress,
      milestonesAchieved: [...session.progress.milestonesAchieved, `tutorial-unlocked-${tutorialId}`]
    };

    updateProgress(updatedProgress);

    console.log(`Advanced tutorial unlocked: ${tutorialId}`);
  }, [session, checkPrerequisites, updateProgress]);

  /**
   * Check if an advanced tutorial is unlocked
   */
  const isAdvancedTutorialUnlocked = useCallback((tutorialId: string): boolean => {
    if (!session) return false;
    const unlockedTutorials = session.unlockedTutorials || [];
    return unlockedTutorials.includes(tutorialId);
  }, [session]);

  const currentStep = getNextStep();
  const isOnboardingActive = session?.isActive || false;
  const isOnboardingComplete = session?.completedAt != null;

  return (
    <OnboardingContext.Provider
      value={{
        session,
        isOnboardingActive,
        isOnboardingComplete,
        currentPath,
        currentStep,
        startOnboarding,
        completeStep,
        skipStep,
        pauseOnboarding,
        resumeOnboarding,
        completeOnboarding,
        updateProgress,
        trackInteraction,
        updateUserProfile,
        calculateMetrics,
        getAdaptivePacing,
        shouldModifyPath,
        modifyPathForUser,
        detectFeatureInterest,
        checkPrerequisites,
        getRecommendedTutorials,
        unlockTutorial,
        isAdvancedTutorialUnlocked,
        getRecommendedPath,
        canAccessStep,
        getNextStep,
        getPreviousStep
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error("useOnboarding must be used within an OnboardingProvider");
  }
  return context;
}

/**
 * Hook to check if user should see onboarding
 */
export function useShouldShowOnboarding(): boolean {
  const { user, isAuthenticated } = useAuth();
  const { isOnboardingComplete } = useOnboarding();
  
  // Show onboarding for new authenticated users who haven't completed it
  return isAuthenticated && !!user && !isOnboardingComplete;
}

/**
 * Hook to get onboarding analytics data
 */
export function useOnboardingAnalytics() {
  const { session } = useOnboarding();
  
  return {
    timeSpent: session?.progress.timeSpent || 0,
    stepsCompleted: session?.progress.stepsCompleted.length || 0,
    completionRate: session?.progress.completionRate || 0,
    interactions: session?.interactions || [],
    userProfile: session?.userProfile
  };
}