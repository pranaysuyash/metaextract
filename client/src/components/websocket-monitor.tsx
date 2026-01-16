import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Activity, 
  Wifi, 
  WifiOff, 
  MemoryStick, 
  Clock, 
  Users, 
  AlertTriangle,
  RefreshCw,
  Trash2
} from 'lucide-react';

interface WebSocketMetrics {
  totalConnections: number;
  activeConnections: number;
  staleConnections: number;
  memoryUsage: number;
}

interface WebSocketStatus {
  status: 'healthy' | 'warning' | 'error';
  metrics: WebSocketMetrics;
  config: {
    maxConnectionsPerSession: number;
    connectionTimeoutMs: number;
    heartbeatIntervalMs: number;
    staleConnectionThresholdMs: number;
  };
  timestamp: number;
}

export function WebSocketMonitor() {
  const [status, setStatus] = useState<WebSocketStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedSession, setSelectedSession] = useState<string>('');

  const fetchStatus = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch('/api/images_mvp/websocket/status');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setStatus(data);
    } catch (err) {
      console.error('Failed to fetch WebSocket status:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch status');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const cleanupSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`/api/images_mvp/websocket/cleanup/${sessionId}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('Cleanup result:', result);
      
      // Refresh status after cleanup
      await fetchStatus();
    } catch (err) {
      console.error('Failed to cleanup session:', err);
      setError(err instanceof Error ? err.message : 'Failed to cleanup session');
    }
  }, [fetchStatus]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchStatus();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, fetchStatus]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'healthy': return 'default';
      case 'warning': return 'secondary';
      case 'error': return 'destructive';
      default: return 'outline';
    }
  };

  const formatMemory = (bytes: number) => {
    const mb = bytes / 1024 / 1024;
    return `${mb.toFixed(1)} MB`;
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  if (isLoading && !status) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>WebSocket Monitor</CardTitle>
          <CardDescription>Loading WebSocket status...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <RefreshCw className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>WebSocket Monitor</CardTitle>
          <CardDescription>Failed to load WebSocket status</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button onClick={fetchStatus} className="mt-4" variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  const { metrics, config, status: healthStatus } = status;
  const hasIssues = metrics.staleConnections > 0 || metrics.totalConnections > 100;

  return (
    <div className="space-y-4">
      {/* Main Status Card */}
      <Card className="w-full">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-sm font-medium">WebSocket Status</CardTitle>
            <CardDescription>Real-time connection health</CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant={getStatusBadgeVariant(healthStatus)}>
              {healthStatus.toUpperCase()}
            </Badge>
            <div className={`w-2 h-2 rounded-full ${getStatusColor(healthStatus)}`} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Users className="w-4 h-4" />
                <span>Total Connections</span>
              </div>
              <div className="text-2xl font-bold">{metrics.totalConnections}</div>
            </div>
            
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Activity className="w-4 h-4" />
                <span>Active</span>
              </div>
              <div className="text-2xl font-bold text-green-600">{metrics.activeConnections}</div>
            </div>
            
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Clock className="w-4 h-4" />
                <span>Stale</span>
              </div>
              <div className="text-2xl font-bold text-yellow-600">{metrics.staleConnections}</div>
            </div>
            
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <MemoryStick className="w-4 h-4" />
                <span>Memory</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">{formatMemory(metrics.memoryUsage)}</div>
            </div>
          </div>

          {hasIssues && (
            <Alert className="mt-4" variant={metrics.staleConnections > metrics.totalConnections * 0.1 ? "destructive" : "default"}>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {metrics.staleConnections > 0 
                  ? `${metrics.staleConnections} stale connections detected. Consider manual cleanup.`
                  : 'High connection count detected. Monitor for potential issues.'
                }
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Configuration Card */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Configuration</CardTitle>
          <CardDescription>WebSocket connection settings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Max per Session:</span>
                <span className="font-medium">{config.maxConnectionsPerSession}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Connection Timeout:</span>
                <span className="font-medium">{formatDuration(config.connectionTimeoutMs)}</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Heartbeat Interval:</span>
                <span className="font-medium">{formatDuration(config.heartbeatIntervalMs)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Stale Threshold:</span>
                <span className="font-medium">{formatDuration(config.staleConnectionThresholdMs)}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Controls Card */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Controls</CardTitle>
          <CardDescription>Monitor and manage WebSocket connections</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button 
              onClick={fetchStatus} 
              variant="outline" 
              size="sm"
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            
            <Button 
              onClick={() => setAutoRefresh(!autoRefresh)} 
              variant={autoRefresh ? "default" : "outline"} 
              size="sm"
            >
              {autoRefresh ? (
                <>
                  <Wifi className="w-4 h-4 mr-2" />
                  Auto-refresh ON
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 mr-2" />
                  Auto-refresh OFF
                </>
              )}
            </Button>

            {metrics.staleConnections > 0 && (
              <Button 
                onClick={() => {
                  // Cleanup all sessions with stale connections
                  // In a real implementation, you'd iterate through sessions
                  cleanupSession('stale_sessions');
                }} 
                variant="destructive" 
                size="sm"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Cleanup Stale ({metrics.staleConnections})
              </Button>
            )}
          </div>

          <div className="mt-4 text-xs text-muted-foreground">
            Last updated: {new Date(status.timestamp).toLocaleTimeString()}
          </div>
        </CardContent>
      </Card>

      {/* Session Cleanup Card */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Session Cleanup</CardTitle>
          <CardDescription>Manually cleanup connections for a specific session</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Enter session ID..."
              value={selectedSession}
              onChange={(e) => setSelectedSession(e.target.value)}
              className="flex-1 px-3 py-2 border border-input bg-background rounded-md text-sm"
            />
            <Button 
              onClick={() => selectedSession && cleanupSession(selectedSession)} 
              variant="outline" 
              size="sm"
              disabled={!selectedSession}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Cleanup Session
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}