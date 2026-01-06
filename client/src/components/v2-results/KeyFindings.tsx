/**
 * Key Findings Component
 *
 * Displays the most important information extracted from metadata in plain English.
 * Enhanced with forensic analysis integration and visual indicators.
 */

import React from 'react';
import {
  Clock,
  MapPin,
  Camera,
  Shield,
  Info,
  Fingerprint,
  AlertTriangle,
  Verified,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { KeyFindings as KeyFindingsType } from '@/utils/metadataTransformers';
import {
  AuthenticityBadge,
  ForensicConfidenceIndicator,
} from './AuthenticityBadge';

export interface KeyFindingsProps {
  findings: KeyFindingsType;
  forensicScore?: number;
  forensicAnalysis?: {
    steganography?: { detected: boolean; confidence: number };
    manipulation?: { detected: boolean; confidence: number };
    aiDetection?: { aiGenerated: boolean; confidence: number };
  };
  className?: string;
  showForensicIndicators?: boolean;
  compact?: boolean;
}

interface FindingCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  confidence?: 'high' | 'medium' | 'low';
  color?: 'blue' | 'green' | 'purple' | 'red' | 'yellow' | 'forensic';
  forensicIndicator?: boolean;
  riskLevel?: 'low' | 'medium' | 'high';
}

interface ConfidenceBadgeProps {
  confidence: 'high' | 'medium' | 'low';
  forensic?: boolean;
}

interface ConfidenceInfoProps {
  confidence: 'high' | 'medium' | 'low';
  forensic?: boolean;
}

interface ForensicSummaryProps {
  score?: number;
  analysis?: {
    steganography?: { detected: boolean; confidence: number };
    manipulation?: { detected: boolean; confidence: number };
    aiDetection?: { aiGenerated: boolean; confidence: number };
  };
  compact?: boolean;
}

/**
 * Forensic Summary Component
 * Displays forensic analysis results in a compact format
 */
const ForensicSummary: React.FC<ForensicSummaryProps> = ({
  score = 0,
  analysis,
  compact = false,
}) => {
  if (!analysis) return null;

  const { steganography, manipulation, aiDetection } = analysis;
  const hasForensicData = !!(steganography || manipulation || aiDetection);

  if (!hasForensicData) return null;

  const getRiskColor = () => {
    const risks = [
      steganography?.detected,
      manipulation?.detected,
      aiDetection?.aiGenerated,
    ].filter(Boolean).length;

    if (risks === 0) return 'text-emerald-500';
    if (risks === 1) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <Fingerprint className={cn('w-3 h-3', getRiskColor())} />
        <span className="text-xs text-gray-600 dark:text-gray-400">
          Forensic: {score}%
        </span>
      </div>
    );
  }

  return (
    <div className="p-4 rounded-lg bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 border border-slate-200 dark:border-slate-700">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Fingerprint className={cn('w-4 h-4', getRiskColor())} />
          <h4 className="font-medium text-gray-900 dark:text-white">
            Forensic Analysis
          </h4>
        </div>
        <AuthenticityBadge score={score} variant="compact" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {steganography && (
          <div className="flex items-center justify-between p-2 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700">
            <span className="text-xs text-gray-600 dark:text-gray-400">
              Steganography
            </span>
            <ForensicConfidenceIndicator
              confidence={steganography.confidence}
              type="manipulation"
              size="sm"
              showLabel={false}
            />
          </div>
        )}

        {manipulation && (
          <div className="flex items-center justify-between p-2 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700">
            <span className="text-xs text-gray-600 dark:text-gray-400">
              Manipulation
            </span>
            <ForensicConfidenceIndicator
              confidence={manipulation.confidence}
              type="manipulation"
              size="sm"
              showLabel={false}
            />
          </div>
        )}

        {aiDetection && (
          <div className="flex items-center justify-between p-2 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700">
            <span className="text-xs text-gray-600 dark:text-gray-400">
              AI Detection
            </span>
            <ForensicConfidenceIndicator
              confidence={aiDetection.confidence}
              type="ai-detection"
              size="sm"
              showLabel={false}
            />
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Enhanced Finding Card with forensic indicators
 */
function FindingCard({
  icon,
  label,
  value,
  confidence,
  color = 'blue',
  forensicIndicator = false,
  riskLevel = 'low',
}: FindingCardProps): React.ReactElement {
  const getForensicColor = () => {
    if (forensicIndicator) {
      switch (riskLevel) {
        case 'high':
          return 'bg-red-50 dark:bg-red-950';
        case 'medium':
          return 'bg-yellow-50 dark:bg-yellow-950';
        case 'low':
          return 'bg-emerald-50 dark:bg-emerald-950';
        default:
          return 'bg-slate-50 dark:bg-slate-950';
      }
    }
    return color === 'blue'
      ? 'bg-blue-50 dark:bg-blue-950'
      : color === 'green'
        ? 'bg-green-50 dark:bg-green-950'
        : color === 'purple'
          ? 'bg-purple-50 dark:bg-purple-950'
          : color === 'red'
            ? 'bg-red-50 dark:bg-red-950'
            : color === 'yellow'
              ? 'bg-yellow-50 dark:bg-yellow-950'
              : 'bg-slate-50 dark:bg-slate-950';
  };

  const getBorderColor = () => {
    if (forensicIndicator) {
      switch (riskLevel) {
        case 'high':
          return 'border-red-200 dark:border-red-800';
        case 'medium':
          return 'border-yellow-200 dark:border-yellow-800';
        case 'low':
          return 'border-emerald-200 dark:border-emerald-800';
        default:
          return 'border-slate-200 dark:border-slate-800';
      }
    }
    return color === 'blue'
      ? 'border-blue-200 dark:border-blue-800'
      : color === 'green'
        ? 'border-green-200 dark:border-green-800'
        : color === 'purple'
          ? 'border-purple-200 dark:border-purple-800'
          : color === 'red'
            ? 'border-red-200 dark:border-red-800'
            : color === 'yellow'
              ? 'border-yellow-200 dark:border-yellow-800'
              : 'border-slate-200 dark:border-slate-800';
  };

  const getIconColor = () => {
    if (forensicIndicator) {
      switch (riskLevel) {
        case 'high':
          return 'text-red-600 dark:text-red-400';
        case 'medium':
          return 'text-yellow-600 dark:text-yellow-400';
        case 'low':
          return 'text-emerald-600 dark:text-emerald-400';
        default:
          return 'text-slate-600 dark:text-slate-400';
      }
    }
    return color === 'blue'
      ? 'text-blue-600 dark:text-blue-400'
      : color === 'green'
        ? 'text-green-600 dark:text-green-400'
        : color === 'purple'
          ? 'text-purple-600 dark:text-purple-400'
          : color === 'red'
            ? 'text-red-600 dark:text-red-400'
            : color === 'yellow'
              ? 'text-yellow-600 dark:text-yellow-400'
              : 'text-slate-600 dark:text-slate-400';
  };

  return (
    <div
      className={cn(
        'p-4 rounded-lg border',
        getForensicColor(),
        getBorderColor()
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn('mt-1', getIconColor())}>{icon}</div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {label}
          </p>
          <p
            className={cn(
              'font-semibold text-gray-900 dark:text-white mt-1',
              forensicIndicator && 'flex items-center gap-2'
            )}
          >
            {value}
            {forensicIndicator && riskLevel === 'high' && (
              <AlertTriangle className="w-4 h-4 text-red-500" />
            )}
            {forensicIndicator && riskLevel === 'low' && (
              <Verified className="w-4 h-4 text-emerald-500" />
            )}
          </p>
        </div>
        {confidence && (
          <ConfidenceBadge
            confidence={confidence}
            forensic={forensicIndicator}
          />
        )}
      </div>
    </div>
  );
}

/**
 * Enhanced Confidence Badge with forensic styling
 */
function ConfidenceBadge({
  confidence,
  forensic = false,
}: ConfidenceBadgeProps): React.ReactElement {
  if (forensic) {
    const config = {
      high: {
        bg: 'bg-emerald-100 dark:bg-emerald-900',
        text: 'text-emerald-800 dark:text-emerald-200',
        label: 'Verified',
      },
      medium: {
        bg: 'bg-yellow-100 dark:bg-yellow-900',
        text: 'text-yellow-800 dark:text-yellow-200',
        label: 'Caution',
      },
      low: {
        bg: 'bg-red-100 dark:bg-red-900',
        text: 'text-red-800 dark:text-red-200',
        label: 'Review',
      },
    };

    const { bg, text, label } = config[confidence];

    return (
      <div
        className={cn(
          'px-2 py-1 rounded text-xs font-medium flex items-center gap-1',
          bg,
          text
        )}
      >
        <Fingerprint className="w-3 h-3" />
        {label}
      </div>
    );
  }

  const config = {
    high: {
      bg: 'bg-green-100 dark:bg-green-900',
      text: 'text-green-800 dark:text-green-200',
      label: 'High',
    },
    medium: {
      bg: 'bg-yellow-100 dark:bg-yellow-900',
      text: 'text-yellow-800 dark:text-yellow-200',
      label: 'Medium',
    },
    low: {
      bg: 'bg-red-100 dark:bg-red-900',
      text: 'text-red-800 dark:text-red-200',
      label: 'Low',
    },
  };

  const { bg, text, label } = config[confidence];

  return (
    <div className={cn('px-2 py-1 rounded text-xs font-medium', bg, text)}>
      {label}
    </div>
  );
}

/**
 * Enhanced Confidence Info with forensic context
 */
function ConfidenceInfo({
  confidence,
  forensic = false,
}: ConfidenceInfoProps): React.ReactElement {
  if (forensic) {
    const messages = {
      high: 'High forensic confidence - extensive analysis completed with consistent results',
      medium: 'Medium forensic confidence - some limitations in analysis scope',
      low: 'Low forensic confidence - limited data available for comprehensive analysis',
    };

    return (
      <div className="flex items-start gap-2 p-3 rounded-lg bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 border border-slate-200 dark:border-slate-700">
        <Fingerprint className="w-4 h-4 text-slate-500 dark:text-slate-400 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-slate-600 dark:text-slate-400">
          {messages[confidence]}
        </p>
      </div>
    );
  }

  const messages = {
    high: 'High confidence based on extensive metadata',
    medium: 'Medium confidence - some metadata may be limited',
    low: 'Low confidence - limited metadata available',
  };

  return (
    <div className="flex items-start gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
      <Info className="w-4 h-4 text-gray-500 dark:text-gray-400 mt-0.5 flex-shrink-0" />
      <p className="text-sm text-gray-600 dark:text-gray-400">
        {messages[confidence]}
      </p>
    </div>
  );
}

/**
 * Enhanced KeyFindings Component with forensic integration
 */
export function KeyFindings({
  findings,
  forensicScore,
  forensicAnalysis,
  className,
  showForensicIndicators = true,
  compact = false,
}: KeyFindingsProps): React.ReactElement {
  const getAuthenticityColor = (
    confidence: 'high' | 'medium' | 'low'
  ): 'green' | 'yellow' | 'red' | 'forensic' => {
    if (showForensicIndicators && forensicScore !== undefined) {
      return 'forensic';
    }
    switch (confidence) {
      case 'high':
        return 'green';
      case 'medium':
        return 'yellow';
      case 'low':
        return 'red';
    }
  };

  const getAuthenticityRisk = (
    confidence: 'high' | 'medium' | 'low'
  ): 'low' | 'medium' | 'high' => {
    if (forensicScore !== undefined) {
      if (forensicScore >= 80) return 'low';
      if (forensicScore >= 60) return 'medium';
      return 'high';
    }
    return confidence;
  };

  return (
    <div className={cn('space-y-4', className)}>
      {findings.when && (
        <FindingCard
          icon={<Clock className="w-5 h-5" />}
          label="When"
          value={findings.when}
          color="blue"
        />
      )}

      {findings.where && (
        <FindingCard
          icon={<MapPin className="w-5 h-5" />}
          label="Where"
          value={findings.where}
          color="green"
        />
      )}

      {findings.device && (
        <FindingCard
          icon={<Camera className="w-5 h-5" />}
          label="Device"
          value={findings.device}
          color="purple"
        />
      )}

      <FindingCard
        icon={<Shield className="w-5 h-5" />}
        label="Authenticity"
        value={findings.authenticity}
        confidence={findings.confidence}
        color={getAuthenticityColor(findings.confidence)}
        forensicIndicator={showForensicIndicators}
        riskLevel={getAuthenticityRisk(findings.confidence)}
      />

      {showForensicIndicators && forensicAnalysis && (
        <ForensicSummary
          score={forensicScore}
          analysis={forensicAnalysis}
          compact={compact}
        />
      )}

      <ConfidenceInfo
        confidence={findings.confidence}
        forensic={showForensicIndicators}
      />
    </div>
  );
}

/**
 * Compact KeyFindings for space-constrained layouts
 */
export function KeyFindingsCompact({
  findings,
  forensicScore,
  forensicAnalysis,
  className,
}: Omit<
  KeyFindingsProps,
  'expandable' | 'showForensicIndicators' | 'compact'
>): React.ReactElement {
  const items = [
    findings.when && { icon: Clock, label: findings.when },
    findings.where && { icon: MapPin, label: findings.where },
    findings.device && { icon: Camera, label: findings.device },
  ].filter(Boolean) as Array<{ icon: React.ComponentType<any>; label: string }>;

  if (items.length === 0 && !forensicAnalysis) {
    return <div className={className}>No key findings available</div>;
  }

  return (
    <div className={cn('space-y-3', className)}>
      <div className={cn('flex flex-wrap gap-4')}>
        {items.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="flex items-center gap-2">
              <Icon className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {item.label}
              </span>
            </div>
          );
        })}
      </div>

      {forensicAnalysis && forensicScore !== undefined && (
        <div className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-900 rounded border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2">
            <Fingerprint className="w-4 h-4 text-slate-500" />
            <span className="text-xs text-slate-600 dark:text-slate-400">
              Forensic Score
            </span>
          </div>
          <AuthenticityBadge score={forensicScore} variant="compact" />
        </div>
      )}
    </div>
  );
}
