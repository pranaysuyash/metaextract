import React from 'react';
import { Badge } from '@/components/ui/badge';
import {
  Calendar,
  MapPin,
  Smartphone,
  Shield,
  CheckCircle2,
  AlertTriangle,
  XCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

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
  // Debug the metadata structure
  console.log('[KeyFindings] Metadata received:', metadata);

  const findings = extractKeyFindings(metadata);

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header matching your forensic theme */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-white/10">
        <div className="p-2 bg-primary/20 rounded border border-primary/30">
          <Smartphone className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white font-mono tracking-tight">
            KEY FINDINGS
          </h2>
          <p className="text-xs text-slate-500 font-mono">
            Plain English answers to the most important questions
          </p>
        </div>
      </div>

      {/* Findings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {findings.map((finding, index) => (
          <FindingCardDark key={index} finding={finding} />
        ))}
      </div>
    </div>
  );
}

function FindingCardDark({ finding }: { finding: Finding }) {
  const Icon = finding.icon;

  const statusColors = {
    success: 'border-emerald-500/30 bg-emerald-500/10',
    warning: 'border-yellow-500/30 bg-yellow-500/10',
    error: 'border-red-500/30 bg-red-500/10'
  };

  const confidenceColors = {
    high: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
    medium: 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
    low: 'text-red-400 border-red-500/30 bg-red-500/10'
  };

  return (
    <div className={cn(
      'border backdrop-blur-sm rounded-lg p-4 transition-all duration-200',
      finding.status ? statusColors[finding.status] : 'border-white/10 bg-white/5'
    )}>
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={cn(
          'p-2 rounded border flex-shrink-0',
          finding.status === 'success' && 'bg-emerald-500/20 border-emerald-500/30',
          finding.status === 'warning' && 'bg-yellow-500/20 border-yellow-500/30',
          finding.status === 'error' && 'bg-red-500/20 border-red-500/30',
          !finding.status && 'bg-primary/20 border-primary/30'
        )}>
          <Icon className={cn(
            'w-4 h-4',
            finding.status === 'success' && 'text-emerald-400',
            finding.status === 'warning' && 'text-yellow-400',
            finding.status === 'error' && 'text-red-400',
            !finding.status && 'text-primary'
          )} />
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
                className={cn('text-[10px] font-mono', confidenceColors[finding.confidence])}
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
// HELPER FUNCTIONS - Updated to read actual metadata structure
// ============================================================================

function extractKeyFindings(metadata: any): Finding[] {
  const findings: Finding[] = [];

  console.log('[extractKeyFindings] Full metadata object:', JSON.stringify(metadata, null, 2));

  // 1. When was this photo taken?
  const whenFinding = extractWhen(metadata);
  if (whenFinding) {
    findings.push(whenFinding);
  }

  // 2. Where was this photo taken?
  const whereFinding = extractWhere(metadata);
  if (whereFinding) {
    findings.push(whereFinding);
  }

  // 3. What device took this photo?
  const deviceFinding = extractDevice(metadata);
  if (deviceFinding) {
    findings.push(deviceFinding);
  }

  // 4. Is this photo authentic?
  const authenticityFinding = extractAuthenticity(metadata);
  if (authenticityFinding) {
    findings.push(authenticityFinding);
  }

  console.log('[extractKeyFindings] Final findings:', findings);
  return findings;
}

function extractWhen(metadata: any): Finding | null {
  console.log('[extractWhen] Looking for file dates...');

  // Look for ALL dates: photo metadata, filesystem, ICC profile, etc.
  const allDateFields = [
    // EXIF photo dates
    metadata?.exif?.DateTimeOriginal,
    metadata?.exif?.CreateDate,
    metadata?.exif?.ModifyDate,
    metadata?.exif?.DateTime,
    metadata?.exif?.['Date/Time Original'],
    metadata?.exif?.['Create Date'],
    metadata?.exif?.['Modify Date'],
    // ICC Profile date
    metadata?.exif?.ProfileDateTime,
    // Filesystem dates
    metadata?.filesystem?.created,
    metadata?.filesystem?.modified,
    metadata?.forensic?.forensic?.filesystem?.file_created,
    metadata?.forensic?.forensic?.filesystem?.file_modified
  ];

  console.log('[extractWhen] All date fields found:', allDateFields);

  let rawDate = allDateFields.find(date => date && date !== '');

  if (!rawDate) {
    console.log('[extractWhen] No date found - BE HONEST about it');
    return {
      icon: Calendar,
      label: 'WHEN',
      value: 'File date not available in metadata',
      status: 'warning'
    };
  }

  console.log('[extractWhen] Found photo date:', rawDate);

  // Format the date in plain English
  const formattedDate = formatDateTime(rawDate);

  return {
    icon: Calendar,
    label: 'WHEN',
    value: formattedDate,
    confidence: 'high'
  };
}

function extractWhere(metadata: any): Finding | null {
  console.log('[extractWhere] Looking for GPS data...');

  // Check multiple possible GPS locations
  const gps = metadata?.gps || metadata?.summary?.gps;

  console.log('[extractWhere] GPS data:', gps);

  if (!gps || (!gps.latitude && !gps.Latitude)) {
    console.log('[extractWhere] No GPS found');
    return {
      icon: MapPin,
      label: 'WHERE',
      value: 'No location information available',
      status: 'warning'
    };
  }

  const lat = gps.latitude || gps.Latitude;
  const lng = gps.longitude || gps.Longitude;

  // For now, show coordinates
  const locationText = formatCoordinates(lat, lng);

  return {
    icon: MapPin,
    label: 'WHERE',
    value: locationText,
    confidence: 'high'
  };
}

function extractDevice(metadata: any): Finding | null {
  console.log('[extractDevice] Looking for device info...');

  // Check multiple possible device locations based on real data structure
  const make = metadata?.exif?.Make || metadata?.exif?.['Make'] || metadata?.exif?.DeviceManufacturer;
  const model = metadata?.exif?.Model || metadata?.exif?.['Model'] || metadata?.exif?.['Device Model Name'] || metadata?.exif?.DeviceModel;

  console.log('[extractDevice] Make:', make, 'Model:', model);

  if (!make && !model) {
    console.log('[extractDevice] No device info found');
    return {
      icon: Smartphone,
      label: 'DEVICE',
      value: 'Device information not available',
      status: 'warning'
    };
  }

  // Format device name - handle complex model strings like "24053PY09I :: Captured by - GPS Map Camera"
  let deviceName = '';
  if (make && model) {
    // If model contains the make, don't repeat it
    if (model.toLowerCase().includes(make.toLowerCase())) {
      deviceName = model;
    } else {
      deviceName = `${make} ${model}`;
    }
  } else if (model) {
    deviceName = model;
  } else if (make) {
    deviceName = make;
  }

  // Clean up device name - remove camera app descriptions
  deviceName = deviceName
    .split('::')[0] // Take everything before :: if present
    .replace(/captured by.*gps map camera/gi, '')
    .replace(/corporation|inc|ltd\.?/gi, '')
    .replace(/\s+/g, ' ') // Clean up extra spaces
    .trim();

  // Capitalize first letter of each word
  deviceName = deviceName
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');

  console.log('[extractDevice] Final device name:', deviceName);

  return {
    icon: Smartphone,
    label: 'DEVICE',
    value: deviceName,
    confidence: 'high'
  };
}

function extractAuthenticity(metadata: any): Finding | null {
  console.log('[extractAuthenticity] Assessing authenticity...');

  // Basic authenticity assessment based on available metadata
  const hasExif = metadata?.exif && Object.keys(metadata.exif).length > 0;
  const hasGPS = metadata?.gps && (metadata.gps.latitude || metadata.gps.Latitude);
  const hasFileHashes = metadata?.file_integrity?.md5 || metadata?.file_integrity?.sha256;

  console.log('[extractAuthenticity] hasExif:', hasExif, 'hasGPS:', hasGPS, 'hasFileHashes:', hasFileHashes);

  // Calculate confidence score
  let confidenceScore = 0;
  if (hasExif) confidenceScore += 40;
  if (hasGPS) confidenceScore += 30;
  if (hasFileHashes) confidenceScore += 30;

  let assessment = '';
  let confidence: 'high' | 'medium' | 'low' = 'medium';
  let status: 'success' | 'warning' | 'error' = 'success';

  if (confidenceScore >= 80) {
    assessment = 'File appears authentic';
    confidence = 'high';
    status = 'success';
  } else if (confidenceScore >= 50) {
    assessment = 'File appears mostly authentic';
    confidence = 'medium';
    status = 'success';
  } else {
    assessment = 'Limited metadata - authenticity uncertain';
    confidence = 'low';
    status = 'warning';
  }

  console.log('[extractAuthenticity] Assessment:', assessment, 'Score:', confidenceScore);

  return {
    icon: Shield,
    label: 'AUTHENTICITY',
    value: assessment,
    confidence,
    status
  };
}

function formatDateTime(dateString: string): string {
  try {
    console.log('[formatDateTime] Formatting:', dateString);

    let cleanDate = dateString;

    // Remove any timezone info for now
    cleanDate = cleanDate.split(/[+-]\d{2}:\d{2}/)[0].trim();

    // Try parsing different formats
    let date: Date;

    // Try EXIF format: "2023:06:15 14:34:22"
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
      console.log('[formatDateTime] Failed to parse, returning original');
      return dateString;
    }

    // Format in plain English
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    };

    const formatted = date.toLocaleDateString('en-US', options);
    console.log('[formatDateTime] Formatted result:', formatted);
    return formatted;

  } catch (error) {
    console.log('[formatDateTime] Error:', error);
    return dateString;
  }
}

function formatCoordinates(lat: number, lng: number): string {
  // Basic coordinate formatting
  const latDir = lat >= 0 ? 'N' : 'S';
  const lngDir = lng >= 0 ? 'E' : 'W';

  return `${Math.abs(lat).toFixed(4)}° ${latDir}, ${Math.abs(lng).toFixed(4)}° ${lngDir}`;
}