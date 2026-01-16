import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Shield,
  Zap,
  Eye,
  Clock,
  GitCompare,
  FileText,
  Upload,
  CheckCircle,
  TrendingUp,
} from 'lucide-react';

import { AdvancedAnalysisResults } from './advanced-analysis-results';
import { ComparisonView } from './comparison-view';
import { TimelineVisualization } from './timeline-visualization';
import { ForensicReport } from './forensic-report';

interface AdvancedResultsIntegrationProps {
  // Standard metadata result
  metadata?: any;

  // Advanced analysis results
  advancedAnalysis?: any;
  comparisonResult?: any;
  timelineResult?: any;
  forensicReport?: any;

  // UI state
  tier: string;
  isProcessingAdvanced?: boolean;
  onUpgrade?: () => void;
  onRunAdvancedAnalysis?: () => void;
  onRunComparison?: (files: FileList) => void;
  onRunTimeline?: (files: FileList) => void;
  onGenerateReport?: (files: FileList) => void;
}

export function AdvancedResultsIntegration({
  metadata,
  advancedAnalysis,
  comparisonResult,
  timelineResult,
  forensicReport,
  tier,
  isProcessingAdvanced = false,
  onUpgrade,
  onRunAdvancedAnalysis,
  onRunComparison,
  onRunTimeline,
  onGenerateReport,
}: AdvancedResultsIntegrationProps) {
  const [activeTab, setActiveTab] = useState('standard');
  const [isProcessing, setIsProcessing] = useState(false);

  // DEV MODE: Always enable all features in development
  const isDev = import.meta.env.DEV;
  const canUseAdvanced = isDev || tier !== 'free';
  const canUseReports = isDev || tier === 'enterprise';

  const handleFileUpload = (action: 'comparison' | 'timeline' | 'report') => {
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = 'image/*,video/*,audio/*,.pdf';

    input.onchange = (e) => {
      const files = (e.target as HTMLInputElement).files;
      if (files && files.length > 0) {
        setIsProcessing(true);

        switch (action) {
          case 'comparison':
            onRunComparison?.(files);
            break;
          case 'timeline':
            onRunTimeline?.(files);
            break;
          case 'report':
            onGenerateReport?.(files);
            break;
        }

        // Simulate processing time
        setTimeout(() => setIsProcessing(false), 3000);
      }
    };

    input.click();
  };

  const getTabCount = () => {
    let count = 1; // Standard tab always available
    if (advancedAnalysis) count++;
    if (comparisonResult) count++;
    if (timelineResult) count++;
    if (forensicReport) count++;
    return count;
  };

  // Defensive derived values (API responses can be partial / evolving)
  const forensicScore =
    advancedAnalysis?.forensic_score ??
    advancedAnalysis?.advanced_analysis?.forensic_score ??
    null;

  const comparisonTotalFiles =
    comparisonResult?.total_files ??
    (Array.isArray(comparisonResult?.files)
      ? comparisonResult.files.length
      : null);

  const timelineEventsCount =
    timelineResult?.timeline?.events?.length ??
    (Array.isArray(timelineResult?.events) ? timelineResult.events.length : 0);

  const reportAssessmentRaw =
    forensicReport?.conclusions?.overall_assessment ??
    (forensicReport as any)?.overall_assessment ??
    null;

  const reportAssessment =
    reportAssessmentRaw == null ? null : String(reportAssessmentRaw);

  const hasTimeline = timelineEventsCount > 0;

  return (
    <div className='space-y-6'>
      {/* Advanced Features Header */}
      <Card className='border-purple-200 bg-purple-50'>
        <CardHeader>
          <CardTitle className='flex items-center gap-2 text-purple-900'>
            <Shield className='h-6 w-6' />
            Advanced Forensic Analysis Suite
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
            {/* Advanced Analysis */}
            <div className='text-center'>
              <div className='flex items-center justify-center mb-2'>
                <Eye className='h-8 w-8 text-blue-600' />
              </div>
              <h4 className='font-medium mb-1'>Advanced Analysis</h4>
              <p className='text-xs text-gray-600 mb-2'>
                Steganography, manipulation & AI detection
              </p>
              {canUseAdvanced ? (
                <Button
                  size='sm'
                  onClick={onRunAdvancedAnalysis}
                  disabled={isProcessing || isProcessingAdvanced || !metadata}
                  className='w-full'
                >
                  {isProcessingAdvanced ? (
                    <div className="flex items-center gap-2">
                      <Zap className="w-3 h-3 animate-pulse" />
                      Analyzing...
                    </div>
                  ) : (
                    advancedAnalysis ? 'Re-analyze' : 'Analyze'
                  )}
                </Button>
              ) : (
                <Button
                  size='sm'
                  variant='outline'
                  onClick={onUpgrade}
                  className='w-full'
                >
                  Upgrade
                </Button>
              )}
            </div>

            {/* Batch Comparison */}
            <div className='text-center'>
              <div className='flex items-center justify-center mb-2'>
                <GitCompare className='h-8 w-8 text-green-600' />
              </div>
              <h4 className='font-medium mb-1'>Batch Comparison</h4>
              <p className='text-xs text-gray-600 mb-2'>
                Compare metadata across multiple files
              </p>
              {canUseAdvanced ? (
                <Button
                  size='sm'
                  onClick={() => handleFileUpload('comparison')}
                  disabled={isProcessing}
                  className='w-full'
                >
                  <Upload className='h-4 w-4 mr-1' />
                  Compare
                </Button>
              ) : (
                <Button
                  size='sm'
                  variant='outline'
                  onClick={onUpgrade}
                  className='w-full'
                >
                  Upgrade
                </Button>
              )}
            </div>

            {/* Timeline Reconstruction */}
            <div className='text-center'>
              <div className='flex items-center justify-center mb-2'>
                <Clock className='h-8 w-8 text-orange-600' />
              </div>
              <h4 className='font-medium mb-1'>Timeline Analysis</h4>
              <p className='text-xs text-gray-600 mb-2'>
                Reconstruct chronological timeline
              </p>
              {canUseAdvanced ? (
                <Button
                  size='sm'
                  onClick={() => handleFileUpload('timeline')}
                  disabled={isProcessing}
                  className='w-full'
                >
                  <Upload className='h-4 w-4 mr-1' />
                  Timeline
                </Button>
              ) : (
                <Button
                  size='sm'
                  variant='outline'
                  onClick={onUpgrade}
                  className='w-full'
                >
                  Upgrade
                </Button>
              )}
            </div>

            {/* Forensic Report */}
            <div className='text-center'>
              <div className='flex items-center justify-center mb-2'>
                <FileText className='h-8 w-8 text-red-600' />
              </div>
              <h4 className='font-medium mb-1'>Forensic Report</h4>
              <p className='text-xs text-gray-600 mb-2'>
                Professional court-ready reports
              </p>
              {canUseReports ? (
                <Button
                  size='sm'
                  onClick={() => handleFileUpload('report')}
                  disabled={isProcessing}
                  className='w-full'
                >
                  <Upload className='h-4 w-4 mr-1' />
                  Generate
                </Button>
              ) : (
                <Button
                  size='sm'
                  variant='outline'
                  onClick={onUpgrade}
                  className='w-full'
                >
                  Enterprise
                </Button>
              )}
            </div>
          </div>

          {/* Processing Indicator */}
          {isProcessing && (
            <Alert className='mt-4 border-blue-200 bg-blue-50'>
              <Zap className='h-4 w-4 text-blue-600 animate-pulse' />
              <AlertDescription className='text-blue-800'>
                Processing advanced analysis... This may take up to 5 minutes
                for comprehensive forensic analysis.
              </AlertDescription>
            </Alert>
          )}

          {/* Tier Information */}
          <div className='mt-4 flex items-center justify-between'>
            <div className='flex items-center gap-2'>
              <Badge variant='outline' className='capitalize'>
                {tier} Tier
              </Badge>
              <span className='text-sm text-gray-600'>
                {getTabCount()} analysis type{getTabCount() !== 1 ? 's' : ''}{' '}
                available
              </span>
            </div>
            {!canUseAdvanced && (
              <Button size='sm' onClick={onUpgrade}>
                <TrendingUp className='h-4 w-4 mr-2' />
                Upgrade for Advanced Features
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Results Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className='w-full'>
        <TabsList className='grid w-full grid-cols-5'>
          <TabsTrigger value='standard'>Standard Analysis</TabsTrigger>
          <TabsTrigger value='advanced' disabled={!advancedAnalysis}>
            Advanced Analysis
            {forensicScore != null && (
              <Badge className='ml-2 h-4 text-xs'>{forensicScore}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value='comparison' disabled={!comparisonResult}>
            Comparison
            {comparisonTotalFiles != null && (
              <Badge className='ml-2 h-4 text-xs'>{comparisonTotalFiles}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value='timeline' disabled={!hasTimeline}>
            Timeline
            {hasTimeline && (
              <Badge className='ml-2 h-4 text-xs'>{timelineEventsCount}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value='report' disabled={!forensicReport}>
            Report
            {reportAssessment && (
              <Badge className='ml-2 h-4 text-xs'>
                {reportAssessment.length > 16
                  ? `${reportAssessment.slice(0, 16)}…`
                  : reportAssessment}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Standard Analysis Tab */}
        <TabsContent value='standard' className='space-y-4'>
          {metadata ? (
            <Card>
              <CardHeader>
                <CardTitle className='flex items-center gap-2'>
                  <FileText className='h-5 w-5' />
                  Standard Metadata Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className='grid grid-cols-2 md:grid-cols-4 gap-4 mb-4'>
                  <div className='text-center'>
                    <div className='text-2xl font-bold text-blue-600'>
                      {metadata.fields_extracted || 0}
                    </div>
                    <div className='text-sm text-gray-600'>
                      Fields Extracted
                    </div>
                  </div>
                  <div className='text-center'>
                    <div className='text-2xl font-bold text-green-600'>
                      {metadata.filetype || 'Unknown'}
                    </div>
                    <div className='text-sm text-gray-600'>File Type</div>
                  </div>
                  <div className='text-center'>
                    <div className='text-2xl font-bold text-purple-600'>
                      {metadata.filesize || 'Unknown'}
                    </div>
                    <div className='text-sm text-gray-600'>File Size</div>
                  </div>
                  <div className='text-center'>
                    <div className='text-2xl font-bold text-orange-600'>
                      {metadata.processing_ms
                        ? `${(metadata.processing_ms / 1000).toFixed(1)}s`
                        : 'N/A'}
                    </div>
                    <div className='text-sm text-gray-600'>Processing Time</div>
                  </div>
                </div>

                {/* Quick Actions */}
                <div className='flex gap-2'>
                  {canUseAdvanced && !advancedAnalysis && (
                    <Button onClick={onRunAdvancedAnalysis} size='sm'>
                      <Eye className='h-4 w-4 mr-2' />
                      Run Advanced Analysis
                    </Button>
                  )}
                  {!canUseAdvanced && (
                    <Button onClick={onUpgrade} variant='outline' size='sm'>
                      <TrendingUp className='h-4 w-4 mr-2' />
                      Upgrade for Advanced Features
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className='pt-6 text-center'>
                <Upload className='h-12 w-12 text-gray-400 mx-auto mb-4' />
                <p className='text-gray-600'>Upload a file to begin analysis</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Advanced Analysis Tab */}
        <TabsContent value='advanced'>
          {advancedAnalysis ? (
            <AdvancedAnalysisResults
              advancedAnalysis={advancedAnalysis}
              steganographyAnalysis={metadata.steganography_analysis}
              manipulationDetection={metadata.manipulation_detection}
              aiDetection={metadata.ai_detection}
            />
          ) : (
            <Card>
              <CardContent className='pt-6 text-center'>
                <Eye className='h-12 w-12 text-gray-400 mx-auto mb-4' />
                <p className='text-gray-600 mb-4'>
                  No advanced analysis results available
                </p>
                {canUseAdvanced && metadata && (
                  <Button onClick={onRunAdvancedAnalysis}>
                    Run Advanced Analysis
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Comparison Tab */}
        <TabsContent value='comparison'>
          {comparisonResult ? (
            <ComparisonView comparisonResult={comparisonResult} />
          ) : (
            <Card>
              <CardContent className='pt-6 text-center'>
                <GitCompare className='h-12 w-12 text-gray-400 mx-auto mb-4' />
                <p className='text-gray-600 mb-4'>
                  No comparison results available
                </p>
                {canUseAdvanced && (
                  <Button onClick={() => handleFileUpload('comparison')}>
                    <Upload className='h-4 w-4 mr-2' />
                    Upload Files to Compare
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Timeline Tab */}
        <TabsContent value='timeline'>
          {hasTimeline ? (
            <TimelineVisualization timelineResult={timelineResult} />
          ) : (
            <Card>
              <CardContent className='pt-6 text-center'>
                <Clock className='h-12 w-12 text-gray-400 mx-auto mb-4' />
                <p className='text-gray-600 mb-4'>
                  No timeline analysis available
                </p>
                {canUseAdvanced && (
                  <Button onClick={() => handleFileUpload('timeline')}>
                    <Upload className='h-4 w-4 mr-2' />
                    Upload Files for Timeline
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Report Tab */}
        <TabsContent value='report'>
          {forensicReport ? (
            <ForensicReport reportData={forensicReport} />
          ) : (
            <Card>
              <CardContent className='pt-6 text-center'>
                <FileText className='h-12 w-12 text-gray-400 mx-auto mb-4' />
                <p className='text-gray-600 mb-4'>
                  No forensic report available
                </p>
                {canUseReports ? (
                  <Button onClick={() => handleFileUpload('report')}>
                    <Upload className='h-4 w-4 mr-2' />
                    Upload Files for Report
                  </Button>
                ) : (
                  <div>
                    <p className='text-sm text-gray-500 mb-2'>
                      Forensic reports require Enterprise tier
                    </p>
                    <Button onClick={onUpgrade} variant='outline'>
                      Upgrade to Enterprise
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Success Indicators */}
      {(advancedAnalysis ||
        comparisonResult ||
        timelineResult ||
        forensicReport) && (
          <Alert className='border-green-200 bg-green-50'>
            <CheckCircle className='h-4 w-4 text-green-600' />
            <AlertDescription className='text-green-800'>
              <strong>Advanced Analysis Complete:</strong>
              {advancedAnalysis && ' Forensic analysis'}
              {comparisonResult && ' • Batch comparison'}
              {timelineResult && ' • Timeline reconstruction'}
              {forensicReport && ' • Professional report'}
              {' completed successfully.'}
            </AlertDescription>
          </Alert>
        )}
    </div>
  );
}
