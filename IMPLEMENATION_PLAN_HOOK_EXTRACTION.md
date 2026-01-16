# SimpleUploadZone Hook Extraction Implementation Plan

## Phase 1: Foundation Hooks (Low Risk)

### 1. useMobileDetection Hook
**File**: `client/src/hooks/useMobileDetection.ts`

```typescript
import { useState, useEffect } from 'react';

export const useMobileDetection = (breakpoint = 640) => {
  const [isMobile, setIsMobile] = useState(window.innerWidth < breakpoint);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < breakpoint);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoint]);

  return { isMobile };
};
```

### 2. useDragAndDrop Hook
**File**: `client/src/hooks/useDragAndDrop.ts`

```typescript
import { useState, useCallback } from 'react';

interface UseDragAndDropProps {
  onFileDrop: (file: File) => void;
}

export const useDragAndDrop = ({ onFileDrop }: UseDragAndDropProps) => {
  const [isDragActive, setIsDragActive] = useState(false);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFileDrop(files[0]);
    }
  }, [onFileDrop]);

  const onKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      // This will be handled by the component with inputRef
    }
  }, []);

  return {
    isDragActive,
    dragHandlers: {
      onDragOver,
      onDragLeave,
      onDrop,
      onKeyDown,
    },
  };
};
```

### 3. useOcrDetection Hook
**File**: `client/src/hooks/useOcrDetection.ts`

```typescript
import { useState, useCallback } from 'react';

const OCR_MAP_PATTERNS = /gps|map|location|coords|coordinate|geotag/i;

export const useOcrDetection = () => {
  const [ocrAutoApplied, setOcrAutoApplied] = useState(false);
  const [ocrUserOverride, setOcrUserOverride] = useState(false);

  const shouldAutoApplyOcr = useCallback((filename: string): boolean => {
    return OCR_MAP_PATTERNS.test(filename);
  }, []);

  const applyOcrOverride = useCallback(() => {
    setOcrUserOverride(true);
    setOcrAutoApplied(false);
  }, []);

  const clearOcrOverride = useCallback(() => {
    setOcrUserOverride(false);
    setOcrAutoApplied(false);
  }, []);

  const setAutoApplied = useCallback(() => {
    setOcrAutoApplied(true);
    setOcrUserOverride(false);
  }, []);

  return {
    ocrAutoApplied,
    ocrUserOverride,
    shouldAutoApplyOcr,
    applyOcrOverride,
    clearOcrOverride,
    setAutoApplied,
  };
};
```

## Phase 2: Business Logic Hooks (Medium Risk)

### 4. useFileUploadState Hook
**File**: `client/src/hooks/useFileUploadState.ts`

```typescript
import { useState, useCallback } from 'react';

interface FileUploadState {
  file: File | null;
  fileId: string | null;
  dimensions: { width: number; height: number } | null;
}

export const useFileUploadState = () => {
  const [state, setState] = useState<FileUploadState>({
    file: null,
    fileId: null,
    dimensions: null,
  });

  const setFile = useCallback((file: File) => {
    const fileId = crypto.randomUUID();
    setState({
      file,
      fileId,
      dimensions: null,
    });
    
    // Reset session storage
    sessionStorage.setItem('images_mvp_status', 'idle');
    sessionStorage.removeItem('images_mvp_error');
  }, []);

  const setDimensions = useCallback((dimensions: { width: number; height: number } | null) => {
    setState(prev => ({ ...prev, dimensions }));
  }, []);

  const clearFile = useCallback(() => {
    setState({
      file: null,
      fileId: null,
      dimensions: null,
    });
  }, []);

  return {
    file: state.file,
    fileId: state.fileId,
    dimensions: state.dimensions,
    setFile,
    setDimensions,
    clearFile,
  };
};
```

### 5. useQuoteManagement Hook
**File**: `client/src/hooks/useQuoteManagement.ts`

```typescript
import { useState, useCallback } from 'react';
import { 
  fetchImagesMvpQuote, 
  createDefaultQuoteOps, 
  type ImagesMvpQuoteOps, 
  type ImagesMvpQuoteResponse 
} from '@/lib/images-mvp-quote';

export const useQuoteManagement = () => {
  const [quoteData, setQuoteData] = useState<ImagesMvpQuoteResponse | null>(null);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [quoteError, setQuoteError] = useState<string | null>(null);
  const [quoteOps, setQuoteOps] = useState<ImagesMvpQuoteOps>(createDefaultQuoteOps());

  const requestQuote = useCallback(async (
    file: File,
    fileId: string,
    dimensions: { width: number; height: number } | null,
    ops: ImagesMvpQuoteOps
  ) => {
    setQuoteLoading(true);
    setQuoteError(null);
    
    try {
      const response = await fetchImagesMvpQuote(
        [{
          id: fileId,
          name: file.name,
          mime: file.type || null,
          sizeBytes: file.size,
          width: dimensions?.width ?? null,
          height: dimensions?.height ?? null,
        }],
        ops
      );
      
      setQuoteData(response);
      return response;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to get quote';
      setQuoteError(message);
      setQuoteData(null);
      return null;
    } finally {
      setQuoteLoading(false);
    }
  }, []);

  const updateOps = useCallback((key: keyof ImagesMvpQuoteOps) => {
    setQuoteOps(prev => ({ ...prev, [key]: !prev[key] }));
  }, []);

  const resetQuote = useCallback(() => {
    setQuoteData(null);
    setQuoteError(null);
  }, []);

  return {
    quoteData,
    quoteLoading,
    quoteError,
    quoteOps,
    setQuoteOps,
    requestQuote,
    updateOps,
    resetQuote,
  };
};
```

### 6. useAnalyticsTracking Hook
**File**: `client/src/hooks/useAnalyticsTracking.ts`

```typescript
import { useCallback } from 'react';
import { 
  trackImagesMvpEvent, 
  getFileSizeBucket 
} from '@/lib/images-mvp-analytics';

const getFileExtension = (name: string): string | null => {
  const index = name.lastIndexOf('.');
  if (index <= 0) return null;
  return name.slice(index).toLowerCase();
};

export const useAnalyticsTracking = () => {
  const trackUploadSelected = useCallback((file: File) => {
    const ext = getFileExtension(file.name);
    const mimeType = file.type || 'application/octet-stream';
    const sizeBucket = getFileSizeBucket(file.size);

    trackImagesMvpEvent('upload_selected', {
      extension: ext,
      mime_type: mimeType,
      size_bytes: file.size,
      size_bucket: sizeBucket,
      has_trial_email: false,
    });
  }, []);

  const trackUploadRejected = useCallback((file: File, reason: string) => {
    const ext = getFileExtension(file.name);
    const mimeType = file.type || 'application/octet-stream';
    const sizeBucket = getFileSizeBucket(file.size);

    trackImagesMvpEvent('upload_rejected', {
      extension: ext,
      mime_type: mimeType,
      size_bytes: file.size,
      size_bucket: sizeBucket,
      reason,
    });
  }, []);

  const trackAnalysisStarted = useCallback((file: File) => {
    const ext = getFileExtension(file.name);
    const mimeType = file.type || 'application/octet-stream';
    const sizeBucket = getFileSizeBucket(file.size);

    trackImagesMvpEvent('analysis_started', {
      extension: ext,
      mime_type: mimeType,
      size_bytes: file.size,
      size_bucket: sizeBucket,
      has_trial_email: false,
    });
  }, []);

  const trackAnalysisCompleted = useCallback((
    file: File, 
    success: boolean, 
    data?: any
  ) => {
    const ext = getFileExtension(file.name);
    const mimeType = file.type || 'application/octet-stream';
    const sizeBucket = getFileSizeBucket(file.size);

    trackImagesMvpEvent('analysis_completed', {
      success,
      extension: ext,
      mime_type: mimeType,
      size_bucket: sizeBucket,
      elapsed_ms: data?.elapsed_ms ?? null,
      fields_extracted: data?.fields_extracted ?? null,
      trial_granted: data?.access?.trial_granted ?? null,
      credits_charged: data?.access?.credits_charged ?? null,
      credits_required: data?.access?.credits_required ?? null,
    });
  }, []);

  const trackPaywallViewed = useCallback((file: File) => {
    const ext = getFileExtension(file.name);
    const mimeType = file.type || 'application/octet-stream';

    trackImagesMvpEvent('paywall_viewed', {
      reason: 'free_quota_exhausted_or_insufficient_credits',
      extension: ext,
      mime_type: mimeType,
    });
  }, []);

  return {
    trackUploadSelected,
    trackUploadRejected,
    trackAnalysisStarted,
    trackAnalysisCompleted,
    trackPaywallViewed,
  };
};
```

## Phase 3: Complex Hooks (High Risk)

### 7. useUploadProgress Hook
**File**: `client/src/hooks/useUploadProgress.ts`

```typescript
import { useState, useRef, useCallback } from 'react';
import { getImagesMvpSessionId } from '@/lib/images-mvp-analytics';
import { generateBrowserFingerprint } from '@/lib/browser-fingerprint';
import type { ImagesMvpQuoteResponse } from '@/lib/images-mvp-quote';

export const useUploadProgress = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState('');
  
  const uploadAbortRef = useRef<XMLHttpRequest | null>(null);
  const fingerprintPromiseRef = useRef<Promise<Record<string, unknown>> | null>(null);

  const getFingerprintData = useCallback(async () => {
    try {
      const cached = sessionStorage.getItem('metaextract_fingerprint_v1');
      if (cached) {
        const parsed = JSON.parse(cached);
        if (parsed && typeof parsed === 'object') {
          return parsed as Record<string, unknown>;
        }
      }
    } catch {
      // Ignore cache failures
    }

    try {
      if (!fingerprintPromiseRef.current) {
        fingerprintPromiseRef.current = generateBrowserFingerprint() as any;
      }
      const fp = await fingerprintPromiseRef.current;
      try {
        sessionStorage.setItem('metaextract_fingerprint_v1', JSON.stringify(fp));
      } catch {
        // Ignore cache failures
      }
      return fp as Record<string, unknown>;
    } catch {
      return null;
    }
  }, []);

  const startUpload = useCallback(async (
    file: File,
    quoteData: ImagesMvpQuoteResponse,
    fileId: string,
    quoteOps: any
  ) => {
    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(false);
    
    const sessionId = getImagesMvpSessionId() || 
      `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    setCurrentSessionId(sessionId);
    
    const formData = new FormData();
    sessionStorage.setItem('images_mvp_status', 'processing');
    sessionStorage.setItem('images_mvp_ocr', String(quoteOps.ocr));

    const fingerprintData = await getFingerprintData();
    if (fingerprintData) {
      formData.append('fingerprintData', JSON.stringify(fingerprintData));
    }

    formData.append('session_id', sessionId);
    formData.append('quote_id', quoteData.quoteId);
    formData.append('client_file_id', fileId);
    formData.append('op_embedding', String(quoteOps.embedding));
    formData.append('op_ocr', String(quoteOps.ocr));
    formData.append('op_forensics', String(quoteOps.forensics));
    
    if (file.lastModified) {
      formData.append('client_last_modified', String(file.lastModified));
    }
    formData.append('file', file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      uploadAbortRef.current = xhr;

      xhr.upload.onprogress = event => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          setUploadProgress(percentComplete);
        }
      };

      xhr.onload = () => {
        uploadAbortRef.current = null;
        let responseData;
        try {
          responseData = xhr.responseText ? JSON.parse(xhr.responseText) : null;
        } catch {
          responseData = null;
        }

        if (xhr.status >= 200 && xhr.status < 300) {
          setUploadProgress(100);
          resolve(responseData);
        } else {
          reject({
            status: xhr.status,
            message: responseData?.error || 'Upload failed',
            data: responseData,
          });
        }
      };

      xhr.onerror = () => {
        uploadAbortRef.current = null;
        setUploadError(true);
        reject({ message: 'Network error' });
      };

      xhr.onabort = () => {
        uploadAbortRef.current = null;
        reject({ message: 'Upload cancelled', aborted: true });
      };

      xhr.open('POST', '/api/images_mvp/extract');
      xhr.send(formData);
    });
  }, [getFingerprintData]);

  const abortUpload = useCallback(() => {
    if (uploadAbortRef.current) {
      uploadAbortRef.current.abort();
      uploadAbortRef.current = null;
    }
    setIsUploading(false);
    setUploadProgress(0);
  }, []);

  const resetProgress = useCallback(() => {
    setIsUploading(false);
    setUploadProgress(0);
    setUploadError(false);
    setCurrentSessionId('');
  }, []);

  return {
    isUploading,
    uploadProgress,
    uploadError,
    currentSessionId,
    startUpload,
    abortUpload,
    resetProgress,
  };
};
```

### 8. usePaywallManagement Hook
**File**: `client/src/hooks/usePaywallManagement.ts`

```typescript
import { useState, useCallback } from 'react';

export const usePaywallManagement = () => {
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [paywallShownAt, setPaywallShownAt] = useState<number | null>(null);
  const [pricingDismissed, setPricingDismissed] = useState(false);
  const [resumeRequested, setResumeRequested] = useState(false);

  const checkCreditsAndMaybeResume = useCallback(async () => {
    if (!resumeRequested) return;
    
    try {
      const res = await fetch('/api/images_mvp/credits/balance', {
        credentials: 'include',
      });
      if (!res.ok) return;
      
      const data = await res.json();
      const credits = typeof data?.credits === 'number' ? data.credits : 0;
      
      return credits;
    } catch {
      return 0;
    }
  }, [resumeRequested]);

  const showPaywall = useCallback(() => {
    setShowPricingModal(true);
    setPaywallShownAt(Date.now());
    setPricingDismissed(false);
  }, []);

  const dismissPaywall = useCallback(() => {
    setShowPricingModal(false);
    setPricingDismissed(true);
  }, []);

  const requestResume = useCallback(() => {
    setResumeRequested(true);
  }, []);

  const clearResumeRequest = useCallback(() => {
    setResumeRequested(false);
  }, []);

  return {
    showPricingModal,
    paywallShownAt,
    pricingDismissed,
    resumeRequested,
    checkCreditsAndMaybeResume,
    showPaywall,
    dismissPaywall,
    requestResume,
    clearResumeRequest,
  };
};
```

## Phase 4: URL Parameter Hooks

### 9. useUrlParameterHandler Hook
**File**: `client/src/hooks/useUrlParameterHandler.ts`

```typescript
import { useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

interface UrlParameterConfig {
  pricing?: boolean;
  credits?: boolean;
  ocr?: boolean;
}

export const useUrlParameterHandler = (
  onPricingParam: () => void,
  onOcrParam: () => void
) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const openedFromQueryRef = useRef(false);
  const ocrFromQueryRef = useRef(false);

  useEffect(() => {
    if (openedFromQueryRef.current) return;
    
    const pricingFlag = searchParams.get('pricing') || searchParams.get('credits');
    if (pricingFlag) {
      openedFromQueryRef.current = true;
      onPricingParam();
      
      const next = new URLSearchParams(searchParams);
      next.delete('pricing');
      next.delete('credits');
      setSearchParams(next, { replace: true });
    }
  }, [searchParams, setSearchParams, onPricingParam]);

  useEffect(() => {
    if (ocrFromQueryRef.current) return;
    if (searchParams.get('ocr') !== '1') return;
    
    ocrFromQueryRef.current = true;
    onOcrParam();
    
    const next = new URLSearchParams(searchParams);
    next.delete('ocr');
    setSearchParams(next, { replace: true });
  }, [searchParams, setSearchParams, onOcrParam]);
};
```

## Phase 5: Utility Functions

### File Processing Utilities
**File**: `client/src/utils/fileProcessing.ts`

```typescript
export const getFileExtension = (name: string): string | null => {
  const index = name.lastIndexOf('.');
  if (index <= 0) return null;
  return name.slice(index).toLowerCase();
};

export const probeImageDimensions = async (
  file: File
): Promise<{ width: number; height: number } | null> => {
  try {
    const objectUrl = URL.createObjectURL(file);
    const result = await new Promise<{ width: number; height: number } | null>(resolve => {
      const img = new Image();
      img.onload = () => {
        resolve({ width: img.width, height: img.height });
        URL.revokeObjectURL(objectUrl);
      };
      img.onerror = () => {
        resolve(null);
        URL.revokeObjectURL(objectUrl);
      };
      img.src = objectUrl;
    });
    return result;
  } catch {
    return null;
  }
};
```

### Error Handling Utilities
**File**: `client/src/utils/uploadErrorHandler.ts`

```typescript
import { showFileValidationError, showPaywallError } from '@/lib/toast-helpers';

export class UploadErrorHandler {
  static handleQuoteError(
    toast: any,
    error: string,
    clearFile: () => void
  ): void {
    showFileValidationError(toast, 'failed');
    clearFile();
  }

  static handlePaywallError(
    toast: any,
    showPaywall: () => void,
    requestResume: () => void
  ): void {
    showPaywallError(toast);
    showPaywall();
    requestResume();
  }
}
```

## Phase 6: Component Refactoring

### Refactored SimpleUploadZone Component
**File**: `client/src/components/images-mvp/simple-upload.tsx` (Refactored)

```typescript
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { PricingModal } from '@/components/images-mvp/pricing-modal';
import { ProgressTracker } from '@/components/images-mvp/progress-tracker';
import { UploadErrorBoundary } from '@/components/images-mvp/upload-error-boundary';

// Hooks
import { useMobileDetection } from '@/hooks/useMobileDetection';
import { useDragAndDrop } from '@/hooks/useDragAndDrop';
import { useFileUploadState } from '@/hooks/useFileUploadState';
import { useQuoteManagement } from '@/hooks/useQuoteManagement';
import { useUploadProgress } from '@/hooks/useUploadProgress';
import { usePaywallManagement } from '@/hooks/usePaywallManagement';
import { useOcrDetection } from '@/hooks/useOcrDetection';
import { useAnalyticsTracking } from '@/hooks/useAnalyticsTracking';
import { useUrlParameterHandler } from '@/hooks/useUrlParameterHandler';

// Utilities
import { probeImageDimensions, getFileExtension } from '@/utils/fileProcessing';
import { UploadErrorHandler } from '@/utils/uploadErrorHandler';

// Auth and analytics
import { useAuth } from '@/lib/auth';
import { getImagesMvpSessionId } from '@/lib/images-mvp-analytics';

function SimpleUploadZoneInternal() {
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  // Hooks
  const { isMobile } = useMobileDetection();
  const { file, fileId, dimensions, setFile, setDimensions, clearFile } = useFileUploadState();
  const { 
    quoteData, 
    quoteLoading, 
    quoteError, 
    quoteOps, 
    setQuoteOps, 
    requestQuote, 
    updateOps, 
    resetQuote 
  } = useQuoteManagement();
  const { 
    isUploading, 
    uploadProgress, 
    uploadError, 
    currentSessionId, 
    startUpload, 
    resetProgress 
  } = useUploadProgress();
  const { 
    showPricingModal, 
    paywallShownAt, 
    pricingDismissed, 
    resumeRequested,
    showPaywall, 
    dismissPaywall, 
    requestResume,
    clearResumeRequest 
  } = usePaywallManagement();
  const { ocrAutoApplied, ocrUserOverride, shouldAutoApplyOcr, setAutoApplied } = useOcrDetection();
  const { 
    trackUploadSelected, 
    trackUploadRejected, 
    trackAnalysisStarted, 
    trackAnalysisCompleted,
    trackPaywallViewed 
  } = useAnalyticsTracking();

  // Drag and drop
  const { isDragActive, dragHandlers } = useDragAndDrop({
    onFileDrop: handleFile,
  });

  // URL parameter handling
  useUrlParameterHandler(
    () => {
      showPaywall();
      dismissPaywall();
    },
    () => {
      setQuoteOps(prev => ({ ...prev, ocr: true }));
    }
  );

  // Storage event listener
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'metaextract_images_mvp_purchase_completed') {
        handleCreditCheck();
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Cleanup will be handled by individual hooks
    };
  }, []);

  async function handleFile(file: File) {
    const ext = getFileExtension(file.name);
    const mimeType = file.type || 'application/octet-stream';

    trackUploadSelected(file);
    setFile(file);

    // Probe image dimensions
    const dimensions = await probeImageDimensions(file);
    setDimensions(dimensions);

    // Check for OCR auto-application
    const shouldSuggestOcr = shouldAutoApplyOcr(file.name);
    if (shouldSuggestOcr && !ocrUserOverride && !quoteOps.ocr) {
      setQuoteOps(prev => ({ ...prev, ocr: true }));
      setAutoApplied();
    }

    // Request quote
    const quote = await requestQuote(file, fileId!, dimensions, quoteOps);
    const fileQuote = quote?.quote?.perFile?.find(entry => entry.id === fileId);
    
    if (!quote || !fileQuote) {
      trackUploadRejected(file, 'quote_failed');
      UploadErrorHandler.handleQuoteError(toast, 'failed', clearFile);
      return;
    }

    if (!fileQuote.accepted) {
      const reason = fileQuote.reason === 'file_too_large' ? 'too_large' :
                    fileQuote.reason === 'megapixels_exceed_limit' ? 'megapixels' : 'unsupported';
      trackUploadRejected(file, reason);
      clearFile();
      resetQuote();
    }
  }

  async function handleUpload() {
    if (!quoteData || !fileId || !file) {
      UploadErrorHandler.handleQuoteError(toast, 'validation', clearFile);
      return;
    }

    trackAnalysisStarted(file);
    
    try {
      const result = await startUpload(file, quoteData, fileId, quoteOps);
      
      trackAnalysisCompleted(file, true, result);
      
      // Navigate to results
      sessionStorage.setItem('currentMetadata', JSON.stringify(result));
      sessionStorage.setItem('images_mvp_status', 'success');
      sessionStorage.removeItem('images_mvp_error');
      
      setTimeout(() => {
        navigate('/images_mvp/results', { state: { metadata: result } });
      }, 500);
      
    } catch (error: any) {
      trackAnalysisCompleted(file, false, { error: error.message });
      
      const isPaywall = error.status === 402 || 
                       (error.status === 429 && error.data?.credits_required);
      
      if (isPaywall) {
        trackPaywallViewed(file);
        UploadErrorHandler.handlePaywallError(toast, showPaywall, requestResume);
      } else {
        // Handle other errors
        resetProgress();
      }
    }
  }

  async function handleCreditCheck() {
    if (!resumeRequested || !file || isUploading) return;
    
    const credits = await checkCreditsAndMaybeResume();
    if (credits && credits >= 1) {
      clearResumeRequest();
      dismissPaywall();
      // Show success message
    }
  }

  // Get active quote entry
  const activeQuoteEntry = quoteData?.quote?.perFile?.find(
    entry => entry.id === fileId
  ) ?? null;

  return (
    <div className="w-full max-w-lg mx-auto px-4 sm:px-0">
      <PricingModal
        isOpen={showPricingModal}
        onClose={dismissPaywall}
      />

      {/* Progress Tracker */}
      {currentSessionId && (
        <div className="mb-4 sm:mb-6">
          <ProgressTracker
            sessionId={currentSessionId}
            uploadComplete={uploadProgress >= 100}
          />
        </div>
      )}

      {/* Resume Upload Section */}
      {resumeRequested && file && (
        <div className="mb-3 rounded-lg border border-white/10 bg-white/5 p-3 text-left">
          <div className="text-xs text-slate-200">
            Ready to analyze:{' '}
            <span className="text-white font-semibold">{file.name}</span>
          </div>
          <div className="mt-2 flex gap-2">
            <Button
              variant="outline"
              className="border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
              onClick={handleCreditCheck}
              disabled={isUploading}
            >
              Refresh credits
            </Button>
            <Button
              className="bg-primary hover:bg-primary/90 text-black font-semibold"
              onClick={showPaywall}
              disabled={isUploading}
            >
              Buy credits
            </Button>
            <Button
              variant="ghost"
              className="text-slate-300 hover:text-white hover:bg-white/10"
              onClick={() => {
                clearFile();
                clearResumeRequest();
              }}
              disabled={isUploading}
            >
              Pick different file
            </Button>
          </div>
        </div>
      )}

      {/* File Upload Area */}
      <FileUploadArea
        isDragActive={isDragActive}
        isUploading={isUploading}
        uploadProgress={uploadProgress}
        uploadError={uploadError}
        isMobile={isMobile}
        isAuthenticated={isAuthenticated}
        maxBytesDisplay={quoteData?.limits?.maxBytes}
        onFileSelect={(selectedFile) => handleFile(selectedFile)}
        {...dragHandlers}
      />

      {/* File Preview */}
      {file && (
        <FilePreview
          file={file}
          dimensions={dimensions}
          quoteLoading={quoteLoading}
          quoteError={quoteError}
          activeQuoteEntry={activeQuoteEntry}
          quoteOps={quoteOps}
          ocrAutoApplied={ocrAutoApplied}
          onOcrToggle={() => updateOps('ocr')}
          onUpload={handleUpload}
          onClear={clearFile}
          isUploading={isUploading}
        />
      )}
    </div>
  );
}

/**
 * SimpleUploadZone wrapped in error boundary for resilience
 */
export function SimpleUploadZone() {
  return (
    <UploadErrorBoundary
      onError={(error, errorInfo) => {
        console.error('Upload zone error:', error, errorInfo);
      }}
    >
      <SimpleUploadZoneInternal />
    </UploadErrorBoundary>
  );
}
```

## Testing Strategy

### Unit Tests for Hooks
Each hook should have comprehensive unit tests:
- State management behavior
- Side effect cleanup
- Error handling
- Edge cases

### Integration Tests
- Hook interactions
- Component integration
- Error boundary behavior
- Analytics tracking

### E2E Tests
- Complete upload flow
- Error scenarios
- Paywall flow
- Mobile responsiveness

## Migration Timeline

### Week 1: Foundation
- Extract utility functions
- Implement simple hooks (mobile, drag & drop, OCR)
- Write unit tests

### Week 2: Business Logic
- Implement quote management hook
- Implement analytics tracking hook
- Integration testing

### Week 3: Complex Hooks
- Implement upload progress hook
- Implement paywall management hook
- URL parameter handling

### Week 4: Component Refactoring
- Decompose UI components
- Integration testing
- Performance optimization

### Week 5: Testing & Deployment
- Comprehensive testing
- Bug fixes and polish
- Gradual rollout

This implementation plan provides a systematic approach to refactoring the complex SimpleUploadZone component into manageable, testable hooks while maintaining functionality and improving maintainability.