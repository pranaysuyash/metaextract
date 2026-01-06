/**
 * Extraction Progress Tracker Component
 * Real-time progress updates during metadata extraction
 */

import React from 'react';

interface ExtractionProgress {
  stage: string;
  progress: number;
  message: string;
  estimatedTimeRemaining?: number;
  currentOperation: string;
  completedOperations: string[];
  errors: string[];
}

interface ProgressTrackerProps {
  extractionId: string;
  onComplete: (result: any) => void;
  onError: (error: string) => void;
}

/**
 * DEPRECATED: ExtractionProgressTracker
 *
 * This implementation has been temporarily disabled in favor of the
 * images-mvp specific `ProgressTracker` component located at:
 * `client/src/components/images-mvp/progress-tracker.tsx`.
 *
 * Reason: Using both components caused duplicate progress UIs in the
 * Images MVP flow. To avoid regressions while we consolidate the
 * logic, this component now exports a no-op placeholder that returns
 * `null` and logs a deprecation warning. Keep the file for future
 * refactor and re-implementation if needed.
 */
/**
 * Deprecated and removed
 *
 * ExtractionProgressTracker was intentionally removed and replaced by
 * `client/src/components/images-mvp/progress-tracker.tsx`. This file no
 * longer exports a React component to avoid accidental imports and the
 * duplicate progress UI issue. Keep this file as documentation of the
 * previous implementation; do not import `ExtractionProgressTracker`.
 */

// NOTE: QualityIndicators and helpers remain available in this file if
// needed in future, but the ExtractionProgressTracker component has been
// removed on purpose.


// Quality Indicators Component
export function QualityIndicators({ metadata }: { metadata: any }) {
  const getQualityScore = () => {
    if (!metadata) return 0;

    let score = 100;

    // Deduct for missing critical fields
    if (!metadata.gps) score -= 10;
    if (!metadata.exif || Object.keys(metadata.exif).length < 5) score -= 15;
    if (!metadata.iptc) score -= 5;
    if (!metadata.xmp) score -= 5;

    // Award for comprehensive data
    if (metadata.ai_quality_assessment) score += 5;
    if (metadata.perceptual_hashes) score += 5;
    if (metadata.specialized_modules) score += 10;

    return Math.min(100, Math.max(0, score));
  };

  const getQualityLevel = (score: number) => {
    if (score >= 90) return { level: 'Excellent', color: 'green' };
    if (score >= 70) return { level: 'Good', color: 'blue' };
    if (score >= 50) return { level: 'Fair', color: 'yellow' };
    return { level: 'Poor', color: 'red' };
  };

  const score = getQualityScore();
  const { level, color } = getQualityLevel(score);

  return (
    <div className="flex items-center gap-4">
      <div className="text-center">
        <div className={`text-3xl font-bold text-${color}-600`}>{score}</div>
        <div className="text-xs text-gray-500">Quality Score</div>
      </div>
      <div
        className={`px-3 py-1 rounded-full bg-${color}-100 text-${color}-800 text-sm font-medium`}
      >
        {level}
      </div>
      <div className="flex-1">
        <div className="flex gap-2 text-xs">
          <QualityBadge present={!!metadata.gps} label="GPS" />
          <QualityBadge present={!!metadata.exif} label="EXIF" />
          <QualityBadge present={!!metadata.iptc} label="IPTC" />
          <QualityBadge present={!!metadata.xmp} label="XMP" />
          <QualityBadge present={!!metadata.ai_quality_assessment} label="AI" />
        </div>
      </div>
    </div>
  );
}

function QualityBadge({ present, label }: { present: boolean; label: string }) {
  return (
    <span
      className={`px-2 py-1 rounded ${
        present ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-400'
      }`}
    >
      {label}
    </span>
  );
}
