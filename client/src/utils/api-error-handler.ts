/**
 * Client-Side API Error Handler
 *
 * Converts standardized API error responses to user-friendly messages.
 * Integrates with the existing error-messages system.
 *
 * Usage:
 *   try {
 *     const response = await fetch('/api/extract', { ... });
 *     if (!response.ok) {
 *       throw await parseApiError(response);
 *     }
 *   } catch (error) {
 *     const userFriendly = mapApiErrorToUserFriendly(error);
 *     showErrorToUser(userFriendly);
 *   }
 */

// Type definitions from shared schema for reference

export interface ApiError {
  code: string;
  message: string;
  status: number;
  timestamp: string;
  requestId?: string;
  details?: unknown;
  context?: Record<string, unknown>;
  fields?: Array<{
    field: string;
    message: string;
    code?: string;
    received?: unknown;
  }>;
}

/**
 * Parse API error response from a failed fetch
 *
 * @param response - Fetch Response object
 * @returns Parsed API error
 */
export async function parseApiError(response: Response): Promise<ApiError> {
  const contentType = response.headers.get('content-type');
  const isJson = contentType?.includes('application/json');

  let body: unknown;
  try {
    body = isJson ? await response.json() : await response.text();
  } catch {
    body = null;
  }

  // Handle standardized API error response
  if (
    body &&
    typeof body === 'object' &&
    'error' in body
  ) {
    const error = body as Record<string, unknown>;
    const errorData = error.error as Record<string, unknown>;
    return {
      code: (errorData.code as string) || 'UNKNOWN_ERROR',
      message: (errorData.message as string) || response.statusText,
      status: (errorData.status as number) || response.status,
      timestamp: (errorData.timestamp as string) || new Date().toISOString(),
      requestId: errorData.requestId as string | undefined,
      details: errorData.details,
      context: errorData.context as Record<string, unknown> | undefined,
      fields: errorData.fields as ApiError['fields'],
    };
  }

  // Fallback for non-standard responses
  return {
    code: `HTTP_${response.status}`,
    message: typeof body === 'string' ? body : response.statusText,
    status: response.status,
    timestamp: new Date().toISOString(),
    details: body,
  };
}

/**
 * Check if error is a validation error
 */
export function isValidationError(error: ApiError): error is ApiError & {
  fields: Array<{ field: string; message: string; code?: string }>;
} {
  return error.code === 'VALIDATION_ERROR' && Array.isArray(error.fields);
}

/**
 * Check if error is an authentication error
 */
export function isAuthenticationError(error: ApiError): boolean {
  return error.status === 401 || error.code === 'UNAUTHORIZED';
}

/**
 * Check if error is an authorization error
 */
export function isAuthorizationError(error: ApiError): boolean {
  return (
    error.status === 403 ||
    error.code === 'FORBIDDEN' ||
    error.code === 'TIER_INSUFFICIENT'
  );
}

/**
 * Check if error is a file-related error
 */
export function isFileError(error: ApiError): boolean {
  return ['FILE_NOT_FOUND', 'FILE_TOO_LARGE', 'INVALID_FILE_TYPE'].includes(
    error.code
  );
}

/**
 * Check if error is a quota/credit error
 */
export function isQuotaError(error: ApiError): boolean {
  return (
    error.status === 429 ||
    error.status === 402 ||
    error.code === 'QUOTA_EXCEEDED' ||
    error.code === 'CREDITS_INSUFFICIENT'
  );
}

/**
 * Get user-friendly error title
 */
export function getErrorTitle(error: ApiError): string {
  if (isValidationError(error)) {
    return 'Validation Error';
  }
  if (isAuthenticationError(error)) {
    return 'Authentication Required';
  }
  if (isAuthorizationError(error)) {
    return 'Access Denied';
  }
  if (isFileError(error)) {
    return 'File Error';
  }
  if (isQuotaError(error)) {
    return 'Quota Exceeded';
  }

  switch (error.status) {
    case 400:
      return 'Invalid Request';
    case 404:
      return 'Not Found';
    case 409:
      return 'Conflict';
    case 500:
      return 'Server Error';
    case 503:
      return 'Service Unavailable';
    default:
      return 'Error';
  }
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: ApiError): string {
  if (isValidationError(error)) {
    const fields = error.fields || [];
    if (fields.length === 1) {
      return `${fields[0].field}: ${fields[0].message}`;
    } else if (fields.length > 1) {
      return `Validation failed on ${fields.length} field${fields.length > 1 ? 's' : ''}`;
    }
  }

  if (isAuthenticationError(error)) {
    return 'Your session has expired. Please log in again.';
  }

  if (isAuthorizationError(error)) {
    if (error.code === 'TIER_INSUFFICIENT') {
      return 'This feature requires a higher subscription tier.';
    }
    return 'You do not have permission to perform this action.';
  }

  if (isFileError(error)) {
    switch (error.code) {
      case 'FILE_TOO_LARGE':
        return `File size exceeds the maximum limit for your plan.`;
      case 'INVALID_FILE_TYPE':
        return 'This file type is not supported for your subscription tier.';
      default:
        return 'There was a problem with the file.';
    }
  }

  if (isQuotaError(error)) {
    return 'You have exceeded your quota or insufficient credits. Please upgrade or purchase credits.';
  }

  return error.message || 'An unexpected error occurred.';
}

/**
 * Get suggested user actions for an error
 */
export function getErrorSuggestions(error: ApiError): string[] {
  if (isValidationError(error)) {
    return ['Please check your input and try again'];
  }

  if (isAuthenticationError(error)) {
    return ['Log in again', 'Check your credentials'];
  }

  if (isAuthorizationError(error)) {
    if (error.code === 'TIER_INSUFFICIENT') {
      return ['Upgrade your subscription', 'Contact support'];
    }
    return ['Contact support for access'];
  }

  if (isFileError(error)) {
    if (error.code === 'FILE_TOO_LARGE') {
      return ['Try a smaller file', 'Upgrade to a higher tier'];
    }
    return ['Use a supported file type', 'Check the documentation'];
  }

  if (isQuotaError(error)) {
    return ['Upgrade your subscription', 'Purchase additional credits', 'Try again later'];
  }

  if (error.status >= 500) {
    return ['Try again later', 'Contact support if the problem persists'];
  }

  return ['Try again', 'Contact support if the problem persists'];
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: ApiError): boolean {
  // Retryable status codes
  if ([408, 429, 500, 502, 503, 504].includes(error.status)) {
    return true;
  }

  // Retryable error codes
  if (['TIMEOUT', 'SERVICE_UNAVAILABLE', 'INTERNAL_ERROR'].includes(error.code)) {
    return true;
  }

  return false;
}

/**
 * Extract field-level errors for form validation
 */
export function getFormErrors(
  error: ApiError
): Record<string, string> {
  const formErrors: Record<string, string> = {};

  if (isValidationError(error) && error.fields) {
    error.fields.forEach((field) => {
      formErrors[field.field] = field.message;
    });
  }

  return formErrors;
}
