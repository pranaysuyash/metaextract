import { test, expect, describe, beforeEach, afterEach } from '@playwright/test';
import { WebSocket } from 'ws';
import { wsConnectionManager } from '../server/utils/websocket-manager';

/**
 * WebSocket Memory Leak Tests
 * 
 * These tests verify that:
 * 1. Connections are properly cleaned up after disconnection
 * 2. No stale connections accumulate over time
 * 3. Memory usage remains stable with many connections
 * 4. Connection limits are enforced
 * 5. Timeouts work correctly
 */

describe('WebSocket Memory Leak Prevention', () => {
  const TEST_SESSION_ID = 'test_session_memory_leak';
  const WS_URL = 'ws://localhost:3000/api/images_mvp/progress/';
  
  beforeEach(() => {
    // Clean up any existing connections
    wsConnectionManager.cleanupSession(TEST_SESSION_ID);
  });

  afterEach(() => {
    // Ensure cleanup after each test
    wsConnectionManager.cleanupSession(TEST_SESSION_ID);
  });

  test('connections are properly cleaned up on disconnection', async () => {
    const initialMetrics = wsConnectionManager.getMetrics();
    
    // Create a WebSocket connection
    const ws = new WebSocket(`${WS_URL}${TEST_SESSION_ID}`);
    
    await new Promise<void>((resolve) => {
      ws.on('open', () => {
        console.log('Test WebSocket connected');
        resolve();
      });
    });

    // Wait a bit for connection to be registered
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const afterConnectionMetrics = wsConnectionManager.getMetrics();
    expect(afterConnectionMetrics.totalConnections).toBeGreaterThan(initialMetrics.totalConnections);

    // Close the connection
    ws.close();
    
    // Wait for cleanup
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const afterCleanupMetrics = wsConnectionManager.getMetrics();
    expect(afterCleanupMetrics.totalConnections).toBe(initialMetrics.totalConnections);
  });

  test('connection limits are enforced per session', async () => {
    const connections: WebSocket[] = [];
    
    // Try to create more connections than the limit (5)
    for (let i = 0; i < 7; i++) {
      const ws = new WebSocket(`${WS_URL}${TEST_SESSION_ID}`);
      connections.push(ws);
      
      await new Promise<void>((resolve, reject) => {
        ws.on('open', resolve);
        ws.on('error', reject);
      });
    }

    // Wait for connection limit enforcement
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const metrics = wsConnectionManager.getMetrics();
    const sessionConnections = wsConnectionManager.getSessionConnections(TEST_SESSION_ID);
    
    // Should not exceed the limit (5 connections per session)
    expect(sessionConnections.length).toBeLessThanOrEqual(5);
    
    // Clean up
    connections.forEach(ws => {
      try {
        ws.close();
      } catch (e) {
        // Ignore errors during cleanup
      }
    });
  });

  test('stale connections are automatically cleaned up', async () => {
    // Create a connection
    const ws = new WebSocket(`${WS_URL}${TEST_SESSION_ID}`);
    
    await new Promise<void>((resolve) => {
      ws.on('open', resolve);
    });

    // Wait for connection to be established
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Simulate stale connection by not sending any messages
    // The connection manager should detect this as stale after 2 minutes
    // For testing, we'll manually trigger cleanup
    const metricsBefore = wsConnectionManager.getMetrics();
    expect(metricsBefore.totalConnections).toBeGreaterThan(0);

    // Manually trigger stale connection cleanup
    wsConnectionManager['cleanupStaleConnections']();
    
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Since our connection is still active (WebSocket.OPEN), it shouldn't be cleaned up
    const metricsAfter = wsConnectionManager.getMetrics();
    expect(metricsAfter.totalConnections).toBe(metricsBefore.totalConnections);

    // Close the connection to make it stale
    ws.close();
    
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Now cleanup should remove it
    wsConnectionManager['cleanupStaleConnections']();
    
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const finalMetrics = wsConnectionManager.getMetrics();
    expect(finalMetrics.totalConnections).toBe(0);
  });

  test('heartbeat mechanism keeps connections alive', async () => {
    const ws = new WebSocket(`${WS_URL}${TEST_SESSION_ID}`);
    let heartbeatReceived = false;
    
    await new Promise<void>((resolve) => {
      ws.on('open', resolve);
    });

    ws.on('message', (data) => {
      const message = JSON.parse(data.toString());
      if (message.type === 'heartbeat') {
        heartbeatReceived = true;
      }
    });

    // Wait for heartbeat (should be sent every 30 seconds, but we'll wait less for testing)
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    expect(heartbeatReceived).toBe(true);
    
    ws.close();
  });

  test('multiple sessions do not interfere with each other', async () => {
    const sessionIds = ['session_1', 'session_2', 'session_3'];
    const connections: WebSocket[] = [];

    // Create connections for different sessions
    for (const sessionId of sessionIds) {
      const ws = new WebSocket(`${WS_URL}${sessionId}`);
      connections.push(ws);
      
      await new Promise<void>((resolve) => {
        ws.on('open', resolve);
      });
    }

    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Verify all sessions have connections
    for (const sessionId of sessionIds) {
      const sessionConnections = wsConnectionManager.getSessionConnections(sessionId);
      expect(sessionConnections.length).toBeGreaterThan(0);
    }

    // Clean up one session
    wsConnectionManager.cleanupSession('session_1');
    
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Verify session 1 is cleaned up but others remain
    const session1Connections = wsConnectionManager.getSessionConnections('session_1');
    expect(session1Connections.length).toBe(0);
    
    const session2Connections = wsConnectionManager.getSessionConnections('session_2');
    expect(session2Connections.length).toBeGreaterThan(0);

    // Clean up remaining connections
    connections.forEach(ws => {
      try {
        ws.close();
      } catch (e) {
        // Ignore errors during cleanup
      }
    });
  });

  test('memory usage remains stable with many connections', async () => {
    const initialMemory = process.memoryUsage();
    const connections: WebSocket[] = [];
    
    // Create many connections
    for (let i = 0; i < 20; i++) {
      const ws = new WebSocket(`${WS_URL}${TEST_SESSION_ID}_${i}`);
      connections.push(ws);
      
      await new Promise<void>((resolve, reject) => {
        ws.on('open', resolve);
        ws.on('error', () => resolve()); // Continue even if some fail
      });
    }

    await new Promise(resolve => setTimeout(resolve, 200));
    
    const duringConnectionsMemory = process.memoryUsage();
    
    // Clean up all connections
    connections.forEach(ws => {
      try {
        ws.close();
      } catch (e) {
        // Ignore errors during cleanup
      }
    });

    // Wait for cleanup
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const afterCleanupMemory = process.memoryUsage();
    
    // Memory usage should not increase dramatically
    const memoryIncrease = duringConnectionsMemory.heapUsed - initialMemory.heapUsed;
    const memoryDecrease = duringConnectionsMemory.heapUsed - afterCleanupMemory.heapUsed;
    
    console.log(`Memory increase during connections: ${Math.round(memoryIncrease / 1024 / 1024)}MB`);
    console.log(`Memory decrease after cleanup: ${Math.round(memoryDecrease / 1024 / 1024)}MB`);
    
    // Memory should be mostly cleaned up (allowing for some overhead)
    expect(memoryDecrease).toBeGreaterThan(memoryIncrease * 0.8); // At least 80% cleanup
  });
});

describe('WebSocket Integration Tests', () => {
  test('progress updates are broadcast correctly', async () => {
    const sessionId = 'test_progress_session';
    const connections: WebSocket[] = [];
    const receivedMessages: any[] = [];
    
    // Create multiple connections to the same session
    for (let i = 0; i < 3; i++) {
      const ws = new WebSocket(`ws://localhost:3000/api/images_mvp/progress/${sessionId}`);
      connections.push(ws);
      
      ws.on('message', (data) => {
        const message = JSON.parse(data.toString());
        receivedMessages.push({ connectionIndex: i, message });
      });
      
      await new Promise<void>((resolve) => {
        ws.on('open', resolve);
      });
    }

    // Wait for connections to be established
    await new Promise(resolve => setTimeout(resolve, 100));

    // Broadcast a progress update
    const { broadcastProgress } = await import('../server/routes/images-mvp-websocket');
    broadcastProgress(sessionId, 50, 'Test progress', 'testing');

    // Wait for messages to be received
    await new Promise(resolve => setTimeout(resolve, 100));

    // Verify all connections received the message
    const progressMessages = receivedMessages.filter(m => m.message.type === 'progress');
    expect(progressMessages.length).toBe(3);
    
    // Verify message content
    progressMessages.forEach(({ message }) => {
      expect(message.type).toBe('progress');
      expect(message.sessionId).toBe(sessionId);
      expect(message.progress).toBe(50);
      expect(message.message).toBe('Test progress');
    });

    // Clean up
    connections.forEach(ws => {
      try {
        ws.close();
      } catch (e) {
        // Ignore errors during cleanup
      }
    });
  });
});

// Performance monitoring test
describe('WebSocket Performance Monitoring', () => {
  test('connection metrics are tracked accurately', async () => {
    const initialMetrics = wsConnectionManager.getMetrics();
    
    // Create a connection
    const ws = new WebSocket(`ws://localhost:3000/api/images_mvp/progress/test_metrics_session`);
    
    await new Promise<void>((resolve) => {
      ws.on('open', resolve);
    });

    await new Promise(resolve => setTimeout(resolve, 100));
    
    const duringConnectionMetrics = wsConnectionManager.getMetrics();
    
    expect(duringConnectionMetrics.totalConnections).toBe(initialMetrics.totalConnections + 1);
    expect(duringConnectionMetrics.activeConnections).toBeGreaterThan(0);
    expect(duringConnectionMetrics.memoryUsage).toBeGreaterThan(0);

    // Close connection
    ws.close();
    
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const finalMetrics = wsConnectionManager.getMetrics();
    expect(finalMetrics.totalConnections).toBe(initialMetrics.totalConnections);
  });
});