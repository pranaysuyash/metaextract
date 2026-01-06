/**
 * Onboarding Storage Tests
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
const vi = jest;
import {
  OnboardingStorage,
  LocalStorageAdapter,
  SessionStorageAdapter,
} from '@/lib/onboarding/onboarding-storage';

describe('OnboardingStorage', () => {
  let storage: OnboardingStorage;

  beforeEach(() => {
    storage = new OnboardingStorage();
    localStorage.clear();
    sessionStorage.clear();
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    vi.restoreAllMocks();
  });

  describe('progress management', () => {
    it('should get progress (null if not set)', async () => {
      const progress = await storage.getProgress('user-1', 'v2');
      expect(progress).toBeNull();
    });

    it('should set and get progress', async () => {
      const progress = {
        userId: 'user-1',
        uiVersion: 'v2',
        completedTutorials: ['tutorial-1'],
        activeTutorial: null,
        unlockedFeatures: ['feature-1'],
        totalStepsCompleted: 10,
        totalStepsSkipped: 2,
        lastUpdated: Date.now(),
      };

      await storage.setProgress('user-1', 'v2', progress);
      const retrieved = await storage.getProgress('user-1', 'v2');

      expect(retrieved).toEqual(progress);
    });

    it('should handle different users separately', async () => {
      const progress1 = {
        userId: 'user-1',
        uiVersion: 'v2' as const,
        completedTutorials: [],
        activeTutorial: null,
        unlockedFeatures: [],
        totalStepsCompleted: 0,
        totalStepsSkipped: 0,
        lastUpdated: Date.now(),
      };
      const progress2 = {
        userId: 'user-2',
        uiVersion: 'v2' as const,
        completedTutorials: ['tutorial-1'],
        activeTutorial: null,
        unlockedFeatures: [],
        totalStepsCompleted: 5,
        totalStepsSkipped: 0,
        lastUpdated: Date.now(),
      };

      await storage.setProgress('user-1', 'v2', progress1);
      await storage.setProgress('user-2', 'v2', progress2);

      const retrieved1 = await storage.getProgress('user-1', 'v2');
      const retrieved2 = await storage.getProgress('user-2', 'v2');

      expect(retrieved1?.completedTutorials).toEqual([]);
      expect(retrieved2?.completedTutorials).toEqual(['tutorial-1']);
    });
  });

  describe('active tutorial state', () => {
    it('should get active tutorial (null if not set)', async () => {
      const activeTutorial = await storage.getActiveTutorial();
      expect(activeTutorial).toBeNull();
    });

    it('should set and get active tutorial', async () => {
      const tutorialState = {
        tutorialId: 'tutorial-1',
        currentStepIndex: 2,
        status: 'active' as const,
        startTime: Date.now(),
        completedSteps: new Set<string>(['step-1', 'step-2']),
        skippedSteps: new Set<string>(),
      };

      await storage.setActiveTutorial(tutorialState);
      const retrieved = await storage.getActiveTutorial();

      expect(retrieved).not.toBeNull();
      expect(retrieved?.tutorialId).toBe('tutorial-1');
      expect(retrieved?.currentStepIndex).toBe(2);
    });

    it('should remove active tutorial when null is set', async () => {
      const tutorialState = {
        tutorialId: 'tutorial-1',
        currentStepIndex: 0,
        status: 'active' as const,
        startTime: Date.now(),
        completedSteps: new Set<string>(),
        skippedSteps: new Set<string>(),
      };

      await storage.setActiveTutorial(tutorialState);
      await storage.setActiveTutorial(null);

      const retrieved = await storage.getActiveTutorial();
      expect(retrieved).toBeNull();
    });
  });

  describe('preferences', () => {
    it('should get preference (null if not set)', async () => {
      const pref = await storage.getPreferences('user-1', 'theme');
      expect(pref).toBeNull();
    });

    it('should set and get preference', async () => {
      await storage.setPreferences('user-1', 'theme', 'dark');
      const pref = await storage.getPreferences('user-1', 'theme');
      expect(pref).toBe('dark');
    });

    it('should handle complex preference objects', async () => {
      const complexPref = {
        showTutorials: true,
        skipCount: 0,
        lastSeen: Date.now(),
      };

      await storage.setPreferences('user-1', 'onboarding', complexPref);
      const retrieved = await storage.getPreferences('user-1', 'onboarding');
      expect(retrieved).toEqual(complexPref);
    });
  });

  describe('skip preferences', () => {
    it('should get skip preference (false by default)', async () => {
      const skipped = await storage.getSkipPreferences('user-1', 'tutorial-1');
      expect(skipped).toBe(false);
    });

    it('should set skip preference to true', async () => {
      await storage.setSkipPreferences('user-1', 'tutorial-1', true);
      const skipped = await storage.getSkipPreferences('user-1', 'tutorial-1');
      expect(skipped).toBe(true);
    });

    it('should set skip preference to false', async () => {
      await storage.setSkipPreferences('user-1', 'tutorial-1', true);
      await storage.setSkipPreferences('user-1', 'tutorial-1', false);
      const skipped = await storage.getSkipPreferences('user-1', 'tutorial-1');
      expect(skipped).toBe(false);
    });
  });

  describe('cleanup', () => {
    it('should clear user session', async () => {
      await storage.setActiveTutorial({
        tutorialId: 'tutorial-1',
        currentStepIndex: 0,
        status: 'active',
        startTime: Date.now(),
        completedSteps: new Set<string>(),
        skippedSteps: new Set<string>(),
      });

      await storage.clearUserSession('user-1');

      const activeTutorial = await storage.getActiveTutorial();
      expect(activeTutorial).toBeNull();
    });
  });
});
