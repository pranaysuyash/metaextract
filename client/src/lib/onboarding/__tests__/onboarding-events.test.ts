/**
 * Onboarding Events Tests
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
const vi = jest;
import {
  OnboardingEventBus,
  onboardingEventBus,
} from '@/lib/onboarding/onboarding-events';

describe('OnboardingEventBus', () => {
  let bus: OnboardingEventBus;

  beforeEach(() => {
    bus = new OnboardingEventBus();
    vi.spyOn(console, 'debug').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    bus.clearAll();
    vi.restoreAllMocks();
  });

  describe('event subscription', () => {
    it('should subscribe to event type', () => {
      const handler = vi.fn();
      const unsubscribe = bus.on('tutorial:started', handler);

      expect(bus.listenerCount('tutorial:started')).toBe(1);

      unsubscribe();
      expect(bus.listenerCount('tutorial:started')).toBe(0);
    });

    it('should call listener when event is emitted', () => {
      const handler = vi.fn();
      bus.on('tutorial:started', handler);

      bus.emit({ type: 'tutorial:started', tutorialId: 'test-tutorial' });

      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'tutorial:started',
          tutorialId: 'test-tutorial',
        })
      );
    });

    it('should handle multiple listeners', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      bus.on('tutorial:started', handler1);
      bus.on('tutorial:started', handler2);

      bus.emit({ type: 'tutorial:started', tutorialId: 'test' });

      expect(handler1).toHaveBeenCalledTimes(1);
      expect(handler2).toHaveBeenCalledTimes(1);
    });

    it('should only call listeners of correct type', () => {
      const startedHandler = jest.fn();
      const completedHandler = jest.fn();

      bus.on('tutorial:started', startedHandler);
      bus.on('tutorial:completed', completedHandler);

      bus.emit({ type: 'tutorial:started', tutorialId: 'test' });

      expect(startedHandler).toHaveBeenCalledTimes(1);
      expect(completedHandler).not.toHaveBeenCalled();
    });

    it('should unsubscribe specific listener', () => {
      const handler1 = jest.fn();
      const handler2 = jest.fn();

      const unsub1 = bus.on('tutorial:started', handler1);
      const unsub2 = bus.on('tutorial:started', handler2);

      unsub1();

      bus.emit({ type: 'tutorial:started', tutorialId: 'test' });

      expect(handler1).not.toHaveBeenCalled();
      expect(handler2).toHaveBeenCalledTimes(1);
    });
  });

  describe('once', () => {
    it('should call listener once and unsubscribe', () => {
      const handler = jest.fn();
      bus.once('tutorial:started', handler);

      bus.emit({ type: 'tutorial:started', tutorialId: 'test1' });
      bus.emit({ type: 'tutorial:started', tutorialId: 'test2' });

      expect(handler).toHaveBeenCalledTimes(1);
    });

    it('should work with other listeners', () => {
      const onceHandler = jest.fn();
      const alwaysHandler = jest.fn();

      bus.once('tutorial:started', onceHandler);
      bus.on('tutorial:started', alwaysHandler);

      bus.emit({ type: 'tutorial:started', tutorialId: 'test1' });
      bus.emit({ type: 'tutorial:started', tutorialId: 'test2' });

      expect(onceHandler).toHaveBeenCalledTimes(1);
      expect(alwaysHandler).toHaveBeenCalledTimes(2);
    });
  });

  describe('event history', () => {
    it('should track event history', () => {
      bus.emit({ type: 'tutorial:started', tutorialId: 'test1' });
      bus.emit({
        type: 'step:completed',
        tutorialId: 'test1',
        stepId: 'step1',
      });
      bus.emit({
        type: 'tutorial:completed',
        tutorialId: 'test1',
        duration: 10,
      });

      const history = bus.getHistory();

      expect(history).toHaveLength(3);
      expect(history[0].type).toBe('tutorial:started');
      expect(history[1].type).toBe('step:completed');
      expect(history[2].type).toBe('tutorial:completed');
    });

    it('should limit history size', () => {
      const busWithLimit = new OnboardingEventBus();

      for (let i = 0; i < 150; i++) {
        busWithLimit.emit({
          type: 'tutorial:started',
          tutorialId: `test-${i}`,
        });
      }

      const history = busWithLimit.getHistory();

      expect(history.length).toBeLessThanOrEqual(100);

      busWithLimit.clearAll();
    });

    it('should filter history by type', () => {
      bus.emit({ type: 'tutorial:started', tutorialId: 'test1' });
      bus.emit({
        type: 'step:completed',
        tutorialId: 'test1',
        stepId: 'step1',
      });
      bus.emit({
        type: 'step:completed',
        tutorialId: 'test1',
        stepId: 'step2',
      });
      bus.emit({
        type: 'tutorial:completed',
        tutorialId: 'test1',
        duration: 10,
      });

      const stepEvents = bus.getHistoryByType('step:completed');

      expect(stepEvents).toHaveLength(2);
      expect(stepEvents[0].stepId).toBe('step1');
      expect(stepEvents[1].stepId).toBe('step2');
    });

    it('should clear history', () => {
      bus.emit({ type: 'tutorial:started', tutorialId: 'test1' });
      bus.emit({
        type: 'tutorial:completed',
        tutorialId: 'test1',
        duration: 10,
      });

      bus.clearHistory();

      const history = bus.getHistory();
      expect(history).toHaveLength(0);
    });
  });

  describe('waitFor', () => {
    it('should resolve when event is emitted', async () => {
      const promise = bus.waitFor('tutorial:started', 1000);

      setTimeout(() => {
        bus.emit({ type: 'tutorial:started', tutorialId: 'test' });
      }, 100);

      const event = await promise;
      expect(event.type).toBe('tutorial:started');
    });

    it('should timeout if event is not emitted', async () => {
      await expect(bus.waitFor('tutorial:started', 100)).rejects.toThrow(
        'Timeout waiting for event: tutorial:started'
      );
    });

    it('should resolve immediately if event already happened', async () => {
      bus.emit({ type: 'tutorial:started', tutorialId: 'test' });

      const event = await bus.waitFor('tutorial:started', 1000);
      expect(event.type).toBe('tutorial:started');
    });
  });

  describe('error handling', () => {
    it('should handle errors in listeners gracefully', () => {
      const errorHandler = jest.fn(() => {
        throw new Error('Test error');
      });
      const successHandler = jest.fn();

      bus.on('tutorial:started', errorHandler);
      bus.on('tutorial:started', successHandler);

      bus.emit({ type: 'tutorial:started', tutorialId: 'test' });

      expect(successHandler).toHaveBeenCalledTimes(1);
      expect(console.error).toHaveBeenCalled();
    });

    it('should log events', () => {
      bus.emit({ type: 'tutorial:started', tutorialId: 'test' });

      expect(console.debug).toHaveBeenCalledWith(
        '[OnboardingEventBus] Emitted:',
        'tutorial:started',
        expect.objectContaining({ type: 'tutorial:started' })
      );
    });
  });

  describe('emitBatch', () => {
    it('should emit multiple events', () => {
      const handler = vi.fn();
      bus.on('tutorial:started', handler);

      bus.emitBatch([
        { type: 'tutorial:started', tutorialId: 'test1' },
        { type: 'tutorial:started', tutorialId: 'test2' },
        { type: 'tutorial:started', tutorialId: 'test3' },
      ]);

      expect(handler).toHaveBeenCalledTimes(3);
    });
  });

  describe('clear', () => {
    it('should clear listeners for specific type', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      bus.on('tutorial:started', handler1);
      bus.on('tutorial:started', handler2);
      bus.on('tutorial:completed', handler1);

      bus.clear('tutorial:started');

      expect(bus.listenerCount('tutorial:started')).toBe(0);
      expect(bus.listenerCount('tutorial:completed')).toBe(1);
    });

    it('should clear all listeners', () => {
      const handler = vi.fn();

      bus.on('tutorial:started', handler);
      bus.on('tutorial:completed', handler);
      bus.on('step:completed', handler);

      bus.clearAll();

      expect(bus.totalListenerCount()).toBe(0);
    });
  });
});

describe('onboardingEventBus singleton', () => {
  beforeEach(() => {
    vi.spyOn(console, 'debug').mockImplementation(() => {});
  });

  afterEach(() => {
    onboardingEventBus.clearAll();
    vi.restoreAllMocks();
  });

  it('should be a singleton instance', () => {
    expect(onboardingEventBus).toBeInstanceOf(OnboardingEventBus);
  });

  it('should work across multiple imports', () => {
    const {
      onboardingEventBus: bus1,
    } = require('@/lib/onboarding/onboarding-events');
    const {
      onboardingEventBus: bus2,
    } = require('@/lib/onboarding/onboarding-events');

    const handler = vi.fn();
    bus1.on('tutorial:started', handler);
    bus2.emit({ type: 'tutorial:started', tutorialId: 'test' });

    expect(handler).toHaveBeenCalledTimes(1);
  });
});
