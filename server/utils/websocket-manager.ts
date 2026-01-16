import type { WebSocket } from 'ws';

interface WebSocketConnection {
  ws: WebSocket;
  sessionId: string;
  connectionId: string;
  startTime: number;
  lastActivity: number;
  heartbeatInterval?: NodeJS.Timeout;
  cleanupTimeout?: NodeJS.Timeout;
  isAlive: boolean;
}

interface ConnectionMetrics {
  totalConnections: number;
  activeConnections: number;
  staleConnections: number;
  memoryUsage: number;
}

/**
 * WebSocket Connection Manager - Prevents memory leaks and connection accumulation
 */
export class WebSocketConnectionManager {
  private connections = new Map<string, WebSocketConnection[]>();
  private connectionTimeouts = new Map<string, NodeJS.Timeout>();
  private metricsInterval?: NodeJS.Timeout;
  private cleanupInterval?: NodeJS.Timeout;
  
  // Configuration
  private readonly config = {
    maxConnectionsPerSession: 5, // Prevent connection flooding
    connectionTimeoutMs: 5 * 60 * 1000, // 5 minutes max connection lifetime
    heartbeatIntervalMs: 30000, // 30 seconds heartbeat
    staleConnectionThresholdMs: 2 * 60 * 1000, // 2 minutes without activity
    cleanupIntervalMs: 60 * 1000, // Cleanup every minute
    metricsIntervalMs: 30 * 1000, // Metrics every 30 seconds
  };

  constructor() {
    this.startPeriodicCleanup();
    this.startMetricsCollection();
  }

  /**
   * Add a new WebSocket connection with proper lifecycle management
   */
  addConnection(ws: WebSocket, sessionId: string): WebSocketConnection {
    const connectionId = `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const connection: WebSocketConnection = {
      ws,
      sessionId,
      connectionId,
      startTime: Date.now(),
      lastActivity: Date.now(),
      isAlive: true,
    };

    // Enforce connection limits per session
    this.enforceConnectionLimit(sessionId);

    // Add to session connections
    if (!this.connections.has(sessionId)) {
      this.connections.set(sessionId, []);
    }
    this.connections.get(sessionId)!.push(connection);

    // Set up connection timeout
    this.setupConnectionTimeout(connection);

    // Set up heartbeat mechanism
    this.setupHeartbeat(connection);

    // Set up event handlers
    this.setupConnectionHandlers(connection);

    console.log(`[WebSocketManager] Connection added: ${connectionId} for session: ${sessionId}`);
    this.logConnectionMetrics();

    return connection;
  }

  /**
   * Remove a connection and clean up all resources
   */
  removeConnection(connection: WebSocketConnection): void {
    const { sessionId, connectionId } = connection;
    
    // Clear timeouts
    if (connection.heartbeatInterval) {
      clearInterval(connection.heartbeatInterval);
    }
    if (connection.cleanupTimeout) {
      clearTimeout(connection.cleanupTimeout);
    }

    // Close WebSocket if still open
    if (connection.ws.readyState === 1) { // WebSocket.OPEN
      connection.ws.close(1000, 'Connection cleanup');
    }

    // Remove from session connections
    const sessionConnections = this.connections.get(sessionId);
    if (sessionConnections) {
      const index = sessionConnections.findIndex(conn => conn.connectionId === connectionId);
      if (index > -1) {
        sessionConnections.splice(index, 1);
      }
      
      // Clean up empty session
      if (sessionConnections.length === 0) {
        this.connections.delete(sessionId);
      }
    }

    console.log(`[WebSocketManager] Connection removed: ${connectionId} for session: ${sessionId}`);
    this.logConnectionMetrics();
  }

  /**
   * Remove all connections for a session
   */
  cleanupSession(sessionId: string): void {
    const connections = this.connections.get(sessionId);
    if (connections) {
      console.log(`[WebSocketManager] Cleaning up session: ${sessionId} (${connections.length} connections)`);
      
      // Create a copy of the array to avoid modification during iteration
      const connectionsToRemove = [...connections];
      connectionsToRemove.forEach(connection => {
        this.removeConnection(connection);
      });
    }
  }

  /**
   * Get all active connections for a session
   */
  getSessionConnections(sessionId: string): WebSocketConnection[] {
    return this.connections.get(sessionId) || [];
  }

  /**
   * Broadcast message to all connections in a session
   */
  broadcastToSession(sessionId: string, message: any): void {
    const connections = this.getSessionConnections(sessionId);
    const messageStr = JSON.stringify(message);
    
    connections.forEach(connection => {
      if (connection.ws.readyState === 1) { // WebSocket.OPEN
        try {
          connection.ws.send(messageStr);
          connection.lastActivity = Date.now();
        } catch (error) {
          console.error(`[WebSocketManager] Failed to send message to ${connection.connectionId}:`, error);
          this.removeConnection(connection);
        }
      }
    });
  }

  /**
   * Get connection metrics for monitoring
   */
  getMetrics(): ConnectionMetrics {
    let totalConnections = 0;
    let activeConnections = 0;
    let staleConnections = 0;
    
    const now = Date.now();
    
    this.connections.forEach(sessionConnections => {
      totalConnections += sessionConnections.length;
      
      sessionConnections.forEach(connection => {
        if (connection.isAlive) {
          activeConnections++;
        }
        
        if (now - connection.lastActivity > this.config.staleConnectionThresholdMs) {
          staleConnections++;
        }
      });
    });

    // Rough memory estimation (each connection ~50KB + message buffers)
    const memoryUsage = totalConnections * 50 * 1024;

    return {
      totalConnections,
      activeConnections,
      staleConnections,
      memoryUsage,
    };
  }

  /**
   * Clean up stale and expired connections
   */
  private cleanupStaleConnections(): void {
    const now = Date.now();
    const connectionsToRemove: WebSocketConnection[] = [];

    this.connections.forEach(sessionConnections => {
      sessionConnections.forEach(connection => {
        const age = now - connection.startTime;
        const idleTime = now - connection.lastActivity;

        // Remove connections that are too old or have been idle too long
        if (age > this.config.connectionTimeoutMs || 
            idleTime > this.config.staleConnectionThresholdMs || 
            !connection.isAlive) {
          connectionsToRemove.push(connection);
        }
      });
    });

    if (connectionsToRemove.length > 0) {
      console.log(`[WebSocketManager] Cleaning up ${connectionsToRemove.length} stale connections`);
      connectionsToRemove.forEach(connection => this.removeConnection(connection));
    }
  }

  /**
   * Enforce maximum connections per session
   */
  private enforceConnectionLimit(sessionId: string): void {
    const connections = this.connections.get(sessionId) || [];
    
    if (connections.length >= this.config.maxConnectionsPerSession) {
      // Remove oldest connection
      const oldestConnection = connections.reduce((oldest, current) => 
        current.startTime < oldest.startTime ? current : oldest
      );
      
      console.log(`[WebSocketManager] Enforcing connection limit for session ${sessionId}`);
      this.removeConnection(oldestConnection);
    }
  }

  /**
   * Set up connection timeout
   */
  private setupConnectionTimeout(connection: WebSocketConnection): void {
    connection.cleanupTimeout = setTimeout(() => {
      console.log(`[WebSocketManager] Connection timeout: ${connection.connectionId}`);
      this.removeConnection(connection);
    }, this.config.connectionTimeoutMs);
  }

  /**
   * Set up heartbeat mechanism
   */
  private setupHeartbeat(connection: WebSocketConnection): void {
    connection.heartbeatInterval = setInterval(() => {
      if (connection.ws.readyState === 1) { // WebSocket.OPEN
        try {
          connection.ws.ping();
          connection.isAlive = false; // Will be set to true on pong
          
          // Check if connection responded to previous ping
          setTimeout(() => {
            if (!connection.isAlive) {
              console.log(`[WebSocketManager] Heartbeat failed for: ${connection.connectionId}`);
              this.removeConnection(connection);
            }
          }, 5000);
        } catch (error) {
          console.error(`[WebSocketManager] Heartbeat error for ${connection.connectionId}:`, error);
          this.removeConnection(connection);
        }
      } else {
        this.removeConnection(connection);
      }
    }, this.config.heartbeatIntervalMs);

    // Handle pong responses
    connection.ws.on('pong', () => {
      connection.isAlive = true;
      connection.lastActivity = Date.now();
    });
  }

  /**
   * Set up WebSocket event handlers
   */
  private setupConnectionHandlers(connection: WebSocketConnection): void {
    const { ws, sessionId, connectionId } = connection;

    ws.on('message', (data) => {
      connection.lastActivity = Date.now();
      
      try {
        const message = JSON.parse(data.toString());
        
        if (message.type === 'ping') {
          ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
        }
      } catch (error) {
        console.error(`[WebSocketManager] Message parsing error for ${connectionId}:`, error);
      }
    });

    ws.on('close', () => {
      console.log(`[WebSocketManager] Connection closed: ${connectionId}`);
      this.removeConnection(connection);
    });

    ws.on('error', (error) => {
      console.error(`[WebSocketManager] Connection error for ${connectionId}:`, error);
      this.removeConnection(connection);
    });
  }

  /**
   * Start periodic cleanup of stale connections
   */
  private startPeriodicCleanup(): void {
    this.cleanupInterval = setInterval(() => {
      this.cleanupStaleConnections();
    }, this.config.cleanupIntervalMs);
  }

  /**
   * Start metrics collection and logging
   */
  private startMetricsCollection(): void {
    this.metricsInterval = setInterval(() => {
      this.logConnectionMetrics();
    }, this.config.metricsIntervalMs);
  }

  /**
   * Log connection metrics for monitoring
   */
  private logConnectionMetrics(): void {
    const metrics = this.getMetrics();
    
    console.log('[WebSocketManager] Metrics:', {
      totalConnections: metrics.totalConnections,
      activeConnections: metrics.activeConnections,
      staleConnections: metrics.staleConnections,
      memoryUsageMB: Math.round(metrics.memoryUsage / 1024 / 1024),
      sessions: this.connections.size,
    });

    // Alert if metrics are concerning
    if (metrics.staleConnections > metrics.totalConnections * 0.1) {
      console.warn(`[WebSocketManager] Warning: ${metrics.staleConnections} stale connections detected`);
    }

    if (metrics.totalConnections > 100) {
      console.warn(`[WebSocketManager] Warning: High connection count: ${metrics.totalConnections}`);
    }
  }

  /**
   * Clean shutdown of the connection manager
   */
  shutdown(): void {
    console.log('[WebSocketManager] Shutting down...');
    
    // Clear intervals
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    if (this.metricsInterval) {
      clearInterval(this.metricsInterval);
    }

    // Clean up all connections
    this.connections.forEach((_, sessionId) => {
      this.cleanupSession(sessionId);
    });

    console.log('[WebSocketManager] Shutdown complete');
  }
}

// Singleton instance
export const wsConnectionManager = new WebSocketConnectionManager();

// Graceful shutdown handling
process.on('SIGTERM', () => {
  wsConnectionManager.shutdown();
});

process.on('SIGINT', () => {
  wsConnectionManager.shutdown();
});