/**
 * Adaptive Learning - shared types
 *
 * These types are used across the adaptive-learning submodules.
 */

export type SkillLevelId = 'beginner' | 'intermediate' | 'advanced';

export interface SkillLevel {
  id: SkillLevelId;
  name: string;
  confidence: number; // 0..1
  nextLevelId?: SkillLevelId;
}

export interface UserAction {
  type: string;
  timestamp: number;
  target?: string;
  durationMs?: number;
  metadata?: Record<string, unknown>;
}

export interface CommonPattern {
  type: string;
  frequency: number;
  confidence: number;
  target?: string;
}

export interface UserBehaviorProfile {
  userId: string;
  expertiseLevel: SkillLevelId;
  totalActions: number;
  completionRate: number; // 0..1
  engagementRate: number; // 0..1
  averageTimeBetweenActions: number; // seconds
  commonPatterns: CommonPattern[];

  getActionsByType(type: string): UserAction[];
  getRecentActions(limit: number): UserAction[];
}

export type ExplanationDepth = 'minimal' | 'concise' | 'standard' | 'detailed';

export interface PersonalizedContent {
  originalContent: string;
  adjustedContent: string;
  explanationDepth: ExplanationDepth;
  examples: string[];
  metadata: {
    skillLevel: SkillLevelId;
    adjustments: string[];
  };
}
