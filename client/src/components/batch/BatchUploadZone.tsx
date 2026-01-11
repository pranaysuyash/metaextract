import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  AlertTriangle,
  FileImage,
  FileSpreadsheet,
  Database,
  Clock,
} from 'lucide-react';
import { formatFileSize } from '@/lib/utils';
import { useAuth } from '@/lib/auth';
import { getTierConfig } from '@shared/tierConfig';

interface BatchUploadZoneProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUpload: (files: File[]) => void;
  isUploading: boolean;
}

interface FileWithValidation {
  file: File;
  status: 'valid' | 'invalid' | 'duplicate';
  error?: string;
  id: string;
}

export const BatchUploadZone: React.FC<BatchUploadZoneProps> = ({
  open,
  onOpenChange,
  onUpload,
  isUploading,
}) => {
  const { user } = useAuth();
  const [files, setFiles] = useState<FileWithValidation[]>([]);
  const [isValidating, setIsValidating] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // Get tier configuration for current user
  const tierConfig = React.useMemo(() => {
    if (!user?.tier) return getTierConfig('free');
    return getTierConfig(user.tier);
  }, [user]);

  const validateFiles = useCallback((newFiles: File[]): FileWithValidation[] => {
    const errors: string[] = [];
    const seenNames = new Set<string>();
    
    const validatedFiles = newFiles.map(file => {
      // Check for duplicate filenames
      if (seenNames.has(file.name)) {
        return {
          file,
          status: 'duplicate' as const,
          error: 'Duplicate filename',
          id: `${file.name}-${Date.now()}-${Math.random()}`,
        };
      }
      seenNames.add(file.name);

      // Check file type
      const isAllowedType = tierConfig.allowedFileTypes.some(allowedType =>
        file.type.startsWith(allowedType) || file.name.toLowerCase().endsWith(allowedType)
      );

      if (!isAllowedType) {
        errors.push(`${file.name}: File type not supported`);
        return {
          file,
          status: 'invalid' as const,
          error: 'File type not supported for your tier',
          id: `${file.name}-${Date.now()}-${Math.random()}`,
        };
      }

      // Check file size
      const maxSizeBytes = tierConfig.maxFileSizeMB * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        errors.push(`${file.name}: File too large (${formatFileSize(file.size)} > ${formatFileSize(maxSizeBytes)})`);
        return {
          file,
          status: 'invalid' as const,
          error: `File too large (max ${tierConfig.maxFileSizeMB}MB)`,
          id: `${file.name}-${Date.now()}-${Math.random()}`,
        };
      }

      return {
        file,
        status: 'valid' as const,
        id: `${file.name}-${Date.now()}-${Math.random()}`,
      };
    });

    setValidationErrors(errors);
    return validatedFiles;
  }, [tierConfig]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setIsValidating(true);
    
    // Simulate validation delay for better UX
    setTimeout(() => {
      const validatedFiles = validateFiles(acceptedFiles);
      setFiles(prev => [...prev, ...validatedFiles]);
      setIsValidating(false);
    }, 500);
  }, [validateFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled: isUploading || isValidating,
  });

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  const clearFiles = () => {
    setFiles([]);
    setValidationErrors([]);
  };

  const handleUpload = () => {
    const validFiles = files.filter(f => f.status === 'valid').map(f => f.file);
    if (validFiles.length > 0) {
      onUpload(validFiles);
    }
  };

  const getFileIcon = (fileName: string, fileType: string) => {
    if (fileType.startsWith('image/')) return <FileImage className="w-4 h-4 text-blue-500" />;
    if (fileType.includes('pdf')) return <FileSpreadsheet className="w-4 h-4 text-red-500" />;
    if (fileType.includes('dicom')) return <Database className="w-4 h-4 text-purple-500" />;
    return <FileText className="w-4 h-4 text-slate-500" />;
  };

  const validFiles = files.filter(f => f.status === 'valid');
  const invalidFiles = files.filter(f => f.status === 'invalid');
  const duplicateFiles = files.filter(f => f.status === 'duplicate');

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Batch File Upload
          </DialogTitle>
          <DialogDescription>
            Upload multiple files for batch metadata extraction
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-4">
          {/* Upload Zone */}
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
              transition-all duration-200
              ${isDragActive 
                ? 'border-primary bg-primary/10' 
                : 'border-slate-600 hover:border-slate-500'
              }
              ${isUploading || isValidating ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <input {...getInputProps()} multiple />
            <Upload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
            <p className="text-white font-medium mb-2">
              {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-slate-400 text-sm">
              or click to select files from your computer
            </p>
            <div className="mt-4 text-xs text-slate-500">
              <p>Supported formats: {tierConfig.allowedFileTypes.join(', ')}</p>
              <p>Max file size: {tierConfig.maxFileSizeMB}MB per file</p>
              <p>Max files per batch: {tierConfig.monthlyFileLimit || 'Unlimited'}</p>
            </div>
          </div>

          {/* Validation Status */}
          {isValidating && (
            <div className="flex items-center justify-center gap-2 p-4 bg-muted/20 rounded-lg">
              <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              <span className="text-slate-300">Validating files...</span>
            </div>
          )}

          {/* Validation Errors */}
          {validationErrors.length > 0 && (
            <Alert variant="destructive">
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription>
                <div className="space-y-1">
                  {validationErrors.map((error, index) => (
                    <p key={index} className="text-sm">{error}</p>
                  ))}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* File Lists */}
          {files.length > 0 && (
            <div className="space-y-4">
              {/* Valid Files */}
              {validFiles.length > 0 && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-white flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-emerald-500" />
                      Valid Files ({validFiles.length})
                    </h4>
                    <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400">
                      Ready to upload
                    </Badge>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {validFiles.map(({ file, id }) => (
                      <div key={id} className="flex items-center gap-3 p-3 bg-muted/20 rounded-lg">
                        {getFileIcon(file.name, file.type)}
                        <div className="flex-1 min-w-0">
                          <p className="text-white text-sm font-medium truncate">{file.name}</p>
                          <p className="text-slate-400 text-xs">
                            {formatFileSize(file.size)} • {file.type || 'Unknown type'}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(id)}
                          className="h-6 w-6 p-0 text-slate-400 hover:text-white"
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Invalid Files */}
              {invalidFiles.length > 0 && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-white flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                      Invalid Files ({invalidFiles.length})
                    </h4>
                    <Badge variant="secondary" className="bg-red-500/20 text-red-400">
                      Will be skipped
                    </Badge>
                  </div>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {invalidFiles.map(({ file, error, id }) => (
                      <div key={id} className="flex items-center gap-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        {getFileIcon(file.name, file.type)}
                        <div className="flex-1 min-w-0">
                          <p className="text-white text-sm font-medium truncate">{file.name}</p>
                          <p className="text-red-400 text-xs">{error}</p>
                          <p className="text-slate-400 text-xs">
                            {formatFileSize(file.size)} • {file.type || 'Unknown type'}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(id)}
                          className="h-6 w-6 p-0 text-slate-400 hover:text-white"
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Duplicate Files */}
              {duplicateFiles.length > 0 && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-white flex items-center gap-2">
                      <Clock className="w-4 h-4 text-yellow-500" />
                      Duplicate Files ({duplicateFiles.length})
                    </h4>
                    <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-400">
                      Will be skipped
                    </Badge>
                  </div>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {duplicateFiles.map(({ file, id }) => (
                      <div key={id} className="flex items-center gap-3 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                        {getFileIcon(file.name, file.type)}
                        <div className="flex-1 min-w-0">
                          <p className="text-white text-sm font-medium truncate">{file.name}</p>
                          <p className="text-yellow-400 text-xs">Duplicate filename</p>
                          <p className="text-slate-400 text-xs">
                            {formatFileSize(file.size)} • {file.type || 'Unknown type'}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(id)}
                          className="h-6 w-6 p-0 text-slate-400 hover:text-white"
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          <div className="flex items-center gap-2">
            {files.length > 0 && (
              <Button
                variant="outline"
                onClick={clearFiles}
                disabled={isUploading}
                size="sm"
              >
                Clear All
              </Button>
            )}
            <div className="text-sm text-slate-400">
              {validFiles.length} valid files • {invalidFiles.length + duplicateFiles.length} skipped
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isUploading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={validFiles.length === 0 || isUploading}
              className="gap-2"
            >
              {isUploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Upload {validFiles.length} Files
                </>
              )}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
