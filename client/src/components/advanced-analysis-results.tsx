import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Zap,
  Clock,
  FileText,
  TrendingUp
} from 'lucide-react';

interface AdvancedAnalysisData {
  enabled: boolean;
  processing_time_ms: number;
  modules_run: string[];
  forensic_score: number;
  authenticity_assessment: 'authentic' | 'questionable' | 'suspicious';
}

interface SteganographyAnalysis {
  suspicious_score: number;
  methods_detected: string[];
  entropy_analysis?: {
    score: number;
    suspicious_regions: number;
  };
  lsb_analysis?: {
    suspicious_channels: string[];
    confidence: number;
  };
}

interface ManipulationDetection {
  manipulation_probability: number;
  indicators: string[];
  jpeg_analysis?: {
    compression_artifacts: boolean;
    recompression_detected: boolean;
  };
  noise_analysis?: {
    inconsistent_regions: number;
    confidence: number;
  };
}

interface AIDetection {
  ai_probability: number;
  detection_methods: string[];
  confidence: number;
  suspicious_patterns: string[];
}

interface AdvancedAnalysisResultsProps {
  advancedAnalysis: AdvancedAnalysisData;
  steganographyAnalysis?: SteganographyAnalysis;
  manipulationDetection?: ManipulationDetection;
  aiDetection?: AIDetection;
}

export function AdvancedAnalysisResults({
  advancedAnalysis,
  steganographyAnalysis,
  manipulationDetection,
  aiDetection
}: AdvancedAnalysisResultsProps) {
  if (!advancedAnalysis?.enabled) {
    return (
      <Card className="border-amber-200 bg-amber-50">
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-amber-700">
            <Shield className="h-5 w-5" />
            <span className="font-medium">Advanced Analysis Not Available</span>
          </div>
          <p className="text-sm text-amber-600 mt-2">
            Upgrade to Professional or higher tier for advanced forensic analysis
          </p>
        </CardContent>
      </Card>
    );
  }

  const getAuthenticityIcon = (assessment: string) => {
    switch (assessment) {
      case 'authentic':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'questionable':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'suspicious':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Shield className="h-5 w-5 text-gray-600" />;
    }
  };

  const getAuthenticityColor = (assessment: string) => {
    switch (assessment) {
      case 'authentic':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'questionable':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'suspicious':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Overall Assessment */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-900">
            <Shield className="h-6 w-6" />
            Advanced Forensic Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Forensic Score */}
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                <span className="font-medium text-gray-700">Forensic Score</span>
              </div>
              <div className={`text-3xl font-bold ${getScoreColor(advancedAnalysis.forensic_score)}`}>
                {advancedAnalysis.forensic_score}
              </div>
              <Progress
                value={advancedAnalysis.forensic_score}
                className="mt-2 h-2"
              />
            </div>

            {/* Authenticity Assessment */}
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                {getAuthenticityIcon(advancedAnalysis.authenticity_assessment)}
                <span className="font-medium text-gray-700">Authenticity</span>
              </div>
              <Badge className={getAuthenticityColor(advancedAnalysis.authenticity_assessment)}>
                {(advancedAnalysis.authenticity_assessment || 'unknown').toUpperCase()}
              </Badge>
            </div>

            {/* Processing Time */}
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Clock className="h-5 w-5 text-gray-600" />
                <span className="font-medium text-gray-700">Analysis Time</span>
              </div>
              <div className="text-lg font-semibold text-gray-800">
                {(advancedAnalysis.processing_time_ms / 1000).toFixed(1)}s
              </div>
            </div>
          </div>

          {/* Modules Run */}
          <div className="mt-4">
            <h4 className="font-medium text-gray-700 mb-2">Analysis Modules</h4>
            <div className="flex flex-wrap gap-2">
              {advancedAnalysis.modules_run.map((module) => (
                <Badge key={module} variant="outline" className="text-xs">
                  {module.replace('_', ' ').toUpperCase()}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Steganography Analysis */}
      {steganographyAnalysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Steganography Detection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Suspicious Score</span>
                  <span className={`font-bold ${getScoreColor(100 - steganographyAnalysis.suspicious_score * 100)}`}>
                    {(steganographyAnalysis.suspicious_score * 100).toFixed(1)}%
                  </span>
                </div>
                <Progress
                  value={steganographyAnalysis.suspicious_score * 100}
                  className="h-2"
                />
              </div>

              <div>
                <span className="font-medium">Methods Detected</span>
                <div className="mt-2">
                  {steganographyAnalysis.methods_detected.length > 0 ? (
                    steganographyAnalysis.methods_detected.map((method, index) => (
                      <Badge key={index} variant="destructive" className="mr-1 mb-1">
                        {method}
                      </Badge>
                    ))
                  ) : (
                    <Badge variant="outline" className="text-green-700 border-green-300">
                      No methods detected
                    </Badge>
                  )}
                </div>
              </div>
            </div>

            {steganographyAnalysis.entropy_analysis && (
              <Alert className="mt-4">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Entropy analysis detected {steganographyAnalysis.entropy_analysis.suspicious_regions} suspicious regions
                  (Score: {steganographyAnalysis.entropy_analysis.score.toFixed(2)})
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Manipulation Detection */}
      {manipulationDetection && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Manipulation Detection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Manipulation Probability</span>
                  <span className={`font-bold ${getScoreColor(100 - manipulationDetection.manipulation_probability * 100)}`}>
                    {(manipulationDetection.manipulation_probability * 100).toFixed(1)}%
                  </span>
                </div>
                <Progress
                  value={manipulationDetection.manipulation_probability * 100}
                  className="h-2"
                />
              </div>

              <div>
                <span className="font-medium">Indicators Found</span>
                <div className="mt-2">
                  {manipulationDetection.indicators.length > 0 ? (
                    manipulationDetection.indicators.map((indicator, index) => (
                      <Badge key={index} variant="destructive" className="mr-1 mb-1 text-xs">
                        {indicator}
                      </Badge>
                    ))
                  ) : (
                    <Badge variant="outline" className="text-green-700 border-green-300">
                      No indicators found
                    </Badge>
                  )}
                </div>
              </div>
            </div>

            {manipulationDetection.jpeg_analysis && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <h5 className="font-medium mb-2">JPEG Analysis</h5>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    {manipulationDetection.jpeg_analysis.compression_artifacts ? (
                      <XCircle className="h-4 w-4 text-red-500" />
                    ) : (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    )}
                    <span>Compression Artifacts</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {manipulationDetection.jpeg_analysis.recompression_detected ? (
                      <XCircle className="h-4 w-4 text-red-500" />
                    ) : (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    )}
                    <span>Recompression Detected</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* AI Detection */}
      {aiDetection && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              AI Content Detection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">AI Probability</span>
                  <span className={`font-bold ${getScoreColor(100 - aiDetection.ai_probability * 100)}`}>
                    {(aiDetection.ai_probability * 100).toFixed(1)}%
                  </span>
                </div>
                <Progress
                  value={aiDetection.ai_probability * 100}
                  className="h-2"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Confidence</span>
                  <span className="font-bold text-gray-700">
                    {(aiDetection.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <Progress
                  value={aiDetection.confidence * 100}
                  className="h-2"
                />
              </div>
            </div>

            <div className="mt-4">
              <span className="font-medium">Detection Methods</span>
              <div className="mt-2 flex flex-wrap gap-1">
                {aiDetection.detection_methods.map((method, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {method}
                  </Badge>
                ))}
              </div>
            </div>

            {aiDetection.suspicious_patterns.length > 0 && (
              <Alert className="mt-4">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Suspicious patterns detected: {aiDetection.suspicious_patterns.join(', ')}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Summary Alert */}
      {advancedAnalysis.forensic_score < 50 && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>Forensic Alert:</strong> This file shows multiple indicators of potential manipulation or artificial generation.
            Further investigation is recommended for legal or professional use.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}