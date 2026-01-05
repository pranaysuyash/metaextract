// client/src/pages/PremiumTimelineDemoPage.tsx
import React from 'react';
import { PremiumTimeline } from '@/components/viz';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  FileImage,
  FileType,
  FileText,
  FileAudio,
  FileVideo,
} from 'lucide-react';

const sampleFiles = [
  {
    id: 1,
    filename: 'summer_vacation_2024.jpg',
    type: 'image' as const,
    icon: FileImage,
    created: new Date('2024-07-15T14:30:00'),
    modified: new Date('2024-08-22T09:15:00'),
    accessed: new Date('2025-01-03T16:45:00'),
    dateTaken: new Date('2024-07-15T14:28:30'),
    size: '4.2 MB',
    sizeBytes: 4404019,
    dimensions: '4032x3024',
    location: 'Maldives',
    camera: 'iPhone 15 Pro',
    tags: ['vacation', 'beach', 'summer'],
  },
  {
    id: 2,
    filename: 'project_report.pdf',
    type: 'document' as const,
    icon: FileType,
    created: new Date('2024-09-10T10:00:00'),
    modified: new Date('2024-12-15T14:30:00'),
    accessed: new Date('2025-01-04T11:20:00'),
    size: '1.8 MB',
    sizeBytes: 1887436,
    pages: 24,
    author: 'John Doe',
    tags: ['work', 'report', 'Q4'],
  },
  {
    id: 3,
    filename: 'meeting_notes.txt',
    type: 'text' as const,
    icon: FileText,
    created: new Date('2024-11-20T09:00:00'),
    modified: new Date('2024-11-20T17:45:00'),
    accessed: new Date('2025-01-02T08:30:00'),
    size: '12 KB',
    sizeBytes: 12288,
    tags: ['meeting', 'notes'],
  },
  {
    id: 4,
    filename: 'photo_edited.psd',
    type: 'image' as const,
    icon: FileImage,
    created: new Date('2024-06-20T10:20:00'),
    modified: new Date('2024-12-01T16:30:00'),
    accessed: new Date('2025-01-05T09:00:00'),
    dateTaken: new Date('2024-06-20T10:15:00'),
    size: '24.5 MB',
    sizeBytes: 25690102,
    dimensions: '6000x4000',
    location: 'Studio',
    camera: 'Adobe Photoshop',
    tags: ['design', 'edited'],
  },
  {
    id: 5,
    filename: 'music_track.mp3',
    type: 'audio' as const,
    icon: FileAudio,
    created: new Date('2024-05-01T12:00:00'),
    modified: new Date('2024-05-01T12:00:00'),
    accessed: new Date('2025-01-01T20:00:00'),
    size: '8.7 MB',
    sizeBytes: 9123456,
    tags: ['music', 'demo'],
  },
  {
    id: 6,
    filename: 'screenshot.png',
    type: 'image' as const,
    icon: FileImage,
    created: new Date('2024-10-05T08:45:00'),
    modified: new Date('2024-10-05T08:45:00'),
    accessed: new Date('2024-12-20T14:00:00'),
    dateTaken: new Date('2024-10-05T08:45:00'),
    size: '1.2 MB',
    sizeBytes: 1258291,
    dimensions: '2560x1440',
    tags: ['screenshot', 'work'],
  },
];

export default function PremiumTimelineDemoPage() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold">Premium Timeline Visualization</h1>
          <Badge variant="secondary">Interactive Demo</Badge>
        </div>
        <p className="text-muted-foreground text-lg">
          Advanced timeline component with playback controls, filters,
          comparison mode, and export options.
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Features</CardTitle>
          <CardDescription>
            Comprehensive timeline visualization for file metadata analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div className="space-y-1">
              <strong className="text-primary">Playback Controls</strong>
              <p className="text-muted-foreground">
                Play/pause, speed control, seek
              </p>
            </div>
            <div className="space-y-1">
              <strong className="text-primary">Zoom & Pan</strong>
              <p className="text-muted-foreground">
                Mouse wheel zoom, drag to pan
              </p>
            </div>
            <div className="space-y-1">
              <strong className="text-primary">Filters</strong>
              <p className="text-muted-foreground">
                Event types, date range, file types
              </p>
            </div>
            <div className="space-y-1">
              <strong className="text-primary">Comparison</strong>
              <p className="text-muted-foreground">
                Side-by-side file analysis
              </p>
            </div>
            <div className="space-y-1">
              <strong className="text-primary">Export</strong>
              <p className="text-muted-foreground">JSON and CSV export</p>
            </div>
            <div className="space-y-1">
              <strong className="text-primary">Keyboard Shortcuts</strong>
              <p className="text-muted-foreground">
                Space, arrows, +/- , D, F, S
              </p>
            </div>
            <div className="space-y-1">
              <strong className="text-primary">Dark/Light Mode</strong>
              <p className="text-muted-foreground">Toggle theme support</p>
            </div>
            <div className="space-y-1">
              <strong className="text-primary">Minimap</strong>
              <p className="text-muted-foreground">
                Overview with zoom indicator
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <PremiumTimeline files={sampleFiles} />
    </div>
  );
}
