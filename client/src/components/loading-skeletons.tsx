/**
 * Loading Skeleton Components
 * 
 * Provides smooth loading states for different UI components.
 */

import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

// ============================================================================
// Base Skeleton Components
// ============================================================================

interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export function SkeletonLine({ className, animate = true }: SkeletonProps) {
  return (
    <Skeleton 
      className={cn(
        "h-4 bg-muted rounded",
        animate && "animate-pulse",
        className
      )} 
    />
  );
}

export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn("space-y-2", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonLine 
          key={i} 
          className={i === lines - 1 ? "w-3/4" : "w-full"} 
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className }: SkeletonProps) {
  return (
    <Card className={className}>
      <CardHeader>
        <Skeleton className="h-6 w-1/3" />
        <Skeleton className="h-4 w-1/2" />
      </CardHeader>
      <CardContent>
        <SkeletonText lines={3} />
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Metadata-Specific Skeletons
// ============================================================================

export function MetadataFieldSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-4 py-2 px-3 border-b border-white/5">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-4 w-32 ml-auto" />
    </div>
  );
}

export function MetadataSectionSkeleton({ fieldCount = 5 }: { fieldCount?: number }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Skeleton className="h-4 w-4" />
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-4 w-8 ml-2" />
      </div>
      <div className="space-y-1">
        {Array.from({ length: fieldCount }).map((_, i) => (
          <MetadataFieldSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

export function MetadataPageSkeleton() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header Skeleton */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 pb-6 border-b border-white/10 gap-4">
        <div className="flex items-center gap-4">
          <Skeleton className="w-12 h-12 rounded" />
          <div>
            <Skeleton className="h-6 w-48 mb-2" />
            <div className="flex gap-4">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-32" />
            </div>
          </div>
        </div>
        <Skeleton className="h-10 w-32" />
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar Skeleton */}
        <div className="w-full md:w-72 shrink-0 space-y-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>

        {/* Main Content Skeleton */}
        <div className="flex-1">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div className="flex gap-2">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Skeleton key={i} className="h-8 w-16" />
                  ))}
                </div>
                <Skeleton className="h-8 w-48" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {Array.from({ length: 4 }).map((_, i) => (
                  <MetadataSectionSkeleton key={i} fieldCount={6} />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Advanced Analysis Skeletons
// ============================================================================

export function AdvancedAnalysisSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-purple-200 bg-purple-50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Skeleton className="h-6 w-6" />
            <Skeleton className="h-6 w-48" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="text-center space-y-2">
                <Skeleton className="h-8 w-8 mx-auto" />
                <Skeleton className="h-4 w-24 mx-auto" />
                <Skeleton className="h-3 w-32 mx-auto" />
                <Skeleton className="h-8 w-full" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Skeleton className="h-5 w-5" />
                <Skeleton className="h-5 w-32" />
              </div>
            </CardHeader>
            <CardContent>
              <SkeletonText lines={4} />
              <div className="mt-4 flex gap-2">
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-24" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function ForensicAnalysisSkeleton() {
  return (
    <div className="space-y-6">
      {/* Status Banner */}
      <div className="p-4 border rounded-lg">
        <div className="flex items-center gap-3">
          <Skeleton className="h-5 w-5" />
          <div className="flex-1">
            <Skeleton className="h-5 w-48 mb-2" />
            <Skeleton className="h-4 w-96" />
          </div>
          <Skeleton className="h-6 w-16" />
        </div>
      </div>

      {/* Analysis Results */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-4 w-4" />
                  <Skeleton className="h-4 w-24" />
                </div>
                <Skeleton className="h-6 w-12" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-16" />
                </div>
                <Skeleton className="h-2 w-full rounded-full" />
                <SkeletonText lines={2} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// File Explorer Skeletons
// ============================================================================

export function FileExplorerSkeleton() {
  return (
    <div className="flex h-full flex-col">
      {/* Search Bar */}
      <div className="border-b p-3">
        <Skeleton className="h-9 w-full" />
      </div>

      {/* File List */}
      <div className="flex-1 p-2 space-y-1">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3 p-3 rounded-lg">
            <Skeleton className="h-4 w-4" />
            <div className="flex-1">
              <Skeleton className="h-4 w-32 mb-1" />
              <Skeleton className="h-3 w-24" />
            </div>
            <Skeleton className="h-3 w-3 rounded-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function MetadataTreeSkeleton() {
  return (
    <div className="flex h-full flex-col">
      {/* Search Bar */}
      <div className="border-b p-3">
        <Skeleton className="h-9 w-full" />
      </div>

      {/* Category Tree */}
      <div className="flex-1 p-2 space-y-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="flex items-center gap-2 p-2">
              <Skeleton className="h-4 w-4" />
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-8 ml-auto" />
            </div>
            <div className="pl-6 space-y-1">
              {Array.from({ length: 4 }).map((_, j) => (
                <div key={j} className="flex items-center justify-between p-2">
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-3 w-16" />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function DetailViewSkeleton() {
  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b p-4">
        <Skeleton className="h-6 w-32 mb-2" />
        <Skeleton className="h-4 w-20" />
      </div>

      {/* Content */}
      <div className="flex-1 p-4 space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <Skeleton className="h-4 w-16" />
                <Skeleton className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <SkeletonText lines={2} />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Upload Zone Skeleton
// ============================================================================

export function UploadZoneSkeleton() {
  return (
    <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8">
      <div className="text-center space-y-4">
        <Skeleton className="h-12 w-12 mx-auto" />
        <div className="space-y-2">
          <Skeleton className="h-6 w-48 mx-auto" />
          <Skeleton className="h-4 w-64 mx-auto" />
        </div>
        <div className="flex justify-center gap-2">
          <Skeleton className="h-9 w-24" />
          <Skeleton className="h-9 w-32" />
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Processing Indicators
// ============================================================================

export function ProcessingIndicator({ 
  message = "Processing...", 
  progress 
}: { 
  message?: string; 
  progress?: number;
}) {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center space-y-4">
        <div className="relative">
          <Skeleton className="h-12 w-12 mx-auto rounded-full animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-6 w-6 bg-background rounded-full" />
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-sm font-medium">{message}</p>
          {progress !== undefined && (
            <div className="w-48 mx-auto">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {Math.round(progress)}% complete
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Shimmer Effect
// ============================================================================

export function ShimmerWrapper({ 
  children, 
  isLoading, 
  className 
}: { 
  children: React.ReactNode; 
  isLoading: boolean; 
  className?: string;
}) {
  if (!isLoading) return <>{children}</>;
  
  return (
    <div className={cn("relative overflow-hidden", className)}>
      <div className="opacity-50">{children}</div>
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
    </div>
  );
}

// ============================================================================
// Skeleton Variants
// ============================================================================

export const SkeletonVariants = {
  pulse: "animate-pulse",
  wave: "animate-wave",
  shimmer: "animate-shimmer",
  none: "",
} as const;

export function SkeletonWithVariant({ 
  variant = "pulse", 
  className,
  ...props 
}: SkeletonProps & { 
  variant?: keyof typeof SkeletonVariants;
}) {
  return (
    <Skeleton 
      className={cn(
        SkeletonVariants[variant],
        className
      )}
      {...props}
    />
  );
}