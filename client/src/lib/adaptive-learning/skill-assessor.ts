/**
 * Skill Assessor - Evaluate user's proficiency level
 */

import type { SkillLevelId, UserBehaviorProfile } from './types';

export interface SkillLevel {
  id: SkillLevelId;
  name: string;
  requirements: SkillLevelRequirement[];
  confidence: number; // 0..1
  nextLevelId?: SkillLevelId;
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
      id: 'beginner',
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
      id: 'intermediate',
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
      id: 'advanced',
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
  assess(profile: UserBehaviorProfile): SkillLevel {
    // Evaluate all levels and pick the highest level whose REQUIRED requirements are met.
    const levels: SkillLevel[] = ['beginner', 'intermediate', 'advanced']
      .map(id => this.skillLevels.get(id))
      .filter((v): v is SkillLevel => Boolean(v));

    let matched: SkillLevel = levels[0]!;

    for (const level of levels) {
      const updatedRequirements = level.requirements.map(req => {
        const progress = this.calculateRequirementProgress(req.id, profile);
        return {
          ...req,
          currentProgress: Math.min(req.targetValue, progress),
        };
      });

      const required = updatedRequirements.filter(r => r.required);
      const metRequired = required.filter(r => r.currentProgress >= r.targetValue);
      const meetsAllRequired = required.length > 0 && metRequired.length === required.length;

      // Confidence: average completion across required requirements (0..1)
      const completion =
        required.length === 0
          ? 0
          : required.reduce((sum, r) => sum + r.currentProgress / r.targetValue, 0) /
            required.length;

      const candidate: SkillLevel = {
        ...level,
        requirements: updatedRequirements,
        confidence: Math.max(0, Math.min(1, completion)),
      };

      if (meetsAllRequired) {
        matched = candidate;
      }
    }

    matched = {
      ...matched,
      nextLevelId:
        matched.id === 'beginner'
          ? 'intermediate'
          : matched.id === 'intermediate'
            ? 'advanced'
            : undefined,
    };

    return matched;
  }

  private calculateRequirementProgress(
    requirementId: string,
    profile: UserBehaviorProfile
  ): number {
    switch (requirementId) {
      case 'uploads_5':
        return Math.min(5, profile.getActionsByType('upload').length);
      case 'uploads_15':
        return Math.min(15, profile.getActionsByType('upload').length);
      case 'uploads_50':
        return Math.min(50, profile.getActionsByType('upload').length);
      case 'navigation_explore': {
        const uniqueTargets = new Set(
          profile
            .getActionsByType('navigation')
            .map(a => a.target)
            .filter((t): t is string => Boolean(t))
        );
        return Math.min(3, uniqueTargets.size);
      }
      case 'help_views_5':
        return Math.min(5, profile.getActionsByType('help_view').length);
      case 'help_views_15':
        return Math.min(15, profile.getActionsByType('help_view').length);
      case 'advanced_filters':
        return profile.commonPatterns.some(p => p.type === 'filter') ? 5 : 0;
      case 'batch_processing':
        return profile.commonPatterns.some(p => p.type === 'batch') ? 5 : 0;
      case 'export_advanced':
        return Math.min(5, profile.getActionsByType('export').length);
      case 'all_help_views':
        return Math.min(5, profile.getActionsByType('help_view').length);
      default:
        return 0;
    }
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
    // Without a live behavior profile, return the baseline beginner level.
    // Callers that have a profile should call assess(profile) directly.
    return this.skillLevels.get('beginner')!;
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

    const required = level.requirements.filter(r => r.required);
    for (const requirement of required) {
      const percentage = (requirement.currentProgress / requirement.targetValue) * 100;
      totalProgress += percentage;
      metRequirements += percentage >= 100 ? 1 : 0;
    }

    return required.length === 0 ? 0 : totalProgress / (required.length * 100);
  }
}

export const skillAssessor = new SkillAssessor();
