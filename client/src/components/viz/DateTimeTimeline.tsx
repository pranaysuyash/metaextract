// client/src/components/viz/DateTimeTimeline.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Calendar,
  Clock,
  Camera,
  FileEdit,
  History,
  AlertCircle,
} from 'lucide-react';

interface DateTimeTimelineProps {
  metadata: {
    // Image dates
    DateTimeOriginal?: string;
    CreateDate?: string;
    ModifyDate?: string;
    SubSecTimeOriginal?: string;
    // Filesystem dates
    FileCreateDate?: string;
    FileModifyDate?: string;
    FileAccessDate?: string;
    // Email dates
    email_date?: string;
    email_timestamp?: number;
    email_datetime_parsed?: string;
    email_hour_of_day?: number;
    email_day_of_week?: string;
    email_is_weekend?: boolean;
    // Derived
    capture_date_source?: string;
    location_embedded?: boolean;
  };
  fileType: 'image' | 'video' | 'audio' | 'document' | 'email' | 'other';
}

interface TimelineEvent {
  label: string;
  date: Date | null;
  isoDate: string;
  source: string;
  icon: React.ReactNode;
  color: string;
  tooltip: string;
}

export function DateTimeTimeline({
  metadata,
  fileType,
}: DateTimeTimelineProps) {
  const parseExifDate = (dateStr: string | undefined): Date | null => {
    if (!dateStr) return null;
    // EXIF format: "2024:01:15 14:30:45"
    const match = dateStr.match(
      /^(\d{4}):(\d{2}):(\d{2})\s+(\d{2}):(\d{2}):(\d{2})/
    );
    if (!match) return null;
    const [, year, month, day, hour, min, sec] = match;
    return new Date(
      parseInt(year),
      parseInt(month) - 1,
      parseInt(day),
      parseInt(hour),
      parseInt(min),
      parseInt(sec)
    );
  };

  const parseIsoDate = (dateStr: string | undefined): Date | null => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return isNaN(date.getTime()) ? null : date;
  };

  const formatDate = (date: Date | null): string => {
    if (!date) return 'Unknown';
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTime = (date: Date | null): string => {
    if (!date) return '';
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getTimeSince = (date: Date | null): string => {
    if (!date) return '';
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffDays > 365) return `${Math.floor(diffDays / 365)} years ago`;
    if (diffDays > 30) return `${Math.floor(diffDays / 30)} months ago`;
    if (diffDays > 0) return `${diffDays} days ago`;
    if (diffHours > 0) return `${diffHours} hours ago`;
    return `${diffMins} minutes ago`;
  };

  const events: TimelineEvent[] = [];

  if (fileType === 'image' || fileType === 'video') {
    // EXIF capture date (most reliable for photos)
    const captureDate = parseExifDate(metadata.DateTimeOriginal);
    events.push({
      label: 'Capture',
      date: captureDate,
      isoDate: metadata.DateTimeOriginal || '',
      source: 'EXIF:DateTimeOriginal',
      icon: <Camera className="w-4 h-4" />,
      color: 'text-green-600',
      tooltip: 'When the photo/video was actually captured',
    });

    // EXIF create date
    const createDate = parseExifDate(metadata.CreateDate);
    events.push({
      label: 'Created',
      date: createDate,
      isoDate: metadata.CreateDate || '',
      source: 'EXIF:CreateDate',
      icon: <FileEdit className="w-4 h-4" />,
      color: 'text-blue-600',
      tooltip: 'When the file was created by the device',
    });

    // EXIF modify date
    const modifyDate = parseExifDate(metadata.ModifyDate);
    events.push({
      label: 'Modified',
      date: modifyDate,
      isoDate: metadata.ModifyDate || '',
      source: 'EXIF:ModifyDate',
      icon: <History className="w-4 h-4" />,
      color: 'text-orange-600',
      tooltip: 'Last modification time in EXIF data',
    });

    // Filesystem dates
    const fsCreateDate = parseIsoDate(metadata.FileCreateDate);
    events.push({
      label: 'File Created',
      date: fsCreateDate,
      isoDate: metadata.FileCreateDate || '',
      source: 'filesystem',
      icon: <Calendar className="w-4 h-4" />,
      color: 'text-purple-600',
      tooltip: 'When the file was saved to disk',
    });

    const fsModifyDate = parseIsoDate(metadata.FileModifyDate);
    events.push({
      label: 'File Modified',
      date: fsModifyDate,
      isoDate: metadata.FileModifyDate || '',
      source: 'filesystem',
      icon: <Clock className="w-4 h-4" />,
      color: 'text-red-600',
      tooltip: 'When the file was last modified on disk',
    });
  }

  if (fileType === 'email') {
    const emailDate =
      parseIsoDate(metadata.email_datetime_parsed) ||
      (metadata.email_timestamp
        ? new Date(metadata.email_timestamp * 1000)
        : null);
    events.push({
      label: 'Sent',
      date: emailDate,
      isoDate: metadata.email_date || metadata.email_datetime_parsed || '',
      source: 'email',
      icon: <Camera className="w-4 h-4" />,
      color: 'text-green-600',
      tooltip: `Sent ${metadata.email_day_of_week || ''} at ${metadata.email_hour_of_day || ''}:00`,
    });
  }

  // Sort by date
  const sortedEvents = events
    .filter(e => e.date)
    .sort((a, b) => (a.date?.getTime() || 0) - (b.date?.getTime() || 0));

  // Find date anomalies
  let anomalyMessage = '';
  if (sortedEvents.length >= 2) {
    const first = sortedEvents[0].date?.getTime() || 0;
    const last = sortedEvents[sortedEvents.length - 1].date?.getTime() || 0;
    const diffHours = (last - first) / (1000 * 60 * 60);

    if (diffHours > 24) {
      anomalyMessage = `⚠️ ${sortedEvents[0].label} and ${sortedEvents[sortedEvents.length - 1].label} are ${Math.round(diffHours)} hours apart - check for data inconsistencies`;
    } else if (diffHours < 0) {
      anomalyMessage =
        '⚠️ Date order anomaly detected - check for clock issues or data manipulation';
    }
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <History className="w-5 h-5" />
          Timeline
          {anomalyMessage && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Badge
                    variant="secondary"
                    className="ml-2 bg-amber-100 text-amber-800 hover:bg-amber-100"
                  >
                    <AlertCircle className="w-3 h-3 mr-1" />
                    Anomaly
                  </Badge>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{anomalyMessage}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border" />

          <div className="space-y-4">
            {sortedEvents.map((event, idx) => (
              <div
                key={`${event.label}-${event.isoDate}-${idx}`}
                className="relative flex items-start gap-4 pl-12"
              >
                {/* Icon badge */}
                <div
                  className={`absolute left-2 w-8 h-8 rounded-full bg-background border-2 border-${event.color.replace('text-', '')} flex items-center justify-center z-10 ${event.color}`}
                >
                  {event.icon}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium">{event.label}</span>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Badge variant="outline" className="text-xs">
                            {event.source}
                          </Badge>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>{event.tooltip}</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>

                  <div className="text-sm text-muted-foreground mt-1">
                    <span className="font-mono">{formatDate(event.date)}</span>
                    {formatTime(event.date) && (
                      <>
                        {' · '}
                        <span className="font-mono">
                          {formatTime(event.date)}
                        </span>
                      </>
                    )}
                  </div>

                  <div className="text-xs text-muted-foreground mt-1">
                    {getTimeSince(event.date)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
