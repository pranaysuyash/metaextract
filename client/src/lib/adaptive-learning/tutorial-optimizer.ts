/**
 * Tutorial Optimizer - A/B testing framework for tutorials
 */

import type { PersonalizedContent } from './content-personalizer';
import type { UserBehaviorProfile } from './behavior-tracker';

export interface TutorialVariant {
  id: string;
  name: string;
  content: string;
  userSkillLevel: 'beginner' | 'intermediate' | 'advanced';
  targetSegment: 'explorers' | 'beginners' | 'learners';
}

export interface ABTest {
  variantA: TutorialVariant;
  variantB: TutorialVariant;
  startTime: number;
  endTime: number;
  metrics: ABTestMetrics;
  results: ABTestResult;
}

export interface ABTestMetrics {
  completionRate: number;
  timeToComplete: number;
  stepsSkipped: number;
  helpViews: number;
  userSatisfaction: number;
  userEngagement: number;
}

export interface ABTestResult {
  winner: 'A' | 'B' | 'tie';
  confidenceDelta: number;
  metricsA: ABTestMetrics;
  metricsB: ABTestMetrics;
  recommendation: string;
  insights: string[];
}

export class TutorialOptimizer {
  private tests: Map<string, ABTest[]> = new Map();
  private userProfiles: Map<string, UserBehaviorProfile> = new Map();

  /**
   * Create tutorial variants (A/B tests)
   */
  createVariants(): TutorialVariant[] {
    return [
      {
        id: 'quick_vs_detailed',
        name: 'Quick vs Detailed Tutorial',
        content: 'Should we use concise 2-min version or comprehensive 7-min version?',
        userSkillLevel: 'beginner',
      },
      {
        id: 'interactive_vs_passive',
        name: 'Interactive vs Passive Learning',
        content: 'Should tutorial have interactive elements or be self-guided?',
        userSkillLevel: 'beginner',
      },
      {
        id: 'minimal_vs_rich',
        name: 'Minimal vs Rich Explanations',
        content: 'Should we use minimal text or comprehensive examples?',
        userSkillLevel: 'beginner',
      },
    ];
  }

  /**
   * Start A/B test for tutorial step
   */
  startABTest(tutorialStepId: string, variants: TutorialVariant[]): string {
    const testId = `ab_test_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const startTime = Date.now();

    // Create test record
    const test: ABTest = {
      id: testId,
      variantA: variants[0],
      variantB: variants[1],
      startTime,
      endTime: 0,
      metrics: {
        completionRate: 0,
        timeToComplete: 0,
        stepsSkipped: 0,
        helpViews: 0,
        userSatisfaction: 0,
        userEngagement: 0,
      },
      results: {
        recommendation: '',
        insights: [],
      },
    };

    // Save test
    if (this.tests.has(tutorialStepId)) {
      this.tests.get(tutorialStepId).push(test);
    } else {
      this.tests.set(tutorialStepId, [test]);
    }

    return testId;
  }

  /**
   * Complete variant (simulate user going through tutorial)
   */
  completeVariant(testId: string, variant: TutorialVariant, userProfile: UserBehaviorProfile): void {
    const test = this.tests.get(testId);
    if (!test) return;

    const endTime = Date.now();
    const duration = endTime - test.startTime;
    test.endTime = endTime;

    // Simulate user going through tutorial
    const steps = variant.content.split('\n');
    let stepIndex = 0;
    let completed = 0;
    let skipped = 0;

    steps.forEach(step => {
      stepIndex++;

      // Simulate time per step (average 2 seconds per step)
      const stepTime = 2000;

      // Random completion rate based on user engagement
      const baseCompletionRate = userProfile.engagementRate || 0.8;

      // Skip some steps if user is exploratory
      if (userProfile.commonPatterns.some(p => p.type === 'skip')) {
        if (Math.random() < 0.3 && stepIndex < steps.length - 1) {
          skipped++;
          completed = Math.max(completed - 1, 0);
        }
      } else {
        completed++;
      }

      // Track help views
      if (step.toLowerCase().includes('help')) {
        test.metrics.helpViews++;
      }

      // Track user engagement
      test.metrics.userEngagement += (userProfile.engagementRate * stepTime);
    });

    const completionRate = (completed / steps.length) * baseCompletionRate;
    test.metrics.completionRate = completionRate;
    test.metrics.timeToComplete = duration;

    // Simulate satisfaction (random between 2-5)
    test.metrics.userSatisfaction = Math.floor(Math.random() * 3) + 2;
  }

    test.metrics.stepsSkipped = skipped;

    test.results = {
      recommendation: this.generateRecommendation(test, variant, userProfile),
      insights: this.generateInsights(test, variant, userProfile),
    };
  }

  /**
   * Generate recommendation from test results
   */
  private generateRecommendation(test: ABTest, variant: TutorialVariant, profile: ABTestResult): string {
    const insights: this.generateInsights(test, variant, profile);

    if (test.metricsA.completionRate > test.metricsB.completionRate + 0.1) {
      return `Variant A (${variant.name}) outperforms B (${variant.name}) with ${this.formatPercentage(test.metricsA.completionRate)} vs ${this.formatPercentage(test.metricsB.completionRate)} completion rate. ${this.getInsightExplanation(test, variant, profile)}`;
    } else if (test.metricsB.completionRate > test.metricsA.completionRate + 0.1) {
      return `Variant B (${variant.name}) outperforms A (${variant.name}) with ${this.formatPercentage(test.metricsB.completionRate)} vs ${this.formatPercentage(test.metricsA.completionRate)} completion rate. ${this.getInsightExplanation(test, variant, profile)}`;
    } else {
      const diff = Math.abs(test.metricsA.completionRate - test.metricsB.completionRate);
      if (diff < 0.05) {
        return `No significant difference between variants (diff% difference). Both perform similarly.`;
      } else {
        return `Variant A and B perform similarly (diff% difference). Consider other factors like personalization and user segment.`;
      }
    }
  }

  /**
   * Generate insights from test results
   */
  private generateInsights(test: ABTest, variant: TutorialVariant, profile: ABTestResult): string[] {
    const insights: string[] = [];

    // Completion rate insight
    insights.push(`Completion Rate Variant A: ${this.formatPercentage(test.metricsA.completionRate)}% vs Variant B: ${this.formatPercentage(test.metricsB.completionRate)}%`);

    // Time insight
    const timeDiff = test.metricsA.timeToComplete - test.metricsB.timeToComplete;
    const timeRatio = test.metricsA.timeToComplete / (test.metricsB.timeToComplete || 1);
    if (timeRatio < 0.8) {
      insights.push(`Variant A completes ${(timeRatio * 100).toFixed(0)}% faster than B`);
    } else if (timeRatio > 1.2) {
      insights.push(`Variant B completes ${((1 / timeRatio) * 100).toFixed(0)}% faster than A`);
    }

    // Skip insight
    if (test.metricsA.stepsSkipped !== test.metricsB.stepsSkipped) {
      const diff = test.metricsA.stepsSkipped - test.metricsB.stepsSkipped;
      if (diff > 0) {
        insights.push(`Variant A has ${diff} more skips than B (${test.metricsA.stepsSkipped} vs ${test.metricsB.stepsSkipped})`);
      } else if (diff < 0) {
        insights.push(`Variant B has ${Math.abs(diff)} more skips than A (${test.metricsB.stepsSkipped} vs ${test.metricsA.stepsSkipped})`);
      }
    }

    return insights;
  }

  /**
   * Get insight explanation
   */
  private getInsightExplanation(test: ABTest, variant: TutorialVariant, profile: ABTestResult): string {
    const userProfile = profile.userProfile || 'unknown';

    // Skill level match
    if (variant.userSkillLevel === userProfile.expertiseLevel) {
      return 'Perfect skill level match';
    } else if (
        variant.userSkillLevel === 'intermediate' && userProfile.expertiseLevel === 'beginner'
      ) {
        return 'Variant B slightly overestimates user (intermediate vs beginner)';
      } else if (
        variant.userSkillLevel === 'beginner' && userProfile.expertiseLevel === 'intermediate'
      ) {
        return 'Variant A slightly underestimates user (beginner vs intermediate)';
      }
    }

    // Engagement match
    const engagementDiff = Math.abs(test.metricsA.userEngagement - test.metricsB.userEngagement);
    const relativeDiff = (engagementDiff / test.metricsA.userEngagement) * 100;

    if (engagementDiff > 0.2) {
      return `User engaged ${relativeDiff.toFixed(0)}% ${engagementDiff > 0 ? 'more' : 'less'} with Variant A (${test.metricsA.userEngagement} interactions) vs Variant B (${test.metricsB.userEngagement} interactions)`;
    }

    return 'No significant engagement difference';
  }

  /**
   * Format percentage
   */
  private formatPercentage(value: number): string {
    return `${value.toFixed(1)}%`;
  }

  /**
   * Save test results
   */
  saveTestResults(testId: string): void {
    const test = this.tests.get(testId);
    if (test) {
      try {
        localStorage.setItem(`ab_test_${testId}_results`, JSON.stringify(test));
      } catch (error) {
        console.error('[TutorialOptimizer] Failed to save test results', error);
      }
    }
  }

  /**
   * Get test results
   */
  getTestResults(testId: string): ABTest | null {
    return this.tests.get(testId) || null;
  }

  /**
   * Clear all tests
   */
  clearAllTests(): void {
    this.tests.clear();
    localStorage.clear();
  }
}

export const tutorialOptimizer = new TutorialOptimizer();
