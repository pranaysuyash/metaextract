# Images MVP Current File Analysis

## File Statistics
- **Total Lines**: 1,613
- **File Size**: ~1,562 lines of code (as mentioned in issue)
- **Functions/Methods**: 40+ functions and route handlers
- **Imports**: 20+ external dependencies

## Code Structure Analysis

### Section 1: Imports and Configuration (Lines 1-91)
**Lines**: 1-91 (90 lines)
**Content**: Import statements, type definitions, constants
**Concerns**: External dependencies, WebSocket interfaces, configuration

### Section 2: Utility Functions (Lines 92-153)
**Lines**: 92-153 (61 lines)
**Functions**:
- `parseBooleanField()` - Data parsing utility
- `parseOpsFromRequest()` - Request parsing for operations
- `computeSizeCreditsFromUpload()` - File size to credits calculation
- `getDodoClient()` - Payment client initialization

### Section 3: WebSocket Progress Functions (Lines 155-243)
**Lines**: 155-243 (88 lines)
**Functions**:
- `broadcastProgress()` - Send progress updates to WebSocket clients
- `broadcastError()` - Send error notifications
- `broadcastComplete()` - Send completion notifications
- `cleanupConnections()` - WebSocket cleanup

### Section 4: File Upload Configuration (Lines 245-278)
**Lines**: 245-278 (33 lines)
**Content**: Multer configuration for file uploads
**Concerns**: File storage, size limits, upload directory management

### Section 5: Rate Limiting and Type Definitions (Lines 280-396)
**Lines**: 280-396 (116 lines)
**Content**: 
- Analytics rate limiter configuration
- Supported image MIME types and extensions
- Base URL configuration
- Session ID utilities
- Analytics parameter parsing functions

### Section 6: Route Registration Function (Lines 402-1612)
**Lines**: 402-1612 (1,210 lines)
**Main Function**: `registerImagesMvpRoutes(app: Express)`

#### 6.1 WebSocket Route (Lines 406-494)
**Lines**: 88 lines
**Route**: `/api/images_mvp/progress/:sessionId`
**Responsibilities**: WebSocket connection handling, progress tracking

#### 6.2 Analytics Track Route (Lines 499-532)
**Lines**: 33 lines
**Route**: `POST /api/images_mvp/analytics/track`
**Responsibilities**: UI event logging

#### 6.3 Quote Route (Lines 541-674)
**Lines**: 133 lines
**Route**: `POST /api/images_mvp/quote`
**Responsibilities**: 
- File preflight validation
- Credit cost calculation
- Quote generation
- File type and size validation

#### 6.4 Analytics Report Route (Lines 675-934)
**Lines**: 259 lines
**Route**: `GET /api/images_mvp/analytics/report`
**Responsibilities**:
- Analytics data aggregation
- Event counting and metrics
- Report generation with multiple data points

#### 6.5 Credit Packs Route (Lines 939-944)
**Lines**: 5 lines
**Route**: `GET /api/images_mvp/credits/packs`
**Responsibilities**: Return available credit packs

#### 6.6 Credit Balance Route (Lines 949-1001)
**Lines**: 52 lines
**Route**: `GET /api/images_mvp/credits/balance`
**Responsibilities**: 
- Retrieve credit balance
- Handle authenticated and anonymous users
- Session and user balance management

#### 6.7 Credit Purchase Route (Lines 1007-1089)
**Lines**: 82 lines
**Route**: `POST /api/images_mvp/credits/purchase`
**Responsibilities**:
- Create payment checkout session
- Handle payment integration
- Session metadata management

#### 6.8 Credit Claim Route (Lines 1095-1133)
**Lines**: 38 lines
**Route**: `POST /api/images_mvp/credits/claim`
**Responsibilities**: Transfer credits from session to user account

#### 6.9 Main Extraction Route (Lines 1139-1612)
**Lines**: 473 lines
**Route**: `POST /api/images_mvp/extract`
**Responsibilities**:
- File upload handling
- Complete extraction workflow
- Trial and quota management
- Credit charging
- Progress tracking
- Access control and redaction

## Complexity Analysis

### Most Complex Sections (by line count):
1. **Main Extraction Route**: 473 lines (29% of file)
2. **Analytics Report Route**: 259 lines (16% of file)
3. **Quote Route**: 133 lines (8% of file)
4. **Rate Limiting/Type Definitions**: 116 lines (7% of file)

### Business Logic Distribution:
- **Credit/Payment Logic**: ~200 lines (12%)
- **File Validation Logic**: ~100 lines (6%)
- **Trial/Quota Logic**: ~150 lines (9%)
- **Analytics Logic**: ~300 lines (19%)
- **Extraction Logic**: ~400 lines (25%)
- **WebSocket/Progress Logic**: ~150 lines (9%)

### Data Access Patterns:
- **Database Queries**: 8+ queries scattered throughout
- **External Service Calls**: Payment service, Python extraction service
- **In-memory Storage**: Quote storage, WebSocket connections
- **File System Operations**: Upload handling, temporary file management

## Anti-Pattern Indicators

### 1. Multiple Responsibilities in Single Function
The `registerImagesMvpRoutes` function handles:
- Route registration
- Business logic execution
- Data access operations
- External service integration
- Error handling

### 2. Tight Coupling
- Routes directly manipulate database
- Business logic mixed with HTTP request handling
- External service calls embedded in route handlers
- No abstraction layers between concerns

### 3. Difficult Testing
- Cannot unit test business logic without HTTP layer
- Database operations embedded in route handlers
- External dependencies not mockable
- Complex setup required for testing

### 4. Code Duplication
- Similar validation logic in multiple routes
- Repeated credit calculation patterns
- Duplicate error handling code
- Similar quota checking logic

### 5. Configuration Scattered
- Constants defined throughout the file
- No central configuration management
- Hard-coded values in business logic
- Environment variable access mixed with logic

## Specific Extraction Opportunities

### Immediate Wins (Low Risk):
1. **Extract File Type Constants** (Lines 286-340)
2. **Extract Configuration Functions** (Lines 342-396)
3. **Extract Utility Functions** (Lines 83-144)
4. **Extract WebSocket Functions** (Lines 155-243)

### Medium Complexity (Medium Risk):
1. **Extract Credit Calculation Logic** (Lines 117-144, 593-600)
2. **Extract File Validation Logic** (Lines 1169-1185, 571-592)
3. **Extract Analytics Aggregation** (Lines 727-859)
4. **Extract Quote Generation** (Lines 549-669)

### High Complexity (Higher Risk):
1. **Extract Main Extraction Logic** (Lines 1139-1612)
2. **Extract Payment Integration** (Lines 1011-1088)
3. **Extract Trial/Quota Management** (Lines 1242-1272, 1522-1579)
4. **Extract Access Control Logic** (Lines 1423-1588)

## Dependencies Analysis

### External Dependencies:
- **express**: Web framework
- **ws**: WebSocket library
- **multer**: File upload handling
- **sharp**: Image processing
- **drizzle-orm**: Database ORM
- **dodopayments**: Payment processing
- **crypto**: Cryptographic functions
- **fs/promises**: File system operations

### Internal Dependencies:
- **../db**: Database connection
- **../storage**: Storage operations
- **../utils/extraction-helpers**: Extraction utilities
- **../utils/error-response**: Error handling
- **../auth**: Authentication middleware
- **../middleware/***: Various middleware functions
- **../payments**: Payment configuration
- **@shared/***: Shared schemas and utilities

## Risk Assessment

### Low Risk Changes:
- Moving constants to separate files
- Extracting utility functions
- Creating type definitions
- Moving configuration

### Medium Risk Changes:
- Extracting business logic to services
- Creating repository layers
- Separating route handlers

### High Risk Changes:
- Refactoring main extraction workflow
- Changing payment integration
- Modifying quota management logic
- Altering access control mechanisms

This analysis provides a comprehensive view of the current file structure and identifies specific opportunities for refactoring based on complexity and risk level.