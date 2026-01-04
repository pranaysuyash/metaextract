/**
 * Extraction Progress Tracker Component
 * Real-time progress updates during metadata extraction
 */

import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';

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

export function ExtractionProgressTracker({
  extractionId,
  onComplete,
  onError
}: ProgressTrackerProps) {
  const [progress, setProgress] = useState<ExtractionProgress | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:5000/ws/progress/${extractionId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data);

      if (data.stage === 'complete') {
        setIsComplete(true);
        onComplete(data.result);
      } else if (data.stage === 'error') {
        onError(data.errors[0] || 'Extraction failed');
      }
    };

    ws.onerror = () => {
      onError('WebSocket connection failed');
    };

    return () => ws.close();
  }, [extractionId, onComplete, onError]);

  if (!progress) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
          <div>
            <h3 className="font-medium">Initializing extraction...</h3>
            <p className="text-sm text-gray-500">Preparing your image for analysis</p>
          </div>
        </div>
      </Card>
    );
  }

  if (isComplete) {
    return (
      <Card className="p-6 bg-green-50 border-green-500">
        <div className="flex items-center gap-4">
          <div className="text-green-500 text-4xl">✅</div>
          <div>
            <h3 className="font-medium text-green-800">Extraction Complete!</h3>
            <p className="text-sm text-green-600">
              {progress.completedOperations.length} operations completed successfully
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Progress Bar */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-medium">{progress.currentOperation}</h3>
            <span className="text-sm text-gray-500">{progress.progress.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress.progress}%` }}
            />
          </div>
        </div>

        {/* Stage Information */}
        <div className="flex items-center gap-2 text-sm">
          <span className="font-medium">Stage:</span>
          <span className="text-gray-600">{progress.stage}</span>
          {progress.estimatedTimeRemaining && (
            <>
              <span className="text-gray-400">•</span>
              <span className="text-gray-600">
                ~{progress.estimatedTimeRemaining}s remaining
              </span>
            </>
          )}
        </div>

        {/* Current Message */}
        <p className="text-sm text-gray-600">{progress.message}</p>

        {/* Completed Operations */}
        {progress.completedOperations.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Completed Operations:</h4>
            <div className="space-y-1">
              {progress.completedOperations.map((op, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <span className="text-green-500">✓</span>
                  <span className="text-gray-600">{op}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Errors */}
        {progress.errors.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <h4 className="text-sm font-medium text-yellow-800 mb-1">Warnings:</h4>
            {progress.errors.map((error, index) => (
              <p key={index} className="text-sm text-yellow-700">{error}</p>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}

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
      <div className={`px-3 py-1 rounded-full bg-${color}-100 text-${color}-800 text-sm font-medium`}>
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
        present
          ? 'bg-green-100 text-green-800'
          : 'bg-gray-100 text-gray-400'
      }`}
    >
      {label}
    </span>
  );
}