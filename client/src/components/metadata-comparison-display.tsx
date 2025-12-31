import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Eye,
  XCircle,
} from 'lucide-react';
import { motion } from 'framer-motion';

interface MetadataComparisonDisplayProps {
  comparison?: {
    has_both: boolean;
    has_embedded_only: boolean;
    has_burned_only: boolean;
    matches: Array<{
      field: string;
      matches: boolean;
      embedded?: any;
      burned?: any;
      difference?: any;
    }>;
    discrepancies: Array<{ field: string; matches: boolean; warning?: string }>;
    warnings: string[];
    summary: {
      embedded_metadata_present: boolean;
      burned_metadata_present: boolean;
      gps_comparison: string;
      timestamp_comparison: string;
      overall_status:
        | 'verified'
        | 'suspicious'
        | 'stripped_exif'
        | 'no_overlay'
        | 'no_metadata';
    };
  } | null;
}

const statusConfig = {
  verified: {
    icon: CheckCircle2,
    title: '✓ VERIFIED',
    description: 'Embedded and burned metadata match',
    color: 'emerald',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    textColor: 'text-emerald-400',
  },
  suspicious: {
    icon: AlertTriangle,
    title: '⚠️ SUSPICIOUS',
    description: 'Metadata sources conflict - possible tampering',
    color: 'rose',
    bg: 'bg-rose-500/10 border-rose-500/30',
    textColor: 'text-rose-400',
  },
  stripped_exif: {
    icon: Eye,
    title: '🚨 EXIF STRIPPED',
    description: 'EXIF data removed but overlay remains',
    color: 'amber',
    bg: 'bg-amber-500/10 border-amber-500/30',
    textColor: 'text-amber-400',
  },
  no_overlay: {
    icon: AlertCircle,
    title: 'ℹ️ STANDARD PHOTO',
    description: 'No visible overlay detected',
    color: 'slate',
    bg: 'bg-slate-500/10 border-slate-500/30',
    textColor: 'text-slate-400',
  },
  no_metadata: {
    icon: XCircle,
    title: '❓ NO METADATA',
    description: 'Neither embedded nor burned metadata found',
    color: 'slate',
    bg: 'bg-slate-500/10 border-slate-500/30',
    textColor: 'text-slate-400',
  },
};

export function MetadataComparisonDisplay({
  comparison,
}: MetadataComparisonDisplayProps) {
  if (!comparison) {
    return null;
  }

  const summary = comparison.summary ?? {
    embedded_metadata_present: false,
    burned_metadata_present: false,
    gps_comparison: 'no_gps',
    timestamp_comparison: 'no_timestamp',
    overall_status: 'no_metadata',
  };
  const matches = comparison.matches ?? [];
  const discrepancies = comparison.discrepancies ?? [];
  const warnings = comparison.warnings ?? [];

  const status = summary.overall_status || 'no_metadata';
  const config = statusConfig[status] ?? statusConfig.no_metadata;
  const Icon = config.icon;
  const isSuspicious = status === 'suspicious';
  const isVerified = status === 'verified';
  const isStripped = status === 'stripped_exif';

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h4 className='flex items-center gap-2 text-xs font-bold mb-4 uppercase tracking-widest text-slate-300 border-b border-white/5 pb-2'>
        <Eye className='w-3 h-3' /> Metadata Comparison
      </h4>

      {/* Main Status Alert */}
      <div className={`rounded-lg border p-4 mb-4 ${config.bg}`}>
        <div className='flex items-start gap-3'>
          <Icon className={`w-5 h-5 ${config.textColor} shrink-0 mt-0.5`} />
          <div className='flex-1 min-w-0'>
            <h5 className={`text-sm font-bold ${config.textColor}`}>
              {config.title}
            </h5>
            <p className='text-xs text-slate-400 mt-1'>{config.description}</p>
          </div>
        </div>
      </div>

      {/* Detailed Comparisons */}
      <div className='grid grid-cols-1 md:grid-cols-2 gap-3 mb-4'>
        {/* GPS Comparison */}
        <div className='bg-black/40 border border-white/10 rounded-lg p-3'>
          <h6 className='text-xs font-bold text-rose-400 mb-2'>
            📍 GPS Comparison
          </h6>
          <div
            className={`text-xs px-2 py-1 rounded font-mono ${
              summary.gps_comparison === 'match'
                ? 'bg-emerald-500/20 text-emerald-300'
                : summary.gps_comparison === 'mismatch'
                ? 'bg-rose-500/20 text-rose-300'
                : 'bg-slate-500/20 text-slate-300'
            }`}
          >
            {summary.gps_comparison.toUpperCase()}
          </div>

          {/* Show GPS distance if mismatch */}
          {matches.find((m) => m.field === 'gps' && m.matches === true)
            ?.difference && (
            <div className='text-[10px] text-emerald-400 mt-2 font-mono'>
              ✓ Match (±
              {matches
                .find((m) => m.field === 'gps')
                ?.difference?.approx_meters?.toFixed(1)}
              m)
            </div>
          )}

          {discrepancies.find((d) => d.field === 'gps') && (
            <div className='text-[10px] text-rose-400 mt-2'>
              ⚠️{' '}
              {discrepancies.find((d) => d.field === 'gps')?.warning}
            </div>
          )}
        </div>

        {/* Timestamp Comparison */}
        <div className='bg-black/40 border border-white/10 rounded-lg p-3'>
          <h6 className='text-xs font-bold text-purple-400 mb-2'>
            🕐 Timestamp Comparison
          </h6>
          <div
            className={`text-xs px-2 py-1 rounded font-mono ${
              summary.timestamp_comparison === 'match'
                ? 'bg-emerald-500/20 text-emerald-300'
                : summary.timestamp_comparison === 'mismatch'
                ? 'bg-rose-500/20 text-rose-300'
                : 'bg-slate-500/20 text-slate-300'
            }`}
          >
            {summary.timestamp_comparison.toUpperCase()}
          </div>

          {discrepancies.find((d) => d.field === 'timestamp') && (
            <div className='text-[10px] text-rose-400 mt-2'>
              ⚠️ Timestamps don't match
            </div>
          )}
        </div>
      </div>

      {/* Matches Section */}
      {matches.length > 0 && (
        <div className='bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3 mb-3'>
          <h6 className='text-xs font-bold text-emerald-400 mb-2 flex items-center gap-2'>
            <CheckCircle2 className='w-3 h-3' /> Verified Fields (
            {matches.length})
          </h6>
          <div className='space-y-1'>
            {matches.map((match, i) => (
              <div
                key={i}
                className='text-xs text-emerald-300 font-mono flex items-center gap-2'
              >
                <span className='text-emerald-500'>✓</span>
                <span className='capitalize'>{match.field}:</span>
                <span className='text-slate-400'>Both sources match</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Discrepancies Section */}
      {discrepancies.length > 0 && (
        <div className='bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 mb-3'>
          <h6 className='text-xs font-bold text-rose-400 mb-2 flex items-center gap-2'>
            <AlertTriangle className='w-3 h-3' /> Discrepancies (
            {discrepancies.length})
          </h6>
          <div className='space-y-1'>
            {discrepancies.map((disc, i) => (
              <div key={i} className='text-xs text-rose-300 font-mono'>
                <span className='text-rose-500'>⚠️</span>{' '}
                {disc.warning || `${disc.field} mismatch detected`}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings Section */}
      {warnings.length > 0 && (
        <div className='bg-amber-500/10 border border-amber-500/30 rounded-lg p-3'>
          <h6 className='text-xs font-bold text-amber-400 mb-2 flex items-center gap-2'>
            <AlertCircle className='w-3 h-3' /> Warnings
          </h6>
          <div className='space-y-1'>
            {warnings.map((warning, i) => (
              <div key={i} className='text-xs text-amber-300'>
                • {warning}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interpretation Guide */}
      {isSuspicious && (
        <div className='bg-rose-500/10 border border-rose-500/20 rounded-lg p-3 mt-3 text-xs text-slate-400'>
          <p className='font-semibold text-rose-400 mb-1'>What this means:</p>
          <p>
            The GPS or timestamp data in your image's EXIF tags differs from
            what's visible in the overlay. This could indicate:
          </p>
          <ul className='list-disc list-inside space-y-0.5 mt-1 text-slate-500'>
            <li>The image was edited after the overlay was added</li>
            <li>Location/time was spoofed</li>
            <li>Different devices/cameras contributed metadata</li>
          </ul>
        </div>
      )}

      {isStripped && (
        <div className='bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 mt-3 text-xs text-slate-400'>
          <p className='font-semibold text-amber-400 mb-1'>What this means:</p>
          <p>
            The EXIF metadata has been removed from the image file, but the
            visual overlay persists. Location/timestamp info is only available
            from the overlay text.
          </p>
        </div>
      )}

      {isVerified && (
        <div className='bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3 mt-3 text-xs text-slate-400'>
          <p className='font-semibold text-emerald-400 mb-1'>
            What this means:
          </p>
          <p>
            ✓ The image metadata appears authentic. Both EXIF data and visible
            overlay contain matching information, suggesting the image hasn't
            been tampered with.
          </p>
        </div>
      )}
    </motion.section>
  );
}
