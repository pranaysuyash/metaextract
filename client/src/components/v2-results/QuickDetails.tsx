/**
 * Quick Details Component
 *
 * Displays essential metadata in a compact, scannable format.
 * Shows: Resolution, file size, dimensions, camera settings at a glance.
 */

import React from 'react';
import { Maximize2, HardDrive, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface QuickDetailsData {
  resolution?: string;
  fileSize?: string;
  dimensions?: string;
  colorSpace?: string;
  iso?: number;
  focalLength?: string;
  exposure?: string;
  aperture?: string;
}

interface QuickDetailsProps {
  data: QuickDetailsData;
  className?: string;
}

export function QuickDetails({
  data,
  className
}: QuickDetailsProps): React.ReactElement {
  if (!hasAnyData(data)) {
    return (
      <div className={cn('text-center text-gray-500 dark:text-gray-400', className)}>
        No quick details available
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {/* Image Properties */}
      {(data.resolution || data.dimensions) && (
        <QuickDetailGroup title="Image" icon={<Maximize2 className="w-4 h-4" />}>
          {data.resolution && (
            <DetailItem label="Resolution" value={data.resolution} />
          )}
          {data.dimensions && (
            <DetailItem label="Dimensions" value={data.dimensions} />
          )}
          {data.colorSpace && (
            <DetailItem label="Color Space" value={data.colorSpace} />
          )}
        </QuickDetailGroup>
      )}

      {/* File Properties */}
      {data.fileSize && (
        <QuickDetailGroup title="File" icon={<HardDrive className="w-4 h-4" />}>
          <DetailItem label="Size" value={data.fileSize} />
        </QuickDetailGroup>
      )}

      {/* Camera Settings */}
      {hasAnyCameraSetting(data) && (
        <QuickDetailGroup title="Camera Settings" icon={<Settings className="w-4 h-4" />}>
          {data.iso && <DetailItem label="ISO" value={data.iso.toString()} />}
          {data.focalLength && (
            <DetailItem label="Focal Length" value={data.focalLength} />
          )}
          {data.exposure && (
            <DetailItem label="Exposure" value={data.exposure} />
          )}
          {data.aperture && <DetailItem label="Aperture" value={data.aperture} />}
        </QuickDetailGroup>
      )}
    </div>
  );
}

interface QuickDetailGroupProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

function QuickDetailGroup({
  title,
  icon,
  children
}: QuickDetailGroupProps): React.ReactElement {
  return (
    <div className="rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="px-3 py-2 bg-gray-50 dark:bg-gray-900 flex items-center gap-2 border-b border-gray-200 dark:border-gray-700">
        <div className="text-gray-600 dark:text-gray-400">{icon}</div>
        <h4 className="text-sm font-medium text-gray-900 dark:text-white">
          {title}
        </h4>
      </div>
      <div className="px-3 py-2 space-y-2">
        {children}
      </div>
    </div>
  );
}

interface DetailItemProps {
  label: string;
  value: string | number;
}

function DetailItem({
  label,
  value
}: DetailItemProps): React.ReactElement {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-xs text-gray-600 dark:text-gray-400">
        {label}
      </span>
      <span className="text-sm font-medium text-gray-900 dark:text-white">
        {value}
      </span>
    </div>
  );
}

function hasAnyData(data: QuickDetailsData): boolean {
  return Object.values(data).some(v => v !== undefined && v !== null && v !== '');
}

function hasAnyCameraSetting(data: QuickDetailsData): boolean {
  return !!(data.iso || data.focalLength || data.exposure || data.aperture);
}
