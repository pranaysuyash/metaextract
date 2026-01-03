import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import {
  Calendar,
  MapPin,
  Smartphone,
  Shield,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Conditional logging
const DEBUG = import.meta.env.DEV;
const log = DEBUG ? console.log.bind(console) : () => {};

interface KeyFindingsProps {
  metadata: any;
  className?: string;
}

interface Finding {
  icon: React.ElementType;
  label: string;
  value: string;
  confidence?: 'high' | 'medium' | 'low';
  status?: 'success' | 'warning' | 'error';
}

export function KeyFindings({ metadata, className }: KeyFindingsProps) {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [isLoadingLLM, setIsLoadingLLM] = useState(false);
  const [usedLLM, setUsedLLM] = useState(false);

  log('[KeyFindings] Metadata received:', metadata);

  useEffect(() => {
    async function loadFindings() {
      // Try LLM extraction first if available
      try {
        setIsLoadingLLM(true);
        const llmFindings = await extractFindingsWithLLM(metadata);
        if (llmFindings && llmFindings.length > 0) {
          log('[KeyFindings] Using LLM-generated findings');
          setFindings(llmFindings);
          setUsedLLM(true);
          setIsLoadingLLM(false);
          return;
        }
      } catch (error) {
        log(
          '[KeyFindings] LLM extraction failed, falling back to rules:',
          error
        );
      }

      setIsLoadingLLM(false);
      // Fallback to rule-based extraction
      const ruleBasedFindings = extractKeyFindings(metadata);
      setFindings(ruleBasedFindings);
      setUsedLLM(false);
    }

    loadFindings();
  }, [metadata]);

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header matching your forensic theme */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/10">
        <div className="p-2 bg-primary/20 rounded border border-primary/30">
          <Smartphone className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1">
          <h2 className="text-xl font-bold text-white font-mono tracking-tight">
            KEY FINDINGS
          </h2>
          <p className="text-xs text-slate-500 font-mono">
            Plain English answers to the most important questions
          </p>
        </div>
        {usedLLM && (
          <div className="flex items-center gap-1 px-2 py-1 bg-purple-500/20 border border-purple-500/30 rounded text-purple-300 text-xs font-mono">
            <Sparkles className="w-3 h-3" />
            AI Enhanced
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoadingLLM && (
        <div className="flex items-center justify-center py-12 text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin mr-3" />
          <span className="font-mono text-sm">
            Analyzing metadata with AI...
          </span>
        </div>
      )}

      {/* Empty State */}
      {!isLoadingLLM && findings.length === 0 && (
        <div className="text-center py-12 px-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
          <AlertTriangle className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
          <p className="text-slate-300 font-mono text-sm mb-2">
            No key findings could be extracted from this file.
          </p>
          <p className="text-xs text-slate-500 font-mono">
            File may be missing standard metadata fields (EXIF, GPS, etc.)
          </p>
        </div>
      )}

      {/* Findings Grid */}
      {!isLoadingLLM && findings.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {findings.map((finding, index) => (
            <FindingCardDark key={index} finding={finding} />
          ))}
        </div>
      )}
    </div>
  );
}

function FindingCardDark({ finding }: { finding: Finding }) {
  const Icon = finding.icon;

  const statusColors = {
    success: 'border-emerald-500/30 bg-emerald-500/10',
    warning: 'border-yellow-500/30 bg-yellow-500/10',
    error: 'border-red-500/30 bg-red-500/10',
  };

  const confidenceColors = {
    high: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    medium: 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
    low: 'text-red-400 border-red-500/30 bg-red-500/10',
  };

  return (
    <div
      className={cn(
        'border backdrop-blur-sm rounded-lg p-4 transition-all duration-200',
        finding.status
          ? statusColors[finding.status]
          : 'border-white/10 bg-white/5'
      )}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div
          className={cn(
            'p-2 rounded border flex-shrink-0',
            finding.status === 'success' &&
              'bg-emerald-500/20 border-emerald-500/30',
            finding.status === 'warning' &&
              'bg-yellow-500/20 border-yellow-500/30',
            finding.status === 'error' && 'bg-red-500/20 border-red-500/30',
            !finding.status && 'bg-primary/20 border-primary/30'
          )}
        >
          <Icon
            className={cn(
              'w-4 h-4',
              finding.status === 'success' && 'text-emerald-400',
              finding.status === 'warning' && 'text-yellow-400',
              finding.status === 'error' && 'text-red-400',
              !finding.status && 'text-primary'
            )}
          />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p className="text-xs font-mono text-slate-500 uppercase tracking-wider">
              {finding.label}
            </p>
            {finding.confidence && (
              <Badge
                variant="outline"
                className={cn(
                  'text-[10px] font-mono',
                  confidenceColors[finding.confidence]
                )}
              >
                {finding.confidence.toUpperCase()}
              </Badge>
            )}
          </div>

          <p className="text-sm font-semibold text-white font-mono break-words">
            {finding.value}
          </p>
        </div>

        {/* Status Icon */}
        {finding.status === 'success' && (
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
        )}
        {finding.status === 'warning' && (
          <AlertTriangle className="w-4 h-4 text-yellow-400 flex-shrink-0" />
        )}
        {finding.status === 'error' && (
          <XCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
        )}
      </div>
    </div>
  );
}

// ============================================================================
// HELPER FUNCTIONS - LLM-powered and rule-based extraction
// ============================================================================

async function extractFindingsWithLLM(
  metadata: any
): Promise<Finding[] | null> {
  try {
    const response = await fetch('/api/metadata/findings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metadata }),
    });

    if (!response.ok) {
      throw new Error(`LLM extraction failed: ${response.status}`);
    }

    const data = await response.json();
    return data.findings || null;
  } catch (error) {
    log('[extractFindingsWithLLM] Error:', error);
    return null;
  }
}

// Robust metadata value finder
function findMetadataValue(metadata: any, paths: string[][]): any {
  for (const path of paths) {
    let value = metadata;
    for (const key of path) {
      value = value?.[key];
      if (value === undefined || value === null) break;
    }
    if (value !== undefined && value !== null && value !== '') {
      return value;
    }
  }
  return null;
}

function extractKeyFindings(metadata: any): Finding[] {
  const findings: Finding[] = [];

  log('[extractKeyFindings] Processing metadata');

  // Extensible finding extractors - easy to add more
  const extractors = [
    extractWhen,
    extractWhere,
    extractDevice,
    extractAuthenticity,
  ];

  extractors.forEach(extractor => {
    const finding = extractor(metadata);
    if (finding) {
      findings.push(finding);
    }
  });

  log('[extractKeyFindings] Extracted', findings.length, 'findings');
  return findings;
}

function extractWhen(metadata: any): Finding | null {
  const rawDate = findMetadataValue(metadata, [
    ['exif', 'DateTimeOriginal'],
    ['exif', 'CreateDate'],
    ['exif', 'ModifyDate'],
    ['exif', 'DateTime'],
    ['exif', 'Date/Time Original'],
    ['exif', 'ProfileDateTime'],
    ['filesystem', 'created'],
    ['filesystem', 'modified'],
    ['forensic', 'filesystem', 'file_created'],
    ['forensic', 'filesystem', 'file_modified'],
  ]);

  if (!rawDate) {
    return {
      icon: Calendar,
      label: 'WHEN',
      value: 'Date not available in metadata',
      status: 'warning',
    };
  }

  console.log('[extractWhen] Found photo date:', rawDate);

  // Format the date in plain English
  const formattedDate = formatDateTime(rawDate);

  return {
    icon: Calendar,
    label: 'WHEN',
    value: formattedDate,
    confidence: 'high',
  };
}

function extractWhere(metadata: any): Finding | null {
  const gps = metadata?.gps || metadata?.summary?.gps;

  if (!gps || (!gps.latitude && !gps.Latitude)) {
    return {
      icon: MapPin,
      label: 'WHERE',
      value: 'No location data in metadata',
      status: 'warning',
    };
  }

  const lat = gps.latitude || gps.Latitude;
  const lng = gps.longitude || gps.Longitude;

  // TODO: Add reverse geocoding for human-readable location
  const locationText = formatCoordinates(lat, lng);

  return {
    icon: MapPin,
    label: 'WHERE',
    value: locationText,
    confidence: 'high',
  };
}

// Device model database for friendly names
const DEVICE_DATABASE: Record<string, string> = {
  '24053PY09I': 'Xiaomi Redmi Note 11S',
  'iPhone14,3': 'iPhone 13 Pro Max',
  'iPhone14,2': 'iPhone 13 Pro',
  'iPhone13,4': 'iPhone 12 Pro Max',
  'SM-G998B': 'Samsung Galaxy S21 Ultra',
  'SM-G991B': 'Samsung Galaxy S21',
  // Add more as needed
};

function extractDevice(metadata: any): Finding | null {
  const make = findMetadataValue(metadata, [
    ['exif', 'Make'],
    ['exif', 'DeviceManufacturer'],
  ]);

  const model = findMetadataValue(metadata, [
    ['exif', 'Model'],
    ['exif', 'Device Model Name'],
    ['exif', 'DeviceModel'],
  ]);

  if (!make && !model) {
    return {
      icon: Smartphone,
      label: 'DEVICE',
      value: 'Device information not in metadata',
      status: 'warning',
    };
  }

  // Clean raw model for database lookup
  const rawModel = (model || '').split('::')[0].trim();

  // Check device database first
  let deviceName = DEVICE_DATABASE[rawModel] || '';

  if (!deviceName) {
    // Fallback to cleaned make + model
    if (make && model) {
      deviceName = model.toLowerCase().includes(make.toLowerCase())
        ? model
        : `${make} ${model}`;
    } else {
      deviceName = model || make;
    }

    // Clean up
    deviceName = deviceName
      .replace(/captured by.*gps map camera/gi, '')
      .replace(/corporation|inc|ltd\.?/gi, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  return {
    icon: Smartphone,
    label: 'DEVICE',
    value: deviceName,
    confidence: deviceName === DEVICE_DATABASE[rawModel] ? 'high' : 'medium',
  };
}

function extractAuthenticity(metadata: any): Finding | null {
  // Check for actual forensic indicators
  const manipulationDetected =
    metadata?.manipulation_detection?.is_manipulated ||
    metadata?.forensic?.manipulation_detected ||
    metadata?.ai_detection?.is_ai_generated;

  if (manipulationDetected) {
    return {
      icon: Shield,
      label: 'AUTHENTICITY',
      value: 'Manipulation indicators detected',
      confidence: 'high',
      status: 'error',
    };
  }

  // Check date consistency
  const exifDate = findMetadataValue(metadata, [
    ['exif', 'DateTimeOriginal'],
    ['exif', 'CreateDate'],
  ]);
  const fileDate = findMetadataValue(metadata, [['filesystem', 'created']]);

  if (exifDate && fileDate) {
    try {
      const exifTime = new Date(exifDate.replace(/:/g, '-')).getTime();
      const fileTime = new Date(fileDate).getTime();
      const daysDiff = Math.abs(exifTime - fileTime) / (1000 * 60 * 60 * 24);

      if (daysDiff > 1) {
        return {
          icon: Shield,
          label: 'AUTHENTICITY',
          value: 'Date mismatch between EXIF and file system',
          confidence: 'medium',
          status: 'warning',
        };
      }
    } catch (e) {
      // Date parsing failed, continue with other checks
    }
  }

  // Check for metadata completeness
  const hasExif = metadata?.exif && Object.keys(metadata.exif).length > 5;
  const hasGPS = metadata?.gps?.latitude;
  const hasThumbnail = metadata?.thumbnail || metadata?.exif?.ThumbnailImage;

  const signals = [hasExif, hasGPS, hasThumbnail].filter(Boolean).length;

  if (signals >= 2) {
    return {
      icon: Shield,
      label: 'AUTHENTICITY',
      value: 'File appears authentic - complete metadata',
      confidence: 'high',
      status: 'success',
    };
  } else if (signals === 1) {
    return {
      icon: Shield,
      label: 'AUTHENTICITY',
      value: 'Partial metadata - likely authentic',
      confidence: 'medium',
      status: 'success',
    };
  } else {
    return {
      icon: Shield,
      label: 'AUTHENTICITY',
      value: 'Minimal metadata - cannot assess authenticity',
      confidence: 'low',
      status: 'warning',
    };
  }
}

function formatDateTime(dateString: string): string {
  try {
    let cleanDate = dateString;

    // Remove timezone info (TODO: preserve and display timezone)
    cleanDate = cleanDate.split(/[+-]\d{2}:\d{2}/)[0].trim();

    let date: Date;

    // Handle EXIF format: "2023:06:15 14:34:22"
    if (cleanDate.match(/^\d{4}:\d{2}:\d{2}/)) {
      const parts = cleanDate.split(/[\s:T:-]/);
      if (parts.length >= 6) {
        const [year, month, day, hour, minute, second] = parts;
        date = new Date(
          parseInt(year),
          parseInt(month) - 1,
          parseInt(day),
          parseInt(hour),
          parseInt(minute),
          parseInt(second)
        );
      } else {
        date = new Date(cleanDate);
      }
    } else {
      date = new Date(cleanDate);
    }

    if (isNaN(date.getTime())) {
      return dateString;
    }

    // Format in plain English
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    };

    return date.toLocaleDateString('en-US', options);
  } catch (error) {
    return dateString;
  }
}

function formatCoordinates(lat: number, lng: number): string {
  // Basic coordinate formatting
  const latDir = lat >= 0 ? 'N' : 'S';
  const lngDir = lng >= 0 ? 'E' : 'W';

  return `${Math.abs(lat).toFixed(4)}° ${latDir}, ${Math.abs(lng).toFixed(4)}° ${lngDir}`;
}
