import type { Express, Request, Response } from 'express';
import type { WebSocket } from 'ws';
import { wsConnectionManager } from '../utils/websocket-manager';

/**
 * Enhanced WebSocket progress tracking with memory leak prevention
 */
export function registerImagesMvpWebSocketRoutes(app: Express) {
  if (typeof (app as any).ws !== 'function') {
    console.log('[ImagesMVP] WebSocket not available in this environment; progress tracking disabled');
    return;
  }

  // WebSocket endpoint for real-time progress tracking
  (app as any).ws('/api/images_mvp/progress/:sessionId', (ws: WebSocket, req: Request) => {
    const sessionId = req.params.sessionId;
    
    if (!sessionId) {
      ws.close(1002, 'Session ID required');
      return;
    }

    try {
      // Use the connection manager to handle the connection lifecycle
      const connection = wsConnectionManager.addConnection(ws, sessionId);

      // Send initial connection confirmation
      ws.send(JSON.stringify({
        type: 'connected',
        sessionId,
        timestamp: Date.now(),
        connectionId: connection.connectionId,
      }));

      console.log(`[ImagesMVP] WebSocket connection established: ${connection.connectionId} for session: ${sessionId}`);
    } catch (error) {
      console.error(`[ImagesMVP] Failed to establish WebSocket connection for session ${sessionId}:`, error);
      ws.close(1011, 'Internal server error');
    }
  });

  // HTTP endpoint for connection status and debugging
  app.get('/api/images_mvp/websocket/status', (req: Request, res: Response) => {
    try {
      const metrics = wsConnectionManager.getMetrics();
      
      res.json({
        status: 'healthy',
        metrics,
        config: {
          maxConnectionsPerSession: 5,
          connectionTimeoutMs: 5 * 60 * 1000,
          heartbeatIntervalMs: 30000,
          staleConnectionThresholdMs: 2 * 60 * 1000,
        },
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error('[ImagesMVP] WebSocket status error:', error);
      res.status(500).json({
        status: 'error',
        message: 'Failed to retrieve WebSocket status',
        timestamp: Date.now(),
      });
    }
  });

  // HTTP endpoint to manually cleanup a session's connections
  app.post('/api/images_mvp/websocket/cleanup/:sessionId', (req: Request, res: Response) => {
    const sessionId = req.params.sessionId;
    
    try {
      wsConnectionManager.cleanupSession(sessionId);
      
      res.json({
        success: true,
        message: `Cleaned up connections for session: ${sessionId}`,
        timestamp: Date.now(),
      });
    } catch (error) {
      console.error(`[ImagesMVP] Manual cleanup failed for session ${sessionId}:`, error);
      res.status(500).json({
        success: false,
        message: 'Cleanup failed',
        timestamp: Date.now(),
      });
    }
  });
}

/**
 * Enhanced broadcast functions that use the connection manager
 */
export function broadcastProgress(
  sessionId: string,
  progress: number,
  message: string,
  stage?: string
): void {
  const normalizedProgress = Math.min(100, Math.max(0, progress));
  const progressData = {
    type: 'progress',
    sessionId,
    progress: normalizedProgress,
    percentage: normalizedProgress,
    message,
    stage: stage || 'processing',
    timestamp: Date.now(),
  };

  wsConnectionManager.broadcastToSession(sessionId, progressData);
}

export function broadcastError(sessionId: string, error: string): void {
  const errorData = {
    type: 'error',
    sessionId,
    error,
    timestamp: Date.now(),
  };

  wsConnectionManager.broadcastToSession(sessionId, errorData);
}

export function broadcastComplete(sessionId: string, metadata: any): void {
  const completeData = {
    type: 'complete',
    sessionId,
    metadata: {
      fields_extracted: metadata.fields_extracted || 0,
      processing_time_ms: metadata.processing_time_ms || 0,
      file_size: metadata.file_size || 0,
    },
    timestamp: Date.now(),
  };

  wsConnectionManager.broadcastToSession(sessionId, completeData);
}

/**
 * Cleanup function for extraction completion
 */
export function cleanupWebSocketConnections(sessionId: string): void {
  // Delay cleanup to allow final messages to be sent
  setTimeout(() => {
    wsConnectionManager.cleanupSession(sessionId);
  }, 5000);
}