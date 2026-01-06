/**
 * Onboarding Storage - Abstraction layer for persistence
 */

import type { OnboardingProgress, TutorialState } from './onboarding-engine';

export interface StorageAdapter {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T): Promise<void>;
  remove(key: string): Promise<void>;
  clear(): Promise<void>;
}

export class LocalStorageAdapter implements StorageAdapter {
  async get<T>(key: string): Promise<T | null> {
    try {
      const item = localStorage.getItem(key);
      if (item === null) {
        return null;
      }
      return JSON.parse(item) as T;
    } catch (error) {
      console.error(
        '[OnboardingStorage] Failed to get from localStorage',
        error
      );
      return null;
    }
  }

  async set<T>(key: string, value: T): Promise<void> {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('[OnboardingStorage] Failed to set to localStorage', error);
      throw new Error('Storage quota exceeded or storage disabled');
    }
  }

  async remove(key: string): Promise<void> {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(
        '[OnboardingStorage] Failed to remove from localStorage',
        error
      );
    }
  }

  async clear(): Promise<void> {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('[OnboardingStorage] Failed to clear localStorage', error);
    }
  }
}

export class SessionStorageAdapter implements StorageAdapter {
  async get<T>(key: string): Promise<T | null> {
    try {
      const item = sessionStorage.getItem(key);
      if (item === null) {
        return null;
      }
      return JSON.parse(item) as T;
    } catch (error) {
      console.error(
        '[OnboardingStorage] Failed to get from sessionStorage',
        error
      );
      return null;
    }
  }

  async set<T>(key: string, value: T): Promise<void> {
    try {
      sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(
        '[OnboardingStorage] Failed to set to sessionStorage',
        error
      );
      throw new Error('Storage quota exceeded or storage disabled');
    }
  }

  async remove(key: string): Promise<void> {
    try {
      sessionStorage.removeItem(key);
    } catch (error) {
      console.error(
        '[OnboardingStorage] Failed to remove from sessionStorage',
        error
      );
    }
  }

  async clear(): Promise<void> {
    try {
      sessionStorage.clear();
    } catch (error) {
      console.error(
        '[OnboardingStorage] Failed to clear sessionStorage',
        error
      );
    }
  }
}

export class OnboardingStorage {
  private localStorage: LocalStorageAdapter;
  private sessionStorage: SessionStorageAdapter;

  constructor() {
    this.localStorage = new LocalStorageAdapter();
    this.sessionStorage = new SessionStorageAdapter();
  }

  /**
   * Get onboarding progress (persistent)
   */
  async getProgress(
    userId: string,
    uiVersion: string
  ): Promise<OnboardingProgress | null> {
    const key = `onboarding_${userId}_${uiVersion}`;
    return this.localStorage.get<OnboardingProgress>(key);
  }

  async setProgress(
    userId: string,
    uiVersion: string,
    progress: OnboardingProgress
  ): Promise<void> {
    const key = `onboarding_${userId}_${uiVersion}`;
    return this.localStorage.set(key, progress);
  }

  /**
   * Get active tutorial state (session-only)
   */
  async getActiveTutorial(): Promise<TutorialState | null> {
    return this.sessionStorage.get<TutorialState>('active_tutorial');
  }

  async setActiveTutorial(state: TutorialState | null): Promise<void> {
    if (state === null) {
      return this.sessionStorage.remove('active_tutorial');
    }
    return this.sessionStorage.set('active_tutorial', state);
  }

  /**
   * User preferences (persistent)
   */
  async getPreferences<T>(userId: string, key: string): Promise<T | null> {
    const storageKey = `onboarding_prefs_${userId}_${key}`;
    return this.localStorage.get<T>(storageKey);
  }

  async setPreferences<T>(
    userId: string,
    key: string,
    value: T
  ): Promise<void> {
    const storageKey = `onboarding_prefs_${userId}_${key}`;
    return this.localStorage.set(storageKey, value);
  }

  /**
   * Skip preferences (persistent)
   */
  async getSkipPreferences(
    userId: string,
    tutorialId: string
  ): Promise<boolean> {
    const key = `onboarding_skip_${userId}_${tutorialId}`;
    const value = await this.localStorage.get<string>(key);
    return value === 'true';
  }

  async setSkipPreferences(
    userId: string,
    tutorialId: string,
    skipped: boolean
  ): Promise<void> {
    const key = `onboarding_skip_${userId}_${tutorialId}`;
    return this.localStorage.set(key, skipped ? 'true' : 'false');
  }

  /**
   * Cleanup
   */
  async clearUserSession(userId: string): Promise<void> {
    await this.sessionStorage.remove('active_tutorial');
  }

  async clearAllUser(userId: string): Promise<void> {
    // In a real implementation, we'd need to track all keys for this user
    // For now, this is a placeholder
    await this.sessionStorage.clear();
  }
}

export const onboardingStorage = new OnboardingStorage();
