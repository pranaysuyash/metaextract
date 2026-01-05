// client/src/components/viz/ManipulationDashboard.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  ShieldAlert,
  ShieldCheck,
  Eye,
  Zap,
  FileWarning,
  Activity,
  Radar,
  Cpu,
  Search,
} from 'lucide-react';

interface ManipulationDetection {
  manipulation_probability?: number;
  indicators?: string[];
  jpeg_analysis?: {
    compression_artifacts?: boolean;
    recompression_detected?: boolean;
  };
  noise_analysis?: {
    inconsistent_regions?: number;
    confidence?: number;
  };
}

interface SteganographyAnalysis {
  suspicious_score?: number;
  methods_detected?: string[];
  entropy_analysis?: {
    score?: number;
    suspicious_regions?: number;
  };
  lsb_analysis?: {
    suspicious_channels?: string[];
    confidence?: number;
  };
}

interface AIDetection {
  ai_probability?: number;
  detection_methods?: string[];
  confidence?: number;
  suspicious_patterns?: string[];
}

interface ManipulationDashboardProps {
  manipulation?: ManipulationDetection;
  steganography?: SteganographyAnalysis;
  ai_detection?: AIDetection;
}

interface AnalysisCard {
  title: string;
  score: number;
  status: 'safe' | 'suspicious' | 'warning';
  description: string;
  details: Record<string, any>;
  icon: React.ReactNode;
  color: string;
}

function getStatusColor(status: 'safe' | 'suspicious' | 'warning'): string {
  switch (status) {
    case 'safe':
      return 'text-green-600';
    case 'suspicious':
      return 'text-amber-600';
    case 'warning':
      return 'text-red-600';
  }
}

function getStatusBg(status: 'safe' | 'suspicious' | 'warning'): string {
  switch (status) {
    case 'safe':
      return 'bg-green-100 text-green-800';
    case 'suspicious':
      return 'bg-amber-100 text-amber-800';
    case 'warning':
      return 'bg-red-100 text-red-800';
  }
}

function getProbabilityStatus(
  probability: number | undefined
): 'safe' | 'suspicious' | 'warning' {
  if (!probability) return 'safe';
  if (probability < 30) return 'safe';
  if (probability < 70) return 'suspicious';
  return 'warning';
}

export function ManipulationDashboard({
  manipulation,
  steganography,
  ai_detection,
}: ManipulationDashboardProps) {
  const analysisCards: AnalysisCard[] = [
    {
      title: 'Manipulation Detection',
      score: manipulation?.manipulation_probability || 0,
      status: getProbabilityStatus(manipulation?.manipulation_probability),
      description: 'Analysis of editing artifacts and inconsistencies',
      details: {
        'Compression artifacts': manipulation?.jpeg_analysis
          ?.compression_artifacts
          ? 'Detected'
          : 'None',
        Recompression: manipulation?.jpeg_analysis?.recompression_detected
          ? 'Detected'
          : 'Clean',
        'Inconsistent regions':
          manipulation?.noise_analysis?.inconsistent_regions || 0,
        Confidence: `${manipulation?.noise_analysis?.confidence || 0}%`,
      },
      icon: <FileWarning className="w-5 h-5" />,
      color: 'text-orange-600',
    },
    {
      title: 'Steganography',
      score: steganography?.suspicious_score || 0,
      status: getProbabilityStatus(steganography?.suspicious_score),
      description: 'Hidden data detection analysis',
      details: {
        'Methods found': steganography?.methods_detected?.length || 0,
        'Entropy score': steganography?.entropy_analysis?.score || 0,
        'Suspicious regions':
          steganography?.entropy_analysis?.suspicious_regions || 0,
        'LSB analysis': steganography?.lsb_analysis?.confidence || 0,
      },
      icon: <Radar className="w-5 h-5" />,
      color: 'text-purple-600',
    },
    {
      title: 'AI Generation Detection',
      score: ai_detection?.ai_probability || 0,
      status: getProbabilityStatus(ai_detection?.ai_probability),
      description: 'AI-generated content probability',
      details: {
        'Detection methods': ai_detection?.detection_methods?.length || 0,
        Confidence: `${ai_detection?.confidence || 0}%`,
        'Patterns found': ai_detection?.suspicious_patterns?.length || 0,
      },
      icon: <Cpu className="w-5 h-5" />,
      color: 'text-blue-600',
    },
  ];

  const overallScore = Math.round(
    analysisCards.reduce((acc, card) => acc + card.score, 0) /
      analysisCards.length
  );

  const overallStatus = getProbabilityStatus(overallScore);

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <Eye className="w-5 h-5" />
          Manipulation Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Overall Assessment */}
        <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-muted/50 to-muted/30">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {overallStatus === 'safe' ? (
                <ShieldCheck className="w-6 h-6 text-green-600" />
              ) : overallStatus === 'suspicious' ? (
                <ShieldAlert className="w-6 h-6 text-amber-600" />
              ) : (
                <ShieldAlert className="w-6 h-6 text-red-600" />
              )}
              <div>
                <div className="font-medium">Overall Assessment</div>
                <div className="text-sm text-muted-foreground">
                  {overallStatus === 'safe'
                    ? 'No manipulation detected'
                    : overallStatus === 'suspicious'
                      ? 'Some anomalies detected'
                      : 'High manipulation probability'}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div
                className={`text-2xl font-bold ${getStatusColor(overallStatus)}`}
              >
                {overallScore}%
              </div>
              <div className="text-xs text-muted-foreground">Risk Score</div>
            </div>
          </div>
          <Progress value={overallScore} className="h-2" />
        </div>

        {/* Analysis Cards */}
        <div className="space-y-4">
          {analysisCards.map(card => (
            <div
              key={card.title}
              className={`p-4 rounded-lg border ${
                card.status === 'safe'
                  ? 'border-green-200 bg-green-50/30'
                  : card.status === 'suspicious'
                    ? 'border-amber-200 bg-amber-50/30'
                    : 'border-red-200 bg-red-50/30'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={card.color}>{card.icon}</div>
                  <div>
                    <div className="font-medium">{card.title}</div>
                    <div className="text-xs text-muted-foreground">
                      {card.description}
                    </div>
                  </div>
                </div>
                <Badge className={getStatusBg(card.status)}>
                  {card.score}%
                </Badge>
              </div>

              {/* Mini progress bar */}
              <Progress value={card.score} className="h-1 mb-3" />

              {/* Details grid */}
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(card.details).map(([key, value]) => (
                  <div
                    key={key}
                    className="flex items-center gap-2 p-2 rounded bg-background/50"
                  >
                    <Activity className="w-3 h-3 text-muted-foreground" />
                    <div>
                      <div className="text-[10px] text-muted-foreground">
                        {key}
                      </div>
                      <div className="text-sm font-medium">
                        {typeof value === 'number'
                          ? value.toString()
                          : String(value)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Indicators list */}
              {card.title === 'Manipulation Detection' &&
                manipulation?.indicators &&
                manipulation.indicators.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <div className="text-xs text-muted-foreground mb-2">
                      Indicators found:
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {manipulation.indicators.map((indicator, i) => (
                        <Badge
                          key={`indicator-${i}`}
                          variant="outline"
                          className="text-xs"
                        >
                          {indicator}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

              {card.title === 'AI Generation Detection' &&
                ai_detection?.suspicious_patterns &&
                ai_detection.suspicious_patterns.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <div className="text-xs text-muted-foreground mb-2">
                      Suspicious patterns:
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {ai_detection.suspicious_patterns.map((pattern, i) => (
                        <Badge
                          key={`pattern-${i}`}
                          variant="outline"
                          className="text-xs"
                        >
                          {pattern}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
            </div>
          ))}
        </div>

        {/* Info note */}
        <div className="mt-4 p-3 rounded bg-muted/50 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <Search className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <p>
              This analysis is probabilistic and should be verified manually.
              Low confidence results may require additional forensic tools for
              confirmation.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
