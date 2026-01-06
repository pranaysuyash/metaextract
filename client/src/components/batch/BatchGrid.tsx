import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Camera, 
  FileImage,
  File,
  Database,
  Eye,
  Hash
} from 'lucide-react';
import { formatFileSize, getFileIcon } from '@/lib/utils';

interface BatchResult {
  id: string;
  filename: string;
  status: 'success' | 'error' | 'processing';
  extractionDate: string;
  fieldsExtracted: number;
  fileSize: number;
  fileType: string;
  authenticityScore?: number;
  metadata: Record<string, any>;
}

interface BatchGridProps {
  results: BatchResult[];
  selectedFiles: string[];
  onSelectFile: (id: string) => void;
  onSelectAll: () => void;
  allSelected: boolean;
}

export const BatchGrid: React.FC<BatchGridProps> = ({
  results,
  selectedFiles,
  onSelectFile,
  onSelectAll,
  allSelected
}) => {
  const getStatusIcon = (status: BatchResult['status']) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'processing': return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default: return null;
    }
  };

  const getStatusBadge = (status: BatchResult['status']) => {
    switch (status) {
      case 'success': 
        return <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">Success</Badge>;
      case 'error': 
        return <Badge variant="secondary" className="bg-red-500/20 text-red-400 border-red-500/30">Error</Badge>;
      case 'processing': 
        return <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">Processing</Badge>;
      default: 
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getFileTypeIcon = (fileType: string) => {
    if (fileType.includes('image')) return <FileImage className="w-4 h-4 text-blue-500" />;
    if (fileType.includes('pdf')) return <FileText className="w-4 h-4 text-red-500" />;
    if (fileType.includes('dicom')) return <Database className="w-4 h-4 text-purple-500" />;
    return <File className="w-4 h-4 text-slate-500" />;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg">
        <Checkbox
          checked={allSelected}
          onCheckedChange={onSelectAll}
          className="data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
        />
        <span className="text-sm font-medium text-white">Select All</span>
        <span className="text-sm text-slate-300">({selectedFiles.length} of {results.length} selected)</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {results.map((result) => (
          <Card 
            key={result.id} 
            className={`bg-card border-white/10 hover:bg-muted/20 transition-colors ${
              selectedFiles.includes(result.id) ? 'ring-2 ring-primary/50' : ''
            }`}
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Checkbox
                  checked={selectedFiles.includes(result.id)}
                  onCheckedChange={() => onSelectFile(result.id)}
                  className="mt-1 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
                />
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {getFileTypeIcon(result.fileType)}
                      <h3 className="font-medium text-white truncate max-w-[160px]">{result.filename}</h3>
                    </div>
                    {getStatusIcon(result.status)}
                  </div>
                  
                  <div className="mt-3 space-y-2">
                    <div className="flex items-center gap-2 text-xs text-slate-300">
                      <span>{result.fileType.split('/')[1]?.toUpperCase() || result.fileType}</span>
                      <span>•</span>
                      <span>{formatFileSize(result.fileSize)}</span>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-300">Fields:</span>
                      <span className="text-sm font-medium text-white">{result.fieldsExtracted}</span>
                    </div>
                    
                    {result.authenticityScore !== undefined && (
                      <div className="flex items-center gap-2">
                        <Eye className="w-3 h-3 text-primary" />
                        <span className="text-xs text-slate-300">Authenticity:</span>
                        <span className="text-sm font-medium text-white">{result.authenticityScore}%</span>
                      </div>
                    )}
                    
                    <div className="text-xs text-slate-300 mt-2">
                      {new Date(result.extractionDate).toLocaleString()}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-3 pt-3 border-t border-white/10">
                {getStatusBadge(result.status)}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {results.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No batch results to display</p>
          <p className="text-sm mt-1">Upload multiple files to see batch processing results</p>
        </div>
      )}
    </div>
  );
};