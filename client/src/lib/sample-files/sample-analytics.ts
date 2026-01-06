/**
 * Sample Analytics - Track sample file usage and metrics
 */

import { getSampleAnalytics, rateSampleFile } from './sample-loader';

export interface SampleMetrics {
  totalLoads: number;
  totalSamples: number;
  averageLoadTime: number;
  completionRate: number;
  topCategories: Array<{ category: string; count: number }>;
  topSamples: Array<{
    sampleId: string;
    loadCount: number;
    averageRating?: number;
  }>;
}

export interface SampleCompletionEvent {
  sampleId: string;
  completed: boolean;
  timeSpent: number; // milliseconds
  completedSteps: number;
  totalSteps: number;
}

/**
 * Initialize sample analytics tracking
 */
export function initializeSampleAnalytics(): void {
  // Initialize storage if not present
  if (!localStorage.getItem('sample_analytics_initialized')) {
    localStorage.setItem('sample_analytics_initialized', 'true');
    console.log('[SampleAnalytics] Initialized');
  }
}

/**
 * Record sample completion event
 */
export function recordSampleCompletion(event: SampleCompletionEvent): void {
  try {
    const events = getCompletionEvents();
    events.push({
      ...event,
      timestamp: Date.now(),
    });

    localStorage.setItem(
      'sample_completion_events',
      JSON.stringify(events.slice(-100))
    ); // Keep last 100
  } catch (error) {
    console.error('[SampleAnalytics] Failed to record completion:', error);
  }
}

/**
 * Get completion events
 */
function getCompletionEvents(): Array<
  SampleCompletionEvent & { timestamp: number }
> {
  try {
    const stored = localStorage.getItem('sample_completion_events');
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

/**
 * Get overall sample metrics
 */
export function getSampleMetrics(): SampleMetrics {
  const completionEvents = getCompletionEvents();
  const sampleAnalytics = getAllSampleAnalytics();

  const totalLoads = completionEvents.length;
  const averageLoadTime =
    totalLoads > 0
      ? completionEvents.reduce((sum, event) => sum + event.timeSpent, 0) /
        totalLoads
      : 0;

  const completions = completionEvents.filter(e => e.completed);
  const completionRate =
    totalLoads > 0 ? (completions.length / totalLoads) * 100 : 0;

  // Category breakdown
  const categoryCounts = new Map<string, number>();
  completionEvents.forEach(event => {
    // In a real implementation, we'd need to fetch the sample to get its category
    // For now, we'll count by sample ID
    const count = categoryCounts.get(event.sampleId) || 0;
    categoryCounts.set(event.sampleId, count + 1);
  });

  const topCategories = Array.from(categoryCounts.entries())
    .map(([category, count]) => ({ category, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  return {
    totalLoads,
    totalSamples: sampleAnalytics.length,
    averageLoadTime,
    completionRate,
    topCategories,
    topSamples: sampleAnalytics.slice(0, 5),
  };
}

/**
 * Get all sample analytics
 */
function getAllSampleAnalytics(): Array<{
  sampleId: string;
  loadCount: number;
  lastLoaded: number;
  averageRating?: number;
}> {
  const analytics: Array<{
    sampleId: string;
    loadCount: number;
    lastLoaded: number;
    averageRating?: number;
  }> = [];

  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith('sample_analytics_')) {
      const sampleId = key.replace('sample_analytics_', '');
      const data = getSampleAnalytics(sampleId);
      if (data) {
        analytics.push(data);
      }
    }
  }

  return analytics.sort((a, b) => b.loadCount - a.loadCount);
}

/**
 * Get user proficiency level based on sample usage
 */
export function getUserProficiencyLevel():
  | 'beginner'
  | 'intermediate'
  | 'advanced' {
  const metrics = getSampleMetrics();

  if (metrics.totalLoads < 5) {
    return 'beginner';
  }

  if (metrics.totalLoads < 15 || metrics.completionRate < 70) {
    return 'intermediate';
  }

  return 'advanced';
}

/**
 * Get sample difficulty progression
 */
export function getDifficultyProgression(): {
  beginner: number;
  intermediate: number;
  advanced: number;
} {
  const completionEvents = getCompletionEvents();
  const progression = {
    beginner: 0,
    intermediate: 0,
    advanced: 0,
  };

  completionEvents.forEach(event => {
    // In a real implementation, we'd look up the sample's difficulty
    // For now, we'll use completion rate as proxy
    if (event.completed) {
      if (event.totalSteps > 8) {
        progression.advanced++;
      } else if (event.totalSteps > 5) {
        progression.intermediate++;
      } else {
        progression.beginner++;
      }
    }
  });

  return progression;
}

/**
 * Reset sample analytics
 */
export function resetSampleAnalytics(): void {
  const keysToRemove: string[] = [];

  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key?.startsWith('sample_analytics_')) {
      keysToRemove.push(key);
    }
  }

  keysToRemove.forEach(key => localStorage.removeItem(key));
  localStorage.removeItem('sample_completion_events');
  localStorage.removeItem('sample_analytics_initialized');

  console.log('[SampleAnalytics] Reset all analytics');
}

/**
 * Export analytics as JSON
 */
export function exportAnalytics(): string {
  const metrics = getSampleMetrics();
  const completionEvents = getCompletionEvents();

  return JSON.stringify(
    {
      metrics,
      completionEvents,
      exportedAt: new Date().toISOString(),
    },
    null,
    2
  );
}
