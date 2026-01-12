/**
 * Browser Fingerprinting for Advanced Abuse Detection
 *
 * Implements comprehensive browser fingerprinting to detect:
 * - Multiple sessions from same device
 * - Cookie clearing attempts
 * - Device fingerprinting evasion
 * - Advanced abuse patterns
 */

import { Request } from 'express';
import crypto from 'crypto';
import { storage } from '../storage/index';
import { securityEventLogger } from './security-events';

// Browser fingerprint components
interface BrowserFingerprint {
  canvas: string;
  webgl: string;
  fonts: string;
  screen: string;
  timezone: string;
  language: string;
  platform: string;
  userAgent: string;
  plugins: string;
  audio: string;
  deviceMemory: number;
  hardwareConcurrency: number;
  cookieEnabled: boolean;
  doNotTrack: string | null;
  touchSupport: boolean;
  maxTouchPoints: number;
}

// Enhanced fingerprint with behavioral data
export interface EnhancedFingerprint extends BrowserFingerprint {
  fingerprintHash: string;
  deviceId: string;
  sessionId: string;
  ipAddress: string;
  timestamp: Date;
  confidence: number;
  anomalies: string[];
}

// Fingerprint analysis results
export interface FingerprintAnalysis {
  isUnique: boolean;
  confidence: number;
  anomalies: string[];
  riskScore: number;
  recommendations: string[];
  similarFingerprints: Array<{
    fingerprintId: string;
    similarity: number;
    lastSeen: Date;
  }>;
}

// Configuration
const FINGERPRINT_CONFIG = {
  // Risk thresholds
  RISK_SCORE_LOW: 30,
  RISK_SCORE_MEDIUM: 60,
  RISK_SCORE_HIGH: 80,

  // Similarity thresholds
  SIMILARITY_THRESHOLD: 0.85,
  HIGH_CONFIDENCE_THRESHOLD: 0.95,

  // Cache settings
  CACHE_TTL_MS: 24 * 60 * 60 * 1000, // 24 hours
  SIMILARITY_CACHE_TTL_MS: 60 * 60 * 1000, // 1 hour
};

/**
 * Generate browser fingerprint from request headers and client data
 */
export async function generateFingerprint(
  req: Request,
  clientData?: Partial<BrowserFingerprint>
): Promise<EnhancedFingerprint> {
  const baseFingerprint: BrowserFingerprint = {
    // Basic browser info
    userAgent: req.headers['user-agent'] || 'unknown',
    platform: getPlatform(req.headers['user-agent']),
    language: req.headers['accept-language']?.split(',')[0] || 'unknown',
    timezone: getTimezone(req.headers),
    cookieEnabled: true, // Default, would be set by client
    doNotTrack: getDoNotTrack(req.headers),

    // Screen info (would come from client)
    screen: clientData?.screen || 'unknown',

    // Canvas fingerprint (would come from client)
    canvas: clientData?.canvas || 'unknown',

    // WebGL fingerprint (would come from client)
    webgl: clientData?.webgl || 'unknown',

    // Audio fingerprint (would come from client)
    audio: clientData?.audio || 'unknown',

    // Font detection (would come from client)
    fonts: clientData?.fonts || 'unknown',

    // Plugin detection (would come from client)
    plugins: clientData?.plugins || 'unknown',

    // Hardware info (would come from client)
    deviceMemory: clientData?.deviceMemory || 0,
    hardwareConcurrency: clientData?.hardwareConcurrency || 0,
    maxTouchPoints: clientData?.maxTouchPoints || 0,
    touchSupport: clientData?.touchSupport || false,
  };

  // Generate enhanced fingerprint
  const enhanced: EnhancedFingerprint = {
    ...baseFingerprint,
    fingerprintHash: generateFingerprintHash(baseFingerprint),
    deviceId: generateDeviceId(baseFingerprint),
    sessionId: generateSessionId(req),
    ipAddress: req.ip || req.connection.remoteAddress || 'unknown',
    timestamp: new Date(),
    confidence: calculateConfidence(baseFingerprint, clientData),
    anomalies: detectAnomalies(baseFingerprint, req),
  };

  return enhanced;
}

/**
 * Analyze fingerprint for suspicious patterns
 */
export async function analyzeFingerprint(
  fingerprint: EnhancedFingerprint
): Promise<FingerprintAnalysis> {
  const anomalies: string[] = [];
  let riskScore = 0;

  // Check for common evasion techniques
  if (fingerprint.userAgent.includes('HeadlessChrome')) {
    anomalies.push('Headless browser detected');
    riskScore += 30;
  }

  if (fingerprint.doNotTrack === '1') {
    anomalies.push('Do Not Track enabled');
    riskScore += 10;
  }

  if (!fingerprint.cookieEnabled) {
    anomalies.push('Cookies disabled');
    riskScore += 20;
  }

  // Check for automation indicators
  if (fingerprint.plugins === 'none' && fingerprint.fonts === 'none') {
    anomalies.push('Minimal browser fingerprint - possible automation');
    riskScore += 25;
  }

  // Check for inconsistencies
  if (
    fingerprint.userAgent.includes('Mobile') &&
    fingerprint.maxTouchPoints === 0
  ) {
    anomalies.push('Mobile UA but no touch support');
    riskScore += 15;
  }

  // Check for similar fingerprints in database
  const similarFingerprints = await findSimilarFingerprints(fingerprint);

  // Calculate confidence
  let confidence = 1.0;
  if (anomalies.length > 0) confidence -= anomalies.length * 0.1;
  if (similarFingerprints.length > 0) confidence -= 0.2;
  confidence = Math.max(0.1, Math.min(1.0, confidence));

  // Generate recommendations
  const recommendations = generateRecommendations(
    anomalies,
    similarFingerprints
  );

  return {
    isUnique: similarFingerprints.length === 0,
    confidence,
    anomalies,
    riskScore: Math.min(100, riskScore),
    recommendations,
    similarFingerprints: similarFingerprints.slice(0, 5), // Top 5
  };
}

/**
 * Track fingerprint across sessions to detect abuse
 */
export async function trackFingerprint(
  fingerprint: EnhancedFingerprint,
  userId?: string
): Promise<{
  isNewDevice: boolean;
  previousSessions: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  action: 'allow' | 'challenge' | 'block';
}> {
  // Store fingerprint in database
  await storeFingerprint(fingerprint, userId);

  // Analyze for abuse patterns
  const analysis = await analyzeFingerprint(fingerprint);

  // Determine risk level and action
  let riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';
  let action: 'allow' | 'challenge' | 'block' = 'allow';

  if (analysis.riskScore >= FINGERPRINT_CONFIG.RISK_SCORE_HIGH) {
    riskLevel = 'high';
    action = 'challenge';
  } else if (analysis.riskScore >= FINGERPRINT_CONFIG.RISK_SCORE_MEDIUM) {
    riskLevel = 'medium';
    action = 'challenge';
  } else if (analysis.anomalies.length > 0) {
    riskLevel = 'low';
    action = 'allow'; // But log for monitoring
  }

  // Log security event for tracking
  await securityEventLogger.logEvent({
    event: 'fingerprint_analysis',
    severity: riskLevel,
    timestamp: new Date(),
    source: 'browser_fingerprinting',
    ipAddress: fingerprint.ipAddress,
    userId,
    details: {
      fingerprintId: fingerprint.fingerprintHash,
      riskScore: analysis.riskScore,
      confidence: analysis.confidence,
      anomalies: analysis.anomalies,
      similarDevices: analysis.similarFingerprints.length,
    },
  });

  // Check for multiple sessions from same device
  const previousSessions = await getPreviousSessions(fingerprint.deviceId);
  const isNewDevice = previousSessions === 0;

  return {
    isNewDevice,
    previousSessions,
    riskLevel,
    action,
  };
}

/**
 * Generate fingerprint hash for comparison
 */
function generateFingerprintHash(fingerprint: BrowserFingerprint): string {
  const data = JSON.stringify(fingerprint, Object.keys(fingerprint).sort());
  return crypto.createHash('sha256').update(data).digest('hex');
}

/**
 * Generate device ID from fingerprint
 */
function generateDeviceId(fingerprint: BrowserFingerprint): string {
  // Create a more stable device ID by excluding volatile fields
  const stableData = {
    userAgent: fingerprint.userAgent,
    platform: fingerprint.platform,
    language: fingerprint.language,
    timezone: fingerprint.timezone,
    deviceMemory: fingerprint.deviceMemory,
    hardwareConcurrency: fingerprint.hardwareConcurrency,
  };

  const data = JSON.stringify(stableData, Object.keys(stableData).sort());
  return crypto
    .createHash('sha256')
    .update(data)
    .digest('hex')
    .substring(0, 16);
}

/**
 * Generate session ID from request
 */
function generateSessionId(req: Request): string {
  const sessionCookie = req.cookies?.metaextract_session_id;
  if (sessionCookie) return sessionCookie;

  // Generate new session ID if none exists
  return `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get platform from user agent
 */
function getPlatform(userAgent?: string): string {
  if (!userAgent) return 'unknown';

  if (userAgent.includes('Windows')) return 'Windows';
  if (userAgent.includes('Mac OS')) return 'macOS';
  if (userAgent.includes('Linux')) return 'Linux';
  if (userAgent.includes('Android')) return 'Android';
  if (userAgent.includes('iOS')) return 'iOS';

  return 'unknown';
}

/**
 * Get timezone from headers
 */
function getTimezone(headers: any): string {
  // Would normally get from client-side JavaScript
  // For now, use UTC offset from headers or default
  const dateHeader = headers.date;
  if (dateHeader) {
    const date = new Date(dateHeader);
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  }
  return 'UTC';
}

/**
 * Get Do Not Track status
 */
function getDoNotTrack(headers: any): string | null {
  return headers['dnt'] || null;
}

/**
 * Calculate confidence score
 */
function calculateConfidence(
  fingerprint: BrowserFingerprint,
  clientData?: Partial<BrowserFingerprint>
): number {
  let confidence = 0.5; // Base confidence

  // Increase confidence for detailed fingerprints
  if (clientData?.canvas) confidence += 0.2;
  if (clientData?.webgl) confidence += 0.15;
  if (clientData?.fonts) confidence += 0.1;
  if (clientData?.audio) confidence += 0.1;
  if (clientData?.plugins) confidence += 0.05;

  return Math.min(1.0, confidence);
}

/**
 * Detect anomalies in fingerprint
 */
function detectAnomalies(
  fingerprint: BrowserFingerprint,
  req: Request
): string[] {
  const anomalies: string[] = [];

  // Check for headless browser indicators
  if (fingerprint.userAgent.includes('HeadlessChrome')) {
    anomalies.push('Headless browser detected');
  }

  // Check for minimal fingerprint (possible automation)
  if (fingerprint.plugins === 'none' && fingerprint.fonts === 'none') {
    anomalies.push('Minimal browser fingerprint');
  }

  // Check for inconsistencies
  if (
    fingerprint.userAgent.includes('Mobile') &&
    fingerprint.maxTouchPoints === 0
  ) {
    anomalies.push('Mobile UA but no touch support');
  }

  return anomalies;
}

/**
 * Find similar fingerprints in database
 */
async function findSimilarFingerprints(
  fingerprint: EnhancedFingerprint
): Promise<
  Array<{
    fingerprintId: string;
    similarity: number;
    lastSeen: Date;
  }>
> {
  try {
    // This would query the database for similar fingerprints
    // For now, return mock data
    return [
      {
        fingerprintId: 'mock_fp_1',
        similarity: 0.92,
        lastSeen: new Date(Date.now() - 60 * 60 * 1000), // 1 hour ago
      },
      {
        fingerprintId: 'mock_fp_2',
        similarity: 0.88,
        lastSeen: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      },
    ];
  } catch (error) {
    console.error(
      '[BrowserFingerprint] Error finding similar fingerprints:',
      error
    );
    return [];
  }
}

/**
 * Store fingerprint in database
 */
async function storeFingerprint(
  fingerprint: EnhancedFingerprint,
  userId?: string
): Promise<void> {
  try {
    await storage.storeFingerprint?.({
      id: fingerprint.fingerprintHash,
      deviceId: fingerprint.deviceId,
      sessionId: fingerprint.sessionId,
      userId,
      fingerprintData: fingerprint,
      ipAddress: fingerprint.ipAddress,
      timestamp: fingerprint.timestamp,
      confidence: fingerprint.confidence,
      anomalies: fingerprint.anomalies,
    });
  } catch (error) {
    console.error('[BrowserFingerprint] Error storing fingerprint:', error);
  }
}

/**
 * Get previous sessions for device
 */
async function getPreviousSessions(deviceId: string): Promise<number> {
  try {
    // This would query the database for previous sessions
    // For now, return mock data
    return Math.floor(Math.random() * 10); // 0-10 sessions
  } catch (error) {
    console.error(
      '[BrowserFingerprint] Error getting previous sessions:',
      error
    );
    return 0;
  }
}

/**
 * Generate recommendations based on analysis
 */
function generateRecommendations(
  anomalies: string[],
  similarFingerprints: Array<{
    fingerprintId: string;
    similarity: number;
    lastSeen: Date;
  }>
): string[] {
  const recommendations: string[] = [];

  if (anomalies.length > 0) {
    recommendations.push(
      'Monitor this device for continued anomalous behavior'
    );
  }

  if (similarFingerprints.length > 0) {
    recommendations.push(
      'Multiple similar devices detected - consider rate limiting'
    );
  }

  if (anomalies.includes('Headless browser detected')) {
    recommendations.push('Investigate for automation or bot activity');
  }

  if (anomalies.includes('Minimal browser fingerprint')) {
    recommendations.push('Possible browser fingerprinting evasion attempt');
  }

  return recommendations;
}
