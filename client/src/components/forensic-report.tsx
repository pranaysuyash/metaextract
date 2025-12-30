import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  FileText, 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Download,
  Printer,
  Share,
  Calendar,
  User,
  Scale,
  Eye,
  TrendingDown,
  TrendingUp
} from 'lucide-react';

interface FileAnalysis {
  file_name: string;
  file_size: number;
  metadata: any;
  forensic_findings: string[];
  authenticity_score: number;
  risk_level: 'low' | 'medium' | 'high';
}

interface ForensicReportData {
  report_id: string;
  generated_at: string;
  analyst: string;
  case_summary: {
    total_files: number;
    file_names: string[];
    analysis_scope: string;
  };
  files: FileAnalysis[];
  cross_file_analysis: any;
  conclusions: {
    overall_assessment: 'low' | 'medium' | 'high';
    files_analyzed: number;
    high_risk_files: number;
    medium_risk_files: number;
    average_authenticity_score: number;
  };
  recommendations: string[];
  processing_time_ms: number;
}

interface ForensicReportProps {
  reportData: ForensicReportData;
}

export function ForensicReport({ reportData }: ForensicReportProps) {
  const [selectedTab, setSelectedTab] = useState('summary');

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-green-700 bg-green-100 border-green-300';
      case 'medium':
        return 'text-yellow-700 bg-yellow-100 border-yellow-300';
      case 'high':
        return 'text-red-700 bg-red-100 border-red-300';
      default:
        return 'text-gray-700 bg-gray-100 border-gray-300';
    }
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'high':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Shield className="h-4 w-4 text-gray-600" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const exportReport = (format: 'json' | 'pdf') => {
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(reportData, null, 2)], { 
        type: 'application/json' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `forensic-report-${reportData.report_id}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else {
      // PDF export would require additional implementation
      alert('PDF export functionality would be implemented with a PDF generation library');
    }
  };

  const printReport = () => {
    window.print();
  };

  const shareReport = () => {
    if (navigator.share) {
      navigator.share({
        title: `Forensic Analysis Report - ${reportData.report_id}`,
        text: `Forensic analysis completed for ${reportData.case_summary.total_files} files`,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Report URL copied to clipboard');
    }
  };

  return (
    <div className="space-y-6 print:space-y-4">
      {/* Report Header */}
      <Card className="border-blue-200 bg-blue-50 print:bg-white print:border-gray-300">
        <CardHeader>
          <div className="flex items-center justify-between print:block">
            <div>
              <CardTitle className="flex items-center gap-2 text-blue-900 print:text-black">
                <Scale className="h-6 w-6" />
                Forensic Analysis Report
              </CardTitle>
              <div className="text-sm text-blue-700 print:text-gray-600 mt-2">
                Report ID: {reportData.report_id}
              </div>
            </div>
            <div className="flex gap-2 print:hidden">
              <Button onClick={() => exportReport('json')} variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                JSON
              </Button>
              <Button onClick={() => exportReport('pdf')} variant="outline" size="sm">
                <FileText className="h-4 w-4 mr-2" />
                PDF
              </Button>
              <Button onClick={printReport} variant="outline" size="sm">
                <Printer className="h-4 w-4 mr-2" />
                Print
              </Button>
              <Button onClick={shareReport} variant="outline" size="sm">
                <Share className="h-4 w-4 mr-2" />
                Share
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 print:grid-cols-4">
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Calendar className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Generated</span>
              </div>
              <div className="text-sm">
                {new Date(reportData.generated_at).toLocaleDateString()}
              </div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <User className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Analyst</span>
              </div>
              <div className="text-sm">{reportData.analyst}</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <FileText className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Files</span>
              </div>
              <div className="text-sm">{reportData.case_summary.total_files}</div>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center gap-1 mb-1">
                <Shield className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium">Scope</span>
              </div>
              <div className="text-sm">Comprehensive</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Executive Summary */}
      <Card className="print:break-inside-avoid">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Executive Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 rounded-lg border">
              <div className={`text-3xl font-bold ${getRiskColor(reportData.conclusions.overall_assessment).split(' ')[0]}`}>
                {reportData.conclusions.overall_assessment.toUpperCase()}
              </div>
              <div className="text-sm text-gray-600 mt-1">Overall Risk Assessment</div>
            </div>
            <div className="text-center p-4 rounded-lg border">
              <div className={`text-3xl font-bold ${getScoreColor(reportData.conclusions.average_authenticity_score)}`}>
                {reportData.conclusions.average_authenticity_score.toFixed(0)}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Average Authenticity Score</div>
            </div>
            <div className="text-center p-4 rounded-lg border">
              <div className="text-3xl font-bold text-red-600">
                {reportData.conclusions.high_risk_files}
              </div>
              <div className="text-sm text-gray-600 mt-1">High Risk Files</div>
            </div>
          </div>

          <div className="prose max-w-none">
            <p className="text-gray-700">
              This forensic analysis examined {reportData.conclusions.files_analyzed} digital files 
              using advanced metadata extraction and authenticity verification techniques. 
              The analysis identified {reportData.conclusions.high_risk_files} high-risk files 
              and {reportData.conclusions.medium_risk_files} medium-risk files requiring further investigation.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="print:hidden">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="files">File Analysis</TabsTrigger>
          <TabsTrigger value="findings">Key Findings</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
        </TabsList>

        {/* Summary Tab */}
        <TabsContent value="summary" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Case Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2">Analysis Scope</h4>
                  <p className="text-sm text-gray-600">{reportData.case_summary.analysis_scope}</p>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Processing Time</h4>
                  <p className="text-sm text-gray-600">
                    {(reportData.processing_time_ms / 1000).toFixed(1)} seconds
                  </p>
                </div>
              </div>

              <div className="mt-4">
                <h4 className="font-medium mb-2">Files Analyzed</h4>
                <div className="flex flex-wrap gap-2">
                  {reportData.case_summary.file_names.map((fileName, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {fileName}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {['high', 'medium', 'low'].map(risk => {
                  const count = reportData.files.filter(f => f.risk_level === risk).length;
                  const percentage = (count / reportData.files.length) * 100;
                  
                  return (
                    <div key={risk} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getRiskIcon(risk)}
                        <span className="capitalize font-medium">{risk} Risk</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getRiskColor(risk).split(' ')[1]}`}
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-12 text-right">
                          {count} ({percentage.toFixed(0)}%)
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* File Analysis Tab */}
        <TabsContent value="files" className="space-y-4">
          {reportData.files.map((file, index) => (
            <Card key={index} className={getRiskColor(file.risk_level)}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    {getRiskIcon(file.risk_level)}
                    {file.file_name}
                  </CardTitle>
                  <Badge className={getRiskColor(file.risk_level)}>
                    {file.risk_level.toUpperCase()} RISK
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <span className="font-medium">File Size:</span>
                    <div className="text-sm">{(file.file_size / 1024).toFixed(1)} KB</div>
                  </div>
                  <div>
                    <span className="font-medium">Authenticity Score:</span>
                    <div className={`text-sm font-bold ${getScoreColor(file.authenticity_score)}`}>
                      {file.authenticity_score}%
                    </div>
                  </div>
                  <div>
                    <span className="font-medium">Findings:</span>
                    <div className="text-sm">{file.forensic_findings.length} issues</div>
                  </div>
                </div>

                {file.forensic_findings.length > 0 && (
                  <div>
                    <h5 className="font-medium mb-2">Forensic Findings:</h5>
                    <ul className="space-y-1">
                      {file.forensic_findings.map((finding, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <span>{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Key Findings Tab */}
        <TabsContent value="findings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Analysis Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <Eye className="h-4 w-4" />
                    Authenticity Assessment
                  </h4>
                  <p className="text-sm text-gray-600">
                    Based on comprehensive metadata analysis, steganography detection, 
                    manipulation detection, and AI content analysis across all submitted files.
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Chain of Custody
                  </h4>
                  <p className="text-sm text-gray-600">
                    Temporal analysis of file creation, modification, and access patterns 
                    to establish digital evidence integrity.
                  </p>
                </div>

                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <TrendingDown className="h-4 w-4" />
                    Risk Factors Identified
                  </h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {reportData.files.flatMap(f => f.forensic_findings).slice(0, 5).map((finding, idx) => (
                      <li key={idx}>• {finding}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Professional Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {reportData.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                    <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm">{recommendation}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Alert>
            <Scale className="h-4 w-4" />
            <AlertDescription>
              <strong>Legal Notice:</strong> This forensic analysis is provided for informational purposes. 
              For legal proceedings, consult with qualified digital forensics experts and legal counsel 
              regarding admissibility and chain of custody requirements.
            </AlertDescription>
          </Alert>
        </TabsContent>
      </Tabs>

      {/* Print-only Full Report */}
      <div className="hidden print:block space-y-6">
        {/* All content would be rendered here for printing */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold">File Analysis Details</h2>
          {reportData.files.map((file, index) => (
            <div key={index} className="border p-4 break-inside-avoid">
              <h3 className="font-medium mb-2">{file.file_name}</h3>
              <div className="grid grid-cols-3 gap-4 text-sm mb-2">
                <div>Risk Level: {file.risk_level}</div>
                <div>Authenticity: {file.authenticity_score}%</div>
                <div>Size: {(file.file_size / 1024).toFixed(1)} KB</div>
              </div>
              {file.forensic_findings.length > 0 && (
                <div>
                  <strong>Findings:</strong>
                  <ul className="list-disc list-inside text-sm mt-1">
                    {file.forensic_findings.map((finding, idx) => (
                      <li key={idx}>{finding}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-bold">Recommendations</h2>
          <ul className="space-y-2">
            {reportData.recommendations.map((rec, index) => (
              <li key={index} className="text-sm">• {rec}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}