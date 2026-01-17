/**
 * Path Recommender - A/B test for tutorial optimization
 */

import type { CommonPattern, SkillLevelId, UserBehaviorProfile } from './types';

export interface PathOption {
  id: string;
  name: string;
  description: string;
  estimatedDuration: number;
  steps: string[];
  difficulty: SkillLevelId;
  priority: number;
}

export interface PathRecommendation {
  optionId: string;
  confidence: number;
  reasoning: string;
  expectedOutcome: string;
  timestamp: number;
}

export class PathRecommender {
  private paths: PathOption[] = [];

  constructor() {
    this.initializePaths();
    this.loadUserPaths();
  }

  /**
   * Initialize available paths
   */
  private initializePaths(): void {
    this.paths = [
      {
        id: 'quick_start',
        name: 'Quick Start',
        description: '2-minute quick start tutorial for fast learners',
        estimatedDuration: 2,
        steps: ['welcome', 'upload', 'results', 'done'],
        difficulty: 'beginner',
        priority: 1,
      },
      {
        id: 'standard_tour',
        name: 'Standard Tour',
        description: '5-minute standard tutorial with 4 steps',
        estimatedDuration: 5,
        steps: ['welcome', 'upload', 'explore', 'complete'],
        difficulty: 'beginner',
        priority: 2,
      },
      {
        id: 'comprehensive_tour',
        name: 'Comprehensive Tour',
        description: '10-minute comprehensive tour with 7 steps',
        estimatedDuration: 10,
        steps: [
          'welcome',
          'upload',
          'results',
          'explore_gps',
          'explore_exif',
          'download',
          'complete',
        ],
        difficulty: 'beginner',
        priority: 3,
      },
      {
        id: 'quick_skip',
        name: 'Quick Skip',
        description: 'Skip to results immediately, no tutorial',
        estimatedDuration: 0,
        steps: ['upload', 'results'],
        difficulty: 'beginner',
        priority: 0,
      },
      {
        id: 'purpose_driven',
        name: 'Purpose-Driven Tutorial',
        description: "5-minute tutorial focused on user's stated purpose",
        estimatedDuration: 5,
        steps: [
          'purpose_intro',
          'purpose_upload',
          'purpose_explore',
          'complete',
        ],
        difficulty: 'beginner',
        priority: 2,
      },
    ];
  }

  /**
   * Load user's path preferences
   */
  private loadUserPaths(): void {
    try {
      const stored = localStorage.getItem('user_learning_path');
      if (stored) {
        const userPaths: Record<string, number> = JSON.parse(stored);
        // Increment usage count for used paths
        Object.keys(userPaths).forEach(pathId => {
          userPaths[pathId] = (userPaths[pathId] || 0) + 1;
        });
        localStorage.setItem('user_learning_path', JSON.stringify(userPaths));
      }
    } catch (error) {
      console.error('[PathRecommender] Failed to load user paths', error);
    }
  }

  /**
   * Recommend optimal path based on user behavior
   */
  recommendPath(
    profile: UserBehaviorProfile,
    currentTutorialId: string
  ): PathRecommendation {
    const recommendations: PathRecommendation[] = [];
    const now = Date.now();

    // Score each path based on multiple factors
    this.paths.forEach(path => {
      let score = 0;

      // Prefer the explicitly requested tutorial path when it exists.
      if (path.id === currentTutorialId) {
        score += 2;
      }

      // 1. Match with skill level (higher is better)
      const skillLevelMatch = profile.expertiseLevel;
      if (skillLevelMatch === path.difficulty) {
        score += 5;
      } else if (
        skillLevelMatch === 'beginner' &&
        path.difficulty === 'beginner'
      ) {
        score += 3;
      } else if (
        skillLevelMatch === 'intermediate' &&
        path.difficulty === 'beginner'
      ) {
        score += 2;
      }

      // 2. Match with user intent
      const userIntent = this.detectUserIntent(profile);
      if (userIntent.exploring && path.id === 'quick_start') {
        score += 4; // Explorers want quick start
      }
      if (userIntent.exploring && path.id === 'purpose_driven') {
        score += 3; // Explorers with purpose guidance
      }
      if (
        !userIntent.exploring &&
        !userIntent.learning &&
        path.id !== 'quick_skip'
      ) {
        score += 2; // Casual users prefer standard/standard tours
      }

      // 3. Match with user behavior patterns
      profile.commonPatterns.forEach(pattern => {
        if (this.patternMatchesBehavior(pattern, profile)) {
          score += pattern.confidence * 3; // High confidence pattern match
        }
      });

      // 4. Match with current session state
      const recentActions = profile.getRecentActions(10);
      const recentSkipCount = recentActions.filter(
        a => a.type === 'skip'
      ).length;
      if (path.id !== 'quick_skip' && recentSkipCount > 3) {
        score -= 2; // User is skipping tutorials
      }
      const avgTime = profile.averageTimeBetweenActions;
      if (
        path.estimatedDuration > 0 &&
        avgTime > path.estimatedDuration * 1.5
      ) {
        score -= 3; // Tutorial is too slow for this user
      } else if (avgTime < path.estimatedDuration * 0.8) {
        score += 2; // Good match
      }

      recommendations.push({
        optionId: path.id,
        confidence: Math.min(0.95, score / 10),
        reasoning: this.generateReasoning(path, profile, score),
        expectedOutcome: this.generateExpectedOutcome(path, profile),
        timestamp: now,
      });
    });

    // Sort recommendations by confidence
    recommendations.sort((a, b) => b.confidence - a.confidence);

    return recommendations[0];
  }

  /**
   * Check if pattern matches behavior
   */
  private patternMatchesBehavior(
    pattern: CommonPattern,
    profile: UserBehaviorProfile
  ): boolean {
    if (pattern.type === 'hesitant' && profile.averageTimeBetweenActions > 30) {
      return true;
    }
    if (pattern.type === 'systematic_clicker' && profile.totalActions > 20) {
      return true;
    }
    if (pattern.type === 'power_user' && profile.totalActions > 50) {
      return true;
    }
    return false;
  }

  private detectUserIntent(profile: UserBehaviorProfile): {
    exploring: boolean;
    learning: boolean;
  } {
    const hasNavigation = profile.getActionsByType('navigation').length > 0;
    const hasHelpViews = profile.getActionsByType('help_view').length > 0;

    const exploring =
      hasNavigation ||
      profile.commonPatterns.some(p => p.type === 'exploration' || p.type === 'click');

    const learning =
      hasHelpViews || profile.commonPatterns.some(p => p.type === 'help_seeking');

    return { exploring, learning };
  }

  /**
   * Generate reasoning for recommendation
   */
  private generateReasoning(
    path: PathOption,
    profile: UserBehaviorProfile,
    score: number
  ): string {
    const reasons: string[] = [];

    if (score > 7) {
      reasons.push(
        'Excellent match: Perfect alignment with user skill, behavior, and intent'
      );
    } else if (score > 5) {
      reasons.push('Strong match: Good alignment with user characteristics');
    } else if (score > 3) {
      reasons.push('Moderate match: Reasonable alignment');
    } else if (score > 0) {
      reasons.push('Acceptable: May work, but some concerns');
    }

    // Add specific factors
    if (path.difficulty === profile.expertiseLevel) {
      reasons.push("Matches user's skill level");
    } else {
      reasons.push('Difficulty may be challenging');
    }

    const completionRate = profile.completionRate;
    if (completionRate > 0.9 && path.id !== 'quick_skip') {
      reasons.push(
        'High completion rate user: Should handle standard/longer tutorials'
      );
    }

    if (profile.commonPatterns.length > 0) {
      const patternTypes = profile.commonPatterns.map(p => p.type);
      reasons.push(`Behavior patterns: ${patternTypes.slice(0, 3).join(', ')}`);
    }

    const intent = this.detectUserIntent(profile);
    reasons.push(`User intent: ${intent.exploring ? 'Exploring' : 'Task-oriented'}`);

    return reasons.join('; ');
  }

  /**
   * Generate expected outcome
   */
  private generateExpectedOutcome(
    path: PathOption,
    profile: UserBehaviorProfile
  ): string {
    const userIntent = this.detectUserIntent(profile);

    if (path.id === 'quick_skip') {
      return 'Skip tutorial, go directly to results';
    }

    const timeFit =
      profile.averageTimeBetweenActions < path.estimatedDuration * 1.5;
    const timeTooSlow =
      profile.averageTimeBetweenActions > path.estimatedDuration * 2;

    if (timeFit) {
      return 'Optimal length for user';
    } else if (timeTooSlow) {
      return 'May be too long, consider shorter option';
    } else {
      return 'Appropriate length for user pace';
    }
  }

  /**
   * Get optimal path
   */
  getOptimalPath(currentTutorialId: string): PathOption | null {
    // In a real implementation, this would query the recommender
    // For now, return the highest scoring path for the given tutorial
    const path = this.paths.find(p => p.id === currentTutorialId);
    return path || this.paths[0];
  }

  /**
   * Update path usage
   */
  recordPathOutcome(
    optionId: string,
    success: boolean,
    actualDuration: number
  ): void {
    try {
      const userPaths = JSON.parse(
        localStorage.getItem('user_learning_path') || '{}'
      );
      const currentUsage = userPaths[optionId] || 0;

      // Update based on success and duration
      if (success) {
        // Successful completion
        const expected =
          this.paths.find(p => p.id === optionId)?.estimatedDuration || 5;
        const timeFit = actualDuration <= expected * 1.2;
        userPaths[optionId] = currentUsage + (timeFit ? 1 : 0);
      } else {
        // Failed or abandoned
        userPaths[optionId] = Math.max(0, currentUsage - 1);
      }

      localStorage.setItem('user_learning_path', JSON.stringify(userPaths));
    } catch (error) {
      console.error('[PathRecommender] Failed to update path outcome', error);
    }
  }

  /**
   * Get all paths
   */
  getAllPaths(): PathOption[] {
    return [...this.paths];
  }

  /**
   * Reset user path history
   */
  resetUserPaths(): void {
    localStorage.removeItem('user_learning_path');
  }

  /**
   * Get user path history
   */
  getUserPaths(): Record<string, number> {
    try {
      const stored = localStorage.getItem('user_learning_path');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('[PathRecommender] Failed to get user paths', error);
      return {};
    }
  }
}

export const pathRecommender = new PathRecommender();
