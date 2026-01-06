/**
 * Images MVP Progression Tracker
 * Purpose-based progression tracking for Images MVP
 */

import type { OnboardingProgress } from '@/lib/onboarding/onboarding-engine';

export type ImagesPurpose = 'privacy' | 'photography' | 'authenticity';

export interface ImagesMilestone {
  id: string;
  purpose: ImagesPurpose;
  name: string;
  description: string;
  completed: boolean;
  completedAt?: number;
}

export const IMAGES_MILESTONES: ImagesMilestone[] = [
  {
    id: 'privacy-first-check',
    purpose: 'privacy',
    name: 'First Privacy Check',
    description: 'Complete your first privacy check',
    completed: false,
  },
  {
    id: 'privacy-cleaned',
    purpose: 'privacy',
    name: 'Cleaned 10 Photos',
    description: 'Clean metadata from 10 photos',
    completed: false,
  },
  {
    id: 'photo-analyzed',
    purpose: 'photography',
    name: 'Analyzed Settings',
    description: 'Review camera settings for a photo',
    completed: false,
  },
  {
    id: 'photo-learned',
    purpose: 'photography',
    name: 'Learned from Settings',
    description: 'Understand what your settings reveal about your technique',
    completed: false,
  },
  {
    id: 'auth-verified',
    purpose: 'authenticity',
    name: 'Verified Authenticity',
    description: 'Check authenticity of a photo',
    completed: false,
  },
  {
    id: 'auth-compared',
    purpose: 'authenticity',
    name: 'Compared Metadata',
    description: 'Compare embedded vs burned-in metadata',
    completed: false,
  },
];

export class ImagesProgressionTracker {
  private progress: OnboardingProgress | null = null;
  private milestones: Map<string, ImagesMilestone>;
  private currentPurpose: ImagesPurpose | null = null;

  constructor(progress: OnboardingProgress | null) {
    this.progress = progress;
    this.milestones = new Map(
      IMAGES_MILESTONES.map(m => [m.id, { ...m, completed: false }])
    );
    this.loadMilestones();
  }

  /**
   * Set current purpose
   */
  setPurpose(purpose: ImagesPurpose): void {
    this.currentPurpose = purpose;
  }

  /**
   * Get completion percentage for purpose
   */
  getCompletionPercentage(purpose: ImagesPurpose): number {
    const purposeMilestones = Array.from(this.milestones.values()).filter(
      m => m.purpose === purpose
    );
    const completedCount = purposeMilestones.filter(m => m.completed).length;
    return purposeMilestones.length > 0
      ? (completedCount / purposeMilestones.length) * 100
      : 0;
  }

  /**
   * Mark milestone complete
   */
  completeMilestone(milestoneId: string): void {
    const milestone = this.milestones.get(milestoneId);
    if (milestone) {
      milestone.completed = true;
      milestone.completedAt = Date.now();
      this.saveMilestones();
    }
  }

  /**
   * Check if milestone is complete
   */
  isMilestoneComplete(milestoneId: string): boolean {
    const milestone = this.milestones.get(milestoneId);
    return milestone?.completed ?? false;
  }

  /**
   * Get next uncompleted milestone for purpose
   */
  getNextMilestone(purpose: ImagesPurpose): ImagesMilestone | null {
    const uncompleted = Array.from(this.milestones.values()).filter(
      m => m.purpose === purpose && !m.completed
    );
    return uncompleted.length > 0 ? uncompleted[0] : null;
  }

  /**
   * Get all milestones for purpose
   */
  getMilestonesByPurpose(purpose: ImagesPurpose): ImagesMilestone[] {
    return Array.from(this.milestones.values()).filter(
      m => m.purpose === purpose
    );
  }

  /**
   * Get recommended tutorial based on current state
   */
  getRecommendedTutorial(): string | null {
    const completedSteps = this.progress?.totalStepsCompleted ?? 0;

    if (completedSteps === 0) {
      return 'images-privacy-tour';
    } else if (completedSteps < 5) {
      return 'images-photography-tour';
    } else if (completedSteps < 10) {
      return 'images-authenticity-tour';
    }

    return null;
  }

  /**
   * Load milestones from localStorage
   */
  private loadMilestones(): void {
    try {
      const stored = localStorage.getItem('images_mvp_milestones');
      if (stored) {
        const loaded: ImagesMilestone[] = JSON.parse(stored);
        loaded.forEach(m => this.milestones.set(m.id, m));
      }
    } catch (error) {
      console.error(
        '[ImagesProgressionTracker] Failed to load milestones',
        error
      );
    }
  }

  /**
   * Save milestones to localStorage
   */
  private saveMilestones(): void {
    try {
      const data = Array.from(this.milestones.values());
      localStorage.setItem('images_mvp_milestones', JSON.stringify(data));
    } catch (error) {
      console.error(
        '[ImagesProgressionTracker] Failed to save milestones',
        error
      );
    }
  }

  /**
   * Reset all milestones
   */
  resetMilestones(): void {
    IMAGES_MILESTONES.forEach(m => {
      this.milestones.set(m.id, {
        ...m,
        completed: false,
        completedAt: undefined,
      });
    });
    this.saveMilestones();
  }
}

export function createImagesProgressionTracker(
  progress: OnboardingProgress | null
): ImagesProgressionTracker {
  return new ImagesProgressionTracker(progress);
}
