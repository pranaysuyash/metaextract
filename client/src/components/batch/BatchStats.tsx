import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  FileText, 
  Camera, 
  FileImage, 
  FileSpreadsheet, 
  Database,
  Hash,
  Eye,
  Clock
} from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from '@/components/ui/chart';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
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

interface BatchStatsProps {
  results: BatchResult[];
  batchJob?: BatchJob;
}

export const BatchStats: React.FC<BatchStatsProps> = ({ results, batchJob }) => {
  // Calculate statistics
  const totalFiles = results.length;
  const successfulFiles = results.filter(r => r.status === 'success').length;
  const errorFiles = results.filter(r => r.status === 'error').length;
  const processingFiles = results.filter(r => r.status === 'processing').length;
  
  const totalFields = results.reduce((sum, r) => sum + r.fieldsExtracted, 0);
  const avgFields = totalFiles > 0 ? Math.round(totalFields / totalFiles) : 0;
  
  const totalSize = results.reduce((sum, r) => sum + r.fileSize, 0);
  const avgSize = totalFiles > 0 ? totalSize / totalFiles : 0;
  
  // File type distribution
  const fileTypeCounts: Record<string, number> = {};
  results.forEach(r => {
    const type = r.fileType.split('/')[0] || r.fileType;
    fileTypeCounts[type] = (fileTypeCounts[type] || 0) + 1;
  });
  
  const fileTypeData = Object.entries(fileTypeCounts).map(([type, count]) => ({
    name: type,
    count,
    fill: getFileTypeColor(type)
  }));
  
  // Status distribution
  const statusData = [
    { name: 'Success', value: successfulFiles, fill: '#10b981' },
    { name: 'Error', value: errorFiles, fill: '#ef4444' },
    { name: 'Processing', value: processingFiles, fill: '#f59e0b' }
  ];
  
  // File size distribution
  const sizeRanges = [
    { name: '< 1MB', count: results.filter(r => r.fileSize < 1024 * 1024).length },
    { name: '1-10MB', count: results.filter(r => r.fileSize >= 1024 * 1024 && r.fileSize < 10 * 1024 * 1024).length },
    { name: '10-100MB', count: results.filter(r => r.fileSize >= 10 * 1024 * 1024 && r.fileSize < 100 * 1024 * 1024).length },
    { name: '> 100MB', count: results.filter(r => r.fileSize >= 100 * 1024 * 1024).length }
  ];
  
  // Fields extracted distribution
  const fieldsRanges = [
    { name: '0-50', count: results.filter(r => r.fieldsExtracted >= 0 && r.fieldsExtracted <= 50).length },
    { name: '51-100', count: results.filter(r => r.fieldsExtracted > 50 && r.fieldsExtracted <= 100).length },
    { name: '101-200', count: results.filter(r => r.fieldsExtracted > 100 && r.fieldsExtracted <= 200).length },
    { name: '200+', count: results.filter(r => r.fieldsExtracted > 200).length }
  ];

  return (
    <div className="space-y-6">
      {/* Batch Job Information */}
      {batchJob && (
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary" />
              Batch Job Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-1">
                <p className="text-xs text-slate-300">Job ID</p>
                <p className="text-sm font-mono text-white">{batchJob.id.slice(0, 8)}...</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-slate-300">Created</p>
                <p className="text-sm text-white">
                  {new Date(batchJob.createdAt).toLocaleDateString()}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-slate-300">Status</p>
                <Badge 
                  variant="secondary" 
                  className={cn(
                    "capitalize",
                    batchJob.status === 'completed' && "bg-emerald-500/20 text-emerald-400",
                    batchJob.status === 'failed' && "bg-red-500/20 text-red-400",
                    batchJob.status === 'processing' && "bg-yellow-500/20 text-yellow-400 animate-pulse",
                    batchJob.status === 'pending' && "bg-blue-500/20 text-blue-400"
                  )}
                >
                  {batchJob.status}
                </Badge>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-slate-300">Progress</p>
                <div className="flex items-center gap-2">
                  <Progress 
                    value={(batchJob.processedFiles / batchJob.totalFiles) * 100} 
                    className="h-2 flex-1"
                  />
                  <span className="text-sm text-white">
                    {batchJob.processedFiles}/{batchJob.totalFiles}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Total Files</p>
                <p className="text-xl font-bold text-white">{totalFiles}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-500/10 rounded-lg">
                <BarChart3 className="w-6 h-6 text-emerald-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Avg Fields</p>
                <p className="text-xl font-bold text-white">{avgFields}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Hash className="w-6 h-6 text-blue-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Avg Size</p>
                <p className="text-xl font-bold text-white">{formatFileSize(avgSize)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <Eye className="w-6 h-6 text-purple-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Success Rate</p>
                <p className="text-xl font-bold text-white">
                  {totalFiles > 0 ? Math.round((successfulFiles / totalFiles) * 100) : 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              Status Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-64">
              <PieChart>
                <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <ChartLegend content={<ChartLegendContent />} />
              </PieChart>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* File Type Distribution */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <FileImage className="w-5 h-5 text-primary" />
              File Type Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-64">
              <PieChart>
                <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                <Pie
                  data={fileTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="name"
                >
                  {fileTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <ChartLegend content={<ChartLegendContent />} />
              </PieChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* File Size Distribution */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              File Size Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-64">
              <BarChart data={sizeRanges}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Fields Extracted Distribution */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              Fields Extracted Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-64">
              <BarChart data={fieldsRanges}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="count" fill="#8b5cf6" />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <p className="text-sm text-slate-300 mb-2">Total Files Processed</p>
            <p className="text-2xl font-bold text-white">{totalFiles}</p>
            <div className="mt-2 space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-emerald-400">Success</span>
                <span className="text-white">{successfulFiles} ({totalFiles > 0 ? Math.round((successfulFiles / totalFiles) * 100) : 0}%)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-red-400">Errors</span>
                <span className="text-white">{errorFiles} ({totalFiles > 0 ? Math.round((errorFiles / totalFiles) * 100) : 0}%)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-yellow-400">Processing</span>
                <span className="text-white">{processingFiles} ({totalFiles > 0 ? Math.round((processingFiles / totalFiles) * 100) : 0}%)</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <p className="text-sm text-slate-300 mb-2">Total Data Processed</p>
            <p className="text-2xl font-bold text-white">{formatFileSize(totalSize)}</p>
            <div className="mt-2 space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Avg Size</span>
                <span className="text-white">{formatFileSize(avgSize)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Total Fields</span>
                <span className="text-white">{totalFields}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Avg Fields</span>
                <span className="text-white">{avgFields}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <p className="text-sm text-slate-300 mb-2">Authenticity Analysis</p>
            <p className="text-2xl font-bold text-white">
              {results.filter(r => r.authenticityScore !== undefined).length} files
            </p>
            <div className="mt-2 space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Avg Score</span>
                <span className="text-white">
                  {results.filter(r => r.authenticityScore !== undefined).length > 0
                    ? Math.round(results.reduce((sum, r) => r.authenticityScore ? sum + r.authenticityScore : sum, 0) / 
                      results.filter(r => r.authenticityScore !== undefined).length)
                    : 0}%
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">High Confidence</span>
                <span className="text-white">
                  {results.filter(r => r.authenticityScore && r.authenticityScore >= 80).length}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Low Confidence</span>
                <span className="text-white">
                  {results.filter(r => r.authenticityScore && r.authenticityScore < 50).length}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Helper function to format file size
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Helper function to get color for file types
function getFileTypeColor(type: string): string {
  switch (type) {
    case 'image': return '#3b82f6'; // blue
    case 'application': return '#ef4444'; // red
    case 'text': return '#10b981'; // green
    case 'video': return '#8b5cf6'; // purple
    case 'audio': return '#f59e0b'; // yellow
    default: return '#6b7280'; // gray
  }
}
