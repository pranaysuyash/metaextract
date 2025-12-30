import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  GitCompare, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  FileText,
  Calendar,
  MapPin,
  Camera,
  Hash,
  Download,
  Eye,
  EyeOff
} from 'lucide-react';

interface ComparisonResult {
  comparison_id: string;
  total_files: number;
  file_names: string[];
  processing_time_ms: number;
  comparison_result: {
    summary: {
      total_comparisons: number;
      identical_files: number;
      similar_files: number;
      different_files: number;
      overall_similarity: number;
    };
    field_comparisons: {
      [fieldName: string]: {
        identical_count: number;
        different_count: number;
        similarity_score: number;
        variations: Array<{
          file_index: number;
          file_name: string;
          value: any;
        }>;
      };
    };
    file_pairs: Array<{
      file1_index: number;
      file2_index: number;
      file1_name: string;
      file2_name: string;
      similarity_score: number;
      matching_fields: string[];
      differing_fields: string[];
    }>;
    suspicious_patterns: string[];
    recommendations: string[];
  };
}

interface ComparisonViewProps {
  comparisonResult: ComparisonResult;
}

export function ComparisonView({ comparisonResult }: ComparisonViewProps) {
  const [selectedFields, setSelectedFields] = useState<string[]>([]);
  const [showOnlyDifferences, setShowOnlyDifferences] = useState(false);

  const { comparison_result: result } = comparisonResult;

  const getSimilarityColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 0.7) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getSimilarityIcon = (score: number) => {
    if (score >= 0.9) return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (score >= 0.7) return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
    return <XCircle className="h-4 w-4 text-red-600" />;
  };

  const getFieldIcon = (fieldName: string) => {
    if (fieldName.includes('gps') || fieldName.includes('location')) {
      return <MapPin className="h-4 w-4" />;
    }
    if (fieldName.includes('date') || fieldName.includes('time')) {
      return <Calendar className="h-4 w-4" />;
    }
    if (fieldName.includes('camera') || fieldName.includes('exif')) {
      return <Camera className="h-4 w-4" />;
    }
    if (fieldName.includes('hash') || fieldName.includes('checksum')) {
      return <Hash className="h-4 w-4" />;
    }
    return <FileText className="h-4 w-4" />;
  };

  const filteredFields = Object.entries(result.field_comparisons).filter(([fieldName, comparison]) => {
    if (showOnlyDifferences && comparison.similarity_score >= 0.99) {
      return false;
    }
    if (selectedFields.length > 0 && !selectedFields.includes(fieldName)) {
      return false;
    }
    return true;
  });

  const exportComparison = () => {
    const exportData = {
      comparison_id: comparisonResult.comparison_id,
      generated_at: new Date().toISOString(),
      files: comparisonResult.file_names,
      summary: result.summary,
      detailed_comparison: result.field_comparisons,
      file_pairs: result.file_pairs,
      suspicious_patterns: result.suspicious_patterns,
      recommendations: result.recommendations
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `metadata-comparison-${comparisonResult.comparison_id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-blue-900">
              <GitCompare className="h-6 w-6" />
              Metadata Comparison Analysis
            </CardTitle>
            <Button onClick={exportComparison} variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-700">
                {comparisonResult.total_files}
              </div>
              <div className="text-sm text-blue-600">Files Compared</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-700">
                {(result.summary.overall_similarity * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-green-600">Overall Similarity</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-700">
                {result.summary.total_comparisons}
              </div>
              <div className="text-sm text-gray-600">Field Comparisons</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-700">
                {(comparisonResult.processing_time_ms / 1000).toFixed(1)}s
              </div>
              <div className="text-sm text-purple-600">Processing Time</div>
            </div>
          </div>

          {/* File List */}
          <div className="mt-4">
            <h4 className="font-medium text-gray-700 mb-2">Files Analyzed</h4>
            <div className="flex flex-wrap gap-2">
              {comparisonResult.file_names.map((fileName, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {fileName}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Suspicious Patterns Alert */}
      {result.suspicious_patterns.length > 0 && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>Suspicious Patterns Detected:</strong>
            <ul className="mt-2 list-disc list-inside">
              {result.suspicious_patterns.map((pattern, index) => (
                <li key={index}>{pattern}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Comparison Tabs */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="fields">Field Analysis</TabsTrigger>
          <TabsTrigger value="pairs">File Pairs</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Identical Files
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-700">
                  {result.summary.identical_files}
                </div>
                <div className="text-sm text-gray-600">
                  {((result.summary.identical_files / comparisonResult.total_files) * 100).toFixed(1)}% of total
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  Similar Files
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-yellow-700">
                  {result.summary.similar_files}
                </div>
                <div className="text-sm text-gray-600">
                  {((result.summary.similar_files / comparisonResult.total_files) * 100).toFixed(1)}% of total
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <XCircle className="h-5 w-5 text-red-600" />
                  Different Files
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-700">
                  {result.summary.different_files}
                </div>
                <div className="text-sm text-gray-600">
                  {((result.summary.different_files / comparisonResult.total_files) * 100).toFixed(1)}% of total
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {result.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{recommendation}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Field Analysis Tab */}
        <TabsContent value="fields" className="space-y-4">
          {/* Field Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4 mb-4">
                <Button
                  variant={showOnlyDifferences ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowOnlyDifferences(!showOnlyDifferences)}
                >
                  {showOnlyDifferences ? <Eye className="h-4 w-4 mr-2" /> : <EyeOff className="h-4 w-4 mr-2" />}
                  {showOnlyDifferences ? 'Show All Fields' : 'Show Only Differences'}
                </Button>
              </div>

              <div className="text-sm text-gray-600 mb-2">
                Showing {filteredFields.length} of {Object.keys(result.field_comparisons).length} fields
              </div>
            </CardContent>
          </Card>

          {/* Field Comparison Results */}
          <div className="space-y-3">
            {filteredFields.map(([fieldName, comparison]) => (
              <Card key={fieldName} className={getSimilarityColor(comparison.similarity_score)}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {getFieldIcon(fieldName)}
                      <span className="font-medium">{fieldName}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {getSimilarityIcon(comparison.similarity_score)}
                      <span className="font-bold">
                        {(comparison.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Identical: </span>
                      <span>{comparison.identical_count}</span>
                    </div>
                    <div>
                      <span className="font-medium">Different: </span>
                      <span>{comparison.different_count}</span>
                    </div>
                  </div>

                  {comparison.variations.length > 0 && (
                    <div className="mt-3">
                      <span className="font-medium text-sm">Variations:</span>
                      <div className="mt-1 space-y-1">
                        {comparison.variations.map((variation, index) => (
                          <div key={index} className="text-xs bg-white bg-opacity-50 p-2 rounded">
                            <span className="font-medium">{variation.file_name}:</span>
                            <span className="ml-2">{JSON.stringify(variation.value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* File Pairs Tab */}
        <TabsContent value="pairs" className="space-y-4">
          <div className="grid gap-4">
            {result.file_pairs.map((pair, index) => (
              <Card key={index} className={getSimilarityColor(pair.similarity_score)}>
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <GitCompare className="h-4 w-4" />
                      <span className="font-medium">
                        {pair.file1_name} ↔ {pair.file2_name}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {getSimilarityIcon(pair.similarity_score)}
                      <span className="font-bold">
                        {(pair.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Matching Fields ({pair.matching_fields.length}):</span>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {pair.matching_fields.slice(0, 5).map((field, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {field}
                          </Badge>
                        ))}
                        {pair.matching_fields.length > 5 && (
                          <Badge variant="outline" className="text-xs">
                            +{pair.matching_fields.length - 5} more
                          </Badge>
                        )}
                      </div>
                    </div>

                    <div>
                      <span className="font-medium">Differing Fields ({pair.differing_fields.length}):</span>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {pair.differing_fields.slice(0, 5).map((field, idx) => (
                          <Badge key={idx} variant="destructive" className="text-xs">
                            {field}
                          </Badge>
                        ))}
                        {pair.differing_fields.length > 5 && (
                          <Badge variant="destructive" className="text-xs">
                            +{pair.differing_fields.length - 5} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}