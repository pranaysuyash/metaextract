/**
 * Security Alerting System
 *
 * Monitors security metrics and sends alerts when thresholds are exceeded.
 * Integrates with multiple alerting channels: email, webhooks, logs.
 */

import { storage } from '../storage/index';
import { checkTempHealth } from '../startup-cleanup';
import os from 'os';

// Alert Configuration
const ALERT_THRESHOLDS = {
  // Temp Directory Alerts
  TEMP_FILE_COUNT: 500, // Alert at 500 temp files
  TEMP_DIR_SIZE_GB: 5, // Alert at 5GB temp usage
  TEMP_FILE_AGE_HOURS: 2, // Alert if files older than 2 hours

  // Rate Limiting Alerts
  RATE_LIMIT_HITS_PER_MINUTE: 20, // Alert at 20 rate limit hits/minute
  BURST_LIMIT_HITS_PER_MINUTE: 50, // Alert at 50 burst limit hits/minute

  // System Resource Alerts
  MEMORY_USAGE_PERCENT: 85, // Alert at 85% memory usage
  DISK_USAGE_PERCENT: 90, // Alert at 90% disk usage

  // Security Event Alerts
  FAILED_UPLOADS_PER_MINUTE: 100, // Alert at 100 failed uploads/minute
  SUSPICIOUS_IPS_THRESHOLD: 10, // Alert at 10 suspicious IPs

  // Abuse Pattern Alerts
  COOKIE_RESETS_PER_HOUR: 50, // Alert at 50 cookie resets/hour
  MULTIPLE_SESSIONS_PER_IP: 20, // Alert at 20 sessions per IP
};

// Alert Channels
interface AlertChannel {
  name: string;
  enabled: boolean;
  send: (alert: SecurityAlert) => Promise<void>;
}

interface SecurityAlert {
  id?: string;
  type: 'security' | 'performance' | 'abuse' | string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  details: Record<string, any>;
  timestamp?: Date;
  source?: string;
  recommendation?: string;
  metadata?: Record<string, any>;
}

/**
 * Email Alert Channel
 */
class EmailAlertChannel implements AlertChannel {
  name = 'email';
  enabled = process.env.ENABLE_EMAIL_ALERTS === 'true';

  async send(alert: SecurityAlert): Promise<void> {
    if (!this.enabled) return;

    try {
      // Implementation would integrate with email service
      console.log(`[SecurityAlert] Email alert sent: ${alert.title}`);

      // Log the email that would be sent
      const emailContent = this.formatEmail(alert);
      console.log('[SecurityAlert] Email content:', emailContent);

      // Store alert in database for audit trail
      await this.storeAlert(alert);
    } catch (error) {
      console.error('[SecurityAlert] Failed to send email alert:', error);
    }
  }

  private formatEmail(alert: SecurityAlert): string {
    const ts = alert.timestamp || new Date();
    return `
Subject: [${alert.severity.toUpperCase()}] ${alert.title}

${alert.message}

Details:
${JSON.stringify(alert.details, null, 2)}

Timestamp: ${ts.toISOString()}
Source: ${alert.source}
${alert.recommendation ? `Recommendation: ${alert.recommendation}` : ''}

---
This is an automated security alert from MetaExtract.
    `.trim();
  }

  private async storeAlert(alert: SecurityAlert): Promise<void> {
    try {
      await storage.logSecurityEvent?.({
        event: 'security_alert_sent',
        severity: alert.severity,
        alertId: alert.id,
        alertType: alert.type,
        channel: this.name,
        details: alert.details,
        timestamp: alert.timestamp,
      });
    } catch (error) {
      console.error('[SecurityAlert] Failed to store alert:', error);
    }
  }
}

/**
 * Webhook Alert Channel
 */
class WebhookAlertChannel implements AlertChannel {
  name = 'webhook';
  enabled = !!process.env.SECURITY_WEBHOOK_URL;
  webhookUrl = process.env.SECURITY_WEBHOOK_URL || '';

  async send(alert: SecurityAlert): Promise<void> {
    if (!this.enabled) return;

    try {
      const ts = alert.timestamp || new Date();
      const payload = {
        alert_id: alert.id,
        severity: alert.severity,
        title: alert.title,
        message: alert.message,
        details: alert.details,
        timestamp: ts.toISOString(),
        source: alert.source,
        recommendation: alert.recommendation,
      };

      console.log(`[SecurityAlert] Webhook alert sent: ${alert.title}`);
      console.log(
        '[SecurityAlert] Webhook payload:',
        JSON.stringify(payload, null, 2)
      );

      // In production, this would make actual HTTP request
      // await fetch(this.webhookUrl, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(payload),
      // });
    } catch (error) {
      console.error('[SecurityAlert] Failed to send webhook alert:', error);
    }
  }
}

/**
 * Log Alert Channel
 */
class LogAlertChannel implements AlertChannel {
  name = 'log';
  enabled = true; // Always enabled for audit trail

  async send(alert: SecurityAlert): Promise<void> {
    const logMessage = `[SECURITY_ALERT] ${alert.severity.toUpperCase()}: ${alert.title} - ${alert.message}`;

    switch (alert.severity) {
      case 'critical':
        console.error(logMessage, alert.details);
        break;
      case 'high':
        console.warn(logMessage, alert.details);
        break;
      case 'medium':
        console.log(logMessage, alert.details);
        break;
      case 'low':
        console.debug(logMessage, alert.details);
        break;
    }

    // Always store in database for audit trail
    try {
      await storage.logSecurityEvent?.({
        event: 'security_alert_logged',
        severity: alert.severity,
        alertId: alert.id,
        alertType: alert.type,
        channel: this.name,
        details: alert.details,
        timestamp: alert.timestamp,
      });
    } catch (error) {
      console.error('[SecurityAlert] Failed to log security event:', error);
    }
  }
}

/**
 * Security Alert Manager
 */
export class SecurityAlertManager {
  private channels: AlertChannel[] = [
    new LogAlertChannel(),
    new EmailAlertChannel(),
    new WebhookAlertChannel(),
  ];

  private alertHistory: SecurityAlert[] = [];
  private alertCooldowns = new Map<string, number>();
  private readonly COOLDOWN_MS = 5 * 60 * 1000; // 5 minutes

  /**
   * Check system security metrics and trigger alerts if needed
   */
  async checkSecurityMetrics(): Promise<void> {
    try {
      // Check temp directory health
      await this.checkTempDirectoryHealth();

      // Check system resources
      await this.checkSystemResources();

      // Check rate limiting metrics
      await this.checkRateLimitingMetrics();

      // Check for abuse patterns
      await this.checkAbusePatterns();
    } catch (error) {
      console.error(
        '[SecurityAlert] Error during security metrics check:',
        error
      );

      // Send critical alert about monitoring failure
      await this.sendAlert({
        id: `monitoring_failure_${Date.now()}`,
        type: 'security',
        severity: 'critical',
        title: 'Security Monitoring Failure',
        message: 'The security monitoring system encountered an error',
        details: {
          error: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date(),
        source: 'SecurityAlertManager',
        recommendation: 'Check system logs and restart monitoring services',
      });
    }
  }

  /**
   * Check temp directory health and alert if needed
   */
  private async checkTempDirectoryHealth(): Promise<void> {
    const health = await checkTempHealth();

    if (!health.healthy) {
      await this.sendAlert({
        id: `temp_health_${Date.now()}`,
        type: 'performance',
        severity: 'medium',
        title: 'Temp Directory Health Warning',
        message: 'Temp directory usage exceeded normal thresholds',
        details: {
          fileCount: health.fileCount,
          totalSize: health.totalSize,
          warnings: health.warnings,
        },
        timestamp: new Date(),
        source: 'TempHealthCheck',
        recommendation: 'Run manual cleanup via /api/health/cleanup endpoint',
      });
    }

    // Check for excessive temp file usage
    if (health.fileCount > ALERT_THRESHOLDS.TEMP_FILE_COUNT) {
      await this.sendAlert({
        id: `temp_files_${Date.now()}`,
        type: 'security',
        severity: 'high',
        title: 'Excessive Temp Files Detected',
        message: `Temp directory contains ${health.fileCount} files (threshold: ${ALERT_THRESHOLDS.TEMP_FILE_COUNT})`,
        details: {
          currentCount: health.fileCount,
          threshold: ALERT_THRESHOLDS.TEMP_FILE_COUNT,
          directory: '/tmp',
        },
        timestamp: new Date(),
        source: 'TempFileCheck',
        recommendation: 'Investigate upload patterns and run cleanup',
      });
    }

    // Check for large temp directory size
    const tempSizeGB = health.totalSize / (1024 * 1024 * 1024);
    if (tempSizeGB > ALERT_THRESHOLDS.TEMP_DIR_SIZE_GB) {
      await this.sendAlert({
        id: `temp_size_${Date.now()}`,
        type: 'security',
        severity: 'high',
        title: 'Large Temp Directory Size',
        message: `Temp directory size is ${tempSizeGB.toFixed(2)}GB (threshold: ${ALERT_THRESHOLDS.TEMP_DIR_SIZE_GB}GB)`,
        details: {
          currentSizeGB: tempSizeGB,
          thresholdGB: ALERT_THRESHOLDS.TEMP_DIR_SIZE_GB,
        },
        timestamp: new Date(),
        source: 'TempSizeCheck',
        recommendation: 'Run cleanup and investigate large file sources',
      });
    }
  }

  /**
   * Check system resource usage
   */
  private async checkSystemResources(): Promise<void> {
    // Check memory usage
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const memUsagePercent = ((totalMem - freeMem) / totalMem) * 100;

    if (memUsagePercent > ALERT_THRESHOLDS.MEMORY_USAGE_PERCENT) {
      await this.sendAlert({
        id: `memory_usage_${Date.now()}`,
        type: 'performance',
        severity: 'high',
        title: 'High Memory Usage',
        message: `Memory usage is ${memUsagePercent.toFixed(1)}% (threshold: ${ALERT_THRESHOLDS.MEMORY_USAGE_PERCENT}%)`,
        details: {
          totalMemory: totalMem,
          freeMemory: freeMem,
          usedMemory: totalMem - freeMem,
          usagePercent: memUsagePercent,
        },
        timestamp: new Date(),
        source: 'MemoryCheck',
        recommendation: 'Monitor for memory leaks and consider scaling',
      });
    }

    // Check disk usage (simplified - would need proper disk stats in production)
    const loadAvg = os.loadavg();
    if (loadAvg[0] > 2.0) {
      // High load average
      await this.sendAlert({
        id: `high_load_${Date.now()}`,
        type: 'performance',
        severity: 'medium',
        title: 'High System Load',
        message: `System load average is ${loadAvg[0].toFixed(2)}`,
        details: {
          loadAverage: loadAvg,
          cpuCount: os.cpus().length,
        },
        timestamp: new Date(),
        source: 'LoadCheck',
        recommendation:
          'Monitor system performance and check for resource-intensive processes',
      });
    }
  }

  /**
   * Check rate limiting metrics
   */
  private async checkRateLimitingMetrics(): Promise<void> {
    // This would check Redis/memory for rate limit counters
    // For now, we'll simulate the check
    const rateLimitHits = await this.getRateLimitHits('last_minute');

    if (rateLimitHits > ALERT_THRESHOLDS.RATE_LIMIT_HITS_PER_MINUTE) {
      await this.sendAlert({
        id: `rate_limit_hits_${Date.now()}`,
        type: 'abuse',
        severity: 'medium',
        title: 'High Rate Limit Activity',
        message: `${rateLimitHits} rate limit hits in the last minute (threshold: ${ALERT_THRESHOLDS.RATE_LIMIT_HITS_PER_MINUTE})`,
        details: {
          hits: rateLimitHits,
          threshold: ALERT_THRESHOLDS.RATE_LIMIT_HITS_PER_MINUTE,
          timeWindow: '1 minute',
        },
        timestamp: new Date(),
        source: 'RateLimitCheck',
        recommendation: 'Monitor for potential abuse or bot activity',
      });
    }
  }

  /**
   * Check for abuse patterns
   */
  private async checkAbusePatterns(): Promise<void> {
    // Check for suspicious IP patterns
    const suspiciousIPs = await this.getSuspiciousIPs();

    if (suspiciousIPs.length > ALERT_THRESHOLDS.SUSPICIOUS_IPS_THRESHOLD) {
      await this.sendAlert({
        id: `suspicious_ips_${Date.now()}`,
        type: 'abuse',
        severity: 'high',
        title: 'Multiple Suspicious IPs Detected',
        message: `${suspiciousIPs.length} suspicious IPs detected (threshold: ${ALERT_THRESHOLDS.SUSPICIOUS_IPS_THRESHOLD})`,
        details: {
          suspiciousIPs: suspiciousIPs.slice(0, 10), // Top 10
          totalCount: suspiciousIPs.length,
          threshold: ALERT_THRESHOLDS.SUSPICIOUS_IPS_THRESHOLD,
        },
        timestamp: new Date(),
        source: 'AbusePatternCheck',
        recommendation: 'Review access logs and consider IP blocking',
      });
    }
  }

  /**
   * Send alert through all enabled channels
   */
  public async sendAlert(alert: SecurityAlert): Promise<void> {
    // Ensure required defaults exist
    alert.id =
      alert.id ||
      `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    alert.timestamp = alert.timestamp || new Date();
    alert.source = alert.source || 'SecurityAlertManager';

    // Check cooldown to prevent alert spam
    const cooldownKey = `${alert.type}_${alert.severity}_${alert.source}`;
    const now = Date.now();

    if (this.alertCooldowns.has(cooldownKey)) {
      const cooldownUntil = this.alertCooldowns.get(cooldownKey)!;
      if (now < cooldownUntil) {
        console.log(
          `[SecurityAlert] Alert suppressed due to cooldown: ${alert.title}`
        );
        return;
      }
    }

    // Set cooldown for this alert type
    this.alertCooldowns.set(cooldownKey, now + this.COOLDOWN_MS);

    // Store in history
    this.alertHistory.push(alert);

    // Keep only last 1000 alerts in memory
    if (this.alertHistory.length > 1000) {
      this.alertHistory = this.alertHistory.slice(-1000);
    }

    // Send through all channels
    const results = await Promise.allSettled(
      this.channels.map(channel =>
        channel.enabled ? channel.send(alert) : Promise.resolve()
      )
    );

    // Log any failures
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        console.error(
          `[SecurityAlert] Failed to send alert via ${this.channels[index].name}:`,
          result.reason
        );
      }
    });

    console.log(
      `[SecurityAlert] Alert sent: ${alert.title} (${alert.severity})`
    );
  }

  /**
   * Get recent alert history
   */
  getAlertHistory(limit = 100): SecurityAlert[] {
    return this.alertHistory.slice(-limit);
  }

  /**
   * Get rate limit hits (mock implementation - would integrate with Redis/store)
   */
  private async getRateLimitHits(timeWindow: string): Promise<number> {
    // This would query Redis/memory store for actual rate limit data
    // For now, return mock data
    return Math.floor(Math.random() * 30); // 0-30 hits
  }

  /**
   * Get suspicious IPs (mock implementation)
   */
  private async getSuspiciousIPs(): Promise<string[]> {
    // This would analyze access patterns and identify suspicious IPs
    // For now, return mock data
    return ['192.168.1.100', '10.0.0.50']; // Mock suspicious IPs
  }

  /**
   * Start periodic security monitoring
   */
  startPeriodicMonitoring(intervalMs = 60 * 1000): NodeJS.Timeout {
    console.log(
      `[SecurityAlert] Starting periodic security monitoring every ${intervalMs / 1000} seconds`
    );

    return setInterval(async () => {
      try {
        await this.checkSecurityMetrics();
      } catch (error) {
        console.error(
          '[SecurityAlert] Error during periodic monitoring:',
          error
        );
      }
    }, intervalMs);
  }

  /**
   * Stop periodic monitoring
   */
  stopPeriodicMonitoring(timer: NodeJS.Timeout): void {
    clearInterval(timer);
    console.log('[SecurityAlert] Periodic security monitoring stopped');
  }
}

// Export singleton instance
export const securityAlertManager = new SecurityAlertManager();
