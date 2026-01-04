/**
 * Key Findings Component
 *
 * Displays the most important information extracted from metadata in plain English.
 */

import React from 'react';
import { Clock, MapPin, Camera, Shield, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { KeyFindings as KeyFindingsType } from '@/utils/metadataTransformers';

interface KeyFindingsProps {
  findings: KeyFindingsType;
  className?: string;
}

export function KeyFindings({
  findings,
  className
}: KeyFindingsProps): React.ReactElement {
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
      />

      <ConfidenceInfo confidence={findings.confidence} />
    </div>
  );
}

interface FindingCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  confidence?: 'high' | 'medium' | 'low';
  color?: 'blue' | 'green' | 'purple' | 'red' | 'yellow';
}

function FindingCard({
  icon,
  label,
  value,
  confidence,
  color = 'blue'
}: FindingCardProps): React.ReactElement {
  const bgColor = {
    blue: 'bg-blue-50 dark:bg-blue-950',
    green: 'bg-green-50 dark:bg-green-950',
    purple: 'bg-purple-50 dark:bg-purple-950',
    red: 'bg-red-50 dark:bg-red-950',
    yellow: 'bg-yellow-50 dark:bg-yellow-950'
  };

  const borderColor = {
    blue: 'border-blue-200 dark:border-blue-800',
    green: 'border-green-200 dark:border-green-800',
    purple: 'border-purple-200 dark:border-purple-800',
    red: 'border-red-200 dark:border-red-800',
    yellow: 'border-yellow-200 dark:border-yellow-800'
  };

  const iconColor = {
    blue: 'text-blue-600 dark:text-blue-400',
    green: 'text-green-600 dark:text-green-400',
    purple: 'text-purple-600 dark:text-purple-400',
    red: 'text-red-600 dark:text-red-400',
    yellow: 'text-yellow-600 dark:text-yellow-400'
  };

  return (
    <div
      className={cn(
        'p-4 rounded-lg border',
        bgColor[color],
        borderColor[color]
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn('mt-1', iconColor[color])}>
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {label}
          </p>
          <p className="text-base font-semibold text-gray-900 dark:text-white mt-1">
            {value}
          </p>
        </div>
        {confidence && (
          <ConfidenceBadge confidence={confidence} />
        )}
      </div>
    </div>
  );
}

interface ConfidenceBadgeProps {
  confidence: 'high' | 'medium' | 'low';
}

function ConfidenceBadge({ confidence }: ConfidenceBadgeProps): React.ReactElement {
  const config = {
    high: {
      bg: 'bg-green-100 dark:bg-green-900',
      text: 'text-green-800 dark:text-green-200',
      label: 'High'
    },
    medium: {
      bg: 'bg-yellow-100 dark:bg-yellow-900',
      text: 'text-yellow-800 dark:text-yellow-200',
      label: 'Medium'
    },
    low: {
      bg: 'bg-red-100 dark:bg-red-900',
      text: 'text-red-800 dark:text-red-200',
      label: 'Low'
    }
  };

  const { bg, text, label } = config[confidence];

  return (
    <div className={cn('px-2 py-1 rounded text-xs font-medium', bg, text)}>
      {label}
    </div>
  );
}

interface ConfidenceInfoProps {
  confidence: 'high' | 'medium' | 'low';
}

function ConfidenceInfo({ confidence }: ConfidenceInfoProps): React.ReactElement {
  const messages = {
    high: 'High confidence based on extensive metadata',
    medium: 'Medium confidence - some metadata may be limited',
    low: 'Low confidence - limited metadata available'
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

function getAuthenticityColor(confidence: 'high' | 'medium' | 'low'): 'green' | 'yellow' | 'red' {
  switch (confidence) {
    case 'high': return 'green';
    case 'medium': return 'yellow';
    case 'low': return 'red';
  }
}

export function KeyFindingsCompact({
  findings,
  className
}: Omit<KeyFindingsProps, 'expandable'>): React.ReactElement {
  const items = [
    findings.when && { icon: Clock, label: findings.when },
    findings.where && { icon: MapPin, label: findings.where },
    findings.device && { icon: Camera, label: findings.device }
  ].filter(Boolean) as Array<{ icon: React.ComponentType<any>; label: string }>;

  if (items.length === 0) {
    return <div className={className}>No key findings available</div>;
  }

  return (
    <div className={cn('flex flex-wrap gap-4', className)}>
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
  );
}
