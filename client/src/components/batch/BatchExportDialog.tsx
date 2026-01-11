import React, { useState } from 'react';
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
import { useToast } from '@/hooks/use-toast';
import { FileJson, FileSpreadsheet, Download, Loader2 } from 'lucide-react';

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

interface BatchExportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  results: BatchResult[];
  selectedFiles: string[];
}

export const BatchExportDialog: React.FC<BatchExportDialogProps> = ({
  open,
  onOpenChange,
  results,
  selectedFiles,
}) => {
  const { toast } = useToast();
  const [exportFormat, setExportFormat] = useState<'json' | 'csv'>('json');
  const [isExporting, setIsExporting] = useState(false);
  const [exportScope, setExportScope] = useState<'all' | 'selected'>('all');

  const handleExport = async () => {
    setIsExporting(true);
    
    try {
      const dataToExport = exportScope === 'selected' && selectedFiles.length > 0
        ? results.filter(result => selectedFiles.includes(result.id))
        : results;

      if (exportFormat === 'json') {
        // Export as JSON
        const jsonString = JSON.stringify(dataToExport, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `batch-results-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } else {
        // Export as CSV
        const headers = ['Filename', 'Status', 'Fields Extracted', 'File Size (KB)', 'File Type', 'Extraction Date', 'Processing Time (ms)'];
        const csvContent = [
          headers.join(','),
          ...dataToExport.map(result => [
            `"${result.filename}"`,
            result.status,
            result.fieldsExtracted,
            Math.round(result.fileSize / 1024),
            `"${result.fileType}"`,
            `"${new Date(result.extractionDate).toISOString()}"`,
            result.processingTime || ''
          ].join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `batch-results-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }

      toast({
        title: 'Export Complete',
        description: `${dataToExport.length} results exported as ${exportFormat.toUpperCase()}`,
      });
      
      onOpenChange(false);
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: 'Export Failed',
        description: 'An error occurred while exporting the results.',
        variant: 'destructive',
      });
    } finally {
      setIsExporting(false);
    }
  };

  const exportableCount = exportScope === 'selected' && selectedFiles.length > 0 
    ? selectedFiles.length 
    : results.length;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export Batch Results</DialogTitle>
          <DialogDescription>
            Choose the format and scope for exporting your batch processing results.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Export Scope */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Export Scope</label>
            <div className="flex gap-2">
              <Button
                variant={exportScope === 'all' ? 'default' : 'outline'}
                onClick={() => setExportScope('all')}
                className="flex-1"
              >
                All Results ({results.length})
              </Button>
              <Button
                variant={exportScope === 'selected' ? 'default' : 'outline'}
                onClick={() => setExportScope('selected')}
                className="flex-1"
                disabled={selectedFiles.length === 0}
              >
                Selected ({selectedFiles.length})
              </Button>
            </div>
          </div>

          {/* Export Format */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Export Format</label>
            <div className="flex gap-2">
              <Button
                variant={exportFormat === 'json' ? 'default' : 'outline'}
                onClick={() => setExportFormat('json')}
                className="flex-1 gap-2"
              >
                <FileJson className="w-4 h-4" />
                JSON
              </Button>
              <Button
                variant={exportFormat === 'csv' ? 'default' : 'outline'}
                onClick={() => setExportFormat('csv')}
                className="flex-1 gap-2"
              >
                <FileSpreadsheet className="w-4 h-4" />
                CSV
              </Button>
            </div>
          </div>

          {/* Export Preview */}
          <div className="rounded-lg border bg-muted/20 p-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Files to export:</span>
              <Badge variant="secondary">{exportableCount}</Badge>
            </div>
            <div className="mt-2 text-slate-400">
              Format: <span className="text-white">{exportFormat.toUpperCase()}</span>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isExporting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleExport}
            disabled={isExporting || exportableCount === 0}
            className="gap-2"
          >
            {isExporting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            {isExporting ? 'Exporting...' : 'Export'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
