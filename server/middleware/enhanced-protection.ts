/**
 * Enhanced Protection Middleware with Threat Intelligence
 *
 * Integrates external threat feeds with behavioral analysis
 * for comprehensive advanced threat protection
 */

import { Request, Response, NextFunction } from 'express';
import { advancedProtectionMiddleware } from './advanced-protection';
import { threatIntelligenceService } from '../monitoring/production-validation';
import { mlAnomalyDetector } from '../monitoring/ml-anomaly-detection';
import { securityEventLogger } from '../monitoring/security-events';
import { securityAlertManager } from '../monitoring/security-alerts';

// Enhanced protection configuration
const ENHANCED_PROTECTION_CONFIG = {
  // Feature flags
  THREAT_INTELLIGENCE: true,
  BEHAVIORAL_ANALYSIS: true,
  ADVANCED_ML: true,
  REAL_TIME_UPDATES: true,

  // Risk thresholds
  CRITICAL_RISK_THRESHOLD: 85,
  HIGH_RISK_THRESHOLD: 70,
  MEDIUM_RISK_THRESHOLD: 50,
  LOW_RISK_THRESHOLD: 30,

  // Response actions
  ACTIONS: {
    ALLOW: 'allow',
    CHALLENGE_EASY: 'challenge_easy',
    CHALLENGE_MEDIUM: 'challenge_medium',
    CHALLENGE_HARD: 'challenge_hard',
    BLOCK_TEMPORARY: 'block_temporary',
    BLOCK_PERMANENT: 'block_permanent',
    MONITOR: 'monitor',
  },

  // Challenge types
  CHALLENGES: {
    CAPTCHA: 'captcha',
    BEHAVIORAL: 'behavioral',
    DELAY: 'delay',
    MFA: 'mfa',
    RATE_LIMIT: 'rate_limit',
    DEVICE_VERIFICATION: 'device_verification',
  },

  // Feature weights for risk calculation
  WEIGHTS: {
    threatIntelligence: 0.35,
    behavioralAnalysis: 0.25,
    mlAnomalyDetection: 0.25,
    deviceFingerprint: 0.15,
  },
};

// Enhanced protection result
interface EnhancedProtectionResult {
  action: string;
  confidence: number;
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  threatIntelligence?: any;
  behavioralAnalysis?: any;
  mlAnalysis?: any;
  deviceAnalysis?: any;
  reasons: string[];
  recommendations: string[];
  challengeType?: string;
  challengeData?: any;
  incidentId?: string;
  requiresVerification?: boolean;
}

/**
 * Enhanced protection middleware
 */
export async function enhancedProtectionMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    // Skip if protection is disabled
    if (!shouldApplyProtection(req)) {
      return next();
    }

    console.log(`[EnhancedProtection] Processing request from ${req.ip}`);

    // Gather all protection data in parallel
    const [threatIntel, behavioralData, mlAnalysis, deviceAnalysis] =
      await Promise.allSettled([
        gatherThreatIntelligence(req),
        gatherBehavioralAnalysis(req),
        gatherMLAnalysis(req),
        gatherDeviceAnalysis(req),
      ]);

    // Calculate comprehensive risk assessment
    const protectionResult = await calculateEnhancedRisk(req, {
      threatIntel:
        threatIntel.status === 'fulfilled' ? threatIntel.value : null,
      behavioral:
        behavioralData.status === 'fulfilled' ? behavioralData.value : null,
      ml: mlAnalysis.status === 'fulfilled' ? mlAnalysis.value : null,
      device:
        deviceAnalysis.status === 'fulfilled' ? deviceAnalysis.value : null,
    });

    // Store protection result in request for later use
    (req as any).enhancedProtectionResult = protectionResult;

    // Execute protection action
    await executeEnhancedProtectionAction(req, res, next, protectionResult);
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    console.error('[EnhancedProtection] Critical error:', error);

    // On critical error, allow request but log extensively
    await securityEventLogger.logEvent({
      event: 'enhanced_protection_critical_error',
      severity: 'critical' as const,
      timestamp: new Date(),
      source: 'enhanced_protection' as const,
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userId: (req as any).user?.id,
      details: {
        error: error.message,
        stack: error.stack,
        fallbackAction: 'allow',
      },
    });

    // Allow request to continue on protection failure
    return next();
  }
}

/**
 * Gather threat intelligence data
 */
async function gatherThreatIntelligence(req: Request): Promise<any> {
  if (!ENHANCED_PROTECTION_CONFIG.THREAT_INTELLIGENCE) {
    return null;
  }

  try {
    const threatIntel =
      await threatIntelligenceService.checkThreatIntelligence(req);

    console.log(
      `[EnhancedProtection] Threat intelligence: ${threatIntel.riskScore}/100 (${threatIntel.threatLevel})`
    );

    return threatIntel;
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    console.warn(
      '[EnhancedProtection] Threat intelligence failed:',
      error.message
    );
    return null;
  }
}

/**
 * Gather behavioral analysis data
 */
async function gatherBehavioralAnalysis(req: Request): Promise<any> {
  if (!ENHANCED_PROTECTION_CONFIG.BEHAVIORAL_ANALYSIS) {
    return null;
  }

  try {
    // Get behavioral data from client if available
    const clientBehavioralData = req.body.behavioralData;

    if (clientBehavioralData) {
      console.log(
        `[EnhancedProtection] Received behavioral analysis: score=${clientBehavioralData.behavioralScore}, human=${clientBehavioralData.isHuman}`
      );
      return clientBehavioralData;
    }

    return null;
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    console.warn(
      '[EnhancedProtection] Behavioral analysis failed:',
      error.message
    );
    return null;
  }
}

/**
 * Gather ML anomaly detection data
 */
async function gatherMLAnalysis(req: Request): Promise<any> {
  if (!ENHANCED_PROTECTION_CONFIG.ADVANCED_ML) {
    return null;
  }

  try {
    const fingerprint = (req as any).protectionResult?.fingerprint;
    const mlResult = await mlAnomalyDetector.detectUploadAnomaly(
      req,
      fingerprint
    );

    console.log(
      `[EnhancedProtection] ML analysis: ${mlResult.riskScore}/100 (${mlResult.riskLevel})`
    );

    return mlResult;
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    console.warn('[EnhancedProtection] ML analysis failed:', error.message);
    return null;
  }
}

/**
 * Gather device analysis data
 */
async function gatherDeviceAnalysis(req: Request): Promise<any> {
  try {
    // Use existing device fingerprinting
    const existingResult = (req as any).protectionResult;

    if (existingResult?.fingerprint) {
      return {
        fingerprint: existingResult.fingerprint,
        deviceTracking: existingResult.fingerprintTracking,
        analysis: existingResult.anomalyResult,
      };
    }

    return null;
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    console.warn('[EnhancedProtection] Device analysis failed:', error.message);
    return null;
  }
}

/**
 * Calculate comprehensive risk assessment
 */
async function calculateEnhancedRisk(
  req: Request,
  data: {
    threatIntel?: any;
    behavioral?: any;
    ml?: any;
    device?: any;
  }
): Promise<EnhancedProtectionResult> {
  let totalRiskScore = 0;
  let confidence = 0;
  const reasons: string[] = [];
  const recommendations: string[] = [];
  let maxThreatLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';

  // 1. Threat Intelligence Analysis (35% weight)
  if (data.threatIntel) {
    const threatScore =
      data.threatIntel.riskScore *
      ENHANCED_PROTECTION_CONFIG.WEIGHTS.threatIntelligence;
    totalRiskScore += threatScore;
    confidence += 0.25;
    maxThreatLevel = getMaxThreatLevel(
      maxThreatLevel,
      data.threatIntel.threatLevel
    );

    reasons.push(
      ...data.threatIntel.sources.map(
        (source: string) => `Threat intelligence: ${source}`
      )
    );
    recommendations.push(...data.threatIntel.recommendations);

    console.log(
      `[EnhancedProtection] Threat intel contribution: ${threatScore.toFixed(1)} points`
    );
  }

  // 2. Behavioral Analysis (25% weight)
  if (data.behavioral) {
    const behavioralScore = calculateBehavioralRiskScore(data.behavioral);
    const weightedScore =
      behavioralScore * ENHANCED_PROTECTION_CONFIG.WEIGHTS.behavioralAnalysis;
    totalRiskScore += weightedScore;
    confidence += 0.25;

    if (!data.behavioral.isHuman) {
      maxThreatLevel = getMaxThreatLevel(maxThreatLevel, 'high');
      reasons.push('Behavioral analysis indicates automated behavior');
      recommendations.push('Monitor for continued automated patterns');
    }

    console.log(
      `[EnhancedProtection] Behavioral analysis contribution: ${weightedScore.toFixed(1)} points`
    );
  }

  // 3. ML Anomaly Detection (25% weight)
  if (data.ml) {
    const mlScore =
      data.ml.riskScore * ENHANCED_PROTECTION_CONFIG.WEIGHTS.mlAnomalyDetection;
    totalRiskScore += mlScore;
    confidence += 0.25;
    maxThreatLevel = getMaxThreatLevel(maxThreatLevel, data.ml.riskLevel);

    reasons.push(...data.ml.contributingFactors);
    recommendations.push(...data.ml.recommendations);

    console.log(
      `[EnhancedProtection] ML analysis contribution: ${mlScore.toFixed(1)} points`
    );
  }

  // 4. Device Fingerprinting (15% weight)
  if (data.device) {
    const deviceScore = calculateDeviceRiskScore(data.device);
    const weightedScore =
      deviceScore * ENHANCED_PROTECTION_CONFIG.WEIGHTS.deviceFingerprint;
    totalRiskScore += weightedScore;
    confidence += 0.15;

    if (data.device.fingerprint?.anomalies?.length > 0) {
      reasons.push(...data.device.fingerprint.anomalies);
    }

    console.log(
      `[EnhancedProtection] Device analysis contribution: ${weightedScore.toFixed(1)} points`
    );
  }

  // Normalize confidence
  confidence = Math.min(1.0, confidence + 0.1); // Boost confidence slightly

  // Normalize risk score
  totalRiskScore = Math.min(100, Math.round(totalRiskScore));

  // Determine final threat level
  const finalThreatLevel =
    maxThreatLevel !== 'low' ? maxThreatLevel : getRiskLevel(totalRiskScore);

  // Determine protection action
  const action = determineProtectionAction(
    totalRiskScore,
    finalThreatLevel,
    confidence
  );
  const challengeType = determineChallengeType(
    totalRiskScore,
    finalThreatLevel,
    data
  );

  // Generate incident ID for tracking
  const incidentId = `INC_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  return {
    action,
    confidence,
    riskScore: totalRiskScore,
    riskLevel: finalThreatLevel,
    threatIntelligence: data.threatIntel,
    behavioralAnalysis: data.behavioral,
    mlAnalysis: data.ml,
    deviceAnalysis: data.device,
    reasons: [...new Set(reasons)], // Remove duplicates
    recommendations: [...new Set(recommendations)],
    challengeType,
    incidentId,
    requiresVerification: action !== ENHANCED_PROTECTION_CONFIG.ACTIONS.ALLOW,
  };
}

/**
 * Calculate behavioral risk score
 */
function calculateBehavioralRiskScore(behavioralData: any): number {
  if (!behavioralData) return 0;

  let riskScore = 0;

  // Base score on behavioral score
  riskScore += (100 - behavioralData.behavioralScore) * 0.8;

  // Adjust for confidence level
  riskScore *= 1.5 - behavioralData.confidence;

  // Additional risk factors
  if (!behavioralData.isHuman) {
    riskScore += 25; // Significant boost for non-human detection
  }

  return Math.min(100, riskScore);
}

/**
 * Calculate device risk score
 */
function calculateDeviceRiskScore(deviceData: any): number {
  if (!deviceData) return 0;

  let riskScore = 0;

  // Fingerprint confidence
  if (deviceData.fingerprint) {
    riskScore += (1 - deviceData.fingerprint.confidence) * 30;
  }

  // Device tracking anomalies
  if (deviceData.deviceTracking) {
    if (deviceData.deviceTracking.isNewDevice) {
      riskScore += 10;
    }
    if (deviceData.deviceTracking.previousSessions > 10) {
      riskScore += 15;
    }
  }

  // ML analysis results
  if (deviceData.analysis) {
    riskScore += deviceData.analysis.riskScore * 0.3;
  }

  return Math.min(100, riskScore);
}

/**
 * Determine protection action
 */
function determineProtectionAction(
  riskScore: number,
  threatLevel: string,
  confidence: number
): string {
  // High confidence decisions
  if (confidence > 0.8) {
    if (riskScore >= ENHANCED_PROTECTION_CONFIG.CRITICAL_RISK_THRESHOLD) {
      return ENHANCED_PROTECTION_CONFIG.ACTIONS.BLOCK_TEMPORARY;
    }
    if (riskScore >= ENHANCED_PROTECTION_CONFIG.HIGH_RISK_THRESHOLD) {
      return ENHANCED_PROTECTION_CONFIG.ACTIONS.CHALLENGE_HARD;
    }
    if (riskScore >= ENHANCED_PROTECTION_CONFIG.MEDIUM_RISK_THRESHOLD) {
      return ENHANCED_PROTECTION_CONFIG.ACTIONS.CHALLENGE_MEDIUM;
    }
    if (riskScore >= ENHANCED_PROTECTION_CONFIG.LOW_RISK_THRESHOLD) {
      return ENHANCED_PROTECTION_CONFIG.ACTIONS.CHALLENGE_EASY;
    }
    return ENHANCED_PROTECTION_CONFIG.ACTIONS.ALLOW;
  }

  // Medium confidence - more conservative
  if (confidence > 0.5) {
    if (riskScore >= ENHANCED_PROTECTION_CONFIG.HIGH_RISK_THRESHOLD) {
      return ENHANCED_PROTECTION_CONFIG.ACTIONS.CHALLENGE_MEDIUM;
    }
    if (riskScore >= ENHANCED_PROTECTION_CONFIG.MEDIUM_RISK_THRESHOLD) {
      return ENHANCED_PROTECTION_CONFIG.ACTIONS.CHALLENGE_EASY;
    }
    return ENHANCED_PROTECTION_CONFIG.ACTIONS.MONITOR;
  }

  // Low confidence - monitor only
  return ENHANCED_PROTECTION_CONFIG.ACTIONS.MONITOR;
}

/**
 * Determine challenge type
 */
function determineChallengeType(
  riskScore: number,
  threatLevel: string,
  data: any
): string {
  // Behavioral challenges for sophisticated threats
  if (data.behavioral && !data.behavioral.isHuman) {
    return ENHANCED_PROTECTION_CONFIG.CHALLENGES.BEHAVIORAL;
  }

  // CAPTCHA for high-risk automated behavior
  if (riskScore >= ENHANCED_PROTECTION_CONFIG.HIGH_RISK_THRESHOLD) {
    return ENHANCED_PROTECTION_CONFIG.CHALLENGES.CAPTCHA;
  }

  // Device verification for suspicious devices
  if (data.device && data.device.fingerprint?.confidence < 0.5) {
    return ENHANCED_PROTECTION_CONFIG.CHALLENGES.DEVICE_VERIFICATION;
  }

  // Delay challenges for medium risk
  if (riskScore >= ENHANCED_PROTECTION_CONFIG.MEDIUM_RISK_THRESHOLD) {
    return ENHANCED_PROTECTION_CONFIG.CHALLENGES.DELAY;
  }

  // Rate limiting for low-medium risk
  return ENHANCED_PROTECTION_CONFIG.CHALLENGES.RATE_LIMIT;
}

/**
 * Execute enhanced protection action
 */
async function executeEnhancedProtectionAction(
  req: Request,
  res: Response,
  next: NextFunction,
  result: EnhancedProtectionResult
): Promise<void> {
  const { action, riskScore, riskLevel, reasons, confidence, incidentId } =
    result;

  // Log the protection decision
  await securityEventLogger.logEvent({
    event: 'enhanced_protection_decision',
    severity: riskLevel,
    timestamp: new Date(),
    source: 'enhanced_protection',
    ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
    userId: (req as any).user?.id,
    details: {
      action,
      riskScore,
      riskLevel,
      confidence,
      reasons,
      recommendations: result.recommendations,
      incidentId,
      threatIntel: result.threatIntelligence,
      behavioral: result.behavioralAnalysis,
      ml: result.mlAnalysis,
      device: result.deviceAnalysis,
    },
  });

  // Execute based on action
  switch (action) {
    case ENHANCED_PROTECTION_CONFIG.ACTIONS.ALLOW:
      return next();

    case ENHANCED_PROTECTION_CONFIG.ACTIONS.MONITOR:
      (req as any).monitoringRequired = true;
      return next();

    case ENHANCED_PROTECTION_CONFIG.ACTIONS.CHALLENGE_EASY:
    case ENHANCED_PROTECTION_CONFIG.ACTIONS.CHALLENGE_MEDIUM:
    case ENHANCED_PROTECTION_CONFIG.ACTIONS.CHALLENGE_HARD:
      return await sendEnhancedChallenge(req, res, result);

    case ENHANCED_PROTECTION_CONFIG.ACTIONS.BLOCK_TEMPORARY:
    case ENHANCED_PROTECTION_CONFIG.ACTIONS.BLOCK_PERMANENT:
      return await sendEnhancedBlock(req, res, result);

    default:
      console.warn(`[EnhancedProtection] Unknown action: ${action}`);
      return next();
  }
}

/**
 * Send enhanced challenge response
 */
async function sendEnhancedChallenge(
  req: Request,
  res: Response,
  result: EnhancedProtectionResult
): Promise<void> {
  const { challengeType, riskScore, reasons, incidentId } = result;

  // Generate appropriate challenge based on type
  let challengeData: any = {};

  switch (challengeType) {
    case ENHANCED_PROTECTION_CONFIG.CHALLENGES.BEHAVIORAL:
      challengeData = generateBehavioralChallenge();
      break;
    case ENHANCED_PROTECTION_CONFIG.CHALLENGES.CAPTCHA:
      challengeData = generateCaptchaChallenge(riskScore);
      break;
    case ENHANCED_PROTECTION_CONFIG.CHALLENGES.DEVICE_VERIFICATION:
      challengeData = generateDeviceVerificationChallenge();
      break;
    default:
      const safeChallengeType = challengeType || 'standard';
      challengeData = generateStandardChallenge(safeChallengeType, riskScore);
  }

  res.status(403).json({
    error: 'Security verification required',
    challenge: {
      type: challengeType || 'standard',
      difficulty: getChallengeDifficulty(riskScore),
      data: challengeData,
      reasons: reasons.slice(0, 2), // Show top 2 reasons
      incidentId,
      instructions: getEnhancedChallengeInstructions(
        challengeType || 'standard'
      ),
    },
    retryAfter: getChallengeRetryAfter(challengeType || 'standard', riskScore),
  });
}

/**
 * Send enhanced block response
 */
async function sendEnhancedBlock(
  req: Request,
  res: Response,
  result: EnhancedProtectionResult
): Promise<void> {
  const {
    riskScore,
    reasons,
    recommendations,
    incidentId,
    threatIntelligence,
  } = result;

  // Send security alert for blocked request
  await securityAlertManager.sendAlert({
    type: 'security' as const,
    severity: 'critical' as const,
    title: 'Advanced Threat Blocked',
    message: `Request blocked with risk score ${riskScore}/100 using enhanced protection`,
    details: {
      reasons,
      recommendations,
      threatIntelligence,
      incidentId,
      ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
      userAgent: req.headers['user-agent'] || 'unknown',
      timestamp: new Date().toISOString(),
    },
    metadata: {
      category: 'enhanced_protection',
      tags: ['blocked', 'critical_risk', 'advanced_threat'],
    },
  });

  // Report malicious IP if threat intelligence indicates
  if (threatIntelligence && threatIntelligence.riskScore > 80) {
    await threatIntelligenceService.reportMaliciousIP(
      threatIntelligence.ipAddress,
      ['automated', 'suspicious'],
      `Blocked by enhanced protection system - risk score: ${threatIntelligence.riskScore}`
    );
  }

  res.status(403).json({
    error: 'Access denied - Security threat detected',
    message: 'Your request has been blocked due to advanced security analysis',
    riskScore,
    reasons: reasons.slice(0, 3), // Show top 3 reasons
    recommendations: recommendations.slice(0, 3),
    supportUrl: '/support/security',
    incidentId,
    retryAfter: 3600, // 1 hour
    additionalInfo: {
      threatLevel: result.riskLevel,
      confidence: result.confidence,
      nextSteps: [
        'Contact support if you believe this is an error',
        'Verify your network connection is secure',
        'Check for malware on your device',
      ],
    },
  });
}

/**
 * Generate behavioral challenge
 */
function generateBehavioralChallenge(): any {
  return {
    type: 'behavioral_verification',
    instructions: [
      'Please move your mouse in a natural pattern',
      'Type a few sentences naturally',
      'Complete simple touch gestures if on mobile',
    ],
    duration: 30000, // 30 seconds
    requiredActions: ['mouse_movement', 'keystrokes', 'natural_timing'],
  };
}

/**
 * Generate CAPTCHA challenge
 */
function generateCaptchaChallenge(riskScore: number): any {
  const difficulty =
    riskScore > 80 ? 'hard' : riskScore > 60 ? 'medium' : 'easy';

  return {
    type: 'captcha',
    difficulty,
    siteKey: process.env.RECAPTCHA_SITE_KEY,
    challengeType: riskScore > 70 ? 'invisible' : 'checkbox',
    expectedDuration:
      difficulty === 'hard' ? 60000 : difficulty === 'medium' ? 30000 : 15000,
  };
}

/**
 * Generate device verification challenge
 */
function generateDeviceVerificationChallenge(): any {
  return {
    type: 'device_verification',
    methods: ['sms', 'email', 'authenticator'],
    verificationCode: {
      length: 6,
      expiresIn: 300000, // 5 minutes
      maxAttempts: 3,
    },
    trustedDeviceOption: true,
  };
}

/**
 * Generate standard challenge
 */
function generateStandardChallenge(
  challengeType: string,
  riskScore: number
): any {
  switch (challengeType) {
    case ENHANCED_PROTECTION_CONFIG.CHALLENGES.DELAY:
      return {
        type: 'delay',
        duration: riskScore > 70 ? 10000 : riskScore > 50 ? 5000 : 2000, // 10s, 5s, or 2s
        message: 'Please wait while we verify your request...',
        progressBar: true,
      };

    case ENHANCED_PROTECTION_CONFIG.CHALLENGES.RATE_LIMIT:
      return {
        type: 'rate_limit',
        maxRequests: riskScore > 70 ? 1 : riskScore > 50 ? 3 : 5,
        windowMinutes: 1,
        message: 'Too many requests. Please slow down.',
      };

    default:
      return {
        type: 'standard',
        message: 'Please complete the verification to continue.',
      };
  }
}

/**
 * Get challenge difficulty
 */
function getChallengeDifficulty(riskScore: number): string {
  if (riskScore > 80) return 'hard';
  if (riskScore > 60) return 'medium';
  return 'easy';
}

/**
 * Get challenge retry after time
 */
function getChallengeRetryAfter(
  challengeType: string,
  riskScore: number
): number {
  const baseTimes = {
    captcha: 30,
    behavioral: 60,
    device_verification: 300,
    delay: 0,
    rate_limit: 60,
  };

  const base = (baseTimes as Record<string, number>)[challengeType] || 30;
  const multiplier = riskScore > 80 ? 2 : riskScore > 60 ? 1.5 : 1;

  return Math.round(base * multiplier);
}

/**
 * Get enhanced challenge instructions
 */
function getEnhancedChallengeInstructions(challengeType: string): string {
  const instructions: Record<string, string> = {
    behavioral:
      'Complete natural human interactions to verify you are not automated',
    captcha: 'Complete the CAPTCHA challenge to continue',
    device_verification: 'Verify your identity using a secondary method',
    delay: 'Please wait while we process your request',
    rate_limit: 'Reduce your request frequency and try again',
  };

  return (
    (instructions as any)[challengeType] ||
    'Complete the security verification to continue'
  );
}

/**
 * Verify enhanced challenge response
 */
export async function verifyEnhancedChallengeResponse(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const { challengeResponse, sessionId, incidentId } = req.body;

    if (!challengeResponse || !sessionId) {
      res.status(400).json({
        error: 'Missing challenge response data',
      });
      return;
    }

    // Verify based on challenge type
    const isValid = await verifyEnhancedChallenge(challengeResponse, sessionId);

    if (isValid) {
      // Challenge passed
      (req as any).challengePassed = true;
      (req as any).incidentId = incidentId;

      // Log successful verification
      await securityEventLogger.logEvent({
        event: 'enhanced_challenge_passed',
        severity: 'low',
        timestamp: new Date(),
        source: 'enhanced_challenge_verification',
        ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
        userId: (req as any).user?.id,
        details: {
          challengeType: challengeResponse.type,
          sessionId,
          incidentId,
        },
      });

      return next();
    } else {
      // Challenge failed
      await securityEventLogger.logEvent({
        event: 'enhanced_challenge_failed',
        severity: 'medium',
        timestamp: new Date(),
        source: 'enhanced_challenge_verification',
        ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
        userId: (req as any).user?.id,
        details: {
          challengeType: challengeResponse.type,
          sessionId,
          incidentId,
        },
      });

      res.status(403).json({
        error: 'Challenge verification failed',
        retryAfter: 300, // 5 minutes
      });
      return;
    }
  } catch (error) {
    console.error('[EnhancedChallengeVerification] Error:', error);
    res.status(500).json({
      error: 'Challenge verification error',
    });
    return;
  }
}

/**
 * Verify enhanced challenge based on type
 */
async function verifyEnhancedChallenge(
  challengeResponse: any,
  sessionId: string
): Promise<boolean> {
  try {
    const { type } = challengeResponse;

    switch (type) {
      case 'captcha':
        return verifyCaptchaChallenge(challengeResponse);

      case 'behavioral':
        return verifyBehavioralChallenge(challengeResponse);

      case 'device_verification':
        return verifyDeviceChallenge(challengeResponse);

      case 'delay':
        return verifyDelayChallenge(challengeResponse);

      case 'rate_limit':
        return verifyRateLimitChallenge(challengeResponse);

      default:
        // Standard verification for unknown types
        return (
          challengeResponse.completed === true ||
          challengeResponse.acknowledged === true
        );
    }
  } catch (error) {
    console.error(
      '[EnhancedChallengeVerification] Verification failed:',
      error
    );
    return false;
  }
}

/**
 * Verify CAPTCHA challenge
 */
async function verifyCaptchaChallenge(response: any): Promise<boolean> {
  // This would integrate with actual CAPTCHA verification service
  // For now, validate token format and basic checks
  return (
    response.token && response.token.length > 20 && response.completed === true
  );
}

/**
 * Verify behavioral challenge
 */
async function verifyBehavioralChallenge(response: any): Promise<boolean> {
  // Verify behavioral data shows human patterns
  if (!response.behavioralData) return false;

  const { behavioralScore, isHuman, confidence } = response.behavioralData;

  // Must show improvement in human behavior
  return isHuman === true && behavioralScore > 60 && confidence > 0.7;
}

/**
 * Verify device verification challenge
 */
async function verifyDeviceChallenge(response: any): Promise<boolean> {
  // Verify verification code
  return response.verificationCode && response.verified === true;
}

/**
 * Verify delay challenge
 */
async function verifyDelayChallenge(response: any): Promise<boolean> {
  // Verify minimum delay was observed
  const minimumDelay = response.minimumDelay || 2000;
  const actualDelay = response.actualDelay || 0;

  return actualDelay >= minimumDelay * 0.8; // Allow 20% tolerance
}

/**
 * Verify rate limit challenge
 */
async function verifyRateLimitChallenge(response: any): Promise<boolean> {
  return (
    response.acknowledged === true && response.complianceConfirmed === true
  );
}

/**
 * Utility functions
 */
function shouldApplyProtection(req: Request): boolean {
  // Skip for health checks and monitoring endpoints
  const skipPaths = [
    '/health',
    '/api/monitoring',
    '/api/protection',
    '/metrics',
    '/favicon.ico',
  ];

  return !skipPaths.some(path => req.path.startsWith(path));
}

function getMaxThreatLevel(
  current: 'low' | 'medium' | 'high' | 'critical',
  newLevel: 'low' | 'medium' | 'high' | 'critical'
): 'low' | 'medium' | 'high' | 'critical' {
  const levels: ('low' | 'medium' | 'high' | 'critical')[] = [
    'low',
    'medium',
    'high',
    'critical',
  ];
  const currentIndex = levels.indexOf(current);
  const newIndex = levels.indexOf(newLevel);

  return newIndex > currentIndex ? newLevel : current;
}

function getRiskLevel(
  riskScore: number
): 'low' | 'medium' | 'high' | 'critical' {
  if (riskScore >= ENHANCED_PROTECTION_CONFIG.CRITICAL_RISK_THRESHOLD)
    return 'critical';
  if (riskScore >= ENHANCED_PROTECTION_CONFIG.HIGH_RISK_THRESHOLD)
    return 'high';
  if (riskScore >= ENHANCED_PROTECTION_CONFIG.MEDIUM_RISK_THRESHOLD)
    return 'medium';
  return 'low';
}

/**
 * Get enhanced protection statistics
 */
export async function getEnhancedProtectionStats(): Promise<any> {
  try {
    const threatIntelMetrics = threatIntelligenceService.getMetrics();
    const mlStats = mlAnomalyDetector.getModelStats();

    return {
      threatIntelligence: threatIntelMetrics,
      mlModel: mlStats,
      timestamp: new Date(),
      config: {
        thresholds: {
          critical: ENHANCED_PROTECTION_CONFIG.CRITICAL_RISK_THRESHOLD,
          high: ENHANCED_PROTECTION_CONFIG.HIGH_RISK_THRESHOLD,
          medium: ENHANCED_PROTECTION_CONFIG.MEDIUM_RISK_THRESHOLD,
          low: ENHANCED_PROTECTION_CONFIG.LOW_RISK_THRESHOLD,
        },
        weights: ENHANCED_PROTECTION_CONFIG.WEIGHTS,
        features: {
          threatIntelligence: ENHANCED_PROTECTION_CONFIG.THREAT_INTELLIGENCE,
          behavioralAnalysis: ENHANCED_PROTECTION_CONFIG.BEHAVIORAL_ANALYSIS,
          advancedML: ENHANCED_PROTECTION_CONFIG.ADVANCED_ML,
          realTimeUpdates: ENHANCED_PROTECTION_CONFIG.REAL_TIME_UPDATES,
        },
      },
    };
  } catch (error) {
    console.error('[EnhancedProtectionStats] Error:', error);
    throw error;
  }
}

export { EnhancedProtectionResult, ENHANCED_PROTECTION_CONFIG };
