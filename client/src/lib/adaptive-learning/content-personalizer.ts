/**
 * Content Personalizer
 *
 * Applies skill-based adjustments to tutorial/help content.
 */

import type { PersonalizedContent, SkillLevelId } from './types';
import { difficultyScaler } from './difficulty-scaler';

export class ContentPersonalizer {
  personalizeContent(
    originalContent: string,
    tutorialStepId: string,
    userSkillLevel: { id: SkillLevelId }
  ): PersonalizedContent {
    const adjustment = difficultyScaler.adjustContent({ id: userSkillLevel.id });

    const adjustments: string[] = [];

    adjustments.push(`explanationDepth:${adjustment.explanationDepth}`);
    adjustments.push(`examples:${adjustment.examples}`);
    adjustments.push(`technicalTerms:${adjustment.technicalTerms ? 'on' : 'off'}`);

    const examples: string[] = [];
    for (let i = 1; i <= adjustment.examples; i++) {
      examples.push(`Example ${i} for ${tutorialStepId}`);
    }

    // For now we keep content intact and append optional guidance.
    // This intentionally avoids rewriting user-facing copy without explicit product direction.
    let adjustedContent = originalContent;
    if (adjustment.explanationDepth === 'minimal') {
      adjustedContent = originalContent;
    } else if (adjustment.explanationDepth === 'concise') {
      adjustedContent = originalContent;
    } else if (adjustment.explanationDepth === 'detailed') {
      adjustedContent = `${originalContent}\n\nAdditional details available in the help panel.`;
      adjustments.push('appended_detail_hint');
    }

    return {
      originalContent,
      adjustedContent,
      explanationDepth: adjustment.explanationDepth,
      examples,
      metadata: {
        skillLevel: userSkillLevel.id,
        adjustments,
      },
    };
  }

  getRecommendedContent(
    originalContent: string,
    tutorialStepId: string,
    userSkillLevel: { id: SkillLevelId }
  ): { adjustedContent: string } {
    const personalized = this.personalizeContent(
      originalContent,
      tutorialStepId,
      userSkillLevel
    );
    return { adjustedContent: personalized.adjustedContent };
  }
}

export const contentPersonalizer = new ContentPersonalizer();
