// client/src/components/viz/VideoKeyframesViz.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Film, Video, Clock, Layers, Maximize2, Database } from 'lucide-react';

interface VideoMetadata {
  duration?: number;
  width?: number;
  height?: number;
  frame_rate?: number;
  bitrate?: number;
  codec?: string;
  audio_codec?: string;
  container?: string;
}

interface VideoKeyframesVizProps {
  video?: VideoMetadata;
}

// Generate simulated keyframes
function generateKeyframes(
  count: number = 6
): Array<{ id: number; time: number; label: string }> {
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    time: i * 10 + Math.floor(Math.random() * 5),
    label: `${i * 10 + Math.floor(Math.random() * 5)}s`,
  }));
}

function formatDuration(seconds: number | undefined): string {
  if (!seconds) return '0:00';
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatBitrate(bitsPerSecond: number | undefined): string {
  if (!bitsPerSecond) return 'Unknown';
  if (bitsPerSecond >= 1000000)
    return `${(bitsPerSecond / 1000000).toFixed(1)} Mbps`;
  if (bitsPerSecond >= 1000) return `${(bitsPerSecond / 1000).toFixed(0)} kbps`;
  return `${bitsPerSecond} bps`;
}

// Placeholder thumbnail component
function ThumbnailPlaceholder({
  time,
  label,
  isActive,
}: {
  time: number;
  label: string;
  isActive?: boolean;
}) {
  return (
    <div
      className={`relative group cursor-pointer ${isActive ? 'ring-2 ring-primary' : ''}`}
    >
      <div className="aspect-video bg-gradient-to-br from-slate-700 to-slate-800 rounded-md flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <Video className="w-8 h-8 text-white/30" />
        </div>
        {/* Simulated frame content */}
        <div className="absolute inset-0 opacity-20 bg-gradient-to-br from-blue-500/20 to-purple-500/20" />
      </div>
      <div className="absolute bottom-1 right-1 bg-black/70 text-white text-[10px] px-1 rounded">
        {label}
      </div>
      {/* Play indicator on hover */}
      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors rounded-md flex items-center justify-center">
        <div className="w-8 h-8 bg-white/90 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-0 h-0 border-l-4 border-l-slate-800 border-y-4 border-y-transparent ml-0.5" />
        </div>
      </div>
    </div>
  );
}

export function VideoKeyframesViz({ video }: VideoKeyframesVizProps) {
  const keyframes = generateKeyframes(6);
  const aspectRatio =
    video?.width && video?.height ? video.width / video.height : 16 / 9;

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <Film className="w-5 h-5" />
          Video Overview
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Video info header */}
        <div className="flex items-center gap-3 mb-4 p-3 rounded-lg bg-muted/50">
          <div
            className="w-16 aspect-video rounded bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center"
            style={{ aspectRatio }}
          >
            <Film className="w-8 h-8 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-medium">Video File</div>
            <div className="text-sm text-muted-foreground">
              {video?.width && video?.height
                ? `${video.width} × ${video.height}`
                : 'Unknown resolution'}
            </div>
            <div className="flex flex-wrap gap-1 mt-1">
              {video?.codec && (
                <Badge variant="outline" className="text-xs">
                  {video.codec}
                </Badge>
              )}
              {video?.container && (
                <Badge variant="outline" className="text-xs">
                  {video.container}
                </Badge>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Clock className="w-4 h-4" />
              {formatDuration(video?.duration)}
            </div>
            {video?.frame_rate && (
              <div className="text-xs text-muted-foreground">
                {video.frame_rate.toFixed(1)} fps
              </div>
            )}
          </div>
        </div>

        {/* Timeline with keyframes */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Layers className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Keyframes</span>
          </div>

          {/* Timeline bar */}
          <div className="relative h-8 bg-muted/30 rounded mb-3">
            <div className="absolute inset-y-0 left-0 right-0 flex items-center">
              {/* Time markers */}
              {Array.from({ length: 11 }, (_, i) => (
                <div
                  key={i}
                  className="flex-1 border-l border-muted-foreground/20 h-full relative"
                >
                  <span className="absolute -bottom-4 left-0 text-[8px] text-muted-foreground">
                    {i * 10}s
                  </span>
                </div>
              ))}
            </div>
            {/* Progress indicator */}
            <div
              className="absolute top-0 bottom-0 w-0.5 bg-primary"
              style={{ left: '30%' }}
            />
          </div>

          {/* Keyframe thumbnails */}
          <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
            {keyframes.map(kf => (
              <ThumbnailPlaceholder
                key={`kf-${kf.time}-${kf.label}`}
                time={kf.time}
                label={kf.label}
                isActive={kf.id === 1} // Simulate second frame as active
              />
            ))}
          </div>
        </div>

        {/* Technical details */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <div className="p-2 rounded bg-muted/30 text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mb-1">
              <Maximize2 className="w-3 h-3" />
              Resolution
            </div>
            <div className="font-mono text-sm">
              {video?.width && video?.height
                ? `${video.width}×${video.height}`
                : 'Unknown'}
            </div>
          </div>

          <div className="p-2 rounded bg-muted/30 text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mb-1">
              <Film className="w-3 h-3" />
              Frame Rate
            </div>
            <div className="font-mono text-sm">
              {video?.frame_rate ? `${video.frame_rate.toFixed(1)} fps` : '?'}
            </div>
          </div>

          <div className="p-2 rounded bg-muted/30 text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mb-1">
              <Database className="w-3 h-3" />
              Bitrate
            </div>
            <div className="font-mono text-sm">
              {formatBitrate(video?.bitrate)}
            </div>
          </div>

          <div className="p-2 rounded bg-muted/30 text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mb-1">
              <Video className="w-3 h-3" />
              Audio
            </div>
            <div className="font-mono text-sm">
              {video?.audio_codec || 'None'}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
