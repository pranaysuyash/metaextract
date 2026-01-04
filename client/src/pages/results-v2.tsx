import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { KeyFindings, KeyFindingsCompact } from '@/components/v2-results/KeyFindings';
import { ProgressiveDisclosure, ProgressiveDisclosureMobile, type ProgressiveDisclosureData } from '@/components/v2-results/ProgressiveDisclosure';
import { ActionsToolbar, ActionsToolbarCompact } from '@/components/v2-results/ActionsToolbar';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, FileText, Cpu, Smartphone } from 'lucide-react';
import generatedBackground from '@assets/generated_images/chaotic_dark_forensic_data_visualization_with_connecting_lines.png';
import { cn } from '@/lib/utils';
import { extractKeyFindings } from '@/utils/metadataTransformers';
import type { LocationData } from '@/components/v2-results/LocationSection';

interface MetadataResponse {
  filename: string;
  filesize: string;
  filetype: string;
  mime_type: string;
  tier: string;
  fields_extracted: number;
  fields_available: number;
  processing_ms: number;
  file_integrity?: {
    md5: string;
    sha256: string;
    sha1?: string;
    crc32?: string;
  };
  gps?: any;
  exif?: any;
  filesystem?: any;
  summary?: any;
  [key: string]: any;
}

export default function ResultsV2() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const resultId = searchParams.get('id');
  const { toast } = useToast();
  const [metadata, setMetadata] = useState<MetadataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  // Handle window resize for responsive design
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    // Priority 1: Load from navigation state (handles large payloads, fresh upload)
    let metadataData = null;

    if (location.state?.metadata) {
      console.log('[ResultsV2] Loaded metadata from navigation state');
      metadataData = location.state.metadata;
    } else if (location.state?.results) {
      console.log('[ResultsV2] Loaded results from navigation state');
      metadataData = location.state.results;
    } else {
      // Priority 2: Try sessionStorage (V2 button uses this)
      const stored = sessionStorage.getItem('currentMetadata');
      if (stored) {
        try {
          metadataData = JSON.parse(stored);
          console.log('[ResultsV2] Loaded from sessionStorage');
          toast({
            title: 'Using last result',
            description: 'Loaded from memory.',
          });
        } catch (e) {
          console.error('[ResultsV2] Failed to parse sessionStorage', e);
        }
      }
    }

    // Handle if data is an array
    if (Array.isArray(metadataData)) {
      console.log('[ResultsV2] Data is array, taking first element');
      setMetadata(metadataData[0]);
      setIsLoading(false);
    } else if (metadataData) {
      console.log('[ResultsV2] Data is object');
      setMetadata(metadataData);
      setIsLoading(false);
    } else {
      console.warn('[ResultsV2] No metadata in navigation or sessionStorage');
      setIsLoading(false);
    }
  }, [location.state, toast]);

  // Transform metadata for ProgressiveDisclosure
  const progressiveDisclosureData = useMemo<ProgressiveDisclosureData | null>(() => {
    if (!metadata) return null;

    // Extract key findings
    const keyFindings = extractKeyFindings(metadata);

    // Extract quick details
    const quickDetails = {
      resolution: metadata.resolution || metadata.exif?.image_width && metadata.exif?.image_height
        ? `${metadata.exif.image_width}x${metadata.exif.image_height}`
        : undefined,
      fileSize: metadata.filesize,
      dimensions: metadata.exif?.image_width && metadata.exif?.image_height
        ? `${metadata.exif.image_width} x ${metadata.exif.image_height} pixels`
        : undefined,
      colorSpace: metadata.exif?.color_space,
      iso: metadata.exif?.iso_speed,
      focalLength: metadata.exif?.focal_length,
      exposure: metadata.exif?.exposure_time,
      aperture: metadata.exif?.f_number,
    };

    // Extract location data
    const locationData: LocationData | undefined = metadata.gps?.latitude && metadata.gps?.longitude
      ? {
          latitude: metadata.gps.latitude,
          longitude: metadata.gps.longitude,
        }
      : undefined;

    // Extract advanced metadata
    const advancedMetadata = {
      ...metadata,
      filename: undefined, // Remove redundant fields
      filesize: undefined,
      filetype: undefined,
    };

    return {
      keyFindings,
      quickDetails,
      location: locationData,
      advancedMetadata,
    };
  }, [metadata]);

  // Priority 3: Fetch from DB if ID param exists and no data loaded yet
  useEffect(() => {
    if (resultId && !metadata) {
      console.log(
        `[ResultsV2] ID found in URL: ${resultId}. Fetching from DB...`
      );
      setIsLoading(true);

      fetch(`/api/extract/results/${resultId}`)
        .then(res => {
          if (!res.ok) throw new Error('Result not found');
          return res.json();
        })
        .then(data => {
          console.log('[ResultsV2] Loaded metadata from DB');
          setMetadata(data);
          setIsLoading(false);
        })
        .catch(err => {
          console.error('[ResultsV2] Failed to fetch by ID:', err);
          toast({
            title: 'Error loading result',
            description: 'Could not load saved analysis.',
            variant: 'destructive',
          });
          setIsLoading(false);
          // Redirect to home after showing error
          setTimeout(() => navigate('/'), 1500);
        });
    } else if (!metadata && !isLoading) {
      // No data available from any source
      toast({
        title: 'No metadata found',
        description: 'Please upload a file first.',
        variant: 'destructive',
      });
      setTimeout(() => navigate('/'), 900);
    }
  }, [resultId, metadata, isLoading, navigate, toast]);

  const handleDownload = () => {
    if (!metadata) return;

    const dataStr = JSON.stringify(metadata, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${metadata.filename}_metadata.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast({
      title: 'Download started',
      description: 'Your metadata file is being downloaded',
    });
  };

  if (isLoading) {
    return (
      <div className="relative min-h-screen overflow-hidden">
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-background/90 z-10"></div>
          <img
            src={generatedBackground}
            alt="Background"
            className="w-full h-full object-cover opacity-10 mix-blend-screen scale-110"
          />
        </div>
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-white font-mono">Loading your results...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!metadata) {
    return (
      <div className="relative min-h-screen overflow-hidden">
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-background/90 z-10"></div>
          <img
            src={generatedBackground}
            alt="Background"
            className="w-full h-full object-cover opacity-10 mix-blend-screen scale-110"
          />
        </div>
        <div className="relative z-10 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4 font-mono">
              No Results Found
            </h2>
            <Button
              onClick={() => navigate('/')}
              variant="default"
              className="gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Go Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-[calc(100vh-64px)] overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-background/90 z-10"></div>
        <img
          src={generatedBackground}
          alt="Background"
          className="w-full h-full object-cover opacity-10 mix-blend-screen scale-110"
        />
      </div>

      {/* Header */}
      <div className="relative z-10 border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="gap-2 text-white hover:text-white hover:bg-white/10"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Button>

            <div className="flex gap-3">
              <div className="flex items-center gap-2 px-3 py-2 bg-blue-600/20 border border-blue-500/30 rounded text-blue-300 text-xs font-mono">
                <Cpu className="w-4 h-4" />
                V2 RESULTS
              </div>

              <Button
                variant="outline"
                onClick={handleDownload}
                className="gap-2 font-mono text-xs border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/10"
              >
                <Download className="w-4 h-4" />
                JSON
              </Button>
              <Button
                variant="outline"
                onClick={() => toast({ title: 'PDF export coming soon to V2' })}
                className="gap-2 font-mono text-xs border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/10"
              >
                <FileText className="w-4 h-4" />
                PDF
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* File Header - Matching forensic theme */}
          <div className="flex items-center justify-between pb-6 border-b border-white/10">
            <div className="flex items-center gap-4 flex-1">
              <div className="w-12 h-12 bg-white/5 rounded border border-white/10 flex items-center justify-center flex-shrink-0">
                <Cpu className="w-6 h-6 text-primary" />
              </div>
              <div className="min-w-0">
                <h1 className="text-xl font-bold text-white font-mono tracking-tight truncate">
                  {metadata.filename}
                </h1>
                <div className={cn(
                  'text-xs text-slate-500 font-mono mt-1',
                  isMobile ? 'flex flex-col gap-1' : 'flex gap-4'
                )}>
                  <span>SIZE: {metadata.filesize}</span>
                  <span className="hidden sm:inline">TYPE: {metadata.filetype}</span>
                  <span className="text-primary hidden md:inline">
                    SHA256:{' '}
                    {metadata.file_integrity?.sha256?.substring(0, 12) || 'N/A'}
                    ...
                  </span>
                </div>
              </div>
            </div>
            {isMobile && (
              <div className="ml-2 flex-shrink-0">
                <Smartphone className="w-5 h-5 text-blue-400" />
              </div>
            )}
          </div>

          {/* Progressive Disclosure Section */}
          {progressiveDisclosureData && (
            <div className={cn(
              'bg-black/40 backdrop-blur-md border border-white/10 rounded-lg shadow-lg',
              isMobile ? 'p-4' : 'p-6'
            )}>
              {isMobile ? (
                <ProgressiveDisclosureMobile data={progressiveDisclosureData} />
              ) : (
                <ProgressiveDisclosure data={progressiveDisclosureData} />
              )}
            </div>
          )}

          {/* Actions Toolbar */}
          <div className={cn(
            'bg-black/40 backdrop-blur-md border border-white/10 rounded-lg shadow-lg'
          )}>
            {isMobile ? (
              <ActionsToolbarCompact
                filename={metadata.filename}
                metadata={metadata}
                className="m-4"
              />
            ) : (
              <ActionsToolbar
                filename={metadata.filename}
                metadata={metadata}
                className="p-6"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
