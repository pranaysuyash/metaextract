import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Eye, 
  FileText, 
  Camera, 
  Hash,
  Download,
  RotateCcw
} from 'lucide-react';
import { AuthenticityBadge } from './AuthenticityBadge';

interface SteganographyAnalysis {
  detected: boolean;
  confidence: number;
  methodsChecked: string[];
  findings: string[];
  details?: string;
}

interface ManipulationAnalysis {
  detected: boolean;
  confidence: number;
  indicators: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high';
    description: string;
    confidence: number;
  }>;
  originalityScore?: number;
}

interface AIDetection {
  aiGenerated: boolean;
  confidence: number;
  modelHints: string[];
  detectionMethods: string[];
}

interface ForensicAnalysisProps {
  steganography?: SteganographyAnalysis;
  manipulation?: ManipulationAnalysis;
  aiDetection?: AIDetection;
  authenticityScore?: number;
  onReanalyze?: () => void;
}

export const ForensicAnalysis: React.FC<ForensicAnalysisProps> = ({ 
  steganography, 
  manipulation, 
  aiDetection, 
  authenticityScore = 0,
  onReanalyze
}) => {
  const [activeTab, setActiveTab] = useState('overview');

  const hasAnalysisData = !!(steganography || manipulation || aiDetection);

  if (!hasAnalysisData) {
    return (
      <Card className="bg-card border-white/10">
        <CardContent className="py-8 text-center">
          <Shield className="w-12 h-12 mx-auto mb-4 text-slate-500" />
          <p className="text-slate-300">No forensic analysis data available</p>
          <p className="text-xs text-slate-500 mt-2">
            Forensic analysis requires Advanced or Enterprise tier
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card border-white/10">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-white">
              <Shield className="w-5 h-5 text-primary" />
              Forensic Analysis
            </CardTitle>
            <p className="text-sm text-slate-300 mt-1">
              Advanced authenticity and manipulation detection
            </p>
          </div>
          <div className="flex items-center gap-2">
            <AuthenticityBadge score={authenticityScore} />
            {onReanalyze && (
              <Button variant="outline" size="sm" onClick={onReanalyze} className="gap-2">
                <RotateCcw className="w-4 h-4" />
                Re-analyze
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 bg-muted/50">
            <TabsTrigger value="overview" className="text-xs">Overview</TabsTrigger>
            <TabsTrigger value="steganography" className="text-xs">Steganography</TabsTrigger>
            <TabsTrigger value="manipulation" className="text-xs">Manipulation</TabsTrigger>
            <TabsTrigger value="ai" className="text-xs">AI Detection</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="mt-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-muted/20 border-white/10">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Eye className="w-4 h-4 text-primary" />
                    <h3 className="font-semibold text-white">Authenticity</h3>
                  </div>
                  <div className="text-2xl font-bold text-white mb-1">
                    {authenticityScore}%
                  </div>
                  <p className="text-xs text-slate-300">Overall confidence score</p>
                </CardContent>
              </Card>

              <Card className="bg-muted/20 border-white/10">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    <h3 className="font-semibold text-white">Manipulation</h3>
                  </div>
                  <div className="text-2xl font-bold text-white mb-1">
                    {manipulation ? (manipulation.detected ? 'Yes' : 'No') : 'N/A'}
                  </div>
                  <p className="text-xs text-slate-300">
                    {manipulation ? `${manipulation.confidence}% confidence` : 'Not analyzed'}
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-muted/20 border-white/10">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Camera className="w-4 h-4 text-purple-500" />
                    <h3 className="font-semibold text-white">AI Generated</h3>
                  </div>
                  <div className="text-2xl font-bold text-white mb-1">
                    {aiDetection ? (aiDetection.aiGenerated ? 'Yes' : 'No') : 'N/A'}
                  </div>
                  <p className="text-xs text-slate-300">
                    {aiDetection ? `${aiDetection.confidence}% confidence` : 'Not analyzed'}
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card className="bg-muted/20 border-white/10">
              <CardContent className="p-4">
                <h3 className="font-semibold text-white mb-3">Analysis Summary</h3>
                <div className="space-y-3">
                  {steganography && (
                    <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                      <span className="text-slate-200">Steganography Detection</span>
                      <Badge variant={steganography.detected ? 'destructive' : 'secondary'}>
                        {steganography.detected ? 'Found' : 'None Detected'}
                      </Badge>
                    </div>
                  )}
                  
                  {manipulation && (
                    <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                      <span className="text-slate-200">Manipulation Analysis</span>
                      <Badge variant={manipulation.detected ? 'destructive' : 'secondary'}>
                        {manipulation.detected ? 'Detected' : 'None Found'}
                      </Badge>
                    </div>
                  )}
                  
                  {aiDetection && (
                    <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                      <span className="text-slate-200">AI Generation Detection</span>
                      <Badge variant={aiDetection.aiGenerated ? 'destructive' : 'secondary'}>
                        {aiDetection.aiGenerated ? 'AI Generated' : 'Likely Original'}
                      </Badge>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Steganography Tab */}
          <TabsContent value="steganography" className="mt-4 space-y-4">
            {steganography ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AuthenticityBadge 
                      score={steganography.detected ? Math.max(10, 100 - steganography.confidence) : steganography.confidence} 
                      label={steganography.detected ? "Hidden Data Found" : "No Hidden Data"} 
                    />
                    <span className="text-sm text-slate-300">
                      {steganography.confidence}% confidence
                    </span>
                  </div>
                </div>
                
                {steganography.methodsChecked.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-2">Methods Analyzed</h4>
                    <div className="flex flex-wrap gap-2">
                      {steganography.methodsChecked.map((method, i) => (
                        <Badge key={i} variant="outline" className="text-xs border-white/20">
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {steganography.findings.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-2">Findings</h4>
                    <div className="space-y-2">
                      {steganography.findings.map((finding, i) => (
                        <div key={i} className="p-3 bg-muted/30 rounded space-y-1">
                          <div className="flex items-start gap-2">
                            <AlertTriangle className="w-4 h-4 mt-0.5 text-primary shrink-0" />
                            <p className="text-sm text-slate-200">{finding}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {steganography.details && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-2">Analysis Details</h4>
                    <div className="p-3 bg-muted/30 rounded">
                      <p className="text-sm text-slate-200">{steganography.details}</p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p className="text-slate-500 text-sm">Steganography analysis not available</p>
            )}
          </TabsContent>

          {/* Manipulation Tab */}
          <TabsContent value="manipulation" className="mt-4 space-y-4">
            {manipulation ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AuthenticityBadge 
                      score={manipulation.detected ? Math.max(10, 100 - manipulation.confidence) : manipulation.confidence} 
                      label={manipulation.detected ? "Manipulation Detected" : "No Manipulation"} 
                    />
                    <span className="text-sm text-slate-300">
                      {manipulation.confidence}% confidence
                    </span>
                  </div>
                </div>
                
                {manipulation.originalityScore !== undefined && (
                  <div className="p-3 bg-muted/30 rounded">
                    <div className="flex justify-between">
                      <span className="text-slate-300">Originality Score:</span>
                      <span className="font-bold text-white">{manipulation.originalityScore}%</span>
                    </div>
                  </div>
                )}
                
                {manipulation.indicators.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-2">Manipulation Indicators</h4>
                    <div className="space-y-3">
                      {manipulation.indicators.map((indicator, i) => (
                        <div
                          key={i}
                          className={`p-3 rounded border ${
                            indicator.severity === 'high'
                              ? 'bg-red-500/10 border-red-500/30'
                              : indicator.severity === 'medium'
                              ? 'bg-yellow-500/10 border-yellow-500/30'
                              : 'bg-slate-500/10 border-slate-500/30'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <Badge
                              variant="outline"
                              className={`text-xs ${
                                indicator.severity === 'high'
                                  ? 'border-red-500 text-red-400'
                                  : indicator.severity === 'medium'
                                  ? 'border-yellow-500 text-yellow-400'
                                  : 'border-slate-500 text-slate-300'
                              }`}
                            >
                              {indicator.severity.toUpperCase()}
                            </Badge>
                            <span className="text-xs text-slate-300">
                              {indicator.confidence}% confidence
                            </span>
                          </div>
                          <h5 className="text-sm font-medium text-white">{indicator.type}</h5>
                          <p className="text-xs text-slate-300">{indicator.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p className="text-slate-500 text-sm">Manipulation detection not available</p>
            )}
          </TabsContent>

          {/* AI Detection Tab */}
          <TabsContent value="ai" className="mt-4 space-y-4">
            {aiDetection ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AuthenticityBadge 
                      score={aiDetection.aiGenerated ? Math.max(10, 100 - aiDetection.confidence) : aiDetection.confidence} 
                      label={aiDetection.aiGenerated ? "AI Generated" : "Likely Original"} 
                    />
                    <span className="text-sm text-slate-300">
                      {aiDetection.confidence}% confidence
                    </span>
                  </div>
                </div>
                
                {aiDetection.detectionMethods.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-2">Detection Methods</h4>
                    <div className="flex flex-wrap gap-2">
                      {aiDetection.detectionMethods.map((method, i) => (
                        <Badge key={i} variant="outline" className="text-xs border-white/20">
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {aiDetection.modelHints.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-2">Model Indicators</h4>
                    <div className="flex flex-wrap gap-2">
                      {aiDetection.modelHints.map((hint, i) => (
                        <Badge key={i} variant="outline" className="text-xs border-white/20 bg-purple-500/10 text-purple-400">
                          {hint}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex gap-2 mt-4">
                  <Button variant="outline" className="gap-2">
                    <Download className="w-4 h-4" />
                    Export Report
                  </Button>
                  <Button variant="outline" className="gap-2">
                    <FileText className="w-4 h-4" />
                    View Details
                  </Button>
                </div>
              </>
            ) : (
              <p className="text-slate-500 text-sm">AI detection not available</p>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};