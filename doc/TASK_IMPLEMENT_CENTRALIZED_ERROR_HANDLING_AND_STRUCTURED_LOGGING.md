# TASK_IMPLEMENT_CENTRALIZED_ERROR_HANDLING_AND_STRUCTURED_LOGGING.md

# Task: Implement Centralized Error Handling and Structured Logging

## Executive Summary

**Priority**: HIGH
**Impact**: RELIABILITY, DEBUGGABILITY, MAINTENANCE, MONITORING
**Estimated Time**: 6-8 hours
**Affected Components**: All server routes, error handling, logging infrastructure

This task addresses a critical reliability issue: **inconsistent error handling and ad-hoc console logging** across all route handlers. Current approach makes debugging difficult, breaks production monitoring, and violates MetaExtract's error handling standards.

---

## What

### Current State - The Problem

#### Scattered Error Handling

**Issue**: Error handling logic duplicated across every route handler with inconsistent patterns

**Evidence**:
```bash
# Statistics from codebase:
43 console statements (console.log + console.error)
39 instances of "console.error" in server/routes/
49 try-catch blocks across route files
No centralized error handler or logging system
```

#### Inconsistent Error Patterns

Different routes handle errors differently:

```typescript
// Pattern 1: Generic error object
app.get('/api/endpoint', async (req, res) => {
  try {
    // ... logic
  } catch (error) {
    console.error('Something failed:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Pattern 2: Partial error details
app.post('/api/other', async (req, res) => {
  try {
    // ... logic
  } catch (error) {
    console.error('Processing error:', error);
    res.status(500).json({
      error: 'Processing failed',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

// Pattern 3: No error response
app.get('/api/another', async (req, res) => {
  try {
    // ... logic
  } catch (error) {
    console.error('Error:', error);
    // No response sent! Request hangs
  }
});

// Pattern 4: Console only
app.get('/api/something', async (req, res) => {
  try {
    // ... logic
  } catch (error) {
    console.error('Something went wrong');
    // Logged to console but not returned to client
  }
});
```

**Problems**:
- 4+ different error handling patterns across routes
- Inconsistent error response structure
- Some routes don't respond on errors (request hangs)
- Generic "Unknown error" messages everywhere
- No error categorization or context

#### Ad-Hoc Console Logging

**Issue**: Direct console statements instead of structured logging system

**Examples from routes**:
```typescript
// server/routes/extraction.ts
console.error('Failed to delete temp file:', tempPath, error);
console.error('Metadata extraction error:', error);
console.error('Batch processing error:', error);
console.error('Advanced extraction error:', error);
console.error('Health check error:', error);

// server/routes/forensic.ts
console.error('Failed to delete temp file:', tempPath, error);
console.error('Comparison error:', error);
console.error('Timeline reconstruction error:', error);
console.error(`Error analyzing ${file.originalname}:`, error);
console.error('Forensic report error:', error);

// server/routes/admin.ts
console.error('Failed to clear cache:', error);
console.error('Failed to retrieve analytics:', error);
```

**Problems**:
- No log levels (error, warning, info, debug)
- No structured fields (timestamp, correlation ID, user ID)
- No log aggregation or querying
- Production logs unparseable
- Difficult to search/filter logs
- No integration with monitoring/alerting
- Logs lost on container restart (no persistence)

#### Missing Error Context

**Issue**: Errors logged without contextual information

```typescript
// Current - No context:
console.error('Metadata extraction error:', error);

// What we need:
logger.error('Metadata extraction error', {
  error: error.message,
  stack: error.stack,
  requestId: req.id,
  userId: req.user?.id,
  filePath: req.file?.path,
  fileType: req.file?.mimetype,
  tier: req.query.tier,
  timestamp: new Date().toISOString(),
  operation: 'extract_metadata',
});
```

**Missing context**:
- Request ID (for tracing requests through system)
- User ID (who triggered the error)
- File information (what was being processed)
- Operation name (what was attempted)
- Tier information (user's access level)
- Correlation ID (connect to frontend logs)
- HTTP method and path
- Performance metrics (how long it took)

#### No Error Categorization

**Issue**: All errors treated the same way

**Current approach**:
```typescript
// Every error results in 500 status
res.status(500).json({ error: 'Something went wrong' });

// Or worse:
res.status(500).json({ error: 'Unknown error' });
```

**What we need**:
```typescript
// Categorized errors with appropriate status codes:
ValidationError → 400
AuthenticationError → 401
AuthorizationError → 403
NotFoundError → 404
ConflictError → 409
RateLimitError → 429
DatabaseError → 503
ExternalServiceError → 502
InternalServerError → 500
```

#### No Monitoring Integration

**Issue**: Server has monitoring system (`server/monitoring.ts`) but routes don't use it

```typescript
// server/monitoring.ts exists with:
// - record_extraction_for_monitoring()
// - Performance tracking
// - Alerting system

// BUT routes don't use it:
console.error('Metadata extraction error:', error);  // ❌ Not recorded in monitoring
```

**Consequences**:
- Analytics don't capture errors
- No error rate metrics
- No alerts on error spikes
- Can't track error trends over time
- Impossible to measure MTTR (Mean Time To Recovery)

### Current Infrastructure

#### Existing Monitoring System

**File**: `server/monitoring.ts` (9,460 lines)

**Features available**:
```typescript
// Function to record extraction for monitoring
record_extraction_for_monitoring(
  processing_time_ms: float,
  success: bool,
  tier: str,
  file_type: str,
  error_type: Optional[str]
)

// But routes don't call this for errors!
```

**Alerting system exists**:
- `server/alerting.ts` (4,775 lines)
- `get_alert_manager()` available
- Not integrated with route error handling

#### Existing Logger

**File**: `server/index.ts` has basic logging:

```typescript
export function log(message: string, source = 'express') {
  const formattedTime = new Date().toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });
  console.log(`${formattedTime} [${source}] ${message}`);
}
```

**Problems**:
- Only info level (no error/warning/debug)
- No structured fields
- No log levels
- No persistence
- Not used by routes (they use console directly)

---

## Why

### 1. **Production Debugging Nightmare** (CRITICAL PRIORITY)

**Problem**: When errors occur in production, you can't debug them effectively

**Scenario**:
1. User reports "Extraction failed"
2. Check logs: "Metadata extraction error: [object]"
3. No stack trace, no request ID, no user context
4. Can't reproduce because don't know what file they uploaded
5. Can't trace request through system
6. Spend hours guessing what went wrong

**Impact**:
- **MTTR increases**: Hours/days to fix bugs
- **User frustration**: Repeated failures with no explanation
- **Revenue impact**: Downtime affects paying customers
- **Support burden**: Support team overwhelmed with vague error reports

### 2. **Monitoring System Useless** (HIGH PRIORITY)

**Problem**: MetaExtract has sophisticated monitoring system but it's not being used

**Infrastructure exists**:
- `server/monitoring.ts` - Performance tracking
- `server/alerting.ts` - Alerting system
- Database tables for analytics
- Performance metrics collection

**But routes don't use it**:
```typescript
// Routes do this:
console.error('Error:', error);  // Lost forever

// They should do this:
monitoring.record_error({
  error: error.message,
  stack: error.stack,
  operation: 'extract_metadata',
  tier: req.query.tier,
  userId: req.user?.id,
});
```

**Impact**:
- No error dashboards
- No error rate monitoring
- No alerts on error spikes
- Can't track error trends
- Investment in monitoring wasted

### 3. **Inconsistent Error Responses** (MEDIUM PRIORITY)

**Problem**: Clients can't parse error responses reliably

**Frontend receives**:
```typescript
// Sometimes:
{ error: "Unknown error" }

// Sometimes:
{ error: "Processing failed", details: "Invalid file type" }

// Sometimes:
// No response at all (request hangs)

// Sometimes:
// Only logged to console, no HTTP response
```

**Frontend code must handle**:
```typescript
try {
  const result = await extractFile(file);
} catch (error) {
  // What's the structure?
  if (error.response?.data?.error) {
    // Pattern A
  } else if (error.response?.data?.details) {
    // Pattern B
  } else {
    // Unknown pattern
  }
}
```

**Impact**:
- Fragile frontend code
- Poor UX (generic error messages)
- Can't show helpful error messages
- Can't guide users to fix problems

### 4. **Security Risk - Information Leakage** (HIGH PRIORITY)

**Problem**: Console logs might expose sensitive information

**Examples**:
```typescript
// Could log:
console.error('Error processing file:', error);
console.error('User upload failed:', error);
// If error object contains file path, user data, etc.

// Should be:
logger.error('Processing error', {
  error: error.message,  // Only message, not full object
  error_type: error.constructor.name,
  // No sensitive data in logs
});
```

**Impact**:
- Potential security breach
- Logs could expose file paths
- Could leak user data
- Compliance violations (GDPR, HIPAA)

### 5. **Performance Monitoring Broken** (MEDIUM PRIORITY)

**Problem**: Can't measure performance because errors aren't tracked

**What we need**:
- Error rate by endpoint
- Error rate by file type
- Error rate by tier
- Error trends over time
- Correlation errors with performance

**What we have**:
- Only console statements
- No aggregation
- No metrics
- No trends

**Impact**:
- Can't identify slow endpoints
- Can't optimize based on error patterns
- Can't predict capacity issues
- Reactive instead of proactive

### 6. **Code Maintenance Burden** (MEDIUM PRIORITY)

**Problem**: Every route handler implements error handling from scratch

**Current**:
```typescript
app.get('/api/endpoint1', async (req, res) => {
  try {
    // 20 lines of logic
  } catch (error) {
    console.error('Endpoint1 error:', error);
    res.status(500).json({ error: 'Something went wrong' });
  }
});

app.post('/api/endpoint2', async (req, res) => {
  try {
    // 30 lines of logic
  } catch (error) {
    console.error('Endpoint2 error:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// ... 30+ more endpoints with same pattern
```

**What we need**:
```typescript
app.get('/api/endpoint1', async (req, res) => {
  try {
    // 20 lines of logic
    // No error handling needed - handled by middleware
  }
});
// Error middleware handles all errors consistently
```

**Impact**:
- **400+ lines of duplicated error handling**
- Changes require updating every route
- Inconsistent error handling
- Maintenance burden

### 7. **Log Analysis Impossible** (HIGH PRIORITY)

**Problem**: Can't search, filter, or analyze logs

**Current logs**:
```text
1:23:45 PM [express] Failed to delete temp file: Error: EACCES
1:23:46 PM [express] Metadata extraction error: Error: ENOENT
1:23:47 PM [express] Batch processing error: Error: EPIPE
1:23:48 PM [express] Advanced extraction error: Error: ECONNREFUSED
```

**What you can do**:
- Scroll through log file
- Grep for "error"
- That's it

**What you can't do**:
- Filter by error type (ENOENT, EACCES)
- Filter by user ID
- Filter by tier
- Filter by operation
- Get error rate per endpoint
- Find all errors for specific user
- Correlate errors across services
- Build error dashboards

**Impact**:
- Impossible to debug production issues
- Can't identify error patterns
- Can't measure error impact
- Reactive troubleshooting only

### 8. **Development Velocity Loss** (MEDIUM PRIORITY)

**Problem**: Developers spend time implementing error handling instead of features

**Current workflow**:
```typescript
// Implement new endpoint (2 hours)
app.post('/api/new-feature', async (req, res) => {
  // Implement logic
});

// Add error handling (30 minutes) - same as every other endpoint
app.post('/api/new-feature', async (req, res) => {
  try {
    // Implement logic
  } catch (error) {
    console.error('New feature error:', error);
    res.status(500).json({ error: 'Unknown error' });
  }
});

// Test error cases (30 minutes)
// Review error handling (15 minutes)
// Total: 3.5 hours for simple endpoint
```

**With centralized error handling**:
```typescript
// Implement new endpoint (2 hours)
app.post('/api/new-feature', async (req, res) => {
  // Implement logic
  // No error handling needed
});
// Total: 2 hours for simple endpoint (43% faster)
```

**Impact**:
- 43% slower development
- Developers avoid adding endpoints
- Reduced velocity
- More code review time

---

## Everything - Complete Technical Analysis

### Architecture Analysis

#### Current Error Handling Flow

```
Request → Route Handler → Try-Catch → Console.error → res.status(500)
                                      ↓
                                    Lost forever
```

**Problems**:
- Every route implements this flow separately
- No error propagation
- No error categorization
- No monitoring integration
- Logs lost on container restart

#### Desired Error Handling Flow

```
Request → Request ID Middleware → Route Handler → Business Logic
                                        ↓
                                    Error
                                        ↓
                    ┌─────────────────────────┴─────────────────────────┐
                    ↓                                               ↓
            Error Categorization                              Error Monitoring
                    ↓                                               ↓
            Appropriate HTTP Status                        Record in Database
                    ↓                                               ↓
            Structured Log Entry                        Alerting System
                    ↓                                               ↓
            Error Response to Client                    Dashboard/Alerts
```

### Error Categorization Strategy

#### Error Hierarchy

```typescript
// server/errors/base.ts
export abstract class AppError extends Error {
  abstract statusCode: number;
  abstract userMessage: string;
  abstract isOperational: boolean;

  constructor(message: string, public context?: Record<string, any>) {
    super(message);
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      name: this.constructor.name,
      message: this.userMessage,
      context: this.context,
      statusCode: this.statusCode,
      isOperational: this.isOperational,
    };
  }
}

// server/errors/validation.ts
export class ValidationError extends AppError {
  statusCode = 400;
  isOperational = true;

  constructor(
    message: string,
    public field?: string,
    public value?: any,
    context?: Record<string, any>
  ) {
    super(message, { field, value, ...context });
    this.userMessage = message;
  }
}

// server/errors/not-found.ts
export class NotFoundError extends AppError {
  statusCode = 404;
  isOperational = true;

  constructor(resource: string, identifier: string, context?: Record<string, any>) {
    super(`${resource} not found: ${identifier}`, context);
    this.userMessage = `The requested ${resource} could not be found`;
  }
}

// server/errors/authorization.ts
export class AuthorizationError extends AppError {
  statusCode = 403;
  isOperational = true;

  constructor(
    message: string,
    public requiredPermission?: string,
    context?: Record<string, any>
  ) {
    super(message, context);
    this.userMessage = 'You do not have permission to perform this action';
  }
}

// server/errors/external-service.ts
export class ExternalServiceError extends AppError {
  statusCode = 502;
  isOperational = true;

  constructor(
    service: string,
    operation: string,
    originalError: Error,
    context?: Record<string, any>
  ) {
    super(
      `External service ${service} failed during ${operation}`,
      { service, operation, originalError: originalError.message, ...context }
    );
    this.userMessage = 'An external service is temporarily unavailable';
  }
}

// server/errors/database.ts
export class DatabaseError extends AppError {
  statusCode = 503;
  isOperational = true;

  constructor(
    operation: string,
    originalError: Error,
    context?: Record<string, any>
  ) {
    super(
      `Database operation ${operation} failed`,
      { operation, originalError: originalError.message, ...context }
    );
    this.userMessage = 'A database error occurred. Please try again later.';
  }
}

// server/errors/rate-limit.ts
export class RateLimitError extends AppError {
  statusCode = 429;
  isOperational = true;

  constructor(
    public retryAfter: number,
    context?: Record<string, any>
  ) {
    super('Rate limit exceeded', context);
    this.userMessage = `Too many requests. Please try again in ${retryAfter} seconds.`;
  }
}
```

### Structured Logging System

#### Logger Implementation

```typescript
// server/logger/index.ts
import pino from 'pino';
import { randomUUID } from 'crypto';

interface LogContext {
  requestId?: string;
  userId?: string;
  sessionId?: string;
  operation?: string;
  endpoint?: string;
  method?: string;
  tier?: string;
  fileType?: string;
  fileSize?: number;
  [key: string]: any;
}

interface LogEntry {
  level: 'error' | 'warn' | 'info' | 'debug';
  message: string;
  error?: {
    name: string;
    message: string;
    stack?: string;
  };
  context?: LogContext;
  timestamp: string;
  requestId: string;
}

class StructuredLogger {
  private logger: pino.Logger;

  constructor() {
    this.logger = pino({
      level: process.env.LOG_LEVEL || 'info',
      transport: {
        target: 'pino/file',
        options: {
          destination: process.env.LOG_FILE || './logs/app.log',
          mkdir: true,
        },
      },
      serializers: {
        err: pino.stdSerializers.err,
        req: pino.stdSerializers.req,
        res: pino.stdSerializers.res,
      },
    });
  }

  private log(entry: LogEntry) {
    this.logger[entry.level](entry);
  }

  error(message: string, error?: Error, context?: LogContext) {
    this.log({
      level: 'error',
      message,
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack,
      } : undefined,
      context,
      timestamp: new Date().toISOString(),
      requestId: context?.requestId || randomUUID(),
    });
  }

  warn(message: string, context?: LogContext) {
    this.log({
      level: 'warn',
      message,
      context,
      timestamp: new Date().toISOString(),
      requestId: context?.requestId || randomUUID(),
    });
  }

  info(message: string, context?: LogContext) {
    this.log({
      level: 'info',
      message,
      context,
      timestamp: new Date().toISOString(),
      requestId: context?.requestId || randomUUID(),
    });
  }

  debug(message: string, context?: LogContext) {
    this.log({
      level: 'debug',
      message,
      context,
      timestamp: new Date().toISOString(),
      requestId: context?.requestId || randomUUID(),
    });
  }
}

export const logger = new StructuredLogger();
```

### Request ID Middleware

```typescript
// server/middleware/request-id.ts
import { Request, Response, NextFunction } from 'express';
import { randomUUID } from 'crypto';

export interface RequestWithId extends Request {
  id: string;
  startTime: number;
}

export function requestIdMiddleware(
  req: RequestWithId,
  res: Response,
  next: NextFunction
) {
  req.id = req.headers['x-request-id'] as string || randomUUID();
  req.startTime = Date.now();

  res.setHeader('x-request-id', req.id);

  next();
}
```

### Error Handler Middleware

```typescript
// server/middleware/error-handler.ts
import type { Request, Response, NextFunction } from 'express';
import type { RequestWithId } from './request-id';
import { AppError } from '../errors/base';
import { logger } from '../logger';

export function errorHandlerMiddleware(
  err: Error,
  req: RequestWithId,
  res: Response,
  next: NextFunction
) {
  const duration = Date.now() - req.startTime;

  // Log error with full context
  logger.error('Request failed', err, {
    requestId: req.id,
    userId: (req as any).user?.id,
    sessionId: (req as any).sessionId,
    endpoint: req.path,
    method: req.method,
    tier: req.query.tier,
    duration,
  });

  // Record in monitoring
  if (process.env.NODE_ENV === 'production') {
    // Import monitoring to avoid circular dependency
    import('./monitoring').then(({ recordExtractionForMonitoring }) => {
      recordExtractionForMonitoring(duration, false, req.query.tier as string, 'unknown', err.name);
    });
  }

  // Categorize error and send appropriate response
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.userMessage,
      requestId: req.id,
      ...(process.env.NODE_ENV === 'development' && {
        details: err.message,
        context: err.context,
      }),
    });
  }

  // Unknown errors
  if (process.env.NODE_ENV === 'production') {
    // Don't leak internal errors
    res.status(500).json({
      error: 'An internal error occurred',
      requestId: req.id,
    });
  } else {
    // Development: show full error
    res.status(500).json({
      error: err.message,
      requestId: req.id,
      stack: err.stack,
    });
  }
}
```

### Integration with Routes

#### Before Refactoring

```typescript
// Current - Every route has error handling:
app.post('/api/extract', upload.single('file'), async (req, res) => {
  try {
    const result = await extractMetadata(req.file.path);
    res.json(result);
  } catch (error) {
    console.error('Metadata extraction error:', error);
    res.status(500).json({
      error: 'Unknown error',
    });
  }
});
```

#### After Refactoring

```typescript
// After - Clean route handlers:
app.post('/api/extract', upload.single('file'), async (req, res, next) => {
  try {
    const result = await extractMetadata(req.file.path);
    res.json(result);
  } catch (error) {
    // Let error handler middleware handle it
    next(error);
  }
});
```

### Migration Strategy

#### Phase 1: Create Error Classes (2 hours)

1. Create error base class:
   ```bash
   mkdir -p server/errors
   touch server/errors/base.ts
   ```

2. Create specific error types:
   ```bash
   touch server/errors/validation.ts
   touch server/errors/not-found.ts
   touch server/errors/authorization.ts
   touch server/errors/external-service.ts
   touch server/errors/database.ts
   touch server/errors/rate-limit.ts
   touch server/errors/index.ts
   ```

3. Implement each error class
4. Export from `server/errors/index.ts`

#### Phase 2: Implement Structured Logger (2 hours)

5. Install pino logging library:
   ```bash
   npm install pino pino/file
   ```

6. Create logger implementation:
   ```typescript
   // server/logger/index.ts
   // Implement as shown above
   ```

7. Configure log levels and output
8. Add log rotation configuration

#### Phase 3: Create Middleware (1 hour)

9. Create request ID middleware:
   ```typescript
   // server/middleware/request-id.ts
   ```

10. Create error handler middleware:
    ```typescript
    // server/middleware/error-handler.ts
    ```

11. Integrate with monitoring system
12. Add alerting for error spikes

#### Phase 4: Update Server Index (30 minutes)

13. Add middleware to server:
    ```typescript
    // server/index.ts
    import { requestIdMiddleware } from './middleware/request-id';
    import { errorHandlerMiddleware } from './middleware/error-handler';

    app.use(requestIdMiddleware);

    // Register routes...

    app.use(errorHandlerMiddleware);
    ```

#### Phase 5: Migrate Routes (2-3 hours)

14. Update extraction routes:
    ```typescript
    // Before:
    try { ... } catch (error) { console.error(...); res.status(500)... }

    // After:
    try { ... } catch (error) { next(error); }
    ```

15. Update forensic routes
16. Update metadata routes
17. Update tier routes
18. Update admin routes
19. Update onboarding routes

#### Phase 6: Testing & Verification (1 hour)

20. Create error tests:
    ```typescript
    // tests/error-handling.test.ts
    describe('Error Handling', () => {
      it('should categorize validation errors correctly');
      it('should return 404 for not found');
      it('should return 429 for rate limit');
      it('should log errors with full context');
      it('should record errors in monitoring');
      // ... more tests
    });
    ```

21. Test error responses
22. Verify monitoring integration
23. Check log output format
24. Test error scenarios manually

#### Phase 7: Documentation (30 minutes)

25. Update AGENTS.md with error handling guidelines
26. Update DEVELOPMENT_GUIDE.md
27. Document error types and when to use
28. Document logger usage
29. Document monitoring integration

### Implementation Checklist

- [ ] Phase 1: Create Error Classes
  - [ ] Create `server/errors/` directory
  - [ ] Implement `AppError` base class
  - [ ] Implement `ValidationError`
  - [ ] Implement `NotFoundError`
  - [ ] Implement `AuthorizationError`
  - [ ] Implement `AuthenticationError`
  - [ ] Implement `ExternalServiceError`
  - [ ] Implement `DatabaseError`
  - [ ] Implement `RateLimitError`
  - [ ] Export all from `server/errors/index.ts`

- [ ] Phase 2: Implement Structured Logger
  - [ ] Install `pino` and `pino/file`
  - [ ] Create `server/logger/index.ts`
  - [ ] Implement `StructuredLogger` class
  - [ ] Add `error()` method
  - [ ] Add `warn()` method
  - [ ] Add `info()` method
  - [ ] Add `debug()` method
  - [ ] Configure log levels
  - [ ] Configure log output
  - [ ] Add log rotation

- [ ] Phase 3: Create Middleware
  - [ ] Create `server/middleware/request-id.ts`
  - [ ] Implement `requestIdMiddleware()`
  - [ ] Add request timing
  - [ ] Create `server/middleware/error-handler.ts`
  - [ ] Implement `errorHandlerMiddleware()`
  - [ ] Integrate with monitoring system
  - [ ] Add alerting for error spikes
  - [ ] Handle `AppError` vs generic `Error`

- [ ] Phase 4: Update Server Index
  - [ ] Import middleware
  - [ ] Add `requestIdMiddleware` before routes
  - [ ] Add `errorHandlerMiddleware` after routes
  - [ ] Test middleware order

- [ ] Phase 5: Migrate Routes
  - [ ] Update `server/routes/extraction.ts`
    - [ ] Remove try-catch blocks
    - [ ] Replace with `next(error)`
    - [ ] Remove `console.error` calls
    - [ ] Use new error types where appropriate
  - [ ] Update `server/routes/forensic.ts`
    - [ ] Remove try-catch blocks
    - [ ] Replace with `next(error)`
    - [ ] Remove `console.error` calls
  - [ ] Update `server/routes/metadata.ts`
  - [ ] Update `server/routes/tiers.ts`
  - [ ] Update `server/routes/admin.ts`
  - [ ] Update `server/routes/onboarding.ts`

- [ ] Phase 6: Testing
  - [ ] Create error handling tests
  - [ ] Test validation errors
  - [ ] Test not found errors
  - [ ] Test authorization errors
  - [ ] Test database errors
  - [ ] Test error responses
  - [ ] Verify logging output
  - [ ] Verify monitoring integration
  - [ ] Verify request ID propagation
  - [ ] Manual smoke test

- [ ] Phase 7: Documentation
  - [ ] Update AGENTS.md
  - [ ] Update DEVELOPMENT_GUIDE.md
  - [ ] Document error types
  - [ ] Document logger usage
  - [ ] Document error handling patterns
  - [ ] Add examples

### Code Metrics

#### Before Refactoring

```
Error Handling:
- Try-catch blocks: 49 (duplicated across routes)
- Console.error statements: 39
- Error response patterns: 4+ (inconsistent)
- Lines of error handling code: ~400+
- Code duplication: HIGH

Logging:
- Console statements: 43
- Structured fields: 0
- Request IDs: 0
- Error context: Minimal
- Log levels: None
- Integration with monitoring: NO

Maintainability:
- Add new endpoint: Must implement error handling (30 min)
- Change error response: Must update all routes (2+ hours)
- Debug production error: Hours/days (no context)
```

#### After Refactoring

```
Error Handling:
- Try-catch blocks: 1 (centralized middleware)
- Console.error statements: 0
- Error response patterns: 1 (consistent)
- Lines of error handling code: ~200 (reusable)
- Code duplication: NONE

Logging:
- Console statements: 0
- Structured fields: 10+ (request ID, user ID, operation, etc.)
- Request IDs: 100% (all requests)
- Error context: Comprehensive
- Log levels: 4 (error, warn, info, debug)
- Integration with monitoring: YES

Maintainability:
- Add new endpoint: No error handling needed (0 min)
- Change error response: Update 1 file (5 min)
- Debug production error: Minutes (full context)
```

### Performance Impact

**No negative performance impact**:

- Error handling overhead: Minimal (few ms)
- Logging overhead: Minimal (pino is fast)
- Request ID generation: <1ms (UUID)
- Monitoring integration: Async (non-blocking)

**Potential improvements**:
- Faster error debugging (structured logs)
- Better error tracking (monitoring)
- Faster MTTR (context-rich errors)
- Better capacity planning (error metrics)

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Breaking changes in error response** | Medium | High | Keep existing response structure, add new fields gradually |
| **Performance regression** | Low | Low | Monitor performance, pino is highly optimized |
| **Lost error context** | Low | Medium | Test all error scenarios, verify logging |
| **Monitoring overload** | Low | Medium | Rate-limit error recording, sample high-frequency errors |
| **Storage issues with logs** | Low | Low | Implement log rotation, size limits |
| **Migration errors** | Medium | High | Thorough testing, gradual rollout |

### Success Metrics

#### Before Refactoring

```
Production Issues:
- Average MTTR: 4-8 hours (hard to debug without context)
- Error resolution time: 30+ minutes per error
- Log search time: 10-30 minutes (grep through files)
- Error tracking: IMPOSSIBLE (no metrics)

Development:
- New endpoint development time: 3.5 hours (with error handling)
- Error response consistency: POOR (4+ patterns)
- Code duplication: HIGH (400+ lines)
- Testing effort: HIGH (many error scenarios)

Monitoring:
- Error dashboard: NONE
- Error rate metrics: NONE
- Error alerting: NONE (infrastructure exists but unused)
- Error trends: IMPOSSIBLE to track
```

#### After Refactoring

```
Production Issues:
- Average MTTR: 30 minutes - 2 hours (structured logs, request IDs)
- Error resolution time: 5-10 minutes (search by request ID)
- Log search time: <1 minute (structured queries)
- Error tracking: EXCELLENT (full metrics, trends)

Development:
- New endpoint development time: 2 hours (no error handling needed)
- Error response consistency: EXCELLENT (single pattern)
- Code duplication: NONE (centralized)
- Testing effort: LOW (error scenarios tested once)

Monitoring:
- Error dashboard: YES (built from logs)
- Error rate metrics: YES (by endpoint, tier, file type)
- Error alerting: YES (infrastructure utilized)
- Error trends: YES (historical data available)
```

---

## Conclusion

This task addresses a **critical reliability gap** in MetaExtract. The current approach:

- **43 console statements** scattered across routes
- **49 try-catch blocks** with inconsistent patterns
- **400+ lines of duplicated error handling**
- **No structured logging** or request tracing
- **Monitoring infrastructure unused** despite investment
- **Production debugging takes hours/days** instead of minutes

The solution is well-established:
1. Create hierarchical error class system
2. Implement structured logging with pino
3. Add request ID middleware for tracing
4. Create centralized error handler middleware
5. Migrate all routes to use new system
6. Integrate with existing monitoring/alerting

**Estimated Time**: 6-8 hours
**Impact**: MAJOR improvement to reliability, debuggability, and maintenance
**Risk**: Medium - involves changes to error responses, can be rolled back

**Priority**: HIGH - This should be completed soon to improve production reliability and developer velocity.

---

**Documented**: January 1, 2026
**Status**: READY FOR IMPLEMENTATION
**Component**: All server routes, error handling, logging
**Priority**: HIGH
**Estimated Time**: 6-8 hours
**Impact**: MAJOR RELIABILITY AND MAINTENANCE IMPROVEMENT
