/**
 * Enhanced Quota Handler with Risk-Based Escalation
 *
 * Phase 2 Implementation: Enhanced Detection with Security Event Logging
 * Implements graduated response based on comprehensive risk analysis
 */

import { Request, Response } from 'express';
import { storage } from '../storage/index';
import {
  calculateDeviceRiskScore,
  getPreviousAttempts,
  getSessionAge,
} from './risk-calculator';

/**
 * Enhanced quota exceeded handler with risk-based escalation
 */
export async function handleEnhancedQuotaExceeded(
  req: Request,
  res: Response,
  clientId: string,
  ip: string
): Promise<void> {
  try {
    console.warn(`[Security] Quota exceeded for client: ${clientId} from IP ${ip}`);

    // Calculate comprehensive risk score
    const riskAnalysis = await calculateDeviceRiskScore(req, clientId);

    // Log detailed security event
    await logSecurityEvent({
      event: 'quota_exceeded',
      severity: riskAnalysis.riskLevel,
      timestamp: new Date(),
      source: 'enhanced_quota_handler',
      ipAddress: ip,
      clientId: clientId,
      userAgent: req.headers['user-agent'] || 'unknown',
      details: {
        riskScore: riskAnalysis.riskScore,
        riskLevel: riskAnalysis.riskLevel,
        confidence: riskAnalysis.confidence,
        contributingFactors: riskAnalysis.contributingFactors,
        previousAttempts: await getPreviousAttempts(ip, clientId),
        sessionAge: getSessionAge(req)
      }
    });

    // Escalate response based on risk level
    if (riskAnalysis.riskScore >= 80) {
      // Critical risk - Send alert and require CAPTCHA
      await sendSecurityAlert({
        type: 'security',
        severity: 'high',
        title: 'Critical Risk Quota Abuse Detected',
        message: `Client ${clientId} from IP ${ip} exceeded quota with critical risk score ${riskAnalysis.riskScore}/100`,
        details: {
          clientId,
          ipAddress: ip,
          riskScore: riskAnalysis.riskScore,
          contributingFactors: riskAnalysis.contributingFactors,
          timestamp: new Date()
        },
        metadata: {
          category: 'quota_abuse',
          tags: ['critical_risk', 'quota_exceeded', 'manual_review_recommended']
        }
      });

      // Return CAPTCHA challenge response
      res.status(429).json({
        error: 'Additional verification required',
        challenge: 'captcha',
        message: 'Please complete the CAPTCHA to continue',
        code: 'HIGH_RISK_CHALLENGE_REQUIRED',
        retryAfter: 300,
        riskAnalysis: {
          riskScore: riskAnalysis.riskScore,
          riskLevel: riskAnalysis.riskLevel,
          contributingFactors: riskAnalysis.contributingFactors.slice(0, 3)
        }
      });
      return;
    }

    if (riskAnalysis.riskScore >= 60) {
      // High risk - Require delay challenge
      res.status(429).json({
        error: 'Rate limit exceeded',
        challenge: 'delay',
        delaySeconds: 5,
        message: 'Please wait a moment before continuing',
        code: 'MODERATE_RISK_DELAY_REQUIRED',
        retryAfter: 60,
        riskAnalysis: {
          riskScore: riskAnalysis.riskScore,
          riskLevel: riskAnalysis.riskLevel,
          contributingFactors: riskAnalysis.contributingFactors.slice(0, 2)
        }
      });
      return;
    }

    if (riskAnalysis.riskScore >= 40) {
      // Medium risk - Standard rate limit with monitoring
      res.status(429).json({
        error: 'Rate limit exceeded',
        message: 'Please try again later',
        code: 'SUSPICIOUS_DEVICE',
        retryAfter: 300,
        riskAnalysis: {
          riskScore: riskAnalysis.riskScore,
          riskLevel: riskAnalysis.riskLevel,
          contributingFactors: riskAnalysis.contributingFactors.slice(0, 1)
        }
      });
      return;
    }

    // Low/Normal risk - Standard quota exceeded response
    res.status(429).json({
      error: 'Quota exceeded',
      message: 'Free limit reached on this device. Purchase credits to continue.',
      code: 'QUOTA_EXCEEDED',
      retryAfter: 86400, // 24 hours
      credits_required: 1
    });

  } catch (error) {
    console.error('[EnhancedQuotaHandler] Error:', error);
    // Fallback response
    res.status(429).json({
      error: 'Quota exceeded',
      message: 'Free limit reached on this device. Purchase credits to continue.',
      code: 'QUOTA_EXCEEDED'
    });
  }
}

/**
 * Log security event to storage
 */
async function logSecurityEvent(event: {
  event: string;
  severity: string;
  timestamp: Date;
  source: string;
  ipAddress: string;
  clientId?: string;
  userAgent?: string;
  details: any;
}): Promise<void> {
  try {
    const key = `security_events:${Date.now()}:${Math.random().toString(36).substr(2, 9)}`;

    const record = { ...event, id: key };

    await storage.logSecurityEvent?.(record);
    await storage.set(key, JSON.stringify(record));

    // Set expiry for security events (7 days)
    if (typeof (storage as any).expire === 'function') {
      await (storage as any).expire(key, 7 * 24 * 60 * 60);
    }

    console.log(`[SecurityEvent] ${event.event}: ${event.severity} - ${event.ipAddress}`);
  } catch (error) {
    console.error('[SecurityEvent] Failed to log event:', error);
  }
}

/**
 * Send security alert for high-risk incidents
 */
async function sendSecurityAlert(alert: {
  type: string;
  severity: string;
  title: string;
  message: string;
  details: any;
  metadata: any;
}): Promise<void> {
  try {
    // Log the alert
    const alertKey = `security_alert:${Date.now()}:${Math.random().toString(36).substr(2, 9)}`;
    await storage.set(alertKey, JSON.stringify({
      ...alert,
      id: alertKey,
      timestamp: new Date()
    }));

    console.warn(`[SecurityAlert] ${alert.severity.toUpperCase()}: ${alert.title}`);
    console.warn(`[SecurityAlert] Details:`, alert.details);

    // In production, this would send notifications via email, Slack, PagerDuty, etc.
    // For now, we just log to console
  } catch (error) {
    console.error('[SecurityAlert] Failed to send alert:', error);
  }
}

/**
 * Get recent security events for monitoring dashboard
 */
export async function getRecentSecurityEvents(limit: number = 50): Promise<any[]> {
  try {
    if (!storage.getSecurityEvents) return [];
    const result = await storage.getSecurityEvents({ limit, offset: 0 });
    return Array.isArray((result as any)?.events) ? (result as any).events : [];
  } catch {
    return [];
  }
}

/**
 * Get security statistics for dashboard
 */
export async function getSecurityStats(): Promise<{
  totalEvents: number;
  criticalEvents: number;
  highRiskEvents: number;
  mediumRiskEvents: number;
  lowRiskEvents: number;
}> {
  try {
    const events = await getRecentSecurityEvents(1000);
    const stats = {
      totalEvents: events.length,
      criticalEvents: 0,
      highRiskEvents: 0,
      mediumRiskEvents: 0,
      lowRiskEvents: 0,
    };

    for (const e of events) {
      const sev = String((e as any)?.severity || '').toLowerCase();
      if (sev === 'critical') stats.criticalEvents += 1;
      else if (sev === 'high') stats.highRiskEvents += 1;
      else if (sev === 'medium') stats.mediumRiskEvents += 1;
      else stats.lowRiskEvents += 1;
    }

    return stats;
  } catch {
    return {
      totalEvents: 0,
      criticalEvents: 0,
      highRiskEvents: 0,
      mediumRiskEvents: 0,
      lowRiskEvents: 0,
    };
  }
}
