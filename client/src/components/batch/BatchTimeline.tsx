import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Timeline,
  TimelineItem,
  TimelineConnector,
  TimelineHeader,
  TimelineTitle,
  TimelineTime,
  TimelineDescription,
  TimelineIcon,
  TimelineContent,
} from '@/components/ui/timeline';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  FileText,
  TrendingUp,
  Calendar
} from 'lucide-react';
import { format, differenceInSeconds, differenceInMinutes } from 'date-fns';
import { cn } from '@/lib/utils';

interface BatchResult {
  id: string;
  filename: string;
  status: 'success' | 'error' | 'processing' | 'pending';
  extractionDate: string;
  fieldsExtracted: number;
  fileSize: number;
  fileType: string;
  authenticityScore?: number;
  metadata: Record<string, any>;
  processingTime?: number;
  errorMessage?: string;
}

interface BatchJob {
  id: string;
  name: string;
  createdAt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  totalFiles: number;
  processedFiles: number;
  results: BatchResult[];
}

interface BatchTimelineProps {
  results: BatchResult[];
  batchJob: BatchJob;
}

export const BatchTimeline: React.FC<BatchTimelineProps> = ({ results, batchJob }) => {
  const getStatusIcon = (status: BatchResult['status']) => {
    switch (status) {
      case 'success': 
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'error': 
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'processing': 
        return <Clock className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'pending': 
        return <AlertCircle className="w-4 h-4 text-blue-500" />;
      default: 
        return <FileText className="w-4 h-4 text-slate-500" />;
    }
  };

  const getStatusColor = (status: BatchResult['status']) => {
    switch (status) {
      case 'success': return 'emerald';
      case 'error': return 'red';
      case 'processing': return 'yellow';
      case 'pending': return 'blue';
      default: return 'slate';
    }
  };

  const formatProcessingTime = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const getTimelineStats = () => {
    if (results.length === 0) return null;

    const sortedResults = [...results].sort((a, b) => 
      new Date(a.extractionDate).getTime() - new Date(b.extractionDate).getTime()
    );

    const startTime = new Date(sortedResults[0].extractionDate);
    const endTime = new Date(sortedResults[sortedResults.length - 1].extractionDate);
    const totalDuration = differenceInSeconds(endTime, startTime);
    
    const processingTimes = results.flatMap(result =>
      typeof result.processingTime === 'number' ? [result.processingTime] : []
    );
    const avgProcessingTime = processingTimes.length > 0 
      ? processingTimes.reduce((sum, time) => sum + time, 0) / processingTimes.length 
      : 0;
    const fastestProcessing =
      processingTimes.length > 0 ? Math.min(...processingTimes) : 0;
    const slowestProcessing =
      processingTimes.length > 0 ? Math.max(...processingTimes) : 0;

    const successRate = (results.filter(r => r.status === 'success').length / results.length) * 100;

    return {
      startTime,
      endTime,
      totalDuration,
      avgProcessingTime,
      fastestProcessing,
      slowestProcessing,
      successRate,
      totalFiles: results.length,
      successfulFiles: results.filter(r => r.status === 'success').length,
      errorFiles: results.filter(r => r.status === 'error').length,
    };
  };

  const stats = getTimelineStats();

  if (!stats) {
    return (
      <Card className="bg-card border-white/10">
        <CardContent className="py-12 text-center">
          <Calendar className="w-12 h-12 mx-auto mb-4 text-slate-500" />
          <p className="text-white">No timeline data available</p>
          <p className="text-sm text-slate-300 mt-1">
            Process some files to see the timeline
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Timeline Overview */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-primary" />
            Processing Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Start Time</p>
              <p className="text-lg font-bold text-white">
                {format(stats.startTime, 'HH:mm:ss')}
              </p>
              <p className="text-xs text-slate-400">
                {format(stats.startTime, 'MMM dd, yyyy')}
              </p>
            </div>
            
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">End Time</p>
              <p className="text-lg font-bold text-white">
                {format(stats.endTime, 'HH:mm:ss')}
              </p>
              <p className="text-xs text-slate-400">
                {format(stats.endTime, 'MMM dd, yyyy')}
              </p>
            </div>
            
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Total Duration</p>
              <p className="text-lg font-bold text-white">
                {stats.totalDuration < 60 
                  ? `${stats.totalDuration}s`
                  : `${Math.round(stats.totalDuration / 60)}m ${stats.totalDuration % 60}s`
                }
              </p>
              <p className="text-xs text-slate-400">
                for {stats.totalFiles} files
              </p>
            </div>
            
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Success Rate</p>
              <p className="text-lg font-bold text-white">
                {Math.round(stats.successRate)}%
              </p>
              <p className="text-xs text-slate-400">
                {stats.successfulFiles}/{stats.totalFiles} files
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Timeline */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            File Processing Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Timeline>
            {results
              .sort((a, b) => new Date(b.extractionDate).getTime() - new Date(a.extractionDate).getTime())
              .map((result, index) => {
                const processingTime = result.processingTime || 0;
                const isLast = index === results.length - 1;
                
                return (
                  <TimelineItem key={result.id}>
                    {!isLast && <TimelineConnector />}
                    
                    <TimelineHeader>
                      <TimelineIcon color={getStatusColor(result.status)}>
                        {getStatusIcon(result.status)}
                      </TimelineIcon>
                      <div className="flex-1">
                        <TimelineTitle className="text-white">
                          {result.filename}
                        </TimelineTitle>
                        <TimelineTime className="text-slate-400">
                          {format(new Date(result.extractionDate), 'MMM dd, yyyy HH:mm:ss')}
                        </TimelineTime>
                      </div>
                      <Badge 
                        variant="secondary" 
                        className={cn(
                          "capitalize",
                          result.status === 'success' && "bg-emerald-500/20 text-emerald-400",
                          result.status === 'error' && "bg-red-500/20 text-red-400",
                          result.status === 'processing' && "bg-yellow-500/20 text-yellow-400 animate-pulse",
                          result.status === 'pending' && "bg-blue-500/20 text-blue-400"
                        )}
                      >
                        {result.status}
                      </Badge>
                    </TimelineHeader>
                    
                    <TimelineContent className="space-y-2">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-slate-400">Type:</span>
                          <span className="text-white ml-2">{result.fileType}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Size:</span>
                          <span className="text-white ml-2">{formatFileSize(result.fileSize)}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Fields:</span>
                          <span className="text-white ml-2">{result.fieldsExtracted}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Time:</span>
                          <span className="text-white ml-2">
                            {formatProcessingTime(processingTime)}
                          </span>
                        </div>
                      </div>
                      
                      {result.authenticityScore !== undefined && (
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400">Authenticity Score:</span>
                          <Badge 
                            variant="secondary" 
                            className={cn(
                              result.authenticityScore >= 80 && "bg-emerald-500/20 text-emerald-400",
                              result.authenticityScore >= 50 && result.authenticityScore < 80 && "bg-yellow-500/20 text-yellow-400",
                              result.authenticityScore < 50 && "bg-red-500/20 text-red-400"
                            )}
                          >
                            {result.authenticityScore}%
                          </Badge>
                        </div>
                      )}
                      
                      {result.errorMessage && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                          <p className="text-sm text-red-400">{result.errorMessage}</p>
                        </div>
                      )}
                      
                      {result.status === 'processing' && (
                        <div className="flex items-center gap-2 text-sm text-yellow-400">
                          <Clock className="w-4 h-4 animate-spin" />
                          Processing... This may take a few moments
                        </div>
                      )}
                      
                      {result.status === 'pending' && (
                        <div className="flex items-center gap-2 text-sm text-blue-400">
                          <Clock className="w-4 h-4" />
                          Waiting in queue...
                        </div>
                      )}
                    </TimelineContent>
                  </TimelineItem>
                );
              })}
          </Timeline>
        </CardContent>
      </Card>

      {/* Processing Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white text-sm">Processing Times</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-300">Average:</span>
                <span className="text-white">
                  {formatProcessingTime(stats.avgProcessingTime)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Fastest:</span>
                <span className="text-white">
                  {formatProcessingTime(stats.fastestProcessing)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Slowest:</span>
                <span className="text-white">
                  {formatProcessingTime(stats.slowestProcessing)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white text-sm">Status Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-slate-300">Successful:</span>
                <div className="flex items-center gap-2">
                  <span className="text-emerald-400 font-medium">{stats.successfulFiles}</span>
                  <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400">
                    {Math.round((stats.successfulFiles / stats.totalFiles) * 100)}%
                  </Badge>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-300">Errors:</span>
                <div className="flex items-center gap-2">
                  <span className="text-red-400 font-medium">{stats.errorFiles}</span>
                  <Badge variant="secondary" className="bg-red-500/20 text-red-400">
                    {Math.round((stats.errorFiles / stats.totalFiles) * 100)}%
                  </Badge>
                </div>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Total:</span>
                <span className="text-white font-medium">{stats.totalFiles}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white text-sm">Batch Info</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-300">Batch ID:</span>
                <span className="text-white font-mono text-xs">
                  {batchJob.id.slice(0, 8)}...
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Created:</span>
                <span className="text-white">
                  {format(new Date(batchJob.createdAt), 'MMM dd, HH:mm')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Status:</span>
                <Badge 
                  variant="secondary" 
                  className={cn(
                    "capitalize",
                    batchJob.status === 'completed' && "bg-emerald-500/20 text-emerald-400",
                    batchJob.status === 'failed' && "bg-red-500/20 text-red-400",
                    batchJob.status === 'processing' && "bg-yellow-500/20 text-yellow-400 animate-pulse",
                    batchJob.status === 'pending' && "bg-blue-500/20 text-blue-400"
                  )}
                >
                  {batchJob.status}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Helper function to format file size
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
