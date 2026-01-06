/**
 * Tutorial Provider - Context provider for tutorial system
 */

import React, {
  createContext,
  useContext,
  useCallback,
  useMemo,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import type {
  OnboardingTutorial,
  OnboardingStep,
} from '@/lib/onboarding/onboarding-engine';
import { OnboardingEngine } from '@/lib/onboarding/onboarding-engine';
import { onboardingStorage } from '@/lib/onboarding/onboarding-storage';
import { onboardingEventBus } from '@/lib/onboarding/onboarding-events';
import {
  getUIConfig,
  getTutorialById,
} from '@/lib/onboarding/onboarding-config';

interface TutorialContextValue {
  engine: OnboardingEngine;
  activeTutorial: OnboardingTutorial | null;
  currentStep: OnboardingStep | null;
  stepIndex: number;
  isPaused: boolean;
  isLoading: boolean;
  startTutorial: (tutorialId: string) => Promise<void>;
  completeStep: (stepId: string) => Promise<void>;
  skipStep: (stepId: string) => Promise<void>;
  nextStep: () => Promise<void>;
  previousStep: () => Promise<void>;
  skipTutorial: () => Promise<void>;
  pauseTutorial: () => void;
  resumeTutorial: () => void;
  restartTutorial: () => Promise<void>;
  dismissTutorial: () => Promise<void>;
}

const TutorialContext = createContext<TutorialContextValue | null>(null);

export function TutorialProvider({
  children,
  userId,
  uiVersion,
}: {
  children: ReactNode;
  userId: string;
  uiVersion: 'original' | 'v2' | 'images-mvp';
}) {
  const [engine] = useState(() => new OnboardingEngine(userId, uiVersion));
  const [activeTutorial, setActiveTutorial] =
    useState<OnboardingTutorial | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const currentStep = useMemo(() => {
    if (!activeTutorial || stepIndex >= activeTutorial.steps.length) {
      return null;
    }
    return activeTutorial.steps[stepIndex];
  }, [activeTutorial, stepIndex]);

  const startTutorial = useCallback(
    async (tutorialId: string) => {
      setIsLoading(true);
      try {
        const tutorial = getTutorialById(tutorialId);
        if (!tutorial) {
          console.error(`[TutorialProvider] Tutorial not found: ${tutorialId}`);
          return;
        }

        const config = getUIConfig(uiVersion);
        const isSkipped = await onboardingStorage.getSkipPreferences(
          userId,
          tutorialId
        );

        if (isSkipped) {
          console.log(
            `[TutorialProvider] Tutorial skipped by user preference: ${tutorialId}`
          );
          return;
        }

        await engine.startTutorial(tutorial);
        setActiveTutorial(tutorial);
        setStepIndex(0);
        setIsPaused(false);
      } catch (error) {
        console.error('[TutorialProvider] Failed to start tutorial', error);
      } finally {
        setIsLoading(false);
      }
    },
    [engine, userId, uiVersion]
  );

  const completeStep = useCallback(
    async (stepId: string) => {
      if (!activeTutorial) return;

      setIsLoading(true);
      try {
        await engine.completeStep(activeTutorial.id, stepId);
        setStepIndex(prev => prev + 1);
      } catch (error) {
        console.error('[TutorialProvider] Failed to complete step', error);
      } finally {
        setIsLoading(false);
      }
    },
    [engine, activeTutorial]
  );

  const skipStep = useCallback(
    async (stepId: string) => {
      if (!activeTutorial) return;

      setIsLoading(true);
      try {
        await engine.skipStep(activeTutorial.id, stepId);
        setStepIndex(prev => prev + 1);
      } catch (error) {
        console.error('[TutorialProvider] Failed to skip step', error);
      } finally {
        setIsLoading(false);
      }
    },
    [engine, activeTutorial]
  );

  const nextStep = useCallback(async () => {
    if (!activeTutorial) return;

    const nextIndex = stepIndex + 1;
    if (nextIndex >= activeTutorial.steps.length) {
      await engine.completeTutorial(activeTutorial.id);
      setActiveTutorial(null);
      setStepIndex(0);
    } else {
      setStepIndex(nextIndex);
    }
  }, [engine, activeTutorial, stepIndex]);

  const previousStep = useCallback(async () => {
    if (!activeTutorial || stepIndex <= 0) return;

    const prevIndex = stepIndex - 1;
    setStepIndex(prevIndex);
  }, [activeTutorial, stepIndex]);

  const skipTutorial = useCallback(async () => {
    if (!activeTutorial) return;

    setIsLoading(true);
    try {
      await onboardingStorage.setSkipPreferences(
        userId,
        activeTutorial.id,
        true
      );
      await engine.dismissTutorial(activeTutorial.id);
      setActiveTutorial(null);
      setStepIndex(0);
      setIsPaused(false);
    } catch (error) {
      console.error('[TutorialProvider] Failed to skip tutorial', error);
    } finally {
      setIsLoading(false);
    }
  }, [engine, activeTutorial, userId]);

  const pauseTutorial = useCallback(() => {
    engine.pauseTutorial();
    setIsPaused(true);
  }, [engine]);

  const resumeTutorial = useCallback(() => {
    engine.resumeTutorial();
    setIsPaused(false);
  }, [engine]);

  const restartTutorial = useCallback(async () => {
    if (!activeTutorial) return;

    setIsLoading(true);
    try {
      engine.resetTutorial(activeTutorial.id);
      await startTutorial(activeTutorial.id);
    } catch (error) {
      console.error('[TutorialProvider] Failed to restart tutorial', error);
    } finally {
      setIsLoading(false);
    }
  }, [engine, activeTutorial, startTutorial]);

  const dismissTutorial = useCallback(async () => {
    if (!activeTutorial) return;

    setIsLoading(true);
    try {
      await engine.dismissTutorial(activeTutorial.id);
      setActiveTutorial(null);
      setStepIndex(0);
      setIsPaused(false);
    } catch (error) {
      console.error('[TutorialProvider] Failed to dismiss tutorial', error);
    } finally {
      setIsLoading(false);
    }
  }, [engine, activeTutorial]);

  // Listen to engine events
  useEffect(() => {
    const unsubscribes = [
      engine.on('tutorial:started', event => {
        if (event.type === 'tutorial:started') {
          const tutorial = getTutorialById(event.tutorialId);
          if (tutorial) {
            setActiveTutorial(tutorial);
            setStepIndex(0);
          }
        }
      }),
      engine.on('tutorial:completed', event => {
        if (
          event.type === 'tutorial:completed' &&
          activeTutorial?.id === event.tutorialId
        ) {
          setActiveTutorial(null);
          setStepIndex(0);
        }
      }),
      engine.on('tutorial:dismissed', event => {
        if (
          event.type === 'tutorial:dismissed' &&
          activeTutorial?.id === event.tutorialId
        ) {
          setActiveTutorial(null);
          setStepIndex(0);
        }
      }),
    ];

    return () => {
      unsubscribes.forEach(unsub => unsub());
    };
  }, [engine, activeTutorial]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      engine.destroy();
    };
  }, [engine]);

  const value: TutorialContextValue = useMemo(
    () => ({
      engine,
      activeTutorial,
      currentStep,
      stepIndex,
      isPaused,
      isLoading,
      startTutorial,
      completeStep,
      skipStep,
      nextStep,
      previousStep,
      skipTutorial,
      pauseTutorial,
      resumeTutorial,
      restartTutorial,
      dismissTutorial,
    }),
    [
      engine,
      activeTutorial,
      currentStep,
      stepIndex,
      isPaused,
      isLoading,
      startTutorial,
      completeStep,
      skipStep,
      nextStep,
      previousStep,
      skipTutorial,
      pauseTutorial,
      resumeTutorial,
      restartTutorial,
      dismissTutorial,
    ]
  );

  return (
    <TutorialContext.Provider value={value}>
      {children}
    </TutorialContext.Provider>
  );
}

export function useTutorial() {
  const context = useContext(TutorialContext);
  if (!context) {
    throw new Error('useTutorial must be used within TutorialProvider');
  }
  return context;
}
