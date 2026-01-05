// client/src/components/viz/MetadataComparison.tsx
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  GitCompare,
  ArrowRightLeft,
  FileDiff,
  Plus,
  Minus,
  RefreshCw,
  Columns,
} from 'lucide-react';

interface MetadataComparisonProps {
  file1?: {
    filename: string;
    metadata: Record<string, any>;
    thumbnail?: string;
  };
  file2?: {
    filename: string;
    metadata: Record<string, any>;
    thumbnail?: string;
  };
}

interface DiffResult {
  key: string;
  value1: any;
  value2: any;
  status: 'added' | 'removed' | 'changed' | 'unchanged';
}

function compareMetadata(
  meta1: Record<string, any> | undefined,
  meta2: Record<string, any> | undefined
): DiffResult[] {
  if (!meta1 || !meta2) return [];

  const allKeys = new Set([...Object.keys(meta1), ...Object.keys(meta2)]);
  const results: DiffResult[] = [];

  allKeys.forEach(key => {
    const val1 = meta1[key];
    const val2 = meta2[key];

    if (val1 === undefined && val2 !== undefined) {
      results.push({ key, value1: null, value2: val2, status: 'added' });
    } else if (val1 !== undefined && val2 === undefined) {
      results.push({ key, value1: val1, value2: null, status: 'removed' });
    } else if (JSON.stringify(val1) !== JSON.stringify(val2)) {
      results.push({ key, value1: val1, value2: val2, status: 'changed' });
    } else {
      results.push({ key, value1: val1, value2: val2, status: 'unchanged' });
    }
  });

  return results.sort((a, b) => {
    const order = { added: 0, removed: 1, changed: 2, unchanged: 3 };
    return order[a.status] - order[b.status];
  });
}

function formatValue(value: any): string {
  if (value === null || value === undefined) return 'N/A';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

export function MetadataComparison({ file1, file2 }: MetadataComparisonProps) {
  const [filter, setFilter] = useState<'all' | 'changed' | 'added' | 'removed'>(
    'all'
  );
  const [viewMode, setViewMode] = useState<'diff' | 'split'>('diff');

  // Sample data if no files provided
  const sampleMeta1 = file1?.metadata || {
    DateTimeOriginal: '2024:03:15 14:30:00',
    Make: 'Canon',
    Model: 'EOS R5',
    ISO: 400,
    FNumber: 2.8,
    FocalLength: 50,
    Flash: 'No flash',
    WhiteBalance: 'Auto',
  };

  const sampleMeta2 = file2?.metadata || {
    DateTimeOriginal: '2024:03:15 14:30:05',
    Make: 'Canon',
    Model: 'EOS R5',
    ISO: 800,
    FNumber: 2.8,
    FocalLength: 85,
    Flash: 'Fired',
    WhiteBalance: 'Manual',
  };

  const diffResults = compareMetadata(sampleMeta1, sampleMeta2);

  const filteredDiff = diffResults.filter(
    r => filter === 'all' || r.status === filter
  );

  const stats = {
    total: diffResults.length,
    changed: diffResults.filter(r => r.status === 'changed').length,
    added: diffResults.filter(r => r.status === 'added').length,
    removed: diffResults.filter(r => r.status === 'removed').length,
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <GitCompare className="w-5 h-5" />
          Metadata Comparison
        </CardTitle>
        <CardDescription>Compare metadata between two files</CardDescription>
      </CardHeader>
      <CardContent>
        {/* File headers */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1 p-3 rounded-lg bg-muted/50 text-center">
            <div className="font-medium truncate">
              {file1?.filename || 'File 1'}
            </div>
            <div className="text-xs text-muted-foreground">
              {Object.keys(sampleMeta1).length} fields
            </div>
          </div>
          <ArrowRightLeft className="w-5 h-5 text-muted-foreground" />
          <div className="flex-1 p-3 rounded-lg bg-muted/50 text-center">
            <div className="font-medium truncate">
              {file2?.filename || 'File 2'}
            </div>
            <div className="text-xs text-muted-foreground">
              {Object.keys(sampleMeta2).length} fields
            </div>
          </div>
        </div>

        {/* Filter tabs */}
        <Tabs
          value={filter}
          onValueChange={v => setFilter(v as any)}
          className="mb-4"
        >
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all" className="flex items-center gap-1">
              All
              <Badge variant="secondary" className="text-xs">
                {stats.total}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="changed" className="flex items-center gap-1">
              Changed
              <Badge variant="secondary" className="text-xs">
                {stats.changed}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="added" className="flex items-center gap-1">
              Added
              <Badge variant="secondary" className="text-xs">
                {stats.added}
              </Badge>
            </TabsTrigger>
            <TabsTrigger value="removed" className="flex items-center gap-1">
              Removed
              <Badge variant="secondary" className="text-xs">
                {stats.removed}
              </Badge>
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Diff view */}
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {filteredDiff.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No differences found
            </div>
          ) : (
            filteredDiff.map((diff, idx) => (
              <div
                key={`${diff.key}-${idx}`}
                className={`p-3 rounded-lg border ${
                  diff.status === 'changed'
                    ? 'border-amber-200 bg-amber-50/50'
                    : diff.status === 'added'
                      ? 'border-green-200 bg-green-50/50'
                      : diff.status === 'removed'
                        ? 'border-red-200 bg-red-50/50'
                        : 'border-muted bg-muted/30'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Badge
                    variant={
                      diff.status === 'changed'
                        ? 'secondary'
                        : diff.status === 'added'
                          ? 'default'
                          : diff.status === 'removed'
                            ? 'destructive'
                            : 'outline'
                    }
                    className="text-xs"
                  >
                    {diff.status === 'changed' && (
                      <ArrowRightLeft className="w-3 h-3 mr-1" />
                    )}
                    {diff.status === 'added' && (
                      <Plus className="w-3 h-3 mr-1" />
                    )}
                    {diff.status === 'removed' && (
                      <Minus className="w-3 h-3 mr-1" />
                    )}
                    {diff.status}
                  </Badge>
                  <span className="font-medium text-sm">{diff.key}</span>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-2">
                  <div className={diff.status === 'added' ? 'opacity-50' : ''}>
                    <div className="text-xs text-muted-foreground">File 1</div>
                    <div className="font-mono text-sm">
                      {formatValue(diff.value1)}
                    </div>
                  </div>
                  <div
                    className={diff.status === 'removed' ? 'opacity-50' : ''}
                  >
                    <div className="text-xs text-muted-foreground">File 2</div>
                    <div className="font-mono text-sm">
                      {formatValue(diff.value2)}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
