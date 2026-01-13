/**
 * Access Control & Redaction Module
 *
 * SINGLE SOURCE OF TRUTH for:
 * 1. Entitlement decisions (allowed/not allowed, redaction mode, credit charging)
 * 2. Redaction as final step in pipeline
 *
 * Policy (MVP):
 * - Free quota remaining (0 < free_remaining <= 2) AND credits = 0:
 *   → Allow extract, return REDACTED output, do not charge credits
 * - Free quota exhausted (free_remaining = 0) AND credits = 0:
 *   → BLOCK, return 402 PAYMENT_REQUIRED with CREDITS_REQUIRED code
 * - Credits > 0:
 *   → Allow extract, return FULL output, deduct 1 credit
 *
 * IMPORTANT: Paid users should ALWAYS get full output, never redacted.
 */

import type { Request } from 'express';
import type { FrontendMetadataResponse } from './extraction-helpers';
import { storage } from '../storage/index';
import { getSessionId, normalizeEmail } from './extraction-helpers';
import { isDatabaseConnected } from '../db';
import { trialUsages } from '@shared/schema';
import { eq } from 'drizzle-orm';
import { getDatabase } from '../db';
import {
  getClientUsage,
  verifyClientToken,
  generateClientToken,
} from './free-quota-enforcement';

/**
 * Access Decision Type
 * Single source of truth for all access control decisions
 */
export type AccessDecision = {
  allowed: boolean;
  mode: 'redacted' | 'full';
  chargeCredits: boolean;
  reason: 'FREE_REDACTED' | 'PAID_FULL' | 'BLOCKED_NO_CREDITS' | 'TRIAL_FULL';
  creditsRemaining: number;
  freeQuotaUsed: number;
  userId?: string | null;
};

/**
 * Entitlement Resolver
 *
 * Returns a single AccessDecision for the current request.
 * All routes must call this function - no scattered if/else logic.
 */
export async function resolveAccessDecision(
  req: Request
): Promise<AccessDecision> {
  const sessionId = getSessionId(req);
  const userId = (req as any).user?.id as string | undefined;
  const trialEmail = req.body?.trial_email
    ? normalizeEmail(req.body?.trial_email)
    : null;
  const creditCost = 1;

  const isDev = process.env.NODE_ENV === 'development';

  if (isDev) {
    console.log('[Access] Development mode: bypassing all restrictions');
    return {
      allowed: true,
      mode: 'full',
      chargeCredits: false,
      reason: 'PAID_FULL',
      creditsRemaining: 999999,
      freeQuotaUsed: 0,
      userId: userId || null,
    };
  }

  // Case 1: Trial user
  if (trialEmail) {
    let trialUses = 0;
    if (isDatabaseConnected()) {
      const dbClient = getDatabase();
      const result = await dbClient
        .select({ uses: trialUsages.uses })
        .from(trialUsages)
        .where(eq(trialUsages.email, trialEmail))
        .limit(1);
      trialUses = result[0]?.uses || 0;
    } else {
      const usage = await storage.getTrialUsageByEmail(trialEmail);
      trialUses = usage?.uses || 0;
    }

    if (trialUses >= 2) {
      return {
        allowed: false,
        mode: 'redacted',
        chargeCredits: false,
        reason: 'BLOCKED_NO_CREDITS',
        creditsRemaining: 0,
        freeQuotaUsed: 2,
        userId: null,
      };
    }

    return {
      allowed: true,
      mode: 'full',
      chargeCredits: false,
      reason: 'TRIAL_FULL',
      creditsRemaining: 0,
      freeQuotaUsed: trialUses,
      userId: null,
    };
  }

  // Case 2: Authenticated user
  if (userId) {
    const namespaced = `images_mvp:user:${userId}`;
    const balance = await storage.getOrCreateCreditBalance(namespaced, userId);
    const credits = balance?.credits ?? 0;

    if (credits >= creditCost) {
      return {
        allowed: true,
        mode: 'full',
        chargeCredits: true,
        reason: 'PAID_FULL',
        creditsRemaining: credits - creditCost,
        freeQuotaUsed: 0,
        userId,
      };
    }

    return {
      allowed: false,
      mode: 'redacted',
      chargeCredits: false,
      reason: 'BLOCKED_NO_CREDITS',
      creditsRemaining: 0,
      freeQuotaUsed: 0,
      userId,
    };
  }

  // Case 3: Anonymous user
  let clientToken = req.cookies?.metaextract_client;
  let decoded = verifyClientToken(clientToken);
  let isNewToken = false;

  if (!decoded) {
    clientToken = generateClientToken();
    decoded = verifyClientToken(clientToken);
    isNewToken = true;
  }

  if (!decoded) {
    return {
      allowed: false,
      mode: 'redacted',
      chargeCredits: false,
      reason: 'BLOCKED_NO_CREDITS',
      creditsRemaining: 0,
      freeQuotaUsed: 0,
      userId: null,
    };
  }

  const usage = await getClientUsage(decoded.clientId);
  const currentCount = usage?.freeUsed || 0;

  if (currentCount >= 2) {
    return {
      allowed: false,
      mode: 'redacted',
      chargeCredits: false,
      reason: 'BLOCKED_NO_CREDITS',
      creditsRemaining: 0,
      freeQuotaUsed: 2,
      userId: null,
    };
  }

  return {
    allowed: true,
    mode: 'redacted',
    chargeCredits: false,
    reason: 'FREE_REDACTED',
    creditsRemaining: 0,
    freeQuotaUsed: currentCount,
    userId: null,
  };
}

/**
 * Centralized Redaction Function
 *
 * Applies redaction as the FINAL step in the pipeline.
 * Backend should always produce full normalized report internally,
 * then call this function before sending to client.
 */
export function redactMetadata(
  report: FrontendMetadataResponse,
  mode: 'redacted' | 'full'
): FrontendMetadataResponse {
  if (mode === 'full') {
    return report;
  }

  const metadata = report as any;

  // GPS: round coordinates to 2 decimals, remove precise map link
  if (metadata.gps && typeof metadata.gps === 'object') {
    const lat = Number(metadata.gps.latitude ?? NaN);
    const lon = Number(metadata.gps.longitude ?? NaN);
    if (Number.isFinite(lat) && Number.isFinite(lon)) {
      metadata.gps.latitude = Math.round(lat * 100) / 100;
      metadata.gps.longitude = Math.round(lon * 100) / 100;
      if (metadata.gps.google_maps_url) delete metadata.gps.google_maps_url;
    } else {
      metadata.gps = null;
    }
  }

  // Burned metadata: keep presence and confidence, redact text and parsed precise location
  if (metadata.burned_metadata) {
    const bm = metadata.burned_metadata;
    bm.extracted_text = null;
    if (bm.parsed_data) {
      if (bm.parsed_data.gps) delete bm.parsed_data.gps;
      if (bm.parsed_data.plus_code) delete bm.parsed_data.plus_code;
      if (bm.parsed_data.location) {
        const loc = bm.parsed_data.location as any;
        const coarse: any = {};
        if (loc.city) coarse.city = loc.city;
        if (loc.state) coarse.state = loc.state;
        if (loc.country) coarse.country = loc.country;
        bm.parsed_data.location = Object.keys(coarse).length ? coarse : null;
      }
    }
  }

  // Extended attributes: keep available/count, redact attribute values
  if (metadata.extended_attributes && metadata.extended_attributes.attributes) {
    const attrs = metadata.extended_attributes.attributes;
    const redacted: Record<string, any> = {};
    Object.keys(attrs).forEach(k => (redacted[k] = null));
    metadata.extended_attributes.attributes = redacted;
  }

  // Filesystem: remove owner and sensitive internals
  if (metadata.filesystem && typeof metadata.filesystem === 'object') {
    [
      'owner',
      'owner_uid',
      'group',
      'group_gid',
      'inode',
      'device',
      'permissions_octal',
      'permissions_human',
      'hard_links',
    ].forEach(k => delete metadata.filesystem[k]);
  }

  // Thumbnail: keep presence + basic attrs only
  if (metadata.thumbnail && typeof metadata.thumbnail === 'object') {
    const t = metadata.thumbnail as any;
    metadata.thumbnail = {
      has_embedded: !!t.has_embedded,
      width: t.width || null,
      height: t.height || null,
    } as any;
  }

  // Perceptual hashes: keep only basic hashes
  if (
    metadata.perceptual_hashes &&
    typeof metadata.perceptual_hashes === 'object'
  ) {
    const p = metadata.perceptual_hashes as any;
    metadata.perceptual_hashes = {
      phash: p.phash || null,
      dhash: p.dhash || null,
      ahash: p.ahash || null,
      whash: p.whash || null,
    } as any;
  }

  // Enterprise-only bulky buckets: hide to avoid leaking heavy internals
  [
    'drone_telemetry',
    'emerging_technology',
    'synthetic_media_analysis',
    'blockchain_provenance',
  ].forEach(k => {
    if (metadata[k]) metadata[k] = null;
  });

  return report;
}

/**
 * Log access decision for observability
 */
export function logAccessDecision(
  req: Request,
  decision: AccessDecision,
  sessionId: string | null
): void {
  console.log('[Access] Decision:', {
    path: req.path,
    sessionId: sessionId || 'none',
    userId: decision.userId || 'anonymous',
    allowed: decision.allowed,
    mode: decision.mode,
    chargeCredits: decision.chargeCredits,
    reason: decision.reason,
    creditsRemaining: decision.creditsRemaining,
    freeQuotaUsed: decision.freeQuotaUsed,
    timestamp: new Date().toISOString(),
  });
}
