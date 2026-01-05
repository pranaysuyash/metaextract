// client/src/components/viz/CameraSettingsRadar.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
} from 'recharts';
import { Aperture, Timer, Focus, Zap, Sun, Droplets } from 'lucide-react';

interface CameraSettingsRadarProps {
  exif: {
    ISO?: number | string;
    FNumber?: number | string;
    ExposureTime?: string;
    FocalLength?: number | string;
    WhiteBalance?: string | number;
    ColorTemperature?: number | string;
    ExposureCompensation?: number | string;
    Flash?: string | number;
    DigitalZoomRatio?: number | string;
  };
  image?: {
    width?: number;
    height?: number;
    bit_depth?: number;
  };
}

interface CameraSetting {
  name: string;
  value: string | number | undefined;
  normalized: number;
  icon: React.ReactNode;
  description: string;
}

function parseExposure(
  exposureStr: string | number | undefined
): number | null {
  if (!exposureStr || typeof exposureStr === 'number') return null;
  // Format: "1/120" or "0.002" or "2"
  const match = String(exposureStr).match(/^(\d+\.?\d*)\/(\d+\.?\d*)$/);
  if (match) {
    return parseFloat(match[1]) / parseFloat(match[2]);
  }
  const val = parseFloat(exposureStr);
  return isNaN(val) ? null : val;
}

function normalizeISO(value: number | string | undefined): number {
  if (!value) return 0;
  const num = typeof value === 'string' ? parseInt(value) : value;
  if (isNaN(num)) return 0;
  // Log scale: 50 -> 0.2, 100 -> 0.4, 400 -> 0.6, 1600 -> 0.8, 6400 -> 1.0
  return Math.min(Math.log2(num / 50) / 7, 1);
}

function normalizeAperture(value: number | string | undefined): number {
  if (!value) return 0;
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return 0;
  // Aperture: f/1.4 -> 1.0, f/2.8 -> 0.5, f/5.6 -> 0.25, f/16 -> 0.1
  return Math.min(2.8 / num, 1);
}

function normalizeExposure(value: number | string | undefined): number {
  const exposure = typeof value === 'string' ? parseExposure(value) : value;
  if (!exposure) return 0.5;
  // Exposure: 1/4000 -> 1.0, 1/125 -> 0.5, 2s -> 0.2
  return Math.min(Math.abs(Math.log2(exposure * 1000)) / 12, 1);
}

function normalizeFocalLength(value: number | string | undefined): number {
  if (!value) return 0.5;
  const num = typeof value === 'string' ? parseInt(value) : value;
  if (isNaN(num)) return 0.5;
  // Focal length: 14mm -> 0.1, 35mm -> 0.3, 85mm -> 0.7, 600mm -> 1.0
  return Math.min(num / 600, 1);
}

function normalizeFlash(value: number | string | undefined): number {
  if (!value) return 0.5;
  const num = typeof value === 'string' ? parseInt(value) : value;
  // Flash fired: 1, not fired: 0
  return num > 0 ? 0.8 : 0.3;
}

function normalizeWhiteBalance(value: number | string | undefined): number {
  if (!value) return 0.5;
  // Temperature: 2000K -> 0, 6500K -> 0.5, 10000K -> 1.0
  const num = typeof value === 'string' ? parseInt(value) : value;
  if (isNaN(num)) return 0.5;
  return Math.min(Math.max((num - 2000) / 8000, 0), 1);
}

export function CameraSettingsRadar({ exif, image }: CameraSettingsRadarProps) {
  const data: CameraSetting[] = [
    {
      name: 'ISO',
      value: exif.ISO,
      normalized: normalizeISO(exif.ISO),
      icon: <Zap className="w-4 h-4" />,
      description: 'Light sensitivity',
    },
    {
      name: 'Aperture',
      value: exif.FNumber,
      normalized: normalizeAperture(exif.FNumber),
      icon: <Aperture className="w-4 h-4" />,
      description: 'f/' + (exif.FNumber || '?'),
    },
    {
      name: 'Shutter',
      value: exif.ExposureTime,
      normalized: normalizeExposure(exif.ExposureTime),
      icon: <Timer className="w-4 h-4" />,
      description: 'Exposure time',
    },
    {
      name: 'Focal',
      value: exif.FocalLength,
      normalized: normalizeFocalLength(exif.FocalLength),
      icon: <Focus className="w-4 h-4" />,
      description: (exif.FocalLength || '?') + 'mm',
    },
    {
      name: 'White Bal',
      value: exif.ColorTemperature || exif.WhiteBalance,
      normalized: normalizeWhiteBalance(
        exif.ColorTemperature || exif.WhiteBalance
      ),
      icon: <Sun className="w-4 h-4" />,
      description: 'Color temperature',
    },
    {
      name: 'Flash',
      value: exif.Flash,
      normalized: normalizeFlash(exif.Flash),
      icon: <Droplets className="w-4 h-4" />,
      description: exif.Flash ? 'Fired' : 'Not fired',
    },
  ];

  const radarData = data.map(d => ({
    subject: d.name,
    value: d.normalized * 100,
    fullMark: 100,
    description: d.description,
  }));

  const hasAnyData = data.some(d => d.normalized > 0);

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <Aperture className="w-5 h-5" />
          Camera Settings
        </CardTitle>
      </CardHeader>
      <CardContent>
        {!hasAnyData ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            No camera settings available
          </div>
        ) : (
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="hsl(var(--border))" />
                <PolarAngleAxis
                  dataKey="subject"
                  tick={{ fill: 'hsl(var(--foreground))', fontSize: 12 }}
                />
                <PolarRadiusAxis
                  angle={30}
                  domain={[0, 100]}
                  tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                />
                <Radar
                  name="Settings"
                  dataKey="value"
                  stroke="hsl(var(--primary))"
                  fill="hsl(var(--primary))"
                  fillOpacity={0.4}
                  strokeWidth={2}
                />
                <RechartsTooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-background border rounded-lg shadow-lg p-3">
                          <p className="font-medium">{data.subject}</p>
                          <p className="text-sm text-muted-foreground">
                            {data.description}
                          </p>
                          <p className="text-xs mt-1">
                            Value: {data.value.toFixed(0)}%
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Settings summary */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-4">
          {data
            .filter(d => d.value)
            .map(setting => (
              <div
                key={setting.name}
                className="flex items-center gap-2 p-2 rounded-lg bg-muted/50"
              >
                <span className="text-muted-foreground">{setting.icon}</span>
                <div>
                  <p className="text-xs text-muted-foreground">
                    {setting.name}
                  </p>
                  <p className="text-sm font-medium">{setting.description}</p>
                </div>
              </div>
            ))}
        </div>
      </CardContent>
    </Card>
  );
}
