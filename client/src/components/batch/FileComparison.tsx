import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  Camera, 
  MapPin, 
  Calendar, 
  Hash,
  Eye,
  Settings,
  Image,
  FileImage,
  Database
} from 'lucide-react';

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

interface FileComparisonProps {
  results: BatchResult[];
}

export const FileComparison: React.FC<FileComparisonProps> = ({ results }) => {
  const [selectedComparison, setSelectedComparison] = useState('camera');
  
  if (results.length < 2) {
    return (
      <Card className="bg-card border-white/10">
        <CardContent className="py-12 text-center">
          <FileText className="w-12 h-12 mx-auto mb-4 text-slate-500" />
          <p className="text-white">Select at least 2 files to compare</p>
          <p className="text-sm text-slate-300 mt-1">Select files in the grid view to enable comparison</p>
        </CardContent>
      </Card>
    );
  }

  // Get common metadata keys across all selected files
  const allKeys = new Set<string>();
  results.forEach(result => {
    Object.keys(result.metadata).forEach(key => allKeys.add(key));
  });
  
  const commonKeys = Array.from(allKeys).filter(key => {
    return results.every(result => result.metadata.hasOwnProperty(key));
  });

  // Camera-specific keys
  const cameraKeys = [
    'make', 'model', 'lens_model', 'iso', 'focal_length', 'aperture', 'exposure_time', 
    'flash', 'white_balance', 'metering_mode', 'exposure_program'
  ].filter(key => commonKeys.includes(key));
  
  // Location-specific keys
  const locationKeys = [
    'gps_latitude', 'gps_longitude', 'gps_altitude', 'gps_date_stamp', 'gps_time_stamp'
  ].filter(key => commonKeys.includes(key));
  
  // File-specific keys
  const fileKeys = [
    'file_size', 'file_type', 'datetime_original', 'datetime_digitized', 'modify_date'
  ].filter(key => commonKeys.includes(key));

  const renderComparisonTable = (keys: string[]) => {
    if (keys.length === 0) {
      return (
        <div className="text-center py-8 text-slate-500">
          No common metadata fields to compare
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Field</th>
              {results.map((result, idx) => (
                <th key={idx} className="text-left py-3 px-4 text-slate-300 font-medium">
                  <div className="flex items-center gap-2">
                    <FileImage className="w-4 h-4 text-primary" />
                    <span className="truncate max-w-[120px]">{result.filename}</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {keys.map((key, idx) => (
              <tr key={key} className={`border-b border-white/5 ${idx % 2 === 0 ? 'bg-muted/10' : ''}`}>
                <td className="py-3 px-4 text-white font-medium capitalize">
                  {key.replace(/_/g, ' ')}
                </td>
                {results.map((result, idx) => (
                  <td key={idx} className="py-3 px-4 text-slate-200">
                    {formatValue(result.metadata[key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'object') return JSON.stringify(value);
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    return String(value);
  };

  const renderFileCards = () => {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {results.map((result, idx) => (
          <Card key={result.id} className="bg-card border-white/10">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <FileImage className="w-8 h-8 text-primary mt-1" />
                <div className="flex-1">
                  <h3 className="font-medium text-white truncate">{result.filename}</h3>
                  <div className="mt-2 space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-300">Type:</span>
                      <span className="text-white">{result.fileType}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-300">Size:</span>
                      <span className="text-white">{formatFileSize(result.fileSize)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-300">Fields:</span>
                      <span className="text-white">{result.fieldsExtracted}</span>
                    </div>
                    {result.authenticityScore !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-slate-300">Authenticity:</span>
                        <span className="text-white">{result.authenticityScore}%</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            Compare {results.length} Files
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedComparison} onValueChange={setSelectedComparison}>
            <TabsList className="grid w-full grid-cols-4 bg-muted/50">
              <TabsTrigger value="overview" className="text-xs">Overview</TabsTrigger>
              <TabsTrigger value="camera" className="text-xs">Camera Settings</TabsTrigger>
              <TabsTrigger value="location" className="text-xs">Location</TabsTrigger>
              <TabsTrigger value="file" className="text-xs">File Details</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="mt-4">
              {renderFileCards()}
            </TabsContent>

            <TabsContent value="camera" className="mt-4">
              {renderComparisonTable(cameraKeys)}
            </TabsContent>

            <TabsContent value="location" className="mt-4">
              {renderComparisonTable(locationKeys)}
            </TabsContent>

            <TabsContent value="file" className="mt-4">
              {renderComparisonTable(fileKeys)}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Summary Card */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            Comparison Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Files Compared</p>
              <p className="text-xl font-bold text-white">{results.length}</p>
            </div>
            
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Common Fields</p>
              <p className="text-xl font-bold text-white">{commonKeys.length}</p>
            </div>
            
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Total Fields</p>
              <p className="text-xl font-bold text-white">
                {results.reduce((sum, r) => sum + r.fieldsExtracted, 0)}
              </p>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-white/10">
            <h4 className="font-medium text-white mb-2">Key Differences</h4>
            <div className="space-y-2">
              {commonKeys.slice(0, 5).map(key => {
                const values = results.map(r => r.metadata[key]);
                const uniqueValues = new Set(values.map(v => JSON.stringify(v)));
                
                if (uniqueValues.size > 1) {
                  return (
                    <div key={key} className="flex items-center gap-2 text-sm">
                      <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                      <span className="text-slate-300 capitalize">{key.replace(/_/g, ' ')}:</span>
                      <div className="flex gap-2">
                        {Array.from(uniqueValues).map((value, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {value}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  );
                }
                return null;
              })}
            </div>
          </div>
        </CardContent>
      </Card>
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