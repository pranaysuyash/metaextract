// client/src/components/viz/AudioWaveformViz.tsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Activity,
  Play,
  Pause,
  Volume2,
  Music,
  Clock,
  Mic,
  Radio,
  Disc,
} from 'lucide-react';

interface AudioMetadata {
  duration?: number;
  bitrate?: number;
  sample_rate?: number;
  channels?: number;
  bit_depth?: number;
  codec?: string;
  artist?: string;
  album?: string;
  title?: string;
  genre?: string;
  year?: number;
}

interface AudioWaveformVizProps {
  audio?: AudioMetadata;
}

// Generate simulated waveform data
function generateWaveformData(points: number = 200): number[] {
  return Array.from({ length: points }, (_, i) => {
    const base = 30 + Math.random() * 20;
    const wave1 = Math.sin(i * 0.1) * 20;
    const wave2 = Math.sin(i * 0.05) * 15;
    const wave3 = Math.sin(i * 0.2) * 10;
    const noise = (Math.random() - 0.5) * 15;
    return Math.max(5, base + wave1 + wave2 + wave3 + noise);
  });
}

function formatDuration(seconds: number | undefined): string {
  if (!seconds) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatBitrate(bitsPerSecond: number | undefined): string {
  if (!bitsPerSecond) return 'Unknown';
  if (bitsPerSecond >= 1000000)
    return `${(bitsPerSecond / 1000000).toFixed(1)} Mbps`;
  if (bitsPerSecond >= 1000) return `${(bitsPerSecond / 1000).toFixed(0)} kbps`;
  return `${bitsPerSecond} bps`;
}

export function AudioWaveformViz({ audio }: AudioWaveformVizProps) {
  const [waveformData] = useState(() => generateWaveformData(200));
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(80);
  const maxValue = Math.max(...waveformData);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && audio?.duration) {
      interval = setInterval(() => {
        setCurrentTime(prev => {
          if (prev >= audio.duration!) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 0.1;
        });
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isPlaying, audio?.duration]);

  const progress = audio?.duration ? (currentTime / audio.duration) * 100 : 0;
  const waveformWidth = (currentTime / (audio?.duration || 1)) * 100;

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Audio Waveform
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Track info */}
        <div className="flex items-center gap-3 mb-4 p-3 rounded-lg bg-muted/50">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Music className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-medium truncate">
              {audio?.title || 'Unknown Track'}
            </div>
            <div className="text-sm text-muted-foreground truncate">
              {audio?.artist || 'Unknown Artist'} ·{' '}
              {audio?.album || 'Unknown Album'}
            </div>
          </div>
          {audio?.genre && (
            <Badge variant="outline" className="text-xs">
              {audio.genre}
            </Badge>
          )}
        </div>

        {/* Waveform visualization */}
        <div className="relative h-[120px] w-full mb-4 bg-gradient-to-b from-muted/30 to-muted/10 rounded-lg overflow-hidden transition-all duration-300 hover:shadow-md">
          {/* Animated border when playing */}
          {isPlaying && (
            <div className="absolute inset-0 border-2 border-primary/50 rounded-lg animate-pulse" />
          )}
          {/* Background waveform */}
          <svg
            className="w-full h-full absolute inset-0"
            viewBox="0 0 200 100"
            preserveAspectRatio="none"
            role="img"
            aria-label="Audio waveform visualization"
          >
            <title>Audio Waveform</title>
            <defs>
              <linearGradient id="waveGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="hsl(var(--primary))" />
                <stop offset="100%" stopColor="hsl(var(--primary) / 0.3)" />
              </linearGradient>
            </defs>
            <path
              d={`M0,50 ${waveformData.map((v, i) => `L${(i / waveformData.length) * 200},${50 - (v / maxValue) * 40}`).join(' ')} L200,50 Z`}
              fill="url(#waveGradient)"
              opacity="0.4"
            />
            <path
              d={waveformData
                .map(
                  (v, i) =>
                    `L${(i / waveformData.length) * 200},${50 + (v / maxValue) * 40}`
                )
                .join(' ')}
              fill="none"
              stroke="hsl(var(--muted-foreground))"
              strokeWidth="0.5"
              opacity="0.5"
            />
          </svg>

          {/* Playhead */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-red-500"
            style={{ left: `${waveformWidth}%` }}
          />

          {/* Progress fill */}
          <div
            className="absolute top-0 bottom-0 bg-primary/20"
            style={{ width: `${waveformWidth}%` }}
          />
        </div>

        {/* Controls */}
        <div className="flex items-center gap-4 mb-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? (
              <Pause className="w-4 h-4" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </Button>

          <div className="flex-1">
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
              <span>{formatDuration(currentTime)}</span>
              <span>{formatDuration(audio?.duration)}</span>
            </div>
            <Progress value={progress} className="h-1" />
          </div>

          <div className="flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-muted-foreground" />
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={e => setVolume(Number(e.target.value))}
              className="w-20 h-1 accent-primary"
            />
          </div>
        </div>

        {/* Audio technical details */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <div className="p-2 rounded bg-muted/30 text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mb-1">
              <Disc className="w-3 h-3" />
              Format
            </div>
            <div className="font-mono text-sm">{audio?.codec || 'Unknown'}</div>
          </div>

          <div className="p-2 rounded bg-muted/30 text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mb-1">
              <Radio className="w-3 h-3" />
              Sample Rate
            </div>
            <div className="font-mono text-sm">
              {audio?.sample_rate
                ? `${(audio.sample_rate / 1000).toFixed(0)} kHz`
                : '?'}
            </div>
          </div>

          <div className="p-2 rounded bg-muted/30 text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mb-1">
              <Mic className="w-3 h-3" />
              Channels
            </div>
            <div className="font-mono text-sm">
              {audio?.channels || '?'}{' '}
              {audio?.channels === 1
                ? 'Mono'
                : audio?.channels === 2
                  ? 'Stereo'
                  : ''}
            </div>
          </div>

          <div className="p-2 rounded bg-muted/30 text-center">
            <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground mb-1">
              <Clock className="w-3 h-3" />
              Bit Depth
            </div>
            <div className="font-mono text-sm">
              {audio?.bit_depth || '?'} bit
            </div>
          </div>
        </div>

        {/* Bitrate */}
        <div className="mt-3 p-2 rounded bg-muted/30 text-center text-sm">
          <span className="text-muted-foreground">Bitrate: </span>
          <span className="font-mono">{formatBitrate(audio?.bitrate)}</span>
        </div>
      </CardContent>
    </Card>
  );
}
