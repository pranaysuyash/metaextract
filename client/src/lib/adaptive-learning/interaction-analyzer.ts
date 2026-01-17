/**
 * Interaction Analyzer - Detect patterns from user interactions
 */

import type { UserAction } from './types';

export interface InteractionPattern {
  type: string;
  confidence: number;
  frequency: number;
  lastDetected: number;
  description: string;
  averageDurationMs?: number;
}

export interface ClickStream {
  coordinates: { x: number; y: number }[];
  timestamps: number[];
  elementPath?: string;
  scrollDepth?: number;
}

export interface ClickPatternAnalysis {
  isIntentional: boolean;
  isHesitant: boolean;
  clickRate: number;
  averageDepth: number;
  description?: string;
}

export class InteractionAnalyzer {
  private patterns: Map<string, InteractionPattern> = new Map();
  private clickStreams: Map<string, ClickStream> = new Map();
  private interactionHistory: UserAction[] = [];

  /**
   * Analyze a user action and update in-memory patterns.
   */
  analyzeAction(action: UserAction): InteractionPattern {
    this.interactionHistory.push(action);

    const existing = this.patterns.get(action.type);
    if (!existing) {
      const created: InteractionPattern = {
        type: action.type,
        confidence: 1,
        frequency: 1,
        lastDetected: action.timestamp,
        description: this.describeActionPattern(action),
        averageDurationMs: action.durationMs,
      };
      this.patterns.set(action.type, created);
      return created;
    }

    const previousAvg = existing.averageDurationMs ?? action.durationMs ?? 0;
    const current = action.durationMs ?? previousAvg;

    // Confidence based on timing consistency.
    const denom = previousAvg === 0 ? 1 : previousAvg;
    const durationVariance = Math.abs(current - previousAvg) / denom;
    const newConfidence = existing.confidence * (1 - durationVariance * 0.5);

    const updated: InteractionPattern = {
      ...existing,
      frequency: existing.frequency + 1,
      averageDurationMs:
        (previousAvg * (existing.frequency - 1) + current) / existing.frequency,
      confidence: Math.max(0.1, Math.min(1, newConfidence)),
      lastDetected: action.timestamp,
      description: this.describeActionPattern(action),
    };

    this.patterns.set(action.type, updated);
    return updated;
  }

  private describeActionPattern(action: UserAction): string {
    switch (action.type) {
      case 'upload':
        return 'User uploaded files';
      case 'click':
        return `User clicked on ${action.target || 'an element'}`;
      case 'navigation':
        return `User navigated to ${action.target || 'a section'}`;
      case 'help_view':
        return `User viewed help: ${String(action.metadata?.helpTopicId ?? 'unknown')}`;
      case 'skip':
        return `User skipped content (step: ${String(action.metadata?.stepId ?? 'unknown')})`;
      case 'pause':
        return 'User paused tutorial';
      case 'export':
        return `User exported data (${String(action.metadata?.featureId ?? 'unknown')})`;
      default:
        return `User performed ${action.type} action`;
    }
  }

  /**
   * Track clicks for a UI element path.
   */
  trackClickStream(
    elementPath: string,
    coordinates: { x: number; y: number }[],
    scrollDepth?: number
  ): void {
    const existing: ClickStream = this.clickStreams.get(elementPath) || {
      coordinates: [],
      timestamps: [],
      elementPath,
    };

    existing.coordinates.push(...coordinates);
    existing.timestamps.push(Date.now());
    if (scrollDepth !== undefined) {
      existing.scrollDepth = scrollDepth;
    }

    this.clickStreams.set(elementPath, existing);
  }

  /**
   * Basic click-pattern analysis.
   */
  analyzeClickPatterns(elementPath: string): ClickPatternAnalysis {
    const result: ClickPatternAnalysis = {
      isIntentional: false,
      isHesitant: false,
      clickRate: 0,
      averageDepth: 0,
    };

    const stream = this.clickStreams.get(elementPath);
    if (!stream || stream.coordinates.length < 3) {
      return result;
    }

    const first = stream.timestamps[0];
    const last = stream.timestamps[stream.timestamps.length - 1];
    const timeSpanMs = Math.max(1, last - first);

    // clicks per minute
    result.clickRate = stream.coordinates.length / (timeSpanMs / 60000);
    result.averageDepth = stream.scrollDepth ?? 0;

    const xValues = stream.coordinates.map(c => c.x);
    const yValues = stream.coordinates.map(c => c.y);
    const xAvg = this.average(xValues);
    const yAvg = this.average(yValues);

    const xVariance =
      xValues.reduce((sum, val) => sum + Math.pow(val - xAvg, 2), 0) /
      xValues.length;
    const yVariance =
      yValues.reduce((sum, val) => sum + Math.pow(val - yAvg, 2), 0) /
      yValues.length;

    if (xVariance < 50 && yVariance < 50 && stream.coordinates.length > 10) {
      result.isIntentional = true;
      result.description = 'Systematic clicking pattern detected';
    } else if (result.clickRate < 2 && stream.coordinates.length < 5) {
      result.isHesitant = true;
      result.description = 'User appears to be hesitant (slow, deliberate clicks)';
    }

    return result;
  }

  getAllPatterns(): InteractionPattern[] {
    return Array.from(this.patterns.values());
  }

  getPatternsByType(type: string): InteractionPattern | null {
    return this.patterns.get(type) || null;
  }

  clearOldClickStreams(): void {
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    this.clickStreams.forEach((stream, elementPath) => {
      if (stream.timestamps[0] && stream.timestamps[0] < oneHourAgo) {
        this.clickStreams.delete(elementPath);
      }
    });
  }

  detectUserIntent(): { exploring: boolean; learning: boolean; expert: boolean } {
    const uploadActions = this.patterns.get('upload');
    const helpActions = this.patterns.get('help_view');

    const expert = Boolean(uploadActions && uploadActions.frequency >= 5);
    const learning = Boolean(helpActions && helpActions.frequency >= 3);
    const exploring = this.clickStreams.size > 0 || Boolean(this.patterns.get('navigation'));

    return { exploring, learning, expert };
  }

  private average(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((sum, v) => sum + v, 0) / values.length;
  }
}

export const interactionAnalyzer = new InteractionAnalyzer();
