/**
 * Toast helper utilities for consistent error and success messaging
 * Reduces duplication and ensures consistent UX across the application
 */

export interface ToastPayload {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
  action?: React.ReactNode;
}

export interface ToastMessage {
  title: string;
  description: string;
  variant?: 'default' | 'destructive';
  action?: React.ReactNode;
}

/**
 * Show a file validation error toast
 */
export function showFileValidationError(
  toast: (props: any) => void,
  reason: 'processing' | 'validation' | 'expired' | 'failed'
): void {
  const messages: Record<string, ToastMessage> = {
    processing: {
      title: 'Unable to process file',
      description:
        "We couldn't validate this file. Please check the file format and try again.",
      variant: 'destructive',
    },
    validation: {
      title: 'File validation needed',
      description: 'Please select your file again to continue.',
      variant: 'destructive',
    },
    expired: {
      title: 'File validation expired',
      description: 'Please select your file again to continue.',
      variant: 'destructive',
    },
    failed: {
      title: 'File validation failed',
      description: 'Please select the file again to continue.',
      variant: 'destructive',
    },
  };

  const message = messages[reason];
  if (message) {
    toast(message);
  }
}

/**
 * Show a file rejection toast with specific reason
 */
export function showFileRejectionError(
  toast: (props: any) => void,
  reason: 'too_large' | 'megapixels' | 'unsupported' | 'blocked',
  maxMb?: number
): void {
  const messages: Record<string, ToastMessage> = {
    too_large: {
      title: 'File too large',
      description: maxMb ? `Max ${maxMb} MB.` : 'File size exceeds the limit.',
      variant: 'destructive',
    },
    megapixels: {
      title: 'Upload blocked',
      description: 'Image resolution exceeds the supported limit.',
      variant: 'destructive',
    },
    unsupported: {
      title: 'Upload blocked',
      description: 'Unsupported file type.',
      variant: 'destructive',
    },
    blocked: {
      title: 'Upload blocked',
      description: 'Unsupported file type.',
      variant: 'destructive',
    },
  };

  const message = messages[reason];
  if (message) {
    toast(message);
  }
}

/**
 * Show a file type not supported error with format guidance
 */
export function showFileTypeError(
  toast: (props: any) => void,
  status?: number
): void {
  toast({
    title: 'File type not supported',
    description:
      'Please upload a JPG, PNG, GIF, WebP, HEIC, TIFF, or BMP image instead.',
    variant: 'destructive',
  });
}

/**
 * Show a security error toast
 */
export function showSecurityError(
  toast: (props: any) => void,
  message?: string
): void {
  toast({
    title: 'Upload blocked',
    description:
      message || 'For security reasons, this file type is not permitted.',
    variant: 'destructive',
  });
}

/**
 * Show a generic upload error with smart fallback
 */
export function showUploadError(
  toast: (props: any) => void,
  errorMessage: string,
  isDev = false
): void {
  toast({
    title: 'Upload failed',
    description:
      errorMessage.length > 100 || errorMessage.includes('Error:')
        ? "We couldn't upload your file. Please try again or contact support if this continues."
        : errorMessage,
    variant: 'destructive',
  });
}

/**
 * Show a service availability error
 */
export function showServiceError(
  toast: (props: any) => void,
  isDev = false
): void {
  toast({
    title: 'Service unavailable',
    description: isDev
      ? 'Backend server not running. Start with `npm run dev:server`'
      : 'Service temporarily unavailable. Please try again in a few moments.',
    variant: 'destructive',
  });
}

/**
 * Show a credit/paywall error
 */
export function showPaywallError(toast: (props: any) => void): void {
  toast({
    title: 'Free uploads used',
    description: "You've used your free uploads. Purchase credits to continue.",
    variant: 'destructive',
  });
}

/**
 * Show a success message
 */
export function showSuccessMessage(
  toast: (props: any) => void,
  title: string,
  description: string
): void {
  toast({
    title,
    description,
    variant: 'default',
  });
}

/**
 * Show credits added confirmation
 */
export function showCreditsAdded(
  toast: (props: any) => void,
  credits: number
): void {
  toast({
    title: 'Credits added successfully',
    description: `You now have ${credits} upload${credits !== 1 ? 's' : ''} available.`,
    variant: 'default',
  });
}

/**
 * Show a feature coming soon message
 */
export function showFeatureComingSoon(
  toast: (props: any) => void,
  featureName: string
): void {
  toast({
    title: `${featureName} coming soon`,
    description: `${featureName} functionality will be available shortly.`,
    variant: 'default',
  });
}
