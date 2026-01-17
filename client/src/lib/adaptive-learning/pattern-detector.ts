/**
 * Pattern Detector - Identify user behavior patterns
 */

import type { UserBehaviorProfile } from './types';

export interface Pattern {
  id: string;
  type: 'upload_frequency' | 'help_seeking' | 'exploration' | 'completist' | 'hesitant' | 'fast_learner' | 'slow_learner' | 'systematic_clicker' | 'power_user' | 'casual_user';
  name: string;
  description: string;
  triggerCondition: string;
  adaptationRecommendation: string;
  confidence: number;
}

export interface PatternMatch {
  patternId: string;
  confidence: number;
  timestamp: number;
}

export class PatternDetector {
  private patterns: Pattern[] = [];
  private detectedPatterns: Map<string, PatternMatch[]> = new Map();

  constructor() {
    this.initializePatterns();
    this.loadDetectedPatterns();
  }

  /**
   * Initialize built-in patterns
   */
  private initializePatterns(): void {
    this.patterns = [
      {
        id: 'frequent_uploader',
        type: 'upload_frequency',
        name: 'Frequent Uploader',
        description: 'User uploads multiple files frequently',
        triggerCondition: 'Upload count >= 10/week',
        adaptationRecommendation: 'Offer batch processing features',
        confidence: 0.7,
      },
      {
        id: 'help_seeker',
        type: 'help_seeking',
        name: 'Help Seeker',
        description: 'User frequently views help content and tutorials',
        triggerCondition: 'Help view count >= 5/week',
        adaptationRecommendation: 'Provide more contextual help suggestions',
        confidence: 0.6,
      },
      {
        id: 'explorer',
        type: 'exploration',
        name: 'Explorer',
        description: 'User explores UI elements and navigation paths',
        triggerCondition: 'Unique navigation paths >= 3/week',
        adaptationRecommendation: 'Offer guided tours for exploration',
        confidence: 0.5,
      },
      {
        id: 'completist',
        type: 'completist',
        name: 'Completist',
        description: 'User completes tasks without skipping',
        triggerCondition: 'Completion rate >= 90%',
        adaptationRecommendation: 'Keep tutorials brief and focused',
        confidence: 0.8,
      },
      {
        id: 'hesitant',
        type: 'hesitant',
        name: 'Hesitant User',
        description: 'User exhibits slow, deliberate actions, may need guidance',
        triggerCondition: 'Average action time > 30 seconds',
        adaptationRecommendation: 'Provide clear instructions and progress indicators',
        confidence: 0.5,
      },
      {
        id: 'fast_learner',
        type: 'fast_learner',
        name: 'Fast Learner',
        description: 'User quickly processes information and moves through UI',
        triggerCondition: 'Average action time < 10 seconds',
        adaptationRecommendation: 'Provide advanced features and shortcuts',
        confidence: 0.7,
      },
      {
        id: 'slow_learner',
        type: 'slow_learner',
        name: 'Slow Learner',
        description: 'User takes time to process information',
        triggerCondition: 'Average action time > 20 seconds',
        adaptationRecommendation: 'Simplify UI and reduce cognitive load',
        confidence: 0.6,
      },
      {
        id: 'systematic_clicker',
        type: 'systematic_clicker',
        name: 'Systematic Clicker',
        description: 'User exhibits systematic clicking patterns',
        triggerCondition: 'Detected by interaction analyzer',
        adaptationRecommendation: 'Review content organization and navigation flow',
        confidence: 0.8,
      },
      {
        id: 'power_user',
        type: 'power_user',
        name: 'Power User',
        description: 'User demonstrates advanced features and quick proficiency',
        triggerCondition: 'Upload count >= 50 AND completion rate >= 80%',
        adaptationRecommendation: 'Unlock advanced tools and expert features',
        confidence: 0.9,
      },
      {
        id: 'casual_user',
        type: 'casual_user',
        name: 'Casual User',
        description: 'User uses application occasionally with simple tasks',
        triggerCondition: 'Upload count < 5/week AND completion rate >= 50%',
        adaptationRecommendation: 'Keep tutorials simple and focused on quick wins',
        confidence: 0.5,
      },
    ];
  }

  /**
   * Load detected patterns from localStorage
   */
  private loadDetectedPatterns(): void {
    try {
      const stored = localStorage.getItem('detected_patterns_v1');
      if (!stored) return;

      const parsed: unknown = JSON.parse(stored);
      if (!Array.isArray(parsed)) return;

      for (const item of parsed) {
        const match = item as PatternMatch;
        if (!match?.patternId || typeof match.timestamp !== 'number') continue;
        const existing = this.detectedPatterns.get(match.patternId) || [];
        this.detectedPatterns.set(match.patternId, [...existing, match].slice(-3));
      }
    } catch (error) {
      console.error('[PatternDetector] Failed to load patterns', error);
    }
  }

  /**
   * Save detected pattern
   */
  private saveDetectedPattern(match: PatternMatch): void {
    try {
      const existing = this.detectedPatterns.get(match.patternId) || [];
      const updated = [match, ...existing].slice(-3); // Keep last 3 matches
      this.detectedPatterns.set(match.patternId, updated);

      const flattened: PatternMatch[] = [];
      this.detectedPatterns.forEach(matches => {
        flattened.push(...matches);
      });
      localStorage.setItem('detected_patterns_v1', JSON.stringify(flattened));
    } catch (error) {
      console.error('[PatternDetector] Failed to save pattern', error);
    }
  }

  /**
   * Analyze behavior and detect patterns
   */
  analyzeAndDetect(profile: UserBehaviorProfile): Pattern[] {
    const matched: Pattern[] = [];
    const now = Date.now();

    const helpViews = profile.getActionsByType('help_view').length;
    const uploads = profile.getActionsByType('upload').length;
    const navigations = profile.getActionsByType('navigation').length;

    for (const pattern of this.patterns) {
      const isMatch = this.isPatternMatch(pattern, {
        uploads,
        helpViews,
        navigations,
        totalActions: profile.totalActions,
        completionRate: profile.completionRate,
        averageTimeBetweenActions: profile.averageTimeBetweenActions,
        commonPatternTypes: new Set(profile.commonPatterns.map(p => p.type)),
      });

      if (!isMatch) continue;

      matched.push(pattern);
      this.saveDetectedPattern({
        patternId: pattern.id,
        confidence: pattern.confidence,
        timestamp: now,
      });
    }

    return matched;
  }

  private isPatternMatch(
    pattern: Pattern,
    data: {
      uploads: number;
      helpViews: number;
      navigations: number;
      totalActions: number;
      completionRate: number;
      averageTimeBetweenActions: number;
      commonPatternTypes: Set<string>;
    }
  ): boolean {
    switch (pattern.type) {
      case 'upload_frequency':
        return data.uploads >= 10 || data.totalActions >= 10;
      case 'help_seeking':
        return data.helpViews >= 5;
      case 'exploration':
        return data.navigations >= 3;
      case 'completist':
        return data.completionRate >= 0.9;
      case 'hesitant':
        return data.averageTimeBetweenActions > 30;
      case 'fast_learner':
        return data.averageTimeBetweenActions > 0 && data.averageTimeBetweenActions < 10;
      case 'slow_learner':
        return data.averageTimeBetweenActions > 20;
      case 'systematic_clicker':
        return data.commonPatternTypes.has('systematic_clicker');
      case 'power_user':
        return data.totalActions >= 50 && data.completionRate >= 0.8;
      case 'casual_user':
        return data.totalActions < 20 && data.completionRate >= 0.5;
      default:
        return false;
    }
  }

  /**
   * Get matched patterns
   */
  getMatchedPatterns(): PatternMatch[] {
    const matches: PatternMatch[] = [];
    this.detectedPatterns.forEach((patternMatches, patternId) => {
      matches.push(...patternMatches.slice(-1));
    });
    return matches;
  }

  /**
   * Clear all detected patterns
   */
  clearDetectedPatterns(): void {
    this.detectedPatterns.clear();
    localStorage.removeItem('detected_patterns_v1');
  }
}

export const patternDetector = new PatternDetector();
