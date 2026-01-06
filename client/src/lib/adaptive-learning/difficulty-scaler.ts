/**
 * Difficulty Scaler - Adjust content complexity based on user skill
 */

import type { SkillLevel } from './skill-assessor';

export interface DifficultyLevel {
  level: 'minimal' | 'simple' | 'standard' | 'detailed' | 'comprehensive';
  complexityFactor: number;
  description: string;
}

export interface ContentAdjustment {
  explanationDepth: 'minimal' | 'concise' | 'standard' | 'detailed';
  examples: number;
  technicalTerms: boolean;
  animationLevel: 'none' | 'subtle' | 'moderate';
  progressIndicators: 'none' | 'minimal' | 'standard';
}

export class DifficultyScaler {
  private skillLevels: Map<string, DifficultyLevel> = new Map();

  constructor() {
    this.initializeDifficultyLevels();
  }

  /**
   * Initialize difficulty level mappings
   */
  private initializeDifficultyLevels(): void {
    this.skillLevels.set('beginner', {
      level: 'minimal',
      complexityFactor: 1.0,
      description: 'Simple language, clear instructions, minimal information per step',
    });

    this.skillLevels.set('intermediate', {
      level: 'simple',
      complexityFactor: 1.5,
      description: 'Standard language, clear examples, balanced information',
    });

    this.skillLevels.set('advanced', {
      level: 'standard',
      complexityFactor: 2.0,
      description: 'Detailed language, comprehensive examples, rich information',
    });
  }

    this.skillLevels.forEach((_, level) => {
      if (!level.explanationDepth) {
        level.explanationDepth = 'concise';
      }
      if (!level.animationLevel) {
        level.animationLevel = 'subtle';
      }
      if (!level.progressIndicators) {
        level.progressIndicators = 'minimal';
      }
    });
  }

  /**
   * Get difficulty level for skill level
   */
  getDifficultyLevel(skillLevelId: string): DifficultyLevel | undefined {
    return this.skillLevels.get(skillLevelId);
  }

  /**
   * Adjust content based on skill level
   */
  adjustContent(skillLevel: SkillLevel): ContentAdjustment {
    const level = this.skillLevels.get(skillLevel.id);
    if (!level) {
      return {
        explanationDepth: 'standard',
        examples: 3,
        technicalTerms: false,
        animationLevel: 'moderate',
        progressIndicators: 'minimal',
      };
    }

    const isIntermediate = skillLevel.id === 'intermediate';
    const isAdvanced = skillLevel.id === 'advanced';

    // Adjust based on level
    const adjustment: ContentAdjustment = {
      explanationDepth: level.explanationDepth,
      examples: isAdvanced ? 5 : isIntermediate ? 3 : 2,
      technicalTerms: isAdvanced,
      animationLevel: isAdvanced ? 'moderate' : 'subtle',
      progressIndicators: isAdvanced ? 'standard' : 'minimal',
    };

    return adjustment;
  }

  /**
   * Get recommended tutorial length based on skill level
   */
  getRecommendedTutorialLength(skillLevelId: string): number {
    const level = this.skillLevels.get(skillLevelId);
    switch (level.level) {
      case 'minimal':
        return 2; // 2 steps for beginner
      case 'simple':
        return 4; // 4 steps for intermediate
      case 'standard':
        return 7; // 7 steps for advanced
      case 'detailed':
        return 12; // 12 steps for experts
      default:
        return 5;
    }
  }

  /**
   * Get explanation depth
   */
  getExplanationDepth(skillLevelId: string): 'minimal' | 'concise' | 'standard' | 'detailed' {
    const level = this.skillLevels.get(skillLevelId);
    return level.explanationDepth || 'standard';
  }

  /**
   * Should show advanced features?
   */
  shouldShowAdvancedFeatures(skillLevelId: string): boolean {
    const level = this.skillLevels.get(skillLevelId);
    return level.id === 'advanced';
  }
}

  /**
   * Get all difficulty levels
   */
  getAllDifficultyLevels(): DifficultyLevel[] {
    return Array.from(this.skillLevels.values());
  }
}

export const difficultyScaler = new DifficultyScaler();
