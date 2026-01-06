/**
 * Metadata Export - Export functionality for metadata results
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Download,
  FileText,
  FileJson,
  FileSpreadsheet,
  File,
} from 'lucide-react';

export interface MetadataExportProps {
  metadata: any;
  fileName: string;
  className?: string;
}

export const MetadataExport: React.FC<MetadataExportProps> = ({
  metadata,
  fileName,
  className = '',
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<
    'json' | 'csv' | 'pdf' | 'excel'
  >('json');

  const exportToJson = () => {
    const blob = new Blob([JSON.stringify(metadata, null, 2)], {
      type: 'application/json',
    });
    downloadBlob(blob, `${fileName}.json`);
  };

  const exportToCsv = () => {
    // Convert metadata to CSV format
    const csvContent = convertToCsv(metadata);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    downloadBlob(blob, `${fileName}.csv`);
  };

  const exportToPdf = async () => {
    // In a real implementation, this would use a PDF library like jsPDF
    // For now, we'll just create a text representation
    const textContent = convertToText(metadata);
    const blob = new Blob([textContent], { type: 'text/plain' });
    downloadBlob(blob, `${fileName}.txt`);
  };

  const exportToExcel = () => {
    // In a real implementation, this would use a library like xlsx
    // For now, we'll just export as CSV
    exportToCsv();
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const convertToCsv = (obj: any, prefix: string = ''): string => {
    const flattenObj = (obj: any, prefix: string = ''): Record<string, any> => {
      const flattened: Record<string, any> = {};

      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          const newKey = prefix ? `${prefix}.${key}` : key;

          if (
            typeof obj[key] === 'object' &&
            obj[key] !== null &&
            !Array.isArray(obj[key])
          ) {
            Object.assign(flattened, flattenObj(obj[key], newKey));
          } else {
            flattened[newKey] = obj[key];
          }
        }
      }

      return flattened;
    };

    const flattened = flattenObj(obj);
    const headers = Object.keys(flattened);
    const values = Object.values(flattened);

    return [
      headers.join(','),
      values.map(v => `"${String(v).replace(/"/g, '""')}"`).join(','),
    ].join('\n');
  };

  const convertToText = (obj: any, indent: number = 0): string => {
    let text = '';

    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const value = obj[key];
        const spaces = ' '.repeat(indent);

        if (
          typeof value === 'object' &&
          value !== null &&
          !Array.isArray(value)
        ) {
          text += `${spaces}${key}:\n`;
          text += convertToText(value, indent + 2);
        } else {
          text += `${spaces}${key}: ${value}\n`;
        }
      }
    }

    return text;
  };

  const handleExport = async () => {
    setIsExporting(true);

    try {
      switch (exportFormat) {
        case 'json':
          exportToJson();
          break;
        case 'csv':
          exportToCsv();
          break;
        case 'pdf':
          await exportToPdf();
          break;
        case 'excel':
          exportToExcel();
          break;
      }
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Card className={`bg-card border-white/10 ${className}`}>
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Download className="w-5 h-5 text-primary" />
          Export Metadata
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-3">
          <Button
            variant={exportFormat === 'json' ? 'default' : 'outline'}
            onClick={() => setExportFormat('json')}
            className="gap-2"
          >
            <FileJson className="w-4 h-4" />
            JSON
          </Button>

          <Button
            variant={exportFormat === 'csv' ? 'default' : 'outline'}
            onClick={() => setExportFormat('csv')}
            className="gap-2"
          >
            <FileSpreadsheet className="w-4 h-4" />
            CSV
          </Button>

          <Button
            variant={exportFormat === 'pdf' ? 'default' : 'outline'}
            onClick={() => setExportFormat('pdf')}
            className="gap-2"
          >
            <FileText className="w-4 h-4" />
            PDF
          </Button>

          <Button
            variant={exportFormat === 'excel' ? 'default' : 'outline'}
            onClick={() => setExportFormat('excel')}
            className="gap-2"
          >
            <File className="w-4 h-4" />
            Excel
          </Button>
        </div>

        <div className="mt-4 flex justify-between items-center">
          <Badge variant="outline" className="text-xs">
            Format: {exportFormat.toUpperCase()}
          </Badge>

          <Button
            onClick={handleExport}
            disabled={isExporting}
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            {isExporting ? 'Exporting...' : 'Export'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default MetadataExport;
