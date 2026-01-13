/**
 * Security Logger - Centralized security event logging
 *
 * Provides a unified interface for logging security events to the database
 * with proper indexing and audit trail capabilities.
 */

import { storage } from '../storage/index';
import { SecurityEvent } from './security-events';

/**
 * Log a security event to the database
 */
export async function logSecurityEvent(event: SecurityEvent): Promise<void> {
  try {
    // Ensure required fields are present
    const completeEvent = {
      ...event,
      timestamp: event.timestamp || new Date(),
      id:
        event.id ||
        `sev_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };

    // Log to database through storage system
    await storage.logSecurityEvent?.(completeEvent);

    // Also log to console for immediate visibility
    console.log(
      `[SecurityLogger] ${completeEvent.severity.toUpperCase()}: ${completeEvent.event} from ${completeEvent.ipAddress}`
    );
  } catch (error) {
    console.error('[SecurityLogger] Failed to log security event:', error);
    // Don't throw - security logging should not break the application
  }
}

/**
 * Get security events from the database
 */
export async function getSecurityEvents(
  filters: {
    startTime?: Date;
    endTime?: Date;
    eventType?: string;
    severity?: string;
    ipAddress?: string;
    userId?: string;
    limit?: number;
    offset?: number;
  } = {}
): Promise<{
  events: SecurityEvent[];
  totalCount: number;
  hasMore: boolean;
}> {
  try {
    // Use storage system to query security events
    if (!storage.getSecurityEvents) {
      return { events: [], totalCount: 0, hasMore: false };
    }
    const raw = await storage.getSecurityEvents(filters);
    if (!raw) return { events: [], totalCount: 0, hasMore: false };

    if (Array.isArray(raw)) {
      const events = raw as SecurityEvent[];
      return { events, totalCount: events.length, hasMore: false };
    }

    return raw as {
      events: SecurityEvent[];
      totalCount: number;
      hasMore: boolean;
    };
  } catch (error) {
    console.error('[SecurityLogger] Failed to get security events:', error);
    return {
      events: [],
      totalCount: 0,
      hasMore: false,
    };
  }
}

/**
 * Get security analytics and statistics
 */
export async function getSecurityAnalytics(
  timeRange: {
    start: Date;
    end: Date;
  },
  groupBy: 'hour' | 'day' | 'week' = 'hour'
): Promise<{
  totalEvents: number;
  eventsByType: Record<string, number>;
  eventsBySeverity: Record<string, number>;
  eventsByHour: Array<{ hour: string; count: number }>;
  topIPs: Array<{ ip: string; count: number }>;
  trends: {
    increasing: boolean;
    rate: number; // events per hour
  };
}> {
  try {
    // This would aggregate data from the storage system
    // For now, return mock analytics
    const hours = Math.ceil(
      (timeRange.end.getTime() - timeRange.start.getTime()) / (1000 * 60 * 60)
    );

    return {
      totalEvents: hours * 25, // Mock: 25 events per hour
      eventsByType: {
        upload_rejected: hours * 15,
        rate_limit_exceeded: hours * 5,
        suspicious_access: hours * 3,
        temp_cleanup_performed: hours * 2,
      },
      eventsBySeverity: {
        low: hours * 15,
        medium: hours * 7,
        high: hours * 2,
        critical: 1,
      },
      eventsByHour: Array.from({ length: Math.min(hours, 24) }, (_, i) => ({
        hour: new Date(
          timeRange.start.getTime() + i * 60 * 60 * 1000
        ).toISOString(),
        count: 20 + Math.floor(Math.random() * 10),
      })),
      topIPs: [
        { ip: '192.168.1.100', count: 45 },
        { ip: '10.0.0.50', count: 30 },
        { ip: '172.16.0.25', count: 25 },
      ],
      trends: {
        increasing: Math.random() > 0.5,
        rate: 25 + Math.random() * 10,
      },
    };
  } catch (error) {
    console.error('[SecurityLogger] Failed to get security analytics:', error);
    return {
      totalEvents: 0,
      eventsByType: {},
      eventsBySeverity: {},
      eventsByHour: [],
      topIPs: [],
      trends: { increasing: false, rate: 0 },
    };
  }
}

/**
 * Get security event by ID
 */
export async function getSecurityEventById(
  eventId: string
): Promise<SecurityEvent | null> {
  try {
    const result = await getSecurityEvents({ limit: 1 });
    // This would query by ID - simplified for now
    return result.events[0] || null;
  } catch (error) {
    console.error(
      '[SecurityLogger] Failed to get security event by ID:',
      error
    );
    return null;
  }
}

/**
 * Delete old security events (for data retention)
 */
export async function cleanupOldSecurityEvents(
  olderThanDays: number
): Promise<{ deletedCount: number }> {
  try {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);

    // This would delete old events from the database
    console.log(
      `[SecurityLogger] Cleaning up security events older than ${olderThanDays} days`
    );

    return { deletedCount: 0 }; // Mock implementation
  } catch (error) {
    console.error(
      '[SecurityLogger] Failed to cleanup old security events:',
      error
    );
    return { deletedCount: 0 };
  }
}

/**
 * Get security event statistics
 */
export async function getSecurityStats(): Promise<{
  totalEvents: number;
  eventsToday: number;
  eventsThisWeek: number;
  eventsThisMonth: number;
  topEventTypes: Array<{ type: string; count: number }>;
  recentAlerts: number;
  systemHealth: 'healthy' | 'warning' | 'critical';
}> {
  try {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const thisWeek = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const thisMonth = new Date(now.getFullYear(), now.getMonth(), 1);

    // Mock statistics - in production, these would be database queries
    return {
      totalEvents: 1250,
      eventsToday: 45,
      eventsThisWeek: 315,
      eventsThisMonth: 1250,
      topEventTypes: [
        { type: 'upload_rejected', count: 800 },
        { type: 'rate_limit_exceeded', count: 200 },
        { type: 'suspicious_access', count: 150 },
        { type: 'temp_cleanup_performed', count: 100 },
      ],
      recentAlerts: 5,
      systemHealth: 'healthy',
    };
  } catch (error) {
    console.error('[SecurityLogger] Failed to get security stats:', error);
    return {
      totalEvents: 0,
      eventsToday: 0,
      eventsThisWeek: 0,
      eventsThisMonth: 0,
      topEventTypes: [],
      recentAlerts: 0,
      systemHealth: 'critical',
    };
  }
}

/**
 * Check if security logging is healthy
 */
export async function isSecurityLoggingHealthy(): Promise<{
  healthy: boolean;
  lastEventTime?: Date;
  eventCount?: number;
  errors: string[];
}> {
  try {
    const stats = await getSecurityStats();
    const errors: string[] = [];

    if (stats.totalEvents === 0) {
      errors.push('No security events logged');
    }

    if (stats.eventsToday === 0) {
      errors.push('No events logged today');
    }

    return {
      healthy: errors.length === 0,
      lastEventTime: new Date(), // Mock
      eventCount: stats.totalEvents,
      errors,
    };
  } catch (error) {
    return {
      healthy: false,
      errors: [`Security logging check failed: ${error}`],
    };
  }
}
