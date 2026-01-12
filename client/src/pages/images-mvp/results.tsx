import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import {
  MapPin,
  Camera,
  Calendar,
  FileImage,
  ShieldAlert,
  Lock,
  ArrowRight,
  CheckCircle2,
  Hash,
  Fingerprint,
  Search,
  Info,
  Clipboard,
  Upload,
  ChevronDown,
  Download,
  FileJson,
  FileText,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

import { PricingModal } from '@/components/images-mvp/pricing-modal';
import { ProgressTracker } from '@/components/images-mvp/progress-tracker';
import { QualityIndicator } from '@/components/images-mvp/quality-indicator';
import { PublicLayout as Layout } from '@/components/public-layout';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/hooks/use-toast';
import { trackImagesMvpEvent } from '@/lib/images-mvp-analytics';

interface MvpMetadata {
  filename: string;
  filesize: string;
  filetype: string;
  mime_type: string;
  gps: Record<string, unknown> | null;
  exif: Record<string, unknown>;
  filesystem?: { created?: string; modified?: string };
  hashes?: Record<string, unknown>;
  file_integrity?: Record<string, unknown>;
  perceptual_hashes?: Record<string, unknown>;
  burned_metadata?: {
    has_burned_metadata: boolean;
    extracted_text?: string | null;
    confidence?: string;
    parsed_data?: {
      gps?: { latitude: number; longitude: number; google_maps_url?: string };
      timestamp?: string;
      plus_code?: string;
      address?: string;
    };
  } | null;
  metadata_comparison?: {
    warnings?: string[];
    summary?: {
      overall_status?: string;
      gps_comparison?: string;
      timestamp_comparison?: string;
    };
  } | null;
  normalized?: Record<string, unknown> | null;
  calculated?: Record<string, unknown> | null;
  processing_ms?: number;
  fields_extracted?: number;
  quality_metrics?: {
    confidence_score?: number;
    extraction_completeness?: number;
    format_support_level?: string;
  };
  processing_insights?: {
    total_fields_extracted?: number;
    processing_time_ms?: number;
  };
  access: {
    trial_granted: boolean;
    trial_email_present: boolean;
    credits_charged?: number;
    credits_required?: number;
    mode?: 'device_free' | 'trial_limited' | 'paid';
    free_used?: number;
  };
  _trial_limited?: boolean;
  client_last_modified_iso?: string;
  registry_summary?: Record<string, unknown>;
  locked_fields?: string[];
  [key: string]: unknown;
}

type TabValue = 'privacy' | 'authenticity' | 'photography' | 'raw';
type PurposeValue = 'privacy' | 'authenticity' | 'photography' | 'explore';
type DensityMode = 'normal' | 'advanced';
type ResultsViewState = 'idle' | 'processing' | 'success' | 'empty' | 'fail';

const PURPOSE_STORAGE_KEY = 'images_mvp_purpose';
const DENSITY_STORAGE_KEY = 'images_mvp_density';

export default function ImagesMvpResults() {
  const [metadata, setMetadata] = useState<MvpMetadata | null>(null);
  const [viewState, setViewState] = useState<ResultsViewState>('processing');
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
  const { toast } = useToast();
  const purposePromptLogged = useRef(false);
  const formatHintLogged = useRef(false);
  const paywallLogged = useRef(false);
  const resultsLogged = useRef(false);

  // Calculate limited report status (must be declared before any useEffect)
  // Report is limited only when in 'trial_limited' mode — device_free is not considered limited
  const isLimitedReport = metadata?.access?.mode === 'trial_limited';
  const canExport = metadata?.access?.mode !== 'trial_limited';

  const hasValue = (value: unknown): boolean => {
    if (value === null || value === undefined) return false;
    if (typeof value === 'boolean') return value;
    if (typeof value === 'number') return Number.isFinite(value);
    if (typeof value === 'string') {
      const trimmed = value.trim();
      return (
        trimmed.length > 0 &&
        trimmed.toLowerCase() !== 'n/a' &&
        trimmed.toLowerCase() !== 'unknown'
      );
    }
    if (Array.isArray(value)) return value.length > 0;
    if (typeof value === 'object') return Object.keys(value).length > 0;
    return true;
  };

  useEffect(() => {
    const stored = sessionStorage.getItem('currentMetadata');
    const status = sessionStorage.getItem('images_mvp_status');
    const errorRaw = sessionStorage.getItem('images_mvp_error');

    if (status === 'fail') {
      setViewState('fail');
      if (errorRaw) {
        try {
          setErrorInfo(JSON.parse(errorRaw));
        } catch {
          setErrorInfo({ message: 'Extraction failed' });
        }
      } else {
        setErrorInfo({ message: 'Extraction failed' });
      }
      return;
    }

    if (!stored) {
      if (status === 'uploading' || status === 'processing') {
        setViewState('processing');
      } else {
        setViewState('idle');
      }
      return;
    }

    try {
      const parsed = JSON.parse(stored) as MvpMetadata;
      setMetadata(parsed);
      const countMeaningfulFields = (obj: unknown): number => {
        if (obj === null || obj === undefined) return 0;
        if (typeof obj !== 'object') return hasValue(obj) ? 1 : 0;
        if (Array.isArray(obj)) return hasValue(obj) ? 1 : 0;
        const record = obj as Record<string, unknown>;
        let count = 0;
        for (const key of Object.keys(record)) {
          if (key.startsWith('_') || key === 'access') continue;
          const value = record[key];
          if (
            value !== null &&
            typeof value === 'object' &&
            !Array.isArray(value)
          ) {
            count += countMeaningfulFields(value);
          } else if (hasValue(value)) {
            count += 1;
          }
        }
        return count;
      };
      const meaningfulCount = countMeaningfulFields(parsed);
      const fieldCount =
        typeof parsed.fields_extracted === 'number'
          ? parsed.fields_extracted
          : typeof parsed.processing_insights?.total_fields_extracted ===
              'number'
            ? parsed.processing_insights.total_fields_extracted
            : 0;
      setViewState(meaningfulCount > 0 ? 'success' : 'empty');
    } catch {
      setViewState('fail');
      setErrorInfo({ message: 'Failed to load results' });
    }
  }, []);

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

  const getFormatHint = (mimeType: string, filename: string) => {
    const normalizedMime = (mimeType || '').toLowerCase();
    const filenameLower = (filename || '').toLowerCase();
    if (normalizedMime.includes('heic') || normalizedMime.includes('heif')) {
      return {
        title: 'HEIC photo detected',
        body: 'HEIC photos (common on iPhones) usually include rich metadata such as capture settings and device details.',
        tone: 'emerald',
      };
    }
    if (normalizedMime.includes('webp')) {
      return {
        title: 'WebP image detected',
        body: 'WebP metadata support varies by source. Some uploads may only include basic file details.',
        tone: 'amber',
      };
    }
    if (normalizedMime.includes('png')) {
      const screenshotHint =
        filenameLower.includes('screenshot') ||
        filenameLower.includes('screen shot');
      return {
        title: screenshotHint ? 'Screenshot detected' : 'PNG image detected',
        body: screenshotHint
          ? 'Screenshots often contain minimal metadata. For richer data, try the original photo.'
          : 'PNG files (especially graphics) often contain minimal metadata compared to camera photos.',
        tone: 'amber',
      };
    }
    if (normalizedMime.includes('jpeg') || normalizedMime.includes('jpg')) {
      return {
        title: 'JPEG photo detected',
        body: 'JPEG photos usually include camera metadata such as device, timestamps, and settings.',
        tone: 'emerald',
      };
    }
    return null;
  };

  const trackEvent = useCallback(
    (event: string, properties: Record<string, unknown> = {}) => {
      trackImagesMvpEvent(event, properties);
    },
    []
  );

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

  useEffect(() => {
    if (densityMode === 'normal' && activeTab === 'raw') {
      setActiveTab('privacy');
    }
  }, [densityMode, activeTab]);

  useEffect(() => {
    if (!showPurposeModal || purposePromptLogged.current) return;
    trackEvent('purpose_prompt_shown', { location: 'results' });
    purposePromptLogged.current = true;
  }, [showPurposeModal, trackEvent]);

  useEffect(() => {
    if (!metadata) return;
    trackEvent('tab_changed', {
      tab: activeTab,
      density: densityMode,
      purpose: purpose || 'unset',
    });
  }, [activeTab, densityMode, metadata, purpose, trackEvent]);

  useEffect(() => {
    if (!metadata || formatHintLogged.current) return;
    const hint = getFormatHint(metadata.mime_type, metadata.filename);
    if (!hint) return;
    trackEvent('format_hint_shown', {
      mime_type: metadata.mime_type,
      hint: hint.title,
    });
    formatHintLogged.current = true;
  }, [metadata, trackEvent]);

  useEffect(() => {
    if (!metadata || resultsLogged.current) return;
    trackEvent('results_viewed', {
      filetype: metadata.filetype,
      mime_type: metadata.mime_type,
    });
    resultsLogged.current = true;
  }, [metadata, trackEvent]);

  useEffect(() => {
    if (!metadata || paywallLogged.current) return;
    const trialLimited = isLimitedReport;
    const summary = metadata.registry_summary?.image as
      | { exif?: number; iptc?: number; xmp?: number }
      | undefined;
    const lockedTotal =
      (summary?.exif ?? 0) + (summary?.iptc ?? 0) + (summary?.xmp ?? 0);
    if (trialLimited && lockedTotal > 0) {
      trackEvent('paywall_preview_shown', {
        locked_total: lockedTotal,
      });
      paywallLogged.current = true;
    }
  }, [metadata, trackEvent]);

  useEffect(() => {
    if (metadata?.filename) {
      document.title = `Results: ${metadata.filename} | MetaExtract`;
    } else {
      document.title = 'MetaExtract | Analysis Results';
    }
  }, [metadata?.filename]);

  type DetailEntry = { path: string; valuePreview: string; value: unknown };

  const previewValue = (value: unknown): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'string')
      return value.length > 180 ? `${value.slice(0, 180)}…` : value;
    if (typeof value === 'number' || typeof value === 'boolean')
      return String(value);

    try {
      const text = JSON.stringify(value);
      return text.length > 180 ? `${text.slice(0, 180)}…` : text;
    } catch {
      return String(value);
    }
  };

  const collectDetailEntries = (
    obj: unknown,
    prefix = '',
    depth = 0,
    maxDepth = 4,
    out: DetailEntry[] = [],
    maxEntries = 200
  ): DetailEntry[] => {
    if (out.length >= maxEntries) return out;
    if (depth > maxDepth) return out;
    if (obj === null || obj === undefined) return out;
    if (typeof obj !== 'object') {
      if (!hasValue(obj)) return out;
      out.push({
        path: prefix || '(root)',
        valuePreview: previewValue(obj),
        value: obj,
      });
      return out;
    }
    if (Array.isArray(obj)) {
      if (!hasValue(obj)) return out;
      out.push({
        path: prefix || '(root)',
        valuePreview: previewValue(obj),
        value: obj,
      });
      return out;
    }
    const record = obj as Record<string, unknown>;
    for (const key of Object.keys(record)) {
      if (key.startsWith('_')) continue;
      if (key === 'access') continue;
      if (key === 'extracted_text') continue;
      const next = prefix ? `${prefix}.${key}` : key;
      const value = record[key];
      if (
        value !== null &&
        typeof value === 'object' &&
        !Array.isArray(value)
      ) {
        collectDetailEntries(value, next, depth + 1, maxDepth, out, maxEntries);
      } else {
        if (!hasValue(value)) continue;
        out.push({
          path: next,
          valuePreview: previewValue(value),
          value,
        });
      }
      if (out.length >= maxEntries) break;
    }
    return out;
  };

  const fieldsFound = useMemo(() => {
    if (!metadata) return 0;
    return collectDetailEntries(metadata, '', 0, 4, [], 1000).length;
  }, [metadata]);

  if (viewState === 'processing') {
    return (
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-3xl">
            <Card className="bg-[#11121a] border-white/10">
              <CardContent className="p-8 text-center text-slate-200">
                Processing your image...
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  if (viewState === 'idle') {
    return (
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-3xl">
            <Card className="bg-[#11121a] border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileImage className="w-5 h-5 text-primary" />
                  Ready when you are
                </CardTitle>
                <CardDescription className="text-slate-200">
                  Upload an image to extract metadata and view the analysis
                  here.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                <Button
                  className="w-full bg-[#6366f1] hover:bg-[#5855eb] text-white"
                  onClick={() => navigate('/images_mvp')}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Upload an image
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
                  onClick={() => navigate('/images_mvp?pricing=1')}
                >
                  Learn about credits
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  if (viewState === 'fail') {
    return (
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-3xl">
            <Card className="bg-[#11121a] border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-amber-400" />
                  Extraction failed
                </CardTitle>
                <CardDescription className="text-slate-200">
                  {errorInfo?.message || 'We could not process this file.'}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                {errorInfo?.status && (
                  <p className="text-xs text-slate-400">
                    Error code: {errorInfo.status}
                  </p>
                )}
                <Button
                  className="w-full bg-[#6366f1] hover:bg-[#5855eb] text-white"
                  onClick={() => navigate('/images_mvp')}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Try another image
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  if (viewState === 'empty' || !metadata) {
    return (
      <Layout showHeader={true} showFooter={true}>
        <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
          <div className="container mx-auto px-4 max-w-3xl">
            <Card className="bg-[#11121a] border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5 text-primary" />
                  No metadata found
                </CardTitle>
                <CardDescription className="text-slate-200">
                  We didn’t detect metadata in this file. Try another image or a
                  different format.
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col gap-3">
                <Button
                  className="w-full bg-[#6366f1] hover:bg-[#5855eb] text-white"
                  onClick={() => navigate('/images_mvp')}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Upload another image
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }
  const creditsRequired = metadata.access?.credits_required ?? 0;
  const creditsCharged = metadata.access?.credits_charged ?? 0;

  const handleDownloadJson = () => {
    if (!canExport) {
      return;
    }
    trackEvent('export_json_downloaded', {
      filetype: metadata.filetype,
      mime_type: metadata.mime_type,
      purpose: purpose || 'unset',
    });
    const payload = JSON.stringify(metadata, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const baseName = metadata.filename?.replace(/\.[^/.]+$/, '') || 'metadata';
    link.href = url;
    link.download = `${baseName}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadFullTxt = () => {
    if (!canExport) {
      return;
    }
    trackEvent('export_full_txt_downloaded', {
      filetype: metadata.filetype,
      mime_type: metadata.mime_type,
      purpose: purpose || 'unset',
    });
    const payload = JSON.stringify(metadata, null, 2);
    const blob = new Blob([payload], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const baseName = metadata.filename?.replace(/\.[^/.]+$/, '') || 'metadata';
    link.href = url;
    link.download = `${baseName}-full.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadSummary = () => {
    const payload = buildSummaryLines();
    const blob = new Blob([payload], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    const baseName = metadata.filename?.replace(/\.[^/.]+$/, '') || 'metadata';
    link.href = url;
    link.download = `${baseName}-summary.txt`;
    link.click();
    URL.revokeObjectURL(url);
    trackEvent('export_summary_downloaded', {
      filetype: metadata.filetype,
      mime_type: metadata.mime_type,
      purpose: purpose || 'unset',
    });
  };

  // Format Date Helper
  const formatDate = (
    dateStr?: string,
    emptyMessage = 'Not present in this file'
  ) => {
    if (!dateStr) return emptyMessage;
    try {
      return new Date(dateStr).toLocaleString();
    } catch {
      return dateStr;
    }
  };

  const getGpsCoords = (gps: Record<string, unknown> | null | undefined) => {
    if (!gps || typeof gps !== 'object') return null;
    const record = gps as Record<string, unknown>;
    const latRaw =
      record.latitude ??
      record.lat ??
      record.GPSLatitude ??
      record.gps_latitude ??
      record.Latitude;
    const lonRaw =
      record.longitude ??
      record.lon ??
      record.lng ??
      record.GPSLongitude ??
      record.gps_longitude ??
      record.Longitude;
    const lat =
      typeof latRaw === 'number' ? latRaw : parseFloat(String(latRaw));
    const lon =
      typeof lonRaw === 'number' ? lonRaw : parseFloat(String(lonRaw));
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    return { latitude: lat, longitude: lon };
  };

  const parseOverlayGps = (burned?: MvpMetadata['burned_metadata']) => {
    const raw = burned?.parsed_data?.gps;
    if (!raw) return null;
    const lat =
      typeof raw.latitude === 'number'
        ? raw.latitude
        : parseFloat(String(raw.latitude));
    const lon =
      typeof raw.longitude === 'number'
        ? raw.longitude
        : parseFloat(String(raw.longitude));
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    return {
      latitude: lat,
      longitude: lon,
      google_maps_url: raw.google_maps_url,
    };
  };

  const gpsCoords = getGpsCoords(metadata.gps);
  const overlayGps = parseOverlayGps(metadata.burned_metadata);
  const hasGps = !!gpsCoords;
  const gpsMapUrl = gpsCoords
    ? ((metadata.gps as Record<string, unknown> | null)?.google_maps_url as
        | string
        | undefined) ||
      `https://maps.google.com/?q=${gpsCoords.latitude},${gpsCoords.longitude}`
    : overlayGps
      ? overlayGps.google_maps_url ||
        `https://maps.google.com/?q=${overlayGps.latitude},${overlayGps.longitude}`
      : '';
  const parseWhatsappFilenameDate = (name?: string) => {
    if (!name) return null;
    const match = name.match(
      /WhatsApp Image (\d{4})-(\d{2})-(\d{2}) at (\d{2})\.(\d{2})\.(\d{2})/i
    );
    if (!match) return null;
    const [, year, month, day, hour, minute, second] = match;
    return new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`);
  };
  const parseExifDate = (value?: string | null) => {
    if (!value) return null;
    // Handle EXIF format: YYYY:MM:DD HH:MM:SS
    const match = value.match(
      /(\\d{4}):(\\d{2}):(\\d{2})[ T](\\d{2}):(\\d{2}):(\\d{2})/
    );
    if (match) {
      const [, y, m, d, hh, mm, ss] = match;
      return new Date(`${y}-${m}-${d}T${hh}:${mm}:${ss}`);
    }
    const dt = new Date(value);
    return Number.isNaN(dt.getTime()) ? null : dt;
  };
  const filenameDate = parseWhatsappFilenameDate(metadata.filename);
  const captureDateFromExif = parseExifDate(
    (metadata.exif?.DateTimeOriginal as string | null | undefined) ||
      (metadata.exif?.CreateDate as string | null | undefined)
  );
  const captureDateLabel = captureDateFromExif
    ? 'CAPTURE DATE'
    : filenameDate
      ? 'FILENAME DATE'
      : 'CAPTURE DATE';
  const captureDateValue = captureDateFromExif
    ? captureDateFromExif.toISOString()
    : filenameDate
      ? filenameDate.toISOString()
      : null;
  const localModifiedValue = metadata.client_last_modified_iso || null;

  const embeddedGpsState = hasGps
    ? 'embedded'
    : overlayGps
      ? 'overlay'
      : 'none';
  const burnedTimestamp =
    metadata.burned_metadata?.parsed_data?.timestamp || null;
  const hashSha256 =
    metadata.hashes?.sha256 || metadata.file_integrity?.sha256 || null;
  const hashMd5 = metadata.hashes?.md5 || metadata.file_integrity?.md5 || null;
  const fieldsExtracted = metadata.fields_extracted ?? null;
  const processingMs = metadata.processing_ms ?? null;
  const software = (metadata.exif?.Software as string | undefined) || null;
  const formatHint = getFormatHint(metadata.mime_type, metadata.filename);
  const formatToneClass =
    formatHint?.tone === 'emerald'
      ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-100'
      : 'border-amber-500/20 bg-amber-500/5 text-amber-100';



  const scrollTo = (tab: typeof activeTab, anchorId: string) => {
    setActiveTab(tab);
    window.setTimeout(() => {
      const el = document.getElementById(anchorId);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  };

  const highlightIcon = (
    intent: 'Privacy' | 'Authenticity' | 'Photography'
  ) => {
    if (intent === 'Privacy') return <MapPin className="w-4 h-4" />;
    if (intent === 'Authenticity') return <Fingerprint className="w-4 h-4" />;
    return <Camera className="w-4 h-4" />;
  };

  const highlightAccent = (
    intent: 'Privacy' | 'Authenticity' | 'Photography'
  ) => {
    if (intent === 'Privacy')
      return 'border-emerald-500/20 bg-emerald-500/5 text-emerald-200';
    if (intent === 'Authenticity')
      return 'border-purple-500/20 bg-purple-500/5 text-purple-200';
    return 'border-blue-500/20 bg-blue-500/5 text-blue-200';
  };

  const highlights: Array<{
    text: string;
    intent: 'Privacy' | 'Authenticity' | 'Photography';
    impact: 'Privacy' | 'Authenticity' | 'Workflow' | 'None';
    confidence: 'High' | 'Medium' | 'Low';
    icon: React.ReactNode;
    accentClass: string;
    target?: { tab: typeof activeTab; anchorId: string };
  }> = [];
  if (captureDateValue) {
    highlights.push({
      text: `Capture time found (${captureDateLabel === 'FILENAME DATE' ? 'from filename' : 'from EXIF'}).`,
      intent: 'Photography',
      impact: 'Workflow',
      confidence: captureDateLabel === 'FILENAME DATE' ? 'Medium' : 'High',
      icon: highlightIcon('Photography'),
      accentClass: highlightAccent('Photography'),
      target: { tab: 'privacy', anchorId: 'section-timestamps' },
    });
  } else {
    highlights.push({
      text: 'Capture time not present in this file (common after sharing apps).',
      intent: 'Photography',
      impact: 'Workflow',
      confidence: 'Medium',
      icon: highlightIcon('Photography'),
      accentClass: highlightAccent('Photography'),
      target: { tab: 'privacy', anchorId: 'section-timestamps' },
    });
  }
  if (embeddedGpsState === 'embedded') {
    highlights.push({
      text: 'Location is embedded in EXIF.',
      intent: 'Privacy',
      impact: 'Privacy',
      confidence: 'High',
      icon: highlightIcon('Privacy'),
      accentClass: highlightAccent('Privacy'),
      target: { tab: 'privacy', anchorId: 'section-location' },
    });
  } else if (embeddedGpsState === 'overlay') {
    highlights.push({
      text: 'Location not embedded in EXIF, but found in overlay text (pixels).',
      intent: 'Privacy',
      impact: 'Privacy',
      confidence: 'Medium',
      icon: highlightIcon('Privacy'),
      accentClass: highlightAccent('Privacy'),
      target: { tab: 'privacy', anchorId: 'section-location' },
    });
  } else {
    highlights.push({
      text: 'Location not present in this file.',
      intent: 'Privacy',
      impact: 'Privacy',
      confidence: 'High',
      icon: highlightIcon('Privacy'),
      accentClass: highlightAccent('Privacy'),
      target: { tab: 'privacy', anchorId: 'section-location' },
    });
  }
  if (hasValue(metadata.exif?.Make) || hasValue(metadata.exif?.Model)) {
    highlights.push({
      text: `Device detected: ${[metadata.exif?.Make, metadata.exif?.Model].filter(Boolean).join(' ')}`,
      intent: 'Photography',
      impact: 'Privacy',
      confidence: 'High',
      icon: highlightIcon('Photography'),
      accentClass: highlightAccent('Photography'),
      target: { tab: 'privacy', anchorId: 'section-device' },
    });
  }
  if (hasValue(software)) {
    highlights.push({
      text: `Software tag present: ${software}`,
      intent: 'Authenticity',
      impact: 'Authenticity',
      confidence: 'High',
      icon: highlightIcon('Authenticity'),
      accentClass: highlightAccent('Authenticity'),
      target: { tab: 'authenticity', anchorId: 'section-auth-signals' },
    });
  } else {
    highlights.push({
      text: 'No editing software tag present (inconclusive).',
      intent: 'Authenticity',
      impact: 'Authenticity',
      confidence: 'Low',
      icon: highlightIcon('Authenticity'),
      accentClass: highlightAccent('Authenticity'),
      target: { tab: 'authenticity', anchorId: 'section-auth-signals' },
    });
  }
  if (hasValue(hashSha256)) {
    highlights.push({
      text: 'SHA-256 hash computed for integrity.',
      intent: 'Authenticity',
      impact: 'Authenticity',
      confidence: 'High',
      icon: highlightIcon('Authenticity'),
      accentClass: highlightAccent('Authenticity'),
      target: { tab: 'privacy', anchorId: 'section-integrity' },
    });
  }

  // Compute preferred intent (moved outside of useMemo to fix hook order issues)
  const preferredIntent =
    purpose === 'authenticity'
      ? 'Authenticity'
      : purpose === 'photography'
        ? 'Photography'
        : 'Privacy';

  // Order highlights by preferred intent (moved outside of useMemo to fix hook order issues)
  const orderedHighlights = (() => {
    // Create a copy of highlights to avoid mutating the original array
    const highlightsCopy = [...highlights];

    // Sort by preferred intent
    highlightsCopy.sort((a, b) => {
      const aScore = a.intent === preferredIntent ? 1 : 0;
      const bScore = b.intent === preferredIntent ? 1 : 0;
      return bScore - aScore;
    });

    return highlightsCopy;
  })();

  const buildSummaryLines = () => {
    const intentLabel = purpose
      ? `${purpose.charAt(0).toUpperCase()}${purpose.slice(1)}`
      : 'Unspecified';
    const lines = [
      `File: ${metadata.filename}`,
      `Type: ${metadata.filetype} (${metadata.mime_type})`,
      `Size: ${metadata.filesize}`,
      `Intent: ${intentLabel}`,
      '',
      'Highlights:',
    ];
    orderedHighlights.slice(0, 6).forEach(h => {
      lines.push(
        `- ${h.text} (Impact: ${h.impact}, Confidence: ${h.confidence})`
      );
    });
    lines.push('');
    lines.push(
      'Limitations: Metadata can be missing or stripped. Absence is not proof.'
    );
    return lines.join('\n');
  };

  const handleCopySummary = async () => {
    try {
      await navigator.clipboard?.writeText(buildSummaryLines());
      toast({
        title: 'Summary copied',
        description: 'Highlights copied to your clipboard.',
      });
      trackEvent('summary_copied', {
        filetype: metadata.filetype,
        mime_type: metadata.mime_type,
        purpose: purpose || 'unset',
      });
    } catch {
      toast({
        title: 'Unable to copy',
        description: 'Clipboard access was blocked by your browser.',
        variant: 'destructive',
      });
    }
  };

  const handlePurposeSelect = (value: PurposeValue) => {
    setPurpose(value);
    localStorage.setItem(PURPOSE_STORAGE_KEY, value);
    trackEvent('purpose_selected', {
      purpose: value,
    });
    if (value === 'explore') {
      setDensityMode('advanced');
      localStorage.setItem(DENSITY_STORAGE_KEY, 'advanced');
      trackEvent('density_changed', {
        mode: 'advanced',
        source: 'purpose_select',
      });
    }
    setActiveTab(mapPurposeToTab(value));
    setShowPurposeModal(false);
  };

  const handleDensityChange = (value: string | null) => {
    if (value !== 'normal' && value !== 'advanced') return;
    setDensityMode(value);
    localStorage.setItem(DENSITY_STORAGE_KEY, value);
    trackEvent('density_changed', { mode: value });
  };

  const isAdvanced = densityMode === 'advanced';
  const purposeLabel = purpose
    ? `${purpose.charAt(0).toUpperCase()}${purpose.slice(1)}`
    : 'Not set';
  const trialEmail =
    typeof window !== 'undefined'
      ? localStorage.getItem('metaextract_trial_email')
      : null;

  const exifEntries = Object.entries(metadata.exif || {}).filter(([, v]) =>
    hasValue(v)
  );
  const exifEntriesForList =
    showAllExif || canExport ? exifEntries : exifEntries.slice(0, 14);

  const registrySummary = metadata.registry_summary?.image as
    | {
        exif?: number;
        iptc?: number;
        xmp?: number;
        mobile?: number;
        perceptual_hashes?: number;
      }
    | undefined;
  const lockedGroups = [
    {
      key: 'exif',
      label: 'Full EXIF fields',
      count: registrySummary?.exif ?? 0,
    },
    {
      key: 'iptc',
      label: 'IPTC (author/rights)',
      count: registrySummary?.iptc ?? 0,
    },
    {
      key: 'xmp',
      label: 'XMP (edit history)',
      count: registrySummary?.xmp ?? 0,
    },
  ].filter(group => group.count > 0);
  const lockedTotal = lockedGroups.reduce((sum, group) => sum + group.count, 0);
  const lockedFields = Array.isArray(metadata.locked_fields)
    ? metadata.locked_fields
        .filter((field): field is string => typeof field === 'string')
        .map(field => field.trim())
        .filter(field => field.length > 0)
    : [];
  const showUnlock =
    !canExport &&
    lockedTotal > 0 &&
    creditsRequired > 0 &&
    creditsCharged === 0;

  const imageWidth = metadata.exif?.ImageWidth;
  const imageHeight = metadata.exif?.ImageHeight ?? metadata.exif?.ImageLength;
  const dimensionsValue =
    hasValue(imageWidth) && hasValue(imageHeight)
      ? `${String(imageWidth)} × ${String(imageHeight)}`
      : null;
  const megapixelsValue = hasValue(metadata.calculated?.megapixels)
    ? String(metadata.calculated?.megapixels)
    : null;
  const colorSpaceNumeric = Number(metadata.exif?.ColorSpace);
  const colorSpaceValue =
    Number.isFinite(colorSpaceNumeric) && colorSpaceNumeric === 1
      ? 'sRGB'
      : hasValue(metadata.exif?.ColorSpace)
        ? String(metadata.exif?.ColorSpace)
        : null;

  const collectPaths = (
    obj: unknown,
    prefix = '',
    depth = 0,
    out: DetailEntry[] = []
  ): DetailEntry[] => {
    if (out.length >= 500) return out;
    if (depth > 5) return out;
    if (obj === null || obj === undefined) return out;
    if (typeof obj !== 'object') {
      out.push({
        path: prefix || '(root)',
        valuePreview: previewValue(obj).slice(0, 140),
        value: obj,
      });
      return out;
    }
    if (Array.isArray(obj)) {
      const preview = previewValue(obj.slice(0, 5));
      out.push({
        path: prefix || '(root)',
        valuePreview: preview.slice(0, 140),
        value: obj,
      });
      return out;
    }
    const record = obj as Record<string, unknown>;
    for (const key of Object.keys(record)) {
      const next = prefix ? `${prefix}.${key}` : key;
      const value = record[key];
      if (
        value !== null &&
        typeof value === 'object' &&
        !Array.isArray(value)
      ) {
        collectPaths(value, next, depth + 1, out);
      } else if (Array.isArray(value)) {
        const preview = previewValue(value.slice(0, 5));
        out.push({
          path: next,
          valuePreview: preview.slice(0, 140),
          value,
        });
      } else {
        if (!hasValue(value)) continue;
        out.push({
          path: next,
          valuePreview: previewValue(value).slice(0, 140),
          value,
        });
      }
      if (out.length >= 500) break;
    }
    return out;
  };

  const allRawPaths = collectPaths(metadata);
  const q = rawSearch.trim().toLowerCase();
  const rawMatches = q
    ? allRawPaths
        .filter(
          e =>
            e.path.toLowerCase().includes(q) ||
            e.valuePreview.toLowerCase().includes(q)
        )
        .slice(0, 80)
    : allRawPaths.slice(0, 40);

  return (
    <Layout showHeader={true} showFooter={true}>
      <div
        className="min-h-screen bg-[#0B0C10] text-white pt-16 sm:pt-20 pb-20"
        data-testid="results-root"
      >
        <div className="container mx-auto px-3 sm:px-4 max-w-4xl">
          <PricingModal
            isOpen={showPricingModal}
            onClose={() => setShowPricingModal(false)}
            defaultEmail={trialEmail || undefined}
          />
          <Dialog open={showPurposeModal} onOpenChange={setShowPurposeModal}>
            <DialogContent className="sm:max-w-[520px] bg-[#0A0A0A] border border-white/10 text-white">
              <DialogTitle className="text-lg font-semibold">
                What brings you here?
              </DialogTitle>
              <DialogDescription className="text-sm text-slate-200">
                Pick a focus so we can highlight what matters most. You can
                change this later.
              </DialogDescription>
              <div className="mt-5 grid grid-cols-1 gap-3">
                <button
                  type="button"
                  onClick={() => handlePurposeSelect('privacy')}
                  className="border border-white/10 rounded-lg p-4 text-left hover:border-primary/60 hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-black"
                >
                  <div className="text-sm font-semibold text-white">
                    Privacy check
                  </div>
                  <div className="text-xs text-slate-200">
                    Find location data, device details, and personal
                    identifiers.
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => handlePurposeSelect('authenticity')}
                  className="border border-white/10 rounded-lg p-4 text-left hover:border-primary/60 hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-black"
                >
                  <div className="text-sm font-semibold text-white">
                    Verify authenticity
                  </div>
                  <div className="text-xs text-slate-200">
                    Check edit history, hashes, and integrity signals.
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => handlePurposeSelect('photography')}
                  className="border border-white/10 rounded-lg p-4 text-left hover:border-primary/60 hover:bg-white/5 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-black"
                >
                  <div className="text-sm font-semibold text-white">
                    Photography details
                  </div>
                  <div className="text-xs text-slate-200">
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
                  className="text-slate-200 hover:text-white"
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
          <div className="mb-6 sm:mb-8 flex flex-col gap-3 sm:gap-4">
            <div className="min-w-full">
              <h1 className="text-xl sm:text-2xl font-bold flex items-center gap-2 break-words">
                <FileImage className="w-5 h-5 sm:w-6 sm:h-6 text-primary shrink-0" />
                <span title={metadata.filename} className="line-clamp-2">
                  {metadata.filename}
                </span>
              </h1>
              <p
                className="text-slate-200 text-xs sm:text-sm font-mono mt-1 break-words"
                data-testid="key-field-mime-type"
              >
                {metadata.filesize} • {metadata.mime_type}
              </p>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap items-stretch sm:items-center w-full sm:w-auto">
              <Button
                variant="outline"
                onClick={() => navigate('/images_mvp')}
                className="border-white/10 hover:bg-white/5 w-full sm:w-auto"
              >
                Analyze Another Photo
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    className="border-white/10 hover:bg-white/5 flex items-center gap-2 w-full sm:w-auto justify-center sm:justify-between"
                  >
                    <Clipboard className="w-4 h-4" />
                    <span className="flex-1 sm:flex-none">Summary actions</span>
                    <ChevronDown className="w-4 h-4 text-slate-200" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="start"
                  className="border-[#1b1b24] bg-[#050608] text-white"
                >
                  <DropdownMenuItem onSelect={handleCopySummary}>
                    <Clipboard className="w-4 h-4 text-slate-200" />
                    Copy summary
                  </DropdownMenuItem>
                  <DropdownMenuItem onSelect={handleDownloadSummary}>
                    <FileText className="w-4 h-4 text-slate-200" />
                    Download summary
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    className="border-white/10 hover:bg-white/5 flex items-center gap-2 w-full sm:w-auto justify-center sm:justify-between"
                  >
                    <Download className="w-4 h-4" />
                    <span className="flex-1 sm:flex-none">Export data</span>
                    <ChevronDown className="w-4 h-4 text-slate-200" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="start"
                  className="border-[#1b1b24] bg-[#050608] text-white"
                >
                  <DropdownMenuItem
                    onSelect={handleDownloadJson}
                    disabled={!canExport}
                  >
                    <FileJson className="w-4 h-4 text-slate-200" />
                    Download JSON
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={handleDownloadFullTxt}
                    disabled={!canExport}
                  >
                    <FileText className="w-4 h-4 text-slate-200" />
                    Download full report (txt)
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          {!canExport && (
            <p className="text-xs text-slate-500 mb-6">
              JSON export is available after credits are applied. Summary export
              stays available.
            </p>
          )}

          {metadata?.access?.mode === 'device_free' && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8 p-4 bg-primary/10 border border-primary/20 rounded-lg flex items-start gap-3"
            >
              <Info className="w-5 h-5 text-primary shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-primary text-sm mb-1">
                  Free check used ({metadata.access?.free_used ?? 1}/2). Credits not used yet.
                </h4>
                <p className="text-slate-200 text-xs leading-relaxed">
                  Sensitive identifiers hidden: exact GPS, device IDs, owner/contact fields, and OCR-extracted address text. Credits are charged after 2 free checks.
                </p>
              </div>
            </motion.div>
          )}

          {isLimitedReport && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8 p-4 bg-primary/10 border border-primary/20 rounded-lg flex items-start gap-3"
            >
              <ShieldAlert className="w-5 h-5 text-primary shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-primary text-sm mb-1">
                  Limited report
                </h4>
                <p className="text-slate-200 text-xs leading-relaxed">
                  You are viewing a limited free report. Raw IPTC and XMP data
                  has been summarized or redacted. Use credits to view the full
                  report and raw exports.
                </p>
              </div>
            </motion.div>
          )}
          {isLimitedReport && lockedFields.length > 0 && (
            <Card className="mb-6 bg-[#121217] border-white/10">
              <CardHeader>
                <CardTitle className="text-sm font-mono text-slate-200">
                  LOCKED FIELDS PREVIEW
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Field names are visible, values are hidden.{' '}
                  {lockedFields.length} total locked fields.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  {lockedFields.slice(0, 12).map(field => (
                    <div
                      key={field}
                      className="flex items-center justify-between border border-white/5 rounded px-3 py-2 bg-white/5"
                    >
                      <span className="text-slate-200 truncate pr-2">
                        {field}
                      </span>
                      <span className="text-slate-500">•••</span>
                    </div>
                  ))}
                </div>
                {lockedFields.length > 12 && (
                  <div className="text-xs text-slate-500">
                    +{lockedFields.length - 12} more locked fields hidden
                  </div>
                )}
              </CardContent>
            </Card>
          )}
          {formatHint && (
            <Card className={`mb-6 border ${formatToneClass}`}>
              <CardContent className="pt-6 flex items-start gap-3 text-sm">
                <Info className="w-5 h-5 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">
                    {formatHint.title}
                  </div>
                  <div className="text-xs text-slate-200 mt-1">
                    {formatHint.body}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          {showUnlock && (
            <Card className="mb-6 bg-[#121217] border-white/10">
              <CardHeader>
                <CardTitle className="text-sm font-mono text-slate-200">
                  UNLOCK FULL REPORT
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-sm">
                <div className="text-slate-200">
                  Use credits to unlock {lockedTotal} additional fields for this
                  file.
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {lockedGroups.slice(0, 6).map(group => (
                    <div
                      key={group.key}
                      className="flex items-center justify-between border border-white/5 rounded px-3 py-2 bg-white/5"
                    >
                      <span className="text-slate-200">{group.label}</span>
                      <span className="text-slate-200 font-mono">
                        {group.count}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    onClick={() => {
                      trackEvent('paywall_cta_clicked', {
                        locked_total: lockedTotal,
                      });
                      setShowPricingModal(true);
                    }}
                    className="bg-primary text-black hover:bg-primary/90"
                  >
                    Get credits
                  </Button>
                  <Button
                    variant="outline"
                    className="border-white/10 hover:bg-white/5"
                    onClick={() => navigate('/images_mvp')}
                  >
                    Analyze another file
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <Card className="bg-[#121217] border-white/5 mb-6">
            <CardHeader>
              <CardTitle className="text-sm font-mono text-slate-200">
                HIGHLIGHTS
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {orderedHighlights.slice(0, 6).map((h, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() =>
                    h.target
                      ? scrollTo(h.target.tab, h.target.anchorId)
                      : undefined
                  }
                  className={`w-full text-left flex items-start gap-3 rounded-lg border px-3 py-2 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-black ${h.accentClass} ${h.target ? 'hover:bg-white/5' : ''}`}
                >
                  <div className="mt-0.5 opacity-90">{h.icon}</div>
                  <div className="flex-1">
                    <div className="text-sm">{h.text}</div>
                    <div className="mt-2 flex flex-wrap gap-2 text-[10px] font-mono">
                      <span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 text-slate-200">
                        Impact: {h.impact}
                      </span>
                      <span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 text-slate-200">
                        Confidence: {h.confidence}
                      </span>
                    </div>
                  </div>
                </button>
              ))}
              <div className="text-xs text-slate-500">
                Limitations: Metadata can be missing or stripped. Absence is not
                proof.
              </div>
              {(fieldsExtracted || fieldsFound || processingMs) && (
                <div className="pt-2 text-xs text-slate-500 font-mono">
                  {fieldsExtracted ? `${fieldsExtracted} fields checked` : null}
                  {fieldsExtracted && (fieldsFound || processingMs)
                    ? ' • '
                    : null}
                  {fieldsFound ? `${fieldsFound} fields found` : null}
                  {fieldsFound && processingMs ? ' • ' : null}
                  {processingMs ? `${Math.round(processingMs)} ms` : null}
                </div>
              )}
            </CardContent>
          </Card>

          <div className="mb-4 flex flex-col gap-3">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div className="flex items-center gap-2 sm:gap-3 text-xs text-slate-500 font-mono">
                <span className="whitespace-nowrap">
                  Focus: {typeof purposeLabel === 'string' ? purposeLabel : ''}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-slate-200 hover:text-white h-7 px-2 text-xs"
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
                className="bg-[#121217] border border-white/10 rounded-lg p-1 w-fit"
              >
                <ToggleGroupItem
                  value="normal"
                  className="text-xs px-2 sm:px-3 py-1 text-slate-200 data-[state=on]:bg-white/10 data-[state=on]:text-white"
                >
                  Normal
                </ToggleGroupItem>
                <ToggleGroupItem
                  value="advanced"
                  className="text-xs px-2 sm:px-3 py-1 text-slate-200 data-[state=on]:bg-white/10 data-[state=on]:text-white"
                >
                  Advanced
                </ToggleGroupItem>
              </ToggleGroup>
            </div>
          </div>

          <Tabs
            value={activeTab}
            onValueChange={v => (isTabValue(v) ? setActiveTab(v) : undefined)}
            className="w-full"
          >
            <TabsList
              className="bg-[#121217] border border-white/5 overflow-x-auto flex-nowrap"
              aria-label="Metadata categories"
            >
              <TabsTrigger
                value="privacy"
                className="text-xs sm:text-sm whitespace-nowrap"
              >
                Privacy
              </TabsTrigger>
              <TabsTrigger
                value="authenticity"
                className="text-xs sm:text-sm whitespace-nowrap"
              >
                Authenticity
              </TabsTrigger>
              <TabsTrigger
                value="photography"
                className="text-xs sm:text-sm whitespace-nowrap"
              >
                Photography
              </TabsTrigger>
              {isAdvanced && (
                <TabsTrigger
                  value="raw"
                  className="text-xs sm:text-sm whitespace-nowrap"
                >
                  <span className="inline-flex items-center gap-1 sm:gap-2">
                    {!canExport && (
                      <Lock
                        className="w-3 h-3 sm:w-3.5 sm:h-3.5 opacity-70"
                        aria-hidden="true"
                      />
                    )}
                    Raw
                  </span>
                </TabsTrigger>
              )}
            </TabsList>

            <TabsContent value="privacy" className="mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Location Card */}
                <Card
                  className="bg-[#121217] border-white/5"
                  id="section-location"
                >
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-200">
                      <MapPin className="w-4 h-4" aria-hidden="true" /> LOCATION
                      DATA
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {hasGps && gpsCoords ? (
                      <div className="space-y-4">
                        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-200 text-sm flex items-center gap-2">
                          <ShieldAlert className="w-5 h-5" />
                          <span>Location data present in this file.</span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm font-mono text-white">
                          <div>
                            <span className="text-slate-500 block text-xs">
                              LATITUDE
                            </span>
                            {gpsCoords.latitude}
                          </div>
                          <div>
                            <span className="text-slate-500 block text-xs">
                              LONGITUDE
                            </span>
                            {gpsCoords.longitude}
                          </div>
                        </div>
                        {gpsMapUrl && (
                          <a
                            href={gpsMapUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block w-full py-2 bg-white/5 hover:bg-white/10 text-center rounded text-sm transition-colors text-primary"
                          >
                            View on Google Maps{' '}
                            <ArrowRight className="w-3 h-3 inline ml-1" />
                          </a>
                        )}
                      </div>
                    ) : overlayGps ? (
                      <div className="space-y-4">
                        <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-200 text-sm flex items-center gap-2">
                          <ShieldAlert className="w-5 h-5" />
                          <span>
                            Overlay GPS detected from burned-in text (pixels).
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm font-mono text-white">
                          <div>
                            <span className="text-slate-500 block text-xs">
                              LATITUDE (Overlay)
                            </span>
                            {overlayGps.latitude}
                          </div>
                          <div>
                            <span className="text-slate-500 block text-xs">
                              LONGITUDE (Overlay)
                            </span>
                            {overlayGps.longitude}
                          </div>
                        </div>
                        {gpsMapUrl && (
                          <a
                            href={gpsMapUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block w-full py-2 bg-white/5 hover:bg-white/10 text-center rounded text-sm transition-colors text-primary"
                          >
                            View on Google Maps{' '}
                            <ArrowRight className="w-3 h-3 inline ml-1" />
                          </a>
                        )}
                        {(burnedTimestamp ||
                          metadata.burned_metadata?.parsed_data?.plus_code) && (
                          <div className="text-xs text-slate-200 space-y-1">
                            {burnedTimestamp && (
                              <div>
                                <span className="text-slate-500">
                                  Overlay time:
                                </span>{' '}
                                {burnedTimestamp}
                              </div>
                            )}
                            {metadata.burned_metadata?.parsed_data
                              ?.plus_code && (
                              <div>
                                <span className="text-slate-500">
                                  Plus code:
                                </span>{' '}
                                {metadata.burned_metadata.parsed_data.plus_code}
                              </div>
                            )}
                          </div>
                        )}
                        <div className="pt-2">
                          <Button
                            variant="outline"
                            className="border-white/10 hover:bg-white/5 w-full"
                            onClick={() => setShowOverlayText(s => !s)}
                          >
                            {showOverlayText
                              ? 'Hide overlay text'
                              : 'View overlay text'}
                          </Button>
                          {showOverlayText && (
                            <div className="mt-3 text-xs text-slate-200 bg-black/30 border border-white/5 rounded p-3 max-h-40 overflow-auto">
                              {metadata.burned_metadata?.extracted_text?.slice(
                                0,
                                1200
                              ) || 'Text not available'}
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="py-8 text-center">
                        <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3 opacity-20" />
                        <p className="text-emerald-500 font-bold">
                          Location not present
                        </p>
                        <p className="text-slate-500 text-xs mt-1">
                          No GPS coordinates were found in this file.
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Device Info */}
                <Card
                  className="bg-[#121217] border-white/5"
                  id="section-device"
                >
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-200">
                      <Camera className="w-4 h-4" aria-hidden="true" /> DEVICE
                      INFORMATION
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 gap-4">
                      {!hasValue(metadata.exif?.Make) &&
                      !hasValue(metadata.exif?.Model) ? (
                        <div className="text-xs text-slate-500">
                          No camera make/model tags present in this file.
                        </div>
                      ) : (
                        <>
                          {hasValue(metadata.exif?.Make) && (
                            <div className="pb-3 border-b border-white/5">
                              <span className="text-slate-500 block text-xs font-mono mb-1">
                                CAMERA MAKE
                              </span>
                              <span className="text-white font-medium">
                                {String(metadata.exif?.Make)}
                              </span>
                            </div>
                          )}
                          {hasValue(metadata.exif?.Model) && (
                            <div className="pb-3 border-b border-white/5">
                              <span className="text-slate-500 block text-xs font-mono mb-1">
                                CAMERA MODEL
                              </span>
                              <span className="text-white font-medium">
                                {String(metadata.exif?.Model)}
                              </span>
                            </div>
                          )}
                        </>
                      )}
                      {hasValue(software) && (
                        <div>
                          <span className="text-slate-500 block text-xs font-mono mb-1">
                            SOFTWARE
                          </span>
                          <span className="text-white font-medium">
                            {software}
                          </span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Timestamps */}
                <Card
                  className="bg-[#121217] border-white/5"
                  id="section-timestamps"
                >
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-200">
                      <Calendar className="w-4 h-4" aria-hidden="true" />{' '}
                      TIMESTAMPS
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 gap-4">
                      <div className="pb-3 border-b border-white/5">
                        <span className="text-slate-500 block text-xs font-mono mb-1">
                          {captureDateLabel}
                        </span>
                        <span className="text-white font-medium">
                          {captureDateValue
                            ? formatDate(captureDateValue)
                            : 'Not present in this file'}
                        </span>
                      </div>
                      {hasValue(burnedTimestamp) && (
                        <div className="pb-3 border-b border-white/5">
                          <span className="text-slate-500 block text-xs font-mono mb-1">
                            OVERLAY TIMESTAMP
                          </span>
                          <span className="text-white font-medium">
                            {burnedTimestamp}
                          </span>
                        </div>
                      )}
                      <div>
                        <span className="text-slate-500 block text-xs font-mono mb-1">
                          LOCAL FILE MODIFIED
                        </span>
                        <span className="text-white font-medium">
                          {formatDate(
                            localModifiedValue || undefined,
                            'Not available (browser did not provide)'
                          )}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Hidden Data Summary */}
                <Card className="bg-[#121217] border-white/5">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-200">
                      <Lock className="w-4 h-4" aria-hidden="true" /> HIDDEN
                      DATA
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {(() => {
                      const exifKeys = Object.keys(metadata.exif || {});
                      const hasMakerNotes =
                        hasValue(metadata.exif?.MakerNote) ||
                        exifKeys.some(k => k.toLowerCase().includes('maker'));
                      const serial =
                        (metadata.exif?.BodySerialNumber as
                          | string
                          | undefined) ||
                        (metadata.exif?.LensSerialNumber as
                          | string
                          | undefined) ||
                        (metadata.exif?.SerialNumber as string | undefined) ||
                        null;
                      const colorProfile = colorSpaceValue;

                      if (
                        !hasMakerNotes &&
                        !hasValue(serial) &&
                        !hasValue(colorProfile)
                      ) {
                        return (
                          <div className="text-xs text-slate-500">
                            No hidden identifiers present in this file.
                          </div>
                        );
                      }

                      return (
                        <ul className="space-y-3">
                          {hasMakerNotes && (
                            <li className="flex justify-between text-sm">
                              <span className="text-slate-200">MakerNotes</span>
                              <span className="text-red-400">Detected</span>
                            </li>
                          )}
                          {hasValue(serial) && (
                            <li className="flex justify-between text-sm">
                              <span className="text-slate-200">
                                Serial Numbers
                              </span>
                              <span className="text-slate-200 truncate max-w-[55%]">
                                {serial}
                              </span>
                            </li>
                          )}
                          {hasValue(colorProfile) && (
                            <li className="flex justify-between text-sm">
                              <span className="text-slate-200">
                                Color Profile
                              </span>
                              <span className="text-slate-200">
                                {colorProfile}
                              </span>
                            </li>
                          )}
                        </ul>
                      );
                    })()}
                  </CardContent>
                </Card>

                {/* Integrity */}
                {(hasValue(hashSha256) || hasValue(hashMd5)) && (
                  <Card
                    className="bg-[#121217] border-white/5"
                    id="section-integrity"
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-200">
                        <Hash className="w-4 h-4" aria-hidden="true" />{' '}
                        INTEGRITY
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm font-mono">
                      {hasValue(hashSha256) && (
                        <div className="flex justify-between gap-3">
                          <span className="text-slate-200">SHA256</span>
                          <span className="text-slate-200 truncate max-w-[60%]">
                            {String(hashSha256)}
                          </span>
                        </div>
                      )}
                      {hasValue(hashMd5) && (
                        <div className="flex justify-between gap-3">
                          <span className="text-slate-200">MD5</span>
                          <span className="text-slate-200 truncate max-w-[60%]">
                            {String(hashMd5)}
                          </span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                {isAdvanced && (
                  <Card className="bg-[#121217] border-white/5 md:col-span-2">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-200">
                        ADVANCED DETAILS
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Accordion
                        type="single"
                        collapsible
                        className="border-white/10"
                      >
                        <AccordionItem
                          value="privacy-advanced"
                          className="border-white/10"
                        >
                          <AccordionTrigger className="text-slate-200 hover:no-underline">
                            Privacy details (filtered)
                          </AccordionTrigger>
                          <AccordionContent>
                            {(() => {
                              const maxEntries = canExport ? 200 : 20;
                              const details = collectDetailEntries(
                                {
                                  location: {
                                    embedded_gps: gpsCoords,
                                    overlay_gps: overlayGps,
                                    overlay_plus_code:
                                      metadata.burned_metadata?.parsed_data
                                        ?.plus_code,
                                    overlay_address:
                                      metadata.burned_metadata?.parsed_data
                                        ?.address,
                                  },
                                  timestamps: {
                                    capture_date: captureDateValue || null,
                                    overlay_timestamp: burnedTimestamp,
                                    local_file_modified: localModifiedValue,
                                  },
                                  device: {
                                    make: metadata.exif?.Make,
                                    model: metadata.exif?.Model,
                                    software,
                                  },
                                  identifiers: {
                                    maker_notes_detected:
                                      hasValue(metadata.exif?.MakerNote) ||
                                      Object.keys(metadata.exif || {}).some(k =>
                                        k.toLowerCase().includes('maker')
                                      ),
                                    serial_numbers:
                                      metadata.exif?.BodySerialNumber ||
                                      metadata.exif?.LensSerialNumber ||
                                      metadata.exif?.SerialNumber,
                                  },
                                  registry_summary:
                                    metadata.registry_summary ?? null,
                                },
                                '',
                                0,
                                4,
                                [],
                                maxEntries
                              );

                              if (details.length === 0) {
                                return (
                                  <div className="text-xs text-slate-500">
                                    No additional fields in this view.
                                  </div>
                                );
                              }

                              return (
                                <>
                                  {!canExport && (
                                    <div className="text-xs text-slate-500 mb-3">
                                      Showing the first {maxEntries} entries.
                                      Use credits to unlock the full report and
                                      search everything.
                                    </div>
                                  )}
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                    {details.map(d => (
                                      <button
                                        key={d.path}
                                        type="button"
                                        className="text-left bg-white/5 border border-white/5 rounded px-3 py-2 hover:bg-white/10 transition-colors min-h-[44px] flex flex-col justify-center"
                                        onClick={() =>
                                          navigator.clipboard?.writeText(
                                            JSON.stringify(
                                              { [d.path]: d.value },
                                              null,
                                              2
                                            )
                                          )
                                        }
                                      >
                                        <div className="text-xs font-mono text-slate-200 truncate">
                                          {d.path}
                                        </div>
                                        <div className="text-xs text-slate-500 truncate">
                                          {d.valuePreview}
                                        </div>
                                      </button>
                                    ))}
                                  </div>
                                </>
                              );
                            })()}
                          </AccordionContent>
                        </AccordionItem>
                      </Accordion>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            <TabsContent value="authenticity" className="mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card
                  className="bg-[#121217] border-white/5"
                  id="section-auth-signals"
                >
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-200">
                      AUTHENTICITY SIGNALS
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <div className="text-slate-200">
                      <span className="text-slate-500 block text-xs font-mono mb-1">
                        EDIT SOFTWARE
                      </span>
                      <span className="text-white">
                        {hasValue(software)
                          ? software
                          : 'No tag present (inconclusive)'}
                      </span>
                    </div>
                    <div className="text-slate-200">
                      <span className="text-slate-500 block text-xs font-mono mb-1">
                        METADATA STATE
                      </span>
                      <span className="text-white">
                        {metadata.metadata_comparison?.summary
                          ?.overall_status || 'Not available for this file'}
                      </span>
                    </div>
                    {metadata.metadata_comparison?.warnings?.length ? (
                      <ul className="list-disc pl-5 text-slate-200 text-xs space-y-1">
                        {metadata.metadata_comparison.warnings
                          .slice(0, 3)
                          .map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                      </ul>
                    ) : (
                      <div className="text-xs text-slate-500">
                        No additional authenticity warnings present.
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card className="bg-[#121217] border-white/5">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-200">
                      FINGERPRINTS
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm font-mono">
                    {hasValue(metadata.perceptual_hashes?.phash) && (
                      <div className="flex justify-between gap-3">
                        <span className="text-slate-200">pHash</span>
                        <span className="text-slate-200 truncate max-w-[60%]">
                          {String(metadata.perceptual_hashes?.phash)}
                        </span>
                      </div>
                    )}
                    {hasValue(metadata.perceptual_hashes?.dhash) && (
                      <div className="flex justify-between gap-3">
                        <span className="text-slate-200">dHash</span>
                        <span className="text-slate-200 truncate max-w-[60%]">
                          {String(metadata.perceptual_hashes?.dhash)}
                        </span>
                      </div>
                    )}
                    {!hasValue(metadata.perceptual_hashes?.phash) &&
                      !hasValue(metadata.perceptual_hashes?.dhash) && (
                        <div className="text-xs text-slate-500">
                          Perceptual hashes not present for this file.
                        </div>
                      )}
                  </CardContent>
                </Card>

                {isAdvanced && (
                  <Card className="bg-[#121217] border-white/5 md:col-span-2">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-200">
                        ADVANCED DETAILS
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Accordion
                        type="single"
                        collapsible
                        className="border-white/10"
                      >
                        <AccordionItem
                          value="auth-advanced"
                          className="border-white/10"
                        >
                          <AccordionTrigger className="text-slate-200 hover:no-underline">
                            Authenticity details (filtered)
                          </AccordionTrigger>
                          <AccordionContent>
                            {(() => {
                              const maxEntries = canExport ? 200 : 20;
                              const details = collectDetailEntries(
                                {
                                  hashes: metadata.hashes ?? null,
                                  file_integrity:
                                    metadata.file_integrity ?? null,
                                  perceptual_hashes:
                                    metadata.perceptual_hashes ?? null,
                                  metadata_comparison:
                                    metadata.metadata_comparison ?? null,
                                  software,
                                  processing: {
                                    fields_extracted: fieldsExtracted,
                                    processing_ms: processingMs,
                                  },
                                },
                                '',
                                0,
                                4,
                                [],
                                maxEntries
                              );

                              if (details.length === 0) {
                                return (
                                  <div className="text-xs text-slate-500">
                                    No additional fields in this view.
                                  </div>
                                );
                              }

                              return (
                                <>
                                  {!canExport && (
                                    <div className="text-xs text-slate-500 mb-3">
                                      Showing the first {maxEntries} entries.
                                      Use credits to unlock the full report and
                                      search everything.
                                    </div>
                                  )}
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                    {details.map(d => (
                                      <button
                                        key={d.path}
                                        type="button"
                                        className="text-left bg-white/5 border border-white/5 rounded px-3 py-2 hover:bg-white/10 transition-colors min-h-[44px] flex flex-col justify-center"
                                        onClick={() =>
                                          navigator.clipboard?.writeText(
                                            JSON.stringify(
                                              { [d.path]: d.value },
                                              null,
                                              2
                                            )
                                          )
                                        }
                                      >
                                        <div className="text-xs font-mono text-slate-200 truncate">
                                          {d.path}
                                        </div>
                                        <div className="text-xs text-slate-500 truncate">
                                          {d.valuePreview}
                                        </div>
                                      </button>
                                    ))}
                                  </div>
                                </>
                              );
                            })()}
                          </AccordionContent>
                        </AccordionItem>
                      </Accordion>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            <TabsContent value="photography" className="mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="bg-[#121217] border-white/5">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-200">
                      CAMERA SETTINGS
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    {hasValue(metadata.normalized?.exposure_triangle) && (
                      <div className="text-slate-200">
                        <span className="text-slate-500 block text-xs font-mono mb-1">
                          EXPOSURE
                        </span>
                        <span className="text-white">
                          {String(metadata.normalized?.exposure_triangle)}
                        </span>
                      </div>
                    )}
                    <div className="grid grid-cols-2 gap-4 font-mono text-xs">
                      {hasValue(metadata.exif?.ISO) && (
                        <div>
                          <span className="text-slate-500 block">ISO</span>
                          <span className="text-slate-200">
                            {String(metadata.exif?.ISO)}
                          </span>
                        </div>
                      )}
                      {hasValue(metadata.exif?.FNumber) && (
                        <div>
                          <span className="text-slate-500 block">APERTURE</span>
                          <span className="text-slate-200">
                            f/{String(metadata.exif?.FNumber)}
                          </span>
                        </div>
                      )}
                      {hasValue(metadata.exif?.ExposureTime) && (
                        <div>
                          <span className="text-slate-500 block">SHUTTER</span>
                          <span className="text-slate-200">
                            {String(metadata.exif?.ExposureTime)}s
                          </span>
                        </div>
                      )}
                      {hasValue(metadata.exif?.FocalLength) && (
                        <div>
                          <span className="text-slate-500 block">
                            FOCAL LENGTH
                          </span>
                          <span className="text-slate-200">
                            {String(metadata.exif?.FocalLength)}mm
                          </span>
                        </div>
                      )}
                    </div>
                    {!hasValue(metadata.exif?.ISO) &&
                      !hasValue(metadata.exif?.FNumber) &&
                      !hasValue(metadata.exif?.ExposureTime) &&
                      !hasValue(metadata.exif?.FocalLength) && (
                        <div className="text-xs text-slate-500">
                          No camera setting fields present in this file.
                        </div>
                      )}
                  </CardContent>
                </Card>

                <Card className="bg-[#121217] border-white/5">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-200">
                      IMAGE INFO
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    {!dimensionsValue &&
                    !megapixelsValue &&
                    !colorSpaceValue ? (
                      <div className="text-xs text-slate-500">
                        No image info fields present in this file.
                      </div>
                    ) : (
                      <>
                        {dimensionsValue && (
                          <div className="text-slate-200">
                            <span className="text-slate-500 block text-xs font-mono mb-1">
                              DIMENSIONS
                            </span>
                            <span className="text-white">
                              {dimensionsValue}
                            </span>
                          </div>
                        )}
                        {megapixelsValue && (
                          <div className="text-slate-200">
                            <span className="text-slate-500 block text-xs font-mono mb-1">
                              MEGAPIXELS
                            </span>
                            <span className="text-white">
                              {megapixelsValue}
                            </span>
                          </div>
                        )}
                        {colorSpaceValue && (
                          <div className="text-slate-200">
                            <span className="text-slate-500 block text-xs font-mono mb-1">
                              COLOR SPACE
                            </span>
                            <span className="text-white">
                              {colorSpaceValue}
                            </span>
                          </div>
                        )}
                      </>
                    )}
                  </CardContent>
                </Card>

                <Card className="bg-[#121217] border-white/5 md:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-200">
                      EXIF FIELDS
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="text-xs text-slate-500">
                      {exifEntries.length} fields present
                      {!canExport && exifEntries.length > 14
                        ? ' • Use credits to see all fields'
                        : ''}
                    </div>
                    {exifEntries.length === 0 ? (
                      <div className="text-xs text-slate-500">
                        No EXIF fields present in this file.
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
                        {exifEntriesForList.map(([k, v]) => (
                          <div
                            key={k}
                            className="flex justify-between gap-3 bg-white/5 border border-white/5 rounded px-3 py-2"
                          >
                            <span className="text-slate-200 truncate">{k}</span>
                            <span className="text-slate-200 truncate max-w-[55%]">
                              {String(v)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                    {exifEntries.length > 14 && (
                      <div className="pt-2">
                        <Button
                          variant="outline"
                          className="border-white/10 hover:bg-white/5"
                          onClick={() => setShowAllExif(s => !s)}
                        >
                          {showAllExif ? 'Show fewer' : 'Show more'}
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {isAdvanced && (
                  <Card className="bg-[#121217] border-white/5 md:col-span-2">
                    <CardHeader>
                      <CardTitle className="text-sm font-mono text-slate-200">
                        ADVANCED DETAILS
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Accordion
                        type="single"
                        collapsible
                        className="border-white/10"
                      >
                        <AccordionItem
                          value="photo-advanced"
                          className="border-white/10"
                        >
                          <AccordionTrigger className="text-slate-200 hover:no-underline">
                            Photography details (filtered)
                          </AccordionTrigger>
                          <AccordionContent>
                            {(() => {
                              const maxEntries = canExport ? 200 : 20;
                              const details = collectDetailEntries(
                                {
                                  camera: {
                                    make: metadata.exif?.Make,
                                    model: metadata.exif?.Model,
                                  },
                                  capture: {
                                    capture_date: captureDateValue || null,
                                    date_source: captureDateLabel,
                                  },
                                  settings: {
                                    iso: metadata.exif?.ISO,
                                    f_number: metadata.exif?.FNumber,
                                    exposure_time: metadata.exif?.ExposureTime,
                                    focal_length: metadata.exif?.FocalLength,
                                    focal_length_35mm:
                                      metadata.exif?.FocalLengthIn35mmFormat,
                                  },
                                  image: {
                                    dimensions: dimensionsValue,
                                    megapixels: megapixelsValue,
                                    color_space: colorSpaceValue,
                                  },
                                  normalized: metadata.normalized ?? null,
                                  calculated: metadata.calculated ?? null,
                                },
                                '',
                                0,
                                4,
                                [],
                                maxEntries
                              );

                              if (details.length === 0) {
                                return (
                                  <div className="text-xs text-slate-500">
                                    No additional fields in this view.
                                  </div>
                                );
                              }

                              return (
                                <>
                                  {!canExport && (
                                    <div className="text-xs text-slate-500 mb-3">
                                      Showing the first {maxEntries} entries.
                                      Use credits to unlock the full report and
                                      search everything.
                                    </div>
                                  )}
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                    {details.map(d => (
                                      <button
                                        key={d.path}
                                        type="button"
                                        className="text-left bg-white/5 border border-white/5 rounded px-3 py-2 hover:bg-white/10 transition-colors min-h-[44px] flex flex-col justify-center"
                                        onClick={() =>
                                          navigator.clipboard?.writeText(
                                            JSON.stringify(
                                              { [d.path]: d.value },
                                              null,
                                              2
                                            )
                                          )
                                        }
                                      >
                                        <div className="text-xs font-mono text-slate-200 truncate">
                                          {d.path}
                                        </div>
                                        <div className="text-xs text-slate-500 truncate">
                                          {d.valuePreview}
                                        </div>
                                      </button>
                                    ))}
                                  </div>
                                </>
                              );
                            })()}
                          </AccordionContent>
                        </AccordionItem>
                      </Accordion>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            {isAdvanced && (
              <TabsContent value="raw" className="mt-6">
                <Card className="bg-[#121217] border-white/5">
                  <CardHeader>
                    <CardTitle className="text-sm font-mono text-slate-200">
                      {canExport ? 'RAW JSON' : 'RAW JSON (PREVIEW)'}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {!canExport && (
                      <div className="text-sm text-slate-200 mb-4">
                        Raw JSON export is locked on free scans, but you can
                        preview and search a subset of extracted fields here.
                      </div>
                    )}
                    <div className="mb-3 flex items-center gap-2">
                      <Search className="w-4 h-4 text-slate-500" />
                      <Input
                        value={rawSearch}
                        onChange={e => setRawSearch(e.target.value)}
                        placeholder="Search keys/values..."
                        className="bg-black/30 border-white/10 text-slate-200 placeholder:text-slate-600"
                      />
                    </div>
                    <div className="mb-4 grid grid-cols-1 md:grid-cols-2 gap-2">
                      {(canExport ? rawMatches : rawMatches.slice(0, 20)).map(
                        m => (
                          <button
                            key={m.path}
                            type="button"
                            className="text-left bg-white/5 border border-white/5 rounded px-3 py-2 hover:bg-white/10 transition-colors min-h-[44px] flex flex-col justify-center"
                            onClick={() =>
                              navigator.clipboard?.writeText(
                                JSON.stringify({ [m.path]: m.value }, null, 2)
                              )
                            }
                          >
                            <div className="text-xs font-mono text-slate-200 truncate">
                              {m.path}
                            </div>
                            <div className="text-xs text-slate-500 truncate">
                              {m.valuePreview}
                            </div>
                          </button>
                        )
                      )}
                    </div>
                    {canExport ? (
                      <pre className="text-xs text-slate-200 bg-black/30 border border-white/5 rounded p-3 overflow-auto max-h-[520px]">
                        {JSON.stringify(metadata, null, 2)}
                      </pre>
                    ) : (
                      <div className="text-xs text-slate-500">
                        Showing up to 20 matches. Use credits to download the
                        full report and view complete raw JSON.
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            )}
          </Tabs>
          {(metadata.quality_metrics || metadata.processing_insights) && (
            <div className="mt-8 flex items-center gap-2 text-xs text-slate-500">
              <span>Extraction details</span>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    className="inline-flex items-center justify-center w-5 h-5 rounded-full border border-white/10 text-slate-200 hover:text-white hover:bg-white/5"
                    aria-label="Extraction details"
                  >
                    i
                  </button>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs text-xs leading-relaxed">
                  <div className="space-y-1">
                    {metadata.quality_metrics?.confidence_score ? (
                      <div>
                        Confidence:{' '}
                        {(
                          metadata.quality_metrics.confidence_score * 100
                        ).toFixed(0)}
                        %
                      </div>
                    ) : null}
                    {metadata.quality_metrics?.extraction_completeness ? (
                      <div>
                        Coverage:{' '}
                        {(
                          metadata.quality_metrics.extraction_completeness * 100
                        ).toFixed(0)}
                        %
                      </div>
                    ) : null}
                    {metadata.processing_insights?.total_fields_extracted ? (
                      <div>
                        Fields extracted:{' '}
                        {metadata.processing_insights.total_fields_extracted.toLocaleString()}
                      </div>
                    ) : null}
                    {metadata.processing_insights?.processing_time_ms ? (
                      <div>
                        Processing time:{' '}
                        {(
                          metadata.processing_insights.processing_time_ms / 1000
                        ).toFixed(1)}
                        s
                      </div>
                    ) : null}
                    {metadata.quality_metrics?.format_support_level ? (
                      <div>
                        Format support:{' '}
                        {metadata.quality_metrics.format_support_level.replace(
                          /_/g,
                          ' '
                        )}
                      </div>
                    ) : null}
                    {!metadata.quality_metrics?.confidence_score &&
                    !metadata.quality_metrics?.extraction_completeness &&
                    !metadata.processing_insights?.total_fields_extracted &&
                    !metadata.processing_insights?.processing_time_ms &&
                    !metadata.quality_metrics?.format_support_level ? (
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
  );
}
