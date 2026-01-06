/**
 * Onboarding Events - Event bus for onboarding system
 */

import type { OnboardingEvent } from './onboarding-engine';

type EventListener = (event: OnboardingEvent) => void;
type EventUnsubscribe = () => void;

export class OnboardingEventBus {
  private listeners: Map<OnboardingEvent['type'], Set<EventListener>> =
    new Map();
  private eventHistory: OnboardingEvent[] = [];
  private maxHistorySize = 100;

  /**
   * Subscribe to an event type
   */
  on(
    eventType: OnboardingEvent['type'],
    listener: EventListener
  ): EventUnsubscribe {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(listener);

    // Return unsubscribe function
    return () => this.off(eventType, listener);
  }

  /**
   * Unsubscribe from an event type
   */
  private off(
    eventType: OnboardingEvent['type'],
    listener: EventListener
  ): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.delete(listener);
    }
  }

  /**
   * Emit an event
   */
  emit(event: OnboardingEvent): void {
    // Add to history
    this.eventHistory.push(event);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }

    // Notify listeners
    const listeners = this.listeners.get(event.type);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(event);
        } catch (error) {
          console.error(
            `[OnboardingEventBus] Error in listener for ${event.type}:`,
            error
          );
        }
      });
    }

    // Log for debugging
    console.debug('[OnboardingEventBus] Emitted:', event.type, event);
  }

  /**
   * Emit multiple events
   */
  emitBatch(events: OnboardingEvent[]): void {
    events.forEach(event => this.emit(event));
  }

  /**
   * Once - subscribe to one-time event
   */
  once(
    eventType: OnboardingEvent['type'],
    listener: EventListener
  ): EventUnsubscribe {
    const wrappedListener = (event: OnboardingEvent) => {
      if (event.type === eventType) {
        this.off(eventType, wrappedListener);
        listener(event);
      }
    };
    return this.on(eventType, wrappedListener);
  }

  /**
   * Wait for an event (promise-based)
   */
  waitFor(
    eventType: OnboardingEvent['type'],
    timeout = 5000
  ): Promise<OnboardingEvent> {
    // If the event already occurred, resolve immediately with the most recent
    const existing = this.eventHistory.find(e => e.type === eventType);
    if (existing) return Promise.resolve(existing);

    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        unsubscribe();
        reject(new Error(`Timeout waiting for event: ${eventType}`));
      }, timeout);

      const unsubscribe = this.once(eventType, (event: OnboardingEvent) => {
        clearTimeout(timeoutId);
        resolve(event);
      });
    });
  }

  /**
   * Get listener count for an event type
   */
  listenerCount(eventType: OnboardingEvent['type']): number {
    return this.listeners.get(eventType)?.size ?? 0;
  }

  /**
   * Get total listener count
   */
  totalListenerCount(): number {
    let total = 0;
    this.listeners.forEach(listeners => {
      total += listeners.size;
    });
    return total;
  }

  /**
   * Clear all listeners for an event type
   */
  clear(eventType: OnboardingEvent['type']): void {
    this.listeners.delete(eventType);
  }

  /**
   * Clear all listeners
   */
  clearAll(): void {
    this.listeners.clear();
  }

  /**
   * Get event history
   */
  getHistory(): OnboardingEvent[] {
    return [...this.eventHistory];
  }

  /**
   * Get events by type from history
   */
  getHistoryByType(eventType: OnboardingEvent['type']): OnboardingEvent[] {
    return this.eventHistory.filter(event => event.type === eventType);
  }

  /**
   * Clear event history
   */
  clearHistory(): void {
    this.eventHistory = [];
  }
}

export const onboardingEventBus = new OnboardingEventBus();

/**
 * Convenience functions for common event patterns
 */
export const emitTutorialStarted = (tutorialId: string): void => {
  onboardingEventBus.emit({ type: 'tutorial:started', tutorialId });
};

export const emitStepCompleted = (tutorialId: string, stepId: string): void => {
  onboardingEventBus.emit({ type: 'step:completed', tutorialId, stepId });
};

export const emitStepSkipped = (tutorialId: string, stepId: string): void => {
  onboardingEventBus.emit({ type: 'step:skipped', tutorialId, stepId });
};

export const emitTutorialCompleted = (
  tutorialId: string,
  duration: number
): void => {
  onboardingEventBus.emit({ type: 'tutorial:completed', tutorialId, duration });
};

export const emitTutorialDismissed = (tutorialId: string): void => {
  onboardingEventBus.emit({ type: 'tutorial:dismissed', tutorialId });
};

export const emitFeatureUnlocked = (featureId: string): void => {
  onboardingEventBus.emit({ type: 'feature:unlocked', featureId });
};

export const emitHelpViewed = (helpId: string): void => {
  onboardingEventBus.emit({ type: 'help:viewed', helpId });
};
