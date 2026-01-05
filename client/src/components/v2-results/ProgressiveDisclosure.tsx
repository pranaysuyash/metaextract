/**
 * Progressive Disclosure Component
 *
 * Implements a three-tier information hierarchy:
 * 1. Hero section with key findings (always visible)
 * 2. Quick details card (easy to scan)
 * 3. Advanced metadata (collapsible sections)
 *
 * Reduces cognitive load while keeping all information accessible.
 */

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { KeyFindings, KeyFindingsCompact } from './KeyFindings';
import { QuickDetails, type QuickDetailsData } from './QuickDetails';
import { ExpandableSectionList } from './ExpandableSection';
import { LocationSection, type LocationData } from './LocationSection';
import type { KeyFindings as KeyFindingsType } from '@/utils/metadataTransformers';

export interface ProgressiveDisclosureData {
  keyFindings: KeyFindingsType;
  quickDetails: QuickDetailsData;
  location?: LocationData | null;
  advancedMetadata?: Record<string, unknown>;
}

interface ProgressiveDisclosureProps {
  data: ProgressiveDisclosureData;
  className?: string;
}

export function ProgressiveDisclosure({
  data,
  className
}: ProgressiveDisclosureProps): React.ReactElement {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className={cn('space-y-6', className)}>
      {/* Hero Section - Always Visible */}
      <section className="space-y-2">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Key Findings
        </h2>
        <KeyFindings findings={data.keyFindings} />
      </section>

      {/* Tabbed Interface for Progressive Disclosure */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="location">Location</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
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

        {/* Advanced Tab - Collapsible Sections */}
        <TabsContent value="advanced" className="space-y-4">
          <div className="space-y-2">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Detailed metadata organized by category
            </p>
            <AdvancedMetadataView data={data.advancedMetadata} />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

interface AdvancedMetadataViewProps {
  data?: Record<string, unknown>;
}

function AdvancedMetadataView({
  data
}: AdvancedMetadataViewProps): React.ReactElement {
  if (!data) {
    return (
      <div className="p-4 text-center text-gray-600 dark:text-gray-300 rounded-lg bg-gray-50 dark:bg-gray-900">
        No advanced metadata available
      </div>
    );
  }

  // Filter out undefined/null entries to avoid showing 'N/A' for intentionally omitted fields
  const entries = Object.entries(data).filter(([_, v]) => v !== undefined && v !== null);
  if (entries.length === 0) {
    return (
      <div className="p-4 text-center text-gray-600 dark:text-gray-300 rounded-lg bg-gray-50 dark:bg-gray-900">
        No advanced metadata available
      </div>
    );
  }

  // Group metadata by category (if available)
  const sections = entries.map(([key, value]) => ({
    title: formatCategoryName(key),
    content: <MetadataDetails value={value} />
  }));

  return <ExpandableSectionList sections={sections} />;
}

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
      <span className={value ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
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
            <span className="text-gray-700 dark:text-gray-300">{formatCategoryName(k)}</span>
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

function formatCategoryName(name: string): string {
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
}

/**
 * Mobile-optimized variant with collapsible sections
 */
export function ProgressiveDisclosureMobile({
  data,
  className
}: ProgressiveDisclosureProps): React.ReactElement {
  return (
    <div className={cn('space-y-4', className)}>
      {/* Compact Key Findings for mobile */}
      <section className="space-y-2">
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">
          Key Info
        </h2>
        <KeyFindingsCompact findings={data.keyFindings} />
      </section>

      {/* Expandable sections for mobile */}
      <ExpandableSectionList
        sections={[
          {
            title: 'Details',
            content: <QuickDetails data={data.quickDetails} />
          },
          ...(data.location
            ? [
              {
                title: 'Location',
                content: <LocationSection location={data.location} />
              }
            ]
            : []),
          ...(data.advancedMetadata && Object.keys(data.advancedMetadata).length > 0
            ? [
              {
                title: 'Advanced',
                content: <AdvancedMetadataView data={data.advancedMetadata} />
              }
            ]
            : [])
        ]}
      />
    </div>
  );
}
