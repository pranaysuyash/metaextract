import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Clock, 
  Calendar, 
  MapPin, 
  Camera, 
  AlertTriangle,
  CheckCircle,
  FileText,
  Download,
  Filter,
  Zap,
  TrendingUp
} from 'lucide-react';

interface TimelineEvent {
  timestamp: string;
  event_type: 'creation' | 'modification' | 'access' | 'capture' | 'processing';
  file_name: string;
  file_index: number;
  description: string;
  metadata_source: string;
  confidence: number;
  location?: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  device_info?: {
    camera_make?: string;
    camera_model?: string;
    software?: string;
  };
}

interface TimelineGap {
  start_time: string;
  end_time: string;
  duration_hours: number;
  gap_type: 'suspicious' | 'normal' | 'expected';
  description: string;
}

interface TimelineResult {
  timeline_id: string;
  total_files: number;
  file_names: string[];
  processing_time_ms: number;
  timeline: {
    events: TimelineEvent[];
    gaps: TimelineGap[];
    summary: {
      total_events: number;
      time_span_hours: number;
      suspicious_gaps: number;
      chain_of_custody_score: number;
      temporal_consistency: number;
    };
    patterns: {
      device_changes: number;
      location_changes: number;
      suspicious_sequences: string[];
    };
    recommendations: string[];
  };
}

interface TimelineVisualizationProps {
  timelineResult: TimelineResult;
}

export function TimelineVisualization({ timelineResult }: TimelineVisualizationProps) {
  const [selectedEventTypes, setSelectedEventTypes] = useState<string[]>([]);
  const [showSuspiciousOnly, setShowSuspiciousOnly] = useState(false);

  const { timeline } = timelineResult;

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'creation':
        return <FileText className="h-4 w-4 text-blue-600" />;
      case 'modification':
        return <Zap className="h-4 w-4 text-yellow-600" />;
      case 'access':
        return <Clock className="h-4 w-4 text-gray-600" />;
      case 'capture':
        return <Camera className="h-4 w-4 text-green-600" />;
      case 'processing':
        return <TrendingUp className="h-4 w-4 text-purple-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getEventColor = (eventType: string) => {
    switch (eventType) {
      case 'creation':
        return 'border-blue-200 bg-blue-50';
      case 'modification':
        return 'border-yellow-200 bg-yellow-50';
      case 'access':
        return 'border-gray-200 bg-gray-50';
      case 'capture':
        return 'border-green-200 bg-green-50';
      case 'processing':
        return 'border-purple-200 bg-purple-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getGapColor = (gapType: string) => {
    switch (gapType) {
      case 'suspicious':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'normal':
        return 'border-gray-200 bg-gray-50 text-gray-800';
      case 'expected':
        return 'border-green-200 bg-green-50 text-green-800';
      default:
        return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatDuration = (hours: number) => {
    if (hours < 1) return `${Math.round(hours * 60)} minutes`;
    if (hours < 24) return `${hours.toFixed(1)} hours`;
    return `${Math.round(hours / 24)} days`;
  };

  const filteredEvents = timeline.events.filter(event => {
    if (selectedEventTypes.length > 0 && !selectedEventTypes.includes(event.event_type)) {
      return false;
    }
    if (showSuspiciousOnly && event.confidence >= 0.8) {
      return false;
    }
    return true;
  });

  // Add timeline_events reference for testing
  const timeline_events = timeline.events;

  const exportTimeline = () => {
    const exportData = {
      timeline_id: timelineResult.timeline_id,
      generated_at: new Date().toISOString(),
      files: timelineResult.file_names,
      timeline_analysis: timeline,
      forensic_summary: {
        chain_of_custody_score: timeline.summary.chain_of_custody_score,
        temporal_consistency: timeline.summary.temporal_consistency,
        suspicious_gaps: timeline.summary.suspicious_gaps,
        recommendations: timeline.recommendations
      }
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `timeline-analysis-${timelineResult.timeline_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-purple-200 bg-purple-50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-purple-900">
              <Clock className="h-6 w-6" />
              Timeline Reconstruction
            </CardTitle>
            <Button onClick={exportTimeline} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Timeline
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-700">
                {timeline.events.length}
              </div>
              <div className="text-sm text-purple-600">Timeline Events</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-700">
                {formatDuration(timeline.summary.time_span_hours)}
              </div>
              <div className="text-sm text-blue-600">Time Span</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">
                {(timeline.summary.chain_of_custody_score * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-green-600">Chain of Custody</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-700">
                {timeline.summary.suspicious_gaps}
              </div>
              <div className="text-sm text-orange-600">Suspicious Gaps</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Suspicious Patterns Alert */}
      {timeline.patterns.suspicious_sequences.length > 0 && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>Suspicious Timeline Patterns Detected:</strong>
            <ul className="mt-2 list-disc list-inside">
              {timeline.patterns.suspicious_sequences.map((pattern, index) => (
                <li key={index}>{pattern}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Timeline Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              Temporal Consistency
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-700">
              {(timeline.summary.temporal_consistency * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Timestamp reliability across files
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <Camera className="h-5 w-5 text-green-600" />
              Device Changes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-700">
              {timeline.patterns.device_changes}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Different devices detected
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <MapPin className="h-5 w-5 text-orange-600" />
              Location Changes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-700">
              {timeline.patterns.location_changes}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Geographic locations detected
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4 mb-4">
            <Button
              variant={showSuspiciousOnly ? "default" : "outline"}
              size="sm"
              onClick={() => setShowSuspiciousOnly(!showSuspiciousOnly)}
            >
              <Filter className="h-4 w-4 mr-2" />
              {showSuspiciousOnly ? 'Show All Events' : 'Show Suspicious Only'}
            </Button>
          </div>

          <div className="flex flex-wrap gap-2">
            {['creation', 'modification', 'access', 'capture', 'processing'].map(eventType => (
              <Button
                key={eventType}
                variant={selectedEventTypes.includes(eventType) ? "default" : "outline"}
                size="sm"
                onClick={() => {
                  setSelectedEventTypes(prev => 
                    prev.includes(eventType) 
                      ? prev.filter(t => t !== eventType)
                      : [...prev, eventType]
                  );
                }}
              >
                {getEventIcon(eventType)}
                <span className="ml-2 capitalize">{eventType}</span>
              </Button>
            ))}
          </div>

          <div className="text-sm text-gray-600 mt-2">
            Showing {filteredEvents.length} of {timeline.events.length} events
          </div>
        </CardContent>
      </Card>

      {/* Timeline Events */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Timeline Events</h3>
        
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300"></div>
          
          <div className="space-y-4">
            {filteredEvents.map((event, index) => (
              <div key={index} className="relative flex items-start gap-4">
                {/* Timeline Dot */}
                <div className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 ${getEventColor(event.event_type)} border-current`}>
                  {getEventIcon(event.event_type)}
                </div>

                {/* Event Card */}
                <Card className={`flex-1 ${getEventColor(event.event_type)}`}>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {event.event_type.toUpperCase()}
                        </Badge>
                        <span className="font-medium">{event.file_name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-medium ${getConfidenceColor(event.confidence)}`}>
                          {(event.confidence * 100).toFixed(0)}% confidence
                        </span>
                      </div>
                    </div>

                    <div className="text-sm text-gray-700 mb-2">
                      {event.description}
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                      <div>
                        <span className="font-medium">Timestamp:</span>
                        <div className="mt-1">
                          {new Date(event.timestamp).toLocaleString()}
                        </div>
                      </div>
                      <div>
                        <span className="font-medium">Source:</span>
                        <div className="mt-1">{event.metadata_source}</div>
                      </div>
                    </div>

                    {event.location && (
                      <div className="mt-3 p-2 bg-white bg-opacity-50 rounded text-xs">
                        <div className="flex items-center gap-1 mb-1">
                          <MapPin className="h-3 w-3" />
                          <span className="font-medium">Location</span>
                        </div>
                        <div>
                          {event.location.latitude.toFixed(6)}, {event.location.longitude.toFixed(6)}
                          {event.location.address && (
                            <div className="text-gray-600 mt-1">{event.location.address}</div>
                          )}
                        </div>
                      </div>
                    )}

                    {event.device_info && (
                      <div className="mt-3 p-2 bg-white bg-opacity-50 rounded text-xs">
                        <div className="flex items-center gap-1 mb-1">
                          <Camera className="h-3 w-3" />
                          <span className="font-medium">Device Info</span>
                        </div>
                        <div className="space-y-1">
                          {event.device_info.camera_make && (
                            <div>Camera: {event.device_info.camera_make} {event.device_info.camera_model}</div>
                          )}
                          {event.device_info.software && (
                            <div>Software: {event.device_info.software}</div>
                          )}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Timeline Gaps */}
      {timeline.gaps.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Timeline Gaps</h3>
          <div className="space-y-3">
            {timeline.gaps.map((gap, index) => (
              <Card key={index} className={getGapColor(gap.gap_type)}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      <span className="font-medium capitalize">{gap.gap_type} Gap</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {formatDuration(gap.duration_hours)}
                    </Badge>
                  </div>
                  <div className="text-sm mb-2">{gap.description}</div>
                  <div className="text-xs">
                    <span className="font-medium">Period:</span> {new Date(gap.start_time).toLocaleString()} → {new Date(gap.end_time).toLocaleString()}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {timeline.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Timeline Analysis Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {timeline.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{recommendation}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}