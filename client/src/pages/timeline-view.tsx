import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Timeline } from '@/components/v2-results/Timeline';

interface TimelineEvent {
  id: string;
  timestamp: string;
  eventType: string;
  description: string;
  location?: string;
  confidence?: number;
  source: string;
  tags?: string[];
}

const TimelineViewPage: React.FC = () => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  // Mock data for demonstration
  useEffect(() => {
    // Simulate loading timeline data
    const mockEvents: TimelineEvent[] = [
      {
        id: '1',
        timestamp: '2025-01-04T10:30:00Z',
        eventType: 'file creation',
        description: 'Original image file created',
        location: 'New York, NY',
        confidence: 95,
        source: 'Camera EXIF data',
        tags: ['original', 'capture']
      },
      {
        id: '2',
        timestamp: '2025-01-04T10:31:15Z',
        eventType: 'location',
        description: 'GPS coordinates recorded',
        location: 'New York, NY',
        confidence: 98,
        source: 'GPS sensor',
        tags: ['gps', 'coordinates']
      },
      {
        id: '3',
        timestamp: '2025-01-04T10:32:30Z',
        eventType: 'capture',
        description: 'Photo captured with Canon EOS R5',
        location: 'New York, NY',
        confidence: 92,
        source: 'Camera make/model',
        tags: ['camera', 'capture']
      },
      {
        id: '4',
        timestamp: '2025-01-04T11:15:22Z',
        eventType: 'transfer',
        description: 'File transferred to computer',
        confidence: 88,
        source: 'File system timestamp',
        tags: ['transfer', 'computer']
      },
      {
        id: '5',
        timestamp: '2025-01-04T12:45:10Z',
        eventType: 'extraction',
        description: 'Metadata extracted using MetaExtract',
        confidence: 96,
        source: 'MetaExtract analysis',
        tags: ['analysis', 'metadata']
      },
      {
        id: '6',
        timestamp: '2025-01-04T13:20:05Z',
        eventType: 'modification',
        description: 'File edited in photo editor',
        confidence: 75,
        source: 'File modification timestamp',
        tags: ['edit', 'modification']
      },
      {
        id: '7',
        timestamp: '2025-01-04T14:30:45Z',
        eventType: 'upload',
        description: 'File uploaded to cloud storage',
        confidence: 90,
        source: 'Cloud service log',
        tags: ['upload', 'cloud']
      }
    ];

    setTimeout(() => {
      setEvents(mockEvents);
      setLoading(false);
    }, 800);
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Timeline View</h1>
          <p className="text-slate-300">Reconstructing the chronological sequence of events</p>
        </div>
        
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
            <p className="text-white">Loading timeline data...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Timeline View</h1>
        <p className="text-slate-300">Reconstructed chronological sequence of events for the selected file</p>
      </div>

      <Timeline 
        events={events} 
        title="File History Timeline" 
      />
    </div>
  );
};

export default TimelineViewPage;