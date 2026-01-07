import React from 'react';
import { Badge } from '@/components/ui/badge';
import {
  Verified,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Bot,
  Fingerprint,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface AIDetectionBadgeProps {
  likelihood: 'very_low' | 'low' | 'medium' | 'high';
  confidenceScore: number;
  detectedTools?: string[];
  className?: string;
}

export interface C2PAProvenanceBadgeProps {
  detected: boolean;
  verified: boolean;
  claimGenerator?: string;
  className?: string;
}

export interface ForensicSummaryBadgeProps {
  aiDetection?: AIDetectionBadgeProps;
  c2paProvenance?: C2PAProvenanceBadgeProps;
  authenticityScore?: number;
  className?: string;
}

export function AIDetectionBadge({
  likelihood,
  confidenceScore,
  detectedTools = [],
  className,
}: AIDetectionBadgeProps) {
  const config = {
    very_low: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      text: 'text-emerald-600 dark:text-emerald-400',
      label: 'Likely Authentic',
      icon: Verified,
    },
    low: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      text: 'text-emerald-600 dark:text-emerald-400',
      label: 'Probably Authentic',
      icon: ShieldCheck,
    },
    medium: {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
      text: 'text-yellow-600 dark:text-yellow-400',
      label: 'Possibly AI-Generated',
      icon: AlertTriangle,
    },
    high: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      text: 'text-red-600 dark:text-red-400',
      label: 'Likely AI-Generated',
      icon: Bot,
    },
  };

  const { bg, border, text, label, icon: Icon } = config[likelihood];

  return (
    <div
      className={cn(
        'rounded-lg border p-3',
        bg,
        border,
        className
      )}
    >
      <div className="flex items-center gap-2 mb-2">
        <Icon className={cn('w-4 h-4', text)} />
        <span className={cn('font-medium text-sm', text)}>{label}</span>
        <Badge variant="outline" className="ml-auto text-xs">
          {Math.round(confidenceScore * 100)}% confidence
        </Badge>
      </div>
      {detectedTools.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {detectedTools.map((tool, i) => (
            <Badge key={i} variant="secondary" className="text-xs">
              {tool}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}

export function C2PAProvenanceBadge({
  detected,
  verified,
  claimGenerator,
  className,
}: C2PAProvenanceBadgeProps) {
  if (!detected) {
    return (
      <div
        className={cn(
          'rounded-lg border p-3 bg-slate-500/10 border-slate-500/30',
          className
        )}
      >
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-slate-500" />
          <span className="text-sm text-slate-600 dark:text-slate-400">
            No C2PA Content Credentials
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          This file does not contain verified provenance data.
        </p>
      </div>
    );
  }

  const isVerified = verified;

  return (
    <div
      className={cn(
        'rounded-lg border p-3',
        isVerified
          ? 'bg-emerald-500/10 border-emerald-500/30'
          : 'bg-yellow-500/10 border-yellow-500/30',
        className
      )}
    >
      <div className="flex items-center gap-2 mb-1">
        {isVerified ? (
          <Verified className="w-4 h-4 text-emerald-500" />
        ) : (
          <AlertTriangle className="w-4 h-4 text-yellow-500" />
        )}
        <span
          className={cn(
            'font-medium text-sm',
            isVerified
              ? 'text-emerald-600 dark:text-emerald-400'
              : 'text-yellow-600 dark:text-yellow-400'
          )}
        >
          {isVerified ? 'C2PA Verified' : 'C2PA Present (Unverified)'}
        </span>
      </div>
      {claimGenerator && (
        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
          Origin: {claimGenerator}
        </p>
      )}
    </div>
  );
}

export function ForensicSummaryBadge({
  aiDetection,
  c2paProvenance,
  authenticityScore,
  className,
}: ForensicSummaryBadgeProps) {
  return (
    <div className={cn('space-y-3', className)}>
      <div className="flex items-center gap-2 mb-3">
        <Fingerprint className="w-5 h-5 text-primary" />
        <h3 className="font-semibold text-sm">Forensic Analysis (131k+ Fields)</h3>
      </div>

      {c2paProvenance && (
        <C2PAProvenanceBadge
          detected={c2paProvenance.detected}
          verified={c2paProvenance.verified}
          claimGenerator={c2paProvenance.claimGenerator}
        />
      )}

      {aiDetection && (
        <AIDetectionBadge
          likelihood={aiDetection.likelihood}
          confidenceScore={aiDetection.confidenceScore}
          detectedTools={aiDetection.detectedTools}
        />
      )}

      {authenticityScore !== undefined && (
        <div className="flex items-center justify-between p-2 bg-slate-100 dark:bg-slate-800 rounded">
          <span className="text-xs text-slate-600 dark:text-slate-400">
            Overall Authenticity
          </span>
          <Badge
            variant={
              authenticityScore >= 0.8
                ? 'default'
                : authenticityScore >= 0.5
                  ? 'secondary'
                  : 'destructive'
            }
          >
            {Math.round(authenticityScore * 100)}%
          </Badge>
        </div>
      )}
    </div>
  );
}
