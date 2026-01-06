import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
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
  RotateCcw,
  Activity,
  Search,
  Brain,
  Fingerprint,
  TrendingUp,
  PieChart,
  BarChart3,
  Zap,
  Target,
  AlertOctagon,
  Verified,
  XCircle,
} from 'lucide-react';
import { AuthenticityBadge } from './AuthenticityBadge';
import { cn } from '@/lib/utils';

export interface SteganographyAnalysis {
  detected: boolean;
  confidence: number;
  methodsChecked: string[];
  findings: string[];
  details?: string;
}

export interface ManipulationAnalysis {
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

export interface AIDetection {
  aiGenerated: boolean;
  confidence: number;
  modelHints: string[];
  detectionMethods: string[];
}

export interface ForensicAnalysisProps {
  steganography?: SteganographyAnalysis;
  manipulation?: ManipulationAnalysis;
  aiDetection?: AIDetection;
  authenticityScore?: number;
  onReanalyze?: () => void;
  className?: string;
}

export interface ForensicFindingCardProps {
  title: string;
  description: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high';
  icon?: React.ReactNode;
  details?: string;
  recommendations?: string[];
}

interface ForensicScoreGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const ForensicScoreGauge: React.FC<ForensicScoreGaugeProps> = ({
  score,
  size = 'md',
  showLabel = true,
}) => {
  const radius = size === 'sm' ? 30 : size === 'md' ? 45 : 60;
  const strokeWidth = size === 'sm' ? 4 : 6;
  const normalizedRadius = radius - strokeWidth * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDasharray = `${circumference} ${circumference}`;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500';
    if (score >= 60) return 'text-yellow-500';
    if (score >= 40) return 'text-orange-500';
    return 'text-red-500';
  };

  const getStrokeColor = (score: number) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    if (score >= 40) return '#f97316';
    return '#ef4444';
  };

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center',
        size === 'sm' && 'gap-1',
        size === 'md' && 'gap-2',
        size === 'lg' && 'gap-3'
      )}
    >
      <div className="relative">
        <svg
          height={radius * 2}
          width={radius * 2}
          className="transform -rotate-90"
        >
          <circle
            stroke="#374151"
            fill="transparent"
            strokeWidth={strokeWidth}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          <circle
            stroke={getStrokeColor(score)}
            fill="transparent"
            strokeWidth={strokeWidth}
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span
            className={cn(
              'font-bold',
              getScoreColor(score),
              size === 'sm' && 'text-sm',
              size === 'md' && 'text-lg',
              size === 'lg' && 'text-2xl'
            )}
          >
            {score}
          </span>
          <span
            className={cn(
              'text-gray-400',
              size === 'sm' && 'text-xs',
              size === 'md' && 'text-sm',
              size === 'lg' && 'text-base'
            )}
          >
            %
          </span>
        </div>
      </div>
      {showLabel && (
        <div
          className={cn(
            'text-center',
            size === 'sm' && 'text-xs',
            size === 'md' && 'text-sm',
            size === 'lg' && 'text-base'
          )}
        >
          <p className={cn('font-medium', getScoreColor(score))}>
            {score >= 80
              ? 'Authentic'
              : score >= 60
                ? 'Likely Authentic'
                : score >= 40
                  ? 'Questionable'
                  : 'Suspicious'}
          </p>
          <p className="text-gray-400 text-xs mt-1">Forensic Score</p>
        </div>
      )}
    </div>
  );
};

interface AnalysisConfidenceBarProps {
  label: string;
  confidence: number;
  color?: 'blue' | 'green' | 'red' | 'yellow';
  icon?: React.ReactNode;
}

const AnalysisConfidenceBar: React.FC<AnalysisConfidenceBarProps> = ({
  label,
  confidence,
  color = 'blue',
  icon,
}) => {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-emerald-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium text-gray-200">{label}</span>
        </div>
        <span className="text-sm text-gray-400">{confidence}%</span>
      </div>
      <Progress value={confidence} className="h-2" />
    </div>
  );
};

const ForensicFindingCard: React.FC<ForensicFindingCardProps> = ({
  title,
  description,
  severity,
  confidence,
  icon,
}) => {
  const severityConfig = {
    low: {
      border: 'border-slate-500/30',
      bg: 'bg-slate-500/10',
      text: 'text-slate-300',
      badge: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    },
    medium: {
      border: 'border-yellow-500/30',
      bg: 'bg-yellow-500/10',
      text: 'text-yellow-400',
      badge: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    },
    high: {
      border: 'border-red-500/30',
      bg: 'bg-red-500/10',
      text: 'text-red-400',
      badge: 'bg-red-500/20 text-red-400 border-red-500/30',
    },
  };

  const config = severityConfig[severity];

  return (
    <div className={cn('p-4 rounded-lg border', config.border, config.bg)}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon}
          <h5 className={cn('font-medium', config.text)}>{title}</h5>
        </div>
        <Badge className={cn('text-xs', config.badge)}>
          {severity.toUpperCase()}
        </Badge>
      </div>
      <p className="text-sm text-gray-300 mb-2">{description}</p>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">Confidence: {confidence}%</span>
        <div className="w-24">
          <Progress value={confidence} className="h-1" />
        </div>
      </div>
    </div>
  );
};

export const ForensicAnalysis: React.FC<ForensicAnalysisProps> = ({
  steganography,
  manipulation,
  aiDetection,
  authenticityScore = 0,
  onReanalyze,
  className,
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isExpanded, setIsExpanded] = useState(false);

  const hasAnalysisData = !!(steganography || manipulation || aiDetection);

  // Calculate overall forensic metrics
  const totalAnalyses = [steganography, manipulation, aiDetection].filter(
    Boolean
  ).length;
  const suspiciousFindings = [
    steganography?.detected ? 1 : 0,
    manipulation?.detected ? 1 : 0,
    aiDetection?.aiGenerated ? 1 : 0,
  ].reduce((a, b) => a + b, 0);

  const getAuthenticityIcon = (score: number) => {
    if (score >= 80) return <Verified className="w-5 h-5 text-emerald-500" />;
    if (score >= 60) return <Shield className="w-5 h-5 text-yellow-500" />;
    if (score >= 40)
      return <AlertTriangle className="w-5 h-5 text-orange-500" />;
    return <XCircle className="w-5 h-5 text-red-500" />;
  };

  if (!hasAnalysisData) {
    return (
      <Card className={cn('bg-card border-white/10', className)}>
        <CardContent className="py-8 text-center">
          <Fingerprint className="w-12 h-12 mx-auto mb-4 text-slate-500" />
          <p className="text-slate-300">No forensic analysis data available</p>
          <p className="text-xs text-slate-500 mt-2">
            Forensic analysis requires Advanced or Enterprise tier
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn('bg-card border-white/10', className)}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-white">
              <Fingerprint className="w-5 h-5 text-primary" />
              Forensic Analysis
            </CardTitle>
            <p className="text-sm text-slate-300 mt-1">
              Advanced authenticity and manipulation detection
            </p>
          </div>
          <div className="flex items-center gap-2">
            <ForensicScoreGauge score={authenticityScore} size="sm" />
            {onReanalyze && (
              <Button
                variant="outline"
                size="sm"
                onClick={onReanalyze}
                className="gap-2"
              >
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
            <TabsTrigger value="overview" className="text-xs">
              <PieChart className="w-3 h-3 mr-1" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="steganography" className="text-xs">
              <Search className="w-3 h-3 mr-1" />
              Steganography
            </TabsTrigger>
            <TabsTrigger value="manipulation" className="text-xs">
              <Activity className="w-3 h-3 mr-1" />
              Manipulation
            </TabsTrigger>
            <TabsTrigger value="ai" className="text-xs">
              <Brain className="w-3 h-3 mr-1" />
              AI Detection
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="mt-6 space-y-6">
            {/* Forensic Score Dashboard */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <Card className="bg-muted/20 border-white/10 h-full">
                  <CardContent className="p-6">
                    <div className="flex flex-col items-center justify-center h-full">
                      <ForensicScoreGauge score={authenticityScore} size="lg" />
                      <div className="mt-4 text-center">
                        <div className="flex items-center justify-center gap-2 mb-2">
                          {getAuthenticityIcon(authenticityScore)}
                          <span className="text-sm font-medium text-white">
                            {authenticityScore >= 80
                              ? 'Authentic'
                              : authenticityScore >= 60
                                ? 'Likely Authentic'
                                : authenticityScore >= 40
                                  ? 'Questionable'
                                  : 'Suspicious'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400">
                          Based on {totalAnalyses} forensic analyses
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="lg:col-span-2 space-y-4">
                <AnalysisConfidenceBar
                  label="Overall Authenticity"
                  confidence={authenticityScore}
                  color={
                    authenticityScore >= 80
                      ? 'green'
                      : authenticityScore >= 60
                        ? 'yellow'
                        : 'red'
                  }
                  icon={<Shield className="w-4 h-4 text-primary" />}
                />

                {steganography && (
                  <AnalysisConfidenceBar
                    label="Steganography Analysis"
                    confidence={steganography.confidence}
                    color={steganography.detected ? 'red' : 'green'}
                    icon={<Search className="w-4 h-4 text-blue-500" />}
                  />
                )}

                {manipulation && (
                  <AnalysisConfidenceBar
                    label="Manipulation Detection"
                    confidence={manipulation.confidence}
                    color={manipulation.detected ? 'red' : 'green'}
                    icon={<Activity className="w-4 h-4 text-orange-500" />}
                  />
                )}

                {aiDetection && (
                  <AnalysisConfidenceBar
                    label="AI Generation Detection"
                    confidence={aiDetection.confidence}
                    color={aiDetection.aiGenerated ? 'red' : 'green'}
                    icon={<Brain className="w-4 h-4 text-purple-500" />}
                  />
                )}
              </div>
            </div>

            {/* Risk Assessment Summary */}
            <Card className="bg-muted/20 border-white/10">
              <CardContent className="p-6">
                <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                  <Target className="w-4 h-4 text-primary" />
                  Risk Assessment Summary
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-slate-500/10 rounded-lg border border-slate-500/30">
                    <div className="text-2xl font-bold text-slate-300 mb-1">
                      {totalAnalyses}
                    </div>
                    <p className="text-xs text-slate-400">Total Analyses</p>
                  </div>

                  <div
                    className={cn(
                      'text-center p-4 rounded-lg border',
                      suspiciousFindings > 0
                        ? 'bg-red-500/10 border-red-500/30'
                        : 'bg-emerald-500/10 border-emerald-500/30'
                    )}
                  >
                    <div
                      className={cn(
                        'text-2xl font-bold mb-1',
                        suspiciousFindings > 0
                          ? 'text-red-400'
                          : 'text-emerald-400'
                      )}
                    >
                      {suspiciousFindings}
                    </div>
                    <p
                      className={cn(
                        'text-xs',
                        suspiciousFindings > 0
                          ? 'text-red-300'
                          : 'text-emerald-300'
                      )}
                    >
                      Suspicious Findings
                    </p>
                  </div>

                  <div className="text-center p-4 bg-primary/10 rounded-lg border border-primary/30">
                    <div className="text-2xl font-bold text-primary mb-1">
                      {Math.round(
                        (1 - suspiciousFindings / Math.max(1, totalAnalyses)) *
                          100
                      )}
                      %
                    </div>
                    <p className="text-xs text-primary/70">Trust Score</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Detailed Findings */}
            {isExpanded && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-white flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-primary" />
                    Detailed Findings
                  </h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsExpanded(false)}
                    className="text-xs"
                  >
                    Hide Details
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {steganography?.findings.map((finding, i) => (
                    <ForensicFindingCard
                      key={`stego-${i}`}
                      title="Steganography Finding"
                      description={finding}
                      severity={steganography.detected ? 'high' : 'low'}
                      confidence={steganography.confidence}
                      icon={<Search className="w-4 h-4 text-blue-500" />}
                    />
                  ))}

                  {manipulation?.indicators.map((indicator, i) => (
                    <ForensicFindingCard
                      key={`manip-${i}`}
                      title={indicator.type}
                      description={indicator.description}
                      severity={indicator.severity}
                      confidence={indicator.confidence}
                      icon={<Activity className="w-4 h-4 text-orange-500" />}
                    />
                  ))}
                </div>
              </div>
            )}

            {!isExpanded && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsExpanded(true)}
                className="w-full gap-2"
              >
                <BarChart3 className="w-4 h-4" />
                Show Detailed Findings
              </Button>
            )}
          </TabsContent>

          {/* Steganography Tab */}
          <TabsContent value="steganography" className="mt-6 space-y-6">
            {steganography ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <AuthenticityBadge
                      score={
                        steganography.detected
                          ? Math.max(10, 100 - steganography.confidence)
                          : steganography.confidence
                      }
                      label={
                        steganography.detected
                          ? 'Hidden Data Found'
                          : 'No Hidden Data'
                      }
                    />
                    <span className="text-sm text-slate-300">
                      {steganography.confidence}% confidence
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-500" />
                    <span className="text-xs text-slate-400">
                      {steganography.methodsChecked.length} methods analyzed
                    </span>
                  </div>
                </div>

                {steganography.methodsChecked.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <Search className="w-4 h-4 text-primary" />
                      Methods Analyzed
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {steganography.methodsChecked.map((method, i) => (
                        <Badge
                          key={i}
                          variant="outline"
                          className="text-xs border-white/20 justify-center"
                        >
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {steganography.findings.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-primary" />
                      Findings
                    </h4>
                    <div className="space-y-3">
                      {steganography.findings.map((finding, i) => (
                        <ForensicFindingCard
                          key={i}
                          title="Steganography Detection"
                          description={finding}
                          severity={steganography.detected ? 'high' : 'low'}
                          confidence={steganography.confidence}
                          icon={<Search className="w-4 h-4 text-blue-500" />}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {steganography.details && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-primary" />
                      Analysis Details
                    </h4>
                    <div className="p-4 bg-muted/30 rounded-lg border border-white/10">
                      <p className="text-sm text-slate-200 leading-relaxed">
                        {steganography.details}
                      </p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <Search className="w-12 h-12 mx-auto mb-4 text-slate-500" />
                <p className="text-slate-400">
                  Steganography analysis not available
                </p>
              </div>
            )}
          </TabsContent>

          {/* Manipulation Tab */}
          <TabsContent value="manipulation" className="mt-6 space-y-6">
            {manipulation ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <AuthenticityBadge
                      score={
                        manipulation.detected
                          ? Math.max(10, 100 - manipulation.confidence)
                          : manipulation.confidence
                      }
                      label={
                        manipulation.detected
                          ? 'Manipulation Detected'
                          : 'No Manipulation'
                      }
                    />
                    <span className="text-sm text-slate-300">
                      {manipulation.confidence}% confidence
                    </span>
                  </div>
                  {manipulation.originalityScore !== undefined && (
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-green-500" />
                      <span className="text-xs text-slate-400">
                        Originality: {manipulation.originalityScore}%
                      </span>
                    </div>
                  )}
                </div>

                {manipulation.originalityScore !== undefined && (
                  <div className="p-4 bg-muted/30 rounded-lg border border-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-green-500" />
                        <span className="text-slate-300">
                          Originality Score:
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={manipulation.originalityScore}
                          className="w-32 h-2"
                        />
                        <span className="font-bold text-white">
                          {manipulation.originalityScore}%
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {manipulation.indicators.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <Activity className="w-4 h-4 text-primary" />
                      Manipulation Indicators
                    </h4>
                    <div className="space-y-4">
                      {manipulation.indicators.map((indicator, i) => (
                        <ForensicFindingCard
                          key={i}
                          title={indicator.type}
                          description={indicator.description}
                          severity={indicator.severity}
                          confidence={indicator.confidence}
                          icon={
                            <Activity className="w-4 h-4 text-orange-500" />
                          }
                        />
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <Activity className="w-12 h-12 mx-auto mb-4 text-slate-500" />
                <p className="text-slate-400">
                  Manipulation detection not available
                </p>
              </div>
            )}
          </TabsContent>

          {/* AI Detection Tab */}
          <TabsContent value="ai" className="mt-6 space-y-6">
            {aiDetection ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <AuthenticityBadge
                      score={
                        aiDetection.aiGenerated
                          ? Math.max(10, 100 - aiDetection.confidence)
                          : aiDetection.confidence
                      }
                      label={
                        aiDetection.aiGenerated
                          ? 'AI Generated'
                          : 'Likely Original'
                      }
                    />
                    <span className="text-sm text-slate-300">
                      {aiDetection.confidence}% confidence
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-purple-500" />
                    <span className="text-xs text-slate-400">
                      {aiDetection.detectionMethods.length} methods used
                    </span>
                  </div>
                </div>

                {aiDetection.detectionMethods.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <Brain className="w-4 h-4 text-primary" />
                      Detection Methods
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {aiDetection.detectionMethods.map((method, i) => (
                        <Badge
                          key={i}
                          variant="outline"
                          className="text-xs border-white/20 justify-center"
                        >
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {aiDetection.modelHints.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                      <Zap className="w-4 h-4 text-primary" />
                      Model Indicators
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {aiDetection.modelHints.map((hint, i) => (
                        <Badge
                          key={i}
                          variant="outline"
                          className="text-xs border-purple-500/30 bg-purple-500/10 text-purple-400"
                        >
                          {hint}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-2 pt-4">
                  <Button variant="outline" className="gap-2">
                    <Download className="w-4 h-4" />
                    Export Report
                  </Button>
                  <Button variant="outline" className="gap-2">
                    <FileText className="w-4 h-4" />
                    View Technical Details
                  </Button>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <Brain className="w-12 h-12 mx-auto mb-4 text-slate-500" />
                <p className="text-slate-400">AI detection not available</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
