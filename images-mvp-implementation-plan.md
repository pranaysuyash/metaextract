# Images MVP Refactoring - Implementation Plan

## Phase 1: Foundation (Week 1)

### 1.1 Create Directory Structure
```bash
mkdir -p server/routes/images-mvp
mkdir -p server/services/images-mvp
mkdir -p server/repositories
mkdir -p server/integrations
mkdir -p server/models/images-mvp
mkdir -p server/utils/images-mvp
```

### 1.2 Extract Constants and Types
**File**: `server/models/images-mvp/types.ts`
```typescript
// Move from lines 286-340
export const SUPPORTED_IMAGE_MIMES = new Set([
  'image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif',
  'image/tiff', 'image/bmp', 'image/gif', 'image/x-icon', 'image/svg+xml',
  'image/x-raw', 'image/x-canon-cr2', 'image/x-nikon-nef', 'image/x-sony-arw',
  'image/x-adobe-dng', 'image/x-olympus-orf', 'image/x-fuji-raf',
  'image/x-pentax-pef', 'image/x-sigma-x3f', 'image/x-samsung-srw',
  'image/x-panasonic-rw2'
]);

export const SUPPORTED_IMAGE_EXTENSIONS = new Set([
  '.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.tiff', '.tif',
  '.bmp', '.gif', '.ico', '.svg', '.raw', '.cr2', '.nef', '.arw', '.dng',
  '.orf', '.raf', '.pef', '.x3f', '.srw', '.rw2'
]);
```

**File**: `server/models/images-mvp/credit-schedule.model.ts`
```typescript
// Move credit schedule constants
export const IMAGES_MVP_CREDIT_SCHEDULE = {
  base: 1,
  embedding: 2,
  ocr: 3,
  forensics: 5,
} as const;
```

### 1.3 Extract Utility Functions
**File**: `server/utils/images-mvp/parsers.ts`
```typescript
// Move from lines 83-115
export function parseBooleanField(value: unknown): boolean {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase();
    return ['1', 'true', 'yes', 'on'].includes(normalized);
  }
  return false;
}

export function parseOpsFromRequest(body: any): ImagesMvpQuoteOps {
  const opsRaw = body?.ops ?? body ?? {};
  return {
    embedding: typeof opsRaw.embedding === 'boolean' ? opsRaw.embedding : 
               body?.op_embedding != null ? parseBooleanField(body.op_embedding) : true,
    ocr: typeof opsRaw.ocr === 'boolean' ? opsRaw.ocr :
         body?.op_ocr != null ? parseBooleanField(body.op_ocr) : false,
    forensics: typeof opsRaw.forensics === 'boolean' ? opsRaw.forensics :
               body?.op_forensics != null ? parseBooleanField(body.op_forensics) : false,
  };
}
```

**File**: `server/utils/images-mvp/calculations.ts`
```typescript
// Move from lines 117-144
export async function computeSizeCreditsFromUpload(
  file: Express.Multer.File
): Promise<{
  mp: number | null;
  mpBucket: string;
  mpCredits: number;
  warning?: string;
}> {
  try {
    const meta = await sharp(file.buffer).metadata();
    const mp = computeMp(meta.width ?? null, meta.height ?? null);
    const bucket = resolveMpBucket(mp);
    return {
      mp,
      mpBucket: bucket.label,
      mpCredits: bucket.credits,
      warning: bucket.warning,
    };
  } catch {
    const bucket = resolveSizeBucketFromBytes(file.size);
    return {
      mp: null,
      mpBucket: bucket.label,
      mpCredits: bucket.credits,
      warning: 'Dimensions unavailable; using size-based bucket estimate.',
    };
  }
}
```

## Phase 2: Service Layer (Week 2)

### 2.1 Create File Validator Service
**File**: `server/services/images-mvp/file-validator.service.ts`
```typescript
import { SUPPORTED_IMAGE_MIMES, SUPPORTED_IMAGE_EXTENSIONS } from '../../models/images-mvp/types';

export class FileValidatorService {
  private readonly MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

  validateFileType(mimeType: string, fileName: string): { valid: boolean; reason?: string } {
    const extension = fileName.includes('.') ? 
      fileName.slice(fileName.lastIndexOf('.')).toLowerCase() : '';
    
    const isSupportedMime = SUPPORTED_IMAGE_MIMES.has(mimeType);
    const isSupportedExt = extension ? SUPPORTED_IMAGE_EXTENSIONS.has(extension) : false;
    
    // Require BOTH mime type AND extension to be valid (security)
    if (!isSupportedMime || !isSupportedExt) {
      return { valid: false, reason: 'unsupported_type' };
    }
    
    return { valid: true };
  }

  validateFileSize(sizeBytes: number): { valid: boolean; reason?: string } {
    if (sizeBytes > this.MAX_FILE_SIZE) {
      return { valid: false, reason: 'file_too_large' };
    }
    return { valid: true };
  }

  validateFile(file: { mimetype: string; originalname: string; size: number }): {
    valid: boolean;
    reasons?: string[];
  } {
    const typeValidation = this.validateFileType(file.mimetype, file.originalname);
    const sizeValidation = this.validateFileSize(file.size);
    
    const reasons = [];
    if (!typeValidation.valid && typeValidation.reason) {
      reasons.push(typeValidation.reason);
    }
    if (!sizeValidation.valid && sizeValidation.reason) {
      reasons.push(sizeValidation.reason);
    }
    
    return {
      valid: typeValidation.valid && sizeValidation.valid,
      reasons: reasons.length > 0 ? reasons : undefined
    };
  }
}
```

### 2.2 Create Credit Calculator Service
**File**: `server/services/images-mvp/credit-calculator.service.ts`
```typescript
import { IMAGES_MVP_CREDIT_SCHEDULE } from '../../models/images-mvp/credit-schedule.model';
import { computeMp, resolveMpBucket, resolveSizeBucketFromBytes, computeImagesMvpCreditsTotal } from '@shared/imagesMvpPricing';
import sharp from 'sharp';

export class CreditCalculatorService {
  async calculateCreditsFromUpload(file: Express.Multer.File): Promise<{
    mp: number | null;
    mpBucket: string;
    mpCredits: number;
    warning?: string;
  }> {
    try {
      const meta = await sharp(file.buffer).metadata();
      const mp = computeMp(meta.width ?? null, meta.height ?? null);
      const bucket = resolveMpBucket(mp);
      return {
        mp,
        mpBucket: bucket.label,
        mpCredits: bucket.credits,
        warning: bucket.warning,
      };
    } catch {
      const bucket = resolveSizeBucketFromBytes(file.size);
      return {
        mp: null,
        mpBucket: bucket.label,
        mpCredits: bucket.credits,
        warning: 'Dimensions unavailable; using size-based bucket estimate.',
      };
    }
  }

  calculateCreditsFromDimensions(width: number | null, height: number | null): {
    mp: number | null;
    mpBucket: string;
    mpCredits: number;
    warning?: string;
  } {
    const mp = computeMp(width, height);
    const bucket = resolveMpBucket(mp);
    return {
      mp,
      mpBucket: bucket.label,
      mpCredits: bucket.credits,
      warning: bucket.warning,
    };
  }

  calculateTotalCredits(operations: ImagesMvpQuoteOps, baseCredits: number): {
    creditsTotal: number;
    breakdown: any;
  } {
    return computeImagesMvpCreditsTotal(operations, baseCredits);
  }
}
```

### 2.3 Create Progress Service
**File**: `server/services/images-mvp/progress.service.ts`
```typescript
import { WebSocket } from 'ws';

interface ProgressConnection {
  ws: WebSocket;
  sessionId: string;
  startTime: number;
}

export class ProgressService {
  private activeConnections = new Map<string, ProgressConnection[]>();

  registerConnection(sessionId: string, ws: WebSocket): void {
    const connection: ProgressConnection = {
      ws,
      sessionId,
      startTime: Date.now(),
    };

    if (!this.activeConnections.has(sessionId)) {
      this.activeConnections.set(sessionId, []);
    }
    this.activeConnections.get(sessionId)!.push(connection);

    // Send initial connection confirmation
    this.sendMessage(ws, {
      type: 'connected',
      sessionId,
      timestamp: Date.now(),
    });
  }

  broadcastProgress(sessionId: string, progress: number, message: string, stage?: string): void {
    const connections = this.activeConnections.get(sessionId);
    if (!connections || connections.length === 0) return;

    const normalizedProgress = Math.min(100, Math.max(0, progress));
    const progressData = {
      type: 'progress',
      sessionId,
      progress: normalizedProgress,
      percentage: normalizedProgress,
      message,
      stage: stage || 'processing',
      timestamp: Date.now(),
    };

    this.broadcastToSession(sessionId, progressData);
  }

  broadcastError(sessionId: string, error: string): void {
    this.broadcastToSession(sessionId, {
      type: 'error',
      sessionId,
      error,
      timestamp: Date.now(),
    });
  }

  broadcastComplete(sessionId: string, metadata: any): void {
    this.broadcastToSession(sessionId, {
      type: 'complete',
      sessionId,
      metadata: {
        fields_extracted: metadata.fields_extracted || 0,
        processing_time_ms: metadata.processing_time_ms || 0,
        file_size: metadata.file_size || 0,
      },
      timestamp: Date.now(),
    });
  }

  cleanupConnections(sessionId: string): void {
    const connections = this.activeConnections.get(sessionId);
    if (connections) {
      connections.forEach(conn => {
        if (conn.ws.readyState === 1) {
          conn.ws.close();
        }
      });
      this.activeConnections.delete(sessionId);
    }
  }

  private broadcastToSession(sessionId: string, data: any): void {
    const connections = this.activeConnections.get(sessionId);
    if (!connections) return;

    const messageStr = JSON.stringify(data);
    connections.forEach(conn => {
      if (conn.ws.readyState === 1) {
        conn.ws.send(messageStr);
      }
    });
  }

  private sendMessage(ws: WebSocket, data: any): void {
    if (ws.readyState === 1) {
      ws.send(JSON.stringify(data));
    }
  }
}
```

## Phase 3: Route Refactoring (Week 3)

### 3.1 Extract WebSocket Route
**File**: `server/routes/images-mvp/websocket.routes.ts`
```typescript
import { Express } from 'express';
import { WebSocket } from 'ws';
import { ProgressService } from '../../services/images-mvp/progress.service';

export function registerWebSocketRoutes(app: Express): void {
  const progressService = new ProgressService();

  if (typeof (app as any).ws === 'function') {
    (app as any).ws('/api/images_mvp/progress/:sessionId', (ws: WebSocket, req: any) => {
      const sessionId = req.params.sessionId;
      if (!sessionId) {
        ws.close(1002, 'Session ID required');
        return;
      }

      progressService.registerConnection(sessionId, ws);

      ws.on('message', data => {
        try {
          const message = JSON.parse(data.toString());
          if (message.type === 'ping') {
            ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
          }
        } catch (error) {
          console.error('WebSocket message parsing error:', error);
        }
      });

      ws.on('close', () => {
        progressService.cleanupConnections(sessionId);
      });

      ws.on('error', error => {
        console.error('WebSocket error for session', sessionId, ':', error);
        progressService.cleanupConnections(sessionId);
      });
    });
  } else {
    console.log('[ImagesMVP] WebSocket not available; progress tracking disabled');
  }
}
```

### 3.2 Extract Quote Route
**File**: `server/routes/images-mvp/quote.routes.ts`
```typescript
import { Express, Request, Response } from 'express';
import crypto from 'crypto';
import { CreditCalculatorService } from '../../services/images-mvp/credit-calculator.service';
import { FileValidatorService } from '../../services/images-mvp/file-validator.service';
import { parseOpsFromRequest } from '../../utils/images-mvp/parsers';
import { IMAGES_MVP_CREDIT_PACKS } from '../../payments';
import { IMAGES_MVP_CREDIT_SCHEDULE, computeImagesMvpCreditsTotal } from '@shared/imagesMvpPricing';

const IMAGES_MVP_QUOTES = new Map<string, any>();

export function registerQuoteRoutes(app: Express): void {
  const creditCalculator = new CreditCalculatorService();
  const fileValidator = new FileValidatorService();

  app.post('/api/images_mvp/quote', async (req: Request, res: Response) => {
    try {
      const rawFiles = Array.isArray(req.body?.files) ? req.body.files : [];
      const ops = parseOpsFromRequest(req.body);

      const MAX_FILES = 10;
      const MAX_BYTES = 100 * 1024 * 1024;

      const perFileCredits: Record<string, number> = {};
      const perFileById: Record<string, any> = {};

      let creditsTotal = 0;
      const limitedFiles = rawFiles.slice(0, MAX_FILES);

      for (const file of limitedFiles) {
        const fileId = typeof file?.id === 'string' ? file.id : null;
        if (!fileId) continue;

        // Validate file
        const name = typeof file?.name === 'string' ? file.name : '';
        const mime = typeof file?.mime === 'string' ? file.mime : null;
        const sizeBytes = typeof file?.sizeBytes === 'number' ? file.sizeBytes : 0;

        const validation = fileValidator.validateFile({
          mimetype: mime || 'application/octet-stream',
          originalname: name,
          size: sizeBytes
        });

        const creditsResult = creditCalculator.calculateCreditsFromDimensions(
          file?.width ?? null,
          file?.height ?? null
        );

        if (validation.valid) {
          const { creditsTotal: fileCreditsTotal, breakdown } =
            creditCalculator.calculateTotalCredits(ops, creditsResult.mpCredits);

          creditsTotal += fileCreditsTotal;
          perFileCredits[fileId] = fileCreditsTotal;
          perFileById[fileId] = {
            id: fileId,
            accepted: true,
            detected_type: mime,
            creditsTotal: fileCreditsTotal,
            breakdown,
            mp: creditsResult.mp,
            mpBucket: creditsResult.mpBucket,
            warnings: creditsResult.warning ? [creditsResult.warning] : [],
          };
        } else {
          perFileById[fileId] = {
            id: fileId,
            accepted: false,
            reason: validation.reasons?.[0],
            detected_type: mime,
            mp: creditsResult.mp,
            mpBucket: creditsResult.mpBucket,
            warnings: validation.reasons || [],
          };
        }
      }

      const quoteId = crypto.randomUUID();
      const expiresAt = Date.now() + 15 * 60 * 1000;
      IMAGES_MVP_QUOTES.set(quoteId, {
        files: limitedFiles,
        ops,
        creditsTotal,
        perFileCredits,
        perFile: perFileById,
        createdAt: Date.now(),
        expiresAt,
        schedule: IMAGES_MVP_CREDIT_SCHEDULE,
      });

      const perFileArray = Object.values(perFileById);
      const standardCreditsPerImage =
        IMAGES_MVP_CREDIT_SCHEDULE.base + IMAGES_MVP_CREDIT_SCHEDULE.embedding;

      res.json({
        quoteId,
        creditsTotal,
        perFile: perFileById,
        schedule: IMAGES_MVP_CREDIT_SCHEDULE,
        limits: {
          maxBytes: MAX_BYTES,
          allowedMimes: Array.from(SUPPORTED_IMAGE_MIMES),
          maxFiles: MAX_FILES,
        },
        creditSchedule: {
          ...IMAGES_MVP_CREDIT_SCHEDULE,
          standardCreditsPerImage,
        },
        quote: {
          perFile: perFileArray,
          totalCredits: creditsTotal,
          standardEquivalents:
            standardCreditsPerImage > 0
              ? Math.ceil(creditsTotal / standardCreditsPerImage)
              : null,
        },
        expiresAt: new Date(expiresAt).toISOString(),
        warnings: [],
      });
    } catch (error) {
      console.error('ImagesMVP quote error:', error);
      res.status(500).json({ error: 'Failed to create quote' });
    }
  });
}
```

## Phase 4: Integration and Testing (Week 4)

### 4.1 Create Main Route Registration
**File**: `server/routes/images-mvp/index.ts`
```typescript
import { Express } from 'express';
import { registerWebSocketRoutes } from './websocket.routes';
import { registerQuoteRoutes } from './quote.routes';
import { registerAnalyticsRoutes } from './analytics.routes';
import { registerCreditsRoutes } from './credits.routes';
import { registerExtractionRoutes } from './extraction.routes';

export function registerImagesMvpRoutes(app: Express): void {
  // Register all sub-routes
  registerWebSocketRoutes(app);
  registerQuoteRoutes(app);
  registerAnalyticsRoutes(app);
  registerCreditsRoutes(app);
  registerExtractionRoutes(app);
}
```

### 4.2 Update Main Server File
Replace the current import:
```typescript
// Old
import { registerImagesMvpRoutes } from './routes/images-mvp';

// New
import { registerImagesMvpRoutes } from './routes/images-mvp/index';
```

## Testing Strategy

### Unit Tests
- Test each service in isolation
- Mock external dependencies
- Test business logic thoroughly

### Integration Tests
- Test route handlers with mocked services
- Test service integration with mocked repositories
- Test database operations

### End-to-End Tests
- Test complete user workflows
- Test error scenarios
- Test edge cases

## Rollback Plan

1. **Keep Original File**: Rename `images-mvp.ts` to `images-mvp.ts.backup`
2. **Feature Flags**: Use environment variables to switch between old and new implementation
3. **Gradual Migration**: Migrate one route at a time
4. **Monitoring**: Add extensive logging to track issues
5. **Quick Rollback**: Keep git branch ready for immediate rollback

## Success Metrics

1. **Code Quality**: Reduced cyclomatic complexity
2. **Test Coverage**: Achieve 80%+ test coverage
3. **Performance**: Maintain or improve response times
4. **Maintainability**: Reduce time to implement new features
5. **Reliability**: Reduce bug reports and production issues

This implementation plan provides a structured approach to refactoring the God Object into a clean, maintainable architecture.