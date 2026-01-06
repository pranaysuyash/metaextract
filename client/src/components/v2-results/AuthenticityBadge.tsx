import React from 'react';
import { Badge } from '@/components/ui/badge';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Eye,
  Shield,
  Verified,
  AlertOctagon,
  Fingerprint,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface AuthenticityBadgeProps {
  score: number;
  label?: string;
  showIcon?: boolean;
  variant?: 'default' | 'outline' | 'minimal' | 'compact' | 'detailed';
  size?: 'sm' | 'md' | 'lg';
  showConfidence?: boolean;
  animated?: boolean;
  className?: string;
}

export interface AuthenticityAssessmentProps {
  score: number;
  details?: string;
  showConfidence?: boolean;
  showProgress?: boolean;
  className?: string;
}

export interface ForensicConfidenceIndicatorProps {
  confidence: number;
  type?: 'authenticity' | 'manipulation' | 'ai-detection';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

/**
 * Forensic Confidence Indicator
 * Visual representation of confidence levels with color-coded indicators
 */
export const ForensicConfidenceIndicator: React.FC<
  ForensicConfidenceIndicatorProps
> = ({ confidence, type = 'authenticity', size = 'md', showLabel = true }) => {
  const getConfig = () => {
    if (type === 'manipulation') {
      // For manipulation detection, higher confidence in detection = more suspicious
      return confidence >= 80
        ? {
            color: 'text-red-500',
            bg: 'bg-red-500/10',
            border: 'border-red-500/30',
            label: 'High Risk',
          }
        : confidence >= 60
          ? {
              color: 'text-orange-500',
              bg: 'bg-orange-500/10',
              border: 'border-orange-500/30',
              label: 'Medium Risk',
            }
          : {
              color: 'text-emerald-500',
              bg: 'bg-emerald-500/10',
              border: 'border-emerald-500/30',
              label: 'Low Risk',
            };
    } else if (type === 'ai-detection') {
      // For AI detection, similar logic as manipulation
      return confidence >= 80
        ? {
            color: 'text-red-500',
            bg: 'bg-red-500/10',
            border: 'border-red-500/30',
            label: 'AI Detected',
          }
        : confidence >= 60
          ? {
              color: 'text-yellow-500',
              bg: 'bg-yellow-500/10',
              border: 'border-yellow-500/30',
              label: 'Possibly AI',
            }
          : {
              color: 'text-emerald-500',
              bg: 'bg-emerald-500/10',
              border: 'border-emerald-500/30',
              label: 'Likely Original',
            };
    } else {
      // Default authenticity scoring
      return confidence >= 80
        ? {
            color: 'text-emerald-500',
            bg: 'bg-emerald-500/10',
            border: 'border-emerald-500/30',
            label: 'Authentic',
          }
        : confidence >= 60
          ? {
              color: 'text-yellow-500',
              bg: 'bg-yellow-500/10',
              border: 'border-yellow-500/30',
              label: 'Questionable',
            }
          : {
              color: 'text-red-500',
              bg: 'bg-red-500/10',
              border: 'border-red-500/30',
              label: 'Suspicious',
            };
    }
  };

  const config = getConfig();
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 rounded-md border font-medium',
        config.bg,
        config.border,
        config.color,
        sizeClasses[size],
        showLabel ? '' : 'px-2'
      )}
    >
      {confidence >= 80 ? (
        <Verified
          className={cn(
            size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5'
          )}
        />
      ) : confidence >= 60 ? (
        <AlertTriangle
          className={cn(
            size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5'
          )}
        />
      ) : (
        <AlertOctagon
          className={cn(
            size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5'
          )}
        />
      )}
      {showLabel && (
        <span>
          {config.label}
          {confidence < 100 ? ` (${confidence}%)` : ''}
        </span>
      )}
    </div>
  );
};

/**
 * Authenticity Badge Component
 * Enhanced badge with multiple display variants and animated transitions
 */
export const AuthenticityBadge: React.FC<AuthenticityBadgeProps> = ({
  score,
  label,
  showIcon = true,
  variant = 'default',
  size = 'md',
  showConfidence = true,
  animated = true,
  className,
}) => {
  // Determine authenticity level based on score
  let authenticityLevel:
    | 'authentic'
    | 'questionable'
    | 'suspicious'
    | 'unknown';
  let badgeVariant: 'default' | 'destructive' | 'secondary' | 'outline';
  let icon: React.ReactNode;
  let displayLabel: string;
  let trendIcon: React.ReactNode | null = null;

  if (score >= 80) {
    authenticityLevel = 'authentic';
    badgeVariant = 'secondary';
    icon = (
      <Verified
        className={cn(
          size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5',
          'text-emerald-500'
        )}
      />
    );
    displayLabel = label || `Authentic (${score}%)`;
    trendIcon = <TrendingUp className="w-3 h-3 text-emerald-500" />;
  } else if (score >= 60) {
    authenticityLevel = 'questionable';
    badgeVariant = 'outline';
    icon = (
      <AlertTriangle
        className={cn(
          size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5',
          'text-yellow-500'
        )}
      />
    );
    displayLabel = label || `Questionable (${score}%)`;
    trendIcon = <Minus className="w-3 h-3 text-yellow-500" />;
  } else if (score >= 0) {
    authenticityLevel = 'suspicious';
    badgeVariant = 'destructive';
    icon = (
      <AlertOctagon
        className={cn(
          size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5',
          'text-red-500'
        )}
      />
    );
    displayLabel = label || `Suspicious (${score}%)`;
    trendIcon = <TrendingDown className="w-3 h-3 text-red-500" />;
  } else {
    authenticityLevel = 'unknown';
    badgeVariant = 'outline';
    icon = (
      <Eye
        className={cn(
          size === 'sm' ? 'w-3 h-3' : size === 'md' ? 'w-4 h-4' : 'w-5 h-5',
          'text-slate-500'
        )}
      />
    );
    displayLabel = label || 'Authenticity Unknown';
  }

  // Adjust badge variant based on props
  const finalVariant = variant === 'outline' ? 'outline' : badgeVariant;

  // Size-based styling
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs gap-1',
    md: 'px-2.5 py-0.5 text-sm gap-1.5',
    lg: 'px-3 py-1 text-sm gap-2',
  };

  // Handle different variants
  if (variant === 'minimal') {
    return (
      <div
        className={cn(
          'inline-flex items-center gap-1',
          animated && 'transition-all duration-300',
          className
        )}
      >
        {showIcon && icon}
        <span
          className={cn(
            'font-medium',
            authenticityLevel === 'authentic'
              ? 'text-emerald-400'
              : authenticityLevel === 'questionable'
                ? 'text-yellow-400'
                : authenticityLevel === 'suspicious'
                  ? 'text-red-400'
                  : 'text-slate-400'
          )}
        >
          {displayLabel}
        </span>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div
        className={cn(
          'inline-flex items-center gap-1.5 px-2 py-1 rounded-md',
          'bg-background border',
          authenticityLevel === 'authentic'
            ? 'border-emerald-500/30 bg-emerald-500/10'
            : authenticityLevel === 'questionable'
              ? 'border-yellow-500/30 bg-yellow-500/10'
              : authenticityLevel === 'suspicious'
                ? 'border-red-500/30 bg-red-500/10'
                : 'border-slate-500/30 bg-slate-500/10',
          animated && 'transition-all duration-300',
          className
        )}
      >
        {showIcon && icon}
        <span
          className={cn(
            'text-xs font-medium',
            authenticityLevel === 'authentic'
              ? 'text-emerald-400'
              : authenticityLevel === 'questionable'
                ? 'text-yellow-400'
                : authenticityLevel === 'suspicious'
                  ? 'text-red-400'
                  : 'text-slate-400'
          )}
        >
          {score}%
        </span>
      </div>
    );
  }

  if (variant === 'detailed') {
    return (
      <div
        className={cn(
          'inline-flex items-center gap-3 px-3 py-2 rounded-lg',
          'bg-background border',
          authenticityLevel === 'authentic'
            ? 'border-emerald-500/30 bg-emerald-500/10'
            : authenticityLevel === 'questionable'
              ? 'border-yellow-500/30 bg-yellow-500/10'
              : authenticityLevel === 'suspicious'
                ? 'border-red-500/30 bg-red-500/10'
                : 'border-slate-500/30 bg-slate-500/10',
          animated && 'transition-all duration-300',
          className
        )}
      >
        {showIcon && icon}
        <div className="flex flex-col">
          <span
            className={cn(
              'font-medium',
              authenticityLevel === 'authentic'
                ? 'text-emerald-400'
                : authenticityLevel === 'questionable'
                  ? 'text-yellow-400'
                  : authenticityLevel === 'suspicious'
                    ? 'text-red-400'
                    : 'text-slate-400'
            )}
          >
            {displayLabel}
          </span>
          {showConfidence && (
            <div className="flex items-center gap-1 text-xs text-slate-400">
              {trendIcon}
              <span>Confidence: {score}%</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Default badge variant
  return (
    <Badge
      variant={finalVariant}
      className={cn(
        sizeClasses[size],
        authenticityLevel === 'authentic'
          ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
          : '',
        authenticityLevel === 'questionable'
          ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
          : '',
        authenticityLevel === 'suspicious'
          ? 'bg-red-500/20 text-red-400 border-red-500/30'
          : '',
        authenticityLevel === 'unknown'
          ? 'bg-slate-500/20 text-slate-300 border-slate-500/30'
          : '',
        showIcon ? 'flex items-center' : '',
        animated && 'transition-all duration-300 hover:scale-105',
        className
      )}
    >
      {showIcon && icon}
      <span>{displayLabel}</span>
    </Badge>
  );
};

/**
 * Authenticity Assessment Component
 * Comprehensive assessment display with optional progress bar
 */
export const AuthenticityAssessment: React.FC<AuthenticityAssessmentProps> = ({
  score,
  details,
  showConfidence = true,
  showProgress = false,
  className,
}) => {
  return (
    <div className={cn('space-y-3', className)}>
      <div className="flex items-center justify-between">
        <AuthenticityBadge
          score={score}
          variant="detailed"
          showConfidence={showConfidence}
        />
        {showConfidence && (
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <Shield className="w-3 h-3" />
            <span>Analysis Confidence</span>
          </div>
        )}
      </div>

      {showProgress && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-slate-400">
            <span>Authenticity Score</span>
            <span>{score}%</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className={cn(
                'h-2 rounded-full transition-all duration-1000',
                score >= 80
                  ? 'bg-emerald-500'
                  : score >= 60
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
              )}
              style={{ width: `${score}%` }}
            />
          </div>
        </div>
      )}

      {details && (
        <p className="text-xs text-slate-300 mt-2 leading-relaxed">{details}</p>
      )}
    </div>
  );
};

/**
 * Quick Authenticity Indicator
 * Ultra-compact component for use in lists or tables
 */
export const QuickAuthenticityIndicator: React.FC<{ score: number }> = ({
  score,
}) => {
  const getColor = () => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="flex items-center gap-2">
      <div className={cn('w-2 h-2 rounded-full', getColor())} />
      <span className="text-xs text-slate-400">{score}%</span>
    </div>
  );
};

export default AuthenticityBadge;
