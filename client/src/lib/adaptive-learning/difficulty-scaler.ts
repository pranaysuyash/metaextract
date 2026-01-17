/**
 * Difficulty Scaler - Adjust content complexity based on user skill
 */

import type { SkillLevelId } from './types';
import type { SkillLevel } from './skill-assessor';

export interface DifficultyLevel {
  level: 'minimal' | 'simple' | 'standard' | 'detailed' | 'comprehensive';
  complexityFactor: number;
  description: string;
  explanationDepth: 'minimal' | 'concise' | 'standard' | 'detailed';
  animationLevel: 'none' | 'subtle' | 'moderate';
  progressIndicators: 'none' | 'minimal' | 'standard';
}

export interface ContentAdjustment {
  explanationDepth: DifficultyLevel['explanationDepth'];
  examples: number;
  technicalTerms: boolean;
  animationLevel: DifficultyLevel['animationLevel'];
  progressIndicators: DifficultyLevel['progressIndicators'];
}

export class DifficultyScaler {
  private skillLevels: Map<SkillLevelId, DifficultyLevel> = new Map();

  constructor() {
    this.initializeDifficultyLevels();
  }

  private initializeDifficultyLevels(): void {
    this.skillLevels.set('beginner', {
      level: 'minimal',
      complexityFactor: 1.0,
      description: 'Simple language, clear instructions, minimal information per step',
      explanationDepth: 'concise',
      animationLevel: 'subtle',
      progressIndicators: 'minimal',
    });

    this.skillLevels.set('intermediate', {
      level: 'simple',
      complexityFactor: 1.5,
      description: 'Standard language, clear examples, balanced information',
      explanationDepth: 'standard',
      animationLevel: 'subtle',
      progressIndicators: 'standard',
    });

    this.skillLevels.set('advanced', {
      level: 'standard',
      complexityFactor: 2.0,
      description: 'Detailed language, comprehensive examples, rich information',
      explanationDepth: 'detailed',
      animationLevel: 'moderate',
      progressIndicators: 'standard',
    });
  }

  getDifficultyLevel(skillLevelId: SkillLevelId): DifficultyLevel | undefined {
    return this.skillLevels.get(skillLevelId);
  }

  adjustContent(skillLevel: Pick<SkillLevel, 'id'>): ContentAdjustment {
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

    return {
      explanationDepth: level.explanationDepth,
      examples: isAdvanced ? 5 : isIntermediate ? 3 : 2,
      technicalTerms: isAdvanced,
      animationLevel: isAdvanced ? 'moderate' : 'subtle',
      progressIndicators: isAdvanced ? 'standard' : 'minimal',
    };
  }

  getRecommendedTutorialLength(skillLevelId: SkillLevelId): number {
    const level = this.skillLevels.get(skillLevelId);
    if (!level) return 5;

    switch (level.level) {
      case 'minimal':
        return 2;
      case 'simple':
        return 4;
      case 'standard':
        return 7;
      case 'detailed':
        return 12;
      default:
        return 5;
    }
  }

  getExplanationDepth(skillLevelId: SkillLevelId): DifficultyLevel['explanationDepth'] {
    return this.skillLevels.get(skillLevelId)?.explanationDepth ?? 'standard';
  }

  shouldShowAdvancedFeatures(skillLevelId: SkillLevelId): boolean {
    return skillLevelId === 'advanced';
  }

  getAllDifficultyLevels(): DifficultyLevel[] {
    return Array.from(this.skillLevels.values());
  }
}

export const difficultyScaler = new DifficultyScaler();
