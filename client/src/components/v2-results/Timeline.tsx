import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  Camera, 
  FileText, 
  Database, 
  Eye, 
  Download,
  Filter,
  Search
} from 'lucide-react';

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

interface TimelineProps {
  events: TimelineEvent[];
  title?: string;
}

export const Timeline: React.FC<TimelineProps> = ({ 
  events, 
  title = 'Event Timeline' 
}) => {
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [sortBy, setSortBy] = useState<'time' | 'confidence'>('time');
  
  // Filter and sort events
  const filteredEvents = events
    .filter(event => {
      const matchesFilter = filter === 'all' || event.eventType.toLowerCase().includes(filter.toLowerCase());
      const matchesSearch = searchTerm === '' || 
        event.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.source.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesFilter && matchesSearch;
    })
    .sort((a, b) => {
      if (sortBy === 'time') {
        return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      } else {
        return (b.confidence || 0) - (a.confidence || 0);
      }
    });
  
  // Get unique event types for filter
  const eventTypes = Array.from(new Set(events.map(event => event.eventType)));
  
  const getEventTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'capture':
      case 'photo':
      case 'image':
        return <Camera className="w-4 h-4 text-blue-500" />;
      case 'location':
      case 'gps':
        return <MapPin className="w-4 h-4 text-green-500" />;
      case 'file':
      case 'creation':
        return <FileText className="w-4 h-4 text-purple-500" />;
      case 'extraction':
      case 'analysis':
        return <Database className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-slate-500" />;
    }
  };
  
  const getConfidenceColor = (confidence?: number) => {
    if (confidence === undefined) return 'text-slate-300';
    if (confidence >= 80) return 'text-emerald-400';
    if (confidence >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };
  
  const getConfidenceLabel = (confidence?: number) => {
    if (confidence === undefined) return 'Unknown';
    if (confidence >= 80) return 'High';
    if (confidence >= 60) return 'Medium';
    return 'Low';
  };

  return (
    <div className="space-y-6">
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-primary" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Filters and Controls */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-slate-300" />
              <input
                type="text"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-1 bg-muted border border-white/10 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-300" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-1 bg-muted border border-white/10 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="all">All Types</option>
                {eventTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-300" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'time' | 'confidence')}
                className="px-3 py-1 bg-muted border border-white/10 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="time">Sort by Time</option>
                <option value="confidence">Sort by Confidence</option>
              </select>
            </div>
            
            <Button variant="outline" size="sm" className="ml-auto gap-2">
              <Download className="w-4 h-4" />
              Export Timeline
            </Button>
          </div>
          
          {/* Timeline */}
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary to-transparent"></div>
            
            <div className="space-y-6 pl-10">
              {filteredEvents.length > 0 ? (
                filteredEvents.map((event, index) => (
                  <div key={event.id} className="relative">
                    {/* Timeline dot */}
                    <div className="absolute left-[-22px] top-3 w-4 h-4 rounded-full bg-primary border-4 border-card z-10"></div>
                    
                    <Card className="bg-muted/20 border-white/10 hover:bg-muted/30 transition-colors">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              {getEventTypeIcon(event.eventType)}
                              <h3 className="font-semibold text-white capitalize">{event.eventType}</h3>
                              {event.confidence !== undefined && (
                                <Badge 
                                  variant="outline" 
                                  className={`${getConfidenceColor(event.confidence)} border-current`}
                                >
                                  {getConfidenceLabel(event.confidence)} ({event.confidence}%)
                                </Badge>
                              )}
                            </div>
                            
                            <p className="text-slate-200 mb-2">{event.description}</p>
                            
                            <div className="flex flex-wrap gap-4 text-sm">
                              <div className="flex items-center gap-1">
                                <Clock className="w-4 h-4 text-slate-300" />
                                <span className="text-slate-300">
                                  {new Date(event.timestamp).toLocaleString()}
                                </span>
                              </div>
                              
                              {event.location && (
                                <div className="flex items-center gap-1">
                                  <MapPin className="w-4 h-4 text-slate-300" />
                                  <span className="text-slate-300">{event.location}</span>
                                </div>
                              )}
                              
                              <div className="flex items-center gap-1">
                                <Database className="w-4 h-4 text-slate-300" />
                                <span className="text-slate-300">Source: {event.source}</span>
                              </div>
                            </div>
                            
                            {event.tags && event.tags.length > 0 && (
                              <div className="flex flex-wrap gap-2 mt-3">
                                {event.tags.map((tag, idx) => (
                                  <Badge key={idx} variant="secondary" className="text-xs">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ))
              ) : (
                <div className="text-center py-12 text-slate-500">
                  <Calendar className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No events match your filters</p>
                  <p className="text-sm mt-1">Try changing your search or filter criteria</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Timeline Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Calendar className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Total Events</p>
                <p className="text-xl font-bold text-white">{events.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-500/10 rounded-lg">
                <Eye className="w-5 h-5 text-emerald-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Avg Confidence</p>
                <p className="text-xl font-bold text-white">
                  {events.length > 0 
                    ? Math.round(events.reduce((sum, e) => sum + (e.confidence || 0), 0) / events.length) + '%' 
                    : '0%'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Clock className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Time Span</p>
                {events.length > 0 ? (
                  <p className="text-xl font-bold text-white">
                    {Math.max(1, 
                      Math.floor(
                        (new Date(events[events.length - 1].timestamp).getTime() - 
                         new Date(events[0].timestamp).getTime()) / (1000 * 60 * 60 * 24)
                      )
                    )} days
                  </p>
                ) : (
                  <p className="text-xl font-bold text-white">0 days</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <FileText className="w-5 h-5 text-purple-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Event Types</p>
                <p className="text-xl font-bold text-white">{eventTypes.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Event Type Distribution */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-primary" />
            Event Type Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {eventTypes.map(type => {
              const count = events.filter(e => e.eventType === type).length;
              const percentage = events.length > 0 ? Math.round((count / events.length) * 100) : 0;
              
              return (
                <div key={type} className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-300 capitalize">{type}</span>
                    <span className="text-white font-medium">{count}</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full" 
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="text-right text-xs text-slate-300">{percentage}%</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};