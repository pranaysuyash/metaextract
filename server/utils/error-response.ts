/**
 * Server-Side Error Response Utilities
 *
 * Standardizes error responses across all API endpoints.
 * Handles validation errors, business logic errors, and server errors.
 *
 * Usage:
 *   res.status(400).json(createValidationErrorResponse([...fieldErrors]))
 *   res.status(403).json(createApiErrorResponse('TIER_INSUFFICIENT', message, 403))
 */

import type { Response } from 'express';
import { ZodError } from 'zod';
import type {
  ApiErrorResponse,
  ValidationErrorResponse,
  ValidationFieldError,
  ErrorCode,
} from '@shared/error-schema';

/**
 * Generate a unique request ID for error tracking
 */
function generateRequestId(): string {
  return `REQ-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get current ISO timestamp
 */
function getCurrentTimestamp(): string {
  return new Date().toISOString();
}

/**
 * Create a standard API error response
 *
 * @param code - Machine-readable error code
 * @param message - User-friendly error message
 * @param status - HTTP status code
 * @param details - Optional additional details
 * @param context - Optional request context
 * @returns Standard error response
 */
export function createApiErrorResponse(
  code: ErrorCode,
  message: string,
  status: number,
  details?: unknown,
  context?: Record<string, unknown>
): ApiErrorResponse {
  return {
    error: {
      code,
      message,
      status,
      timestamp: getCurrentTimestamp(),
      requestId: generateRequestId(),
      ...(details !== undefined && details !== null ? { details } : {}),
      ...(context && { context }),
    },
  };
}

/**
 * Convert Zod validation errors to field errors
 *
 * @param zodError - Zod validation error
 * @returns Array of field validation errors
 */
export function zodsErrorToFieldErrors(
  zodError: ZodError
): ValidationFieldError[] {
  return zodError.errors.map(error => {
    const fieldError: ValidationFieldError = {
      field: error.path.join('.') || 'unknown',
      message: error.message,
      code: error.code,
    };
    // Some Zod error types have 'received' property
    if ('received' in error) {
      fieldError.received = (error as any).received;
    }
    return fieldError;
  });
}

/**
 * Create a validation error response (400)
 *
 * @param fieldErrors - Array of field validation errors
 * @param context - Optional request context
 * @returns Validation error response
 */
export function createValidationErrorResponse(
  fieldErrors: ValidationFieldError[],
  context?: Record<string, unknown>
): ValidationErrorResponse {
  const errorCount = fieldErrors.length;
  const message =
    errorCount === 1
      ? `Validation failed: ${fieldErrors[0].message}`
      : `Validation failed on ${errorCount} field${errorCount > 1 ? 's' : ''}`;

  return {
    error: {
      code: 'VALIDATION_ERROR',
      message,
      status: 400,
      timestamp: getCurrentTimestamp(),
      requestId: generateRequestId(),
      fields: fieldErrors,
      ...(context && { context }),
    },
  };
}

/**
 * Create a validation error response from Zod error
 *
 * @param zodError - Zod validation error
 * @param context - Optional request context
 * @returns Validation error response
 */
export function createValidationErrorResponseFromZod(
  zodError: ZodError,
  context?: Record<string, unknown>
): ValidationErrorResponse {
  const fieldErrors = zodsErrorToFieldErrors(zodError);
  return createValidationErrorResponse(fieldErrors, context);
}

/**
 * Send an error response and handle response state
 *
 * @param res - Express response object
 * @param status - HTTP status code
 * @param code - Error code
 * @param message - Error message
 * @param details - Optional additional details
 * @param context - Optional request context
 */
export function sendErrorResponse(
  res: Response,
  status: number,
  code: ErrorCode,
  message: string,
  details?: unknown,
  context?: Record<string, unknown>
): Response {
  const response = createApiErrorResponse(
    code,
    message,
    status,
    details,
    context
  );
  return res.status(status).json(response);
}

/**
 * Send a validation error response
 *
 * @param res - Express response object
 * @param fieldErrors - Array of field validation errors
 * @param context - Optional request context
 */
export function sendValidationErrorResponse(
  res: Response,
  fieldErrors: ValidationFieldError[],
  context?: Record<string, unknown>
): Response {
  const response = createValidationErrorResponse(fieldErrors, context);
  return res.status(400).json(response);
}

/**
 * Send a validation error response from Zod error
 *
 * @param res - Express response object
 * @param zodError - Zod validation error
 * @param context - Optional request context
 */
export function sendValidationErrorResponseFromZod(
  res: Response,
  zodError: ZodError,
  context?: Record<string, unknown>
): Response {
  const response = createValidationErrorResponseFromZod(zodError, context);
  return res.status(400).json(response);
}

/**
 * Common error response helpers for specific scenarios
 */

export function sendInvalidRequestError(
  res: Response,
  message: string,
  details?: any
): Response {
  return sendErrorResponse(res, 400, 'INVALID_REQUEST', message, details);
}

export function sendUnauthorizedError(
  res: Response,
  message: string = 'Authentication required'
): Response {
  return sendErrorResponse(res, 401, 'UNAUTHORIZED', message);
}

export function sendForbiddenError(
  res: Response,
  message: string = 'Access denied'
): Response {
  return sendErrorResponse(res, 403, 'FORBIDDEN', message);
}

export function sendTierInsufficientError(
  res: Response,
  requiredTier: string,
  currentTier: string = 'free'
): Response {
  return sendErrorResponse(
    res,
    403,
    'TIER_INSUFFICIENT',
    `This feature requires ${requiredTier} tier`,
    { required_tier: requiredTier, current_tier: currentTier }
  );
}

export function sendQuotaExceededError(
  res: Response,
  reason: string = 'Quota exceeded'
): Response {
  return sendErrorResponse(res, 402, 'QUOTA_EXCEEDED', reason);
}

export function sendFileTooLargeError(
  res: Response,
  fileSizeMB: number,
  maxSizeMB: number,
  currentTier?: string
): Response {
  return sendErrorResponse(
    res,
    413,
    'FILE_TOO_LARGE',
    `File size exceeds limit`,
    {
      file_size_mb: fileSizeMB,
      max_size_mb: maxSizeMB,
    },
    currentTier ? { current_tier: currentTier } : undefined
  );
}

/**
 * Tier-aware file-too-large response (403)
 * Used by endpoints that enforce size limits as a tier restriction rather than a transport-level limit.
 */
export function sendFileTooLargeForTier(
  res: Response,
  fileSizeMB: number,
  maxSizeMB: number,
  currentTier?: string
): Response {
  return sendErrorResponse(
    res,
    403,
    'FILE_TOO_LARGE',
    `File size exceeds limit`,
    {
      file_size_mb: fileSizeMB,
      max_size_mb: maxSizeMB,
    },
    currentTier ? { current_tier: currentTier } : undefined
  );
}

/**
 * Legacy flat file-too-large response (413)
 * Some legacy file-filter endpoints expect a flat error shape (back-compat).
 */
export function sendLegacyFileTooLargeError(
  res: Response,
  message: string = 'File too large'
): Response {
  // Historic endpoints expect a flat error shape; keep compatibility for file-filter errors
  return res.status(413).json({
    error: message,
    code: 'FILE_TOO_LARGE',
  });
}

export function sendInvalidFileTypeError(
  res: Response,
  mimeType: string,
  requiredTier?: string,
  currentTier?: string
): Response {
  return sendErrorResponse(
    res,
    403,
    'INVALID_FILE_TYPE',
    `File type not allowed`,
    {
      mime_type: mimeType,
      ...(requiredTier && { required_tier: requiredTier }),
    },
    currentTier ? { current_tier: currentTier } : undefined
  );
}

export function sendUnsupportedFileTypeError(
  res: Response,
  message: string = 'File type not permitted'
): Response {
  // Historic endpoints expect a flat error shape; keep compatibility for file-filter errors
  return res.status(403).json({
    error: 'Unsupported file type',
    message,
    code: 'UNSUPPORTED_FILE_TYPE',
  });
}

export function sendInternalServerError(
  res: Response,
  message: string = 'Internal server error',
  details?: unknown
): Response {
  return sendErrorResponse(res, 500, 'INTERNAL_ERROR', message, details);
}

export function sendServiceUnavailableError(
  res: Response,
  message: string = 'Service temporarily unavailable'
): Response {
  return sendErrorResponse(res, 503, 'SERVICE_UNAVAILABLE', message);
}
