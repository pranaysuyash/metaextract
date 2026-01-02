import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  AlertCircle,
  Cpu,
  Scan,
  Database,
  Lock,
  X,
  FileWarning,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { TrialAccessModal } from '@/components/trial-access-modal';

// File validation configuration
const FILE_CONFIG = {
  maxSizeBytes: 2000 * 1024 * 1024, // 2GB for development testing
  maxSizeMB: 2000,
  supportedCategories: {
    images: [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
      'image/tiff',
      'image/heic',
      'image/heif',
      'image/bmp',
      'image/svg+xml',
      'image/x-icon',
      'image/x-canon-cr2',
      'image/x-canon-cr3',
      'image/x-nikon-nef',
      'image/x-sony-arw',
      'image/x-adobe-dng',
      'image/x-fuji-raf',
      'image/x-olympus-orf',
      'image/x-panasonic-rw2',
      'image/x-pentax-pef',
    ],
    videos: [
      'video/mp4',
      'video/quicktime',
      'video/x-msvideo',
      'video/x-matroska',
      'video/webm',
      'video/mpeg',
      'video/3gpp',
      'video/x-flv',
    ],
    audio: [
      'audio/mpeg',
      'audio/wav',
      'audio/flac',
      'audio/aac',
      'audio/ogg',
      'audio/x-m4a',
      'audio/webm',
    ],
    documents: [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ],
    specialized: [
      'application/dicom',
      'application/fits',
      'application/x-hdf5',
      'application/x-netcdf',
    ],
  },
  // Common extensions for files that may not have correct MIME types
  supportedExtensions: [
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.webp',
    '.tiff',
    '.tif',
    '.heic',
    '.heif',
    '.bmp',
    '.svg',
    '.ico',
    '.cr2',
    '.cr3',
    '.nef',
    '.arw',
    '.dng',
    '.raf',
    '.orf',
    '.rw2',
    '.pef',
    '.raw',
    '.mp4',
    '.mov',
    '.avi',
    '.mkv',
    '.webm',
    '.mpeg',
    '.mpg',
    '.3gp',
    '.flv',
    '.mp3',
    '.wav',
    '.flac',
    '.aac',
    '.ogg',
    '.m4a',
    '.pdf',
    '.doc',
    '.docx',
    '.dcm',
    '.dicom',
    '.fits',
    '.fit',
    '.fts',
    '.h5',
    '.hdf5',
    '.nc',
    '.nc4',
  ],
};

function getSessionId(): string {
  if (typeof window === 'undefined') return 'anonymous';
  let sessionId = window.localStorage.getItem('metaextract_session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    window.localStorage.setItem('metaextract_session_id', sessionId);
  }
  return sessionId;
}

interface ValidationResult {
  valid: boolean;
  error?: string;
  warning?: string;
}

function validateFile(file: File): ValidationResult {
  // Check file size
  if (file.size > FILE_CONFIG.maxSizeBytes) {
    return {
      valid: false,
      error: `File size (${(file.size / 1024 / 1024).toFixed(
        1
      )}MB) exceeds maximum of ${FILE_CONFIG.maxSizeMB}MB`,
    };
  }

  // Check if file is empty
  if (file.size === 0) {
    return {
      valid: false,
      error: 'File is empty',
    };
  }

  // Check MIME type
  const allSupportedMimes = Object.values(
    FILE_CONFIG.supportedCategories
  ).flat();
  const mimeSupported = allSupportedMimes.includes(file.type);

  // Check extension as fallback
  const extension = '.' + file.name.split('.').pop()?.toLowerCase();
  const extensionSupported =
    FILE_CONFIG.supportedExtensions.includes(extension);

  if (!mimeSupported && !extensionSupported) {
    return {
      valid: false,
      error: `Unsupported file type: ${file.type || extension
        }. We support images, videos, audio, PDFs, and specialized formats (DICOM, FITS, etc.)`,
    };
  }

  // Warning for potentially problematic files
  if (!mimeSupported && extensionSupported) {
    return {
      valid: true,
      warning: `File type "${file.type}" not recognized, but extension "${extension}" is supported. Processing will continue.`,
    };
  }

  return { valid: true };
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

interface UploadError {
  title: string;
  message: string;
  canRetry: boolean;
  showPricingCTA?: boolean;
}

export function UploadZone() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStage, setProcessingStage] = useState('Initializing...');
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<UploadError | null>(null);
  const [trialEmail, setTrialEmail] = useState<string | null>(null);
  const [showTrialModal, setShowTrialModal] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const stored = window.localStorage.getItem('metaextract_trial_email');
    if (stored) setTrialEmail(stored);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Only set to false if we're leaving the drop zone entirely
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      setUploadError(null);

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        if (files.length > 1) {
          toast({
            title: 'Multiple files detected',
            description:
              'Only the first file will be processed. Use batch upload for multiple files.',
            variant: 'default',
          });
        }
        processFile(files[0]);
      }
    },
    [toast]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setUploadError(null);
      if (e.target.files && e.target.files.length > 0) {
        processFile(e.target.files[0]);
      }
      // Reset input so same file can be selected again
      e.target.value = '';
    },
    []
  );

  const processFile = async (file: File) => {
    // Validate file
    const validation = validateFile(file);

    if (!validation.valid) {
      setUploadError({
        title: 'Invalid File',
        message: validation.error || 'File validation failed',
        canRetry: true,
      });
      toast({
        title: 'File Validation Failed',
        description: validation.error,
        variant: 'destructive',
      });
      return;
    }

    if (validation.warning) {
      toast({
        title: 'File Notice',
        description: validation.warning,
        variant: 'default',
      });
    }

    setCurrentFile(file);
    if (!trialEmail) {
      setPendingFile(file);
      setShowTrialModal(true);
      return;
    }
    startUpload(file);
  };

  const startUpload = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);

    const stages = [
      'Uploading file to secure enclave...',
      'Analyzing file header...',
      'Extracting EXIF data...',
      'Parsing MakerNotes...',
      'Decoding GPS coordinates...',
      'Scanning for hidden XMP...',
      'Detecting file context...',
      'Generating forensic report...',
    ];

    let progressInterval: NodeJS.Timeout | null = null;

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('file', file);
      if (trialEmail) {
        formData.append('trial_email', trialEmail);
      }
      formData.append('session_id', getSessionId());

      // Simulate progress during upload
      let progress = 0;
      progressInterval = setInterval(() => {
        if (progress < 90) {
          progress += Math.random() * 8;
          setUploadProgress(Math.min(progress, 90));

          // Update stage text based on progress
          const stageIndex = Math.floor((progress / 90) * stages.length);
          if (stages[stageIndex]) setProcessingStage(stages[stageIndex]);
        }
      }, 250);

      // Make actual API call to extract metadata
      const response = await fetch('/api/extract', {
        method: 'POST',
        body: formData,
      });

      if (progressInterval) clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error ||
          errorData.message ||
          `Server error: ${response.status}`
        );
      }

      const metadata = await response.json();

      // Check for API-level errors
      if (metadata.error) {
        throw new Error(metadata.error);
      }

      // Complete progress
      setUploadProgress(100);
      setProcessingStage('Extraction complete!');

      // Store metadata in sessionStorage for results page
      sessionStorage.setItem('currentMetadata', JSON.stringify(metadata));

      // Navigate to results
      setTimeout(() => {
        navigate('/results');
      }, 600);
    } catch (error) {
      if (progressInterval) clearInterval(progressInterval);
      console.error('Upload error:', error);

      const errorMessage =
        error instanceof Error ? error.message : 'An unexpected error occurred';

      // Determine if error is retryable
      const isNetworkError =
        errorMessage.includes('fetch') || errorMessage.includes('network');
      const isServerError =
        errorMessage.includes('500') || errorMessage.includes('503');
      const isPaymentIssue =
        errorMessage.toLowerCase().includes('payment required') ||
        errorMessage.toLowerCase().includes('insufficient credits');

      setUploadError({
        title: isNetworkError ? 'Connection Error' : 'Extraction Failed',
        message: errorMessage,
        canRetry: isNetworkError || isServerError,
        showPricingCTA: isPaymentIssue,
      });

      toast({
        title: 'Extraction Failed',
        description: errorMessage,
        variant: 'destructive',
      });

      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleRetry = () => {
    if (currentFile) {
      setUploadError(null);
      startUpload(currentFile);
    }
  };

  const handleCancel = () => {
    setUploadError(null);
    setCurrentFile(null);
    setIsUploading(false);
    setUploadProgress(0);
  };

  const handleTrialConfirm = (email: string) => {
    setTrialEmail(email);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('metaextract_trial_email', email);
    }
    setShowTrialModal(false);
    if (pendingFile) {
      const fileToUpload = pendingFile;
      setPendingFile(null);
      startUpload(fileToUpload);
    }
  };

  return (
    <div className='w-full max-w-xl mx-auto'>
      <TrialAccessModal
        isOpen={showTrialModal}
        onClose={() => {
          setShowTrialModal(false);
          setPendingFile(null);
          setCurrentFile(null);
        }}
        onConfirm={handleTrialConfirm}
      />
      <AnimatePresence mode='wait'>
        {uploadError ? (
          <motion.div
            key='error'
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className='bg-black/40 backdrop-blur-md rounded-xl border border-red-500/30 shadow-2xl p-8 relative overflow-hidden'
          >
            <div className='flex items-start gap-4 mb-6'>
              <div className='p-3 bg-red-500/10 rounded-lg border border-red-500/20 shrink-0'>
                <FileWarning className='w-6 h-6 text-red-500' />
              </div>
              <div className='flex-1 min-w-0'>
                <h4 className='font-mono font-bold text-white mb-1'>
                  {uploadError.title}
                </h4>
                <p className='text-sm text-slate-400 break-words'>
                  {uploadError.message}
                </p>
              </div>
              <button
                type='button'
                onClick={handleCancel}
                className='p-1 text-slate-500 hover:text-white transition-colors shrink-0'
                aria-label='Dismiss error'
                title='Dismiss'
              >
                <X className='w-5 h-5' />
              </button>
            </div>

            {currentFile && (
              <div className='mb-6 p-3 bg-white/5 rounded-lg border border-white/10'>
                <div className='text-xs text-slate-400 font-mono'>
                  <span className='text-slate-500'>FILE:</span>{' '}
                  {currentFile.name}
                </div>
                <div className='text-xs text-slate-500 font-mono mt-1'>
                  <span>SIZE:</span> {formatFileSize(currentFile.size)} |{' '}
                  <span>TYPE:</span> {currentFile.type || 'unknown'}
                </div>
              </div>
            )}

            <div className='flex gap-3'>
              {uploadError.canRetry && (
                <Button
                  onClick={handleRetry}
                  className='flex-1 bg-primary hover:bg-primary/90 text-black font-bold'
                >
                  Try Again
                </Button>
              )}
              {uploadError.showPricingCTA && (
                <Button
                  onClick={() => navigate('/')}
                  variant='outline'
                  className='flex-1 border-white/20 text-white hover:bg-white/10'
                >
                  View Pricing
                </Button>
              )}
              <Button
                onClick={handleCancel}
                variant='outline'
                className='flex-1 border-white/20 text-white hover:bg-white/10'
              >
                Select Different File
              </Button>
            </div>
          </motion.div>
        ) : !isUploading ? (
          <motion.div
            key='upload'
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className={cn(
              'relative group rounded-xl border border-dashed transition-all duration-300 ease-in-out cursor-pointer overflow-hidden backdrop-blur-sm',
              isDragging
                ? 'border-primary bg-primary/5 shadow-[0_0_30px_rgba(99,102,241,0.2)]'
                : 'border-white/10 bg-white/5 hover:border-primary/50 hover:bg-white/10'
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-upload')?.click()}
          >
            <input
              id='file-upload'
              type='file'
              className='hidden'
              onChange={handleFileSelect}
              accept={FILE_CONFIG.supportedExtensions.join(',')}
            />

            {/* Tech Decoration Lines */}
            <div className='absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-white/20 group-hover:border-primary transition-colors' />
            <div className='absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-white/20 group-hover:border-primary transition-colors' />
            <div className='absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-white/20 group-hover:border-primary transition-colors' />
            <div className='absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-white/20 group-hover:border-primary transition-colors' />

            <div className='flex flex-col items-center justify-center py-20 px-6 text-center'>
              <div
                className={cn(
                  'mb-8 p-4 rounded-full bg-white/5 transition-all duration-300 group-hover:scale-110 group-hover:bg-primary/20',
                  isDragging && 'bg-primary/20 scale-110'
                )}
              >
                <Upload
                  className={cn(
                    'w-8 h-8 text-slate-400 group-hover:text-primary transition-colors',
                    isDragging && 'text-primary'
                  )}
                />
              </div>
              <h3 className='text-xl font-bold text-white mb-2 tracking-tight'>
                Upload Evidence
              </h3>
              <p className='text-slate-400 mb-4 max-w-xs mx-auto text-sm'>
                Drag & drop media files here or browse to start.
              </p>
              <div className='text-slate-500 text-xs mb-8 space-y-1'>
                <p>Supports 400+ formats including RAW, HEIC, DICOM, FITS</p>
                <p className='text-slate-600'>
                  Max file size: {FILE_CONFIG.maxSizeMB}MB
                </p>
                <p className='text-slate-600'>
                  {trialEmail
                    ? 'Free report unlocked'
                    : '1 free full report with email'}
                </p>
              </div>
              <Button className='h-10 px-8 bg-white/10 text-white hover:bg-primary hover:text-black border border-white/20 hover:border-primary font-bold text-sm rounded transition-all duration-300 shadow-lg'>
                Select File
              </Button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key='processing'
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className='bg-black/40 backdrop-blur-md rounded-xl border border-primary/20 shadow-2xl p-8 relative overflow-hidden'
          >
            {/* Scanning line effect */}
            <div className='absolute inset-0 scanline opacity-20 pointer-events-none'></div>

            <div className='flex items-center gap-4 mb-6 relative z-10'>
              <div className='p-3 bg-primary/10 rounded-lg border border-primary/20'>
                <Cpu className='w-6 h-6 text-primary animate-pulse' />
              </div>
              <div className='flex-1 min-w-0'>
                <h4 className='font-mono font-bold text-white flex items-center gap-2'>
                  PROCESSING <span className='animate-pulse'>_</span>
                </h4>
                <p className='text-xs font-mono text-primary/80 truncate'>
                  {processingStage}
                </p>
              </div>
              <div className='text-right shrink-0 min-w-[60px]'>
                <span className='text-2xl font-bold text-white font-mono'>
                  {Math.round(uploadProgress)}%
                </span>
              </div>
            </div>

            {currentFile && (
              <div className='mb-6 p-3 bg-white/5 rounded-lg border border-white/10 relative z-10'>
                <div className='text-xs text-slate-400 font-mono truncate'>
                  <span className='text-slate-500'>FILE:</span>{' '}
                  {currentFile.name}
                </div>
                <div className='text-xs text-slate-500 font-mono mt-1'>
                  <span>SIZE:</span> {formatFileSize(currentFile.size)}
                </div>
              </div>
            )}

            <div className='space-y-2 relative z-10'>
              <div className='h-1.5 w-full bg-white/10 rounded-full overflow-hidden'>
                <motion.div
                  className='h-full bg-gradient-to-r from-primary to-primary/80 shadow-[0_0_10px_rgba(99,102,241,0.5)]'
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  transition={{ ease: 'linear', duration: 0.1 }}
                />
              </div>
              <div className='flex justify-between text-[10px] font-mono text-slate-500 uppercase'>
                <span className={uploadProgress > 10 ? 'text-primary' : ''}>
                  Header
                </span>
                <span className={uploadProgress > 40 ? 'text-primary' : ''}>
                  Body
                </span>
                <span className={uploadProgress > 70 ? 'text-primary' : ''}>
                  Analysis
                </span>
                <span className={uploadProgress > 95 ? 'text-primary' : ''}>
                  Complete
                </span>
              </div>
            </div>

            <div className='mt-8 grid grid-cols-3 gap-2 relative z-10'>
              <div className='bg-white/5 p-2 rounded border border-white/5 text-center'>
                <Database className='w-4 h-4 text-slate-500 mx-auto mb-1' />
                <span className='text-[10px] text-slate-400 block'>
                  Extensive field coverage
                </span>
              </div>
              <div className='bg-white/5 p-2 rounded border border-white/5 text-center'>
                <Scan className='w-4 h-4 text-slate-500 mx-auto mb-1' />
                <span className='text-[10px] text-slate-400 block'>
                  Deep Scan
                </span>
              </div>
              <div className='bg-white/5 p-2 rounded border border-white/5 text-center'>
                <Lock className='w-4 h-4 text-slate-500 mx-auto mb-1' />
                <span className='text-[10px] text-slate-400 block'>
                  Encrypted
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
