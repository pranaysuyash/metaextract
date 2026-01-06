/**
 * Onboarding Engine - Core state management for intelligent user onboarding
 */

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  target?: string; // CSS selector for element
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  action?: 'click' | 'type' | 'select' | 'wait';
  actionTarget?: string;
  prerequisite?: string[];
  skippable: boolean;
  duration?: number; // seconds
}

export interface OnboardingTutorial {
  id: string;
  name: string;
  description: string;
  uiVersion: 'original' | 'v2' | 'images-mvp';
  steps: OnboardingStep[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedDuration: number; // minutes
}

export interface TutorialState {
  tutorialId: string | null;
  currentStepIndex: number;
  status: 'idle' | 'active' | 'paused' | 'completed' | 'dismissed';
  startTime: number | null;
  completedSteps: Set<string>;
  skippedSteps: Set<string>;
  totalSteps: number;
}

export interface OnboardingProgress {
  userId: string;
  uiVersion: string;
  completedTutorials: string[];
  activeTutorial: TutorialState | null;
  unlockedFeatures: string[];
  totalStepsCompleted: number;
  totalStepsSkipped: number;
  lastUpdated: number;
}

export type OnboardingEvent =
  | { type: 'tutorial:started'; tutorialId: string }
  | { type: 'step:completed'; tutorialId: string; stepId: string }
  | { type: 'step:skipped'; tutorialId: string; stepId: string }
  | { type: 'tutorial:completed'; tutorialId: string; duration: number }
  | { type: 'tutorial:dismissed'; tutorialId: string }
  | { type: 'feature:unlocked'; featureId: string }
  | { type: 'help:viewed'; helpId: string }
  | { type: 'progress:updated'; progress: OnboardingProgress };

type EventListener = (event: OnboardingEvent) => void;

export class OnboardingEngine {
  private userId: string;
  private uiVersion: 'original' | 'v2' | 'images-mvp';
  private listeners: Map<OnboardingEvent['type'], EventListener[]> = new Map();
  private currentState: OnboardingProgress | null = null;

  constructor(userId: string, uiVersion: 'original' | 'v2' | 'images-mvp') {
    this.userId = userId;
    this.uiVersion = uiVersion;
    this.loadState();
  }

  /**
   * Event subscription
   */
  on(eventType: OnboardingEvent['type'], listener: EventListener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)!.push(listener);
    return () => this.off(eventType, listener);
  }

  private off(
    eventType: OnboardingEvent['type'],
    listener: EventListener
  ): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  private emit(event: OnboardingEvent): void {
    const listeners = this.listeners.get(event.type);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(event);
        } catch (err) {
          // Ensure a misbehaving listener doesn't break engine flow
          console.error('[OnboardingEngine] Listener error', err);
        }
      });
    }
  }

  /**
   * State management
   */
  private loadState(): void {
    const stored = localStorage.getItem(
      `onboarding_${this.userId}_${this.uiVersion}`
    );
    if (stored) {
      try {
        // Parse and normalize persisted state. We need to convert any array
        // representations of sets back into Set instances so the runtime
        // behaves consistently across sessions and during tests.
        const parsed = JSON.parse(stored) as OnboardingProgress;

        if (parsed.activeTutorial) {
          const at = parsed.activeTutorial as any;
          if (Array.isArray(at.completedSteps)) {
            at.completedSteps = new Set(at.completedSteps);
          }
          if (Array.isArray(at.skippedSteps)) {
            at.skippedSteps = new Set(at.skippedSteps);
          }
        }

        this.currentState = parsed;
      } catch (error) {
        console.error('[OnboardingEngine] Failed to load state', error);
        this.initializeState();
      }
    } else {
      this.initializeState();
    }
  }

  private saveState(): void {
    if (this.currentState) {
      // Convert Sets to arrays for JSON serialization
      const serializable = JSON.parse(JSON.stringify(this.currentState));

      if (serializable.activeTutorial) {
        if (this.currentState.activeTutorial?.completedSteps instanceof Set) {
          serializable.activeTutorial.completedSteps = Array.from(
            this.currentState.activeTutorial.completedSteps
          );
        }
        if (this.currentState.activeTutorial?.skippedSteps instanceof Set) {
          serializable.activeTutorial.skippedSteps = Array.from(
            this.currentState.activeTutorial.skippedSteps
          );
        }
      }

      localStorage.setItem(
        `onboarding_${this.userId}_${this.uiVersion}`,
        JSON.stringify(serializable)
      );
      this.emit({ type: 'progress:updated', progress: this.currentState });
    }
  }

  private initializeState(): void {
    this.currentState = {
      userId: this.userId,
      uiVersion: this.uiVersion,
      completedTutorials: [],
      activeTutorial: null,
      unlockedFeatures: [],
      totalStepsCompleted: 0,
      totalStepsSkipped: 0,
      lastUpdated: Date.now(),
    };
    this.saveState();
  }

  /**
   * Tutorial management
   */
  async startTutorial(tutorial: OnboardingTutorial): Promise<void> {
    if (!this.currentState) {
      this.initializeState();
    }

    const activeState: TutorialState = {
      tutorialId: tutorial.id,
      currentStepIndex: 0,
      status: 'active',
      startTime: Date.now(),
      completedSteps: new Set(),
      skippedSteps: new Set(),
      totalSteps: tutorial.steps.length,
    };

    this.currentState!.activeTutorial = activeState;
    this.saveState();
    this.emit({ type: 'tutorial:started', tutorialId: tutorial.id });
  }

  async completeStep(tutorialId: string, stepId: string): Promise<void> {
    if (!this.currentState?.activeTutorial) {
      return;
    }

    this.currentState.activeTutorial.completedSteps.add(stepId);
    this.currentState.activeTutorial.currentStepIndex++;
    this.currentState.totalStepsCompleted++;
    this.currentState.lastUpdated = Date.now();

    // If we've completed all expected steps, auto-complete the tutorial
    const total = this.currentState.activeTutorial.totalSteps;
    if (
      typeof total === 'number' &&
      this.currentState.activeTutorial.completedSteps.size >= total
    ) {
      await this.completeTutorial(tutorialId);
      return;
    }

    this.saveState();
    this.emit({ type: 'step:completed', tutorialId, stepId });
  }

  async skipStep(tutorialId: string, stepId: string): Promise<void> {
    if (!this.currentState?.activeTutorial) {
      return;
    }

    this.currentState.activeTutorial.skippedSteps.add(stepId);
    this.currentState.activeTutorial.currentStepIndex++;
    this.currentState.totalStepsSkipped++;
    this.currentState.lastUpdated = Date.now();

    this.saveState();
    this.emit({ type: 'step:skipped', tutorialId, stepId });
  }

  async completeTutorial(tutorialId: string): Promise<void> {
    if (!this.currentState?.activeTutorial) {
      return;
    }

    const duration = this.currentState.activeTutorial.startTime
      ? (Date.now() - this.currentState.activeTutorial.startTime) / 1000
      : 0;

    this.currentState.completedTutorials.push(tutorialId);
    this.currentState.activeTutorial = null;
    this.currentState.lastUpdated = Date.now();

    this.saveState();
    this.emit({ type: 'tutorial:completed', tutorialId, duration });
  }

  async dismissTutorial(tutorialId: string): Promise<void> {
    if (!this.currentState?.activeTutorial) {
      return;
    }

    this.currentState.activeTutorial.status = 'dismissed';
    this.currentState.activeTutorial = null;
    this.currentState.lastUpdated = Date.now();

    this.saveState();
    this.emit({ type: 'tutorial:dismissed', tutorialId });
  }

  pauseTutorial(): void {
    if (this.currentState?.activeTutorial) {
      this.currentState.activeTutorial.status = 'paused';
      this.saveState();
    }
  }

  resumeTutorial(): void {
    if (this.currentState?.activeTutorial) {
      this.currentState.activeTutorial.status = 'active';
      this.saveState();
    }
  }

  /**
   * Feature management
   */
  unlockFeature(featureId: string): void {
    if (!this.currentState) {
      this.initializeState();
    }

    if (!this.currentState!.unlockedFeatures.includes(featureId)) {
      this.currentState!.unlockedFeatures.push(featureId);
      this.saveState();
      this.emit({ type: 'feature:unlocked', featureId });
    }
  }

  isFeatureUnlocked(featureId: string): boolean {
    return this.currentState?.unlockedFeatures.includes(featureId) ?? false;
  }

  /**
   * Progress queries
   */
  getProgress(): OnboardingProgress | null {
    return this.currentState;
  }

  isActiveTutorial(tutorialId: string): boolean {
    return this.currentState?.activeTutorial?.tutorialId === tutorialId;
  }

  isTutorialCompleted(tutorialId: string): boolean {
    return this.currentState?.completedTutorials.includes(tutorialId) ?? false;
  }

  getCompletionRate(): number {
    if (!this.currentState) {
      return 0;
    }

    const total =
      this.currentState.totalStepsCompleted +
      this.currentState.totalStepsSkipped;
    if (total === 0) {
      return 0;
    }

    return (this.currentState.totalStepsCompleted / total) * 100;
  }

  /**
   * Reset and cleanup
   */
  resetProgress(): void {
    this.initializeState();
  }

  resetTutorial(tutorialId: string): void {
    if (this.currentState?.completedTutorials.includes(tutorialId)) {
      this.currentState.completedTutorials =
        this.currentState.completedTutorials.filter(id => id !== tutorialId);
      this.saveState();
    }
  }

  destroy(): void {
    this.listeners.clear();
    this.currentState = null;
  }
}
