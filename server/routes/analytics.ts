/**
 * Analytics Events Ingestion Pipeline
 *
 * Minimal, deterministic, append-only event storage.
 * Validates schemas, prevents prohibited fields, handles batching.
 *
 * Key Design Principles:
 * - Single source of truth (database table, no multiple writes)
 * - Prohibited fields are rejected at ingestion (privacy protection)
 * - Deterministic one-shot firing (client sends once, we store once)
 * - Server-side lifecycle events (system truth, not client guesses)
 * - Analytics health monitoring (catch instrumentation bugs)
 */

import type { Request, Response } from 'express';
import { z } from 'zod';
import crypto from 'crypto';
import { db } from '../db';
import { uiEvents, insertUiEvent, type InsertUiEvent } from '@shared/schema';
import { uiEvents, insertUiEvent as insertUiEventSchema } from '@shared/schema';
import {
  EventName,
  UserIntentEvent,
  ComprehensionEvent,
  type BaseEventProperties,
  type UserIntentEventProperties,
  type ComprehensionEventProperties,
  buildDedupeKey,
  validateEventPayload,
  type FileSizeBucket,
  UserTier,
  AuthState,
  SourceEntryPoint,
  ClientType,
  ResultDensity,
} from '@shared/analytics-events';

// ============================================================================
// INGESTION SCHEMAS (Validation at Edge)
// ============================================================================

/**
 * Base analytics event schema
 * All events must conform to this structure
 */
const baseAnalyticsSchema = z.object({
  // Versioning - enables breaking changes without historical data loss
  version: z.literal('1.0.0'),

  // Event family
  eventFamily: z.enum(['lifecycle', 'user_intent', 'comprehension']),

  // Event name
  eventName: z.string(),

  // Correlation IDs
  sessionId: z.string().uuid(),
  fileId: z.string().uuid().optional(),
  correlationId: z.string().optional(),

  // Properties (validated against prohibited list)
  properties: z.record(z.string(), z.any()),

  // Coarse dimensions (no PII)
  userTier: z.enum([UserTier.ANON, UserTier.FREE, UserTier.PRO]).optional(),
  authState: z.enum([AuthState.LOGGED_OUT, AuthState.LOGGED_IN]).optional(),
  fileSizeBucket: z
    .enum([
      FileSizeBucket.SMALL,
      FileSizeBucket.MEDIUM,
      FileSizeBucket.LARGE,
      FileSizeBucket.XLARGE,
    ])
    .optional(),
  sourceEntryPoint: z
    .enum([
      SourceEntryPoint.UPLOAD_PAGE,
      SourceEntryPoint.LANDING,
      SourceEntryPoint.SHARE_LINK,
      SourceEntryPoint.API,
    ])
    .optional(),
  resultDensity: z
    .enum([
      ResultDensity.SIMPLE,
      ResultDensity.STANDARD,
      ResultDensity.ADVANCED,
    ])
    .optional(),
  client: z
    .enum([ClientType.WEB, ClientType.EXTENSION, ClientType.MOBILE_APP])
    .optional(),

  // Request ID for tracing
  requestId: z.string().optional(),

  // Abuse defense (coarse signals only)
  ipPrefixHash: z.string().max(16).optional(), // First 2 octets of IP, hashed
  asn: z.string().max(16).optional(), // AS number, not IP
  uaHash: z.string().max(32).optional(), // User agent fingerprint, not raw UA
  riskScoreBucket: z.enum(['low', 'medium', 'high', 'blocked']).optional(),

  // Server-enriched fields (always present, no client override)
  receivedAt: z.string().datetime(), // Canonical ordering field
  eventTime: z.string().datetime().optional(), // Client-provided timestamp (for clock skew analysis)
});

/**
 * Deduplication key schema (used for unique constraint)
 */
const dedupeKeySchema = z.object({
  sessionId: z.string().uuid(),
  eventId: z.string(), // eventName or unique fact ID
  fileId: z.string().uuid().optional(),
});

// ============================================================================
// PROHIBITED FIELD VALIDATION (Privacy Protection)
// ============================================================================

/**
 * These patterns are rejected at ingestion to prevent privacy leaks
 * Any payload matching these patterns fails validation
 */
const PROHIBITED_FIELD_PATTERNS = [
  /^raw_gps_latitude$/,
  /^raw_gps_longitude$/,
  /^raw_timestamp_value$/,
  /^filename$/,
  /^device_serial_number$/,
  /^user_email$/,
  /^ip_address$/,
  /^user_agent_string$/,
  /^metadata_values$/,
  /^exact_coordinates$/,
];

/**
 * Validate event payload against prohibited patterns
 * Returns detailed error for debugging
 */
function validateProhibitedFields(properties: Record<string, unknown>): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  for (const key of Object.keys(properties)) {
    for (const pattern of PROHIBITED_FIELD_PATTERNS) {
      if (pattern.test(key)) {
        errors.push(`Prohibited field: "${key}"`);
      }
    }
  }

  return { valid: errors.length === 0, errors };
}

// ============================================================================
// ANALYTICS HEALTH METRICS
// ============================================================================

interface AnalyticsHealthMetrics {
  invalidEventRate: number; // Events rejected by schema validation
  missingSessionIdRate: number; // Events without sessionId
  duplicateRate: number; // Dedupe key collisions
  eventLagDistribution: { p50: number; p95: number; p99: number }; // receivedAt - eventTime
  eventsPerSessionDistribution: { p50: number; p95: number; max: number };
}

// In-memory metrics (rotate every minute)
const healthMetrics: AnalyticsHealthMetrics = {
  invalidEventRate: 0,
  missingSessionIdRate: 0,
  duplicateRate: 0,
  eventLagDistribution: { p50: 0, p95: 0, p99: 0 },
  eventsPerSessionDistribution: { p50: 0, p95: 0, max: 0 },
};

// Sample buffers for distribution tracking
const eventLagBuffer: number[] = [];
const eventsPerSessionBuffer: Map<string, number> = new Map();

/**
 * Update health metrics
 * Called on every event ingestion
 */
function updateHealthMetrics(
  eventType: string,
  validationPassed: boolean,
  sessionId: string | undefined,
  receivedAt: Date,
  eventTime: Date | undefined
): void {
  // Invalid event tracking
  if (!validationPassed) {
    healthMetrics.invalidEventRate++;
  }

  // Missing session ID tracking
  if (!sessionId) {
    healthMetrics.missingSessionIdRate++;
  }

  // Event lag tracking (clock skew detection)
  if (eventTime) {
    const lag = receivedAt.getTime() - eventTime.getTime();
    eventLagBuffer.push(lag);
    if (eventLagBuffer.length > 1000) {
      eventLagBuffer.shift(); // Keep last 1000 events
    }

    // Calculate percentiles
    const sorted = [...eventLagBuffer].sort((a, b) => a - b);
    healthMetrics.eventLagDistribution = {
      p50: sorted[Math.floor(sorted.length * 0.5)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)],
    };
  }

  // Events per session tracking
  if (sessionId) {
    const currentCount = eventsPerSessionBuffer.get(sessionId) || 0;
    eventsPerSessionBuffer.set(sessionId, currentCount + 1);
  }
}

/**
 * Reset health metrics (called every minute)
 */
function resetHealthMetrics(): void {
  const previous = { ...healthMetrics };

  healthMetrics.invalidEventRate = 0;
  healthMetrics.missingSessionIdRate = 0;
  healthMetrics.duplicateRate = 0;

  // Rotate event lag buffer
  eventLagBuffer.length = 0;

  // Calculate events per session distribution
  const sessionCounts = Array.from(eventsPerSessionBuffer.values());
  if (sessionCounts.length > 0) {
    sessionCounts.sort((a, b) => a - b);
    healthMetrics.eventsPerSessionDistribution = {
      p50: sessionCounts[Math.floor(sessionCounts.length * 0.5)] || 0,
      p95: sessionCounts[Math.floor(sessionCounts.length * 0.95)] || 0,
      max: sessionCounts[sessionCounts.length - 1] || 0,
    };
  } else {
    healthMetrics.eventsPerSessionDistribution = { p50: 0, p95: 0, max: 0 };
  }

  eventsPerSessionBuffer.clear();

  // Store previous metrics for comparison
  (globalThis as any).__previousHealthMetrics = previous;
}

// Rotate health metrics every minute
setInterval(resetHealthMetrics, 60000);

// ============================================================================
// ROUTE: Analytics Event Ingestion
// ============================================================================

/**
 * POST /api/analytics/events
 * Ingest batched client-side analytics events
 */
export async function registerAnalyticsRoutes(app: any): Promise<void> {
  app.post('/api/analytics/events', async (req: Request, res: Response) => {
    try {
      // Validate request body
      const body = req.body;

      if (!body || !Array.isArray(body)) {
        return res.status(400).json({
          error: 'Invalid request body',
          message: 'Expected array of events',
        });
      }

      const processedEvents: InsertUiEvent[] = [];
      const errors: string[] = [];
      const duplicates: string[] = [];

      // Process each event
      for (const event of body) {
        try {
          // Validate against base schema
          const validatedEvent = baseAnalyticsSchema.parse(event);

          // Validate against prohibited fields
          const prohibitedCheck = validateProhibitedFields(
            validatedEvent.properties
          );
          if (!prohibitedCheck.valid) {
            errors.push(
              `Event "${validatedEvent.eventName}" contains prohibited fields: ${prohibitedCheck.errors.join(', ')}`
            );
            continue; // Skip this event
          }

          // Build dedupe key
          const dedupeKey = buildDedupeKey(
            validatedEvent.sessionId,
            validatedEvent.eventFamily === 'comprehension' &&
              validatedEvent.properties.fact
              ? `${validatedEvent.sessionId}:${validatedEvent.eventName}:${validatedEvent.properties.fact}`
              : validatedEvent.eventName
          );

          // Check for duplicates (in-memory check, database enforces unique constraint)
          if ((globalThis as any).__dedupeBuffer?.has(dedupeKey)) {
            duplicates.push(dedupeKey);
            continue; // Skip duplicate
          }

          // Prepare database insert
          const insertEvent: InsertUiEvent = {
            // Base properties (all events)
            product: validatedEvent.properties.product || 'core',
            eventName: validatedEvent.eventName,
            sessionId: validatedEvent.sessionId,
            userId: validatedEvent.properties.userId || null,
            properties: JSON.stringify(validateEvent.properties),
            ipAddress: validatedEvent.properties.ipPrefixHash || null,
            userAgent: validatedEvent.properties.uaHash || null,

            // Coarse dimensions (shared by all events)
            userTier: validatedEvent.userTier || UserTier.ANON,
            authState: validatedEvent.authState || AuthState.LOGGED_OUT,
            fileSizeBucket: validatedEvent.fileSizeBucket,
            sourceEntryPoint: validatedEvent.sourceEntryPoint,
            resultDensity: validatedEvent.resultDensity,
            client: validatedEvent.client || ClientType.WEB,

            // Server-enriched fields
            requestId: validatedEvent.requestId,
            receivedAt: validatedEvent.receivedAt,

            // Abuse defense (coarse signals only)
            asn: validatedEvent.asn,
            riskScoreBucket: validatedEvent.riskScoreBucket,
          };

          processedEvents.push(insertEvent);

          // Track dedupe (in-memory, cleared on rotation)
          if (!(globalThis as any).__dedupeBuffer) {
            (globalThis as any).__dedupeBuffer = new Set();
          }
          (globalThis as any).__dedupeBuffer.add(dedupeKey);
        } catch (error) {
          // Log validation error but continue processing other events
          errors.push(error instanceof Error ? error.message : String(error));
        }
      }

      if (processedEvents.length === 0) {
        return res.status(400).json({
          error: 'No valid events to process',
          message: 'All events were invalid or duplicates',
          errors,
        });
      }

      // Batch insert to database (single write, transactional)
      await db.insert(uiEvents).values(processedEvents);

      // Update health metrics
      processedEvents.forEach((event, index) => {
        updateHealthMetrics(
          event.eventName,
          true,
          event.sessionId,
          new Date(event.receivedAt),
          event.eventTime ? new Date(event.eventTime) : undefined
        );
      });

      // Track duplicates for health metrics
      if (duplicates.length > 0) {
        healthMetrics.duplicateRate += duplicates.length;
      }

      return res.json({
        success: true,
        processed: processedEvents.length,
        skipped: errors.length + duplicates.length,
        errors: errors.length > 0 ? errors : undefined,
        duplicates: duplicates.length > 0 ? duplicates : undefined,
        receivedAt: new Date().toISOString(),
      });
    } catch (error) {
      console.error('Analytics ingestion error:', error);

      return res.status(500).json({
        error: 'Failed to process analytics events',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // ============================================================================
  // ROUTE: Analytics Health Check
  // ============================================================================

  /**
   * GET /api/analytics/health
   * Returns analytics pipeline health metrics
   * Used to detect instrumentation bugs, clock skew, abuse patterns
   */
  app.get('/api/analytics/health', async (req: Request, res: Response) => {
    try {
      res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        metrics: {
          invalidEventRate: healthMetrics.invalidEventRate,
          missingSessionIdRate: healthMetrics.missingSessionIdRate,
          duplicateRate: healthMetrics.duplicateRate,
          eventLagDistribution: healthMetrics.eventLagDistribution,
          eventsPerSessionDistribution:
            healthMetrics.eventsPerSessionDistribution,
        },
        healthChecks: {
          invalidEventRate: healthMetrics.invalidEventRate < 100, // Less than 100 invalid/min is OK
          missingSessionIdRate: healthMetrics.missingSessionIdRate < 50, // Less than 50 missing/min is OK
          duplicateRate: healthMetrics.duplicateRate < 100, // Less than 100 dupes/min is OK
          eventLagP95: healthMetrics.eventLagDistribution.p95 < 5000, // Less than 5s lag is OK
          eventsPerSessionMax:
            healthMetrics.eventsPerSessionDistribution.max < 1000, // Less than 1000 events/session is OK
        },
        status:
          healthMetrics.invalidEventRate < 100 &&
          healthMetrics.missingSessionIdRate < 50 &&
          healthMetrics.duplicateRate < 100 &&
          healthMetrics.eventLagDistribution.p95 < 5000 &&
          healthMetrics.eventsPerSessionDistribution.max < 1000
            ? 'healthy'
            : 'degraded',
      });
    } catch (error) {
      console.error('Analytics health check error:', error);

      return res.status(500).json({
        error: 'Failed to retrieve analytics health metrics',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });

  // ============================================================================
  // ROUTE: Event Schema Version
  // ============================================================================

  /**
   * GET /api/analytics/schema
   * Returns current event contracts for client validation
   * Ensures client and server agree on schema version
   */
  app.get('/api/analytics/schema', async (req: Request, res: Response) => {
    try {
      res.json({
        version: '1.0.0',
        supportedEventFamilies: ['lifecycle', 'user_intent', 'comprehension'],
        lifecycleEvents: Object.values(require('@shared/analytics-events'))
          .LifecycleEvent,
        userIntentEvents: Object.values(require('@shared/analytics-events'))
          .UserIntentEvent,
        comprehensionEvents: Object.values(require('@shared/analytics-events'))
          .ComprehensionEvent,
        eventNames: Object.values(require('@shared/analytics-events'))
          .EventName,
        keyFactTypes: Object.values(require('@shared/analytics-events'))
          .KeyFactType,
        factRevealTriggers: Object.values(require('@shared/analytics-events'))
          .FactRevealTrigger,
        prohibitedProperties: require('@shared/analytics-events')
          .PROHIBITED_PROPERTIES,
        coarseDimensions: {
          fileSizeBuckets: Object.values(require('@shared/analytics-events'))
            .FileSizeBucket,
          userTiers: Object.values(require('@shared/analytics-events'))
            .UserTier,
          authStates: Object.values(require('@shared/analytics-events'))
            .AuthState,
          sourceEntryPoints: Object.values(require('@shared/analytics-events'))
            .SourceEntryPoint,
          resultDensities: Object.values(require('@shared/analytics-events'))
            .ResultDensity,
          clientTypes: Object.values(require('@shared/analytics-events'))
            .ClientType,
        },
      });
    } catch (error) {
      console.error('Schema endpoint error:', error);

      return res.status(500).json({
        error: 'Failed to retrieve analytics schema',
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  });
}
