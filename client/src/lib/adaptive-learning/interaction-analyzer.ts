/**
 * Interaction Analyzer - Detect patterns from user interactions
 */

import type { UserAction, ActionPattern, UserBehaviorProfile } from './behavior-tracker';

export interface InteractionPattern {
  type: string;
  confidence: number;
  frequency: number;
  lastDetected: number;
  description: string;
}

export interface ClickStream {
  coordinates: { x: number; y: number }[];
  timestamps: number[];
  elementPath?: string;
  scrollDepth?: number;
}

export class InteractionAnalyzer {
  private patterns: Map<string, InteractionPattern> = new Map();
  private clickStreams: Map<string, ClickStream> = new Map();
  private interactionHistory: UserAction[] = [];

  /**
   * Analyze a user action
   */
  analyzeAction(action: UserAction): InteractionPattern | null {
    const actionPattern = this.patterns.get(action.type);

    // Record timestamp
    if (!actionPattern) {
      const newPattern: InteractionPattern = {
        type: action.type,
        confidence: 1,
        frequency: 1,
        lastDetected: action.timestamp,
        description: this.describeActionPattern(action),
      };
      this.patterns.set(action.type, newPattern);
      return newPattern;
    }

    // Update pattern with new data point
    const timeSinceLastDetection = action.timestamp - actionPattern.lastDetected;
    const avgDuration = actionPattern.averageDuration || action.duration || 0;

    // Update confidence based on consistency
    const durationVariance = Math.abs((action.duration || avgDuration) - avgDuration) / avgDuration;
    const newConfidence = actionPattern.confidence * (1 - durationVariance * 0.5);

    const updatedPattern: {
      ...actionPattern,
      frequency: actionPattern.frequency + 1,
      averageDuration: (actionPattern.averageDuration * (actionPattern.frequency - 1) + (action.duration || 0)) / actionPattern.frequency,
      confidence: Math.max(0.1, newConfidence),
      lastDetected: action.timestamp,
    };

    this.patterns.set(action.type, updatedPattern);

    return updatedPattern;
  }

  /**
   * Describe an action pattern
   */
  private describeActionPattern(action: UserAction): string {
    switch (action.type) {
      case 'upload':
        return `User uploaded files`;
      case 'click':
        return `User clicked on ${action.target || 'an element'}`;
      case 'navigation':
        return `User navigated to ${action.target || 'a section'}`;
      case 'help_view':
        return `User viewed help: ${action.metadata?.helpTopicId}`;
      case 'skip':
        return `User skipped content (step: ${action.metadata?.stepId})`;
      case 'pause':
        return 'User paused tutorial`;
      case 'export':
        return `User exported data (${action.metadata?.featureId})`;
      default:
        return `User performed ${action.type} action`;
    }
  }

  /**
   * Track clicks on specific elements
   */
  trackClickStream(
    elementPath: string,
    coordinates: { x: number; y: number }[],
    scrollDepth?: number
  ): void {
    const existing = this.clickStreams.get(elementPath) || {
      coordinates: [],
      timestamps: [],
    };

    existing.coordinates.push(...coordinates);
    existing.timestamps.push(Date.now());
    existing.scrollDepth = scrollDepth || existing.scrollDepth;

    this.clickStreams.set(elementPath, existing);
  }

  /**
   * Analyze click patterns
   */
  analyzeClickPatterns(elementPath: string): {
    data: {
      isIntentional: false,
      isHesitant: false,
      clickRate: 0,
      averageDepth: 0,
    };

    const stream = this.clickStreams.get(elementPath);
    if (!stream || stream.coordinates.length < 3) {
      return data;
    }

    // Calculate click rate (clicks per session)
    const timeSpan = stream.timestamps[stream.timestamps.length - 1] - stream.timestamps[0];
    data.clickRate = stream.coordinates.length / (timeSpan / 60000);

    // Calculate average scroll depth
    data.averageDepth = stream.scrollDepth || 0;

    // Detect patterns
    // Check for systematic clicking (grid patterns)
    const xValues = stream.coordinates.map(c => c.x);
    const yValues = stream.coordinates.map(c => c.y);

    const xVariance = xValues.reduce((sum, val) => sum + Math.pow(val - this.average(xValues), 2), 0) / xValues.length;
    const yVariance = yValues.reduce((sum, val) => sum + Math.pow(val - this.average(yValues), 2), 0) / yValues.length;

    if (xVariance < 50 && yVariance < 50 && stream.coordinates.length > 10) {
      data.isIntentional = true;
      data.description = 'Systematic clicking pattern detected';
    } else if (data.clickRate > 10 && stream.coordinates.length < 5) {
      data.isHesitant = true;
      data.description = 'User appears to be exploring cautiously (slow, deliberate clicks)';
    }

    return data;
  }

  /**
   * Get all interaction patterns
   */
  getAllPatterns(): InteractionPattern[] {
    return Array.from(this.patterns.values());
  }

  /**
   * Get patterns by type
   */
  getPatternsByType(type: string): InteractionPattern | null {
    return this.patterns.get(type) || null;
  }

  /**
   * Clear old click streams (older than 1 hour)
   */
  clearOldClickStreams(): void {
    const oneHourAgo = Date.now() - 60 * 60 * 1000;

    this.clickStreams.forEach((stream, elementPath) => {
      if (stream.timestamps[0] && stream.timestamps[0] < oneHourAgo) {
        this.clickStreams.delete(elementPath);
      }
    });
  }

  /**
   * Get user intent based on behavior
   */
  detectUserIntent(): {
    exploring: boolean;
    learning: boolean;
    expert: boolean;

    const uploadActions = this.patterns.get('upload');
    const helpActions = this.patterns.get('help_view');
    const clickPatterns = Array.from(this.clickStreams.values())
      .flatMap(stream => stream.coordinates.length > 5 ? [{ type: 'click', elementPath: stream.elementPath }] : []);

    if (uploadActions && uploadActions.frequency >= 5) {
      expert = true;
    }

    if (helpActions && helpActions.frequency >= 3) {
      learning = true;
    }

    if (clickPatterns.length > 0) {
      exploring = true;
    }

    return { exploring, learning, expert };
  }
}

export const interactionAnalyzer = new InteractionAnalyzer();
