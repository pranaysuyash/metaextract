import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Loader2, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { TrialAccessModal } from '@/components/trial-access-modal';
import { PricingModal } from '@/components/images-mvp/pricing-modal';
import {
  getFileSizeBucket,
  getImagesMvpSessionId,
  trackImagesMvpEvent,
} from '@/lib/images-mvp-analytics';

const SUPPORTED_EXTENSIONS = [
  '.jpg',
  '.jpeg',
  '.png',
  '.heic',
  '.heif',
  '.webp',
];

const SUPPORTED_MIMES = [
  'image/jpeg',
  'image/png',
  'image/heic',
  'image/heif',
  'image/webp',
];

export function SimpleUploadZone() {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [trialEmail, setTrialEmail] = useState<string | null>(null);
  const [showTrialModal, setShowTrialModal] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [showPricingModal, setShowPricingModal] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

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
        description: 'Please upload a JPG, PNG, HEIC, or WebP image.',
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
    const startedAt = Date.now();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('trial_email', email);
    if (file.lastModified) {
      formData.append('client_last_modified', String(file.lastModified));
    }

    // Get session ID (reuse main app session logic)
    const sessionId = getImagesMvpSessionId();
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

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
      const res = await fetch('/api/images_mvp/extract', {
        method: 'POST',
        body: formData,
      });

      const responseText = await res.text();
      let data: any = null;
      try {
        data = responseText ? JSON.parse(responseText) : null;
      } catch {
        data = null;
      }

      if (!res.ok) {
        const errorMessage =
          typeof data?.error === 'string'
            ? data.error
            : data?.error?.message || data?.message || responseText || 'Extraction failed';
        trackImagesMvpEvent('analysis_completed', {
          success: false,
          status: res.status,
          error_message: errorMessage,
          extension,
          mime_type: mimeType,
          size_bucket: sizeBucket,
          elapsed_ms: Date.now() - startedAt,
        });

        if (res.status === 402) {
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
        throw new Error(errorMessage);
      }

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

      sessionStorage.setItem('currentMetadata', JSON.stringify(data));
      // Navigate to results page with metadata in state
      navigate('/images_mvp/results', { state: { metadata: data } });
    } catch (err: any) {
      console.error(err);
      const fallbackMessage =
        typeof err?.message === 'string' ? err.message : 'Network error';
      if (fallbackMessage.toLowerCase().includes('failed to fetch')) {
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
        description: err.message || 'Upload failed',
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

      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => document.getElementById('mvp-upload')?.click()}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer bg-black/20 backdrop-blur-sm group',
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-white/10 hover:border-primary/50 hover:bg-white/5',
          isUploading && 'pointer-events-none opacity-50'
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
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 text-primary animate-spin" />
            <p className="text-white font-mono text-sm animate-pulse">
              Extracting Metadata...
            </p>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <div className="w-16 h-16 bg-gradient-to-tr from-primary/20 to-purple-500/20 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                <Upload className="w-8 h-8 text-primary" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">
              Drop your image here
            </h3>
            <p className="text-slate-400 text-sm mb-6">
              Supports JPG, PNG, HEIC (iPhone), WebP. <br />
              <span className="text-primary/80 text-xs font-mono mt-1 block">
                <Zap className="w-3 h-3 inline mr-1" />2 Free Checks Included
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
