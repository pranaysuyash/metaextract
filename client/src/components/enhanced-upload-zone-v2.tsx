import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Upload,
  File,
  Image,
  Video,
  Music,
  FileText,
  X,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Zap,
  Clock,
  Timer,
  Info,
  Sparkles,
  Trophy,
  Star
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { analyzeFile, type FileAnalysis } from '@/utils/fileAnalysis';
import {
  estimateProcessingTime,
  type ProcessingEstimate,
} from '@/utils/processingEstimates';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface FileState {
  file: File;
  id: string;
  preview?: string;
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  result?: any;
  error?: string;
  analysis?: FileAnalysis;
  estimate?: ProcessingEstimate;
}

interface EnhancedUploadZoneProps {
  onResults: (results: any[]) => void;
  tier: string;
  maxFiles?: number;
  className?: string;
  advanced?: boolean;
  showTierInfo?: boolean;
}

/**
 * Enhanced Upload Zone Component
 * Provides an improved drag-and-drop interface with better UX, real-time feedback,
 * and detailed file analysis information.
 */
export function EnhancedUploadZoneV2({ 
  onResults, 
  tier, 
  maxFiles = 10, 
  className,
  advanced = false,
  showTierInfo = true
}: EnhancedUploadZoneProps) {
  const [files, setFiles] = useState<FileState[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    setDragActive(false);
    
    // Show toast for rejected files
    if (fileRejections.length > 0) {
      fileRejections.forEach(({ file, errors }) => {
        toast({
          title: `File Rejected: ${file.name}`,
          description: errors.map((e: any) => e.message).join(', '),
          variant: 'destructive',
        });
      });
    }

    // Process accepted files
    const newFiles = acceptedFiles.slice(0, maxFiles - files.length).map(file => {
      const id = `${Date.now()}-${Math.random()}`;
      const analysis = analyzeFile(file, tier);
      const estimate = estimateProcessingTime(file, tier);
      
      return {
        file,
        id,
        status: 'pending' as const,
        progress: 0,
        analysis,
        estimate,
      };
    });

    if (newFiles.length > 0) {
      setFiles(prev => [...prev, ...newFiles]);
    }

    if (files.length + newFiles.length >= maxFiles) {
      toast({
        title: 'Maximum files reached',
        description: `You can only upload up to ${maxFiles} files at a time.`,
      });
    }
  }, [files.length, maxFiles, tier, toast]);

  // Configure dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.heic', '.heif'],
      'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp'],
      'audio/*': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/zip': ['.zip', '.rar', '.7z'],
    },
    maxFiles: maxFiles - files.length,
    maxSize: 200 * 1024 * 1024, // 200MB
  });

  // Handle file removal
  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  // Handle file submission
  const handleSubmit = async () => {
    if (files.length === 0) return;

    setIsSubmitting(true);
    
    try {
      // Simulate processing for demo purposes
      const updatedFiles = [...files];
      
      for (let i = 0; i < updatedFiles.length; i++) {
        const fileState = updatedFiles[i];
        
        // Update status to uploading
        setFiles(prev => prev.map(f => 
          f.id === fileState.id ? { ...f, status: 'uploading', progress: 10 } : f
        ));
        
        // Simulate upload progress
        for (let progress = 10; progress <= 60; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 200));
          setFiles(prev => prev.map(f => 
            f.id === fileState.id ? { ...f, progress } : f
          ));
        }
        
        // Update status to processing
        setFiles(prev => prev.map(f => 
          f.id === fileState.id ? { ...f, status: 'processing', progress: 70 } : f
        ));
        
        // Simulate processing
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Update to complete
        setFiles(prev => prev.map(f => 
          f.id === fileState.id ? { ...f, status: 'complete', progress: 100, result: { fields: 1500 } } : f
        ));
      }
      
      // Call the results handler after all files are processed
      setTimeout(() => {
        onResults(updatedFiles.map(f => f.result));
        setIsSubmitting(false);
      }, 500);
      
    } catch (error) {
      console.error('Submission error:', error);
      toast({
        title: 'Submission Error',
        description: 'There was an error processing your files. Please try again.',
        variant: 'destructive',
      });
      setIsSubmitting(false);
    }
  };

  // Clear all files
  const clearAllFiles = () => {
    setFiles([]);
  };

  // Get file icon based on type
  const getFileIcon = (file: File) => {
    const type = file.type.split('/')[0];
    const ext = file.name.split('.').pop()?.toLowerCase();

    if (type === 'image') return <Image className="w-5 h-5" />;
    if (type === 'video') return <Video className="w-5 h-5" />;
    if (type === 'audio') return <Music className="w-5 h-5" />;
    if (ext === 'pdf') return <FileText className="w-5 h-5" />;
    return <File className="w-5 h-5" />;
  };

  // Get status badge
  const getStatusBadge = (status: FileState['status']) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      case 'uploading':
        return <Badge variant="secondary">Uploading</Badge>;
      case 'processing':
        return <Badge variant="secondary">Processing</Badge>;
      case 'complete':
        return <Badge variant="default"><CheckCircle2 className="w-3 h-3 mr-1" /> Complete</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  // Get processing time estimate
  const getProcessingEstimate = (estimate?: ProcessingEstimate) => {
    if (!estimate) return 'Calculating...';
    
    if (estimate.estimatedTime < 60) {
      return `${Math.round(estimate.estimatedTime)}s`;
    } else {
      const minutes = Math.floor(estimate.estimatedTime / 60);
      const seconds = Math.round(estimate.estimatedTime % 60);
      return `${minutes}m ${seconds}s`;
    }
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Upload Area */}
      <Card 
        {...getRootProps()} 
        className={cn(
          "border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer hover:border-primary/50",
          isDragActive ? "border-primary bg-primary/5 scale-[1.02]" : "border-gray-300 dark:border-gray-600",
          files.length > 0 ? "mt-0" : ""
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center gap-4">
          <motion.div
            animate={{ scale: isDragActive ? 1.1 : 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
          >
            <Upload className="w-12 h-12 mx-auto text-muted-foreground" />
          </motion.div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">
              Drop files here or click to browse
            </h3>
            <p className="text-sm text-muted-foreground">
              Support for images, videos, audio, PDFs, and more. Max file size: 200MB.
            </p>
          </div>
          
          <Button 
            type="button" 
            variant="outline" 
            className="mt-2"
            onClick={(e) => {
              e.stopPropagation();
              if (fileInputRef.current) {
                fileInputRef.current.click();
              }
            }}
          >
            Browse Files
          </Button>
        </div>
      </Card>

      {/* Tier Information */}
      {showTierInfo && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 dark:from-blue-500/5 dark:to-purple-500/5 p-4 rounded-lg border border-blue-200/30 dark:border-blue-800/30"
        >
          <div className="flex items-start gap-3">
            <Star className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-foreground">Current Tier: {tier.toUpperCase()}</h4>
              <p className="text-sm text-muted-foreground mt-1">
                {tier === 'free' && 'Extract up to 50 metadata fields'}
                {tier === 'starter' && 'Extract up to 200 metadata fields'}
                {tier === 'pro' && 'Extract up to 7,000+ metadata fields including MakerNotes, IPTC, XMP'}
                {tier === 'super' && 'Extract all 15,000+ metadata fields with advanced analysis'}
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4"
          >
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">
                Files ({files.length}/{maxFiles})
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAllFiles}
                className="text-destructive hover:text-destructive"
              >
                Clear All
              </Button>
            </div>

            <div className="grid gap-4">
              {files.map((fileState) => (
                <motion.div
                  key={fileState.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="border rounded-lg p-4 bg-background"
                >
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="text-primary">
                        {getFileIcon(fileState.file)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-medium truncate">{fileState.file.name}</p>
                          {fileState.analysis?.warnings.length > 0 && (
                            <Tooltip>
                              <TooltipTrigger>
                                <AlertCircle className="w-4 h-4 text-yellow-500" />
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>{fileState.analysis.warnings.join(', ')}</p>
                              </TooltipContent>
                            </Tooltip>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                          <span>{(fileState.file.size / 1024 / 1024).toFixed(2)} MB</span>
                          <span>{fileState.file.type || 'Unknown type'}</span>
                          {fileState.estimate && (
                            <div className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              <span>{getProcessingEstimate(fileState.estimate)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {getStatusBadge(fileState.status)}
                      
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeFile(fileState.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {(fileState.status === 'uploading' || fileState.status === 'processing') && (
                    <div className="mt-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span>
                          {fileState.status === 'uploading' ? 'Uploading...' : 'Processing...'}
                        </span>
                        <span>{fileState.progress}%</span>
                      </div>
                      <Progress value={fileState.progress} className="h-2" />
                    </div>
                  )}
                  
                  {fileState.status === 'complete' && fileState.result && (
                    <div className="mt-3 p-3 bg-green-50 dark:bg-green-950/20 rounded-md">
                      <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
                        <CheckCircle2 className="w-4 h-4" />
                        <span className="font-medium">
                          {fileState.result.fields} metadata fields extracted
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {fileState.analysis?.suggestions.length > 0 && (
                    <div className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                      <p>Suggestions: {fileState.analysis.suggestions.join(', ')}</p>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Submit Button */}
      {files.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row gap-3 pt-4"
        >
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || files.some(f => f.status !== 'pending')}
            className="flex-1 relative"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Extract Metadata
              </>
            )}
            
            {advanced && (
              <Badge variant="secondary" className="ml-2">
                Advanced Mode
              </Badge>
            )}
          </Button>
          
          <Button
            variant="outline"
            onClick={clearAllFiles}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
        </motion.div>
      )}

      {/* Empty State Tips */}
      {files.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8"
        >
          <div className="p-4 bg-muted/50 rounded-lg border">
            <div className="flex items-center gap-2 mb-2">
              <Trophy className="w-5 h-5 text-amber-500" />
              <h4 className="font-medium">Best Results</h4>
            </div>
            <p className="text-sm text-muted-foreground">
              Upload original files without compression for maximum metadata extraction.
            </p>
          </div>
          
          <div className="p-4 bg-muted/50 rounded-lg border">
            <div className="flex items-center gap-2 mb-2">
              <Info className="w-5 h-5 text-blue-500" />
              <h4 className="font-medium">Supported Formats</h4>
            </div>
            <p className="text-sm text-muted-foreground">
              JPG, PNG, TIFF, MP4, MOV, MP3, PDF, and 50+ other formats.
            </p>
          </div>
          
          <div className="p-4 bg-muted/50 rounded-lg border">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-5 h-5 text-purple-500" />
              <h4 className="font-medium">Fast Processing</h4>
            </div>
            <p className="text-sm text-muted-foreground">
              Most files process in under 30 seconds with our optimized engines.
            </p>
          </div>
        </motion.div>
      )}
    </div>
  );
}