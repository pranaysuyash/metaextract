// client/src/components/viz/LocationMiniMap.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  MapPin,
  Navigation,
  ExternalLink,
  Clock,
  Map as MapIcon,
  Layers,
} from 'lucide-react';

interface LocationMiniMapProps {
  gps?: {
    latitude?: number;
    longitude?: number;
    latitude_decimal?: number;
    longitude_decimal?: number;
    altitude_meters?: number;
    gps_timestamp?: string;
    gps_speed?: number;
    gps_direction?: number;
    coordinates_formatted?: string;
    google_maps_url?: string;
    openstreetmap_url?: string;
  };
  image?: {
    width?: number;
    height?: number;
  };
}

function formatCoordinates(
  lat: number | undefined,
  lon: number | undefined
): string {
  if (lat === undefined || lon === undefined) return 'Unknown';

  const latDir = lat >= 0 ? 'N' : 'S';
  const lonDir = lon >= 0 ? 'E' : 'W';

  const latAbs = Math.abs(lat);
  const lonAbs = Math.abs(lon);

  return `${latAbs.toFixed(4)}° ${latDir}, ${lonAbs.toFixed(4)}° ${lonDir}`;
}

function getRelativeTime(timestamp: string | undefined): string {
  if (!timestamp) return '';

  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 30) return `${diffDays} days ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  } catch {
    return '';
  }
}

export function LocationMiniMap({ gps, image }: LocationMiniMapProps) {
  const lat = gps?.latitude || gps?.latitude_decimal;
  const lon = gps?.longitude || gps?.longitude_decimal;

  const hasLocation = lat !== undefined && lon !== undefined;
  const googleMapsUrl =
    gps?.google_maps_url ||
    (lat !== undefined && lon !== undefined
      ? `https://www.google.com/maps?q=${lat},${lon}`
      : '');
  const osmUrl =
    gps?.openstreetmap_url ||
    (lat !== undefined && lon !== undefined
      ? `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=15/${lat}/${lon}`
      : '');

  // Simple map visualization (would use Leaflet/Mapbox for full implementation)
  const MapPlaceholder = () => (
    <div className="relative w-full h-full bg-gradient-to-br from-blue-100 via-green-50 to-blue-50 rounded-lg overflow-hidden">
      {/* Grid lines */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            'linear-gradient(rgba(0,0,0,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.05) 1px, transparent 1px)',
          backgroundSize: '20px 20px',
        }}
      />

      {/* Location marker */}
      {hasLocation && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="relative">
            <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center shadow-lg">
              <MapPin className="w-5 h-5 text-white" />
            </div>
            <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-red-500 rotate-45" />
          </div>
        </div>
      )}

      {/* Compass */}
      <div className="absolute top-3 right-3 w-8 h-8 bg-white/80 rounded-full flex items-center justify-center shadow">
        <Navigation
          className="w-5 h-5 text-red-500"
          style={{ transform: 'rotate(45deg)' }}
        />
      </div>

      {/* Scale */}
      <div className="absolute bottom-3 left-3 flex items-center gap-1 bg-white/80 px-2 py-1 rounded text-xs">
        <div className="w-8 h-0.5 bg-gray-600" />
        <span>1 km</span>
      </div>
    </div>
  );

  if (!hasLocation) {
    return (
      <Card className="w-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            Location
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] w-full bg-muted/50 rounded-lg flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No GPS data available</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <MapPin className="w-5 h-5" />
          Location
          <Badge variant="outline" className="ml-2">
            {gps?.altitude_meters
              ? `${gps.altitude_meters.toFixed(0)}m`
              : 'Surface'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Map visualization */}
        <div className="h-[200px] w-full mb-4">
          <MapPlaceholder />
        </div>

        {/* Coordinates */}
        <div className="flex items-center gap-2 mb-3 p-3 rounded-lg bg-muted/50">
          <MapIcon className="w-4 h-4 text-muted-foreground" />
          <span className="font-mono text-sm">
            {formatCoordinates(lat, lon)}
          </span>
        </div>

        {/* Additional info */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          {gps?.gps_speed !== undefined && (
            <div className="p-2 rounded bg-muted/30">
              <div className="text-xs text-muted-foreground">Speed</div>
              <div className="font-mono text-sm">
                {(gps.gps_speed * 3.6).toFixed(1)} km/h
              </div>
            </div>
          )}
          {gps?.gps_direction !== undefined && (
            <div className="p-2 rounded bg-muted/30">
              <div className="text-xs text-muted-foreground">Direction</div>
              <div className="font-mono text-sm">
                {gps.gps_direction.toFixed(0)}°
              </div>
            </div>
          )}
          {gps?.gps_timestamp && (
            <div className="p-2 rounded bg-muted/30 col-span-2">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">
                  GPS time:{' '}
                </span>
                <span className="text-sm">
                  {getRelativeTime(gps.gps_timestamp)}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Map links */}
        <div className="flex gap-2">
          <Button asChild variant="outline" size="sm" className="flex-1">
            <a href={googleMapsUrl} target="_blank" rel="noopener noreferrer">
              <MapPin className="w-4 h-4 mr-2" />
              Google Maps
              <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </Button>
          <Button asChild variant="outline" size="sm" className="flex-1">
            <a href={osmUrl} target="_blank" rel="noopener noreferrer">
              <Layers className="w-4 h-4 mr-2" />
              OpenStreetMap
              <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
