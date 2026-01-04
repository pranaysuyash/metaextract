import React from 'react';
import { Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

interface QualityMetrics {
  confidence_score: number;
  extraction_completeness: number;
  processing_efficiency: number;
  format_support_level: string;
  recommended_actions: string[];
  enhanced_extraction: boolean;
  streaming_enabled: boolean;
}

interface ProcessingInsights {
  total_fields_extracted: number;
  processing_time_ms: number;
  memory_usage_mb: number;
  streaming_enabled: boolean;
  fallback_extraction: boolean;
}

interface QualityIndicatorProps {
  qualityMetrics?: QualityMetrics;
  processingInsights?: ProcessingInsights;
  className?: string;
}

export function QualityIndicator({ 
  qualityMetrics, 
  processingInsights, 
  className 
}: QualityIndicatorProps) {
  const hasProcessingInsights =
    !!processingInsights &&
    (processingInsights.processing_time_ms > 0 ||
      processingInsights.total_fields_extracted > 0 ||
      processingInsights.memory_usage_mb > 0);
  const hasQualityMetrics =
    !!qualityMetrics &&
    (qualityMetrics.confidence_score > 0 ||
      qualityMetrics.extraction_completeness > 0 ||
      !!qualityMetrics.format_support_level);

  if (!hasQualityMetrics && !hasProcessingInsights) {
    return null;
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-500';
    if (score >= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getConfidenceIcon = (score: number) => {
    if (score >= 0.8) return <CheckCircle className="w-4 h-4" />;
    if (score >= 0.6) return <AlertTriangle className="w-4 h-4" />;
    return <Info className="w-4 h-4" />;
  };

  const getFormatSupportBadge = (level: string) => {
    const colors = {
      'comprehensive': 'bg-green-100 text-green-800',
      'advanced': 'bg-blue-100 text-blue-800',
      'basic': 'bg-yellow-100 text-yellow-800',
      'limited': 'bg-red-100 text-red-800'
    };
    
    return colors[level as keyof typeof colors] || colors.basic;
  };

  const formatTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatMemory = (mb: number) => {
    if (mb < 1) return `${(mb * 1024).toFixed(0)}KB`;
    return `${mb.toFixed(1)}MB`;
  };

  const supportLevelLabel = qualityMetrics?.format_support_level
    ? qualityMetrics.format_support_level.replace(/_/g, ' ')
    : '';

  const showCompleteness =
    !!qualityMetrics && qualityMetrics.extraction_completeness > 0;
  const showFieldsExtracted =
    !!processingInsights && processingInsights.total_fields_extracted > 0;
  const showProcessingTime =
    !!processingInsights && processingInsights.processing_time_ms > 0;
  const showMemoryUsage =
    !!processingInsights && processingInsights.memory_usage_mb > 0;

  return (
    <div className={cn("bg-white/5 backdrop-blur-sm rounded-lg border border-white/10 p-4 space-y-4", className)}>
      {/* Header */}
      <div className="flex items-center space-x-2">
        <Shield className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold text-white">Extraction Quality</h3>
        {qualityMetrics?.enhanced_extraction && (
          <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
            Enhanced
          </span>
        )}
      </div>
      {supportLevelLabel && (
        <p className="text-xs text-white/50">
          Format support: {supportLevelLabel}
        </p>
      )}

      {/* Quality Metrics */}
      {hasQualityMetrics && qualityMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Confidence Score */}
          <div className="bg-white/5 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-white/70">Confidence</span>
              <div className={getConfidenceColor(qualityMetrics.confidence_score)}>
                {getConfidenceIcon(qualityMetrics.confidence_score)}
              </div>
            </div>
            <div className="text-2xl font-bold text-white">
              {(qualityMetrics.confidence_score * 100).toFixed(0)}%
            </div>
            <div className="w-full bg-white/10 rounded-full h-2 mt-2">
              <div 
                className={`h-2 rounded-full ${qualityMetrics.confidence_score >= 0.8 ? 'bg-green-500' : qualityMetrics.confidence_score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'}`}
                style={{ width: `${qualityMetrics.confidence_score * 100}%` }}
              />
            </div>
          </div>

          {/* Extraction Completeness */}
          {showCompleteness ? (
            <div className="bg-white/5 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-white/70">Completeness</span>
                <CheckCircle className="w-4 h-4 text-blue-400" />
              </div>
              <div className="text-2xl font-bold text-white">
                {(qualityMetrics.extraction_completeness * 100).toFixed(0)}%
              </div>
              <div className="w-full bg-white/10 rounded-full h-2 mt-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${qualityMetrics.extraction_completeness * 100}%` }}
                />
              </div>
            </div>
          ) : (
            <div className="bg-white/5 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-white/70">Completeness</span>
                <Info className="w-4 h-4 text-white/40" />
              </div>
              <div className="text-lg font-semibold text-white">Not reported</div>
              <div className="text-xs text-white/40 mt-1">Depends on file metadata</div>
            </div>
          )}

          {/* Format Support Level */}
          {qualityMetrics.format_support_level && (
            <div className="bg-white/5 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-white/70">Support Level</span>
                <span className={`px-2 py-1 text-xs rounded-full ${getFormatSupportBadge(qualityMetrics.format_support_level)}`}>
                  {qualityMetrics.format_support_level}
                </span>
              </div>
              {qualityMetrics.streaming_enabled && (
                <div className="text-sm text-green-400 flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span>Streaming Enabled</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Processing Insights */}
      {hasProcessingInsights && processingInsights && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Processing Time */}
          {showProcessingTime && (
            <div className="bg-white/5 rounded-lg p-3">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full" />
                <span className="text-sm text-white/70">Processing Time</span>
              </div>
              <div className="text-lg font-semibold text-white">
                {formatTime(processingInsights.processing_time_ms)}
              </div>
              {processingInsights.streaming_enabled && (
                <div className="text-xs text-green-400 mt-1">Optimized with streaming</div>
              )}
            </div>
          )}

          {/* Fields Extracted */}
          {showFieldsExtracted && (
            <div className="bg-white/5 rounded-lg p-3">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full" />
                <span className="text-sm text-white/70">Fields Extracted</span>
              </div>
              <div className="text-lg font-semibold text-white">
                {processingInsights.total_fields_extracted.toLocaleString()}
              </div>
              <div className="text-xs text-white/50 mt-1">Comprehensive metadata</div>
            </div>
          )}

          {/* Memory Usage */}
          {showMemoryUsage && (
            <div className="bg-white/5 rounded-lg p-3">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 bg-orange-400 rounded-full" />
                <span className="text-sm text-white/70">Memory Used</span>
              </div>
              <div className="text-lg font-semibold text-white">
                {formatMemory(processingInsights.memory_usage_mb)}
              </div>
              {processingInsights.streaming_enabled && (
                <div className="text-xs text-green-400 mt-1">Memory optimized</div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Recommended Actions */}
      {qualityMetrics?.recommended_actions && qualityMetrics.recommended_actions.length > 0 && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            <span className="text-sm font-medium text-yellow-400">Recommendations</span>
          </div>
          <ul className="text-sm text-white/80 space-y-1">
            {qualityMetrics.recommended_actions.map((action, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-1 h-1 bg-yellow-400 rounded-full mt-2 flex-shrink-0" />
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Fallback Warning */}
      {processingInsights?.fallback_extraction && (
        <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-orange-400" />
            <span className="text-sm font-medium text-orange-400">Fallback Mode</span>
          </div>
          <p className="text-sm text-white/80 mt-2">
            Used basic extraction due to compatibility issues. Enhanced features may be limited.
          </p>
        </div>
      )}
    </div>
  );
}
