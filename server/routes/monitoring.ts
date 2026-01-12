/**
 * Monitoring Routes
 * 
 * Security monitoring dashboard and analytics endpoints
 */

import type { Express, Request, Response } from 'express';
import { securityEventLogger, SecurityEventType } from '../monitoring/security-events';
import { securityAlertManager } from '../monitoring/security-alerts';
import { checkTempHealth } from '../startup-cleanup';
import os from 'os';

/**
 * Register monitoring routes
 */
export function registerMonitoringRoutes(app: Express): void {
  
  /**
   * Security Dashboard - Main overview
   */
  app.get('/api/monitoring/dashboard', async (req: Request, res: Response) => {
    try {
      // Get temp directory health
      const tempHealth = await checkTempHealth();
      
      // Get system metrics
      const systemMetrics = {
        memory: {
          total: os.totalmem(),
          free: os.freemem(),
          used: os.totalmem() - os.freemem(),
          usagePercent: Math.round(((os.totalmem() - os.freemem()) / os.totalmem()) * 100),
        },
        loadAverage: os.loadavg(),
        uptime: os.uptime(),
        platform: os.platform(),
        nodeVersion: process.version,
      };

      // Get recent security analytics (mock data for now)
      const analytics = await securityEventLogger.getSecurityAnalytics(
        new Date(Date.now() - 24 * 60 * 60 * 1000), // Last 24 hours
        new Date()
      );

      // Get recent alerts
      const recentAlerts = securityAlertManager.getAlertHistory(10);

      // Get abuse pattern detection
      const abuseDetection = await securityEventLogger.detectAbusePatterns();

      const dashboard = {
        status: 'active',
        timestamp: new Date().toISOString(),
        overview: {
          totalEvents: analytics.totalEvents,
          criticalAlerts: recentAlerts.filter(a => a.severity === 'critical').length,
          highSeverityEvents: analytics.eventsBySeverity.high || 0,
          tempFiles: tempHealth.fileCount,
          tempSizeMB: Math.round(tempHealth.totalSize / (1024 * 1024)),
        },
        systemHealth: {
          tempDirectories: tempHealth,
          systemMetrics,
          status: tempHealth.healthy && systemMetrics.memory.usagePercent < 90 ? 'healthy' : 'warning',
        },
        securityMetrics: {
          eventsByType: analytics.eventsByType,
          eventsBySeverity: analytics.eventsBySeverity,
          topIPs: analytics.topIPs,
          hourlyBreakdown: analytics.hourlyBreakdown,
        },
        recentAlerts,
        abuseDetection,
        recommendations: generateRecommendations(tempHealth, analytics, abuseDetection),
      };

      res.json(dashboard);
    } catch (error) {
      console.error('[Monitoring] Dashboard error:', error);
      res.status(500).json({
        error: 'Dashboard generation failed',
        message: 'Unable to generate security dashboard',
      });
    }
  });

  /**
   * Security Events - Detailed event list
   */
  app.get('/api/monitoring/events', async (req: Request, res: Response) => {
    try {
      const {
        startTime = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        endTime = new Date().toISOString(),
        eventType,
        severity,
        ipAddress,
        limit = 100,
        offset = 0,
      } = req.query;

      // Get security events from logger
      const analytics = await securityEventLogger.getSecurityAnalytics(
        new Date(startTime as string),
        new Date(endTime as string),
        eventType ? [eventType as any] : undefined
      );

      // Mock event list (in production, this would query database)
      const events = generateMockEvents({
        startTime: new Date(startTime as string),
        endTime: new Date(endTime as string),
        eventType: eventType as string,
        severity: severity as string,
        ipAddress: ipAddress as string,
        limit: parseInt(limit as string),
        offset: parseInt(offset as string),
      });

      res.json({
        events,
        totalCount: analytics.totalEvents,
        filters: {
          startTime,
          endTime,
          eventType,
          severity,
          ipAddress,
        },
        pagination: {
          limit: parseInt(limit as string),
          offset: parseInt(offset as string),
          hasMore: events.length === parseInt(limit as string),
        },
      });
    } catch (error) {
      console.error('[Monitoring] Events error:', error);
      res.status(500).json({
        error: 'Events retrieval failed',
        message: 'Unable to retrieve security events',
      });
    }
  });

  /**
   * Alert History - Recent security alerts
   */
  app.get('/api/monitoring/alerts', (req: Request, res: Response) => {
    try {
      const { limit = 50, severity, type } = req.query;
      
      let alerts = securityAlertManager.getAlertHistory(parseInt(limit as string));
      
      // Apply filters if specified
      if (severity) {
        alerts = alerts.filter(a => a.severity === severity);
      }
      
      if (type) {
        alerts = alerts.filter(a => a.type === type);
      }

      res.json({
        alerts,
        totalCount: alerts.length,
        filters: {
          severity: severity as string,
          type: type as string,
          limit: parseInt(limit as string),
        },
      });
    } catch (error) {
      console.error('[Monitoring] Alerts error:', error);
      res.status(500).json({
        error: 'Alerts retrieval failed',
        message: 'Unable to retrieve security alerts',
      });
    }
  });

  /**
   * Abuse Detection - Pattern analysis
   */
  app.get('/api/monitoring/abuse-detection', async (req: Request, res: Response) => {
    try {
      const { hoursBack = 24 } = req.query;
      
      const detection = await securityEventLogger.detectAbusePatterns(
        parseInt(hoursBack as string)
      );

      res.json({
        patterns: detection.patterns,
        riskScore: detection.riskScore,
        riskLevel: getRiskLevel(detection.riskScore),
        analysisTime: new Date().toISOString(),
        timeWindow: `${hoursBack} hours`,
      });
    } catch (error) {
      console.error('[Monitoring] Abuse detection error:', error);
      res.status(500).json({
        error: 'Abuse detection failed',
        message: 'Unable to analyze abuse patterns',
      });
    }
  });

  /**
   * Real-time Metrics - Live security metrics
   */
  app.get('/api/monitoring/metrics', async (req: Request, res: Response) => {
    try {
      const tempHealth = await checkTempHealth();
      
      const metrics = {
        timestamp: new Date().toISOString(),
        tempDirectory: {
          fileCount: tempHealth.fileCount,
          totalSize: tempHealth.totalSize,
          healthy: tempHealth.healthy,
        },
        system: {
          memoryUsagePercent: Math.round(((os.totalmem() - os.freemem()) / os.totalmem()) * 100),
          loadAverage: os.loadavg(),
          uptime: os.uptime(),
        },
        security: {
          eventsLastMinute: Math.floor(Math.random() * 50), // Mock data
          rateLimitHits: Math.floor(Math.random() * 20),    // Mock data
          suspiciousIPs: 2,                                   // Mock data
        },
      };

      res.json(metrics);
    } catch (error) {
      console.error('[Monitoring] Metrics error:', error);
      res.status(500).json({
        error: 'Metrics retrieval failed',
        message: 'Unable to retrieve real-time metrics',
      });
    }
  });

  /**
   * Export Security Data - For external analysis
   */
  app.get('/api/monitoring/export', async (req: Request, res: Response) => {
    try {
      const {
        format = 'json',
        startTime = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        endTime = new Date().toISOString(),
        eventTypes,
      } = req.query;

      // Get analytics data
      const analytics = await securityEventLogger.getSecurityAnalytics(
        new Date(startTime as string),
        new Date(endTime as string),
        eventTypes ? (eventTypes as string).split(',') as any : undefined
      );

      const exportData = {
        exportInfo: {
          timestamp: new Date().toISOString(),
          format: format as string,
          timeRange: {
            start: startTime,
            end: endTime,
          },
        },
        analytics,
        systemInfo: {
          platform: os.platform(),
          nodeVersion: process.version,
          memory: {
            total: os.totalmem(),
            free: os.freemem(),
          },
        },
      };

      if (format === 'csv') {
        // Convert to CSV format
        const csv = convertToCSV(analytics);
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', 'attachment; filename="security-export.csv"');
        res.send(csv);
      } else {
        // Default JSON format
        res.json(exportData);
      }
    } catch (error) {
      console.error('[Monitoring] Export error:', error);
      res.status(500).json({
        error: 'Export failed',
        message: 'Unable to export security data',
      });
    }
  });
}

/**
 * Generate recommendations based on security metrics
 */
function generateRecommendations(
  tempHealth: any,
  analytics: any,
  abuseDetection: any
): string[] {
  const recommendations: string[] = [];

  // Temp directory recommendations
  if (!tempHealth.healthy) {
    recommendations.push('Run manual cleanup via /api/health/cleanup endpoint');
  }
  
  if (tempHealth.fileCount > 100) {
    recommendations.push('Consider increasing cleanup frequency due to high temp file count');
  }

  // Analytics-based recommendations
  if ((analytics.eventsBySeverity.high || 0) > 20) {
    recommendations.push('High number of security events detected - review access patterns');
  }

  if ((analytics.eventsByType.rate_limit_exceeded || 0) > 50) {
    recommendations.push('High rate limit activity - consider adjusting limits or investigating abuse');
  }

  // Abuse detection recommendations
  if (abuseDetection.riskScore > 70) {
    recommendations.push('High abuse risk detected - consider IP blocking or stricter rate limits');
  }

  return recommendations;
}

/**
 * Get risk level from score
 */
function getRiskLevel(score: number): 'low' | 'medium' | 'high' | 'critical' {
  if (score >= 80) return 'critical';
  if (score >= 60) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
}

/**
 * Generate mock security events for testing
 */
function generateMockEvents(params: {
  startTime: Date;
  endTime: Date;
  eventType?: string;
  severity?: string;
  ipAddress?: string;
  limit: number;
  offset: number;
}): any[] {
  const events = [];
  const eventTypes: SecurityEventType[] = [
    'upload_rejected',
    'rate_limit_exceeded',
    'burst_limit_exceeded',
    'invalid_file_type',
    'suspicious_access',
    'temp_cleanup_performed',
  ];

  for (let i = 0; i < params.limit; i++) {
    const timestamp = new Date(
      params.startTime.getTime() + 
      Math.random() * (params.endTime.getTime() - params.startTime.getTime())
    );

    const eventType = params.eventType || eventTypes[Math.floor(Math.random() * eventTypes.length)];
    const severity = params.severity || ['low', 'medium', 'high'][Math.floor(Math.random() * 3)];

    events.push({
      id: `evt_${Date.now()}_${i}`,
      event: eventType,
      severity,
      timestamp: timestamp.toISOString(),
      source: 'security_system',
      ipAddress: params.ipAddress || `192.168.1.${Math.floor(Math.random() * 255)}`,
      userAgent: 'Mozilla/5.0 (Test Browser)',
      details: {
        reason: 'Mock security event',
        confidence: Math.random(),
      },
    });
  }

  return events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}

/**
 * Convert analytics data to CSV format
 */
function convertToCSV(analytics: any): string {
  const headers = ['timestamp', 'event_type', 'severity', 'count', 'description'];
  const rows = [];

  // Add header row
  rows.push(headers.join(','));

  // Add data rows
  Object.entries(analytics.eventsByType).forEach(([type, count]) => {
    const numericCount = Number(count) || 0;
    rows.push([
      new Date().toISOString(),
      type,
      'mixed',
      numericCount,
      `Total ${type} events`,
    ].join(','));
  });

  return rows.join('\n');
}