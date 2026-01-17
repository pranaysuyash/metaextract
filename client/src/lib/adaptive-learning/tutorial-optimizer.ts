/**
 * Tutorial Optimizer - A/B testing framework for tutorials
 */

import type { SkillLevelId, UserBehaviorProfile } from './types';

export interface TutorialVariant {
  id: string;
  name: string;
  content: string;
  userSkillLevel: SkillLevelId;
  targetSegment: 'explorers' | 'beginners' | 'learners';
}

export interface ABTest {
  id: string;
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
  private tests: Map<string, ABTest> = new Map();

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
        targetSegment: 'beginners',
      },
      {
        id: 'interactive_vs_passive',
        name: 'Interactive vs Passive Learning',
        content: 'Should tutorial have interactive elements or be self-guided?',
        userSkillLevel: 'beginner',
        targetSegment: 'learners',
      },
      {
        id: 'minimal_vs_rich',
        name: 'Minimal vs Rich Explanations',
        content: 'Should we use minimal text or comprehensive examples?',
        userSkillLevel: 'beginner',
        targetSegment: 'learners',
      },
    ];
  }

  /**
   * Start A/B test for tutorial step
   */
  startABTest(tutorialStepId: string, variants: TutorialVariant[]): string {
    const testId = `ab_test_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const startTime = Date.now();

    if (variants.length < 2) {
      throw new Error('startABTest requires at least two variants');
    }

    // Create test record
    const emptyMetrics: ABTestMetrics = {
      completionRate: 0,
      timeToComplete: 0,
      stepsSkipped: 0,
      helpViews: 0,
      userSatisfaction: 0,
      userEngagement: 0,
    };

    const test: ABTest = {
      id: testId,
      variantA: variants[0]!,
      variantB: variants[1]!,
      startTime,
      endTime: 0,
      metrics: emptyMetrics,
      results: {
        winner: 'tie',
        confidenceDelta: 0,
        metricsA: emptyMetrics,
        metricsB: emptyMetrics,
        recommendation: `A/B test started for ${tutorialStepId}`,
        insights: [],
      },
    };

    this.tests.set(testId, test);

    return testId;
  }

  /**
   * Complete variant (simulate user going through tutorial)
   */
  completeVariant(
    testId: string,
    variant: 'A' | 'B',
    metrics: ABTestMetrics,
    userProfile?: UserBehaviorProfile
  ): void {
    const test = this.tests.get(testId);
    if (!test) return;

    const endTime = Date.now();
    test.endTime = endTime;
    test.metrics = metrics;

    const metricsA = variant === 'A' ? metrics : test.results.metricsA;
    const metricsB = variant === 'B' ? metrics : test.results.metricsB;

    const winner = this.pickWinner(metricsA, metricsB);
    const confidenceDelta = Math.abs(metricsA.completionRate - metricsB.completionRate);

    test.results = {
      winner,
      confidenceDelta,
      metricsA,
      metricsB,
      recommendation: this.generateRecommendation(winner, confidenceDelta, userProfile),
      insights: this.generateInsights(metricsA, metricsB),
    };
  }

  /**
   * Generate recommendation from test results
   */
  private pickWinner(metricsA: ABTestMetrics, metricsB: ABTestMetrics): 'A' | 'B' | 'tie' {
    if (metricsA.completionRate > metricsB.completionRate + 0.05) return 'A';
    if (metricsB.completionRate > metricsA.completionRate + 0.05) return 'B';
    return 'tie';
  }

  /**
   * Generate insights from test results
   */
  private generateInsights(metricsA: ABTestMetrics, metricsB: ABTestMetrics): string[] {
    const insights: string[] = [];
    insights.push(
      `Completion rate: A=${this.formatPercentage(metricsA.completionRate)}, B=${this.formatPercentage(metricsB.completionRate)}`
    );
    insights.push(
      `Time to complete (ms): A=${Math.round(metricsA.timeToComplete)}, B=${Math.round(metricsB.timeToComplete)}`
    );
    insights.push(`Steps skipped: A=${metricsA.stepsSkipped}, B=${metricsB.stepsSkipped}`);
    insights.push(`Help views: A=${metricsA.helpViews}, B=${metricsB.helpViews}`);
    return insights;
  }

  /**
   * Get insight explanation
   */
  private generateRecommendation(
    winner: 'A' | 'B' | 'tie',
    confidenceDelta: number,
    userProfile?: UserBehaviorProfile
  ): string {
    const userLabel = userProfile ? ` for ${userProfile.expertiseLevel} users` : '';
    if (winner === 'tie') {
      return `No clear winner${userLabel}; consider additional data (Δ=${this.formatPercentage(confidenceDelta)}).`;
    }
    return `Prefer variant ${winner}${userLabel} (Δ=${this.formatPercentage(confidenceDelta)}).`;
  }

  /**
   * Format percentage
   */
  private formatPercentage(value: number): string {
    return `${(value * 100).toFixed(1)}%`;
  }

  /**
   * Save test results
   */
  saveTestResults(testId: string): void {
    const test = this.tests.get(testId);
    if (!test) return;
    try {
      localStorage.setItem(`ab_test_${testId}_results`, JSON.stringify(test));
    } catch (error) {
      console.error('[TutorialOptimizer] Failed to save test results', error);
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
    // Intentionally do not clear all localStorage.
  }
}

export const tutorialOptimizer = new TutorialOptimizer();
