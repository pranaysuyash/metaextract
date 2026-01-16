# Images MVP Route Refactoring Plan

## Current Issues
- **God Object Anti-Pattern**: 1,613 lines mixing all concerns
- **Single Responsibility Violation**: One file handles routing, business logic, data access, and utilities
- **Tight Coupling**: All functionality is interdependent
- **Testing Difficulty**: Impossible to unit test individual components
- **Maintenance Burden**: Changes affect multiple concerns simultaneously

## Proposed Architecture

### 1. Route Layer (`/server/routes/images-mvp/`)
**Purpose**: HTTP request handling only
```
server/routes/images-mvp/
├── index.ts                    # Main route registration
├── websocket.routes.ts         # WebSocket progress tracking
├── analytics.routes.ts         # Analytics endpoints  
├── quote.routes.ts             # Quote/preflight endpoints
├── credits.routes.ts           # Credit management endpoints
└── extraction.routes.ts        # Main extraction endpoint
```

### 2. Service Layer (`/server/services/images-mvp/`)
**Purpose**: Business logic orchestration
```
server/services/images-mvp/
├── extraction.service.ts       # Core extraction orchestration
├── credit-calculator.service.ts # Credit pricing logic
├── quota-manager.service.ts    # Trial and quota management
├── file-validator.service.ts   # File validation logic
├── progress.service.ts         # Progress tracking coordination
└── access-control.service.ts   # Access mode and redaction logic
```

### 3. Data Access Layer (`/server/repositories/`)
**Purpose**: Database and external service interactions
```
server/repositories/
├── credit-balance.repository.ts # Credit balance operations
├── trial-usage.repository.ts   # Trial usage tracking
├── analytics.repository.ts     # Analytics data persistence
└── payment.repository.ts       # Payment service integration
```

### 4. Integration Layer (`/server/integrations/`)
**Purpose**: External service coordination
```
server/integrations/
├── payment.integration.ts      # DodoPayments client wrapper
├── extraction.integration.ts   # Python extraction service
├── storage.integration.ts      # File storage operations
└── websocket.integration.ts    # WebSocket connection management
```

### 5. Domain Models (`/server/models/images-mvp/`)
**Purpose**: Type definitions and business entities
```
server/models/images-mvp/
├── types.ts                    # Core type definitions
├── credit-schedule.model.ts    # Credit pricing models
├── file-types.model.ts         # Supported file type definitions
└── access-modes.model.ts       # Access control models
```

## Detailed Module Breakdown

### Route Modules

#### 1. WebSocket Routes (`websocket.routes.ts`)
**Current Lines**: 406-494
**Responsibilities**:
- WebSocket connection establishment
- Connection lifecycle management
- Progress message broadcasting
- Connection cleanup

**Dependencies**: ProgressService, WebSocketIntegration

#### 2. Analytics Routes (`analytics.routes.ts`)
**Current Lines**: 499-533, 675-934
**Responsibilities**:
- UI event tracking endpoint
- Analytics report generation
- Event aggregation and metrics

**Dependencies**: AnalyticsService, AnalyticsRepository

#### 3. Quote Routes (`quote.routes.ts`)
**Current Lines**: 541-674
**Responsibilities**:
- File preflight validation
- Credit cost calculation
- Quote generation and storage
- File type and size validation

**Dependencies**: QuoteService, FileValidatorService, CreditCalculatorService

#### 4. Credits Routes (`credits.routes.ts`)
**Current Lines**: 939-1134
**Responsibilities**:
- Credit pack information
- Balance retrieval
- Purchase session creation
- Credit claiming (session to account)

**Dependencies**: CreditService, PaymentService, CreditBalanceRepository

#### 5. Extraction Routes (`extraction.routes.ts`)
**Current Lines**: 1139-1612
**Responsibilities**:
- File upload handling
- Extraction orchestration
- Progress tracking coordination
- Response formatting

**Dependencies**: ExtractionService, FileValidatorService, AccessControlService

### Service Modules

#### 1. Extraction Service (`extraction.service.ts`)
**Current Lines**: 1139-1612 (extraction logic)
**Responsibilities**:
- Coordinate extraction workflow
- Manage trial vs paid logic
- Handle credit charging
- Apply access mode redaction
- Log analytics events

**Key Methods**:
- `processExtraction(file, options, sessionContext)`
- `determineAccessMode(trialEmail, creditsAvailable)`
- `applyRedaction(metadata, accessMode)`

#### 2. Credit Calculator Service (`credit-calculator.service.ts`)
**Current Lines**: 117-144, 593-600, 1234
**Responsibilities**:
- Calculate credit costs based on file size and operations
- Resolve megapixel buckets
- Compute total credits for operations

**Key Methods**:
- `calculateCredits(fileSize, operations)`
- `resolveMegapixelBucket(dimensions)`
- `computeOperationCredits(operations, baseCredits)`

#### 3. Quota Manager Service (`quota-manager.service.ts`)
**Current Lines**: 1242-1272, 1522-1579
**Responsibilities**:
- Trial usage tracking
- Free quota enforcement
- Device-based quota management
- Enhanced protection logic

**Key Methods**:
- `checkTrialAvailability(email)`
- `enforceFreeQuota(clientId, ip)`
- `handleQuotaExceeded(clientId, context)`

#### 4. File Validator Service (`file-validator.service.ts`)
**Current Lines**: 286-340, 1169-1185
**Responsibilities**:
- MIME type validation
- File extension validation
- File size checking
- Security validation (malware prevention)

**Key Methods**:
- `validateFileType(mimeType, fileName)`
- `checkFileSize(sizeBytes, maxSize)`
- `getSecurityValidation(mimeType, extension)`

#### 5. Progress Service (`progress.service.ts`)
**Current Lines**: 155-243, 1315-1396
**Responsibilities**:
- Progress state management
- Broadcast coordination
- Connection lifecycle management

**Key Methods**:
- `broadcastProgress(sessionId, progress, message)`
- `registerConnection(sessionId, connection)`
- `cleanupConnections(sessionId)`

### Repository Modules

#### 1. Credit Balance Repository (`credit-balance.repository.ts`)
**Current Lines**: 972-996, 1038-1043, 1477-1505
**Responsibilities**:
- Credit balance CRUD operations
- Credit transaction management
- Balance transfer operations

**Key Methods**:
- `getOrCreateBalance(sessionId, userId)`
- `useCredits(balanceId, amount, description)`
- `transferCredits(fromId, toId, amount)`

#### 2. Trial Usage Repository (`trial-usage.repository.ts`)
**Current Lines**: 1245-1256, 1508-1520
**Responsibilities**:
- Trial usage tracking
- Email-based usage limits
- Usage increment operations

**Key Methods**:
- `getTrialUsageByEmail(email)`
- `recordTrialUsage(usageData)`
- `isTrialAvailable(email)`

#### 3. Analytics Repository (`analytics.repository.ts`)
**Current Lines**: 516-524, 687-931
**Responsibilities**:
- UI event persistence
- Event aggregation queries
- Analytics data retrieval

**Key Methods**:
- `logUiEvent(eventData)`
- `getUiEvents(filters)`
- `aggregateEvents(period, metrics)`

### Integration Modules

#### 1. Payment Integration (`payment.integration.ts`)
**Current Lines**: 146-153, 1011-1088
**Responsibilities**:
- DodoPayments client management
- Checkout session creation
- Payment webhook handling

**Key Methods**:
- `createCheckoutSession(pack, customer)`
- `getPaymentClient()`
- `handlePaymentWebhook(event)`

#### 2. Extraction Integration (`extraction.integration.ts`)
**Current Lines**: 1340-1347
**Responsibilities**:
- Python extraction service coordination
- Extraction options management
- Result processing

**Key Methods**:
- `extractMetadata(filePath, options)`
- `getExtractionTier()`
- `processExtractionResults(rawResults)`

## Migration Strategy

### Phase 1: Extract Configuration and Constants
1. Move file type definitions to `models/images-mvp/file-types.model.ts`
2. Move credit schedules to `models/images-mvp/credit-schedule.model.ts`
3. Move configuration constants to appropriate config files

### Phase 2: Extract Utility Functions
1. Create `utils/images-mvp/` directory
2. Move parsing functions (parseOpsFromRequest, parseBooleanField)
3. Move calculation functions (computeSizeCreditsFromUpload)
4. Move helper functions (getBaseUrl, getImagesMvpBalanceId)

### Phase 3: Extract Business Logic to Services
1. Create individual service files
2. Move business logic from routes to services
3. Maintain same function signatures initially
4. Update route handlers to call services

### Phase 4: Extract Data Access to Repositories
1. Create repository classes
2. Move database queries from services to repositories
3. Add data access interfaces for testing

### Phase 5: Extract External Integrations
1. Create integration classes
2. Move external service calls to integrations
3. Add error handling and retry logic

### Phase 6: Clean Up and Optimize
1. Remove duplicate code
2. Add proper error handling
3. Implement dependency injection
4. Add comprehensive tests

## Benefits of This Refactoring

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Testability**: Individual components can be unit tested in isolation
3. **Maintainability**: Changes to one concern don't affect others
4. **Reusability**: Services and repositories can be used by multiple routes
5. **Scalability**: Easier to add new features without affecting existing code
6. **Debugging**: Clear separation makes issues easier to identify and fix

## Implementation Priority

1. **High Priority**: Extract extraction logic (largest complexity)
2. **Medium Priority**: Extract credit and quota management
3. **Low Priority**: Extract analytics and websocket functionality

This refactoring will transform the 1,613-line God Object into a clean, maintainable architecture with clear separation of concerns.