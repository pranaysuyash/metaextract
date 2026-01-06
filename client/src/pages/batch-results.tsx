import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  XCircle,
  Filter,
  Search,
  RefreshCw,
  Clock,
  Calendar,
  TrendingUp,
  AlertCircle,
  Grid,
  List,
  Eye,
  EyeOff,
} from 'lucide-react';
import { parseApiError } from '@/utils/api-error-handler';
import { apiRequest } from '@/lib/queryClient';
import { useAuth, useCanAccessTier } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';

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

interface BatchFilters {
  status?: string;
  fileType?: string;
  dateRange?: { start: Date; end: Date };
  minFields?: number;
  maxFields?: number;
}

interface BatchSummary {
  totalFiles: number;
  successfulFiles: number;
  errorFiles: number;
  processingFiles: number;
  pendingFiles: number;
  totalFields: number;
  totalSize: number;
  avgProcessingTime: number;
  successRate: number;
}

interface BatchJob {
  id: string;
  name: string;
  createdAt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  totalFiles: number;
  processedFiles: number;
  results: BatchResult[];
}

export const BatchResultsPage: React.FC = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const canAccessProfessional = useCanAccessTier('professional');

  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [filters, setFilters] = useState<BatchFilters>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [showUploadZone, setShowUploadZone] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(12);

  // Fetch batch jobs for the user
  const { data: batchJobs = [], isLoading: isLoadingJobs } = useQuery<
    BatchJob[]
  >({
    queryKey: ['/api/batch/jobs'],
    queryFn: async () => {
      const response = await apiRequest('GET', '/api/batch/jobs');
      return response.json();
    },
    enabled: !!user && canAccessProfessional,
  });

  // Get the most recent batch job
  const currentBatchJob = batchJobs[0];

  // Fetch detailed results for current batch
  const { data: batchResults = [], isLoading: isLoadingResults } = useQuery<
    BatchResult[]
  >({
    queryKey: [`/api/batch/jobs/${currentBatchJob?.id}/results`],
    queryFn: async () => {
      if (!currentBatchJob?.id) return [];
      const response = await apiRequest(
        'GET',
        `/api/batch/jobs/${currentBatchJob.id}/results`
      );
      return response.json();
    },
    enabled: !!currentBatchJob?.id && canAccessProfessional,
    refetchInterval: currentBatchJob?.status === 'processing' ? 5000 : false,
  });

  // Filter and search results
  const filteredResults = React.useMemo(() => {
    if (!canAccessProfessional) return [];

    let results = [...batchResults];

    // Apply search filter
    if (searchTerm) {
      results = results.filter(
        result =>
          result.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
          result.fileType.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply status filter
    if (filters.status && filters.status !== 'all') {
      results = results.filter(result => result.status === filters.status);
    }

    // Apply file type filter
    if (filters.fileType && filters.fileType !== 'all') {
      const fileTypeFilter = filters.fileType;
      results = results.filter(
        result => result.fileType && result.fileType.startsWith(fileTypeFilter)
      );
    }

    return results;
  }, [batchResults, searchTerm, filters, canAccessProfessional]);

  // Pagination
  const paginatedResults = React.useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredResults.slice(startIndex, endIndex);
  }, [filteredResults, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredResults.length / itemsPerPage);

  const handleSelectFile = (id: string) => {
    setSelectedFiles(prev =>
      prev.includes(id) ? prev.filter(fileId => fileId !== id) : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedFiles.length === paginatedResults.length) {
      setSelectedFiles([]);
    } else {
      setSelectedFiles(paginatedResults.map(result => result.id));
    }
  };

  const handleExport = (format: 'json' | 'csv') => {
    setShowExportDialog(true);
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
    setCurrentPage(1);
  };

  const getStatusIcon = (status: BatchResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'processing':
        return <RefreshCw className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-blue-500" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: BatchResult['status']) => {
    switch (status) {
      case 'success':
        return (
          <Badge
            variant="secondary"
            className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
          >
            Success
          </Badge>
        );
      case 'error':
        return (
          <Badge
            variant="secondary"
            className="bg-red-500/20 text-red-400 border-red-500/30"
          >
            Error
          </Badge>
        );
      case 'processing':
        return (
          <Badge
            variant="secondary"
            className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30 animate-pulse"
          >
            Processing
          </Badge>
        );
      case 'pending':
        return (
          <Badge
            variant="secondary"
            className="bg-blue-500/20 text-blue-400 border-blue-500/30"
          >
            Pending
          </Badge>
        );
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const summary = React.useMemo((): BatchSummary => {
    const totalFiles = filteredResults.length;
    const successfulFiles = filteredResults.filter(
      r => r.status === 'success'
    ).length;
    const errorFiles = filteredResults.filter(r => r.status === 'error').length;
    const processingFiles = filteredResults.filter(
      r => r.status === 'processing'
    ).length;
    const pendingFiles = filteredResults.filter(
      r => r.status === 'pending'
    ).length;
    const totalFields = filteredResults.reduce(
      (sum, r) => sum + r.fieldsExtracted,
      0
    );
    const totalSize = filteredResults.reduce((sum, r) => sum + r.fileSize, 0);
    const processingTimes = filteredResults.flatMap(result =>
      typeof result.processingTime === 'number' ? [result.processingTime] : []
    );
    const avgProcessingTime =
      processingTimes.length > 0
        ? processingTimes.reduce((sum, time) => sum + time, 0) /
          processingTimes.length
        : 0;
    const successRate =
      totalFiles > 0 ? (successfulFiles / totalFiles) * 100 : 0;

    return {
      totalFiles,
      successfulFiles,
      errorFiles,
      processingFiles,
      pendingFiles,
      totalFields,
      totalSize,
      avgProcessingTime,
      successRate,
    };
  }, [filteredResults]);

  // Tier restriction message
  if (!canAccessProfessional) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="bg-card border-white/10">
          <CardContent className="py-12 text-center">
            <FileText className="w-12 h-12 mx-auto mb-4 text-slate-500" />
            <h2 className="text-xl font-semibold text-white mb-2">
              Professional Feature
            </h2>
            <p className="text-slate-300 mb-6">
              Batch processing is available for Professional tier and above.
            </p>
            <Button onClick={() => (window.location.href = '/credits')}>
              Upgrade to Professional
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoadingJobs) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="space-y-4">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Batch Processing Results
            </h1>
            <p className="text-slate-300">
              Analyze and compare metadata from multiple files in a single batch
            </p>
          </div>
          <Button onClick={() => setShowUploadZone(true)} className="gap-2">
            <Upload className="w-4 h-4" />
            New Batch
          </Button>
        </div>

        {/* Current Batch Info */}
        {currentBatchJob && (
          <div className="flex items-center gap-4 text-sm text-slate-300">
            <span>Batch: {currentBatchJob.name}</span>
            <span>•</span>
            <span>
              Created: {new Date(currentBatchJob.createdAt).toLocaleString()}
            </span>
            <span>•</span>
            <Badge variant="outline">{currentBatchJob.status}</Badge>
          </div>
        )}
      </div>

      {/* Statistics Overview */}
      {currentBatchJob && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
          <Card className="bg-card border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-300">Total Files</p>
                  <p className="text-2xl font-bold text-white">
                    {summary.totalFiles}
                  </p>
                </div>
                <FileText className="w-6 h-6 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-300">Successful</p>
                  <p className="text-2xl font-bold text-emerald-400">
                    {summary.successfulFiles}
                  </p>
                  <p className="text-xs text-slate-400">
                    {Math.round(summary.successRate)}%
                  </p>
                </div>
                <CheckCircle className="w-6 h-6 text-emerald-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-300">Errors</p>
                  <p className="text-2xl font-bold text-red-400">
                    {summary.errorFiles}
                  </p>
                </div>
                <XCircle className="w-6 h-6 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-300">Processing</p>
                  <p className="text-2xl font-bold text-yellow-400">
                    {summary.processingFiles}
                  </p>
                </div>
                <AlertCircle className="w-6 h-6 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-300">Avg Fields</p>
                  <p className="text-2xl font-bold text-white">
                    {summary.totalFiles > 0
                      ? Math.round(summary.totalFields / summary.totalFiles)
                      : 0}
                  </p>
                </div>
                <BarChart3 className="w-6 h-6 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-300">Avg Time</p>
                  <p className="text-2xl font-bold text-white">
                    {summary.avgProcessingTime > 0
                      ? `${Math.round(summary.avgProcessingTime / 1000)}s`
                      : 'N/A'}
                  </p>
                </div>
                <Clock className="w-6 h-6 text-primary" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Controls */}
      {currentBatchJob && (
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search files by name or type..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Select
              value={filters.status || 'all'}
              onValueChange={value =>
                setFilters(prev => ({
                  ...prev,
                  status: value === 'all' ? undefined : value,
                }))
              }
            >
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="success">Success</SelectItem>
                <SelectItem value="error">Error</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              size="icon"
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            >
              {viewMode === 'grid' ? (
                <List className="w-4 h-4" />
              ) : (
                <Grid className="w-4 h-4" />
              )}
            </Button>

            {(searchTerm || filters.status) && (
              <Button
                variant="outline"
                onClick={clearFilters}
                className="gap-2"
              >
                <Filter className="w-4 h-4" />
                Clear
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Actions Toolbar */}
      {currentBatchJob && (
        <div className="flex flex-wrap gap-3 mb-6">
          <Button variant="outline" onClick={handleSelectAll} className="gap-2">
            {selectedFiles.length === paginatedResults.length
              ? 'Deselect All'
              : 'Select All'}
          </Button>

          <Button
            variant="outline"
            disabled={selectedFiles.length === 0}
            className="gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Reprocess
          </Button>

          <div className="flex gap-2 ml-auto">
            <Button
              variant="outline"
              onClick={() => handleExport('json')}
              className="gap-2"
              disabled={filteredResults.length === 0}
            >
              <FileJson className="w-4 h-4" />
              Export JSON
            </Button>

            <Button
              variant="outline"
              onClick={() => handleExport('csv')}
              className="gap-2"
              disabled={filteredResults.length === 0}
            >
              <FileSpreadsheet className="w-4 h-4" />
              Export CSV
            </Button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      {currentBatchJob ? (
        <div className="space-y-6">
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {paginatedResults.map(result => (
                <Card
                  key={result.id}
                  className="bg-card border-white/10 hover:border-white/20 transition-colors"
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={selectedFiles.includes(result.id)}
                          onChange={() => handleSelectFile(result.id)}
                          className="rounded border-white/20 bg-background"
                        />
                        {getStatusIcon(result.status)}
                      </div>
                      {getStatusBadge(result.status)}
                    </div>

                    <h3
                      className="font-medium text-white mb-2 truncate"
                      title={result.filename}
                    >
                      {result.filename}
                    </h3>

                    <div className="space-y-1 text-sm text-slate-300">
                      <div className="flex justify-between">
                        <span>Fields:</span>
                        <span className="text-white">
                          {result.fieldsExtracted}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Size:</span>
                        <span className="text-white">
                          {Math.round(result.fileSize / 1024)}KB
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Type:</span>
                        <span className="text-white text-xs">
                          {result.fileType}
                        </span>
                      </div>
                    </div>

                    <div className="mt-3 pt-3 border-t border-white/10">
                      <p className="text-xs text-slate-400">
                        {new Date(result.extractionDate).toLocaleDateString()}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="bg-card border-white/10">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b border-white/10">
                    <tr>
                      <th className="text-left p-4">
                        <input
                          type="checkbox"
                          checked={
                            selectedFiles.length === paginatedResults.length &&
                            paginatedResults.length > 0
                          }
                          onChange={handleSelectAll}
                          className="rounded border-white/20 bg-background"
                        />
                      </th>
                      <th className="text-left p-4 text-slate-300 font-medium">
                        File
                      </th>
                      <th className="text-left p-4 text-slate-300 font-medium">
                        Status
                      </th>
                      <th className="text-left p-4 text-slate-300 font-medium">
                        Fields
                      </th>
                      <th className="text-left p-4 text-slate-300 font-medium">
                        Size
                      </th>
                      <th className="text-left p-4 text-slate-300 font-medium">
                        Type
                      </th>
                      <th className="text-left p-4 text-slate-300 font-medium">
                        Date
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedResults.map(result => (
                      <tr
                        key={result.id}
                        className="border-b border-white/5 hover:bg-white/5"
                      >
                        <td className="p-4">
                          <input
                            type="checkbox"
                            checked={selectedFiles.includes(result.id)}
                            onChange={() => handleSelectFile(result.id)}
                            className="rounded border-white/20 bg-background"
                          />
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(result.status)}
                            <span className="text-white font-medium">
                              {result.filename}
                            </span>
                          </div>
                        </td>
                        <td className="p-4">{getStatusBadge(result.status)}</td>
                        <td className="p-4 text-white">
                          {result.fieldsExtracted}
                        </td>
                        <td className="p-4 text-white">
                          {Math.round(result.fileSize / 1024)}KB
                        </td>
                        <td className="p-4 text-white text-sm">
                          {result.fileType}
                        </td>
                        <td className="p-4 text-slate-300 text-sm">
                          {new Date(result.extractionDate).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <div className="text-sm text-slate-300">
                Showing {(currentPage - 1) * itemsPerPage + 1} to{' '}
                {Math.min(currentPage * itemsPerPage, filteredResults.length)}{' '}
                of {filteredResults.length} results
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <span className="flex items-center px-3 text-white">
                  Page {currentPage} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  onClick={() =>
                    setCurrentPage(prev => Math.min(totalPages, prev + 1))
                  }
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <Card className="bg-card border-white/10">
          <CardContent className="py-12 text-center">
            <FileText className="w-12 h-12 mx-auto mb-4 text-slate-500" />
            <p className="text-white mb-2">No batch jobs found</p>
            <p className="text-sm text-slate-300 mb-4">
              Upload multiple files to create your first batch processing job
            </p>
            <Button onClick={() => setShowUploadZone(true)}>
              <Upload className="w-4 h-4 mr-2" />
              Start Batch Processing
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default BatchResultsPage;
