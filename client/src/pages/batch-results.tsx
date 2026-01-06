import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Upload, 
  Download, 
  FileText, 
  BarChart3, 
  FileJson, 
  FileSpreadsheet,
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  XCircle
} from 'lucide-react';
import { BatchGrid } from '@/components/batch/BatchGrid';
import { BatchStats } from '@/components/batch/BatchStats';
import { FileComparison } from '@/components/batch/FileComparison';

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

interface BatchResultsPageProps {
  batchId?: string;
}

export const BatchResultsPage: React.FC<BatchResultsPageProps> = ({ batchId }) => {
  const [batchResults, setBatchResults] = useState<BatchResult[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('grid');

  // Mock data for demonstration
  useEffect(() => {
    // Simulate loading batch results
    const mockResults: BatchResult[] = [
      {
        id: '1',
        filename: 'photo1.jpg',
        status: 'success',
        extractionDate: '2025-01-05T10:30:00Z',
        fieldsExtracted: 142,
        fileSize: 2456789,
        fileType: 'image/jpeg',
        authenticityScore: 92,
        metadata: { make: 'Canon', model: 'EOS R5', datetime: '2025-01-04T15:30:45' }
      },
      {
        id: '2',
        filename: 'photo2.jpg',
        status: 'success',
        extractionDate: '2025-01-05T10:31:00Z',
        fieldsExtracted: 98,
        fileSize: 1876543,
        fileType: 'image/jpeg',
        authenticityScore: 78,
        metadata: { make: 'Nikon', model: 'D850', datetime: '2025-01-04T16:22:10' }
      },
      {
        id: '3',
        filename: 'document.pdf',
        status: 'success',
        extractionDate: '2025-01-05T10:32:00Z',
        fieldsExtracted: 67,
        fileSize: 3210987,
        fileType: 'application/pdf',
        authenticityScore: 85,
        metadata: { producer: 'Adobe PDF Library', creator: 'Microsoft Word', creationDate: 'D:20250103120000Z' }
      },
      {
        id: '4',
        filename: 'image_with_issues.jpg',
        status: 'error',
        extractionDate: '2025-01-05T10:33:00Z',
        fieldsExtracted: 0,
        fileSize: 4567890,
        fileType: 'image/jpeg',
        metadata: {}
      },
      {
        id: '5',
        filename: 'medical_scan.dcm',
        status: 'success',
        extractionDate: '2025-01-05T10:34:00Z',
        fieldsExtracted: 203,
        fileSize: 5678901,
        fileType: 'application/dicom',
        authenticityScore: 95,
        metadata: { modality: 'CT', manufacturer: 'GE Healthcare', studyDate: '20250102' }
      }
    ];

    setTimeout(() => {
      setBatchResults(mockResults);
      setIsLoading(false);
    }, 800);
  }, [batchId]);

  const handleSelectFile = (id: string) => {
    setSelectedFiles(prev => 
      prev.includes(id) 
        ? prev.filter(fileId => fileId !== id) 
        : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedFiles.length === batchResults.length) {
      setSelectedFiles([]);
    } else {
      setSelectedFiles(batchResults.map(result => result.id));
    }
  };

  const handleExport = (format: 'json' | 'csv' | 'pdf') => {
    console.log(`Exporting batch results as ${format.toUpperCase()}`);
    // Implementation would go here
  };

  const handleReprocess = () => {
    console.log('Reprocessing selected files');
    // Implementation would go here
  };

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

  const successCount = batchResults.filter(r => r.status === 'success').length;
  const errorCount = batchResults.filter(r => r.status === 'error').length;
  const processingCount = batchResults.filter(r => r.status === 'processing').length;

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Batch Results</h1>
        <p className="text-slate-300">
          Analyze and compare metadata from multiple files in a single batch
        </p>
      </div>

      {/* Batch Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-300">Total Files</p>
                <p className="text-2xl font-bold text-white">{batchResults.length}</p>
              </div>
              <FileText className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-300">Successful</p>
                <p className="text-2xl font-bold text-emerald-400">{successCount}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-emerald-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-300">Errors</p>
                <p className="text-2xl font-bold text-red-400">{errorCount}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-300">Avg Fields</p>
                <p className="text-2xl font-bold text-white">
                  {batchResults.length > 0 
                    ? Math.round(batchResults.reduce((sum, r) => sum + r.fieldsExtracted, 0) / batchResults.length) 
                    : 0}
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Actions Toolbar */}
      <div className="flex flex-wrap gap-3 mb-6">
        <Button 
          variant="outline" 
          onClick={handleSelectAll}
          className="gap-2"
        >
          {selectedFiles.length === batchResults.length ? 'Deselect All' : 'Select All'}
        </Button>
        
        <Button 
          variant="outline" 
          disabled={selectedFiles.length === 0}
          onClick={handleReprocess}
          className="gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Reprocess Selected
        </Button>
        
        <div className="flex gap-2 ml-auto">
          <Button 
            variant="outline" 
            onClick={() => handleExport('json')}
            className="gap-2"
          >
            <FileJson className="w-4 h-4" />
            Export JSON
          </Button>
          
          <Button 
            variant="outline" 
            onClick={() => handleExport('csv')}
            className="gap-2"
          >
            <FileSpreadsheet className="w-4 h-4" />
            Export CSV
          </Button>
          
          <Button 
            variant="outline" 
            onClick={() => handleExport('pdf')}
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-muted/50">
          <TabsTrigger value="grid" className="text-xs">Grid View</TabsTrigger>
          <TabsTrigger value="stats" className="text-xs">Statistics</TabsTrigger>
          <TabsTrigger value="compare" className="text-xs">Compare</TabsTrigger>
        </TabsList>

        <TabsContent value="grid" className="mt-6">
          <BatchGrid 
            results={batchResults} 
            selectedFiles={selectedFiles}
            onSelectFile={handleSelectFile}
            onSelectAll={handleSelectAll}
            allSelected={selectedFiles.length === batchResults.length}
          />
        </TabsContent>

        <TabsContent value="stats" className="mt-6">
          <BatchStats results={batchResults} />
        </TabsContent>

        <TabsContent value="compare" className="mt-6">
          <FileComparison 
            results={batchResults.filter(r => selectedFiles.includes(r.id))} 
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BatchResultsPage;