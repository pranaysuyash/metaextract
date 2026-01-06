/**
 * User-Friendly Error Messaging System
 *
 * Provides progressive error disclosure with actionable guidance.
 * Replaces technical errors with helpful user messages.
 * Implements error recovery and retry mechanisms.
 *
 * @module error-messages
 * @validates Requirements 1.4, 3.4 - User-friendly error messaging
 */

// ============================================================================
// Error Types and Categories
// ============================================================================

export type ErrorCategory =
  | 'network'
  | 'upload'
  | 'processing'
  | 'authentication'
  | 'authorization'
  | 'validation'
  | 'server'
  | 'timeout'
  | 'quota'
  | 'unknown';

export type ErrorSeverity = 'info' | 'warning' | 'error' | 'critical';

export interface UserFriendlyError {
  /** Unique error code for tracking */
  code: string;
  /** Error category for grouping */
  category: ErrorCategory;
  /** Severity level */
  severity: ErrorSeverity;
  /** User-friendly title */
  title: string;
  /** User-friendly description */
  message: string;
  /** Actionable suggestions for the user */
  suggestions: string[];
  /** Whether the error is recoverable */
  recoverable: boolean;
  /** Retry configuration if recoverable */
  retry?: RetryConfig;
  /** Help article link */
  helpLink?: string;
  /** Original technical error (for logging) */
  technicalDetails?: string;
}

export interface RetryConfig {
  /** Maximum number of retry attempts */
  maxAttempts: number;
  /** Base delay in milliseconds */
  baseDelay: number;
  /** Whether to use exponential backoff */
  exponentialBackoff: boolean;
  /** Maximum delay cap in milliseconds */
  maxDelay?: number;
}

// ============================================================================
// Error Code Definitions
// ============================================================================

export const ERROR_CODES = {
  // Network errors
  NETWORK_OFFLINE: 'NET_001',
  NETWORK_TIMEOUT: 'NET_002',
  NETWORK_UNREACHABLE: 'NET_003',

  // Upload errors
  UPLOAD_FILE_TOO_LARGE: 'UPL_001',
  UPLOAD_INVALID_TYPE: 'UPL_002',
  UPLOAD_FAILED: 'UPL_003',
  UPLOAD_CANCELLED: 'UPL_004',
  UPLOAD_CORRUPTED: 'UPL_005',

  // Processing errors
  PROCESSING_FAILED: 'PRC_001',
  PROCESSING_TIMEOUT: 'PRC_002',
  PROCESSING_UNSUPPORTED: 'PRC_003',
  PROCESSING_PARTIAL: 'PRC_004',

  // Authentication errors
  AUTH_INVALID_CREDENTIALS: 'AUTH_001',
  AUTH_SESSION_EXPIRED: 'AUTH_002',
  AUTH_ACCOUNT_LOCKED: 'AUTH_003',
  AUTH_EMAIL_NOT_VERIFIED: 'AUTH_004',

  // Authorization errors
  AUTHZ_INSUFFICIENT_TIER: 'AUTHZ_001',
  AUTHZ_FEATURE_LOCKED: 'AUTHZ_002',
  AUTHZ_RATE_LIMITED: 'AUTHZ_003',

  // Validation errors
  VALIDATION_REQUIRED_FIELD: 'VAL_001',
  VALIDATION_INVALID_FORMAT: 'VAL_002',
  VALIDATION_OUT_OF_RANGE: 'VAL_003',

  // Server errors
  SERVER_INTERNAL: 'SRV_001',
  SERVER_MAINTENANCE: 'SRV_002',
  SERVER_OVERLOADED: 'SRV_003',

  // Quota errors
  QUOTA_EXCEEDED: 'QTA_001',
  QUOTA_DAILY_LIMIT: 'QTA_002',
  QUOTA_STORAGE_FULL: 'QTA_003',

  // Unknown
  UNKNOWN: 'UNK_001',
} as const;

export type ErrorCode = (typeof ERROR_CODES)[keyof typeof ERROR_CODES];

// ============================================================================
// Error Message Templates
// ============================================================================

const errorTemplates: Record<
  string,
  Omit<UserFriendlyError, 'technicalDetails'>
> = {
  // Network errors
  [ERROR_CODES.NETWORK_OFFLINE]: {
    code: ERROR_CODES.NETWORK_OFFLINE,
    category: 'network',
    severity: 'warning',
    title: "You're offline",
    message: "It looks like you've lost your internet connection.",
    suggestions: [
      'Check your Wi-Fi or mobile data connection',
      "Try refreshing the page once you're back online",
      'Your work will be saved locally and synced when reconnected',
    ],
    recoverable: true,
    retry: {
      maxAttempts: 5,
      baseDelay: 2000,
      exponentialBackoff: true,
      maxDelay: 30000,
    },
  },
  [ERROR_CODES.NETWORK_TIMEOUT]: {
    code: ERROR_CODES.NETWORK_TIMEOUT,
    category: 'timeout',
    severity: 'warning',
    title: 'Request timed out',
    message: 'The server is taking longer than expected to respond.',
    suggestions: [
      'Check your internet connection speed',
      'Try again in a few moments',
      'If the problem persists, the server may be experiencing high load',
    ],
    recoverable: true,
    retry: { maxAttempts: 3, baseDelay: 3000, exponentialBackoff: true },
  },
  [ERROR_CODES.NETWORK_UNREACHABLE]: {
    code: ERROR_CODES.NETWORK_UNREACHABLE,
    category: 'network',
    severity: 'error',
    title: 'Server unreachable',
    message: "We couldn't connect to our servers.",
    suggestions: [
      "Check if you're behind a firewall or VPN",
      'Try disabling browser extensions that might block requests',
      'Visit our status page to check for outages',
    ],
    recoverable: true,
    retry: { maxAttempts: 3, baseDelay: 5000, exponentialBackoff: true },
    helpLink: '/status',
  },

  // Upload errors
  [ERROR_CODES.UPLOAD_FILE_TOO_LARGE]: {
    code: ERROR_CODES.UPLOAD_FILE_TOO_LARGE,
    category: 'upload',
    severity: 'warning',
    title: 'File too large',
    message: 'The file you selected exceeds the maximum allowed size.',
    suggestions: [
      'Try compressing the file before uploading',
      'Split large files into smaller parts',
      'Upgrade your plan for larger file support',
    ],
    recoverable: false,
    helpLink: '/docs/file-limits',
  },
  [ERROR_CODES.UPLOAD_INVALID_TYPE]: {
    code: ERROR_CODES.UPLOAD_INVALID_TYPE,
    category: 'upload',
    severity: 'warning',
    title: 'Unsupported file type',
    message: "This file format isn't supported for metadata extraction.",
    suggestions: [
      'Check our supported formats list',
      'Convert the file to a supported format',
      'Contact support if you need this format added',
    ],
    recoverable: false,
    helpLink: '/docs/supported-formats',
  },
  [ERROR_CODES.UPLOAD_FAILED]: {
    code: ERROR_CODES.UPLOAD_FAILED,
    category: 'upload',
    severity: 'error',
    title: 'Upload failed',
    message: 'Something went wrong while uploading your file.',
    suggestions: [
      'Check your internet connection',
      'Try uploading the file again',
      'If the problem continues, try a different browser',
    ],
    recoverable: true,
    retry: { maxAttempts: 3, baseDelay: 1000, exponentialBackoff: false },
  },
  [ERROR_CODES.UPLOAD_CANCELLED]: {
    code: ERROR_CODES.UPLOAD_CANCELLED,
    category: 'upload',
    severity: 'info',
    title: 'Upload cancelled',
    message: 'The file upload was cancelled.',
    suggestions: ["You can start a new upload whenever you're ready"],
    recoverable: false,
  },
  [ERROR_CODES.UPLOAD_CORRUPTED]: {
    code: ERROR_CODES.UPLOAD_CORRUPTED,
    category: 'upload',
    severity: 'error',
    title: 'File appears corrupted',
    message: "We couldn't read this file. It may be damaged or incomplete.",
    suggestions: [
      'Try downloading the original file again',
      'Check if the file opens correctly on your computer',
      'Try a different copy of the file if available',
    ],
    recoverable: false,
  },

  // Processing errors
  [ERROR_CODES.PROCESSING_FAILED]: {
    code: ERROR_CODES.PROCESSING_FAILED,
    category: 'processing',
    severity: 'error',
    title: 'Processing failed',
    message:
      'We encountered an issue while extracting metadata from your file.',
    suggestions: [
      'Try uploading the file again',
      'Check if the file is valid and not corrupted',
      'Contact support if this keeps happening',
    ],
    recoverable: true,
    retry: { maxAttempts: 2, baseDelay: 2000, exponentialBackoff: false },
  },
  [ERROR_CODES.PROCESSING_TIMEOUT]: {
    code: ERROR_CODES.PROCESSING_TIMEOUT,
    category: 'timeout',
    severity: 'warning',
    title: 'Processing taking too long',
    message: 'Your file is taking longer than expected to process.',
    suggestions: [
      'Large or complex files may take more time',
      'You can wait or try again with a smaller file',
      'Results will be emailed if processing completes',
    ],
    recoverable: true,
    retry: { maxAttempts: 2, baseDelay: 5000, exponentialBackoff: true },
  },
  [ERROR_CODES.PROCESSING_UNSUPPORTED]: {
    code: ERROR_CODES.PROCESSING_UNSUPPORTED,
    category: 'processing',
    severity: 'warning',
    title: 'Limited metadata available',
    message: 'This file type has limited metadata extraction support.',
    suggestions: [
      'Basic metadata has been extracted',
      'Some advanced features may not be available',
      'Check our docs for full format support details',
    ],
    recoverable: false,
    helpLink: '/docs/format-support',
  },
  [ERROR_CODES.PROCESSING_PARTIAL]: {
    code: ERROR_CODES.PROCESSING_PARTIAL,
    category: 'processing',
    severity: 'info',
    title: 'Partial results available',
    message:
      "We extracted some metadata, but couldn't complete the full analysis.",
    suggestions: [
      'Review the available results below',
      'Some metadata categories may be incomplete',
      'Try re-uploading for a complete extraction',
    ],
    recoverable: true,
    retry: { maxAttempts: 1, baseDelay: 1000, exponentialBackoff: false },
  },

  // Authentication errors
  [ERROR_CODES.AUTH_INVALID_CREDENTIALS]: {
    code: ERROR_CODES.AUTH_INVALID_CREDENTIALS,
    category: 'authentication',
    severity: 'warning',
    title: 'Invalid credentials',
    message: 'The email or password you entered is incorrect.',
    suggestions: [
      'Double-check your email address',
      'Make sure Caps Lock is off',
      'Use "Forgot Password" to reset your password',
    ],
    recoverable: false,
    helpLink: '/forgot-password',
  },
  [ERROR_CODES.AUTH_SESSION_EXPIRED]: {
    code: ERROR_CODES.AUTH_SESSION_EXPIRED,
    category: 'authentication',
    severity: 'info',
    title: 'Session expired',
    message: 'Your session has expired for security reasons.',
    suggestions: [
      'Please sign in again to continue',
      'Your work has been saved',
    ],
    recoverable: false,
  },
  [ERROR_CODES.AUTH_ACCOUNT_LOCKED]: {
    code: ERROR_CODES.AUTH_ACCOUNT_LOCKED,
    category: 'authentication',
    severity: 'error',
    title: 'Account locked',
    message:
      'Your account has been temporarily locked due to multiple failed login attempts.',
    suggestions: [
      'Wait 15 minutes before trying again',
      'Use "Forgot Password" to reset your password',
      'Contact support if you need immediate access',
    ],
    recoverable: false,
    helpLink: '/support',
  },
  [ERROR_CODES.AUTH_EMAIL_NOT_VERIFIED]: {
    code: ERROR_CODES.AUTH_EMAIL_NOT_VERIFIED,
    category: 'authentication',
    severity: 'warning',
    title: 'Email not verified',
    message: 'Please verify your email address to continue.',
    suggestions: [
      'Check your inbox for the verification email',
      'Check your spam folder',
      'Click "Resend" to get a new verification email',
    ],
    recoverable: false,
  },

  // Authorization errors
  [ERROR_CODES.AUTHZ_INSUFFICIENT_TIER]: {
    code: ERROR_CODES.AUTHZ_INSUFFICIENT_TIER,
    category: 'authorization',
    severity: 'info',
    title: 'Feature requires upgrade',
    message: 'This feature is available on higher tier plans.',
    suggestions: [
      'View available plans to unlock this feature',
      'Start a free trial of our Pro plan',
      'Contact sales for enterprise options',
    ],
    recoverable: false,
    helpLink: '/#pricing',
  },
  [ERROR_CODES.AUTHZ_FEATURE_LOCKED]: {
    code: ERROR_CODES.AUTHZ_FEATURE_LOCKED,
    category: 'authorization',
    severity: 'info',
    title: 'Feature locked',
    message: "This feature isn't available on your current plan.",
    suggestions: [
      'Upgrade your plan to access this feature',
      "Check what's included in each plan",
    ],
    recoverable: false,
    helpLink: '/#pricing',
  },
  [ERROR_CODES.AUTHZ_RATE_LIMITED]: {
    code: ERROR_CODES.AUTHZ_RATE_LIMITED,
    category: 'authorization',
    severity: 'warning',
    title: 'Too many requests',
    message: "You've made too many requests. Please slow down.",
    suggestions: [
      'Wait a moment before trying again',
      'Upgrade your plan for higher rate limits',
    ],
    recoverable: true,
    retry: {
      maxAttempts: 3,
      baseDelay: 10000,
      exponentialBackoff: true,
      maxDelay: 60000,
    },
  },

  // Validation errors
  [ERROR_CODES.VALIDATION_REQUIRED_FIELD]: {
    code: ERROR_CODES.VALIDATION_REQUIRED_FIELD,
    category: 'validation',
    severity: 'warning',
    title: 'Required field missing',
    message: 'Please fill in all required fields.',
    suggestions: [
      'Look for fields marked with an asterisk (*)',
      'Make sure no required fields are empty',
    ],
    recoverable: false,
  },
  [ERROR_CODES.VALIDATION_INVALID_FORMAT]: {
    code: ERROR_CODES.VALIDATION_INVALID_FORMAT,
    category: 'validation',
    severity: 'warning',
    title: 'Invalid format',
    message: "The value you entered isn't in the correct format.",
    suggestions: [
      'Check the expected format for this field',
      'Remove any special characters if not allowed',
    ],
    recoverable: false,
  },
  [ERROR_CODES.VALIDATION_OUT_OF_RANGE]: {
    code: ERROR_CODES.VALIDATION_OUT_OF_RANGE,
    category: 'validation',
    severity: 'warning',
    title: 'Value out of range',
    message: 'The value you entered is outside the allowed range.',
    suggestions: [
      'Check the minimum and maximum allowed values',
      'Enter a value within the specified range',
    ],
    recoverable: false,
  },

  // Server errors
  [ERROR_CODES.SERVER_INTERNAL]: {
    code: ERROR_CODES.SERVER_INTERNAL,
    category: 'server',
    severity: 'error',
    title: 'Something went wrong',
    message: 'We encountered an unexpected error on our end.',
    suggestions: [
      'Try refreshing the page',
      'If the problem persists, please try again later',
      'Contact support if this keeps happening',
    ],
    recoverable: true,
    retry: { maxAttempts: 2, baseDelay: 3000, exponentialBackoff: true },
    helpLink: '/support',
  },
  [ERROR_CODES.SERVER_MAINTENANCE]: {
    code: ERROR_CODES.SERVER_MAINTENANCE,
    category: 'server',
    severity: 'info',
    title: 'Scheduled maintenance',
    message: "We're currently performing scheduled maintenance.",
    suggestions: [
      'Service will be restored shortly',
      'Check our status page for updates',
      "Your data is safe and will be available when we're back",
    ],
    recoverable: false,
    helpLink: '/status',
  },
  [ERROR_CODES.SERVER_OVERLOADED]: {
    code: ERROR_CODES.SERVER_OVERLOADED,
    category: 'server',
    severity: 'warning',
    title: 'High demand',
    message: 'Our servers are experiencing high demand right now.',
    suggestions: [
      'Please try again in a few minutes',
      'Your request has been queued',
      'Consider upgrading for priority processing',
    ],
    recoverable: true,
    retry: {
      maxAttempts: 3,
      baseDelay: 10000,
      exponentialBackoff: true,
      maxDelay: 60000,
    },
  },

  // Quota errors
  [ERROR_CODES.QUOTA_EXCEEDED]: {
    code: ERROR_CODES.QUOTA_EXCEEDED,
    category: 'quota',
    severity: 'warning',
    title: 'Usage limit reached',
    message: "You've reached your plan's usage limit.",
    suggestions: [
      'Upgrade your plan for more extractions',
      'Wait until your quota resets',
      'View your usage in account settings',
    ],
    recoverable: false,
    helpLink: '/#pricing',
  },
  [ERROR_CODES.QUOTA_DAILY_LIMIT]: {
    code: ERROR_CODES.QUOTA_DAILY_LIMIT,
    category: 'quota',
    severity: 'info',
    title: 'Daily limit reached',
    message: "You've used all your extractions for today.",
    suggestions: [
      'Your limit resets at midnight UTC',
      'Upgrade for unlimited daily extractions',
    ],
    recoverable: false,
    helpLink: '/#pricing',
  },
  [ERROR_CODES.QUOTA_STORAGE_FULL]: {
    code: ERROR_CODES.QUOTA_STORAGE_FULL,
    category: 'quota',
    severity: 'warning',
    title: 'Storage full',
    message: "You've used all your available storage.",
    suggestions: [
      'Delete old results to free up space',
      'Export and download results you want to keep',
      'Upgrade for more storage',
    ],
    recoverable: false,
    helpLink: '/settings/storage',
  },

  // Unknown error
  [ERROR_CODES.UNKNOWN]: {
    code: ERROR_CODES.UNKNOWN,
    category: 'unknown',
    severity: 'error',
    title: 'Unexpected error',
    message: 'Something unexpected happened.',
    suggestions: [
      'Try refreshing the page',
      'If the problem persists, contact support',
    ],
    recoverable: true,
    retry: { maxAttempts: 1, baseDelay: 2000, exponentialBackoff: false },
    helpLink: '/support',
  },
};

// ============================================================================
// Error Detection and Mapping
// ============================================================================

/**
 * Map HTTP status codes to error codes
 */
export function mapHttpStatusToErrorCode(status: number): ErrorCode {
  switch (status) {
    case 400:
      return ERROR_CODES.VALIDATION_INVALID_FORMAT;
    case 401:
      return ERROR_CODES.AUTH_SESSION_EXPIRED;
    case 403:
      return ERROR_CODES.AUTHZ_FEATURE_LOCKED;
    case 404:
      return ERROR_CODES.UNKNOWN;
    case 408:
      return ERROR_CODES.NETWORK_TIMEOUT;
    case 413:
      return ERROR_CODES.UPLOAD_FILE_TOO_LARGE;
    case 415:
      return ERROR_CODES.UPLOAD_INVALID_TYPE;
    case 422:
      return ERROR_CODES.VALIDATION_INVALID_FORMAT;
    case 429:
      return ERROR_CODES.AUTHZ_RATE_LIMITED;
    case 500:
      return ERROR_CODES.SERVER_INTERNAL;
    case 502:
      return ERROR_CODES.SERVER_OVERLOADED;
    case 503:
      return ERROR_CODES.SERVER_MAINTENANCE;
    case 504:
      return ERROR_CODES.NETWORK_TIMEOUT;
    default:
      return status >= 500 ? ERROR_CODES.SERVER_INTERNAL : ERROR_CODES.UNKNOWN;
  }
}

/**
 * Detect error type from various error sources
 */
export function detectErrorCode(error: unknown): ErrorCode {
  // Handle null/undefined
  if (!error) return ERROR_CODES.UNKNOWN;

  // Handle Error objects
  if (error instanceof Error) {
    const message = error.message.toLowerCase();

    // Network errors
    if (message.includes('network') || message.includes('fetch')) {
      if (message.includes('offline') || !navigator.onLine) {
        return ERROR_CODES.NETWORK_OFFLINE;
      }
      return ERROR_CODES.NETWORK_UNREACHABLE;
    }

    // Timeout errors
    if (message.includes('timeout') || message.includes('timed out')) {
      return ERROR_CODES.NETWORK_TIMEOUT;
    }

    // Abort errors
    if (message.includes('abort') || error.name === 'AbortError') {
      return ERROR_CODES.UPLOAD_CANCELLED;
    }
  }

  // Handle response-like objects
  if (typeof error === 'object' && error !== null) {
    const obj = error as Record<string, unknown>;

    // Check for status code
    if (typeof obj.status === 'number') {
      return mapHttpStatusToErrorCode(obj.status);
    }

    // Check for error code
    if (typeof obj.code === 'string' && obj.code in ERROR_CODES) {
      return obj.code as ErrorCode;
    }
  }

  return ERROR_CODES.UNKNOWN;
}

// ============================================================================
// Error Message Generation
// ============================================================================

/**
 * Get a user-friendly error from an error code
 */
export function getUserFriendlyError(
  code: ErrorCode,
  technicalDetails?: string
): UserFriendlyError {
  const template = errorTemplates[code] || errorTemplates[ERROR_CODES.UNKNOWN];
  return {
    ...template,
    technicalDetails,
  };
}

/**
 * Convert any error to a user-friendly error
 */
export function toUserFriendlyError(error: unknown): UserFriendlyError {
  const code = detectErrorCode(error);
  let technicalDetails: string;

  if (error instanceof Error) {
    technicalDetails = `${error.name}: ${error.message}`;
  } else {
    try {
      technicalDetails =
        typeof error === 'string' ? error : JSON.stringify(error);
    } catch (_) {
      try {
        technicalDetails = String(error as any);
      } catch (_) {
        technicalDetails = '<unserializable error>';
      }
    }
  }

  return getUserFriendlyError(code, technicalDetails);
}

/**
 * Create a custom user-friendly error
 */
export function createUserFriendlyError(
  options: Partial<UserFriendlyError> & { title: string; message: string }
): UserFriendlyError {
  return {
    code: options.code || ERROR_CODES.UNKNOWN,
    category: options.category || 'unknown',
    severity: options.severity || 'error',
    title: options.title,
    message: options.message,
    suggestions: options.suggestions || [],
    recoverable: options.recoverable ?? false,
    retry: options.retry,
    helpLink: options.helpLink,
    technicalDetails: options.technicalDetails,
  };
}

// ============================================================================
// Retry Logic
// ============================================================================

/**
 * Calculate delay for retry attempt
 */
export function calculateRetryDelay(
  attempt: number,
  config: RetryConfig
): number {
  if (!config.exponentialBackoff) {
    return config.baseDelay;
  }

  const delay = config.baseDelay * Math.pow(2, attempt - 1);
  return config.maxDelay ? Math.min(delay, config.maxDelay) : delay;
}

/**
 * Check if an error should be retried
 */
export function shouldRetry(
  error: UserFriendlyError,
  currentAttempt: number
): boolean {
  if (!error.recoverable || !error.retry) {
    return false;
  }
  return currentAttempt < error.retry.maxAttempts;
}

/**
 * Execute a function with automatic retry
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  errorCode: ErrorCode = ERROR_CODES.UNKNOWN,
  onRetry?: (attempt: number, delay: number) => void
): Promise<T> {
  const error = getUserFriendlyError(errorCode);
  let attempt = 0;

  while (true) {
    try {
      return await fn();
    } catch (e) {
      attempt++;
      const userError = toUserFriendlyError(e);

      if (!shouldRetry(userError, attempt)) {
        throw userError;
      }

      const delay = calculateRetryDelay(attempt, userError.retry!);
      onRetry?.(attempt, delay);

      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

// ============================================================================
// Error Display Utilities
// ============================================================================

/**
 * Get icon name for error severity
 */
export function getErrorIcon(severity: ErrorSeverity): string {
  switch (severity) {
    case 'info':
      return 'info';
    case 'warning':
      return 'alert-triangle';
    case 'error':
      return 'x-circle';
    case 'critical':
      return 'alert-octagon';
  }
}

/**
 * Get color class for error severity
 */
export function getErrorColorClass(severity: ErrorSeverity): string {
  switch (severity) {
    case 'info':
      return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
    case 'warning':
      return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
    case 'error':
      return 'text-red-500 bg-red-500/10 border-red-500/20';
    case 'critical':
      return 'text-red-600 bg-red-600/10 border-red-600/20';
  }
}

/**
 * Format error for logging (includes technical details)
 */
export function formatErrorForLogging(error: UserFriendlyError): string {
  return JSON.stringify({
    code: error.code,
    category: error.category,
    severity: error.severity,
    title: error.title,
    technicalDetails: error.technicalDetails,
    timestamp: new Date().toISOString(),
  });
}

/**
 * Format error for display (user-friendly)
 */
export function formatErrorForDisplay(error: UserFriendlyError): string {
  return `${error.title}: ${error.message}`;
}

// ============================================================================
// Export All
// ============================================================================

export const errorMessages = {
  ERROR_CODES,
  errorTemplates,
  mapHttpStatusToErrorCode,
  detectErrorCode,
  getUserFriendlyError,
  toUserFriendlyError,
  createUserFriendlyError,
  calculateRetryDelay,
  shouldRetry,
  withRetry,
  getErrorIcon,
  getErrorColorClass,
  formatErrorForLogging,
  formatErrorForDisplay,
} as const;

export default errorMessages;
