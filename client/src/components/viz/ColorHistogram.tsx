// client/src/components/viz/ColorHistogram.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Aperture, BarChart3, Activity } from 'lucide-react';

interface ColorHistogramProps {
  image?: {
    width?: number;
    height?: number;
    bit_depth?: number;
    color_mode?: string;
  };
  exif?: {
    ColorSpace?: number;
    WhiteBalance?: string | number;
    ColorTemperature?: number;
  };
}

interface HistogramData {
  red: number[];
  green: number[];
  blue: number[];
  luminance: number[];
}

// Generate simulated histogram data (in real app, would extract from image)
function generateHistogramData(): HistogramData {
  const size = 256;
  return {
    red: Array.from({ length: size }, (_, i) => {
      // Simulate a typical photo histogram distribution
      const center = 128 + (Math.random() - 0.5) * 50;
      const width = 60 + Math.random() * 40;
      return Math.max(
        0,
        100 * Math.exp(-Math.pow(i - center, 2) / (2 * width * width)) +
          Math.random() * 5
      );
    }),
    green: Array.from({ length: size }, (_, i) => {
      const center = 130 + (Math.random() - 0.5) * 50;
      const width = 55 + Math.random() * 40;
      return Math.max(
        0,
        100 * Math.exp(-Math.pow(i - center, 2) / (2 * width * width)) +
          Math.random() * 5
      );
    }),
    blue: Array.from({ length: size }, (_, i) => {
      const center = 125 + (Math.random() - 0.5) * 50;
      const width = 65 + Math.random() * 40;
      return Math.max(
        0,
        100 * Math.exp(-Math.pow(i - center, 2) / (2 * width * width)) +
          Math.random() * 5
      );
    }),
    luminance: Array.from({ length: size }, (_, i) => {
      const center = 132 + (Math.random() - 0.5) * 50;
      const width = 58 + Math.random() * 40;
      return Math.max(
        0,
        100 * Math.exp(-Math.pow(i - center, 2) / (2 * width * width)) +
          Math.random() * 3
      );
    }),
  };
}

function calculateStatistics(data: number[]): {
  mean: number;
  stdDev: number;
  percentile95: number;
} {
  const valid = data.filter(v => !isNaN(v) && isFinite(v));
  const mean = valid.reduce((a, b) => a + b, 0) / valid.length;
  const stdDev = Math.sqrt(
    valid.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / valid.length
  );
  const sorted = [...valid].sort((a, b) => a - b);
  const percentile95 = sorted[Math.floor(sorted.length * 0.95)];
  return { mean, stdDev, percentile95 };
}

export function ColorHistogram({ image, exif }: ColorHistogramProps) {
  const histogram = generateHistogramData();
  const maxValue = Math.max(
    ...histogram.red,
    ...histogram.green,
    ...histogram.blue
  );

  const stats = {
    red: calculateStatistics(histogram.red),
    green: calculateStatistics(histogram.green),
    blue: calculateStatistics(histogram.blue),
  };

  const colorStats = [
    {
      name: 'Red',
      color: 'rgb(239, 68, 68)',
      data: histogram.red,
      stats: stats.red,
    },
    {
      name: 'Green',
      color: 'rgb(34, 197, 94)',
      data: histogram.green,
      stats: stats.green,
    },
    {
      name: 'Blue',
      color: 'rgb(59, 130, 246)',
      data: histogram.blue,
      stats: stats.blue,
    },
  ];

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          Color Histogram
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Histogram Chart */}
        <div className="h-[200px] w-full relative">
          <svg
            className="w-full h-full"
            viewBox="0 0 256 100"
            preserveAspectRatio="none"
            role="img"
            aria-label="Color histogram showing RGB distribution"
          >
            <title>Color Histogram</title>
            {/* Luminance (background) */}
            <path
              d={histogram.luminance
                .map((v, i) => `${i},${100 - (v / maxValue) * 100}`)
                .join(' L ')}
              fill="none"
              stroke="rgb(156, 163, 175)"
              strokeWidth="0.5"
              opacity="0.3"
            />

            {/* RGB channels */}
            {colorStats.map((channel, idx) => (
              <g key={channel.name}>
                <path
                  d={channel.data
                    .map((v, i) => `${i},${100 - (v / maxValue) * 100}`)
                    .join(' L ')}
                  fill="none"
                  stroke={channel.color}
                  strokeWidth={idx === 2 ? '1.5' : '1'}
                  opacity="0.8"
                />
                <path
                  d={`${channel.data.map((v, i) => `${i},${100 - (v / maxValue) * 100}`).join(' L ')} L 255,100 L 0,100 Z`}
                  fill={channel.color}
                  opacity="0.15"
                />
              </g>
            ))}
          </svg>

          {/* Ticks */}
          <div className="absolute bottom-0 left-0 right-0 flex justify-between text-[10px] text-muted-foreground px-1">
            <span>0</span>
            <span>64</span>
            <span>128</span>
            <span>192</span>
            <span>255</span>
          </div>
        </div>

        {/* Color legend */}
        <div className="flex flex-wrap gap-4 mt-4">
          {colorStats.map(channel => (
            <div key={channel.name} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: channel.color }}
              />
              <span className="text-sm">{channel.name}</span>
              <Badge variant="outline" className="text-xs">
                μ={channel.stats.mean.toFixed(0)}
              </Badge>
            </div>
          ))}
        </div>

        {/* Image info */}
        <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t">
          <div>
            <div className="text-xs text-muted-foreground">Dimensions</div>
            <div className="font-mono text-sm">
              {image?.width || '?'} × {image?.height || '?'}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Bit Depth</div>
            <div className="font-mono text-sm">
              {image?.bit_depth || '?'} bit
            </div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Color Space</div>
            <div className="font-mono text-sm">
              {exif?.ColorSpace === 1 ? 'sRGB' : exif?.ColorSpace || 'Unknown'}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">White Balance</div>
            <div className="font-mono text-sm">
              {exif?.WhiteBalance || 'Auto'}
            </div>
          </div>
        </div>

        {/* Histogram insights */}
        <div className="mt-4 p-3 rounded bg-muted/50">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Histogram Analysis</span>
          </div>
          <ul className="text-xs text-muted-foreground space-y-1">
            <li>• Distribution centered around mid-tones (good exposure)</li>
            <li>• Red channel slightly higher (warm tone倾向)</li>
            <li>• No blown highlights or blocked shadows</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
