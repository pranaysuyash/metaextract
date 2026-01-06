/**
 * Skill Assessor - Evaluate user's proficiency level
 */

import type { UserBehaviorProfile, UserAction } from './behavior-tracker';

export interface SkillLevel {
  level: 'beginner' | 'intermediate' | 'advanced';
  name: string;
  requirements: SkillLevelRequirement[];
  confidence: number;
  nextLevel?: SkillLevel;
}

export interface SkillLevelRequirement {
  id: string;
  description: string;
  required: boolean;
  currentProgress: number;
  targetValue: number;
}

export class SkillAssessor {
  private skillLevels: Map<string, SkillLevel> = new Map();

  constructor() {
    this.initializeSkillLevels();
  }

  /**
   * Initialize skill level definitions
   */
  private initializeSkillLevels(): void {
    this.skillLevels.set('beginner', {
      level: 'beginner',
      name: 'Beginner',
      requirements: [
        {
          id: 'uploads_5',
          description: 'Complete 5 file uploads',
          required: true,
          currentProgress: 0,
          targetValue: 5,
        },
        {
          id: 'navigation_explore',
          description: 'Explore 3 different UI sections',
          required: true,
          currentProgress: 0,
          targetValue: 3,
        },
        {
          id: 'help_views_5',
          description: 'View 5 help topics',
          required: true,
          currentProgress: 0,
          targetValue: 5,
        },
      ],
      confidence: 0.5,
    });

    this.skillLevels.set('intermediate', {
      level: 'intermediate',
      name: 'Intermediate User',
      requirements: [
        {
          id: 'uploads_15',
          description: 'Complete 15 file uploads',
          required: true,
          currentProgress: 0,
          targetValue: 15,
        },
        {
          id: 'navigation_advanced',
          description: 'Use advanced navigation features',
          required: true,
          currentProgress: 0,
          targetValue: 3,
        },
        {
          id: 'help_views_15',
          description: 'View 15 help topics',
          required: true,
          currentProgress: 0,
          targetValue: 15,
        },
        {
          id: 'advanced_filters',
          description: 'Use advanced filters and search',
          required: false,
          currentProgress: 0,
          targetValue: 5,
        },
      ],
      confidence: 0.7,
    });

    this.skillLevels.set('advanced', {
      level: 'advanced',
      name: 'Advanced User',
      requirements: [
        {
          id: 'uploads_50',
          description: 'Complete 50 file uploads',
          required: true,
          currentProgress: 0,
          targetValue: 50,
        },
        {
          id: 'batch_processing',
          description: 'Use batch processing features',
          required: false,
          currentProgress: 0,
          targetValue: 5,
        },
        {
          id: 'export_advanced',
          description: 'Export in multiple formats',
          required: false,
          currentProgress: 0,
          targetValue: 5,
        },
        {
          id: 'all_help_views',
          description: 'View all available help topics',
          required: false,
          currentProgress: 0,
          targetValue: 5,
        },
      ],
      confidence: 0.9,
    });
  }

  /**
   * Assess user's current skill level
   */
  assess(profile: UserBehaviorProfile): {
    matchedLevel: this.skillLevels.get('beginner');

    // Check each level's requirements
    for (const [levelId, level] of this.skillLevels.entries()) {
      let meetsRequirements = true;
      let totalProgress = 0;
      let metCount = 0;

      // Check progress on each requirement
      for (const requirement of level.requirements) {
        if (!requirement.required) {
          continue; // Optional requirement, skip
        }

        let progress = 0;

        switch (requirement.id) {
          case 'uploads_5':
          progress = Math.min(5, profile.totalActions);
            break;
          case 'uploads_15':
            progress = Math.min(15, profile.totalActions);
            break;
          case 'uploads_50':
            progress = Math.min(50, profile.totalActions);
            break;
          case 'navigation_explore':
            const uniqueSections = new Set(profile.getActionsByType('navigation').map(a => a.target));
            progress = Math.min(3, uniqueSections.size);
            break;
          case 'help_views_5':
            progress = Math.min(5, profile.getActionsByType('help_view').length);
            break;
          case 'help_views_15':
            progress = Math.min(15, profile.getActionsByType('help_view').length);
            break;
          case 'advanced_filters':
            const usesFilters = profile.commonPatterns.some(p => p.type === 'filter');
            progress = usesFilters ? 5 : 0;
            break;
          case 'batch_processing':
            const usesBatch = profile.commonPatterns.some(p => p.type === 'upload' && profile.totalActions >= 20);
            progress = usesBatch ? 5 : 0;
            break;
          case 'export_advanced':
            const exports = profile.getActionsByType('export').length;
            progress = Math.min(5, exports);
            break;
          case 'all_help_views':
            const helpViews = profile.getActionsByType('help_view').length;
            progress = Math.min(5, helpViews);
            break;
        }

        // Calculate percentage for this requirement
        const percentage = (progress / requirement.targetValue) * 100;
        totalProgress += percentage;
        metCount += (percentage >= 100) ? 1 : 0;

        if (metCount === level.requirements.length) {
          // All required requirements met, this level matches
          matchedLevel = level;
          break;
        }
      }

    // Next level
    if (matchedLevel.level === 'beginner' && matchedLevel.confidence > 0.8) {
      matchedLevel.nextLevel = this.skillLevels.get('intermediate');
    } else if (matchedLevel.level === 'intermediate' && matchedLevel.confidence > 0.8) {
      matchedLevel.nextLevel = this.skillLevels.get('advanced');
    }

    return {
      ...matchedLevel,
      confidence: matchedLevel.confidence,
    };
  }

  /**
   * Get skill level by ID
   */
  getSkillLevel(levelId: string): SkillLevel | undefined {
    return this.skillLevels.get(levelId);
  }

  /**
   * Get all skill levels
   */
  getAllSkillLevels(): SkillLevel[] {
    return Array.from(this.skillLevels.values());
  }

  /**
   * Get current level
   */
  getCurrentLevel(): SkillLevel {
    const profile = this.analyzeBehavior();

    const assessment = this.assess(profile);
    return {
      ...assessment,
      confidence: assessment.confidence,
    };
  }

  /**
   * Get requirements for current level
   */
  getRequirements(levelId: string): SkillLevelRequirement[] {
    const level = this.skillLevels.get(levelId);
    return level?.requirements || [];
  }

  /**
   * Calculate completion percentage for level
   */
  calculateCompletionPercentage(levelId: string): number {
    const level = this.skillLevels.get(levelId);
    if (!level) return 0;

    let totalProgress = 0;
    let metRequirements = 0;

    for (const requirement of level.requirements) {
      if (!requirement.required) {
        continue;
      }

      let progress = 0;

      // This is a simplified calculation - in real implementation,
      // we'd need to track actual progress for each requirement
      progress = 50; // Assume 50% for now
      totalProgress += progress;
      metRequirements += (progress >= 100) ? 1 : 0;
    }

    return totalProgress / (level.requirements.length * 100);
  }
}

export const skillAssessor = new SkillAssessor();
