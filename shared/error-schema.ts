/**
 * Standardized Error Response Schema
 *
 * Provides consistent error response format across all API endpoints.
 * Ensures clients can reliably parse and handle API errors.
 *
 * Usage:
 *   - Server: Use ValidationErrorResponse for validation failures
 *   - Server: Use ApiErrorResponse for business logic errors
 *   - Client: Parse errors consistently with mapApiErrorToUserFriendly()
 */

import { z } from 'zod';

/**
 * Validation error for a single field
 */
export const ValidationFieldErrorSchema = z.object({
  field: z.string().describe('Field name that failed validation'),
  message: z.string().describe('User-friendly validation message'),
  code: z.string().optional().describe('Machine-readable error code'),
  received: z.unknown().optional().describe('The value that was received'),
});

export type ValidationFieldError = z.infer<typeof ValidationFieldErrorSchema>;

/**
 * Standard API error response format
 *
 * Used for:
 * - Validation errors (400)
 * - Authorization errors (401/403)
 * - Business logic errors (400/403/409)
 * - Server errors (500)
 */
export const ApiErrorResponseSchema = z.object({
  error: z.object({
    code: z.string().describe('Machine-readable error code'),
    message: z.string().describe('User-friendly error message'),
    status: z.number().describe('HTTP status code'),
    timestamp: z.string().describe('ISO 8601 timestamp'),
    requestId: z.string().optional().describe('Request ID for tracking'),
    details: z.unknown().optional().describe('Additional error details'),
    context: z.record(z.unknown()).optional().describe('Request context'),
  }),
});

export type ApiErrorResponse = z.infer<typeof ApiErrorResponseSchema>;

/**
 * Validation error response (400)
 *
 * Used when request validation fails.
 * Includes field-level errors for better client guidance.
 */
export const ValidationErrorResponseSchema = z.object({
  error: z.object({
    code: z.literal('VALIDATION_ERROR').describe('Error code'),
    message: z.string().describe('Summary message'),
    status: z.literal(400).describe('HTTP status code'),
    timestamp: z.string().describe('ISO 8601 timestamp'),
    requestId: z.string().optional().describe('Request ID for tracking'),
    fields: z
      .array(ValidationFieldErrorSchema)
      .describe('Field-level validation errors'),
    context: z
      .record(z.unknown())
      .optional()
      .describe('Request context'),
  }),
});

export type ValidationErrorResponse = z.infer<
  typeof ValidationErrorResponseSchema
>;

/**
 * Error codes for standardized responses
 */
export const ERROR_CODES = {
  // Validation errors
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_REQUEST: 'INVALID_REQUEST',

  // Authentication/Authorization
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  AUTHENTICATION_FAILED: 'AUTHENTICATION_FAILED',
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  SESSION_EXPIRED: 'SESSION_EXPIRED',

  // File/Upload errors
  FILE_NOT_FOUND: 'FILE_NOT_FOUND',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  FILE_UPLOAD_FAILED: 'FILE_UPLOAD_FAILED',

  // Tier/Quota errors
  TIER_INSUFFICIENT: 'TIER_INSUFFICIENT',
  QUOTA_EXCEEDED: 'QUOTA_EXCEEDED',
  CREDITS_INSUFFICIENT: 'CREDITS_INSUFFICIENT',

  // Server errors
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  TIMEOUT: 'TIMEOUT',

  // Business logic errors
  CONFLICT: 'CONFLICT',
  NOT_FOUND: 'NOT_FOUND',
  ALREADY_EXISTS: 'ALREADY_EXISTS',
} as const;

export type ErrorCode = (typeof ERROR_CODES)[keyof typeof ERROR_CODES];

/**
 * Map HTTP status codes to error codes
 */
export function statusToErrorCode(status: number): ErrorCode {
  switch (status) {
    case 400:
      return 'INVALID_REQUEST';
    case 401:
      return 'UNAUTHORIZED';
    case 403:
      return 'FORBIDDEN';
    case 404:
      return 'NOT_FOUND';
    case 409:
      return 'CONFLICT';
    case 429:
      return 'QUOTA_EXCEEDED';
    case 500:
      return 'INTERNAL_ERROR';
    case 503:
      return 'SERVICE_UNAVAILABLE';
    default:
      return 'INTERNAL_ERROR';
  }
}
