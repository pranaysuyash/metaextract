/**
 * Progressive Disclosure Component
 *
 * Implements a three-tier information hierarchy:
 * 1. Hero section with key findings (always visible)
 * 2. Quick details card (easy to scan)
 * 3. Advanced metadata (collapsible sections)
 *
 * Enhanced with forensic analysis integration and visual indicators.
 * Reduces cognitive load while keeping all information accessible.
 */

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { KeyFindings, KeyFindingsCompact } from './KeyFindings';
import { QuickDetails, type QuickDetailsData } from './QuickDetails';
import { ExpandableSectionList } from './ExpandableSection';
import { LocationSection, type LocationData } from './LocationSection';
import { ForensicAnalysis } from './ForensicAnalysis';
import { AuthenticityBadge } from './AuthenticityBadge';
import {
  Fingerprint,
  Shield,
  AlertTriangle,
  Activity,
  Brain,
  Search,
} from 'lucide-react';
import type { KeyFindings as KeyFindingsType } from '@/utils/metadataTransformers';

export interface ProgressiveDisclosureData {
  keyFindings: KeyFindingsType;
  quickDetails: QuickDetailsData;
  location?: LocationData | null;
  advancedMetadata?: Record<string, unknown>;
  forensicAnalysis?: {
    steganography?: {
      detected: boolean;
      confidence: number;
      methodsChecked: string[];
      findings: string[];
      details?: string;
    };
    manipulation?: {
      detected: boolean;
      confidence: number;
      indicators: Array<{
        type: string;
        severity: 'low' | 'medium' | 'high';
        description: string;
        confidence: number;
      }>;
      originalityScore?: number;
    };
    aiDetection?: {
      aiGenerated: boolean;
      confidence: number;
      modelHints: string[];
      detectionMethods: string[];
    };
    authenticityScore?: number;
  };
}

export interface ProgressiveDisclosureProps {
  data: ProgressiveDisclosureData;
  className?: string;
  showForensicAnalysis?: boolean;
  defaultTab?: 'overview' | 'location' | 'advanced' | 'forensic';
}

interface AdvancedMetadataViewProps {
  data?: Record<string, unknown>;
  forensicData?: ProgressiveDisclosureData['forensicAnalysis'];
}

/**
 * Forensic Analysis Tab Content
 */
function ForensicAnalysisTab({
  forensicData,
}: {
  forensicData?: ProgressiveDisclosureData['forensicAnalysis'];
}) {
  if (!forensicData) {
    return (
      <div className="space-y-4">
        <div className="text-center p-8 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
          <Fingerprint className="w-12 h-12 mx-auto mb-4 text-slate-500" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            Forensic Analysis
          </h3>
          <p className="text-slate-600 dark:text-slate-400">
            No forensic analysis data available
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-500 mt-2">
            Forensic analysis requires Advanced or Enterprise tier
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Forensic Analysis Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Fingerprint className="w-5 h-5 text-primary" />
            Forensic Analysis Results
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Advanced authenticity and manipulation detection
          </p>
        </div>
        {forensicData.authenticityScore !== undefined && (
          <AuthenticityBadge
            score={forensicData.authenticityScore}
            variant="detailed"
            showConfidence={true}
          />
        )}
      </div>

      {/* Risk Assessment Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {forensicData.steganography && (
          <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-2 mb-2">
              <Search className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <h4 className="font-medium text-blue-900 dark:text-blue-100">
                Steganography
              </h4>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                {forensicData.steganography.detected
                  ? 'Hidden data detected'
                  : 'No hidden data found'}
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400">
                Confidence: {forensicData.steganography.confidence}%
              </p>
            </div>
          </div>
        )}

        {forensicData.manipulation && (
          <div className="p-4 bg-orange-50 dark:bg-orange-950 rounded-lg border border-orange-200 dark:border-orange-800">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-orange-600 dark:text-orange-400" />
              <h4 className="font-medium text-orange-900 dark:text-orange-100">
                Manipulation
              </h4>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-orange-800 dark:text-orange-200">
                {forensicData.manipulation.detected
                  ? 'Manipulation detected'
                  : 'No manipulation found'}
              </p>
              <p className="text-xs text-orange-600 dark:text-orange-400">
                Confidence: {forensicData.manipulation.confidence}%
              </p>
            </div>
          </div>
        )}

        {forensicData.aiDetection && (
          <div className="p-4 bg-purple-50 dark:bg-purple-950 rounded-lg border border-purple-200 dark:border-purple-800">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <h4 className="font-medium text-purple-900 dark:text-purple-100">
                AI Detection
              </h4>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-purple-800 dark:text-purple-200">
                {forensicData.aiDetection.aiGenerated
                  ? 'AI generated content'
                  : 'Likely original content'}
              </p>
              <p className="text-xs text-purple-600 dark:text-purple-400">
                Confidence: {forensicData.aiDetection.confidence}%
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Full Forensic Analysis Component */}
      <ForensicAnalysis
        steganography={forensicData.steganography}
        manipulation={forensicData.manipulation}
        aiDetection={forensicData.aiDetection}
        authenticityScore={forensicData.authenticityScore}
      />
    </div>
  );
}

/**
 * Advanced Metadata View with forensic integration
 */
function AdvancedMetadataView({
  data,
  forensicData,
}: AdvancedMetadataViewProps): React.ReactElement {
  if (!data && !forensicData) {
    return (
      <div className="p-4 text-center text-gray-600 dark:text-gray-300 rounded-lg bg-gray-50 dark:bg-gray-900">
        No advanced metadata available
      </div>
    );
  }

  const sections = [];

  // Add forensic analysis section if available
  if (forensicData) {
    sections.push({
      title: 'Forensic Analysis',
      content: <ForensicAnalysisTab forensicData={forensicData} />,
      icon: <Fingerprint className="w-4 h-4" />,
    });
  }

  // Add regular metadata sections
  if (data) {
    // Filter out undefined/null entries
    const entries = Object.entries(data).filter(
      ([_, v]) => v !== undefined && v !== null
    );

    if (entries.length > 0) {
      sections.push(
        ...entries.map(([key, value]) => ({
          title: formatCategoryName(key),
          content: <MetadataDetails value={value} />,
          icon: null,
        }))
      );
    }
  }

  if (sections.length === 0) {
    return (
      <div className="p-4 text-center text-gray-600 dark:text-gray-300 rounded-lg bg-gray-50 dark:bg-gray-900">
        No advanced metadata available
      </div>
    );
  }

  return <ExpandableSectionList sections={sections} />;
}

/**
 * Metadata Details Component
 */
interface MetadataDetailsProps {
  value: unknown;
}

function MetadataDetails({ value }: MetadataDetailsProps): React.ReactElement {
  if (value === null || value === undefined) {
    return <span className="text-gray-500 dark:text-gray-400">N/A</span>;
  }

  if (typeof value === 'string' || typeof value === 'number') {
    return <span className="text-gray-900 dark:text-white">{value}</span>;
  }

  if (typeof value === 'boolean') {
    return (
      <span
        className={
          value
            ? 'text-green-600 dark:text-green-400'
            : 'text-red-600 dark:text-red-400'
        }
      >
        {value ? 'Yes' : 'No'}
      </span>
    );
  }

  if (Array.isArray(value)) {
    return (
      <div className="space-y-1">
        {value.map((item, idx) => (
          <div key={idx} className="text-sm text-gray-900 dark:text-white">
            {typeof item === 'object' ? JSON.stringify(item) : item}
          </div>
        ))}
      </div>
    );
  }

  if (typeof value === 'object') {
    return (
      <div className="space-y-2">
        {Object.entries(value).map(([k, v]) => (
          <div key={k} className="flex justify-between text-sm">
            <span className="text-gray-700 dark:text-gray-300">
              {formatCategoryName(k)}
            </span>
            <span className="text-gray-900 dark:text-white font-medium">
              {typeof v === 'object' ? JSON.stringify(v) : String(v)}
            </span>
          </div>
        ))}
      </div>
    );
  }

  return <span className="text-gray-900 dark:text-white">{String(value)}</span>;
}

/**
 * Utility function to format category names
 */
function formatCategoryName(name: string): string {
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
}

/**
 * Main ProgressiveDisclosure Component
 */
export function ProgressiveDisclosure({
  data,
  className,
  showForensicAnalysis = true,
  defaultTab = 'overview',
}: ProgressiveDisclosureProps): React.ReactElement {
  const [activeTab, setActiveTab] = useState(defaultTab);
  const hasForensicData = !!(
    data.forensicAnalysis?.steganography ||
    data.forensicAnalysis?.manipulation ||
    data.forensicAnalysis?.aiDetection
  );

  return (
    <div className={cn('space-y-6', className)}>
      {/* Hero Section - Always Visible */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Key Findings
          </h2>
          {showForensicAnalysis &&
            data.forensicAnalysis?.authenticityScore !== undefined && (
              <AuthenticityBadge
                score={data.forensicAnalysis.authenticityScore}
                variant="compact"
              />
            )}
        </div>
        <KeyFindings
          findings={data.keyFindings}
          forensicScore={data.forensicAnalysis?.authenticityScore}
          forensicAnalysis={data.forensicAnalysis}
          showForensicIndicators={showForensicAnalysis}
        />
      </section>

      {/* Tabbed Interface for Progressive Disclosure */}
      <Tabs
        value={activeTab}
        onValueChange={value => setActiveTab(value as typeof activeTab)}
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-3 md:grid-cols-4">
          <TabsTrigger value="overview" className="text-xs md:text-sm">
            Overview
          </TabsTrigger>
          <TabsTrigger value="location" className="text-xs md:text-sm">
            Location
          </TabsTrigger>
          {showForensicAnalysis && hasForensicData && (
            <TabsTrigger value="forensic" className="text-xs md:text-sm">
              <Fingerprint className="w-3 h-3 mr-1" />
              Forensic
            </TabsTrigger>
          )}
          <TabsTrigger value="advanced" className="text-xs md:text-sm">
            Advanced
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab - Quick Details */}
        <TabsContent value="overview" className="space-y-4">
          <div className="space-y-2">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Essential metadata at a glance
            </p>
            <QuickDetails data={data.quickDetails} />
          </div>
        </TabsContent>

        {/* Location Tab */}
        <TabsContent value="location" className="space-y-4">
          <div className="space-y-2">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              GPS location information
            </p>
            {data.location ? (
              <LocationSection location={data.location} />
            ) : (
              <div className="p-4 text-center text-gray-600 dark:text-gray-300 rounded-lg bg-gray-50 dark:bg-gray-900">
                No location data available
              </div>
            )}
          </div>
        </TabsContent>

        {/* Forensic Tab */}
        {showForensicAnalysis && hasForensicData && (
          <TabsContent value="forensic" className="space-y-4">
            <ForensicAnalysisTab forensicData={data.forensicAnalysis} />
          </TabsContent>
        )}

        {/* Advanced Tab - Collapsible Sections */}
        <TabsContent value="advanced" className="space-y-4">
          <div className="space-y-2">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Detailed metadata organized by category
            </p>
            <AdvancedMetadataView
              data={data.advancedMetadata}
              forensicData={data.forensicAnalysis}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

/**
 * Mobile-optimized variant with collapsible sections
 */
export function ProgressiveDisclosureMobile({
  data,
  className,
  showForensicAnalysis = true,
}: ProgressiveDisclosureProps): React.ReactElement {
  const hasForensicData = !!(
    data.forensicAnalysis?.steganography ||
    data.forensicAnalysis?.manipulation ||
    data.forensicAnalysis?.aiDetection
  );

  return (
    <div className={cn('space-y-4', className)}>
      {/* Compact Key Findings for mobile */}
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">
            Key Info
          </h2>
          {showForensicAnalysis &&
            data.forensicAnalysis?.authenticityScore !== undefined && (
              <AuthenticityBadge
                score={data.forensicAnalysis.authenticityScore}
                variant="compact"
              />
            )}
        </div>
        <KeyFindingsCompact
          findings={data.keyFindings}
          forensicScore={data.forensicAnalysis?.authenticityScore}
          forensicAnalysis={data.forensicAnalysis}
        />
      </section>

      {/* Expandable sections for mobile */}
      <ExpandableSectionList
        sections={[
          {
            title: 'Details',
            content: <QuickDetails data={data.quickDetails} />,
            icon: null,
          },
          ...(data.location
            ? [
                {
                  title: 'Location',
                  content: <LocationSection location={data.location} />,
                  icon: null,
                },
              ]
            : []),
          ...(showForensicAnalysis && hasForensicData
            ? [
                {
                  title: 'Forensic Analysis',
                  content: (
                    <ForensicAnalysisTab forensicData={data.forensicAnalysis} />
                  ),
                  icon: <Fingerprint className="w-4 h-4" />,
                },
              ]
            : []),
          ...(data.advancedMetadata &&
          Object.keys(data.advancedMetadata).length > 0
            ? [
                {
                  title: 'Advanced Metadata',
                  content: (
                    <AdvancedMetadataView
                      data={data.advancedMetadata}
                      forensicData={data.forensicAnalysis}
                    />
                  ),
                  icon: null,
                },
              ]
            : []),
        ]}
      />
    </div>
  );
}
