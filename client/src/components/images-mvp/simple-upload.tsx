import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Upload, Zap } from 'lucide-react';
import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { PricingModal } from '@/components/images-mvp/pricing-modal';
import { ProgressTracker } from '@/components/images-mvp/progress-tracker';
import {
  getFileSizeBucket,
  getImagesMvpSessionId,
  trackImagesMvpEvent,
} from '@/lib/images-mvp-analytics';
import {
  createDefaultQuoteOps,
  fetchImagesMvpQuote,
  type ImagesMvpQuoteOps,
  type ImagesMvpQuoteResponse,
} from '@/lib/images-mvp-quote';

export function SimpleUploadZone() {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [pendingFileId, setPendingFileId] = useState<string | null>(null);
  const [pendingDimensions, setPendingDimensions] = useState<{
    width: number;
    height: number;
  } | null>(null);
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [paywallShownAt, setPaywallShownAt] = useState<number | null>(null);
  const [pricingDismissed, setPricingDismissed] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [showProgressTracker, setShowProgressTracker] = useState(false);
  const [resumeRequested, setResumeRequested] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 640);
  const [quoteOps, setQuoteOps] = useState<ImagesMvpQuoteOps>(
    createDefaultQuoteOps()
  );
  const [quoteData, setQuoteData] = useState<ImagesMvpQuoteResponse | null>(
    null
  );
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [quoteError, setQuoteError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const openedFromQueryRef = useRef(false);
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { toast } = useToast();
  const shouldReduceMotion = useReducedMotion();
  const maxBytesDisplay =
    typeof quoteData?.limits?.maxBytes === 'number'
      ? quoteData.limits.maxBytes
      : null;

  const getExtension = (name: string): string | null => {
    const index = name.lastIndexOf('.');
    if (index <= 0) return null;
    return name.slice(index).toLowerCase();
  };

  const probeImageDimensions = async (
    file: File
  ): Promise<{ width: number; height: number } | null> => {
    try {
      const objectUrl = URL.createObjectURL(file);
      const result = await new Promise<{ width: number; height: number } | null>(
        resolve => {
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
        }
      );
      return result;
    } catch {
      return null;
    }
  };

  const requestQuote = useCallback(
    async (
      file: File,
      fileId: string,
      dimensions: { width: number; height: number } | null,
      ops: ImagesMvpQuoteOps
    ) => {
      setQuoteLoading(true);
      setQuoteError(null);
      try {
        const response = await fetchImagesMvpQuote(
          [
            {
              id: fileId,
              name: file.name,
              mime: file.type || null,
              sizeBytes: file.size,
              width: dimensions?.width ?? null,
              height: dimensions?.height ?? null,
            },
          ],
          ops
        );
        setQuoteData(response);
        return response;
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'Failed to get quote';
        setQuoteError(message);
        setQuoteData(null);
        return null;
      } finally {
        setQuoteLoading(false);
      }
    },
    []
  );

  const checkCreditsAndMaybeResume = useCallback(async () => {
    if (!pendingFile || isUploading) return;
    try {
      const res = await fetch('/api/images_mvp/credits/balance', {
        credentials: 'include',
      });
      if (!res.ok) return;
      const data = await res.json();
      const credits =
        typeof data?.credits === 'number' ? (data.credits as number) : 0;
      if (credits >= 1) {
        if (!quoteData || !pendingFileId) {
          toast({
            title: 'Quote expired',
            description: 'Please select the file again to refresh the quote.',
            variant: 'destructive',
          });
          return;
        }
        setShowPricingModal(false);
        setResumeRequested(false);
        void uploadFile(pendingFile);
      }
    } catch {
      // Best-effort only
    }
  }, [pendingFile, isUploading]);

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'metaextract_images_mvp_purchase_completed') {
        void checkCreditsAndMaybeResume();
      }
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [checkCreditsAndMaybeResume]);

  useEffect(() => {
    const onFocus = () => {
      void checkCreditsAndMaybeResume();
    };
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [checkCreditsAndMaybeResume]);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 640);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (openedFromQueryRef.current) return;
    const pricingFlag = searchParams.get('pricing') || searchParams.get('credits');
    if (!pricingFlag) return;
    openedFromQueryRef.current = true;
    setShowPricingModal(true);
    setPricingDismissed(false);
    const next = new URLSearchParams(searchParams);
    next.delete('pricing');
    next.delete('credits');
    setSearchParams(next, { replace: true });
  }, [searchParams, setSearchParams]);

  useEffect(() => {
    if (!showPricingModal) return;
    const active = document.activeElement as HTMLElement | null;
    if (active && typeof active.blur === 'function') {
      active.blur();
    }
  }, [showPricingModal]);

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
    if (files.length > 0) handleFile(files[0]);
  }, []);

  const onKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      inputRef.current?.click();
    }
  }, []);

  const activeQuoteEntry =
    quoteData?.quote?.perFile?.find(entry => entry.id === pendingFileId) ?? null;

  const handleOpsToggle = (key: keyof ImagesMvpQuoteOps) => {
    const nextOps = { ...quoteOps, [key]: !quoteOps[key] };
    setQuoteOps(nextOps);
    if (pendingFile && pendingFileId) {
      void requestQuote(pendingFile, pendingFileId, pendingDimensions, nextOps);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
    e.target.value = ''; // reset
  };

  const handleFile = async (file: File) => {
    const ext = getExtension(file.name);
    const mimeType = file.type || 'application/octet-stream';
    const sizeBucket = getFileSizeBucket(file.size);

    trackImagesMvpEvent('upload_selected', {
      extension: ext,
      mime_type: mimeType,
      size_bytes: file.size,
      size_bucket: sizeBucket,
      has_trial_email: false,
    });

    const fileId = crypto.randomUUID();
    setPendingFile(file);
    setPendingFileId(fileId);
    setPendingDimensions(null);
    sessionStorage.setItem('images_mvp_status', 'idle');
    sessionStorage.removeItem('images_mvp_error');

    const dimensions = await probeImageDimensions(file);
    setPendingDimensions(dimensions);

    const quote = await requestQuote(file, fileId, dimensions, quoteOps);
    const fileQuote = quote?.quote?.perFile?.find(entry => entry.id === fileId);
    if (!quote || !fileQuote) {
      trackImagesMvpEvent('upload_rejected', {
        extension: ext,
        mime_type: mimeType,
        size_bytes: file.size,
        size_bucket: sizeBucket,
        reason: 'quote_failed',
      });
      toast({
        title: 'Quote failed',
        description: 'We could not price this file. Please try again.',
        variant: 'destructive',
      });
      setPendingFile(null);
      setPendingFileId(null);
      return;
    }

    if (!fileQuote.accepted) {
      trackImagesMvpEvent('upload_rejected', {
        extension: ext,
        mime_type: mimeType,
        size_bytes: file.size,
        size_bucket: sizeBucket,
        reason: fileQuote.reason || 'unsupported_format',
      });
      toast({
        title: 'Upload blocked',
        description:
          fileQuote.reason === 'file_too_large'
            ? 'File exceeds the maximum size limit.'
            : fileQuote.reason === 'megapixels_exceed_limit'
              ? 'Image resolution exceeds the supported limit.'
              : 'Unsupported file type.',
        variant: 'destructive',
      });
      setPendingFile(null);
      setPendingFileId(null);
      setQuoteData(null);
      return;
    }
  };

  const uploadFile = async (file: File) => {
    if (!quoteData || !pendingFileId) {
      toast({
        title: 'Quote required',
        description: 'Please select the file again to get a fresh quote.',
        variant: 'destructive',
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    const startedAt = Date.now();

    // Get session ID for WebSocket progress tracking
    const sessionId =
      getImagesMvpSessionId() ||
      `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setCurrentSessionId(sessionId);
    setShowProgressTracker(true);
    const formData = new FormData();
    sessionStorage.setItem('images_mvp_status', 'processing');

    // Append metadata fields BEFORE file to ensure streaming parsers see them first
    formData.append('session_id', sessionId);
    formData.append('quote_id', quoteData.quoteId);
    formData.append('client_file_id', pendingFileId);
    formData.append('op_embedding', String(quoteOps.embedding));
    formData.append('op_ocr', String(quoteOps.ocr));
    formData.append('op_forensics', String(quoteOps.forensics));
    if (file.lastModified) {
      formData.append('client_last_modified', String(file.lastModified));
    }
    formData.append('file', file);

    const sizeBucket = getFileSizeBucket(file.size);
    const mimeType = file.type || 'application/octet-stream';
    const extension = getExtension(file.name);

    trackImagesMvpEvent('analysis_started', {
      extension,
      mime_type: mimeType,
      size_bytes: file.size,
      size_bucket: sizeBucket,
      has_trial_email: false,
    });

    try {
      const data = await new Promise<any>((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.upload.onprogress = event => {
          if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            setUploadProgress(percentComplete);
          }
        };

        xhr.onload = () => {
          let responseData;
          try {
            responseData = xhr.responseText
              ? JSON.parse(xhr.responseText)
              : null;
          } catch {
            responseData = null;
          }

          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(responseData);
          } else {
            const errorMessage =
              typeof responseData?.error === 'string'
                ? responseData.error
                : responseData?.error?.message ||
                  responseData?.message ||
                  xhr.responseText ||
                  'Extraction failed';

            reject({
              status: xhr.status,
              message: errorMessage,
              data: responseData,
            });
          }
        };

        xhr.onerror = () => reject({ message: 'Network error' });

        xhr.open('POST', '/api/images_mvp/extract');
        xhr.send(formData);
      });

      // Success
      const processingMs =
        typeof data?.processing_ms === 'number' ? data.processing_ms : null;
      trackImagesMvpEvent('analysis_completed', {
        success: true,
        extension,
        mime_type: mimeType,
        size_bucket: sizeBucket,
        processing_ms: processingMs,
        elapsed_ms: Date.now() - startedAt,
        fields_extracted: data?.fields_extracted ?? null,
        trial_granted: data?.access?.trial_granted ?? null,
        credits_charged: data?.access?.credits_charged ?? null,
        credits_required: data?.access?.credits_required ?? null,
      });

      setUploadProgress(100);
      sessionStorage.setItem('currentMetadata', JSON.stringify(data));
      sessionStorage.setItem('images_mvp_status', 'success');
      sessionStorage.removeItem('images_mvp_error');
      // Hide progress tracker and navigate to results
      setShowProgressTracker(false);
      setTimeout(() => {
        navigate('/images_mvp/results', { state: { metadata: data } });
      }, 500);
    } catch (err: any) {
      console.error(err);

      const errorMessage = err.message || 'Upload failed';
      const status = err.status || 500;
      const body = err.data || null;
      sessionStorage.setItem('images_mvp_status', 'fail');
      sessionStorage.setItem(
        'images_mvp_error',
        JSON.stringify({
          status,
          message: errorMessage,
        })
      );

      trackImagesMvpEvent('analysis_completed', {
        success: false,
        status,
        error_message: errorMessage,
        extension,
        mime_type: mimeType,
        size_bucket: sizeBucket,
        elapsed_ms: Date.now() - startedAt,
      });

      const isPaywall =
        status === 402 ||
        (status === 429 &&
          (body?.credits_required ||
            String(body?.error || '')
              .toLowerCase()
              .includes('quota') ||
            String(body?.message || '')
              .toLowerCase()
              .includes('purchase credits')));

      if (isPaywall) {
        // Trigger Credit Purchase Flow
        trackImagesMvpEvent('paywall_viewed', {
          reason: 'free_quota_exhausted_or_insufficient_credits',
          extension,
          mime_type: mimeType,
        });
        toast({
          title: 'Free checks used',
          description: 'Buy credits to continue analyzing images.',
          variant: 'destructive',
        });
        if (!showPricingModal && !pricingDismissed) {
          setShowPricingModal(true);
          setPaywallShownAt(Date.now());
        }
        setResumeRequested(true);
        return;
      }

      setUploadError(true);
      setShowProgressTracker(false); // Hide progress tracker on error
      setTimeout(() => setUploadError(false), 3000);

      if (
        errorMessage.toLowerCase().includes('failed to fetch') ||
        errorMessage === 'Network error'
      ) {
        toast({
          title: 'Backend unavailable',
          description:
            'API is not reachable. Start the server with `npm run dev:server`.',
          variant: 'destructive',
        });
        return;
      }
      if (body?.code && String(body.code).startsWith('QUOTE_')) {
        toast({
          title: 'Quote expired',
          description: 'Please select the file again to refresh the quote.',
          variant: 'destructive',
        });
        setPendingFile(null);
        setPendingFileId(null);
        setQuoteData(null);
        return;
      }
      if (status === 413) {
        const maxBytes = quoteData?.limits?.maxBytes ?? 100 * 1024 * 1024;
        const maxMb = Math.round(maxBytes / (1024 * 1024));
        toast({
          title: 'File too large',
          description: `Max ${maxMb} MB.`,
          variant: 'destructive',
        });
        return;
      }
      if (status === 415) {
        toast({
          title: 'Unsupported file type',
          description: 'Unsupported file type. Please upload a supported image.',
          variant: 'destructive',
        });
        return;
      }
      if (status === 403) {
        toast({
          title: 'Upload blocked',
          description:
            body?.message ||
            'For security reasons, this file type is not permitted.',
          variant: 'destructive',
        });
        return;
      }
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto px-4 sm:px-0">
      <PricingModal
        isOpen={showPricingModal}
        onClose={() => {
          setShowPricingModal(false);
          setPricingDismissed(true);
        }}
      />

      {/* Real-time Progress Tracker */}
      {showProgressTracker && currentSessionId && (
        <div className="mb-4 sm:mb-6">
          <ProgressTracker
            sessionId={currentSessionId}
            uploadComplete={uploadProgress >= 100}
          />
        </div>
      )}

      {resumeRequested && pendingFile && (
        <div className="mb-3 rounded-lg border border-white/10 bg-white/5 p-3 text-left">
          <div className="text-xs text-slate-200">
            Ready to resume:{' '}
            <span className="text-white font-semibold">{pendingFile.name}</span>
          </div>
          <div className="mt-2 flex gap-2">
            <Button
              variant="outline"
              className="border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
              onClick={() => void checkCreditsAndMaybeResume()}
              disabled={isUploading}
            >
              Resume
            </Button>
            <Button
              className="bg-primary hover:bg-primary/90 text-black font-semibold"
              onClick={() => {
                setPricingDismissed(false);
                setShowPricingModal(true);
              }}
              disabled={isUploading}
            >
              Buy credits
            </Button>
            <Button
              variant="ghost"
              className="text-slate-300 hover:text-white hover:bg-white/10"
              onClick={() => {
                setPendingFile(null);
                setResumeRequested(false);
              }}
              disabled={isUploading}
            >
              Pick different file
            </Button>
          </div>
          {paywallShownAt && (
            <div className="mt-2 text-[10px] text-slate-500">
              If you completed checkout in another tab, come back here and we’ll
              continue automatically.
            </div>
          )}
        </div>
      )}

      <label
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onKeyDown={onKeyDown}
        htmlFor="mvp-upload"
        role="button"
        tabIndex={0}
        data-testid="image-dropzone"
        aria-label={
          isMobile
            ? 'Tap to select image'
            : 'Upload image drop zone. Drag and drop a file here or click to browse.'
        }
          className={cn(
            'relative block w-full border-2 border-dashed rounded-lg sm:rounded-xl p-6 sm:p-12 text-center transition-all cursor-pointer overflow-hidden group outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-black min-h-[200px] sm:min-h-auto touch-manipulation select-none active:scale-[0.98]',
            isUploading
              ? 'border-primary/40 bg-black/40 backdrop-blur-sm'
              : isDragActive
                ? 'border-primary bg-primary/5 bg-black/20 backdrop-blur-sm'
                : 'border-white/10 bg-black/20 backdrop-blur-sm hover:border-primary/50 hover:bg-white/5'
          )}

      >
        <input
          id="mvp-upload"
          ref={inputRef}
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleFileSelect}
          title="Upload image"
          data-testid="image-upload-input"
        />

        {isUploading ? (
          <>
            {/* Progress bar background */}
            <div className="absolute inset-0 bg-black/20 rounded-lg sm:rounded-xl" />
            {/* Progress bar fill */}
            <motion.div
              className={`absolute left-0 top-0 h-full rounded-lg sm:rounded-xl ${
                uploadError
                  ? 'bg-gradient-to-r from-red-500/40 to-red-500/20'
                  : 'bg-gradient-to-r from-emerald-500/40 to-emerald-500/20'
              }`}
              initial={{ width: '0%' }}
              animate={{ width: `${uploadProgress}%` }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.3 }}
            />
            {/* Content overlay */}
            <div className="relative flex flex-col items-center justify-center gap-3 sm:gap-4 w-full h-full">
              <p className="text-white font-mono text-xs sm:text-sm">
                {uploadError
                  ? 'Upload Failed'
                  : uploadProgress < 100
                    ? 'Uploading...'
                    : 'Extracting Metadata...'}
              </p>
              <span
                className={`text-xs font-mono ${uploadError ? 'text-red-300' : 'text-emerald-300'}`}
              >
                {uploadError ? 'Error' : `${Math.round(uploadProgress)}%`}
              </span>
            </div>
          </>
        ) : (
          <>
            <div className="mb-3 sm:mb-4">
              <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-tr from-primary/20 to-purple-500/20 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                <Upload
                  className="w-6 h-6 sm:w-8 sm:h-8 text-primary"
                  aria-hidden="true"
                />
              </div>
            </div>
            <h3 className="text-lg sm:text-xl font-bold text-white mb-1 sm:mb-2">
              {isMobile ? 'Tap to select a photo' : 'Drop your image here'}
            </h3>
            <p className="text-slate-200 text-xs sm:text-sm mb-4 sm:mb-6">
              {isMobile ? (
                <>
                  JPG, PNG, HEIC, WebP
                  {maxBytesDisplay
                    ? ` (max ${Math.round(maxBytesDisplay / (1024 * 1024))} MB)`
                    : ''}
                  <span className="text-primary text-xs font-mono mt-1 block">
                    <Zap className="w-3 h-3 inline mr-1" aria-hidden="true" />2
                    free checks (no signup)
                  </span>
                </>
              ) : (
                <>
                  Supports JPG, PNG, HEIC, WebP
                  {maxBytesDisplay
                    ? ` (max ${Math.round(maxBytesDisplay / (1024 * 1024))} MB)`
                    : ''}
                  {' '}
                  <br className="hidden sm:block" />
                  <span className="text-primary text-xs font-mono mt-1 block">
                    <Zap className="w-3 h-3 inline mr-1" aria-hidden="true" />2
                    free checks (no signup)
                  </span>
                </>
              )}
            </p>
            <Button
              variant="outline"
              size="default"
              className="border-white/10 hover:bg-white/5 hover:text-white w-full sm:w-auto"
            >
              Browse Files
            </Button>
          </>
        )}
      </label>

      {pendingFile && (
        <div className="mt-4 rounded-lg border border-white/10 bg-black/30 p-4 text-left">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <div className="text-sm font-semibold text-white">
                {pendingFile.name}
              </div>
              <div className="text-[11px] text-slate-400">
                {(pendingFile.size / (1024 * 1024)).toFixed(2)} MB
                {pendingDimensions
                  ? ` • ${pendingDimensions.width}×${pendingDimensions.height}`
                  : ' • dimensions pending'}
              </div>
            </div>
            <div className="text-xs text-slate-300">
              {quoteLoading
                ? 'Calculating quote...'
                : activeQuoteEntry?.accepted
                  ? `Credits: ${activeQuoteEntry.creditsTotal}`
                  : 'Quote unavailable'}
            </div>
          </div>

          {quoteError && (
            <div className="mt-2 text-xs text-red-300">{quoteError}</div>
          )}

          {activeQuoteEntry?.accepted && activeQuoteEntry.breakdown && (
            <div className="mt-3 space-y-2 text-xs text-slate-300">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-white/10 px-2 py-1 text-[11px]">
                  {activeQuoteEntry.mpBucket || 'standard'}
                </span>
                {activeQuoteEntry.warnings?.map(warning => (
                  <span
                    key={warning}
                    className="rounded-full bg-amber-500/20 px-2 py-1 text-[11px] text-amber-200"
                  >
                    {warning}
                  </span>
                ))}
              </div>
              <div className="grid gap-1">
                <div>
                  Base scan{' '}
                  {activeQuoteEntry.breakdown.base +
                    activeQuoteEntry.breakdown.embedding}{' '}
                  + Text scan {activeQuoteEntry.breakdown.ocr} + Size{' '}
                  {activeQuoteEntry.breakdown.mp} ={' '}
                  <span className="text-white font-semibold">
                    {activeQuoteEntry.creditsTotal}
                  </span>
                </div>
                <div>
                  Batch total:{' '}
                  <span className="text-white font-semibold">
                    {quoteData?.quote.totalCredits ?? 0}
                  </span>{' '}
                  credits
                  {quoteData?.quote.standardEquivalents
                    ? ` (~${quoteData.quote.standardEquivalents} base scans)`
                    : ''}
                </div>
              </div>
            </div>
          )}

          <div className="mt-4 grid gap-2 text-xs text-slate-300">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={quoteOps.ocr}
                onChange={() => handleOpsToggle('ocr')}
                disabled={quoteLoading || isUploading}
              />
              Text scan (+6 credits)
            </label>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <Button
              className="bg-primary hover:bg-primary/90 text-black font-semibold"
              onClick={() => void uploadFile(pendingFile)}
              disabled={
                isUploading ||
                quoteLoading ||
                !activeQuoteEntry?.accepted ||
                !quoteData
              }
            >
              Analyze
            </Button>
            <Button
              variant="ghost"
              className="text-slate-300 hover:text-white hover:bg-white/10"
              onClick={() => {
                setPendingFile(null);
                setPendingFileId(null);
                setPendingDimensions(null);
                setQuoteData(null);
                setQuoteError(null);
              }}
              disabled={isUploading}
            >
              Clear
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
