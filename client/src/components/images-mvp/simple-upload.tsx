import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Zap } from 'lucide-react';
import { motion, useReducedMotion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { TrialAccessModal } from '@/components/trial-access-modal';
import { PricingModal } from '@/components/images-mvp/pricing-modal';
import { ProgressTracker } from '@/components/images-mvp/progress-tracker';
import {
  getFileSizeBucket,
  getImagesMvpSessionId,
  trackImagesMvpEvent,
} from '@/lib/images-mvp-analytics';

const SUPPORTED_EXTENSIONS = [
  // Popular photo formats for casual users
  '.jpg',
  '.jpeg',
  '.png',
  '.heic',
  '.heif',
  '.webp',
];

const SUPPORTED_MIMES = [
  // Popular photo formats for casual users
  'image/jpeg',
  'image/png',
  'image/heic',
  'image/heif',
  'image/webp',
];

export function SimpleUploadZone() {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [trialEmail, setTrialEmail] = useState<string | null>(null);
  const [showTrialModal, setShowTrialModal] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [showProgressTracker, setShowProgressTracker] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  const shouldReduceMotion = useReducedMotion();

  const getExtension = (name: string): string | null => {
    const index = name.lastIndexOf('.');
    if (index <= 0) return null;
    return name.slice(index).toLowerCase();
  };

  useEffect(() => {
    const stored = localStorage.getItem('metaextract_trial_email');
    if (stored) setTrialEmail(stored);
  }, []);

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
      document.getElementById('mvp-upload')?.click();
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
    e.target.value = ''; // reset
  };

  const handleFile = (file: File) => {
    const ext = getExtension(file.name);
    const isSupportedExt = ext ? SUPPORTED_EXTENSIONS.includes(ext) : false;
    const isSupportedMime = SUPPORTED_MIMES.includes(file.type);
    const mimeType = file.type || 'application/octet-stream';
    const sizeBucket = getFileSizeBucket(file.size);

    trackImagesMvpEvent('upload_selected', {
      extension: ext,
      mime_type: mimeType,
      size_bytes: file.size,
      size_bucket: sizeBucket,
      has_trial_email: Boolean(trialEmail),
    });

    if (!isSupportedExt && !isSupportedMime) {
      trackImagesMvpEvent('upload_rejected', {
        extension: ext,
        mime_type: mimeType,
        size_bytes: file.size,
        size_bucket: sizeBucket,
        reason: 'unsupported_format',
      });
      toast({
        title: 'Unsupported File',
        description:
          'Please upload a photo (JPG, PNG, HEIC from iPhone, or WebP).',
        variant: 'destructive',
      });
      return;
    }

    // Client-side file size validation (100MB limit)
    const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
    if (file.size > MAX_FILE_SIZE) {
      const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
      trackImagesMvpEvent('upload_rejected', {
        extension: ext,
        mime_type: mimeType,
        size_bytes: file.size,
        size_bucket: sizeBucket,
        reason: 'file_too_large',
      });
      toast({
        title: 'File Too Large',
        description: `Your file is ${sizeMB}MB. Maximum size is 100MB. Try compressing or resizing the image.`,
        variant: 'destructive',
      });
      return;
    }

    if (!trialEmail) {
      setPendingFile(file);
      setShowTrialModal(true);
    } else {
      uploadFile(file, trialEmail);
    }
  };

  const uploadFile = async (file: File, email: string) => {
    setIsUploading(true);
    setUploadProgress(0);
    const startedAt = Date.now();

    // Get session ID for WebSocket progress tracking
    const sessionId = getImagesMvpSessionId() || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setCurrentSessionId(sessionId);
    setShowProgressTracker(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('trial_email', email);
    if (file.lastModified) {
      formData.append('client_last_modified', String(file.lastModified));
    }

    // Add session ID for WebSocket progress tracking
    formData.append('session_id', sessionId);

    const sizeBucket = getFileSizeBucket(file.size);
    const mimeType = file.type || 'application/octet-stream';
    const extension = getExtension(file.name);

    trackImagesMvpEvent('analysis_started', {
      extension,
      mime_type: mimeType,
      size_bytes: file.size,
      size_bucket: sizeBucket,
      has_trial_email: Boolean(email),
    });

    try {
      const data = await new Promise<any>((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            setUploadProgress(percentComplete);
          }
        };

        xhr.onload = () => {
          let responseData;
          try {
            responseData = xhr.responseText ? JSON.parse(xhr.responseText) : null;
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
              data: responseData
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
      // Hide progress tracker and navigate to results
      setShowProgressTracker(false);
      setTimeout(() => {
        navigate('/images_mvp/results', { state: { metadata: data } });
      }, 500);
    } catch (err: any) {
      console.error(err);

      const errorMessage = err.message || 'Upload failed';
      const status = err.status || 500;

      trackImagesMvpEvent('analysis_completed', {
        success: false,
        status: status,
        error_message: errorMessage,
        extension,
        mime_type: mimeType,
        size_bucket: sizeBucket,
        elapsed_ms: Date.now() - startedAt,
      });

      if (status === 402) {
        // Trigger Credit Purchase Flow
        trackImagesMvpEvent('paywall_viewed', {
          reason: 'trial_exhausted',
          extension,
          mime_type: mimeType,
        });
        toast({
          title: 'Trial Limit Reached',
          description:
            "You've used your 2 free checks. Unlock more with credits.",
          variant: 'destructive',
        });
        setShowPricingModal(true);
        return;
      }

      setUploadError(true);
      setShowProgressTracker(false); // Hide progress tracker on error
      setTimeout(() => setUploadError(false), 3000);

      if (errorMessage.toLowerCase().includes('failed to fetch') || errorMessage === 'Network error') {
        toast({
          title: 'Backend unavailable',
          description:
            'API is not reachable. Start the server with `npm run dev:server`.',
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
    <div className="w-full max-w-lg mx-auto">
      <TrialAccessModal
        isOpen={showTrialModal}
        onClose={() => {
          setShowTrialModal(false);
          setPendingFile(null);
        }}
        onConfirm={email => {
          setTrialEmail(email);
          localStorage.setItem('metaextract_trial_email', email);
          setShowTrialModal(false);
          if (pendingFile) uploadFile(pendingFile, email);
        }}
      />
      <PricingModal
        isOpen={showPricingModal}
        onClose={() => setShowPricingModal(false)}
        defaultEmail={trialEmail || undefined}
      />

      {/* Real-time Progress Tracker */}
      {showProgressTracker && currentSessionId && (
        <div className="mb-6">
          <ProgressTracker sessionId={currentSessionId} />
        </div>
      )}

      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() =>
          !isUploading && document.getElementById('mvp-upload')?.click()
        }
        onKeyDown={onKeyDown}
        role="button"
        tabIndex={0}
        aria-label="Upload image drop zone. Drag and drop a file here or press enter to browse."
        className={cn(
          'relative border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer overflow-hidden group outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-black',
          isUploading
            ? 'border-primary/40 bg-black/40 backdrop-blur-sm'
            : isDragActive
              ? 'border-primary bg-primary/5 bg-black/20 backdrop-blur-sm'
              : 'border-white/10 bg-black/20 backdrop-blur-sm hover:border-primary/50 hover:bg-white/5'
        )}
      >
        <input
          id="mvp-upload"
          type="file"
          className="hidden"
          accept={SUPPORTED_EXTENSIONS.join(',')}
          onChange={handleFileSelect}
        />

        {isUploading ? (
          <>
            {/* Progress bar background */}
            <div className="absolute inset-0 bg-black/20 rounded-xl" />
            {/* Progress bar fill */}
            <motion.div
              className={`absolute left-0 top-0 h-full rounded-xl ${uploadError
                ? 'bg-gradient-to-r from-red-500/40 to-red-500/20'
                : 'bg-gradient-to-r from-emerald-500/40 to-emerald-500/20'
                }`}
              initial={{ width: '0%' }}
              animate={{ width: `${uploadProgress}%` }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.3 }}
            />
            {/* Content overlay */}
            <div className="relative flex flex-col items-center justify-center gap-4 w-full h-full">
              <p className="text-white font-mono text-sm">
                {uploadError ? 'Upload Failed' : (uploadProgress < 100 ? 'Uploading...' : 'Extracting Metadata...')}
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
            <div className="mb-4">
              <div className="w-16 h-16 bg-gradient-to-tr from-primary/20 to-purple-500/20 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                <Upload className="w-8 h-8 text-primary" aria-hidden="true" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">
              Drop your image here
            </h3>
            <p className="text-slate-300 text-sm mb-6">
              Supports popular photo formats: JPG, PNG, HEIC (iPhone), WebP{' '}
              <br />
              <span className="text-primary text-xs font-mono mt-1 block">
                <Zap className="w-3 h-3 inline mr-1" aria-hidden="true" />2 Free Checks Included
              </span>
            </p>
            <Button
              variant="outline"
              className="border-white/10 hover:bg-white/5 hover:text-white"
            >
              Browse Files
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
