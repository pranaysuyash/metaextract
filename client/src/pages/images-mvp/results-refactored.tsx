import React, { useCallback, useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ShieldAlert, Info, Lock } from 'lucide-react';

// Components
import { PublicLayout as Layout } from '@/components/public-layout';
import {
  ResultsLayout,
  LoadState,
} from '@/components/images-mvp/ResultsLayout';
import { ResultsHeader } from '@/components/images-mvp/ResultsHeader';
import { HighlightsCard } from '@/components/images-mvp/HighlightsCard';
import {
  LimitedAccessBanner,
  DeviceFreeBanner,
  LimitedWarningBanner,
} from '@/components/images-mvp/LimitedAccessBanner';
import { FormatHintCard } from '@/components/images-mvp/FormatHintCard';
import { PrivacyTab } from '@/components/images-mvp/PrivacyTab';

// Hooks
import { useImageMetadataProcessing } from '@/hooks/useImageMetadataProcessing';
import { useImageAccessControl } from '@/hooks/useImageAccessControl';
import { useImageAnalytics } from '@/hooks/useImageAnalytics';
import { useToast } from '@/hooks/use-toast';

// UI Components
import { PricingModal } from '@/components/images-mvp/pricing-modal';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';

// Utilities
import { showSuccessMessage, showUploadError } from '@/lib/toast-helpers';
import { MvpMetadata, TabValue, PurposeValue, DensityMode } from '@/lib/types';
import { buildSummaryLines } from '@/utils/imageSummaryUtils';

// Constants
const PURPOSE_STORAGE_KEY = 'images_mvp_purpose';
const DENSITY_STORAGE_KEY = 'images_mvp_density';

const isTabValue = (value: string): value is TabValue =>
  value === 'privacy' ||
  value === 'authenticity' ||
  value === 'photography' ||
  value === 'raw';

const isPurposeValue = (value: string): value is PurposeValue =>
  value === 'privacy' ||
  value === 'authenticity' ||
  value === 'photography' ||
  value === 'explore';

const mapPurposeToTab = (value: PurposeValue): TabValue => {
  if (value === 'authenticity') return 'authenticity';
  if (value === 'photography') return 'photography';
  return 'privacy';
};

export default function ImagesMvpResultsRefactored() {
  const [metadata, setMetadata] = useState<MvpMetadata | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [errorInfo, setErrorInfo] = useState<{
    status?: number;
    message?: string;
  } | null>(null);
  const [activeTab, setActiveTab] = useState<TabValue>('privacy');
  const [rawSearch, setRawSearch] = useState('');
  const [showOverlayText, setShowOverlayText] = useState(false);
  const [showAllExif, setShowAllExif] = useState(false);
  const [purpose, setPurpose] = useState<PurposeValue | null>(null);
  const [showPurposeModal, setShowPurposeModal] = useState(false);
  const [densityMode, setDensityMode] = useState<DensityMode>('normal');
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');

  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { toast } = useToast();

  // Load metadata from session storage
  useEffect(() => {
    const stored = sessionStorage.getItem('currentMetadata');
    if (!stored) {
      const status = sessionStorage.getItem('images_mvp_status');
      if (status === 'processing') {
        setLoadState('processing');
        return;
      }
      if (status === 'fail') {
        const raw = sessionStorage.getItem('images_mvp_error');
        if (raw) {
          try {
            setErrorInfo(JSON.parse(raw));
          } catch {
            setErrorInfo({ message: 'Upload failed' });
          }
        }
        setLoadState('fail');
        return;
      }
      setLoadState('empty');
      return;
    }
    try {
      setMetadata(JSON.parse(stored));
      setLoadState('ready');
    } catch {
      setLoadState('empty');
    }
  }, []);

  // Handle pricing modal from URL params
  useEffect(() => {
    const pricingFlag =
      searchParams.get('pricing') || searchParams.get('credits');
    if (!pricingFlag) return;
    setShowPricingModal(true);
    const next = new URLSearchParams(searchParams);
    next.delete('pricing');
    next.delete('credits');
    setSearchParams(next, { replace: true });
  }, [searchParams, setSearchParams]);

  // Load purpose and density from local storage
  useEffect(() => {
    if (!metadata) return;
    const storedPurpose = localStorage.getItem(PURPOSE_STORAGE_KEY);
    const storedDensity = localStorage.getItem(DENSITY_STORAGE_KEY);
    if (storedDensity === 'advanced' || storedDensity === 'normal') {
      setDensityMode(storedDensity);
    }
    if (storedPurpose && isPurposeValue(storedPurpose)) {
      setPurpose(storedPurpose);
      setActiveTab(mapPurposeToTab(storedPurpose));
    } else {
      setShowPurposeModal(true);
    }
  }, [metadata]);

  // Handle density mode changes
  useEffect(() => {
    if (densityMode === 'normal' && activeTab === 'raw') {
      setActiveTab('privacy');
    }
  }, [densityMode, activeTab]);

  // Analytics setup
  const {
    trackEvent,
    trackPurposeSelect,
    trackDensityChange,
    trackPaywallCta,
  } = useImageAnalytics({
    metadata,
    activeTab,
    densityMode,
    purpose,
    showPurposeModal,
    showPricingModal,
  });

  // Metadata processing
  const {
    gpsCoords,
    overlayGps,
    hasGps,
    embeddedGpsState,
    captureDateLabel,
    captureDateValue,
    localModifiedValue,
    burnedTimestamp,
    hashSha256,
    hashMd5,
    formatHint,
    highlights,
    orderedHighlights,
    gpsMapUrl,
    dimensionsValue,
    megapixelsValue,
    colorSpaceValue,
    exifEntries,
    lockedGroups,
    lockedTotal,
    software,
    fieldsExtracted,
    processingMs,
  } = useImageMetadataProcessing(metadata!, purpose);

  // Access control
  const {
    isLimited,
    canExport,
    handleDownloadJson,
    handleDownloadFullTxt,
    handleDownloadSummary,
  } = useImageAccessControl(metadata!, purpose);

  // Event handlers
  const handlePurposeSelect = useCallback(
    (value: PurposeValue) => {
      setPurpose(value);
      localStorage.setItem(PURPOSE_STORAGE_KEY, value);
      trackPurposeSelect(value);
      if (value === 'explore') {
        setDensityMode('advanced');
        localStorage.setItem(DENSITY_STORAGE_KEY, 'advanced');
      }
      setActiveTab(mapPurposeToTab(value));
      setShowPurposeModal(false);
    },
    [trackPurposeSelect]
  );

  const handleDensityChange = useCallback(
    (value: string | null) => {
      if (value !== 'normal' && value !== 'advanced') return;
      setDensityMode(value);
      localStorage.setItem(DENSITY_STORAGE_KEY, value);
      trackDensityChange(value);
    },
    [trackDensityChange]
  );

  const handleCopySummary = useCallback(async () => {
    try {
      const summary = buildSummaryLines(metadata!, purpose, orderedHighlights);
      await navigator.clipboard?.writeText(summary);
      showSuccessMessage(
        toast,
        'Summary copied',
        'Highlights copied to your clipboard.'
      );
      trackEvent('summary_copied', {
        filetype: metadata!.filetype,
        mime_type: metadata!.mime_type,
        purpose: purpose || 'unset',
      });
    } catch {
      showUploadError(toast, 'Clipboard access was blocked by your browser.');
    }
  }, [metadata, purpose, orderedHighlights, toast, trackEvent]);

  const handleDownloadSummaryLocal = useCallback(() => {
    const buildSummary = () =>
      buildSummaryLines(metadata!, purpose, orderedHighlights);
    handleDownloadSummary(buildSummary);
  }, [metadata, purpose, orderedHighlights, handleDownloadSummary]);

  const scrollTo = useCallback((tab: TabValue, anchorId: string) => {
    setActiveTab(tab);
    window.setTimeout(() => {
      const el = document.getElementById(anchorId);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }, []);

  const onClearError = useCallback(() => {
    sessionStorage.removeItem('images_mvp_error');
    sessionStorage.setItem('images_mvp_status', 'idle');
    setErrorInfo(null);
    setLoadState('empty');
  }, []);

  const onClearStatus = useCallback(() => {
    sessionStorage.removeItem('images_mvp_error');
    sessionStorage.setItem('images_mvp_status', 'idle');
    setLoadState('empty');
  }, []);

  const showPricingModalHandler = useCallback(() => {
    setShowPricingModal(true);
  }, []);

  const onPaywallCta = useCallback(() => {
    trackPaywallCta(lockedTotal);
    setShowPricingModal(true);
  }, [trackPaywallCta, lockedTotal]);

  const onNavigateToUpload = useCallback(() => {
    navigate('/images_mvp');
  }, [navigate]);

  const isAdvanced = densityMode === 'advanced';
  const purposeLabel = purpose
    ? `${purpose.charAt(0).toUpperCase()}${purpose.slice(1)}`
    : 'Not set';

  // Calculate EXIF entries for display
  const exifEntriesForList =
    showAllExif || canExport ? exifEntries : exifEntries.slice(0, 14);

  return (
    <ResultsLayout
      loadState={loadState}
      errorInfo={errorInfo}
      onClearError={onClearError}
      onClearStatus={onClearStatus}
      showPricingModal={showPricingModalHandler}
    >
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-4xl">
            <PricingModal
              isOpen={showPricingModal}
              onClose={() => setShowPricingModal(false)}
              defaultEmail={
                typeof window !== 'undefined'
                  ? localStorage.getItem('metaextract_access_email') ||
                    undefined
                  : undefined
              }
            />

            {/* Purpose Selection Modal */}
            <Dialog open={showPurposeModal} onOpenChange={setShowPurposeModal}>
              <DialogContent className="sm:max-w-[520px] bg-[#0A0A0A] border border-white/10 text-white">
                <DialogTitle className="text-lg font-semibold">
                  What brings you here?
                </DialogTitle>
                <DialogDescription className="text-sm text-slate-400">
                  Pick a focus so we can highlight what matters most. You can
                  change this later.
                </DialogDescription>
                <div className="mt-5 grid grid-cols-1 gap-3">
                  <button
                    type="button"
                    onClick={() => handlePurposeSelect('privacy')}
                    className="border border-white/10 rounded-lg p-4 text-left hover:border-primary/60 hover:bg-white/5 transition-colors"
                  >
                    <div className="text-sm font-semibold text-white">
                      Privacy check
                    </div>
                    <div className="text-xs text-slate-400">
                      Find location data, device details, and personal
                      identifiers.
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => handlePurposeSelect('authenticity')}
                    className="border border-white/10 rounded-lg p-4 text-left hover:border-primary/60 hover:bg-white/5 transition-colors"
                  >
                    <div className="text-sm font-semibold text-white">
                      Verify authenticity
                    </div>
                    <div className="text-xs text-slate-400">
                      Check edit history, hashes, and integrity signals.
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => handlePurposeSelect('photography')}
                    className="border border-white/10 rounded-lg p-4 text-left hover:border-primary/60 hover:bg-white/5 transition-colors"
                  >
                    <div className="text-sm font-semibold text-white">
                      Photography details
                    </div>
                    <div className="text-xs text-slate-400">
                      Review camera settings, lens info, and capture details.
                    </div>
                  </button>
                </div>
                <div className="mt-5 flex items-center justify-between">
                  <Button
                    variant="outline"
                    className="border-white/10 hover:bg-white/5"
                    onClick={() => handlePurposeSelect('explore')}
                  >
                    Show everything
                  </Button>
                  <Button
                    variant="ghost"
                    className="text-slate-400 hover:text-white"
                    onClick={() => {
                      trackEvent('purpose_skipped', { location: 'results' });
                      setShowPurposeModal(false);
                    }}
                  >
                    Skip for now
                  </Button>
                </div>
              </DialogContent>
            </Dialog>

            {/* Header */}
            <ResultsHeader
              metadata={metadata!}
              canExport={canExport}
              onCopySummary={handleCopySummary}
              onDownloadSummary={handleDownloadSummaryLocal}
              onDownloadJson={handleDownloadJson}
              onDownloadFullTxt={handleDownloadFullTxt}
            />

            {!canExport && (
              <p className="text-xs text-slate-500 mb-6">
                JSON export is available after the limit is lifted. Summary
                export stays available.
              </p>
            )}

            {/* Banners */}
            <DeviceFreeBanner
              accessMode={metadata?.access?.mode}
              freeUsed={metadata?.access?.free_used}
            />
            <LimitedWarningBanner isLimited={isLimited} />
            <FormatHintCard formatHint={formatHint} />
            <LimitedAccessBanner
              isLimited={isLimited}
              lockedTotal={lockedTotal}
              lockedGroups={lockedGroups}
              onPaywallCta={onPaywallCta}
              onNavigateToUpload={onNavigateToUpload}
            />

            {/* Highlights */}
            <HighlightsCard
              highlights={highlights}
              orderedHighlights={orderedHighlights}
              fieldsExtracted={fieldsExtracted}
              processingMs={processingMs}
              onScrollTo={scrollTo}
            />

            {/* Tab Controls */}
            <div className="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div className="flex items-center gap-3 text-xs text-slate-500 font-mono">
                <span>Focus: {purposeLabel}</span>
                <Button
                  variant="ghost"
                  className="text-slate-400 hover:text-white h-7 px-2"
                  onClick={() => {
                    trackEvent('purpose_prompt_opened', {
                      location: 'results',
                    });
                    setShowPurposeModal(true);
                  }}
                >
                  Change focus
                </Button>
              </div>
              <ToggleGroup
                type="single"
                value={densityMode}
                onValueChange={handleDensityChange}
                className="bg-[#121217] border border-white/10 rounded-lg p-1"
              >
                <ToggleGroupItem
                  value="normal"
                  className="text-xs px-3 py-1 text-slate-300 data-[state=on]:bg-white/10 data-[state=on]:text-white"
                >
                  Normal
                </ToggleGroupItem>
                <ToggleGroupItem
                  value="advanced"
                  className="text-xs px-3 py-1 text-slate-300 data-[state=on]:bg-white/10 data-[state=on]:text-white"
                >
                  Advanced
                </ToggleGroupItem>
              </ToggleGroup>
            </div>

            {/* Tabs */}
            <Tabs
              value={activeTab}
              onValueChange={v => (isTabValue(v) ? setActiveTab(v) : undefined)}
              className="w-full"
            >
              <TabsList className="bg-[#121217] border border-white/5">
                <TabsTrigger value="privacy">Privacy</TabsTrigger>
                <TabsTrigger value="authenticity">Authenticity</TabsTrigger>
                <TabsTrigger value="photography">Photography</TabsTrigger>
                {isAdvanced && (
                  <TabsTrigger value="raw">
                    <span className="inline-flex items-center gap-2">
                      {!canExport && (
                        <Lock className="w-3.5 h-3.5 opacity-70" />
                      )}
                      Raw
                    </span>
                  </TabsTrigger>
                )}
              </TabsList>

              <TabsContent value="privacy" className="mt-6">
                <PrivacyTab
                  metadata={metadata!}
                  gpsCoords={gpsCoords}
                  overlayGps={overlayGps}
                  hasGps={hasGps}
                  embeddedGpsState={embeddedGpsState}
                  gpsMapUrl={gpsMapUrl}
                  captureDateLabel={captureDateLabel}
                  captureDateValue={captureDateValue}
                  localModifiedValue={localModifiedValue}
                  burnedTimestamp={burnedTimestamp}
                  software={software}
                  hashSha256={hashSha256}
                  hashMd5={hashMd5}
                  showOverlayText={showOverlayText}
                  onToggleOverlayText={() => setShowOverlayText(s => !s)}
                  canExport={canExport}
                  isAdvanced={isAdvanced}
                  onScrollTo={scrollTo}
                />
              </TabsContent>

              {/* Additional tabs would be implemented similarly */}
              {/* ... AuthenticityTab, PhotographyTab, RawTab components ... */}
            </Tabs>

            {/* Quality Metrics */}
            {(metadata?.quality_metrics || metadata?.processing_insights) && (
              <div className="mt-8 flex items-center gap-2 text-xs text-slate-500">
                <span>Extraction details</span>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      type="button"
                      className="inline-flex items-center justify-center w-5 h-5 rounded-full border border-white/10 text-slate-400 hover:text-white hover:bg-white/5"
                      aria-label="Extraction details"
                    >
                      i
                    </button>
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs text-xs leading-relaxed">
                    <div className="space-y-1">
                      {metadata?.quality_metrics?.confidence_score ? (
                        <div>
                          Confidence:{' '}
                          {(
                            metadata.quality_metrics.confidence_score * 100
                          ).toFixed(0)}
                          %
                        </div>
                      ) : null}
                      {metadata?.quality_metrics?.extraction_completeness ? (
                        <div>
                          Coverage:{' '}
                          {(
                            metadata.quality_metrics.extraction_completeness *
                            100
                          ).toFixed(0)}
                          %
                        </div>
                      ) : null}
                      {metadata?.processing_insights?.total_fields_extracted ? (
                        <div>
                          Fields extracted:{' '}
                          {metadata.processing_insights.total_fields_extracted.toLocaleString()}
                        </div>
                      ) : null}
                      {metadata?.processing_insights?.processing_ms ? (
                        <div>
                          Processing time:{' '}
                          {(
                            Number(metadata.processing_insights.processing_ms) /
                            1000
                          ).toFixed(1)}
                          s
                        </div>
                      ) : null}
                      {metadata?.quality_metrics?.format_support_level ? (
                        <div>
                          Format support:{' '}
                          {metadata.quality_metrics.format_support_level.replace(
                            /_/g,
                            ' '
                          )}
                        </div>
                      ) : null}
                      {!metadata?.quality_metrics?.confidence_score &&
                      !metadata?.quality_metrics?.extraction_completeness &&
                      !metadata?.processing_insights?.total_fields_extracted &&
                      !metadata?.processing_insights?.processing_ms &&
                      !metadata?.quality_metrics?.format_support_level ? (
                        <div>Quality data not reported for this file.</div>
                      ) : null}
                    </div>
                  </TooltipContent>
                </Tooltip>
              </div>
            )}
          </div>
        </div>
      </Layout>
    </ResultsLayout>
  );
}
