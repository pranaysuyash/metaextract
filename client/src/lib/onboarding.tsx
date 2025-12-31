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
  metadata: Record<string, any>;
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

    const interaction: UserInteraction = {
      timestamp: new Date(),
      type: 'step-complete',
      stepId,
      metadata: metadata || {}
    };

    const updatedProgress = {
      ...session.progress,
      stepsCompleted: [...session.progress.stepsCompleted, stepId],
      currentStepIndex: session.progress.currentStepIndex + 1,
      completionRate: ((session.progress.stepsCompleted.length + 1) / currentPath.steps.length) * 100
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