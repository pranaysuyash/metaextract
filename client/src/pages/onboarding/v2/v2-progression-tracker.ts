/**
 * V2 UI Progression Tracker
 * Lightweight progression tracking for minimalist V2 UI
 */

import type { OnboardingProgress } from '@/lib/onboarding/onboarding-engine';

export interface V2Milestone {
  id: string;
  name: string;
  description: string;
  completed: boolean;
  completedAt?: number;
}

export const V2_MILESTONES: V2Milestone[] = [
  {
    id: 'first-upload',
    name: 'First Upload',
    description: 'Upload your first file with V2',
    completed: false,
  },
  {
    id: 'five-extractions',
    name: '5 Extractions',
    description: 'Complete 5 file extractions',
    completed: false,
  },
  {
    id: 'privacy-check',
    name: 'Privacy Check',
    description: 'Review privacy data for a file',
    completed: false,
  },
  {
    id: 'download-results',
    name: 'Download Results',
    description: 'Download extraction results',
    completed: false,
  },
  {
    id: 'v2-master',
    name: 'V2 Master',
    description: 'Complete all V2 milestones',
    completed: false,
  },
];

export class V2ProgressionTracker {
  private progress: OnboardingProgress | null = null;
  private milestones: Map<string, V2Milestone>;

  constructor(progress: OnboardingProgress | null) {
    this.progress = progress;
    this.milestones = new Map(
      V2_MILESTONES.map(m => [m.id, { ...m, completed: false }])
    );
    this.loadMilestones();
  }

  /**
   * Get completion percentage
   */
  getCompletionPercentage(): number {
    const completedCount = Array.from(this.milestones.values()).filter(
      m => m.completed
    ).length;
    return (completedCount / V2_MILESTONES.length) * 100;
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
   * Get next uncompleted milestone
   */
  getNextMilestone(): V2Milestone | null {
    const uncompleted = Array.from(this.milestones.values()).filter(
      m => !m.completed
    );
    return uncompleted.length > 0 ? uncompleted[0] : null;
  }

  /**
   * Get all milestones
   */
  getAllMilestones(): V2Milestone[] {
    return Array.from(this.milestones.values());
  }

  /**
   * Get completed milestones
   */
  getCompletedMilestones(): V2Milestone[] {
    return Array.from(this.milestones.values()).filter(m => m.completed);
  }

  /**
   * Get pending milestones
   */
  getPendingMilestones(): V2Milestone[] {
    return Array.from(this.milestones.values()).filter(m => !m.completed);
  }

  /**
   * Load milestones from localStorage
   */
  private loadMilestones(): void {
    try {
      const stored = localStorage.getItem('v2_milestones');
      if (stored) {
        const loaded: V2Milestone[] = JSON.parse(stored);
        loaded.forEach(m => this.milestones.set(m.id, m));
      }
    } catch (error) {
      console.error('[V2ProgressionTracker] Failed to load milestones', error);
    }
  }

  /**
   * Save milestones to localStorage
   */
  private saveMilestones(): void {
    try {
      const data = Array.from(this.milestones.values());
      localStorage.setItem('v2_milestones', JSON.stringify(data));
    } catch (error) {
      console.error('[V2ProgressionTracker] Failed to save milestones', error);
    }
  }

  /**
   * Reset all milestones
   */
  resetMilestones(): void {
    V2_MILESTONES.forEach(m => {
      this.milestones.set(m.id, {
        ...m,
        completed: false,
        completedAt: undefined,
      });
    });
    this.saveMilestones();
  }
}

export function createV2ProgressionTracker(
  progress: OnboardingProgress | null
): V2ProgressionTracker {
  return new V2ProgressionTracker(progress);
}
