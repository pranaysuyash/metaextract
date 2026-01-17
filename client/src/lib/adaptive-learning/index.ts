/**
 * Adaptive Learning System - Main module
 */

export { adaptiveLearningSystem as behaviorTracker } from './behavior-tracker';
export { interactionAnalyzer } from './interaction-analyzer';
export { patternDetector } from './pattern-detector';
export { skillAssessor } from './skill-assessor';
export { difficultyScaler } from './difficulty-scaler';
export { pathRecommender } from './path-recommender';
export { contentPersonalizer } from './content-personalizer';
export { tutorialOptimizer } from './tutorial-optimizer';

export type {
  UserBehaviorProfile,
  UserAction,
  SkillLevelId,
  SkillLevel,
  PersonalizedContent,
} from './types';

export type { DifficultyLevel, ContentAdjustment } from './difficulty-scaler';
export type { TutorialVariant, ABTest, ABTestMetrics, ABTestResult } from './tutorial-optimizer';

import type { PersonalizedContent, SkillLevel } from './types';
import { contentPersonalizer } from './content-personalizer';
import { difficultyScaler } from './difficulty-scaler';
import { pathRecommender } from './path-recommender';

export interface AdaptiveLearningConfig {
  enabled: boolean;
  dataRetentionDays: number;
  minConfidenceThreshold: number;
  minSampleSize: number;
  abTesting: boolean;
}

export class AdaptiveLearningEngine {
  private config: AdaptiveLearningConfig;

  constructor(config: Partial<AdaptiveLearningConfig> = {}) {
    this.config = {
      enabled: true,
      dataRetentionDays: 30,
      minConfidenceThreshold: 0.6,
      minSampleSize: 100,
      abTesting: true,
      ...config,
    };
  }

  /**
   * Get personalized content for tutorial step
   */
  getPersonalizedContent(
    originalContent: string,
    tutorialStepId: string,
    userSkillLevel: SkillLevel
  ): PersonalizedContent {
    return contentPersonalizer.personalizeContent(
      originalContent,
      tutorialStepId,
      userSkillLevel
    );
  }

  /**
   * Get recommended tutorial length
   */
  getRecommendedTutorialLength(userSkillLevel: SkillLevel): number {
    return difficultyScaler.getRecommendedTutorialLength(userSkillLevel.id);
  }

  /**
   * Should show advanced features?
   */
  shouldShowAdvancedFeatures(userSkillLevel: SkillLevel): boolean {
    return difficultyScaler.shouldShowAdvancedFeatures(userSkillLevel.id);
  }

  /**
   * Generate adaptive tutorial
   */
  generateAdaptiveTutorial(
    baseTutorialSteps: string[],
    userSkillLevel: SkillLevel
  ): string {
    const personalizer = contentPersonalizer;
    pathRecommender.getOptimalPath('tutorial_1');

    let adaptiveContent = '';
    baseTutorialSteps.forEach((step, index) => {
      const personalized = personalizer.getRecommendedContent(
        step,
        `tutorial_${index}`,
        userSkillLevel
      );

      adaptiveContent += `${personalized.adjustedContent}\n\n`;
    });

    // Add learning objectives
    adaptiveContent += `\n### Learning Objectives\n`;
    const objectives = this.generateLearningObjectives(userSkillLevel);
    objectives.forEach(obj => {
      adaptiveContent += `- ${obj}\n`;
    });

    return adaptiveContent;
  }

  /**
   * Generate learning objectives based on skill level
   */
  private generateLearningObjectives(skillLevel: SkillLevel): string[] {
    switch (skillLevel.id) {
      case 'beginner':
        return [
          'Understand basic concepts (metadata, GPS, camera settings)',
          'Complete first successful extraction',
          'View 5 key metadata fields',
        ];
      case 'intermediate':
        return [
          'Explore different metadata categories',
          'Use advanced filtering and search',
          'Export in multiple formats',
          'Complete 15 extractions',
        ];
      case 'advanced':
        return [
          'Master all available features',
          'Use forensic tools (comparison, verification)',
          'Create and use custom workflows',
          'Batch process multiple files',
          'Complete 50 extractions',
        ];
      default:
        return [];
    }
  }
}

export const adaptiveLearningEngine = new AdaptiveLearningEngine();
