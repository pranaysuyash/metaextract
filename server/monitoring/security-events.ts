/**
 * Security Event Logging and Analysis
 *
 * Comprehensive security event tracking for:
 * - Failed uploads and rejections
 * - Rate limit violations
 * - Suspicious access patterns
 * - Authentication events
 * - File type blocking
 */

import { storage } from '../storage/index';
import { getRateLimitKey } from '../middleware/upload-rate-limit';
import { Request } from 'express';

// Security Event Types
export type SecurityEventType =
  | 'upload_rejected' // File rejected by fileFilter
  | 'rate_limit_exceeded' // Rate limit violation
  | 'burst_limit_exceeded' // Burst rate limit violation
  | 'invalid_file_type' // Unsupported file type attempt
  | 'suspicious_access' // Unusual access pattern
  | 'authentication_failure' // Failed authentication
  | 'authorization_failure' // Failed authorization
  | 'temp_cleanup_performed' // Temp file cleanup executed
  | 'security_alert_sent' // Security alert triggered
  | 'health_check_failure' // Health check failed
  | 'monitoring_failure' // Monitoring system error
  | 'large_file_upload' // File exceeds size threshold
  | 'multiple_sessions_ip' // Multiple sessions from same IP
  | 'cookie_reset_detected' // Session cookie reset detected
  | 'geographic_anomaly' // Unusual geographic access
  | 'timing_anomaly' // Unusual timing pattern
  | 'user_agent_anomaly' // Suspicious user agent
  | 'ip_reputation_flag' // IP flagged by reputation service
  | 'invalid_fingerprint' // Invalid fingerprint submission
  | 'protection_error'
  | 'protection_decision'
  | 'challenge_failed'
  | 'fingerprint_analysis'
  | 'fingerprint_submitted'
  | 'fingerprint_error'
  | 'protection_feedback'
  | 'anomaly_detection'
  | 'ml_anomaly_detection' // ML anomaly detection result
  | 'enhanced_protection_critical_error' // Enhanced protection critical error
  | 'enhanced_protection_decision' // Enhanced protection decision made
  | 'enhanced_challenge_passed' // Enhanced challenge verification passed
  | 'enhanced_challenge_failed' // Enhanced challenge verification failed
  | 'threat_intelligence_detection' // Threat intelligence check result
  | 'security_threat' // Security threat detected
  | 'malicious_ip_reported' // Malicious IP reported to threat feed
  | 'behavioral_analysis_received' // Behavioral analysis data received
  | 'threat_intelligence_lookup' // Threat intelligence lookup performed
  | 'threat_report_submitted' // Threat report submitted
  | 'security_incident' // Security incident recorded
  | string;

export interface SecurityEvent {
  id?: string;
  event: SecurityEventType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  source: string;
  userId?: string;
  sessionId?: string;
  ipAddress?: string;
  customerId?: string;
  userAgent?: string;
  message?: string;
  details: Record<string, any>;
  metadata?: {
    country?: string;
    city?: string;
    timezone?: string;
    deviceType?: string;
    browser?: string;
    os?: string;
  };
}

// Security Analysis Configuration
const SECURITY_THRESHOLDS = {
  // Upload rejection thresholds
  UPLOAD_REJECTIONS_PER_MINUTE: 50,
  UPLOAD_REJECTIONS_PER_IP_PER_HOUR: 20,

  // Rate limiting thresholds
  RATE_LIMIT_VIOLATIONS_PER_MINUTE: 30,
  RATE_LIMIT_VIOLATIONS_PER_IP_PER_HOUR: 10,

  // Suspicious behavior thresholds
  FAILED_ATTEMPTS_PER_IP_PER_HOUR: 50,
  COOKIE_RESETS_PER_IP_PER_HOUR: 30,
  MULTIPLE_SESSIONS_PER_IP: 15,

  // Geographic thresholds
  COUNTRIES_PER_IP_PER_DAY: 5,
  IMPOSSIBLE_TRAVEL_TIME_MINUTES: 30,

  // File analysis thresholds
  LARGE_FILE_SIZE_MB: 50,
  SUSPICIOUS_EXTENSIONS: ['.exe', '.scr', '.vbs', '.js', '.bat'],
};

/**
 * Security Event Logger
 */
export class SecurityEventLogger {
  private eventBuffer: SecurityEvent[] = [];
  private readonly BUFFER_SIZE = 1000;
  private readonly FLUSH_INTERVAL = 30 * 1000; // 30 seconds

  private flushTimer: NodeJS.Timeout | null = null;

  constructor() {
    // Start periodic buffer flush (skip in test environment to avoid
    // background timers interfering with Jest global teardown and flakiness)
    if (process.env.NODE_ENV !== 'test') {
      this.startPeriodicFlush();
    }
  }

  /**
   * Log a security event
   */
  async logEvent(event: SecurityEvent): Promise<void> {
    try {
      // Add timestamp if not provided
      if (!event.timestamp) {
        event.timestamp = new Date();
      }

      // Generate ID if not provided
      if (!event.id) {
        event.id = `sev_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      }

      // Add to buffer for batch processing
      this.eventBuffer.push(event);

      // Log immediately for debugging
      console.log(
        `[SecurityEvent] ${event.severity.toUpperCase()}: ${event.event} - ${event.message || event.details.message || 'No message'}`
      );

      // Flush buffer if it's getting large
      if (this.eventBuffer.length >= this.BUFFER_SIZE) {
        await this.flushBuffer();
      }
    } catch (error: unknown) {
      console.error('[SecurityEvent] Failed to log security event:', error);
    }
  }

  /**
   * Log file upload rejection
   */
  async logUploadRejection(
    req: Request,
    reason: string,
    fileDetails: {
      filename: string;
      mimetype: string;
      size: number;
      extension: string;
    }
  ): Promise<void> {
    const event: SecurityEvent = {
      event: 'upload_rejected',
      severity: this.getRejectionSeverity(reason),
      timestamp: new Date(),
      source: 'fileFilter',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userAgent: req.headers['user-agent'],
      details: {
        reason,
        filename: fileDetails.filename,
        mimetype: fileDetails.mimetype,
        size: fileDetails.size,
        extension: fileDetails.extension,
        userId: (req as any).user?.id,
        sessionId: getRateLimitKey(req).replace(/^[^:]+:/, ''),
      },
    };

    await this.logEvent(event);
  }

  /**
   * Log rate limit violation
   */
  async logRateLimitViolation(
    req: Request,
    limitType: 'rate' | 'burst',
    limit: number,
    window: string
  ): Promise<void> {
    const event: SecurityEvent = {
      event:
        limitType === 'burst' ? 'burst_limit_exceeded' : 'rate_limit_exceeded',
      severity: 'medium',
      timestamp: new Date(),
      source: 'rate_limiter',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userAgent: req.headers['user-agent'],
      details: {
        limitType,
        limit,
        window,
        userId: (req as any).user?.id,
        sessionId: getRateLimitKey(req).replace(/^[^:]+:/, ''),
      },
    };

    await this.logEvent(event);
  }

  /**
   * Log suspicious access pattern
   */
  async logSuspiciousAccess(
    req: Request,
    reason: string,
    confidence: 'low' | 'medium' | 'high'
  ): Promise<void> {
    const event: SecurityEvent = {
      event: 'suspicious_access',
      severity:
        confidence === 'high'
          ? 'high'
          : confidence === 'medium'
            ? 'medium'
            : 'low',
      timestamp: new Date(),
      source: 'pattern_detection',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userAgent: req.headers['user-agent'],
      details: {
        reason,
        confidence,
        userId: (req as any).user?.id,
        sessionId: getRateLimitKey(req).replace(/^[^:]+:/, ''),
        headers: this.sanitizeHeaders(req.headers),
      },
    };

    await this.logEvent(event);
  }

  /**
   * Log authentication failure
   */
  async logAuthenticationFailure(
    req: Request,
    reason: string,
    username?: string
  ): Promise<void> {
    const event: SecurityEvent = {
      event: 'authentication_failure',
      severity: 'medium',
      timestamp: new Date(),
      source: 'authentication',
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userAgent: req.headers['user-agent'],
      details: {
        reason,
        username,
        headers: this.sanitizeHeaders(req.headers),
      },
    };

    await this.logEvent(event);
  }

  /**
   * Log temp cleanup event
   */
  async logTempCleanup(
    filesRemoved: number,
    spaceFreed: number
  ): Promise<void> {
    const event: SecurityEvent = {
      event: 'temp_cleanup_performed',
      severity: filesRemoved > 100 ? 'medium' : 'low',
      timestamp: new Date(),
      source: 'cleanup_system',
      ipAddress: 'system',
      details: {
        filesRemoved,
        spaceFreed,
        cleanupType: filesRemoved > 0 ? 'automatic' : 'routine',
      },
    };

    await this.logEvent(event);
  }

  /**
   * Get rejection severity based on reason
   */
  private getRejectionSeverity(reason: string): 'low' | 'medium' | 'high' {
    const lowerReason = reason.toLowerCase();

    if (lowerReason.includes('executable') || lowerReason.includes('script')) {
      return 'high';
    }
    if (
      lowerReason.includes('unsupported') ||
      lowerReason.includes('invalid')
    ) {
      return 'medium';
    }
    return 'low';
  }

  /**
   * Sanitize headers for logging
   */
  private sanitizeHeaders(headers: any): Record<string, string> {
    const sanitized: Record<string, string> = {};

    // Only log safe headers
    const safeHeaders = [
      'user-agent',
      'accept',
      'accept-encoding',
      'accept-language',
      'content-type',
      'content-length',
      'x-forwarded-for',
      'x-real-ip',
    ];

    for (const header of safeHeaders) {
      if (headers[header]) {
        sanitized[header] = headers[header];
      }
    }

    return sanitized;
  }

  /**
   * Start periodic buffer flush
   */
  private startPeriodicFlush(): void {
    // Store timer so it can be cleared in tests or on shutdown
    this.flushTimer = setInterval(async () => {
      if (this.eventBuffer.length > 0) {
        await this.flushBuffer();
      }
    }, this.FLUSH_INTERVAL);
  }

  /**
   * Stop periodic buffer flush
   */
  public stopPeriodicFlush(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
      console.log('[SecurityEvent] Periodic flush stopped');
    }
  }

  /**
   * Flush event buffer to database
   */
  private async flushBuffer(): Promise<void> {
    if (this.eventBuffer.length === 0) return;

    const eventsToFlush = [...this.eventBuffer];
    this.eventBuffer = []; // Clear buffer

    try {
      // Batch insert events into database
      await this.batchInsertEvents(eventsToFlush);

      console.log(
        `[SecurityEvent] Flushed ${eventsToFlush.length} events to database`
      );
    } catch (error: unknown) {
      console.error('[SecurityEvent] Failed to flush event buffer:', error);
      // Put events back in buffer for retry
      this.eventBuffer.unshift(...eventsToFlush);
    }
  }

  /**
   * Batch insert events into database
   */
  private async batchInsertEvents(events: SecurityEvent[]): Promise<void> {
    try {
      // In a real implementation, this would batch insert into database
      // For now, we'll log and store individually
      for (const event of events) {
        await storage.logSecurityEvent?.(event);
      }
    } catch (error: unknown) {
      console.error('[SecurityEvent] Failed to batch insert events:', error);
      throw error instanceof Error ? error : new Error(String(error));
    }
  }

  /**
   * Get security analytics for a time period
   */
  async getSecurityAnalytics(
    startTime: Date,
    endTime: Date,
    eventTypes?: SecurityEventType[]
  ): Promise<{
    totalEvents: number;
    eventsByType: Record<string, number>;
    eventsBySeverity: Record<string, number>;
    topIPs: Array<{ ip: string; count: number }>;
    hourlyBreakdown: Array<{ hour: string; count: number }>;
  }> {
    try {
      // This would query the database for analytics
      // For now, return mock data
      return {
        totalEvents: 150,
        eventsByType: {
          upload_rejected: 80,
          rate_limit_exceeded: 30,
          suspicious_access: 20,
          temp_cleanup_performed: 20,
        },
        eventsBySeverity: {
          low: 100,
          medium: 30,
          high: 15,
          critical: 5,
        },
        topIPs: [
          { ip: '192.168.1.100', count: 45 },
          { ip: '10.0.0.50', count: 30 },
          { ip: '172.16.0.25', count: 25 },
        ],
        hourlyBreakdown: [
          { hour: '2026-01-12T10:00:00Z', count: 25 },
          { hour: '2026-01-12T11:00:00Z', count: 30 },
          { hour: '2026-01-12T12:00:00Z', count: 20 },
        ],
      };
    } catch (error: unknown) {
      console.error('[SecurityEvent] Failed to get security analytics:', error);
      throw error instanceof Error ? error : new Error(String(error));
    }
  }

  /**
   * Detect abuse patterns from security events
   */
  async detectAbusePatterns(hoursBack = 24): Promise<{
    patterns: Array<{
      type: string;
      confidence: 'low' | 'medium' | 'high';
      description: string;
      affectedIPs: string[];
      recommendation: string;
    }>;
    riskScore: number; // 0-100
  }> {
    try {
      // This would analyze recent events for patterns
      // For now, return mock detection results

      const patterns = [
        {
          type: 'upload_flooding',
          confidence: 'medium' as const,
          description:
            'Multiple upload attempts with rejected files from same IP ranges',
          affectedIPs: ['192.168.1.100', '192.168.1.101'],
          recommendation: 'Consider IP-based rate limiting or blocking',
        },
        {
          type: 'rate_limit_circumvention',
          confidence: 'low' as const,
          description: 'Pattern suggesting attempts to bypass rate limiting',
          affectedIPs: ['10.0.0.50'],
          recommendation:
            'Monitor for continued attempts and consider stricter limits',
        },
      ];

      return {
        patterns,
        riskScore: 65, // Medium risk
      };
    } catch (error: unknown) {
      console.error('[SecurityEvent] Failed to detect abuse patterns:', error);
      throw error instanceof Error ? error : new Error(String(error));
    }
  }
}

// Export singleton instance
export const securityEventLogger = new SecurityEventLogger();
