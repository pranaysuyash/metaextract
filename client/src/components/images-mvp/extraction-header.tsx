import React from 'react';
import { ProgressBar } from './progress-bar';

export interface QualityMetrics {
  confidence_score?: number; // 0..1
  extraction_completeness?: number; // 0..1
}

export function ExtractionHeader({
  percentage = 0,
  stage = 'starting',
  qualityMetrics,
  compact = false,
}: {
  percentage?: number;
  stage?: string;
  qualityMetrics?: QualityMetrics | null;
  compact?: boolean;
}) {
  const pct = Math.min(100, Math.max(0, percentage));

  return (
    <div
      className={`w-full rounded-lg border border-white/10 p-3 bg-[#11121a] ${compact ? 'mb-3' : 'mb-4'}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-slate-200">
            Extracting Metadata...
          </div>
          <div className="text-xs text-slate-400 font-mono mt-1">{stage}</div>
        </div>
        <div className="text-sm font-mono text-slate-200">
          {pct.toFixed(0)}%
        </div>
      </div>

      <div className="mt-3">
        <ProgressBar percentage={pct} className="h-3 rounded-md" />
      </div>

      {qualityMetrics && (
        <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-slate-300">
          <div className="text-center">
            <div className="text-[10px] text-slate-400">Confidence</div>
            <div className="text-sm font-semibold text-slate-200">
              {typeof qualityMetrics.confidence_score === 'number'
                ? `${Math.round(qualityMetrics.confidence_score * 100)}%`
                : '—'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-[10px] text-slate-400">Completeness</div>
            <div className="text-sm font-semibold text-slate-200">
              {typeof qualityMetrics.extraction_completeness === 'number'
                ? `${Math.round(qualityMetrics.extraction_completeness * 100)}%`
                : '—'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
