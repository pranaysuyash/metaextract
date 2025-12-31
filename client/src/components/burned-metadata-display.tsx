import React from 'react';
import {
  MapPin,
  Thermometer,
  Cloud,
  Wind,
  Mountain,
  Compass,
  Camera,
  ExternalLink,
} from 'lucide-react';
import { motion } from 'framer-motion';

interface BurnedMetadataDisplayProps {
  burned_metadata?: {
    has_burned_metadata: boolean;
    confidence: 'none' | 'low' | 'medium' | 'high';
    parsed_data?: {
      gps?: { latitude: number; longitude: number; google_maps_url: string };
      location?: { city: string; state: string; country: string };
      address?: string;
      plus_code?: string;
      timestamp?: string;
      weather?: {
        temperature?: string;
        humidity?: string;
        speed?: string;
        altitude?: string;
      };
      compass?: { degrees: string; direction: string };
      camera_app?: string;
    };
  } | null;
  isUnlocked?: boolean;
}

const confidenceColors = {
  high: 'text-emerald-400',
  medium: 'text-yellow-400',
  low: 'text-orange-400',
  none: 'text-slate-600',
};

const confidenceBg = {
  high: 'bg-emerald-500/10 border-emerald-500/30',
  medium: 'bg-yellow-500/10 border-yellow-500/30',
  low: 'bg-orange-500/10 border-orange-500/30',
  none: 'bg-slate-500/10 border-slate-500/30',
};

export function BurnedMetadataDisplay({ burned_metadata }: BurnedMetadataDisplayProps) {
  if (!burned_metadata?.has_burned_metadata || !burned_metadata?.parsed_data) {
    return null;
  }

  const parsed = burned_metadata.parsed_data;

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className='mb-4 flex items-center justify-between'>
        <h4 className='flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-cyan-400'>
          <Camera className='w-3 h-3' /> Burned-In Metadata (OCR)
          <span
            className={`text-[10px] font-normal ml-auto px-2 py-1 rounded border ${
              confidenceBg[burned_metadata.confidence]
            }`}
          >
            <span className={confidenceColors[burned_metadata.confidence]}>
              Confidence: {burned_metadata.confidence.toUpperCase()}
            </span>
          </span>
        </h4>
      </div>

      <div
        className={`rounded-lg border mb-4 p-4 ${
          confidenceBg[burned_metadata.confidence]
        }`}
      >
        <p className='text-xs text-slate-400 mb-3'>
          ✓ This image contains metadata visually overlaid on the pixels
          (extracted via OCR)
        </p>

        {parsed.camera_app && (
          <div className='text-xs text-slate-300 mb-2'>
            <span className='text-slate-500'>Camera App:</span>{' '}
            {parsed.camera_app}
          </div>
        )}
      </div>

      <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
        {/* GPS Section */}
        {parsed.gps && (
          <div className='bg-black/40 border border-white/10 rounded-lg p-3'>
            <h5 className='text-xs font-bold text-rose-400 mb-2 flex items-center gap-1'>
              <MapPin className='w-3 h-3' /> GPS Coordinates
            </h5>
            <div className='space-y-1 font-mono text-xs'>
              <div className='text-slate-400'>
                <span className='text-slate-600'>LAT:</span>{' '}
                {parsed.gps.latitude.toFixed(6)}
              </div>
              <div className='text-slate-400'>
                <span className='text-slate-600'>LON:</span>{' '}
                {parsed.gps.longitude.toFixed(6)}
              </div>
              <a
                href={parsed.gps.google_maps_url}
                target='_blank'
                rel='noopener noreferrer'
                className='inline-flex items-center gap-1 text-primary hover:text-primary/80 transition-colors mt-2 text-[10px]'
              >
                View on Maps <ExternalLink className='w-2.5 h-2.5' />
              </a>
            </div>
          </div>
        )}

        {/* Location Section */}
        {(parsed.location || parsed.address) && (
          <div className='bg-black/40 border border-white/10 rounded-lg p-3'>
            <h5 className='text-xs font-bold text-blue-400 mb-2 flex items-center gap-1'>
              <MapPin className='w-3 h-3' /> Location
            </h5>
            <div className='space-y-1 text-xs text-slate-400 font-mono'>
              {parsed.location && (
                <>
                  <div>
                    <span className='text-slate-600'>City:</span>{' '}
                    {parsed.location.city}
                  </div>
                  <div>
                    <span className='text-slate-600'>State:</span>{' '}
                    {parsed.location.state}
                  </div>
                  <div>
                    <span className='text-slate-600'>Country:</span>{' '}
                    {parsed.location.country}
                  </div>
                </>
              )}
              {parsed.address && (
                <div className='mt-2 p-2 bg-white/5 rounded border border-white/5 text-[10px]'>
                  <span className='text-slate-600 block mb-1'>Address:</span>
                  {parsed.address}
                </div>
              )}
              {parsed.plus_code && (
                <div className='mt-2 text-[10px]'>
                  <span className='text-slate-600'>Plus Code:</span>{' '}
                  {parsed.plus_code}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Timestamp Section */}
        {parsed.timestamp && (
          <div className='bg-black/40 border border-white/10 rounded-lg p-3'>
            <h5 className='text-xs font-bold text-purple-400 mb-2 flex items-center gap-1'>
              🕐 Timestamp
            </h5>
            <div className='text-xs text-slate-400 font-mono wrap-break-word'>
              {parsed.timestamp}
            </div>
          </div>
        )}

        {/* Weather Section */}
        {parsed.weather && Object.values(parsed.weather).some((v) => v) && (
          <div className='bg-black/40 border border-white/10 rounded-lg p-3'>
            <h5 className='text-xs font-bold text-amber-400 mb-2 flex items-center gap-1'>
              <Cloud className='w-3 h-3' /> Weather
            </h5>
            <div className='space-y-1 text-xs text-slate-400 font-mono'>
              {parsed.weather.temperature && (
                <div className='flex items-center gap-2'>
                  <Thermometer className='w-3 h-3 text-orange-400' />
                  <span>{parsed.weather.temperature}°C</span>
                </div>
              )}
              {parsed.weather.humidity && (
                <div className='flex items-center gap-2'>
                  <Cloud className='w-3 h-3 text-blue-400' />
                  <span>{parsed.weather.humidity}% Humidity</span>
                </div>
              )}
              {parsed.weather.speed && (
                <div className='flex items-center gap-2'>
                  <Wind className='w-3 h-3 text-cyan-400' />
                  <span>{parsed.weather.speed} km/h</span>
                </div>
              )}
              {parsed.weather.altitude && (
                <div className='flex items-center gap-2'>
                  <Mountain className='w-3 h-3 text-slate-400' />
                  <span>{parsed.weather.altitude} m</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Compass Section */}
        {parsed.compass && (
          <div className='bg-black/40 border border-white/10 rounded-lg p-3'>
            <h5 className='text-xs font-bold text-indigo-400 mb-2 flex items-center gap-1'>
              <Compass className='w-3 h-3' /> Compass Direction
            </h5>
            <div className='text-xs text-slate-400 font-mono'>
              <span className='text-indigo-400 font-bold text-base'>
                {parsed.compass.degrees}°
              </span>
              <span className='ml-2'>{parsed.compass.direction}</span>
            </div>
          </div>
        )}
      </div>
    </motion.section>
  );
}
