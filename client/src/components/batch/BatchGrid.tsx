import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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
  Hash,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Download,
  MoreVertical,
  Clock,
  RefreshCw
} from 'lucide-react';
import { formatFileSize } from '@/lib/utils';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface BatchResult {
  id: string;
  filename: string;
  status: 'success' | 'error' | 'processing' | 'pending';
  extractionDate: string;
  fieldsExtracted: number;
  fileSize: number;
  fileType: string;
  authenticityScore?: number;
  metadata: Record<string, any>;
  processingTime?: number;
  errorMessage?: string;
  batchId?: string;
}

interface BatchGridProps {
  results: BatchResult[];
  selectedFiles: string[];
  onSelectFile: (id: string) => void;
  onSelectAll: () => void;
  allSelected: boolean;
  viewMode: 'grid' | 'list';
  sortBy?: 'filename' | 'date' | 'fields' | 'size' | 'status';
  sortOrder?: 'asc' | 'desc';
  onSortChange?: (field: 'filename' | 'date' | 'fields' | 'size' | 'status', order: 'asc' | 'desc') => void;
  onFileAction?: (action: 'download' | 'view' | 'reprocess', fileId: string) => void;
}

export const BatchGrid: React.FC<BatchGridProps> = ({
  results,
  selectedFiles,
  onSelectFile,
  onSelectAll,
  allSelected,
  viewMode,
  sortBy = 'date',
  sortOrder = 'desc',
  onSortChange,
  onFileAction
}) => {
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());

  const getStatusIcon = (status: BatchResult['status']) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'processing': return <RefreshCw className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'pending': return <Clock className="w-4 h-4 text-blue-500" />;
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
        return <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30 animate-pulse">Processing</Badge>;
      case 'pending': 
        return <Badge variant="secondary" className="bg-blue-500/20 text-blue-400 border-blue-500/30">Pending</Badge>;
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

  const toggleExpanded = (id: string) => {
    setExpandedCards((prev: Set<string>) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const getSortIcon = (field: string) => {
    if (sortBy !== field) return <ArrowUpDown className="w-4 h-4" />;
    return sortOrder === 'asc' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />;
  };

  const handleSort = (field: 'filename' | 'date' | 'fields' | 'size' | 'status') => {
    if (!onSortChange) return;
    
    if (sortBy === field) {
      onSortChange(field, sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      onSortChange(field, 'asc');
    }
  };

  const renderGridView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {results.map((result) => {
        const isExpanded = expandedCards.has(result.id);
        
        return (
          <Card 
            key={result.id} 
            className={`bg-card border-white/10 hover:bg-muted/20 transition-all duration-200 ${
              selectedFiles.includes(result.id) ? 'ring-2 ring-primary/50 shadow-lg' : ''
            } ${result.status === 'processing' ? 'animate-pulse' : ''}`}
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Checkbox
                  checked={selectedFiles.includes(result.id)}
                  onCheckedChange={() => onSelectFile(result.id)}
                  className="mt-1 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
                />
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      {getFileTypeIcon(result.fileType)}
                      <h3 className="font-medium text-white truncate" title={result.filename}>
                        {result.filename}
                      </h3>
                    </div>
                    <div className="flex items-center gap-1">
                      {getStatusIcon(result.status)}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <MoreVertical className="w-3 h-3" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => onFileAction?.('view', result.id)}>
                            <Eye className="w-4 h-4 mr-2" />
                            View Details
                          </DropdownMenuItem>
                          {result.status === 'success' && (
                            <DropdownMenuItem onClick={() => onFileAction?.('download', result.id)}>
                              <Download className="w-4 h-4 mr-2" />
                              Download Metadata
                            </DropdownMenuItem>
                          )}
                          {result.status === 'error' && (
                            <DropdownMenuItem onClick={() => onFileAction?.('reprocess', result.id)}>
                              <RefreshCw className="w-4 h-4 mr-2" />
                              Reprocess File
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-slate-300">
                      <span>{result.fileType.split('/')[1]?.toUpperCase() || result.fileType}</span>
                      <span>•</span>
                      <span>{formatFileSize(result.fileSize)}</span>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Hash className="w-3 h-3 text-slate-400" />
                        <span className="text-xs text-slate-300">Fields:</span>
                        <span className="text-sm font-medium text-white">{result.fieldsExtracted}</span>
                      </div>
                      {result.processingTime && (
                        <div className="flex items-center gap-1 text-xs text-slate-400">
                          <Clock className="w-3 h-3" />
                          {Math.round(result.processingTime / 1000)}s
                        </div>
                      )}
                    </div>
                    
                    {result.authenticityScore !== undefined && (
                      <div className="flex items-center gap-2">
                        <Eye className="w-3 h-3 text-primary" />
                        <span className="text-xs text-slate-300">Authenticity:</span>
                        <Badge 
                          variant="secondary" 
                          className={`text-xs ${
                            result.authenticityScore >= 80 
                              ? 'bg-emerald-500/20 text-emerald-400' 
                              : result.authenticityScore >= 50 
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-red-500/20 text-red-400'
                          }`}
                        >
                          {result.authenticityScore}%
                        </Badge>
                      </div>
                    )}
                    
                    {result.errorMessage && (
                      <div className="p-2 bg-red-500/10 border border-red-500/20 rounded text-xs text-red-400">
                        {result.errorMessage}
                      </div>
                    )}
                    
                    <div className="text-xs text-slate-400">
                      {new Date(result.extractionDate).toLocaleString()}
                    </div>
                  </div>
                  
                  {isExpanded && (
                    <div className="mt-3 pt-3 border-t border-white/10 space-y-2">
                      <div className="text-xs">
                        <span className="text-slate-400">File ID:</span>
                        <span className="text-white font-mono ml-2">{result.id.slice(0, 8)}...</span>
                      </div>
                      {Object.entries(result.metadata).slice(0, 3).map(([key, value]) => (
                        <div key={key} className="text-xs">
                          <span className="text-slate-400 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="text-white ml-2 truncate">{String(value)}</span>
                        </div>
                      ))}
                      {Object.keys(result.metadata).length > 3 && (
                        <div className="text-xs text-slate-400">
                          +{Object.keys(result.metadata).length - 3} more fields
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between">
                {getStatusBadge(result.status)}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleExpanded(result.id)}
                  className="h-6 text-xs text-slate-400 hover:text-white"
                >
                  {isExpanded ? 'Show Less' : 'Show More'}
                </Button>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );

  const renderListView = () => (
    <div className="space-y-2">
      {/* List Header */}
      <div className="grid grid-cols-12 gap-4 p-3 bg-muted/30 rounded-lg text-sm font-medium text-slate-300">
        <div className="col-span-1">
          <Checkbox
            checked={allSelected}
            onCheckedChange={onSelectAll}
            className="data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
          />
        </div>
        <div className="col-span-4 flex items-center gap-2 cursor-pointer hover:text-white" onClick={() => handleSort('filename')}>
          File
          {getSortIcon('filename')}
        </div>
        <div className="col-span-1 flex items-center gap-2 cursor-pointer hover:text-white" onClick={() => handleSort('status')}>
          Status
          {getSortIcon('status')}
        </div>
        <div className="col-span-1 flex items-center gap-2 cursor-pointer hover:text-white" onClick={() => handleSort('fields')}>
          Fields
          {getSortIcon('fields')}
        </div>
        <div className="col-span-1 flex items-center gap-2 cursor-pointer hover:text-white" onClick={() => handleSort('size')}>
          Size
          {getSortIcon('size')}
        </div>
        <div className="col-span-2 flex items-center gap-2 cursor-pointer hover:text-white" onClick={() => handleSort('date')}>
          Date
          {getSortIcon('date')}
        </div>
        <div className="col-span-2">Authenticity</div>
        <div className="col-span-1">Actions</div>
      </div>

      {/* List Items */}
      {results.map((result) => (
        <div
          key={result.id}
          className={`grid grid-cols-12 gap-4 p-3 bg-card border border-white/10 rounded-lg hover:bg-muted/20 transition-colors ${
            selectedFiles.includes(result.id) ? 'ring-2 ring-primary/50' : ''
          } ${result.status === 'processing' ? 'animate-pulse' : ''}`}
        >
          <div className="col-span-1 flex items-center">
            <Checkbox
              checked={selectedFiles.includes(result.id)}
              onCheckedChange={() => onSelectFile(result.id)}
              className="data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
            />
          </div>
          
          <div className="col-span-4 flex items-center gap-3 min-w-0">
            {getFileTypeIcon(result.fileType)}
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate" title={result.filename}>
                {result.filename}
              </p>
              <p className="text-xs text-slate-400">
                {result.fileType} • {new Date(result.extractionDate).toLocaleDateString()}
              </p>
            </div>
          </div>
          
          <div className="col-span-1 flex items-center">
            {getStatusIcon(result.status)}
          </div>
          
          <div className="col-span-1 flex items-center">
            <div className="flex items-center gap-1">
              <Hash className="w-3 h-3 text-slate-400" />
              <span className="text-white">{result.fieldsExtracted}</span>
            </div>
          </div>
          
          <div className="col-span-1 flex items-center text-slate-300">
            {formatFileSize(result.fileSize)}
          </div>
          
          <div className="col-span-2 flex items-center text-slate-300 text-sm">
            <Clock className="w-3 h-3 mr-1" />
            {new Date(result.extractionDate).toLocaleString()}
          </div>
          
          <div className="col-span-2 flex items-center">
            {result.authenticityScore !== undefined ? (
              <Badge 
                variant="secondary" 
                className={`text-xs ${
                  result.authenticityScore >= 80 
                    ? 'bg-emerald-500/20 text-emerald-400' 
                    : result.authenticityScore >= 50 
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-red-500/20 text-red-400'
                }`}
              >
                {result.authenticityScore}%
              </Badge>
            ) : (
              <span className="text-slate-400 text-sm">N/A</span>
            )}
          </div>
          
          <div className="col-span-1 flex items-center">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                  <MoreVertical className="w-3 h-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onFileAction?.('view', result.id)}>
                  <Eye className="w-4 h-4 mr-2" />
                  View Details
                </DropdownMenuItem>
                {result.status === 'success' && (
                  <DropdownMenuItem onClick={() => onFileAction?.('download', result.id)}>
                    <Download className="w-4 h-4 mr-2" />
                    Download Metadata
                  </DropdownMenuItem>
                )}
                {result.status === 'error' && (
                  <DropdownMenuItem onClick={() => onFileAction?.('reprocess', result.id)}>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Reprocess File
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 p-3 bg-muted/30 rounded-lg flex-1">
          <Checkbox
            checked={allSelected}
            onCheckedChange={onSelectAll}
            className="data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground"
          />
          <span className="text-sm font-medium text-white">Select All</span>
          <span className="text-sm text-slate-300">
            ({selectedFiles.length} of {results.length} selected)
          </span>
          {results.length > 0 && (
            <Badge variant="secondary" className="ml-auto">
              {viewMode === 'grid' ? 'Grid View' : 'List View'}
            </Badge>
          )}
        </div>
      </div>

      {/* Results */}
      {viewMode === 'grid' ? renderGridView() : renderListView()}
      
      {results.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-white mb-2">No batch results to display</p>
          <p className="text-sm text-slate-300">
            {viewMode === 'grid' 
              ? 'Upload multiple files to see batch processing results in grid view'
              : 'Upload multiple files to see batch processing results in list view'
            }
          </p>
        </div>
      )}
    </div>
  );
};
