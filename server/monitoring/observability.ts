/**
 * Structured Observability Logging
 *
 * Logs key decisions for debugging pricing complaints and audit trails:
 * - Entitlement decisions
 * - Redaction mode applied
 * - Credit charge decisions
 * - Extractor modules run and timing
 */

import type { Request } from 'express';
import type { AccessDecision } from '../utils/access-control';

export interface ObservabilityLog {
  timestamp: string;
  requestId: string;
  sessionId: string | null;
  userId: string | null;
  ip: string | null;
  userAgent: string | null;
  path: string;
  method: string;
  entitlement: {
    decision: AccessDecision;
    reason: string;
    freeQuotaUsed: number;
    creditsRemaining: number;
  };
  redaction: {
    mode: 'redacted' | 'full';
    fieldsRedacted: string[];
    appliedAt: string;
  };
  billing: {
    chargeCredits: boolean;
    creditsCharged: number;
    cost: number;
    packType?: string;
  };
  extraction: {
    modules: string[];
    duration: number;
    fieldsExtracted: number;
    success: boolean;
    error?: string;
  };
}

/**
 * Generate unique request ID
 */
let requestCounter = 0;
export function generateRequestId(): string {
  return `req_${Date.now()}_${++requestCounter}`;
}

/**
 * Get session ID from request
 */
function getSessionId(req: Request): string | null {
  return (
    (req as any).sessionId ||
    req.cookies?.metaextract_session_id ||
    (req.query?.sessionId as string) ||
    null
  );
}

/**
 * Log entitlement decision
 */
export function logEntitlementDecision(
  req: Request,
  decision: AccessDecision
): void {
  const sessionId = getSessionId(req);
  const ip = req.ip || req.socket.remoteAddress || null;
  const userAgent = req.headers['user-agent'] || null;
  const requestId = (req as any).requestId || generateRequestId();

  console.log('[OBSERVE] Entitlement Decision:', {
    timestamp: new Date().toISOString(),
    requestId,
    sessionId: sessionId || 'anonymous',
    userId: decision.userId || null,
    ip: ip ? ip.replace(/::ffff:/, '') : null,
    userAgent: userAgent ? userAgent.substring(0, 100) : null,
    path: req.path,
    method: req.method,
    entitlement: {
      allowed: decision.allowed,
      mode: decision.mode,
      reason: decision.reason,
      chargeCredits: decision.chargeCredits,
      freeQuotaUsed: decision.freeQuotaUsed,
      creditsRemaining: decision.creditsRemaining,
    },
  });
}

/**
 * Log redaction application
 */
export function logRedactionApplied(
  req: Request,
  mode: 'redacted' | 'full',
  fieldsRedacted: string[] = []
): void {
  const requestId = (req as any).requestId || generateRequestId();

  console.log('[OBSERVE] Redaction Applied:', {
    timestamp: new Date().toISOString(),
    requestId,
    path: req.path,
    method: req.method,
    redaction: {
      mode,
      fieldsRedacted,
      appliedAt: new Date().toISOString(),
    },
  });
}

/**
 * Log credit charge
 */
export function logCreditCharge(
  req: Request,
  creditsCharged: number,
  cost: number,
  packType?: string
): void {
  const sessionId = getSessionId(req);
  const requestId = (req as any).requestId || generateRequestId();

  console.log('[OBSERVE] Credit Charge:', {
    timestamp: new Date().toISOString(),
    requestId,
    sessionId: sessionId || 'anonymous',
    userId: (req as any).user?.id || null,
    path: req.path,
    method: req.method,
    billing: {
      chargeCredits: creditsCharged > 0,
      creditsCharged,
      cost,
      packType,
    },
  });
}

/**
 * Log extraction completion
 */
export function logExtractionComplete(
  req: Request,
  modules: string[],
  duration: number,
  fieldsExtracted: number,
  success: boolean,
  error?: string
): void {
  const sessionId = getSessionId(req);
  const requestId = (req as any).requestId || generateRequestId();

  console.log('[OBSERVE] Extraction Complete:', {
    timestamp: new Date().toISOString(),
    requestId,
    sessionId: sessionId || 'anonymous',
    userId: (req as any).user?.id || null,
    path: req.path,
    method: req.method,
    extraction: {
      modules,
      duration,
      fieldsExtracted,
      success,
      error,
    },
  });
}

/**
 * Log full request lifecycle (call this at the end)
 */
export function logRequestLifecycle(
  req: Request,
  entitlement: AccessDecision,
  redactionMode: 'redacted' | 'full',
  billing: { creditsCharged: number; cost: number },
  extraction: {
    modules: string[];
    duration: number;
    fieldsExtracted: number;
    success: boolean;
    error?: string;
  }
): void {
  const sessionId = getSessionId(req);
  const ip = req.ip || req.socket.remoteAddress || null;
  const requestId = (req as any).requestId || generateRequestId();

  const logEntry: ObservabilityLog = {
    timestamp: new Date().toISOString(),
    requestId,
    sessionId: sessionId || null,
    userId: entitlement.userId || null,
    ip: ip ? ip.replace(/::ffff:/, '') : null,
    userAgent: req.headers['user-agent'] || null,
    path: req.path,
    method: req.method,
    entitlement: {
      decision: entitlement,
      reason: entitlement.reason,
      freeQuotaUsed: entitlement.freeQuotaUsed,
      creditsRemaining: entitlement.creditsRemaining,
    },
    redaction: {
      mode: redactionMode,
      fieldsRedacted:
        redactionMode === 'redacted'
          ? [
              'gps',
              'burned_metadata',
              'extended_attributes',
              'filesystem',
              'perceptual_hashes',
            ]
          : [],
      appliedAt: new Date().toISOString(),
    },
    billing: {
      chargeCredits: billing.creditsCharged > 0,
      creditsCharged: billing.creditsCharged,
      cost: billing.cost,
    },
    extraction: {
      modules: extraction.modules,
      duration: extraction.duration,
      fieldsExtracted: extraction.fieldsExtracted,
      success: extraction.success,
      error: extraction.error,
    },
  };

  console.log('[OBSERVE] Request Lifecycle:', logEntry);
}
