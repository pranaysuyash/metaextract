/**
 * Pattern Detector - Identify user behavior patterns
 */

import type { UserAction, UserBehaviorProfile } from './behavior-tracker';
import { interactionAnalyzer, ClickStream } from './interaction-analyzer';

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
        adaptationRecommendation 'Review content organization and navigation flow',
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
      const stored = localStorage.getItem('detected_patterns');
      if (stored) {
        const loaded: PatternMatch[] = JSON.parse(stored);
        loaded.forEach(match => {
          this.detectedPatterns.set(match.patternId, match);
        });
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

      localStorage.setItem('detected_patterns', JSON.stringify(Array.from(this.detectedPatterns.entries())));
    } catch (error) {
      console.error('[PatternDetector] Failed to save pattern', error);
    }
  }

  /**
   * Analyze behavior and detect patterns
   */
  analyzeAndDetect(profile: UserBehaviorProfile): Pattern[] {
    const detectedPatterns: Pattern[] = [];

    // Check each pattern against behavior
    this.patterns.forEach(pattern => {
      let matches = false;

      switch (pattern.type) {
        case 'upload_frequency':
          const uploadActions = profile.commonPatterns.find(p => p.type === 'upload_frequency');
          if (uploadActions && uploadActions.frequency >= pattern.triggerCondition) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'help_seeking':
          const helpActions = profile.commonPatterns.find(p => p.type === 'help_seeking');
          if (helpActions && helpActions.frequency >= pattern.triggerCondition) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'exploration':
          const explorationActions = profile.commonPatterns.filter(p =>
            p.type === 'click' && p.target?.includes('nav')
          );
          if (explorationActions.length >= pattern.triggerCondition) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'completist':
          if (profile.completionRate >= pattern.triggerCondition) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'hesitant':
          if (profile.averageTimeBetweenActions > pattern.triggerCondition) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'fast_learner':
          if (profile.averageTimeBetweenActions < pattern.triggerCondition) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'slow_learner':
          if (profile.averageTimeBetweenActions > pattern.triggerCondition) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'systematic_clicker':
          const clickAnalysis = interactionAnalyzer.analyzeClickPatterns('*');
          if (clickAnalysis.isIntentional) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'power_user':
          if (profile.totalActions >= 50 && profile.completionRate >= 80) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;

        case 'casual_user':
          if (profile.totalActions < 20 && profile.completionRate >= 50) {
            detectedPatterns.push({
              patternId: pattern.id,
              confidence: pattern.confidence,
              timestamp: Date.now(),
            });
            matches = true;
          }
          break;
      }
    });

    return detectedPatterns;
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
    localStorage.removeItem('detected_patterns');
  }
}

export const patternDetector = new PatternDetector();
