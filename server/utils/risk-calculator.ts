/**
 * Risk Calculator for Enhanced Detection
 *
 * Calculates comprehensive risk scores based on multiple security factors
 * and provides recommendations for graduated response.
 */

import { Request } from 'express';
import { storage } from '../storage/index';

export interface RiskFactors {
  ipChanges: number;
  deviceTokenAge: number;
  requestFrequency: number;
  failedAttempts: number;
  geographicAnomalies: number;
  userAgentAnomalies: number;
  sessionAnomalies: number;
  fingerprintAnomalies: number;
}

export interface DeviceRiskAnalysis {
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  contributingFactors: string[];
  recommendations: string[];
  confidence: number;
  timestamp: Date;
}

/**
 * Calculate comprehensive device risk score
 */
export async function calculateDeviceRiskScore(
  req: Request,
  deviceId: string
): Promise<DeviceRiskAnalysis> {
  const factors = await calculateRiskFactors(req, deviceId);
  let riskScore = 0;
  const contributingFactors: string[] = [];

  // IP changes (0-25 points)
  if (factors.ipChanges > 5) {
    riskScore += 25;
    contributingFactors.push(`Multiple IPs from device: ${factors.ipChanges} different addresses`);
  } else if (factors.ipChanges > 3) {
    riskScore += 15;
    contributingFactors.push(`Multiple IPs from device: ${factors.ipChanges} different addresses`);
  } else if (factors.ipChanges > 1) {
    riskScore += 5;
  }

  // Device token age (0-20 points)
  if (factors.deviceTokenAge < 60) {
    riskScore += 20;
    contributingFactors.push('Very new device token (<1 minute old)');
  } else if (factors.deviceTokenAge < 300) {
    riskScore += 10;
    contributingFactors.push('New device token (<5 minutes old)');
  }

  // Request frequency (0-25 points)
  if (factors.requestFrequency > 20) {
    riskScore += 25;
    contributingFactors.push(`Very high request frequency: ${factors.requestFrequency} requests/hour`);
  } else if (factors.requestFrequency > 10) {
    riskScore += 15;
    contributingFactors.push(`High request frequency: ${factors.requestFrequency} requests/hour`);
  } else if (factors.requestFrequency > 5) {
    riskScore += 5;
  }

  // Failed attempts (0-15 points)
  if (factors.failedAttempts > 10) {
    riskScore += 15;
    contributingFactors.push(`High failure rate: ${factors.failedAttempts} failed attempts`);
  } else if (factors.failedAttempts > 5) {
    riskScore += 8;
    contributingFactors.push(`Elevated failure rate: ${factors.failedAttempts} failed attempts`);
  } else if (factors.failedAttempts > 2) {
    riskScore += 3;
  }

  // Geographic anomalies (0-10 points)
  if (factors.geographicAnomalies > 0) {
    riskScore += 10;
    contributingFactors.push('Geographic inconsistencies detected');
  }

  // User agent anomalies (0-5 points)
  if (factors.userAgentAnomalies > 0) {
    riskScore += 5;
    contributingFactors.push('Suspicious user agent characteristics');
  }

  // Calculate confidence based on data availability
  let confidence = 0.5;
  if (factors.requestFrequency > 0) confidence += 0.2;
  if (factors.ipChanges > 0) confidence += 0.1;
  if (factors.failedAttempts > 0) confidence += 0.1;
  if (contributingFactors.length > 0) confidence += 0.1;
  confidence = Math.min(0.95, confidence);

  return {
    riskScore: Math.min(100, riskScore),
    riskLevel: getRiskLevel(riskScore),
    contributingFactors,
    recommendations: getRecommendations(riskScore, contributingFactors),
    confidence,
    timestamp: new Date()
  };
}

/**
 * Calculate detailed risk factors for a device
 */
export async function calculateRiskFactors(
  req: Request,
  deviceId: string
): Promise<RiskFactors> {
  const ip = req.ip || req.connection.remoteAddress || 'unknown';

  // Get recent activity for this device
  const recentActivity = await getRecentDeviceActivity(deviceId, 60); // Last 60 minutes
  const recentIps = recentActivity.map(a => a.ip).filter(Boolean);
  const uniqueIps = new Set(recentIps);

  // Calculate factors
  const ipChanges = uniqueIps.size - 1;

  // Device token age
  const token = req.cookies?.metaextract_device;
  let deviceTokenAge = 0;
  if (token) {
    try {
      // Simple token age calculation (would use proper JWT verification in production)
      const decoded = JSON.parse(Buffer.from(token, 'base64').toString());
      if (decoded.iat) {
        deviceTokenAge = Math.floor((Date.now() - decoded.iat * 1000) / 1000);
      }
    } catch (e) {
      // Token parsing failed, assume very new
      deviceTokenAge = 0;
    }
  }

  // Request frequency
  const requestFrequency = recentActivity.length;

  // Failed attempts
  const failedAttempts = recentActivity.filter(a => a.status === 'failed').length;

  // Geographic anomalies (basic implementation)
  let geographicAnomalies = 0;
  if (uniqueIps.size > 3) {
    geographicAnomalies = 1;
  }

  // User agent anomalies
  let userAgentAnomalies = 0;
  const userAgent = req.headers['user-agent'] || '';
  if (userAgent.includes('HeadlessChrome')) userAgentAnomalies++;
  if (userAgent.includes('bot') || userAgent.includes('Bot')) userAgentAnomalies++;

  return {
    ipChanges,
    deviceTokenAge,
    requestFrequency,
    failedAttempts,
    geographicAnomalies,
    userAgentAnomalies,
    sessionAnomalies: 0, // Placeholder for future implementation
    fingerprintAnomalies: 0 // Placeholder for future implementation
  };
}

/**
 * Get previous attempts for logging
 */
export async function getPreviousAttempts(ip: string, deviceId: string): Promise<number> {
  try {
    const recentActivity = await getRecentDeviceActivity(deviceId, 15);
    return recentActivity.filter(a => a.ip === ip).length;
  } catch (error) {
    return 0;
  }
}

/**
 * Get session age for analysis
 */
export function getSessionAge(req: Request): number {
  const sessionCookie = req.cookies?.metaextract_session_id;
  if (!sessionCookie) return 0;

  // Parse session age from cookie (simplified)
  try {
    const decoded = JSON.parse(Buffer.from(sessionCookie, 'base64').toString());
    if (decoded.iat) {
      return Math.floor((Date.now() - decoded.iat * 1000) / 1000);
    }
  } catch (e) {
    return 0;
  }
  return 0;
}

/**
 * Get risk level from score
 */
function getRiskLevel(riskScore: number): 'low' | 'medium' | 'high' | 'critical' {
  if (riskScore >= 80) return 'critical';
  if (riskScore >= 60) return 'high';
  if (riskScore >= 40) return 'medium';
  return 'low';
}

/**
 * Get recommendations based on risk score and factors
 */
function getRecommendations(riskScore: number, factors: string[]): string[] {
  const recommendations: string[] = [];

  if (riskScore >= 80) {
    recommendations.push('Block request and require additional verification');
    recommendations.push('Manual security review recommended');
  } else if (riskScore >= 60) {
    recommendations.push('Implement rate limiting');
    recommendations.push('Require additional verification');
  } else if (riskScore >= 40) {
    recommendations.push('Monitor for continued suspicious activity');
    recommendations.push('Consider implementing delay challenge');
  }

  if (factors.some(f => f.includes('frequency'))) {
    recommendations.push('Consider implementing frequency-based rate limiting');
  }

  if (factors.some(f => f.includes('IP'))) {
    recommendations.push('Consider IP-based reputation checking');
  }

  if (factors.some(f => f.includes('user agent'))) {
    recommendations.push('Investigate for automation or bot activity');
  }

  return recommendations;
}

/**
 * Get recent device activity from storage
 */
async function getRecentDeviceActivity(
  deviceId: string,
  minutes: number
): Promise<Array<{
  ip: string;
  timestamp: number;
  status: string;
}>> {
  try {
    const key = `device_activity:${deviceId}`;
    const activityData = await storage.get(key);

    if (!activityData) return [];

    const activities = typeof activityData === 'string'
      ? JSON.parse(activityData)
      : activityData;

    const cutoff = Date.now() - minutes * 60 * 1000;
    return Array.isArray(activities)
      ? activities.filter(a => a.timestamp > cutoff)
      : [];
  } catch (error) {
    console.debug('Error getting device activity:', error);
    return [];
  }
}