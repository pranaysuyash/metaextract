/**
 * Advanced Protection Middleware
 *
 * Combines browser fingerprinting and ML-based anomaly detection
 * for comprehensive abuse prevention
 */

import { Request, Response, NextFunction } from 'express';
import {
  generateFingerprint,
  trackFingerprint,
  EnhancedFingerprint,
} from '../monitoring/browser-fingerprint';
import { mlAnomalyDetector } from '../monitoring/ml-anomaly-detection';
import { securityEventLogger } from '../monitoring/security-events';
import { securityAlertManager } from '../monitoring/security-alerts';

// Protection configuration
const PROTECTION_CONFIG = {
  // Enable/disable features
  BROWSER_FINGERPRINTING: true,
  ML_ANOMALY_DETECTION: true,
  REAL_TIME_ANALYSIS: true,

  // Thresholds (0-100 scale)
  BLOCK_THRESHOLD: 90,
  CHALLENGE_THRESHOLD: 70,
  MONITOR_THRESHOLD: 50,

  // Response actions
  ACTIONS: {
    ALLOW: 'allow',
    CHALLENGE: 'challenge',
    BLOCK: 'block',
    MONITOR: 'monitor',
  },

  // Challenge types
  CHALLENGES: {
    CAPTCHA: 'captcha',
    DELAY: 'delay',
    MFA: 'mfa',
    RATE_LIMIT: 'rate_limit',
  },
} as const;

// Protection result
interface ProtectionResult {
  action: 'allow' | 'challenge' | 'block' | 'monitor';
  confidence: number;
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  reasons: string[];
  recommendations: string[];
  fingerprint?: EnhancedFingerprint;
  anomalyResult?: any;
  challengeType?: string;
  challengeData?: any;
}

// Challenge response
interface ChallengeResponse {
  type: string;
  difficulty: 'easy' | 'medium' | 'hard';
  data: any;
  expiresAt: Date;
  sessionId: string;
}

/**
 * Advanced protection middleware
 */
export async function advancedProtectionMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    // Skip if protection is disabled
    if (!shouldApplyProtection(req)) {
      return next();
    }

    // Generate browser fingerprint
    let fingerprint: EnhancedFingerprint | undefined;
    if (PROTECTION_CONFIG.BROWSER_FINGERPRINTING) {
      const clientDataRaw =
        (req as any).body?.fingerprintData ?? (req as any).body?.fingerprint;
      let clientData: any = clientDataRaw;
      if (typeof clientDataRaw === 'string') {
        try {
          clientData = JSON.parse(clientDataRaw);
        } catch {
          clientData = undefined;
        }
      }
      fingerprint = await generateFingerprint(req, clientData);
    }

    // Run ML anomaly detection
    let anomalyResult;
    if (PROTECTION_CONFIG.ML_ANOMALY_DETECTION) {
      anomalyResult = await mlAnomalyDetector.detectUploadAnomaly(
        req,
        fingerprint
      );
    }

    // Track fingerprint across sessions
    let fingerprintTracking;
    if (fingerprint) {
      const userId = (req as any).user?.id;
      fingerprintTracking = await trackFingerprint(fingerprint, userId);
    }

    // Make protection decision
    const protectionResult = await makeProtectionDecision(
      req,
      fingerprint,
      anomalyResult,
      fingerprintTracking
    );

    // Store protection result in request for later use
    (req as any).protectionResult = protectionResult;

    // Execute protection action
    await executeProtectionAction(req, res, next, protectionResult);
  } catch (error: unknown) {
    console.error('[AdvancedProtection] Error:', error);

    // Normalize error details safely
    const errorDetails: { message?: string; stack?: string; raw?: string } = {};
    if (error instanceof Error) {
      errorDetails.message = error.message;
      errorDetails.stack = error.stack;
    } else {
      try {
        errorDetails.raw =
          typeof error === 'string' ? error : JSON.stringify(error);
      } catch (e) {
        errorDetails.raw = String(error);
      }
    }

    // On error, allow request but log the failure
    await securityEventLogger.logEvent({
      event: 'protection_error',
      severity: 'medium',
      timestamp: new Date(),
      source: 'advanced_protection',
      ipAddress: req.ip || (req as any).connection?.remoteAddress || 'unknown',
      userId: (req as any).user?.id,
      details: errorDetails,
    });

    // Allow request to continue on protection failure
    return next();
  }
}

/**
 * Determine if protection should be applied
 */
function shouldApplyProtection(req: Request): boolean {
  // Skip for health checks and monitoring endpoints
  const skipPaths = ['/health', '/api/monitoring', '/metrics', '/favicon.ico'];

  return !skipPaths.some(path => req.path.startsWith(path));
}

/**
 * Make protection decision based on all available data
 */
async function makeProtectionDecision(
  req: Request,
  fingerprint?: EnhancedFingerprint,
  anomalyResult?: any,
  fingerprintTracking?: any
): Promise<ProtectionResult> {
  let riskScore = 0;
  let confidence = 0;
  const reasons: string[] = [];
  const recommendations: string[] = [];

  // Factor in ML anomaly detection
  if (anomalyResult) {
    riskScore = Math.max(riskScore, anomalyResult.riskScore);
    confidence = Math.max(confidence, anomalyResult.confidence);
    reasons.push(...anomalyResult.contributingFactors);
    recommendations.push(...anomalyResult.recommendations);
  }

  // Factor in fingerprint analysis
  if (fingerprint && fingerprintTracking) {
    // New device risk
    if (fingerprintTracking.isNewDevice) {
      riskScore += 10;
      reasons.push('New device detected');
    }

    // Multiple sessions risk
    if (fingerprintTracking.previousSessions > 5) {
      riskScore += 15;
      reasons.push('Multiple sessions from same device');
    }

    // Fingerprint anomalies
    if (fingerprint.anomalies && fingerprint.anomalies.length > 0) {
      riskScore += 20;
      reasons.push(...fingerprint.anomalies);
    }

    // Low confidence fingerprint
    if (fingerprint.confidence < 0.5) {
      riskScore += 15;
      reasons.push('Low fingerprint confidence');
    }
  }

  // Factor in request characteristics
  const requestRisk = await calculateRequestRisk(req);
  riskScore += requestRisk.score;
  if (requestRisk.reasons.length > 0) {
    reasons.push(...requestRisk.reasons);
  }

  // Normalize risk score
  riskScore = Math.min(100, riskScore);

  // Determine risk level
  const riskLevel = getRiskLevel(riskScore);

  // Determine action based on thresholds
  let action: 'allow' | 'challenge' | 'block' | 'monitor';
  let challengeType: string | undefined;
  let challengeData: any | undefined;

  if (riskScore >= PROTECTION_CONFIG.BLOCK_THRESHOLD) {
    action = PROTECTION_CONFIG.ACTIONS.BLOCK;
  } else if (riskScore >= PROTECTION_CONFIG.CHALLENGE_THRESHOLD) {
    action = PROTECTION_CONFIG.ACTIONS.CHALLENGE;
    const challenge = await generateChallenge(req, riskLevel);
    challengeType = challenge.type;
    challengeData = challenge.data;
  } else if (riskScore >= PROTECTION_CONFIG.MONITOR_THRESHOLD) {
    action = PROTECTION_CONFIG.ACTIONS.MONITOR;
  } else {
    action = PROTECTION_CONFIG.ACTIONS.ALLOW;
  }

  // Determine final confidence
  confidence = Math.min(1.0, confidence + 0.2); // Boost confidence slightly

  return {
    action,
    confidence,
    riskScore,
    riskLevel,
    reasons: [...new Set(reasons)], // Remove duplicates
    recommendations: [...new Set(recommendations)],
    fingerprint,
    anomalyResult,
    challengeType,
    challengeData,
  };
}

/**
 * Calculate request-based risk factors
 */
async function calculateRequestRisk(
  req: Request
): Promise<{ score: number; reasons: string[] }> {
  let score = 0;
  const reasons: string[] = [];

  // Check for suspicious headers
  const userAgent = req.headers['user-agent'];
  if (!userAgent || userAgent.length < 10) {
    score += 15;
    reasons.push('Missing or invalid user agent');
  }

  // Check for automation indicators
  if (userAgent && userAgent.includes('HeadlessChrome')) {
    score += 25;
    reasons.push('Headless browser detected');
  }

  // Check for missing referer
  const referer = req.headers.referer;
  if (!referer) {
    score += 10;
    reasons.push('Missing referer header');
  }

  // Check for suspicious timing
  const hour = new Date().getHours();
  if (hour >= 2 && hour <= 5) {
    score += 10;
    reasons.push('Upload during suspicious hours');
  }

  // Check for missing client fingerprint data
  if (!req.body.fingerprintData) {
    score += 20;
    reasons.push('Missing client fingerprint data');
  }

  return { score, reasons };
}

/**
 * Get risk level from score
 */
export function getRiskLevel(
  riskScore: number
): 'low' | 'medium' | 'high' | 'critical' {
  if (riskScore >= 90) return 'critical';
  if (riskScore >= 70) return 'high';
  if (riskScore >= 40) return 'medium';
  return 'low';
}

/**
 * Execute protection action
 */
async function executeProtectionAction(
  req: Request,
  res: Response,
  next: NextFunction,
  result: ProtectionResult
): Promise<void> {
  const { action, riskScore, riskLevel, reasons, confidence } = result;

  // Log the protection decision
  await securityEventLogger.logEvent({
    event: 'protection_decision',
    severity: riskLevel,
    timestamp: new Date(),
    source: 'advanced_protection',
    ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
    userId: (req as any).user?.id,
    details: {
      action,
      riskScore,
      riskLevel,
      confidence,
      reasons,
      fingerprintId: result.fingerprint?.fingerprintHash,
      anomalyScore: result.anomalyResult?.riskScore,
      deviceId: result.fingerprint?.deviceId,
    },
  });

  // Execute based on action
  switch (action) {
    case PROTECTION_CONFIG.ACTIONS.ALLOW:
      // Allow request to proceed
      return next();

    case PROTECTION_CONFIG.ACTIONS.MONITOR:
      // Allow but add monitoring flag
      (req as any).monitoringRequired = true;
      return next();

    case PROTECTION_CONFIG.ACTIONS.CHALLENGE:
      // Send challenge response
      return await sendChallengeResponse(req, res, result);

    case PROTECTION_CONFIG.ACTIONS.BLOCK:
      // Block the request
      return await sendBlockResponse(req, res, result);

    default:
      // Unknown action, allow request
      console.warn(`[AdvancedProtection] Unknown action: ${action}`);
      return next();
  }
}

/**
 * Generate challenge for suspicious requests
 */
async function generateChallenge(
  req: Request,
  riskLevel: string
): Promise<ChallengeResponse> {
  const sessionId = `challenge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  let type: string;
  let difficulty: 'easy' | 'medium' | 'hard';
  let data: any;

  if (riskLevel === 'high') {
    type = PROTECTION_CONFIG.CHALLENGES.CAPTCHA;
    difficulty = 'hard';
    data = {
      siteKey: process.env.RECAPTCHA_SITE_KEY,
      challengeType: 'invisible',
    };
  } else if (riskLevel === 'medium') {
    type = PROTECTION_CONFIG.CHALLENGES.DELAY;
    difficulty = 'medium';
    data = {
      delaySeconds: 5,
      message: 'Please wait a moment before continuing...',
    };
  } else {
    type = PROTECTION_CONFIG.CHALLENGES.RATE_LIMIT;
    difficulty = 'easy';
    data = {
      maxRequests: 5,
      windowMinutes: 1,
    };
  }

  return {
    type,
    difficulty,
    data,
    expiresAt: new Date(Date.now() + 5 * 60 * 1000), // 5 minutes
    sessionId,
  };
}

/**
 * Send challenge response to client
 */
async function sendChallengeResponse(
  req: Request,
  res: Response,
  result: ProtectionResult
): Promise<void> {
  const { challengeType, challengeData, riskScore, reasons } = result;

  res.status(403).json({
    error: 'Challenge required',
    challenge: {
      type: challengeType,
      data: challengeData,
      riskScore,
      reasons,
      instructions: getChallengeInstructions(challengeType),
    },
    retryAfter: 60, // seconds
  });
  return;
}

/**
 * Send block response to client
 */
async function sendBlockResponse(
  req: Request,
  res: Response,
  result: ProtectionResult
): Promise<void> {
  const { riskScore, reasons, recommendations } = result;

  // Send security alert for blocked request
  await securityAlertManager.sendAlert({
    type: 'security',
    severity: 'high',
    title: 'Upload Blocked - Advanced Protection',
    message: `Upload request blocked due to high risk score (${riskScore}/100)`,
    details: {
      reasons,
      recommendations,
      ipAddress: req.ip || req.connection.remoteAddress,
      userAgent: req.headers['user-agent'],
      timestamp: new Date().toISOString(),
    },
    metadata: {
      category: 'abuse_prevention',
      tags: ['blocked', 'high_risk', 'advanced_protection'],
    },
  });

  res.status(403).json({
    error: 'Access denied',
    message: 'Your request has been blocked due to security concerns',
    riskScore,
    riskLevel: result.riskLevel,
    reasons: reasons.slice(0, 3), // Show top 3 reasons
    supportUrl: '/support/security',
    incidentId: `INC_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    retryAfter: 3600, // 1 hour
  });
  return;
}

/**
 * Get challenge instructions
 */
function getChallengeInstructions(challengeType?: string): string {
  switch (challengeType) {
    case PROTECTION_CONFIG.CHALLENGES.CAPTCHA:
      return 'Please complete the CAPTCHA to continue';
    case PROTECTION_CONFIG.CHALLENGES.DELAY:
      return 'Please wait for the specified delay before continuing';
    case PROTECTION_CONFIG.CHALLENGES.RATE_LIMIT:
      return 'Please reduce your request frequency';
    default:
      return 'Please complete the required verification';
  }
}

/**
 * Verify challenge response
 */
export async function verifyChallengeResponse(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const { challengeResponse, sessionId } = req.body;

    if (!challengeResponse || !sessionId) {
      res.status(400).json({
        error: 'Missing challenge response',
      });
      return;
    }

    // Verify the challenge response
    const isValid = await validateChallengeResponse(
      challengeResponse,
      sessionId
    );

    if (isValid) {
      // Challenge passed, allow request
      (req as any).challengePassed = true;
      return next();
    } else {
      // Challenge failed
      await securityEventLogger.logEvent({
        event: 'challenge_failed',
        severity: 'medium',
        timestamp: new Date(),
        source: 'challenge_verification',
        ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
        userId: (req as any).user?.id,
        details: {
          sessionId,
          challengeResponse,
        },
      });

      res.status(403).json({
        error: 'Challenge verification failed',
        retryAfter: 300, // 5 minutes
      });
      return;
    }
  } catch (error: unknown) {
    console.error('[ChallengeVerification] Error:', error);
    res.status(500).json({
      error: 'Challenge verification error',
    });
    return;
  }
}

/**
 * Validate challenge response
 */
async function validateChallengeResponse(
  response: any,
  sessionId: string
): Promise<boolean> {
  // This would validate the actual challenge response
  // For now, use simple validation

  if (!response || !sessionId) return false;

  // Basic validation logic
  if (response.type === 'captcha') {
    return response.token && response.token.length > 10;
  } else if (response.type === 'delay') {
    return response.completed === true;
  } else if (response.type === 'rate_limit') {
    return response.acknowledged === true;
  }

  return false;
}

/**
 * Get protection statistics
 */
export async function getProtectionStats(): Promise<any> {
  try {
    const stats = {
      totalRequests: 0,
      blockedRequests: 0,
      challengedRequests: 0,
      monitoredRequests: 0,
      allowedRequests: 0,
      averageRiskScore: 0,
      modelVersion: mlAnomalyDetector.getModelVersion(),
      isModelTrained: mlAnomalyDetector.isModelTrained(),
      timestamp: new Date(),
    };

    return stats;
  } catch (error: unknown) {
    console.error('[ProtectionStats] Error:', error);
    // Preserve stack when rethrowing if it's an Error
    if (error instanceof Error) throw error;
    throw new Error(String(error));
  }
}

/**
 * Export for use in routes
 */
export { ProtectionResult, ChallengeResponse };
