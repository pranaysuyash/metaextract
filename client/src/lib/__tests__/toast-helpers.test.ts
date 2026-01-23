/**
 * Toast Helper Tests
 *
 * Tests for toast helper utilities
 */

import {
  showFileValidationError,
  showFileRejectionError,
  showFileTypeError,
  showSecurityError,
  showUploadError,
  showServiceError,
  showPaywallError,
  showSuccessMessage,
  showCreditsAdded,
  showFeatureComingSoon,
} from '../toast-helpers';

describe('Toast Helpers', () => {
  describe('showFileValidationError', () => {
    it('should show processing error', () => {
      const mockToast = jest.fn();
      showFileValidationError(mockToast, 'processing');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Unable to process file',
        description:
          "We couldn't validate this file. Please check the file format and try again.",
        variant: 'destructive',
      });
    });

    it('should show validation error', () => {
      const mockToast = jest.fn();
      showFileValidationError(mockToast, 'validation');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File validation needed',
        description: 'Please select your file again to continue.',
        variant: 'destructive',
      });
    });

    it('should show expired error', () => {
      const mockToast = jest.fn();
      showFileValidationError(mockToast, 'expired');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File validation expired',
        description: 'Please select your file again to continue.',
        variant: 'destructive',
      });
    });

    it('should show failed error', () => {
      const mockToast = jest.fn();
      showFileValidationError(mockToast, 'failed');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File validation failed',
        description: 'Please select the file again to continue.',
        variant: 'destructive',
      });
    });
  });

  describe('showFileRejectionError', () => {
    it('should show too_large error with maxMb', () => {
      const mockToast = jest.fn();
      showFileRejectionError(mockToast, 'too_large', 10);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File too large',
        description: 'Max 10 MB.',
        variant: 'destructive',
      });
    });

    it('should show too_large error without maxMb', () => {
      const mockToast = jest.fn();
      showFileRejectionError(mockToast, 'too_large');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File too large',
        description: 'File size exceeds the limit.',
        variant: 'destructive',
      });
    });

    it('should show megapixels error', () => {
      const mockToast = jest.fn();
      showFileRejectionError(mockToast, 'megapixels');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Upload blocked',
        description: 'Image resolution exceeds the supported limit.',
        variant: 'destructive',
      });
    });

    it('should show unsupported error', () => {
      const mockToast = jest.fn();
      showFileRejectionError(mockToast, 'unsupported');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Upload blocked',
        description: 'Unsupported file type.',
        variant: 'destructive',
      });
    });

    it('should show blocked error', () => {
      const mockToast = jest.fn();
      showFileRejectionError(mockToast, 'blocked');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Upload blocked',
        description: 'Unsupported file type.',
        variant: 'destructive',
      });
    });
  });

  describe('showFileTypeError', () => {
    it('should show generic file type error', () => {
      const mockToast = jest.fn();
      showFileTypeError(mockToast);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File type not supported',
        description:
          'Please upload a JPG, PNG, GIF, WebP, HEIC, TIFF, or BMP image instead.',
        variant: 'destructive',
      });
    });

    it('should show file type error regardless of status code', () => {
      const mockToast = jest.fn();
      showFileTypeError(mockToast, 413);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File type not supported',
        description:
          'Please upload a JPG, PNG, GIF, WebP, HEIC, TIFF, or BMP image instead.',
        variant: 'destructive',
      });
    });

    it('should show file type error for 415 status', () => {
      const mockToast = jest.fn();
      showFileTypeError(mockToast, 415);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File type not supported',
        description:
          'Please upload a JPG, PNG, GIF, WebP, HEIC, TIFF, or BMP image instead.',
        variant: 'destructive',
      });
    });

    it('should show file type error for 429 status', () => {
      const mockToast = jest.fn();
      showFileTypeError(mockToast, 429);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File type not supported',
        description:
          'Please upload a JPG, PNG, GIF, WebP, HEIC, TIFF, or BMP image instead.',
        variant: 'destructive',
      });
    });

    it('should show file type error for 507 status', () => {
      const mockToast = jest.fn();
      showFileTypeError(mockToast, 507);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'File type not supported',
        description:
          'Please upload a JPG, PNG, GIF, WebP, HEIC, TIFF, or BMP image instead.',
        variant: 'destructive',
      });
    });
  });

  describe('showSecurityError', () => {
    it('should show generic security error', () => {
      const mockToast = jest.fn();
      showSecurityError(mockToast);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Upload blocked',
        description: 'For security reasons, this file type is not permitted.',
        variant: 'destructive',
      });
    });

    it('should show security error with custom message', () => {
      const mockToast = jest.fn();
      showSecurityError(mockToast, 'Custom security message');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Upload blocked',
        description: 'Custom security message',
        variant: 'destructive',
      });
    });
  });

  describe('showUploadError', () => {
    it('should show short error message', () => {
      const mockToast = jest.fn();
      showUploadError(mockToast, 'Connection failed');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Upload failed',
        description: 'Connection failed',
        variant: 'destructive',
      });
    });

    it('should show generic message for long errors', () => {
      const mockToast = jest.fn();
      const longError = 'Error: '.repeat(20);
      showUploadError(mockToast, longError);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Upload failed',
        description:
          "We couldn't upload your file. Please try again or contact support if this continues.",
        variant: 'destructive',
      });
    });
  });

  describe('showServiceError', () => {
    it('should show production error message', () => {
      const mockToast = jest.fn();
      showServiceError(mockToast);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Service unavailable',
        description:
          'Service temporarily unavailable. Please try again in a few moments.',
        variant: 'destructive',
      });
    });

    it('should show development error message', () => {
      const mockToast = jest.fn();
      showServiceError(mockToast, true);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Service unavailable',
        description:
          'Backend server not running. Start with `npm run dev:server`',
        variant: 'destructive',
      });
    });
  });

  describe('showPaywallError', () => {
    it('should show paywall error', () => {
      const mockToast = jest.fn();
      showPaywallError(mockToast);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Free uploads used',
        description:
          "You've used your free uploads. Purchase credits to continue.",
        variant: 'destructive',
      });
    });
  });

  describe('showSuccessMessage', () => {
    it('should show custom success message', () => {
      const mockToast = jest.fn();
      showSuccessMessage(mockToast, 'Custom Title', 'Custom description');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Custom Title',
        description: 'Custom description',
        variant: 'default',
      });
    });
  });

  describe('showCreditsAdded', () => {
    it('should show credits added message (singular)', () => {
      const mockToast = jest.fn();
      showCreditsAdded(mockToast, 1);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Credits added successfully',
        description: 'You now have 1 upload available.',
        variant: 'default',
      });
    });

    it('should show credits added message (plural)', () => {
      const mockToast = jest.fn();
      showCreditsAdded(mockToast, 5);
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Credits added successfully',
        description: 'You now have 5 uploads available.',
        variant: 'default',
      });
    });
  });

  describe('showFeatureComingSoon', () => {
    it('should show feature coming soon message', () => {
      const mockToast = jest.fn();
      showFeatureComingSoon(mockToast, 'Dark Mode');
      expect(mockToast).toHaveBeenCalledWith({
        title: 'Dark Mode coming soon',
        description: 'Dark Mode functionality will be available shortly.',
        variant: 'default',
      });
    });
  });
});
