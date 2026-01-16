/**
 * Enhanced WebSocket manager for client-side connection management
 * Prevents memory leaks and provides robust reconnection logic
 */

export interface WebSocketConfig {
  maxReconnectAttempts: number;
  reconnectDelayMs: number;
  reconnectBackoffMultiplier: number;
  connectionTimeoutMs: number;
  heartbeatIntervalMs: number;
  maxConnectionLifetimeMs: number;
}

export interface WebSocketMessage {
  type: 'connected' | 'progress' | 'complete' | 'error' | 'heartbeat' | 'pong';
  sessionId: string;
  timestamp: number;
  [key: string]: any;
}

export interface ConnectionMetrics {
  connectionId: string;
  connectedAt: number;
  lastMessageAt: number;
  messagesReceived: number;
  reconnectAttempts: number;
  isHealthy: boolean;
}

class WebSocketManager {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private connectionMetrics: ConnectionMetrics;
  private reconnectAttempts = 0;
  private heartbeatInterval: number | null = null;
  private connectionTimeout: number | null = null;
  private connectionStartTime: number = 0;
  private messageHandlers: Map<string, (message: WebSocketMessage) => void> =
    new Map();
  private connectionHandlers: Map<string, () => void> = new Map();
  private disconnectionHandlers: Map<string, () => void> = new Map();
  private errorHandlers: Map<string, (error: Event) => void> = new Map();

  constructor(config: Partial<WebSocketConfig> = {}) {
    this.config = {
      maxReconnectAttempts: 5,
      reconnectDelayMs: 1000,
      reconnectBackoffMultiplier: 2,
      connectionTimeoutMs: 10000,
      heartbeatIntervalMs: 30000,
      maxConnectionLifetimeMs: 5 * 60 * 1000, // 5 minutes
      ...config,
    };

    this.connectionMetrics = {
      connectionId: '',
      connectedAt: 0,
      lastMessageAt: 0,
      messagesReceived: 0,
      reconnectAttempts: 0,
      isHealthy: false,
    };
  }

  /**
   * Connect to WebSocket server with enhanced error handling
   */
  connect(url: string, sessionId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Close existing connection if any
        this.disconnect();

        console.log(`[WebSocketManager] Connecting to: ${url}`);

        this.ws = new WebSocket(url);
        this.connectionStartTime = Date.now();
        this.connectionMetrics.connectedAt = this.connectionStartTime;
        this.connectionMetrics.connectionId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Set connection timeout
        this.connectionTimeout = window.setTimeout(() => {
          if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            this.ws.close();
            reject(new Error('Connection timeout'));
          }
        }, this.config.connectionTimeoutMs);

        this.setupEventHandlers(resolve, reject, url, sessionId);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Disconnect and clean up all resources
   */
  disconnect(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.connectionTimeout) {
      clearTimeout(this.connectionTimeout);
      this.connectionTimeout = null;
    }

    if (this.ws) {
      // Remove event handlers to prevent memory leaks
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onclose = null;
      this.ws.onerror = null;

      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.close(1000, 'Client disconnect');
      }

      this.ws = null;
    }

    this.connectionMetrics.isHealthy = false;
    console.log('[WebSocketManager] Disconnected and cleaned up');
  }

  /**
   * Send message to server
   */
  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error('[WebSocketManager] Failed to send message:', error);
        this.handleError(error as Event);
      }
    } else {
      console.warn(
        '[WebSocketManager] Cannot send message - WebSocket not connected'
      );
    }
  }

  /**
   * Add message handler
   */
  onMessage(handler: (message: WebSocketMessage) => void): string {
    const id = `handler_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.messageHandlers.set(id, handler);
    return id;
  }

  /**
   * Add connection handler
   */
  onConnect(handler: () => void): string {
    const id = `connect_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.connectionHandlers.set(id, handler);
    return id;
  }

  /**
   * Add disconnection handler
   */
  onDisconnect(handler: () => void): string {
    const id = `disconnect_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.disconnectionHandlers.set(id, handler);
    return id;
  }

  /**
   * Add error handler
   */
  onError(handler: (error: Event) => void): string {
    const id = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.errorHandlers.set(id, handler);
    return id;
  }

  /**
   * Remove handler
   */
  removeHandler(id: string): void {
    this.messageHandlers.delete(id);
    this.connectionHandlers.delete(id);
    this.disconnectionHandlers.delete(id);
    this.errorHandlers.delete(id);
  }

  /**
   * Get connection metrics
   */
  getMetrics(): ConnectionMetrics {
    return { ...this.connectionMetrics };
  }

  /**
   * Check if connection is healthy
   */
  isHealthy(): boolean {
    if (!this.ws) return false;

    const now = Date.now();
    const connectionAge = now - this.connectionStartTime;
    const timeSinceLastMessage = now - this.connectionMetrics.lastMessageAt;

    return (
      this.ws.readyState === WebSocket.OPEN &&
      connectionAge < this.config.maxConnectionLifetimeMs &&
      timeSinceLastMessage < this.config.heartbeatIntervalMs * 2 &&
      this.connectionMetrics.isHealthy
    );
  }

  /**
   * Set up WebSocket event handlers
   */
  private setupEventHandlers(
    resolve: () => void,
    reject: (error: Error) => void,
    url: string,
    sessionId: string
  ): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('[WebSocketManager] Connected successfully');

      if (this.connectionTimeout) {
        clearTimeout(this.connectionTimeout);
        this.connectionTimeout = null;
      }

      this.connectionMetrics.isHealthy = true;
      this.connectionMetrics.lastMessageAt = Date.now();
      this.reconnectAttempts = 0;

      // Start heartbeat
      this.startHeartbeat();

      // Notify connection handlers
      this.connectionHandlers.forEach(handler => {
        try {
          handler();
        } catch (error) {
          console.error(
            '[WebSocketManager] Error in connection handler:',
            error
          );
        }
      });

      resolve();
    };

    this.ws.onmessage = event => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.connectionMetrics.messagesReceived++;
        this.connectionMetrics.lastMessageAt = Date.now();

        // Handle heartbeat responses
        if (message.type === 'pong') {
          this.connectionMetrics.isHealthy = true;
          return;
        }

        // Handle connection confirmation
        if (message.type === 'connected') {
          this.connectionMetrics.connectionId =
            message.connectionId || this.connectionMetrics.connectionId;
        }

        // Notify message handlers
        this.messageHandlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            console.error(
              '[WebSocketManager] Error in message handler:',
              error
            );
          }
        });
      } catch (error) {
        console.error('[WebSocketManager] Error parsing message:', error);
      }
    };

    this.ws.onclose = event => {
      console.log(
        `[WebSocketManager] Connection closed: ${event.code} - ${event.reason}`
      );

      this.connectionMetrics.isHealthy = false;
      this.cleanup();

      // Notify disconnection handlers
      this.disconnectionHandlers.forEach(handler => {
        try {
          handler();
        } catch (error) {
          console.error(
            '[WebSocketManager] Error in disconnection handler:',
            error
          );
        }
      });

      // Attempt reconnection if appropriate
      if (event.code !== 1000 && event.code !== 1001) {
        this.attemptReconnection(url, sessionId);
      }
    };

    this.ws.onerror = error => {
      console.error('[WebSocketManager] Connection error:', error);
      this.handleError(error);
      reject(new Error('WebSocket connection failed'));
    };
  }

  /**
   * Start heartbeat mechanism
   */
  private startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        try {
          this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
        } catch (error) {
          console.error('[WebSocketManager] Heartbeat failed:', error);
          this.connectionMetrics.isHealthy = false;
        }
      }
    }, this.config.heartbeatIntervalMs);
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private async attemptReconnection(
    url: string,
    sessionId: string
  ): Promise<void> {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.log('[WebSocketManager] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    this.connectionMetrics.reconnectAttempts = this.reconnectAttempts;

    const delay =
      this.config.reconnectDelayMs *
      Math.pow(
        this.config.reconnectBackoffMultiplier,
        this.reconnectAttempts - 1
      );

    console.log(
      `[WebSocketManager] Attempting reconnection ${this.reconnectAttempts}/${this.config.maxReconnectAttempts} in ${delay}ms`
    );

    await new Promise(resolve => setTimeout(resolve, delay));

    try {
      await this.connect(url, sessionId);
      console.log('[WebSocketManager] Reconnection successful');
    } catch (error) {
      console.error('[WebSocketManager] Reconnection failed:', error);
      // Continue attempting until max attempts reached
      this.attemptReconnection(url, sessionId);
    }
  }

  /**
   * Handle connection errors
   */
  private handleError(error: Event): void {
    this.connectionMetrics.isHealthy = false;

    // Notify error handlers
    this.errorHandlers.forEach(handler => {
      try {
        handler(error);
      } catch (handlerError) {
        console.error(
          '[WebSocketManager] Error in error handler:',
          handlerError
        );
      }
    });
  }

  /**
   * Clean up resources
   */
  private cleanup(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.connectionTimeout) {
      clearTimeout(this.connectionTimeout);
      this.connectionTimeout = null;
    }
  }
}

// Singleton instance
export const websocketManager = new WebSocketManager();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  websocketManager.disconnect();
});

// Export for use in components
export default websocketManager;
