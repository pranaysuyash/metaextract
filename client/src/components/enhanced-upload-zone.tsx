import React, { useState, useCallback, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
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
  Timer
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { analyzeFile, type FileAnalysis } from "@/utils/fileAnalysis";
import { estimateProcessingTime, type ProcessingEstimate } from "@/utils/processingEstimates";

interface FileState {
  file: File;
  id: string;
  preview?: string;
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  result?: any;
  error?: string;
  analysis?: FileAnalysis; // File type analysis with warnings/suggestions
  estimate?: ProcessingEstimate; // Processing time estimate
}

interface EnhancedUploadZoneProps {
  onResults: (results: any[]) => void;
  tier: string;
  maxFiles?: number;
  className?: string;
  advanced?: boolean;
}

const ACCEPTED_TYPES = {
  // Standard media types
  'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff', '.tif', '.bmp', '.heic', '.heif', '.svg', '.psd'],
  'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.3gp', '.flv', '.wmv', '.asf', '.rm', '.rmvb'],
  'audio/*': ['.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.aiff', '.opus', '.wma', '.ac3', '.dts'],

  // Documents
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/vnd.ms-excel': ['.xls'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-powerpoint': ['.ppt'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  'text/plain': ['.txt', '.md'],
  'text/csv': ['.csv'],
  'text/html': ['.html', '.htm'],
  'application/xml': ['.xml'],
  'application/json': ['.json'],

  // Medical imaging
  'application/dicom': ['.dcm', '.dicom'],

  // Astronomical data
  'application/fits': ['.fits', '.fit', '.fts'],

  // Scientific data
  'application/x-hdf': ['.h5', '.hdf5', '.he5'],
  'application/x-netcdf': ['.nc', '.netcdf', '.nc4'],

  // Geospatial
  'application/x-shapefile': ['.shp'],

  // Emerging technology formats
  'application/x-ai-model': ['.ai', '.ml', '.model', '.h5', '.pb', '.onnx', '.tflite', '.pt', '.pth', '.ckpt', '.pkl', '.joblib'],
  'application/x-blockchain': ['.blockchain', '.chain', '.ledger', '.crypto', '.nft', '.token'],
  'application/x-ar-vr': ['.ar', '.vr', '.xr', '.gltf', '.glb', '.usdz', '.reality'],
  'application/x-iot': ['.iot', '.device', '.sensor'],
  'application/x-quantum': ['.quantum', '.qasm', '.qisk', '.cirq', '.qubit'],
  'application/x-neural': ['.neural', '.nn', '.dl'],
  'application/x-robotics': ['.robot', '.urdf', '.sdf', '.xacro'],
  'application/x-biotech': ['.bio', '.dna', '.rna', '.protein', '.genome'],
  'application/x-nano': ['.nano'],
  'application/x-space': ['.space', '.satellite', '.tle'],
  'application/x-renewable': ['.renewable', '.grid'],
  'application/x-autonomous': ['.autonomous', '.vehicle'],
  'application/x-telecom': ['.telecom', '.5g', '.6g'],
  'application/x-security': ['.security', '.encrypt'],
  'application/x-digital-twin': ['.digital', '.twin', '.sim'],

  // Archive formats
  'application/zip': ['.zip'],
  'application/x-tar': ['.tar', '.tar.gz', '.tgz'],
  'application/x-rar-compressed': ['.rar'],
  'application/x-7z-compressed': ['.7z']
};

const getFileIcon = (file?: File) => {
  const name = file?.name ? String(file.name) : "";
  const ext = name ? name.toLowerCase().split('.').pop() : "";

  if (file?.type?.startsWith('image/') || ['.psd'].includes(`.${ext}`)) return Image;
  if (file?.type?.startsWith('video/')) return Video;
  if (file?.type?.startsWith('audio/')) return Music;
  if (file?.type === 'application/pdf' || ext === 'pdf') return FileText;

  // Medical/Scientific
  if (['.dcm', '.dicom', '.fits', '.fit', '.fts', '.h5', '.hdf5', '.he5', '.nc', '.netcdf', '.nc4'].includes(`.${ext}`)) {
    return FileText; // Could use a specialized icon
  }

  // Emerging tech
  if (['.ai', '.ml', '.model', '.blockchain', '.ar', '.vr', '.iot', '.quantum', '.neural', '.robot', '.bio', '.nano', '.space'].includes(`.${ext}`)) {
    return Zap; // Tech icon for emerging formats
  }

  // Documents
  if (['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.html', '.xml', '.json'].includes(`.${ext}`)) {
    return FileText;
  }

  return File;
};

const getFileTypeColor = (file?: File) => {
  const name = file?.name ? String(file.name) : "";
  const ext = name ? name.toLowerCase().split('.').pop() : "";

  if (file?.type?.startsWith('image/') || ['.psd'].includes(`.${ext}`)) return 'bg-blue-500/10 text-blue-600 border-blue-200';
  if (file?.type?.startsWith('video/')) return 'bg-purple-500/10 text-purple-600 border-purple-200';
  if (file?.type?.startsWith('audio/')) return 'bg-green-500/10 text-green-600 border-green-200';
  if (file?.type === 'application/pdf' || ext === 'pdf') return 'bg-red-500/10 text-red-600 border-red-200';

  // Medical/Scientific - cyan
  if (['.dcm', '.dicom', '.fits', '.fit', '.fts', '.h5', '.hdf5', '.he5', '.nc', '.netcdf', '.nc4', '.shp'].includes(`.${ext}`)) {
    return 'bg-cyan-500/10 text-cyan-600 border-cyan-200';
  }

  // Emerging tech - orange
  if (['.ai', '.ml', '.model', '.blockchain', '.ar', '.vr', '.iot', '.quantum', '.neural', '.robot', '.bio', '.nano', '.space', '.renewable', '.autonomous', '.telecom', '.security', '.digital', '.twin'].includes(`.${ext}`)) {
    return 'bg-orange-500/10 text-orange-600 border-orange-200';
  }

  // Documents - indigo
  if (['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.html', '.xml', '.json', '.csv'].includes(`.${ext}`)) {
    return 'bg-indigo-500/10 text-indigo-600 border-indigo-200';
  }

  return 'bg-gray-500/10 text-gray-600 border-gray-200';
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

export function EnhancedUploadZone({
  onResults,
  tier,
  maxFiles = 10,
  className,
  advanced = false
}: EnhancedUploadZoneProps) {
  const [files, setFiles] = useState<FileState[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const { toast } = useToast();
  const abortControllerRef = useRef<AbortController | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      errors.forEach((error: any) => {
        toast({
          title: "File rejected",
          description: `${file.name}: ${error.message}`,
          variant: "destructive"
        });
      });
    });

    // Add accepted files with analysis and estimates
    const newFilesPromises = acceptedFiles.map(async (file) => {
      // Run analysis and estimation in parallel
      const [analysis, estimate] = await Promise.all([
        analyzeFile(file),
        Promise.resolve(estimateProcessingTime(file, tier as any)) // Sync but wrapped for consistency
      ]);

      return {
        file,
        id: crypto.randomUUID(),
        status: 'pending' as const,
        progress: 0,
        preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
        analysis,
        estimate
      };
    });

    const newFiles = await Promise.all(newFilesPromises);
    setFiles(prev => [...prev, ...newFiles].slice(0, maxFiles));
  }, [maxFiles, toast, tier]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles,
    maxSize:
      tier === 'enterprise' || tier === 'super'
        ? 2000 * 1024 * 1024
        : tier === 'forensic' || tier === 'premium'
          ? 500 * 1024 * 1024
          : tier === 'professional' || tier === 'starter'
            ? 100 * 1024 * 1024
            : 10 * 1024 * 1024,
    onDragEnter: () => setDragActive(true),
    onDragLeave: () => setDragActive(false),
    onDropAccepted: () => setDragActive(false),
    onDropRejected: () => setDragActive(false)
  });

  const removeFile = (fileId: string) => {
    setFiles(prev => {
      const fileState = prev.find(f => f.id === fileId);
      if (fileState?.preview) {
        URL.revokeObjectURL(fileState.preview);
      }
      return prev.filter(f => f.id !== fileId);
    });
  };

  const processFiles = async () => {
    if (files.length === 0) return;

    setIsProcessing(true);
    abortControllerRef.current = new AbortController();

    try {
      const results = [];

      if (files.length === 1) {
        // Single file processing
        const fileState = files[0];
        setFiles(prev => prev.map(f => f.id === fileState.id ? { ...f, status: 'uploading', progress: 0 } : f));

        const formData = new FormData();
        formData.append('file', fileState.file);

        const endpoint = advanced ? '/api/extract/advanced' : '/api/extract';
        const response = await fetch(`${endpoint}?tier=${tier}`, {
          method: 'POST',
          body: formData,
          signal: abortControllerRef.current.signal
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        setFiles(prev => prev.map(f => f.id === fileState.id ? { ...f, status: 'processing', progress: 50 } : f));

        const result = await response.json();

        setFiles(prev => prev.map(f => f.id === fileState.id ? {
          ...f,
          status: 'complete',
          progress: 100,
          result
        } : f));

        results.push(result);

      } else {
        // Batch processing
        const formData = new FormData();
        files.forEach(fileState => {
          formData.append('files', fileState.file);
        });

        setFiles(prev => prev.map(f => ({ ...f, status: 'uploading', progress: 0 })));

        const response = await fetch(`/api/extract/batch?tier=${tier}`, {
          method: 'POST',
          body: formData,
          signal: abortControllerRef.current.signal
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        setFiles(prev => prev.map(f => ({ ...f, status: 'processing', progress: 50 })));

        const batchResult = await response.json();

        // Update individual file statuses
        setFiles(prev => prev.map(fileState => {
          const result = batchResult.results[fileState.file.name];
          return {
            ...fileState,
            status: result ? 'complete' : 'error',
            progress: 100,
            result,
            error: result ? undefined : 'Processing failed'
          };
        }));

        results.push(...Object.values(batchResult.results));
      }

      onResults(results);

      toast({
        title: "Processing complete",
        description: `Successfully processed ${results.length} file${results.length > 1 ? 's' : ''}`,
      });

    } catch (error) {
      console.error('Processing error:', error);

      setFiles(prev => prev.map(f => ({
        ...f,
        status: 'error',
        progress: 0,
        error: error instanceof Error ? error.message : 'Processing failed'
      })));

      toast({
        title: "Processing failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
      abortControllerRef.current = null;
    }
  };

  const cancelProcessing = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsProcessing(false);
      setFiles(prev => prev.map(f => ({ ...f, status: 'pending', progress: 0 })));
      toast({
        title: "Processing cancelled",
        description: "File processing has been cancelled"
      });
    }
  };

  const clearAll = () => {
    files.forEach(fileState => {
      if (fileState.preview) {
        URL.revokeObjectURL(fileState.preview);
      }
    });
    setFiles([]);
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* Drop Zone */}
      <Card className={cn(
        "border-2 border-dashed transition-all duration-200",
        dragActive || isDragActive
          ? "border-primary bg-primary/5 scale-[1.02]"
          : "border-muted-foreground/25 hover:border-muted-foreground/50"
      )}>
        <CardContent className="p-8">
          <div
            {...getRootProps()}
            className="text-center cursor-pointer"
            role="button"
            aria-label="Upload files for metadata extraction"
            tabIndex={0}
          >
            <input {...getInputProps()} />

            <motion.div
              animate={{
                scale: dragActive ? 1.1 : 1,
                rotate: dragActive ? 5 : 0
              }}
              className="mx-auto mb-4 w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center"
              aria-hidden="true"
            >
              <Upload className={cn(
                "w-8 h-8 transition-colors",
                dragActive ? "text-primary" : "text-muted-foreground"
              )} />
            </motion.div>

            <h3 className="text-lg font-semibold mb-2">
              {dragActive ? "Drop files here" : "Upload files for analysis"}
            </h3>

            <p className="text-muted-foreground mb-4">
              Drag & drop files or click to browse • Supports 500+ file formats
            </p>

            <div className="flex flex-wrap justify-center gap-2 mb-4">
              <Badge variant="outline" className="text-xs">Images</Badge>
              <Badge variant="outline" className="text-xs">Video</Badge>
              <Badge variant="outline" className="text-xs">Audio</Badge>
              <Badge variant="outline" className="text-xs">Documents</Badge>
              <Badge variant="outline" className="text-xs">Medical</Badge>
              <Badge variant="outline" className="text-xs">Scientific</Badge>
              <Badge variant="outline" className="text-xs">AI/ML</Badge>
              <Badge variant="outline" className="text-xs">Blockchain</Badge>
              <Badge variant="outline" className="text-xs">AR/VR</Badge>
              <Badge variant="outline" className="text-xs">IoT</Badge>
              <Badge variant="outline" className="text-xs">+More</Badge>
            </div>

            <p className="text-xs text-muted-foreground">
              Max {maxFiles} files • Up to {
                tier === 'enterprise' || tier === 'super' ? '2GB' :
                  tier === 'forensic' || tier === 'premium' ? '500MB' :
                    tier === 'professional' || tier === 'starter' ? '100MB' : '10MB'
              } per file
            </p>
          </div>
        </CardContent>
      </Card>

      {/* File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between">
              <h4 className="font-medium">Files ({files.length})</h4>
              <div className="flex gap-2">
                {!isProcessing && files.length > 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearAll}
                    aria-label="Clear all files from upload list"
                  >
                    Clear All
                  </Button>
                )}
                {isProcessing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={cancelProcessing}
                    aria-label="Cancel file processing"
                  >
                    Cancel
                  </Button>
                )}
              </div>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto">
              {files.map((fileState) => {
                const FileTypeIcon = getFileIcon(fileState.file);

                return (
                  <motion.div
                    key={fileState.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="flex items-center gap-3 p-3 border rounded-lg bg-card"
                  >
                    {/* File Icon/Preview */}
                    <div className="flex-shrink-0">
                      {fileState.preview ? (
                        <img
                          src={fileState.preview}
                          alt={fileState.file.name}
                          className="w-10 h-10 object-cover rounded"
                        />
                      ) : (
                        <div className={cn(
                          "w-10 h-10 rounded flex items-center justify-center border",
                          getFileTypeColor(fileState.file)
                        )}>
                          <FileTypeIcon className="w-5 h-5" />
                        </div>
                      )}
                    </div>

                    {/* File Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="font-medium truncate">{fileState.file.name}</p>
                        <Badge variant="outline" className="text-xs">
                          {formatFileSize(fileState.file.size)}
                        </Badge>
                        {fileState.estimate && fileState.status === 'pending' && (
                          <Badge variant="secondary" className="text-xs flex items-center gap-1">
                            <Timer className="w-3 h-3" />
                            {fileState.estimate.displayText}
                          </Badge>
                        )}
                      </div>

                      {/* Progress Bar */}
                      <div className="mt-2">
                        <Progress value={fileState.progress} className="h-1" />
                        <div className="flex items-center gap-2 mt-1">
                          {fileState.status === 'pending' && (
                            <>
                              <Clock className="w-3 h-3 text-slate-400" />
                              <span className="text-xs text-muted-foreground">Ready</span>
                            </>
                          )}
                          {fileState.status === 'uploading' && (
                            <>
                              <Upload className="w-3 h-3 text-blue-500" />
                              <span className="text-xs text-muted-foreground">Uploading...</span>
                            </>
                          )}
                          {fileState.status === 'processing' && (
                            <>
                              <Loader2 className="w-3 h-3 text-yellow-500 animate-spin" />
                              <span className="text-xs text-muted-foreground">Processing...</span>
                            </>
                          )}
                          {fileState.status === 'complete' && (
                            <>
                              <CheckCircle2 className="w-3 h-3 text-green-500" />
                              <span className="text-xs text-green-600">Complete</span>
                            </>
                          )}
                          {fileState.status === 'error' && (
                            <>
                              <AlertCircle className="w-3 h-3 text-red-500" />
                              <span className="text-xs text-red-600">{fileState.error || 'Error'}</span>
                            </>
                          )}
                        </div>
                      </div>

                      {/* File Analysis Warnings/Suggestions */}
                      {fileState.analysis && (fileState.analysis.warnings.length > 0 || fileState.analysis.suggestions.length > 0) && (
                        <div className="mt-3 space-y-2">
                          {fileState.analysis.warnings.map((warning, idx) => (
                            <Alert key={`warn-${idx}`} variant="destructive" className="py-2">
                              <AlertDescription className="text-xs">
                                {warning}
                              </AlertDescription>
                            </Alert>
                          ))}
                          {fileState.analysis.suggestions.map((suggestion, idx) => (
                            <Alert key={`sug-${idx}`} className="py-2 border-blue-200 bg-blue-50 dark:bg-blue-950/20">
                              <AlertDescription className="text-xs text-blue-900 dark:text-blue-100">
                                {suggestion}
                              </AlertDescription>
                            </Alert>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex-shrink-0">
                      {!isProcessing && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(fileState.id)}
                          className="h-8 w-8 p-0"
                          aria-label={`Remove ${fileState.file.name}`}
                        >
                          <X className="w-4 h-4" aria-hidden="true" />
                        </Button>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Process Button */}
            {files.length > 0 && !isProcessing && files.some(f => f.status === 'pending') && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="pt-4"
              >
                <Button
                  onClick={processFiles}
                  className="w-full"
                  size="lg"
                  aria-label={`Extract metadata from ${files.filter(f => f.status === 'pending').length} files`}
                >
                  <Zap className="w-4 h-4 mr-2" aria-hidden="true" />
                  Extract Metadata ({files.filter(f => f.status === 'pending').length} files)
                </Button>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
