/**
 * Sample File Loader - Fetch and manage sample files
 */

import { SAMPLE_FILES, type SampleFile } from './sample-library';

export interface SampleLoadResult {
  sample: SampleFile;
  loaded: boolean;
  error?: string;
  loadTime: number;
}

export interface SampleUsageAnalytics {
  sampleId: string;
  loadCount: number;
  lastLoaded: number;
  averageRating?: number;
  completionRate?: number;
}

/**
 * Load sample file by ID
 */
export async function loadSampleFile(
  sampleId: string
): Promise<SampleLoadResult> {
  const startTime = performance.now();

  try {
    const sample = SAMPLE_FILES.find(s => s.id === sampleId);

    if (!sample) {
      throw new Error(`Sample file not found: ${sampleId}`);
    }

    // Simulate network delay for realistic experience
    await new Promise(resolve => setTimeout(resolve, 300));

    const loadTime = performance.now() - startTime;

    // Track analytics
    trackSampleLoad(sampleId, loadTime);

    return {
      sample,
      loaded: true,
      loadTime,
    };
  } catch (error) {
    const loadTime = performance.now() - startTime;

    return {
      sample: {} as SampleFile,
      loaded: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      loadTime,
    };
  }
}

/**
 * Load multiple sample files
 */
export async function loadSampleFiles(
  sampleIds: string[]
): Promise<SampleLoadResult[]> {
  const results = await Promise.all(sampleIds.map(id => loadSampleFile(id)));

  return results;
}

/**
 * Get sample usage analytics from localStorage
 */
export function getSampleAnalytics(
  sampleId: string
): SampleUsageAnalytics | null {
  try {
    const analyticsData = localStorage.getItem(`sample_analytics_${sampleId}`);
    if (!analyticsData) {
      return null;
    }

    return JSON.parse(analyticsData) as SampleUsageAnalytics;
  } catch {
    return null;
  }
}

/**
 * Track sample file load
 */
function trackSampleLoad(sampleId: string, loadTime: number): void {
  try {
    const existing = getSampleAnalytics(sampleId) || {
      sampleId,
      loadCount: 0,
      lastLoaded: 0,
    };

    const updated: SampleUsageAnalytics = {
      ...existing,
      loadCount: existing.loadCount + 1,
      lastLoaded: Date.now(),
    };

    localStorage.setItem(
      `sample_analytics_${sampleId}`,
      JSON.stringify(updated)
    );
  } catch (error) {
    console.error('[SampleLoader] Failed to track sample load:', error);
  }
}

/**
 * Rate sample file (1-5 stars)
 */
export function rateSampleFile(sampleId: string, rating: number): void {
  if (rating < 1 || rating > 5) {
    throw new Error('Rating must be between 1 and 5');
  }

  try {
    const existing = getSampleAnalytics(sampleId) || {
      sampleId,
      loadCount: 0,
      lastLoaded: 0,
    };

    const updated: SampleUsageAnalytics = {
      ...existing,
      averageRating: calculateNewRating(
        existing.averageRating,
        existing.loadCount,
        rating
      ),
    };

    localStorage.setItem(
      `sample_analytics_${sampleId}`,
      JSON.stringify(updated)
    );
  } catch (error) {
    console.error('[SampleLoader] Failed to rate sample:', error);
  }
}

/**
 * Calculate new average rating
 */
function calculateNewRating(
  currentRating: number | undefined,
  ratingCount: number,
  newRating: number
): number {
  if (currentRating === undefined) {
    return newRating;
  }

  return (currentRating * ratingCount + newRating) / (ratingCount + 1);
}

/**
 * Get most popular samples
 */
export function getPopularSamples(limit = 5): SampleFile[] {
  const sampleAnalytics: Array<{ sampleId: string; loadCount: number }> = [];

  SAMPLE_FILES.forEach(sample => {
    const analytics = getSampleAnalytics(sample.id);
    if (analytics) {
      sampleAnalytics.push({
        sampleId: sample.id,
        loadCount: analytics.loadCount,
      });
    }
  });

  sampleAnalytics.sort((a, b) => b.loadCount - a.loadCount);

  const popularSampleIds = sampleAnalytics.slice(0, limit).map(s => s.sampleId);
  return popularSampleIds
    .map(id => SAMPLE_FILES.find(s => s.id === id))
    .filter((sample): sample is SampleFile => sample !== undefined);
}

/**
 * Get recommended samples based on usage
 */
export function getRecommendedSamplesByUsage(limit = 3): SampleFile[] {
  const recommended = new Set<string>();

  // Add highly-rated samples
  SAMPLE_FILES.forEach(sample => {
    const analytics = getSampleAnalytics(sample.id);
    if (analytics && analytics.averageRating && analytics.averageRating >= 4) {
      recommended.add(sample.id);
    }
  });

  // Add popular samples
  const popular = getPopularSamples(limit * 2);
  popular.forEach(sample => {
    recommended.add(sample.id);
  });

  // Add diverse categories
  const categories = new Set<string>();
  SAMPLE_FILES.forEach(sample => {
    if (recommended.size >= limit) return;
    if (!categories.has(sample.category)) {
      recommended.add(sample.id);
      categories.add(sample.category);
    }
  });

  return Array.from(recommended)
    .map(id => SAMPLE_FILES.find(s => s.id === id))
    .filter((sample): sample is SampleFile => sample !== undefined)
    .slice(0, limit);
}
