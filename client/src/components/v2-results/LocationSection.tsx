/**
 * Location Section Component
 *
 * Display GPS location information with map preview and reverse geocoding.
 * Transforms raw GPS data into meaningful location context.
 */

import React, { useEffect, useState } from 'react';
import { MapPin, Loader2, AlertCircle, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface LocationData {
  latitude: number;
  longitude: number;
}

export interface ReverseGeocodingResult {
  success: boolean;
  address?: string;
  city?: string;
  region?: string;
  country?: string;
  confidence?: 'high' | 'medium' | 'low';
  coordinates?: string;
  mapsUrl?: string;
  osmUrl?: string;
  cached?: boolean;
  error?: string;
}

interface LocationSectionProps {
  location?: LocationData | null;
  onLocationChange?: (result: ReverseGeocodingResult) => void;
  className?: string;
}

/**
 * Main LocationSection component
 */
export function LocationSection({
  location,
  onLocationChange,
  className
}: LocationSectionProps): React.ReactElement {
  const [geocoding, setGeocoding] = useState<ReverseGeocodingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Perform reverse geocoding when location changes
  useEffect(() => {
    if (!location) {
      setGeocoding(null);
      return;
    }

    const performGeocoding = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/api/geocode/reverse', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            latitude: location.latitude,
            longitude: location.longitude
          })
        });

        if (!response.ok) {
          throw new Error('Geocoding failed');
        }

        const result = await response.json() as ReverseGeocodingResult;
        setGeocoding(result);
        onLocationChange?.(result);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Geocoding error';
        setError(message);
        console.error('Geocoding error:', err);
      } finally {
        setLoading(false);
      }
    };

    performGeocoding();
  }, [location, onLocationChange]);

  if (!location) {
    return (
      <div className={cn('p-4 text-center text-gray-500', className)}>
        No location data available
      </div>
    );
  }

  if (loading) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-center justify-center p-6 rounded-lg bg-blue-50 dark:bg-blue-950">
          <Loader2 className="w-5 h-5 animate-spin text-blue-600 dark:text-blue-400 mr-2" />
          <span className="text-sm text-blue-700 dark:text-blue-300">
            Looking up location...
          </span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn('space-y-4', className)}>
        <div className="flex items-start gap-3 p-4 rounded-lg bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-700 dark:text-red-300">
              Location lookup failed
            </p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-1">
              {error}
            </p>
          </div>
        </div>

        {/* Fall back to coordinates */}
        <CoordinatesCard latitude={location.latitude} longitude={location.longitude} />
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Main location card */}
      {geocoding && (
        <LocationCard
          address={geocoding.address}
          city={geocoding.city}
          region={geocoding.region}
          country={geocoding.country}
          confidence={geocoding.confidence}
          mapsUrl={geocoding.mapsUrl}
          cached={geocoding.cached}
        />
      )}

      {/* Coordinates fallback */}
      <CoordinatesCard latitude={location.latitude} longitude={location.longitude} />

      {/* Map links */}
      <MapLinks
        latitude={location.latitude}
        longitude={location.longitude}
        mapsUrl={geocoding?.mapsUrl}
        osmUrl={geocoding?.osmUrl}
      />
    </div>
  );
}

/**
 * Main location card display
 */
interface LocationCardProps {
  address?: string;
  city?: string;
  region?: string;
  country?: string;
  confidence?: 'high' | 'medium' | 'low';
  mapsUrl?: string;
  cached?: boolean;
}

function LocationCard({
  address,
  city,
  region,
  country,
  confidence = 'medium',
  mapsUrl,
  cached
}: LocationCardProps): React.ReactElement {
  const bgColor = {
    high: 'bg-green-50 dark:bg-green-950',
    medium: 'bg-blue-50 dark:bg-blue-950',
    low: 'bg-yellow-50 dark:bg-yellow-950'
  };

  const borderColor = {
    high: 'border-green-200 dark:border-green-800',
    medium: 'border-blue-200 dark:border-blue-800',
    low: 'border-yellow-200 dark:border-yellow-800'
  };

  const textColor = {
    high: 'text-green-900 dark:text-green-100',
    medium: 'text-blue-900 dark:text-blue-100',
    low: 'text-yellow-900 dark:text-yellow-100'
  };

  return (
    <div
      className={cn(
        'p-4 rounded-lg border',
        bgColor[confidence],
        borderColor[confidence]
      )}
    >
      <div className="flex items-start gap-3">
        <MapPin className={cn('w-5 h-5 flex-shrink-0 mt-0.5', {
          'text-green-600 dark:text-green-400': confidence === 'high',
          'text-blue-600 dark:text-blue-400': confidence === 'medium',
          'text-yellow-600 dark:text-yellow-400': confidence === 'low'
        })} />

        <div className="flex-1">
          <p className={cn('text-sm font-medium text-gray-600 dark:text-gray-400')}>
            Location
          </p>

          {address && (
            <p className={cn('text-base font-semibold mt-2', textColor[confidence])}>
              {address}
            </p>
          )}

          {/* Location hierarchy */}
          {(city || region || country) && (
            <div className={cn('text-xs mt-2 space-y-1', textColor[confidence])}>
              {city && <p>📍 City: {city}</p>}
              {region && <p>🗺️ Region: {region}</p>}
              {country && <p>🌍 Country: {country}</p>}
            </div>
          )}

          {/* Metadata */}
          <div className="flex items-center gap-2 mt-3 text-xs">
            {cached && (
              <span className="px-2 py-1 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                Cached
              </span>
            )}
            <span className="text-gray-500 dark:text-gray-400">
              {confidence === 'high' && '✅ High confidence'}
              {confidence === 'medium' && '⚠️ Medium confidence'}
              {confidence === 'low' && '❓ Low confidence'}
            </span>
          </div>
        </div>

        {mapsUrl && (
          <a
            href={mapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              'p-2 rounded hover:bg-opacity-75 transition-colors',
              {
                'hover:bg-green-200 dark:hover:bg-green-800': confidence === 'high',
                'hover:bg-blue-200 dark:hover:bg-blue-800': confidence === 'medium',
                'hover:bg-yellow-200 dark:hover:bg-yellow-800': confidence === 'low'
              }
            )}
            title="Open in Google Maps"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        )}
      </div>
    </div>
  );
}

/**
 * Coordinates display card
 */
interface CoordinatesCardProps {
  latitude: number;
  longitude: number;
}

function CoordinatesCard({
  latitude,
  longitude
}: CoordinatesCardProps): React.ReactElement {
  const latDir = latitude >= 0 ? 'N' : 'S';
  const lonDir = longitude >= 0 ? 'E' : 'W';
  const formattedCoords = `${Math.abs(latitude).toFixed(4)}° ${latDir}, ${Math.abs(longitude).toFixed(4)}° ${lonDir}`;

  return (
    <div className="p-4 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
        Exact Coordinates
      </p>
      <p className="text-sm font-mono text-gray-700 dark:text-gray-300 mt-2">
        {formattedCoords}
      </p>
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        Latitude: {latitude.toFixed(6)} | Longitude: {longitude.toFixed(6)}
      </p>
    </div>
  );
}

/**
 * Map links section
 */
interface MapLinksProps {
  latitude: number;
  longitude: number;
  mapsUrl?: string;
  osmUrl?: string;
}

function MapLinks({
  latitude,
  longitude,
  mapsUrl,
  osmUrl
}: MapLinksProps): React.ReactElement {
  return (
    <div className="flex gap-2">
      {mapsUrl && (
        <a
          href={mapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          Google Maps
        </a>
      )}

      {osmUrl && (
        <a
          href={osmUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          OpenStreetMap
        </a>
      )}
    </div>
  );
}

/**
 * Hook to perform reverse geocoding
 */
export function useReverseGeocode(location: LocationData | null | undefined) {
  const [result, setResult] = useState<ReverseGeocodingResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!location) {
      setResult(null);
      return;
    }

    const performGeocoding = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/api/geocode/reverse', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            latitude: location.latitude,
            longitude: location.longitude
          })
        });

        if (!response.ok) {
          throw new Error('Geocoding failed');
        }

        const data = await response.json() as ReverseGeocodingResult;
        setResult(data);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Geocoding error';
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    performGeocoding();
  }, [location]);

  return { result, loading, error };
}
