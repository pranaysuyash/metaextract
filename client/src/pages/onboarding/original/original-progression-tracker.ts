/**
 * Original UI Progression Tracker
 * Tracks feature unlock, milestones, and achievements for Original UI
 */

import type { OnboardingProgress } from '@/lib/onboarding/onboarding-engine';

export interface ProgressionMilestone {
  id: string;
  name: string;
  description: string;
  requiredSteps: number;
  reward: string;
  unlockedFeatures: string[];
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlockedAt?: number;
}

export const ORIGINAL_MILESTONES: ProgressionMilestone[] = [
  {
    id: 'first-upload',
    name: 'First Upload',
    description: 'Upload your first file to extract metadata',
    requiredSteps: 1,
    reward: 'Explorer Badge',
    unlockedFeatures: ['basic-extraction'],
  },
  {
    id: 'gps-discovery',
    name: 'GPS Explorer',
    description: 'View GPS location data for the first time',
    requiredSteps: 4,
    reward: 'Navigator Badge',
    unlockedFeatures: ['gps-visualization'],
  },
  {
    id: 'exif-master',
    name: 'EXIF Master',
    description: 'Successfully view EXIF camera settings',
    requiredSteps: 5,
    reward: 'Photographer Badge',
    unlockedFeatures: ['advanced-exif-analysis'],
  },
  {
    id: 'forensic-beginner',
    name: 'Forensic Beginner',
    description: 'Explore advanced forensic features like metadata comparison',
    requiredSteps: 12,
    reward: 'Investigator Badge',
    unlockedFeatures: ['forensic-tools', 'metadata-comparison'],
  },
  {
    id: 'data-exporter',
    name: 'Data Exporter',
    description: 'Export metadata in at least one format',
    requiredSteps: 7,
    reward: 'Exporter Badge',
    unlockedFeatures: ['export-options', 'batch-export'],
  },
  {
    id: 'batch-processor',
    name: 'Batch Processor',
    description: 'Process multiple files in a single session',
    requiredSteps: 15,
    reward: 'Efficiency Badge',
    unlockedFeatures: ['batch-upload', 'parallel-processing'],
  },
  {
    id: 'power-user',
    name: 'Power User',
    description: 'Complete all basic tour steps and explore advanced features',
    requiredSteps: 20,
    reward: 'Power User Badge',
    unlockedFeatures: ['all-basic-features', 'advanced-features-unlocked'],
  },
];

export const ORIGINAL_ACHIEVEMENTS: Achievement[] = [
  {
    id: 'metadata-novice',
    name: 'Metadata Novice',
    description: 'Complete 1 file extraction',
    icon: '🔍',
    unlocked: false,
  },
  {
    id: 'metadata-explorer',
    name: 'Metadata Explorer',
    description: 'Complete 5 file extractions',
    icon: '🗺️',
    unlocked: false,
  },
  {
    id: 'gps-hunter',
    name: 'GPS Hunter',
    description: 'View GPS data in 10 files',
    icon: '📍',
    unlocked: false,
  },
  {
    id: 'forensic-detective',
    name: 'Forensic Detective',
    description: 'Use metadata comparison 5 times',
    icon: '🔎',
    unlocked: false,
  },
  {
    id: 'batch-master',
    name: 'Batch Master',
    description: 'Process 50 files in batch mode',
    icon: '📦',
    unlocked: false,
  },
  {
    id: 'metadata-virtuoso',
    name: 'Metadata Virtuoso',
    description: 'Extract metadata from 100 different files',
    icon: '🏆',
    unlocked: false,
  },
  {
    id: 'metaextract-expert',
    name: 'MetaExtract Expert',
    description: 'Complete all tutorials and unlock all features',
    icon: '⭐',
    unlocked: false,
  },
];

export class OriginalProgressionTracker {
  private progress: OnboardingProgress | null = null;
  private achievements: Achievement[];

  constructor(progress: OnboardingProgress | null) {
    this.progress = progress;
    this.achievements = ORIGINAL_ACHIEVEMENTS.map(a => ({
      ...a,
      unlocked: false,
    }));
    this.loadAchievements();
  }

  /**
   * Calculate completion percentage
   */
  getCompletionPercentage(): number {
    if (!this.progress) return 0;
    return (
      (this.progress.totalStepsCompleted / ORIGINAL_MILESTONES.length) * 100
    );
  }

  /**
   * Get next milestone
   */
  getNextMilestone(): ProgressionMilestone | null {
    const completedSteps = this.progress?.totalStepsCompleted ?? 0;
    return (
      ORIGINAL_MILESTONES.find(m => m.requiredSteps > completedSteps) || null
    );
  }

  /**
   * Check if milestone is complete
   */
  isMilestoneComplete(milestoneId: string): boolean {
    const milestone = ORIGINAL_MILESTONES.find(m => m.id === milestoneId);
    if (!milestone || !this.progress) return false;
    return this.progress.totalStepsCompleted >= milestone.requiredSteps;
  }

  /**
   * Update achievement status
   */
  updateAchievement(achievementId: string, unlocked: boolean): void {
    const achievement = this.achievements.find(a => a.id === achievementId);
    if (achievement) {
      achievement.unlocked = unlocked;
      achievement.unlockedAt = unlocked ? Date.now() : undefined;
      this.saveAchievements();
    }
  }

  /**
   * Get unlocked achievements
   */
  getUnlockedAchievements(): Achievement[] {
    return this.achievements.filter(a => a.unlocked);
  }

  /**
   * Get locked achievements
   */
  getLockedAchievements(): Achievement[] {
    return this.achievements.filter(a => !a.unlocked);
  }

  /**
   * Check if feature is unlocked
   */
  isFeatureUnlocked(featureId: string): boolean {
    const unlockedFeatures = new Set<string>();
    const completedSteps = this.progress?.totalStepsCompleted ?? 0;

    ORIGINAL_MILESTONES.forEach(milestone => {
      if (completedSteps >= milestone.requiredSteps) {
        milestone.unlockedFeatures.forEach(f => unlockedFeatures.add(f));
      }
    });

    return unlockedFeatures.has(featureId);
  }

  /**
   * Get recommended next tutorial
   */
  getRecommendedTutorial(): string | null {
    const completedSteps = this.progress?.totalStepsCompleted ?? 0;

    if (completedSteps === 0) {
      return 'original-basic-tour';
    } else if (completedSteps < 7) {
      return 'original-basic-tour';
    } else if (completedSteps < 20) {
      return 'original-advanced-tour';
    }

    return null;
  }

  /**
   * Load achievements from localStorage
   */
  private loadAchievements(): void {
    try {
      const stored = localStorage.getItem('original_achievements');
      if (stored) {
        this.achievements = JSON.parse(stored);
      }
    } catch (error) {
      console.error(
        '[OriginalProgressionTracker] Failed to load achievements',
        error
      );
    }
  }

  /**
   * Save achievements to localStorage
   */
  private saveAchievements(): void {
    try {
      localStorage.setItem(
        'original_achievements',
        JSON.stringify(this.achievements)
      );
    } catch (error) {
      console.error(
        '[OriginalProgressionTracker] Failed to save achievements',
        error
      );
    }
  }

  /**
   * Reset all achievements
   */
  resetAchievements(): void {
    this.achievements = ORIGINAL_ACHIEVEMENTS.map(a => ({
      ...a,
      unlocked: false,
    }));
    this.saveAchievements();
  }
}

export function createOriginalProgressionTracker(
  progress: OnboardingProgress | null
): OriginalProgressionTracker {
  return new OriginalProgressionTracker(progress);
}
