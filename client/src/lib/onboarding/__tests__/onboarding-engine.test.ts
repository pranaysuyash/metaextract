/**
 * Onboarding Tests - Unit tests for onboarding system
 */

// Use Jest globals in test environment
const vi = jest;
import { OnboardingEngine } from '@/lib/onboarding/onboarding-engine';
import type {
  OnboardingTutorial,
  OnboardingStep,
} from '@/lib/onboarding/onboarding-engine';

describe('OnboardingEngine', () => {
  let engine: OnboardingEngine;
  const testUserId = 'test-user-123';
  const testUIVersion = 'v2' as const;

  const mockTutorial: OnboardingTutorial = {
    id: 'test-tutorial',
    name: 'Test Tutorial',
    description: 'A test tutorial',
    uiVersion: 'v2',
    difficulty: 'beginner',
    estimatedDuration: 5,
    steps: [
      {
        id: 'step-1',
        title: 'Step 1',
        description: 'First step',
        skippable: false,
      },
      {
        id: 'step-2',
        title: 'Step 2',
        description: 'Second step',
        skippable: true,
      },
      {
        id: 'step-3',
        title: 'Step 3',
        description: 'Third step',
        skippable: true,
      },
    ],
  };

  beforeEach(() => {
    // Ensure a clean localStorage before constructing engine
    localStorage.clear();
    engine = new OnboardingEngine(testUserId, testUIVersion);
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    engine.destroy();
    vi.restoreAllMocks();
  });

  describe('initialization', () => {
    it('should initialize with empty state', () => {
      const progress = engine.getProgress();

      expect(progress).not.toBeNull();
      expect(progress?.userId).toBe(testUserId);
      expect(progress?.uiVersion).toBe(testUIVersion);
      expect(progress?.completedTutorials).toEqual([]);
      expect(progress?.activeTutorial).toBeNull();
    });

    it('should load existing state from localStorage', () => {
      const existingState = {
        userId: testUserId,
        uiVersion: testUIVersion,
        completedTutorials: ['previous-tutorial'],
        activeTutorial: null,
        unlockedFeatures: ['feature-1'],
        totalStepsCompleted: 10,
        totalStepsSkipped: 2,
        lastUpdated: Date.now(),
      };

      localStorage.setItem(
        `onboarding_${testUserId}_${testUIVersion}`,
        JSON.stringify(existingState)
      );

      const newEngine = new OnboardingEngine(testUserId, testUIVersion);
      const progress = newEngine.getProgress();

      expect(progress?.completedTutorials).toEqual(['previous-tutorial']);
      expect(progress?.unlockedFeatures).toEqual(['feature-1']);
      expect(progress?.totalStepsCompleted).toBe(10);

      newEngine.destroy();
    });
  });

  describe('tutorial management', () => {
    it('should start a tutorial', async () => {
      await engine.startTutorial(mockTutorial);

      const progress = engine.getProgress();

      expect(progress?.activeTutorial).not.toBeNull();
      expect(progress?.activeTutorial?.tutorialId).toBe(mockTutorial.id);
      expect(progress?.activeTutorial?.status).toBe('active');
      expect(progress?.activeTutorial?.startTime).not.toBeNull();
    });

    it('should emit tutorial:started event', async () => {
      const handler = vi.fn();
      engine.on('tutorial:started', handler);

      await engine.startTutorial(mockTutorial);

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'tutorial:started',
          tutorialId: mockTutorial.id,
        })
      );
    });

    it('should complete a step', async () => {
      await engine.startTutorial(mockTutorial);
      await engine.completeStep(mockTutorial.id, 'step-1');

      const progress = engine.getProgress();

      expect(progress?.activeTutorial?.completedSteps.has('step-1')).toBe(true);
      expect(progress?.activeTutorial?.currentStepIndex).toBe(1);
      expect(progress?.totalStepsCompleted).toBe(1);
    });

    it('should emit step:completed event', async () => {
      const handler = vi.fn();
      await engine.startTutorial(mockTutorial);
      engine.on('step:completed', handler);

      await engine.completeStep(mockTutorial.id, 'step-1');

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'step:completed',
          tutorialId: mockTutorial.id,
          stepId: 'step-1',
        })
      );
    });

    it('should skip a step', async () => {
      await engine.startTutorial(mockTutorial);
      await engine.skipStep(mockTutorial.id, 'step-2');

      const progress = engine.getProgress();

      expect(progress?.activeTutorial?.skippedSteps.has('step-2')).toBe(true);
      expect(progress?.totalStepsSkipped).toBe(1);
    });

    it('should emit step:skipped event', async () => {
      const handler = vi.fn();
      await engine.startTutorial(mockTutorial);
      engine.on('step:skipped', handler);

      await engine.skipStep(mockTutorial.id, 'step-2');

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'step:skipped',
          tutorialId: mockTutorial.id,
          stepId: 'step-2',
        })
      );
    });

    it('should complete tutorial after last step', async () => {
      await engine.startTutorial(mockTutorial);
      await engine.completeStep(mockTutorial.id, 'step-1');
      await engine.completeStep(mockTutorial.id, 'step-2');
      await engine.completeStep(mockTutorial.id, 'step-3');

      const progress = engine.getProgress();

      expect(progress?.completedTutorials).toContain(mockTutorial.id);
      expect(progress?.activeTutorial).toBeNull();
    });

    it('should emit tutorial:completed event', async () => {
      const handler = vi.fn();
      engine.on('tutorial:completed', handler);

      await engine.startTutorial(mockTutorial);
      await engine.completeStep(mockTutorial.id, 'step-1');
      await engine.completeStep(mockTutorial.id, 'step-2');
      await engine.completeStep(mockTutorial.id, 'step-3');

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'tutorial:completed',
          tutorialId: mockTutorial.id,
        })
      );
    });

    it('should dismiss tutorial', async () => {
      await engine.startTutorial(mockTutorial);
      await engine.dismissTutorial(mockTutorial.id);

      const progress = engine.getProgress();

      expect(progress?.activeTutorial).toBeNull();
    });

    it('should emit tutorial:dismissed event', async () => {
      const handler = vi.fn();
      await engine.startTutorial(mockTutorial);
      engine.on('tutorial:dismissed', handler);

      await engine.dismissTutorial(mockTutorial.id);

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'tutorial:dismissed',
          tutorialId: mockTutorial.id,
        })
      );
    });

    it('should pause tutorial', async () => {
      await engine.startTutorial(mockTutorial);
      engine.pauseTutorial();

      const progress = engine.getProgress();

      expect(progress?.activeTutorial?.status).toBe('paused');
    });

    it('should resume tutorial', async () => {
      await engine.startTutorial(mockTutorial);
      engine.pauseTutorial();
      engine.resumeTutorial();

      const progress = engine.getProgress();

      expect(progress?.activeTutorial?.status).toBe('active');
    });
  });

  describe('feature management', () => {
    it('should unlock feature', () => {
      engine.unlockFeature('test-feature');

      expect(engine.isFeatureUnlocked('test-feature')).toBe(true);
    });

    it('should emit feature:unlocked event', () => {
      const handler = vi.fn();
      engine.on('feature:unlocked', handler);

      engine.unlockFeature('test-feature');

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'feature:unlocked',
          featureId: 'test-feature',
        })
      );
    });

    it('should not unlock feature twice', () => {
      const handler = vi.fn();
      engine.on('feature:unlocked', handler);

      engine.unlockFeature('test-feature');
      engine.unlockFeature('test-feature');

      expect(handler).toHaveBeenCalledTimes(1);
    });

    it('should return false for locked features', () => {
      expect(engine.isFeatureUnlocked('non-existent')).toBe(false);
    });
  });

  describe('progress queries', () => {
    it('should return current progress', () => {
      const progress = engine.getProgress();

      expect(progress).not.toBeNull();
      expect(progress).toHaveProperty('userId');
      expect(progress).toHaveProperty('uiVersion');
    });

    it('should check if tutorial is active', async () => {
      expect(engine.isActiveTutorial('test-tutorial')).toBe(false);

      await engine.startTutorial(mockTutorial);

      expect(engine.isActiveTutorial('test-tutorial')).toBe(true);
    });

    it('should check if tutorial is completed', async () => {
      expect(engine.isTutorialCompleted('test-tutorial')).toBe(false);

      await engine.startTutorial(mockTutorial);
      await engine.completeStep(mockTutorial.id, 'step-1');
      await engine.completeStep(mockTutorial.id, 'step-2');
      await engine.completeStep(mockTutorial.id, 'step-3');

      expect(engine.isTutorialCompleted('test-tutorial')).toBe(true);
    });

    it('should calculate completion rate', async () => {
      expect(engine.getCompletionRate()).toBe(0);

      await engine.startTutorial(mockTutorial);
      await engine.completeStep(mockTutorial.id, 'step-1');
      await engine.skipStep(mockTutorial.id, 'step-2');

      expect(engine.getCompletionRate()).toBe(50); // 1 completed, 1 skipped = 50%
    });
  });

  describe('reset', () => {
    it('should reset all progress', async () => {
      await engine.startTutorial(mockTutorial);
      await engine.completeStep(mockTutorial.id, 'step-1');
      engine.unlockFeature('test-feature');

      engine.resetProgress();

      const progress = engine.getProgress();

      expect(progress?.completedTutorials).toEqual([]);
      expect(progress?.activeTutorial).toBeNull();
      expect(progress?.unlockedFeatures).toEqual([]);
      expect(engine.isFeatureUnlocked('test-feature')).toBe(false);
    });

    it('should reset specific tutorial', async () => {
      await engine.startTutorial(mockTutorial);
      await engine.completeStep(mockTutorial.id, 'step-1');
      await engine.completeStep(mockTutorial.id, 'step-2');
      await engine.completeStep(mockTutorial.id, 'step-3');

      engine.resetTutorial('test-tutorial');

      expect(engine.isTutorialCompleted('test-tutorial')).toBe(false);
    });
  });

  describe('event management', () => {
    it('should subscribe and unsubscribe from events', () => {
      const handler = vi.fn();
      const unsubscribe = engine.on('tutorial:started', handler);

      expect(engine['listeners'].get('tutorial:started')).toContain(handler);

      unsubscribe();

      expect(engine['listeners'].get('tutorial:started')).not.toContain(
        handler
      );
    });

    it('should handle multiple listeners', async () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      engine.on('tutorial:started', handler1);
      engine.on('tutorial:started', handler2);

      await engine.startTutorial(mockTutorial);

      expect(handler1).toHaveBeenCalledTimes(1);
      expect(handler2).toHaveBeenCalledTimes(1);
    });

    it('should handle errors in listeners gracefully', async () => {
      const errorHandler = vi.fn(() => {
        throw new Error('Listener error');
      });
      const successHandler = vi.fn();

      engine.on('tutorial:started', errorHandler);
      engine.on('tutorial:started', successHandler);

      await engine.startTutorial(mockTutorial);

      expect(successHandler).toHaveBeenCalledTimes(1);
      expect(console.error).toHaveBeenCalled();
    });
  });
});
