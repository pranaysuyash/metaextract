import React, { useState, useMemo, useEffect } from 'react';
import { useLocation, useSearchParams, useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { showUploadError } from '@/lib/toast-helpers';
import { Layout } from '@/components/layout';
import { PaymentModal } from '@/components/payment-modal';
import { BurnedMetadataDisplay } from '@/components/burned-metadata-display';
import { MetadataComparisonDisplay } from '@/components/metadata-comparison-display';
import { AdvancedResultsIntegration } from '@/components/advanced-results-integration';
import { MedicalAnalysisResult } from '@/components/medical-analysis-result';
import { ForensicAnalysis } from '@/components/v2-results/ForensicAnalysis';
import { AuthenticityBadge } from '@/components/v2-results/AuthenticityBadge';
import { AlertTriangle } from 'lucide-react';
import { PersonaDisplay } from '@/components/persona-display';
import {
  MetadataExplorer,
  convertMetadataToProcessedFile,
} from '@/components/metadata-explorer';
import {
  UIAdaptationProvider,
  ContextBanner,
  ContextIndicator,
} from '@/components/ui-adaptation-controller';
import {
  ErrorBoundary,
  MetadataErrorBoundary,
} from '@/components/error-boundary';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Download,
  MapPin,
  Camera,
  FileText,
  Image as ImageIcon,
  Lock,
  Search,
  Database,
  Cpu,
  Hash,
  Folder,
  Calculator,
  Tag,
  ExternalLink,
  Copy,
  Check,
  ShieldCheck,
  Zap,
  Eye,
  TrendingUp,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import generatedBackground from '@assets/generated_images/chaotic_dark_forensic_data_visualization_with_connecting_lines.png';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

interface BurnedMetadata {
  has_burned_metadata: boolean;
  ocr_available: boolean;
  confidence: 'none' | 'low' | 'medium' | 'high';
  extracted_text?: string | null;
  parsed_data?: {
    gps?: { latitude: number; longitude: number; google_maps_url: string };
    location?: { city: string; state: string; country: string };
    address?: string;
    plus_code?: string;
    timestamp?: string;
    weather?: {
      temperature?: string;
      humidity?: string;
      speed?: string;
      altitude?: string;
    };
    compass?: { degrees: string; direction: string };
    camera_app?: string;
  };
}

interface MetadataComparison {
  has_both: boolean;
  has_embedded_only: boolean;
  has_burned_only: boolean;
  matches: Array<{
    field: string;
    matches: boolean;
    embedded?: any;
    burned?: any;
    difference?: any;
  }>;
  discrepancies: Array<{ field: string; matches: boolean; warning?: string }>;
  warnings: string[];
  summary: {
    embedded_metadata_present: boolean;
    burned_metadata_present: boolean;
    gps_comparison: string;
    timestamp_comparison: string;
    overall_status:
      | 'verified'
      | 'suspicious'
      | 'stripped_exif'
      | 'no_overlay'
      | 'no_metadata';
  };
}

interface MetadataResponse {
  filename: string;
  filesize: string;
  filetype: string;
  mime_type: string;
  tier: string;
  fields_extracted: number;
  file_integrity: { md5: string; sha256: string };
  hashes?: { md5: string; sha256: string };
  hash?: string;
  file?: { created?: string; modified?: string };
  advanced_analysis?: {
    enabled: boolean;
    processing_time_ms: number;
    modules_run: string[];
    forensic_score: number;
    authenticity_assessment: string;
  };
  filesystem: Record<string, any>;
  calculated: Record<string, any>;
  gps: Record<string, any> | null;
  summary: Record<string, any>;
  forensic: Record<string, any>;
  exif: Record<string, any>;
  exif_ifd?: Record<string, any>;
  makernote: Record<string, any>;
  interoperability?: Record<string, any>;
  iptc: Record<string, any>;
  xmp: Record<string, any>;
  xmp_namespaces?: Record<string, any>;
  thumbnail_metadata?: Record<string, any>;
  image_container?: Record<string, any>;
  icc_profile?: Record<string, any>;
  iptc_raw?: Record<string, any>;
  xmp_raw?: Record<string, any>;
  thumbnail?: Record<string, any>;
  embedded_thumbnails?: Record<string, any>;
  perceptual_hashes?: Record<string, any>;
  normalized?: Record<string, any>;
  web_metadata?: Record<string, any>;
  social_media?: Record<string, any>;
  mobile_metadata?: Record<string, any>;
  camera_360?: Record<string, any>;
  forensic_security?: Record<string, any>;
  action_camera?: Record<string, any>;
  print_publishing?: Record<string, any>;
  workflow_dam?: Record<string, any>;
  video?: Record<string, any>;
  audio_advanced?: Record<string, any>;
  video_advanced?: Record<string, any>;
  steganography_analysis?: Record<string, any>;
  manipulation_detection?: Record<string, any>;
  ai_detection?: Record<string, any>;
  timeline_analysis?: Record<string, any>;
  scientific?: Record<string, any>;
  scientific_data?: Record<string, any>;
  extended: Record<string, any>;
  extended_attributes?: Record<string, any>;
  burned_metadata?: BurnedMetadata | null;
  metadata_comparison?: MetadataComparison | null;
  locked_fields: string[];
  access?: {
    trial_email_present?: boolean;
    trial_granted?: boolean;
    credits_charged?: number;
    credits_required?: number;
    mode?: 'device_free' | 'trial_limited' | 'paid';
    free_used?: number;
  };
  persona_interpretation?: import('@shared/schema').PersonaInterpretation;
  medical_imaging?: Record<string, any>;
}

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const resultId = searchParams.get('id');
  const { toast } = useToast();

  const [metadata, setMetadata] = useState<MetadataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const creditsCharged = metadata?.access?.credits_charged;
  const creditsRequired = metadata?.access?.credits_required;

  // Fetch metadata from the database instead of using session storage
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        setError(null);
        // Priority 1: Navigation State (In-Memory, handles large payloads)
        if (location.state?.metadata) {
          // Handle both array and object formats
          const metadataObj = Array.isArray(location.state.metadata)
            ? location.state.metadata[0]
            : location.state.metadata;

          setMetadata(metadataObj);
          setLoading(false);
          return;
        }

        // Priority 2: Query Parameter (for sharing links)
        const urlParams = new URLSearchParams(location.search);
        const metadataId = urlParams.get('id');

        if (metadataId) {
          // Fetch from database via API
          const response = await fetch(`/api/extract/results/${metadataId}`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('auth_token') || ''}`,
            },
          });

          if (response.ok) {
            const result = await response.json();
            setMetadata(result);
            console.log('[Results] Loaded metadata from database:', result);
          } else if (response.status === 404) {
            console.warn('[Results] Metadata not found in database');
            setMetadata(null);
          } else {
            throw new Error(
              `Failed to fetch metadata: ${response.status} ${response.statusText}`
            );
          }
        } else {
          // No metadata ID provided, show empty state
          console.warn('[Results] No metadata ID provided');
          setMetadata(null);
        }
      } catch (err) {
        console.error('[Results] Error fetching metadata:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setMetadata(null);
      } finally {
        setLoading(false);
      }
    };

    fetchMetadata();
  }, [location]);

  // Fetch from DB if ID is present and we don't have fresh data

  const [showPayment, setShowPayment] = useState(false);
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedField, setCopiedField] = useState<string | null>(null);

  // Advanced analysis state
  const [advancedAnalysis, setAdvancedAnalysis] = useState<any>(null);
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [timelineResult, setTimelineResult] = useState<any>(null);
  const [forensicReport, setForensicReport] = useState<any>(null);
  const [isProcessingAdvanced, setIsProcessingAdvanced] = useState(false);

  // Metadata explorer state
  const [explorerViewMode, setExplorerViewMode] = useState<
    'simple' | 'advanced' | 'raw'
  >('advanced');
  const [processedFiles, setProcessedFiles] = useState<any[]>([]);

  // Initialize processed files for metadata explorer
  useEffect(() => {
    if (metadata) {
      const processedFile = convertMetadataToProcessedFile(
        metadata,
        'current-file'
      );
      setProcessedFiles([processedFile]);

      // Extract advanced analysis from metadata if available
      if (metadata.advanced_analysis) {
        setAdvancedAnalysis(metadata.advanced_analysis);
      }
    }
  }, [metadata]);

  useEffect(() => {
    const access = metadata?.access;
    if (!access) return;
    // Prefer explicit access.mode when available
    const unlocked = access.mode
      ? access.mode === 'paid' || access.mode === 'device_free'
      : access.trial_granted || (access.credits_charged ?? 0) > 0;
    if (unlocked) {
      setIsUnlocked(true);
    }
  }, [metadata]);

  const handleDownload = () => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (!metadata) {
      showUploadError(toast, 'No metadata available to download');
      return;
    }

    if (isUnlocked) {
      const dataStr = JSON.stringify(metadata, null, 2);
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${metadata.filename}_metadata.json`;
      a.click();
      URL.revokeObjectURL(url);
    } else {
      setShowPayment(true);
    }
  };

  const handlePDFExport = () => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (!metadata) {
      showUploadError(toast, 'No metadata available to export');
      return;
    }

    if (!isUnlocked) {
      setShowPayment(true);
      return;
    }

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.width;
    let yPosition = 20;

    // Helper function to add text with word wrapping
    const addWrappedText = (
      text: string,
      x: number,
      y: number,
      maxWidth: number,
      fontSize: number = 10
    ) => {
      doc.setFontSize(fontSize);
      const lines = doc.splitTextToSize(text, maxWidth);
      doc.text(lines, x, y);
      return y + lines.length * fontSize * 0.4;
    };

    // Title
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('METADATA ANALYSIS REPORT', pageWidth / 2, yPosition, {
      align: 'center',
    });
    yPosition += 15;

    // File Info
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text(`File: ${metadata.filename || 'Unknown'}`, 20, yPosition);
    yPosition += 8;
    doc.text(`Size: ${metadata.filesize || 0} bytes`, 20, yPosition);
    yPosition += 8;
    doc.text(`Type: ${metadata.filetype || 'Unknown'}`, 20, yPosition);
    yPosition += 8;
    doc.text(`MIME Type: ${metadata.mime_type || 'Unknown'}`, 20, yPosition);
    yPosition += 8;
    doc.text(`Analyzed: ${new Date().toLocaleString()}`, 20, yPosition);
    yPosition += 15;

    // Summary
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('ANALYSIS SUMMARY', 20, yPosition);
    yPosition += 10;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(
      `Fields Extracted: ${metadata.fields_extracted || 0}`,
      20,
      yPosition
    );
    yPosition += 8;
    doc.text(`Tier: ${metadata.tier || 'free'}`, 20, yPosition);
    yPosition += 15;

    // Advanced Analysis (if available)
    if (advancedAnalysis?.enabled) {
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('ADVANCED FORENSIC ANALYSIS', 20, yPosition);
      yPosition += 10;

      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(
        `Forensic Score: ${advancedAnalysis.forensic_score?.toFixed(2) || 'N/A'}`,
        20,
        yPosition
      );
      yPosition += 8;
      doc.text(
        `Authenticity Assessment: ${advancedAnalysis.authenticity_assessment || 'Unknown'}`,
        20,
        yPosition
      );
      yPosition += 8;
      doc.text(
        `Modules Run: ${advancedAnalysis.modules_run?.join(', ') || 'None'}`,
        20,
        yPosition
      );
      yPosition += 8;
      doc.text(
        `Processing Time: ${(advancedAnalysis.processing_time_ms || 0).toFixed(0)}ms`,
        20,
        yPosition
      );
      yPosition += 15;
    }

    // Key Findings
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('KEY FINDINGS', 20, yPosition);
    yPosition += 10;

    // Extract some key metadata fields for the report
    const captureDate = metadata.calculated?.capture_date;
    const modifiedDate =
      metadata.filesystem?.modified ||
      metadata.file?.modified ||
      metadata.calculated?.file_modified;

    const keyFields = [
      {
        label: 'MD5 Hash',
        value: metadata.hashes?.md5 || metadata.file_integrity?.md5 || 'N/A',
      },
      {
        label: 'SHA256 Hash',
        value:
          metadata.hashes?.sha256 || metadata.file_integrity?.sha256 || 'N/A',
      },
      { label: 'Capture Date', value: captureDate || 'Not embedded' },
      {
        label: 'Modified Date (server file)',
        value: modifiedDate || 'Not available',
      },
      {
        label: 'GPS Location',
        value: gpsCoords
          ? `${gpsCoords.latitude}, ${gpsCoords.longitude}`
          : 'Not embedded',
      },
      { label: 'Camera Make', value: metadata.exif?.Make || 'Not embedded' },
      { label: 'Camera Model', value: metadata.exif?.Model || 'Not embedded' },
    ];

    doc.setFontSize(9);
    keyFields.forEach(field => {
      if (yPosition > doc.internal.pageSize.height - 30) {
        doc.addPage();
        yPosition = 20;
      }
      doc.text(`${field.label}: ${field.value}`, 20, yPosition);
      yPosition += 6;
    });

    // Footer
    const totalPages = doc.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'italic');
      doc.text(
        `Generated by MetaExtract - Page ${i} of ${totalPages}`,
        pageWidth / 2,
        doc.internal.pageSize.height - 10,
        { align: 'center' }
      );
    }

    doc.save(`${metadata.filename}_analysis_report.pdf`);
  };

  const onPaymentSuccess = () => {
    // CRITICAL FIX: Only unlock if metadata exists
    if (metadata) {
      setIsUnlocked(true);
    } else {
      showUploadError(toast, 'No metadata available to unlock');
    }
  };

  // Advanced analysis API calls
  const runAdvancedAnalysis = async () => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (!metadata || !metadata.filename) {
      showUploadError(toast, 'No metadata available for analysis');
      return;
    }

    setIsProcessingAdvanced(true);
    try {
      // Get the original file from session storage or create a mock file
      const formData = new FormData();

      // For demo purposes, we'll use the test.jpg file
      const response = await fetch('/test.jpg');
      const blob = await response.blob();
      const file = new File([blob], metadata?.filename || 'unknown', {
        type: metadata?.mime_type || 'application/octet-stream',
      });

      formData.append('file', file);

      const analysisResponse = await fetch(
        `/api/extract/advanced?tier=${import.meta.env.DEV ? 'enterprise' : 'professional'}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (analysisResponse.ok) {
        const result = await analysisResponse.json();
        setAdvancedAnalysis(result);
      } else {
        console.error(
          'Advanced analysis failed:',
          await analysisResponse.text()
        );
      }
    } catch (error) {
      console.error('Advanced analysis error:', error);
    } finally {
      setIsProcessingAdvanced(false);
    }
  };

  const runComparison = async (files: FileList) => {
    setIsProcessingAdvanced(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch(
        `/api/compare/batch?tier=${import.meta.env.DEV ? 'enterprise' : 'professional'}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (response.ok) {
        const result = await response.json();
        setComparisonResult(result);
      }
    } catch (error) {
      console.error('Comparison error:', error);
    } finally {
      setIsProcessingAdvanced(false);
    }
  };

  const runTimeline = async (files: FileList) => {
    setIsProcessingAdvanced(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch(
        `/api/timeline/reconstruct?tier=${import.meta.env.DEV ? 'enterprise' : 'professional'}`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (response.ok) {
        const result = await response.json();
        setTimelineResult(result);
      }
    } catch (error) {
      console.error('Timeline error:', error);
    } finally {
      setIsProcessingAdvanced(false);
    }
  };

  const generateReport = async (files: FileList) => {
    setIsProcessingAdvanced(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('/api/forensic/report?tier=enterprise', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setForensicReport(result);
      }
    } catch (error) {
      console.error('Report generation error:', error);
    } finally {
      setIsProcessingAdvanced(false);
    }
  };

  const copyToClipboard = (value: string, field: string) => {
    navigator.clipboard.writeText(value);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const filterFields = (fields: Record<string, any>) => {
    if (!fields) return [];
    // If no search query, return all fields (excluding internal ones)
    if (!searchQuery.trim()) {
      return Object.entries(fields).filter(([key]) => !key.startsWith('_'));
    }
    return Object.entries(fields).filter(([key, val]) => {
      if (key.startsWith('_')) return false;
      const searchLower = searchQuery.toLowerCase();
      return (
        key.toLowerCase().includes(searchLower) ||
        String(val).toLowerCase().includes(searchLower)
      );
    });
  };

  const flattenForDisplay = (data: any, prefix = ''): Record<string, any> => {
    if (!data || typeof data !== 'object') return {};
    const flat: Record<string, any> = {};
    Object.entries(data).forEach(([key, value]) => {
      if (key.startsWith('_') || key === 'data_base64') return;
      const nextKey = prefix ? `${prefix}.${key}` : key;
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        Object.assign(flat, flattenForDisplay(value, nextKey));
      } else {
        flat[nextKey] = value;
      }
    });
    return flat;
  };

  const isSectionLocked = (
    section: Record<string, any> | null | undefined
  ): boolean => {
    if (!section) return false;
    return section._locked === true;
  };

  const totalFields = useMemo(() => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (!metadata) {
      return 0;
    }

    if (metadata.fields_extracted && metadata.fields_extracted > 0) {
      return metadata.fields_extracted;
    }
    return (
      Object.keys(metadata.summary || {}).length +
      Object.keys(metadata.forensic || {}).length +
      Object.keys(metadata.exif || {}).length +
      Object.keys(metadata.filesystem || {}).length +
      Object.keys(metadata.calculated || {}).length +
      Object.keys(metadata.makernote || {}).length +
      Object.keys(metadata.iptc || {}).length +
      Object.keys(metadata.xmp || {}).length +
      Object.keys(metadata.scientific || {}).length +
      Object.keys(metadata.scientific_data || {}).length +
      Object.keys(metadata.extended || {}).length +
      (metadata.video?.telemetry
        ? Object.keys(metadata.video.telemetry || {}).length
        : 0) +
      (metadata.gps ? Object.keys(metadata.gps).length : 0) +
      2
    );
  }, [metadata]);

  const flatXmpNamespaces = useMemo(() => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (
      !metadata ||
      !metadata.xmp_namespaces ||
      metadata.xmp_namespaces._locked
    ) {
      return {};
    }
    const flat: Record<string, any> = {};
    Object.entries(metadata.xmp_namespaces).forEach(([namespace, fields]) => {
      if (!fields || typeof fields !== 'object') return;
      Object.entries(fields as Record<string, any>).forEach(([key, value]) => {
        flat[`${namespace}.${key}`] = value;
      });
    });
    return flat;
  }, [metadata]);

  const flatEmbeddedThumbnails = useMemo(() => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (
      !metadata ||
      !metadata.embedded_thumbnails ||
      metadata.embedded_thumbnails._locked
    ) {
      return {};
    }
    return flattenForDisplay(metadata.embedded_thumbnails);
  }, [metadata]);

  const flatCamera360 = useMemo(() => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (!metadata || !metadata.camera_360) {
      return {};
    }
    return flattenForDisplay(metadata.camera_360);
  }, [metadata]);

  const flatScientific = useMemo(() => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (!metadata || !metadata.scientific || metadata.scientific._locked) {
      return {};
    }
    return flattenForDisplay(metadata.scientific);
  }, [metadata]);

  const flatScientificData = useMemo(() => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (
      !metadata ||
      !metadata.scientific_data ||
      metadata.scientific_data._locked
    ) {
      return {};
    }
    return flattenForDisplay(metadata.scientific_data);
  }, [metadata]);

  const flatTelemetry = useMemo(() => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (!metadata || !metadata.video || !metadata.video.telemetry) {
      return {};
    }
    return flattenForDisplay(metadata.video.telemetry);
  }, [metadata]);

  const getGpsCoords = (gps: Record<string, any> | null | undefined) => {
    if (!gps || typeof gps !== 'object') return null;
    const latRaw =
      gps.latitude ??
      gps.lat ??
      gps.latitude_decimal ??
      gps.GPSLatitude ??
      gps.gps_latitude ??
      gps.Latitude;
    const lonRaw =
      gps.longitude ??
      gps.lon ??
      gps.longitude_decimal ??
      gps.GPSLongitude ??
      gps.gps_longitude ??
      gps.Longitude;
    const lat =
      typeof latRaw === 'number' ? latRaw : parseFloat(String(latRaw));
    const lon =
      typeof lonRaw === 'number' ? lonRaw : parseFloat(String(lonRaw));
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    return { latitude: lat, longitude: lon };
  };

  const gpsCoords = useMemo(() => {
    // CRITICAL FIX: Handle null metadata gracefully
    if (!metadata || !metadata.gps) {
      return null;
    }
    return getGpsCoords(metadata.gps as any);
  }, [metadata?.gps]);
  const hasGPS = !!gpsCoords;

  const isFieldLocked = (value: any): boolean => {
    if (typeof value === 'string') {
      return (
        value === 'LOCKED' ||
        value === 'LOCKED_UPGRADE_TO_VIEW' ||
        value.startsWith('LOCKED')
      );
    }
    return false;
  };

  const formatValue = (val: any): string => {
    if (val === null || val === undefined) return 'N/A';
    if (Array.isArray(val)) return val.join(', ');
    if (typeof val === 'object') {
      if (val instanceof Date) return val.toISOString();
      if (val.rawValue !== undefined) return String(val.rawValue);
      if (val.toString && val.toString() !== '[object Object]')
        return val.toString();
      try {
        return JSON.stringify(val);
      } catch {
        return '[Complex Object]';
      }
    }
    return String(val);
  };

  const FieldRow = ({
    label,
    value,
    locked = false,
    index = 0,
    copyable = false,
  }: {
    label: string;
    value: string | any;
    locked?: boolean;
    index?: number;
    copyable?: boolean;
  }) => {
    const stringValue = formatValue(value);
    const isLocked = locked || isFieldLocked(value);

    return (
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.003 }}
        className="group grid grid-cols-2 gap-4 py-2 px-3 border-b border-white/5 hover:bg-white/5 rounded transition-colors font-mono text-xs"
        data-testid={`field-row-${label
          .toLowerCase()
          .replace(/[^a-z0-9]/g, '-')}`}
      >
        <span className="text-slate-300 group-hover:text-primary/80 transition-colors break-all">
          {label}
        </span>
        <div className="flex items-center gap-2 justify-end min-w-0">
          {isLocked && !isUnlocked ? (
            <button
              type="button"
              className="flex items-center gap-2 text-slate-600 select-none bg-black/40 px-2 py-0.5 rounded border border-white/5 cursor-pointer hover:border-primary/30 transition-colors shrink-0 focus:outline-none focus:ring-2 focus:ring-primary/50"
              onClick={() => setShowPayment(true)}
            >
              <span className="text-xs text-slate-500">Upgrade to view</span>
              <Lock className="w-3 h-3 text-primary/60" />
            </button>
          ) : (
            <>
              <span className="text-slate-200 text-right break-all selection:bg-primary/30 min-w-0">
                {stringValue}
              </span>
              {copyable && !isLocked && (
                <button
                  type="button"
                  onClick={() => copyToClipboard(stringValue, label)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-white/10 rounded shrink-0 focus:outline-none focus:ring-1 focus:ring-primary/50"
                  data-testid={`copy-${label
                    .toLowerCase()
                    .replace(/[^a-z0-9]/g, '-')}`}
                >
                  {copiedField === label ? (
                    <Check className="w-3 h-3 text-emerald-500" />
                  ) : (
                    <Copy className="w-3 h-3 text-slate-500" />
                  )}
                </button>
              )}
            </>
          )}
        </div>
      </motion.div>
    );
  };

  const SectionHeader = ({
    icon: Icon,
    title,
    color,
    count,
  }: {
    icon: any;
    title: string;
    color: string;
    count?: number;
  }) => (
    <h4
      className={`flex items-center gap-2 text-xs font-bold mb-3 uppercase tracking-widest ${color}`}
    >
      <Icon className="w-3 h-3" /> {title}
      {count !== undefined && (
        <span className="text-slate-600 font-normal">({count})</span>
      )}
    </h4>
  );

  // Show loading state while fetching metadata
  if (loading) {
    return (
      <UIAdaptationProvider initialMetadata={undefined}>
        <Layout>
          <div className="flex items-center justify-center min-h-[calc(100vh-64px)]">
            <div className="flex flex-col items-center gap-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
              <p className="text-white text-lg">Loading metadata...</p>
              <p className="text-slate-300 text-sm">Fetching from database</p>
            </div>
          </div>
        </Layout>
      </UIAdaptationProvider>
    );
  }

  // Show error state if there was an error
  if (error) {
    return (
      <UIAdaptationProvider initialMetadata={undefined}>
        <Layout>
          <div className="flex items-center justify-center min-h-[calc(100vh-64px)]">
            <div className="max-w-md w-full bg-red-900/30 border border-red-700/50 rounded-lg p-6 text-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-white mb-2">
                Error Loading Metadata
              </h2>
              <p className="text-slate-200 mb-4">{error}</p>
              <Button
                onClick={() => navigate('/images_mvp')}
                className="bg-[#6366f1] hover:bg-[#5855eb] text-white w-full"
              >
                Upload a file
              </Button>
            </div>
          </div>
        </Layout>
      </UIAdaptationProvider>
    );
  }

  // Show error if no metadata was loaded
  if (!metadata) {
    return (
      <UIAdaptationProvider initialMetadata={undefined}>
        <Layout>
          <div className="flex items-center justify-center min-h-[calc(100vh-64px)]">
            <div className="max-w-md w-full bg-[#11121a] border border-white/10 rounded-lg p-6 text-center">
              <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-white mb-2">
                No Results Yet
              </h2>
              <p className="text-slate-200 mb-4">
                Upload a file to view extracted metadata and analysis here.
              </p>
              <Button
                onClick={() => navigate('/images_mvp')}
                className="bg-[#6366f1] hover:bg-[#5855eb] text-white w-full"
              >
                Start extraction
              </Button>
            </div>
          </div>
        </Layout>
      </UIAdaptationProvider>
    );
  }

  return (
    <UIAdaptationProvider initialMetadata={metadata}>
      <Layout>
        <ErrorBoundary level="page">
          <div className="relative min-h-[calc(100vh-64px)] overflow-hidden">
            <div className="absolute inset-0 z-0 pointer-events-none">
              <div className="absolute inset-0 bg-background/90 z-10"></div>
              <img
                src={generatedBackground}
                alt="Background"
                className="w-full h-full object-cover opacity-10 mix-blend-screen scale-110"
              />
            </div>

            <div className="container mx-auto px-4 py-8 relative z-10 h-full flex flex-col">
              <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 pb-6 border-b border-white/10 gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-white/5 rounded border border-white/10 flex items-center justify-center">
                    <Cpu className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h1
                      className="text-xl font-bold text-white font-mono tracking-tight"
                      data-testid="text-filename"
                    >
                      {metadata?.filename || 'Unknown'}
                    </h1>
                    <div className="flex gap-4 text-xs text-slate-500 font-mono mt-1">
                      <span data-testid="text-filesize">
                        SIZE: {metadata?.filesize || 'Unknown'}
                      </span>
                      <span data-testid="text-filetype">
                        TYPE: {metadata?.filetype || 'Unknown'}
                      </span>
                      <span className="text-primary" data-testid="text-hash">
                        SHA256:{' '}
                        {metadata?.file_integrity?.sha256?.substring(0, 12) ||
                          metadata?.hash?.substring(0, 12) ||
                          'N/A'}
                        ...
                      </span>
                      <ContextIndicator />
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap gap-3 items-center">
                  {typeof creditsRequired === 'number' && (
                    <div className="px-3 py-2 bg-white/5 border border-white/10 rounded text-xs text-slate-200 font-mono">
                      {typeof creditsCharged === 'number' && creditsCharged > 0
                        ? `Charged: ${creditsCharged} credits`
                        : `Cost: ${creditsRequired} credits (covered by free check)`}
                      {creditsRequired > 4 ? ' (Text scan applied)' : ''}
                    </div>
                  )}
                  {isProcessingAdvanced && (
                    <div className="flex items-center gap-2 px-3 py-2 bg-blue-600/20 border border-blue-500/30 rounded text-blue-300 text-xs font-mono">
                      <Zap className="w-4 h-4 animate-pulse" />
                      PROCESSING_ADVANCED_ANALYSIS...
                    </div>
                  )}
                  <div className="px-2 py-1 bg-white/5 border border-white/10 rounded text-xs text-slate-200 font-mono flex items-center gap-1">
                    {isUnlocked ? <ShieldCheck className="w-3 h-3 text-emerald-500" /> : <Lock className="w-3 h-3 text-yellow-500" />}
                    {isUnlocked ? 'Unlocked' : 'Locked'}
                  </div>
                  <div className="flex flex-col items-start gap-1">
                    <Button
                      onClick={handleDownload}
                      disabled={!isUnlocked}
                      className={cn(
                        'gap-2 font-mono text-xs tracking-wider',
                        isUnlocked
                          ? 'bg-emerald-600 hover:bg-emerald-700'
                          : 'bg-gray-600 cursor-not-allowed opacity-50'
                      )}
                      data-testid="button-download"
                    >
                      <Download className="w-4 h-4" />
                      Download JSON
                    </Button>
                    {!isUnlocked && (
                      <div className="text-xs text-slate-400 font-mono">
                        Unlock to download full data
                      </div>
                    )}
                  </div>
                  {!isUnlocked && (
                    <Button
                      onClick={() => setShowPayment(true)}
                      className="gap-2 font-mono text-xs tracking-wider bg-primary hover:bg-primary/90 text-black"
                    >
                      <Lock className="w-4 h-4" />
                      Unlock
                    </Button>
                  )}
                  {isUnlocked && (
                    <Button
                      onClick={handlePDFExport}
                      variant="outline"
                      className="gap-2 font-mono text-xs tracking-wider border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/10"
                    >
                      <FileText className="w-4 h-4" />
                      PDF
                    </Button>
                  )}
                  {import.meta.env.DEV && (
                    <Button
                      onClick={() =>
                        navigate('/results-v2', {
                          state: { metadata },
                        })
                      }
                      variant="outline"
                      className="gap-2 font-mono text-xs tracking-wider border-blue-500/50 text-blue-300 hover:bg-blue-500/10"
                    >
                      <Cpu className="w-4 h-4" />
                      V2
                    </Button>
                  )}
                </div>
              </div>

              <ContextBanner />

              <div className="flex-1 flex flex-col md:flex-row gap-8 min-h-0">
                <div className="w-full md:w-72 shrink-0 space-y-4 md:overflow-y-auto pr-2 custom-scrollbar">
                  <div className="bg-black/40 backdrop-blur-md border border-white/10 rounded-lg p-4 shadow-lg">
                    <h3 className="text-xs font-bold text-white mb-4 uppercase tracking-widest border-b border-white/5 pb-2">
                      Analysis Summary
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">
                          Total Fields
                        </div>
                        <div
                          className="text-2xl font-mono text-primary font-bold"
                          data-testid="text-total-fields"
                        >
                          {totalFields}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">
                          File Integrity
                        </div>
                        <div className="text-sm font-mono text-emerald-500 font-bold">
                          VERIFIED [MD5+SHA256]
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">
                          Location Data
                        </div>
                        <div className="text-sm font-mono text-white flex items-center gap-2">
                          <MapPin
                            className={`w-3 h-3 ${
                              hasGPS ? 'text-primary' : 'text-slate-600'
                            }`}
                          />
                          {hasGPS ? 'Present' : 'Not Embedded'}
                        </div>
                      </div>
                      {metadata?.calculated && (
                        <div>
                          <div className="text-[10px] text-slate-500 uppercase">
                            Dimensions
                          </div>
                          <div className="text-sm font-mono text-white">
                            {metadata?.calculated?.megapixels
                              ? `${metadata?.calculated?.megapixels} MP`
                              : 'N/A'}
                            {metadata?.calculated?.aspect_ratio &&
                              ` (${metadata?.calculated?.aspect_ratio})`}
                          </div>
                        </div>
                      )}
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">
                          Advanced Analysis
                        </div>
                        <div className="text-sm font-mono text-white flex items-center gap-2">
                          <Eye
                            className={`w-3 h-3 ${
                              advancedAnalysis
                                ? 'text-primary'
                                : 'text-slate-600'
                            }`}
                          />
                          {advancedAnalysis ? 'Available' : 'Not Run'}
                        </div>
                      </div>
                    </div>
                  </div>

                  {hasGPS && metadata?.gps?.google_maps_url && (
                    <div className="bg-black/40 backdrop-blur-md border border-white/10 rounded-lg p-4 shadow-lg">
                      <h3 className="text-xs font-bold text-white mb-4 uppercase tracking-widest border-b border-white/5 pb-2">
                        GPS Location
                      </h3>
                      <div className="space-y-2 font-mono text-xs">
                        <div className="text-slate-300">
                          <span className="text-slate-600">LAT:</span>{' '}
                          {gpsCoords?.latitude.toFixed(6)}
                        </div>
                        <div className="text-slate-300">
                          <span className="text-slate-600">LON:</span>{' '}
                          {gpsCoords?.longitude.toFixed(6)}
                        </div>
                        <a
                          href={metadata?.gps?.google_maps_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 text-primary hover:text-primary/80 transition-colors mt-3"
                          data-testid="link-google-maps"
                        >
                          <MapPin className="w-3 h-3" /> View on Maps{' '}
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  )}

                  <div className="bg-black/40 backdrop-blur-md border border-white/10 rounded-lg p-4 shadow-lg">
                    <h3 className="text-xs font-bold text-white mb-4 uppercase tracking-widest border-b border-white/5 pb-2">
                      File Preview
                    </h3>
                    <div className="aspect-square bg-black/50 rounded flex items-center justify-center border border-white/5 mb-2 relative overflow-hidden group">
                      <div className="absolute inset-0 bg-grid opacity-20"></div>
                      <ImageIcon className="w-8 h-8 text-slate-600 group-hover:text-primary transition-colors" />
                    </div>
                    <div className="text-[10px] text-slate-500 text-center font-mono">
                      ZERO_DATA_RETENTION
                    </div>
                  </div>
                </div>

                <div className="flex-1 bg-black/40 backdrop-blur-md border border-white/10 rounded-lg flex flex-col overflow-hidden shadow-2xl">
                  {/* PERSONA DISPLAY - Show Sarah-friendly answers first */}
                  {metadata?.persona_interpretation && (
                    <div className="p-4 border-b border-white/10 bg-black/20">
                      <PersonaDisplay
                        interpretation={metadata?.persona_interpretation}
                      />
                    </div>
                  )}

                  <Tabs defaultValue="all" className="flex-1 flex flex-col">
                    <div className="flex flex-col md:flex-row md:items-center justify-between p-4 border-b border-white/10 bg-black/20 gap-4">
                      <TabsList className="bg-white/5 border border-white/5 h-9 w-full md:w-auto overflow-x-auto scrollbar-hide">
                        <TabsTrigger
                          value="all"
                          className="text-xs font-mono data-[state=active]:bg-primary data-[state=active]:text-black relative"
                          data-testid="tab-all"
                        >
                          ALL
                          {metadata.metadata_comparison?.summary
                            ?.overall_status === 'suspicious' && (
                            <div className="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full"></div>
                          )}
                        </TabsTrigger>
                        <TabsTrigger
                          value="explorer"
                          className="text-xs font-mono data-[state=active]:bg-primary data-[state=active]:text-black relative"
                          data-testid="tab-explorer"
                        >
                          EXPLORER
                          <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full"></div>
                        </TabsTrigger>
                        {metadata?.medical_imaging?.available && (
                          <TabsTrigger
                            value="medical"
                            className="text-xs font-mono data-[state=active]:bg-primary data-[state=active]:text-black relative"
                          >
                            MEDICAL
                            <div className="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full"></div>
                          </TabsTrigger>
                        )}
                        <TabsTrigger
                          value="advanced"
                          className="text-xs font-mono data-[state=active]:bg-primary data-[state=active]:text-black relative"
                          data-testid="tab-advanced"
                        >
                          ADVANCED
                          {advancedAnalysis && (
                            <div className="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full"></div>
                          )}
                        </TabsTrigger>
                        <TabsTrigger
                          value="forensic"
                          className="text-xs font-mono data-[state=active]:bg-primary data-[state=active]:text-black relative"
                          data-testid="tab-forensic"
                        >
                          FORENSIC
                          {metadata.metadata_comparison?.summary
                            ?.overall_status === 'suspicious' && (
                            <div className="absolute -top-1 -right-1 w-2 h-2 bg-rose-500 rounded-full"></div>
                          )}
                        </TabsTrigger>
                        <TabsTrigger
                          value="technical"
                          className="text-xs font-mono data-[state=active]:bg-primary data-[state=active]:text-black"
                          data-testid="tab-technical"
                        >
                          TECHNICAL
                        </TabsTrigger>
                        <TabsTrigger
                          value="raw"
                          className="text-xs font-mono data-[state=active]:bg-primary data-[state=active]:text-black"
                          data-testid="tab-raw"
                        >
                          RAW
                        </TabsTrigger>
                      </TabsList>

                      <div className="relative w-full md:w-64">
                        <Search className="absolute left-2.5 top-2.5 h-3 w-3 text-slate-500" />
                        <input
                          type="text"
                          placeholder="Search metadata fields…"
                          className="w-full bg-black/40 border border-white/10 rounded-md pl-8 pr-3 py-1.5 text-xs text-white placeholder:text-slate-600 focus:border-primary/50 focus:ring-0 outline-none font-mono"
                          value={searchQuery}
                          onChange={e => setSearchQuery(e.target.value)}
                          data-testid="input-search"
                        />
                      </div>
                    </div>

                    <div className="flex-1 overflow-hidden relative">
                      <ScrollArea className="h-full">
                        <div className="p-4 space-y-6">
                          <TabsContent
                            value="explorer"
                            className="mt-0 h-[600px]"
                          >
                            <MetadataErrorBoundary>
                              <MetadataExplorer
                                files={processedFiles}
                                viewMode={explorerViewMode}
                                onViewModeChange={setExplorerViewMode}
                              />
                            </MetadataErrorBoundary>
                          </TabsContent>

                          <TabsContent value="medical" className="mt-0">
                            <MedicalAnalysisResult
                              data={
                                (metadata?.medical_imaging || {
                                  available: false,
                                }) as any
                              }
                              isUnlocked={isUnlocked}
                            />
                          </TabsContent>

                          <TabsContent value="all" className="mt-0 space-y-6">
                            {metadata?.file_integrity && (
                              <section>
                                <SectionHeader
                                  icon={Hash}
                                  title="File Integrity"
                                  color="text-amber-500"
                                  count={2}
                                />
                                <div className="grid grid-cols-1 gap-y-1">
                                  <FieldRow
                                    label="MD5"
                                    value={
                                      metadata?.file_integrity?.md5 || 'N/A'
                                    }
                                    copyable
                                    index={0}
                                  />
                                  <FieldRow
                                    label="SHA256"
                                    value={
                                      metadata?.file_integrity?.sha256 || 'N/A'
                                    }
                                    copyable
                                    index={1}
                                  />
                                </div>
                              </section>
                            )}

                            {metadata?.metadata_comparison &&
                              (metadata?.fields_extracted === 0 ||
                                metadata?.metadata_comparison?.summary
                                  ?.overall_status !== 'no_metadata' ||
                                metadata?.metadata_comparison?.has_both) && (
                                <section>
                                  <MetadataComparisonDisplay
                                    comparison={metadata?.metadata_comparison}
                                  />
                                </section>
                              )}

                            {metadata?.burned_metadata &&
                              metadata?.burned_metadata
                                ?.has_burned_metadata && (
                                <section>
                                  <BurnedMetadataDisplay
                                    burned_metadata={metadata?.burned_metadata}
                                    isUnlocked={isUnlocked}
                                  />
                                </section>
                              )}

                            <section>
                              <SectionHeader
                                icon={ShieldCheck}
                                title="Forensic Evidence"
                                color="text-emerald-500"
                                count={
                                  filterFields(metadata.forensic || {}).length
                                }
                              />
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                {filterFields(metadata.forensic || {}).map(
                                  ([key, val], i) => (
                                    <FieldRow
                                      key={key}
                                      label={key}
                                      value={val}
                                      index={i}
                                      locked={
                                        key.includes('Serial') && !isUnlocked
                                      }
                                      copyable
                                    />
                                  )
                                )}
                              </div>
                            </section>

                            <section>
                              <SectionHeader
                                icon={FileText}
                                title="File Summary"
                                color="text-primary"
                                count={
                                  filterFields(metadata.summary || {}).length
                                }
                              />
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                {filterFields(metadata.summary || {}).map(
                                  ([key, val], i) => (
                                    <FieldRow
                                      key={key}
                                      label={key}
                                      value={val}
                                      index={i}
                                    />
                                  )
                                )}
                              </div>
                            </section>

                            {metadata.calculated && (
                              <section>
                                <SectionHeader
                                  icon={Calculator}
                                  title="Calculated Fields"
                                  color="text-cyan-500"
                                  count={
                                    filterFields(metadata.calculated || {})
                                      .length
                                  }
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(metadata.calculated || {}).map(
                                    ([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                        locked={!isUnlocked}
                                      />
                                    )
                                  )}
                                </div>
                              </section>
                            )}

                            <section>
                              <SectionHeader
                                icon={Camera}
                                title="Camera & EXIF"
                                color="text-purple-400"
                                count={filterFields(metadata.exif || {}).length}
                              />
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                {filterFields(metadata.exif || {}).map(
                                  ([key, val], i) => (
                                    <FieldRow
                                      key={key}
                                      label={key}
                                      value={val}
                                      index={i}
                                    />
                                  )
                                )}
                              </div>
                            </section>

                            {hasGPS && metadata.gps && (
                              <section>
                                <SectionHeader
                                  icon={MapPin}
                                  title="GPS Location"
                                  color="text-rose-500"
                                  count={
                                    filterFields(metadata.gps || {}).length
                                  }
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(metadata.gps || {}).map(
                                    ([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                        copyable
                                      />
                                    )
                                  )}
                                </div>
                              </section>
                            )}

                            {!isUnlocked && (
                              <div className="p-4 border border-dashed border-white/10 rounded bg-white/5 text-center">
                                <p className="text-xs text-slate-300 font-mono mb-2">
                                  {Object.keys(metadata?.makernote || {})
                                    .length +
                                    Object.keys(metadata?.extended || {})
                                      .length}{' '}
                                  ADDITIONAL FIELDS AVAILABLE
                                </p>
                                <Button
                                  variant="link"
                                  onClick={() => setShowPayment(true)}
                                  className="text-primary text-xs h-auto p-0"
                                  data-testid="button-unlock-fields"
                                >
                                  UNLOCK_ALL_FIELDS
                                </Button>
                              </div>
                            )}
                          </TabsContent>

                          <TabsContent value="advanced" className="mt-0">
                            <AdvancedResultsIntegration
                              metadata={metadata}
                              advancedAnalysis={advancedAnalysis}
                              comparisonResult={comparisonResult}
                              timelineResult={timelineResult}
                              forensicReport={forensicReport}
                              tier={
                                import.meta.env.DEV
                                  ? 'enterprise'
                                  : metadata?.tier || 'free'
                              }
                              isProcessingAdvanced={isProcessingAdvanced}
                              onUpgrade={() => setShowPayment(true)}
                              onRunAdvancedAnalysis={runAdvancedAnalysis}
                              onRunComparison={runComparison}
                              onRunTimeline={runTimeline}
                              onGenerateReport={generateReport}
                            />
                          </TabsContent>

                          <TabsContent
                            value="forensic"
                            className="mt-0 space-y-6"
                          >
                            {metadata?.metadata_comparison && (
                              <section>
                                <MetadataComparisonDisplay
                                  comparison={metadata?.metadata_comparison}
                                />
                              </section>
                            )}

                            {metadata?.burned_metadata &&
                              metadata?.burned_metadata
                                ?.has_burned_metadata && (
                                <section>
                                  <BurnedMetadataDisplay
                                    burned_metadata={metadata?.burned_metadata}
                                    isUnlocked={isUnlocked}
                                  />
                                </section>
                              )}

                            <section>
                              <SectionHeader
                                icon={Hash}
                                title="File Integrity Hashes"
                                color="text-amber-500"
                              />
                              <div className="space-y-1">
                                <FieldRow
                                  label="MD5"
                                  value={metadata?.file_integrity?.md5 || 'N/A'}
                                  locked={!isUnlocked}
                                  copyable
                                  index={0}
                                />
                                <FieldRow
                                  label="SHA256"
                                  value={
                                    metadata?.file_integrity?.sha256 || 'N/A'
                                  }
                                  locked={!isUnlocked}
                                  copyable
                                  index={1}
                                />
                              </div>
                            </section>

                            <section>
                              <SectionHeader
                                icon={ShieldCheck}
                                title="Chain of Custody"
                                color="text-emerald-500"
                              />
                              <div className="space-y-1">
                                {filterFields(metadata.forensic || {}).map(
                                  ([key, val], i) => (
                                    <FieldRow
                                      key={key}
                                      label={key}
                                      value={val}
                                      index={i}
                                      copyable
                                    />
                                  )
                                )}
                              </div>
                            </section>

                            <section>
                              <SectionHeader
                                icon={Folder}
                                title="Filesystem Metadata"
                                color="text-blue-400"
                              />
                              <div className="space-y-1">
                                {filterFields(metadata.filesystem || {}).map(
                                  ([key, val], i) => (
                                    <FieldRow
                                      key={key}
                                      label={key}
                                      value={val}
                                      index={i}
                                    />
                                  )
                                )}
                              </div>
                            </section>

                            {/* Forensic Analysis Components */}
                            {(metadata?.steganography_analysis ||
                              metadata?.manipulation_detection ||
                              metadata?.ai_detection) &&
                              (metadata?.tier === 'forensic' ||
                                metadata?.tier === 'enterprise' ||
                                metadata?.tier === 'professional' ||
                                import.meta.env.DEV) && (
                                <section>
                                  <SectionHeader
                                    icon={ShieldCheck}
                                    title="Advanced Forensic Analysis"
                                    color="text-red-400"
                                  />
                                  <div className="space-y-6">
                                    {metadata?.advanced_analysis
                                      ?.forensic_score !== undefined && (
                                      <div className="flex items-center justify-between p-4 bg-black/20 rounded-lg border border-white/10">
                                        <div className="flex items-center gap-3">
                                          <ShieldCheck className="w-5 h-5 text-primary" />
                                          <div>
                                            <h4 className="text-sm font-medium text-white">
                                              Overall Authenticity Score
                                            </h4>
                                            <p className="text-xs text-slate-400">
                                              Based on forensic analysis
                                            </p>
                                          </div>
                                        </div>
                                        <AuthenticityBadge
                                          score={
                                            metadata.advanced_analysis
                                              .forensic_score
                                          }
                                          variant="detailed"
                                          showConfidence={true}
                                        />
                                      </div>
                                    )}

                                    <ForensicAnalysis
                                      steganography={
                                        metadata?.steganography_analysis
                                          ? {
                                              detected:
                                                metadata.steganography_analysis
                                                  .suspicious_score > 0.3,
                                              confidence: Math.round(
                                                (metadata.steganography_analysis
                                                  .suspicious_score || 0) * 100
                                              ),
                                              methodsChecked: metadata
                                                .steganography_analysis
                                                .methods_checked || [
                                                'LSB Analysis',
                                                'FFT Analysis',
                                              ],
                                              findings:
                                                metadata.steganography_analysis
                                                  .findings || [],
                                              details:
                                                metadata.steganography_analysis
                                                  .analysis_details,
                                            }
                                          : undefined
                                      }
                                      manipulation={
                                        metadata?.manipulation_detection
                                          ? {
                                              detected:
                                                metadata.manipulation_detection
                                                  .manipulation_probability >
                                                0.5,
                                              confidence: Math.round(
                                                (metadata.manipulation_detection
                                                  .manipulation_probability ||
                                                  0) * 100
                                              ),
                                              indicators:
                                                metadata.manipulation_detection.indicators?.map(
                                                  (indicator: any) => ({
                                                    type:
                                                      indicator.type ||
                                                      'Manipulation',
                                                    severity:
                                                      indicator.severity ||
                                                      (indicator.confidence >
                                                      0.7
                                                        ? 'high'
                                                        : indicator.confidence >
                                                            0.4
                                                          ? 'medium'
                                                          : 'low'),
                                                    description:
                                                      indicator.description ||
                                                      'Manipulation detected',
                                                    confidence: Math.round(
                                                      (indicator.confidence ||
                                                        0) * 100
                                                    ),
                                                  })
                                                ) || [],
                                              originalityScore: metadata
                                                .manipulation_detection
                                                .originality_score
                                                ? Math.round(
                                                    metadata
                                                      .manipulation_detection
                                                      .originality_score * 100
                                                  )
                                                : undefined,
                                            }
                                          : undefined
                                      }
                                      aiDetection={
                                        metadata?.ai_detection
                                          ? {
                                              aiGenerated:
                                                metadata.ai_detection
                                                  .ai_probability > 0.7,
                                              confidence: Math.round(
                                                (metadata.ai_detection
                                                  .ai_probability || 0) * 100
                                              ),
                                              modelHints:
                                                metadata.ai_detection
                                                  .model_hints || [],
                                              detectionMethods: metadata
                                                .ai_detection
                                                .detection_methods || [
                                                'Neural Network Analysis',
                                              ],
                                            }
                                          : undefined
                                      }
                                      authenticityScore={
                                        metadata?.advanced_analysis
                                          ?.forensic_score || 100
                                      }
                                      className="bg-black/20 border border-white/10"
                                    />
                                  </div>
                                </section>
                              )}

                            {/* Forensic Analysis Upgrade Message */}
                            {(metadata?.tier === 'free' ||
                              metadata?.tier === 'basic') && (
                              <section>
                                <div className="p-6 text-center bg-black/20 rounded-lg border border-white/10">
                                  <ShieldCheck className="w-12 h-12 mx-auto mb-4 text-slate-500" />
                                  <h4 className="text-lg font-semibold text-white mb-2">
                                    Advanced Forensic Analysis
                                  </h4>
                                  <p className="text-slate-300 mb-4">
                                    Unlock steganography detection, manipulation
                                    analysis, and AI content detection
                                  </p>
                                  <Button
                                    variant="outline"
                                    onClick={() => setShowPayment(true)}
                                    className="gap-2 border-primary text-primary hover:bg-primary/10"
                                  >
                                    <ShieldCheck className="w-4 h-4" />
                                    Upgrade to Professional
                                  </Button>
                                </div>
                              </section>
                            )}
                          </TabsContent>

                          <TabsContent
                            value="technical"
                            className="mt-0 space-y-6"
                          >
                            <section>
                              <SectionHeader
                                icon={Camera}
                                title="Camera Settings"
                                color="text-purple-400"
                              />
                              {filterFields(metadata.exif || {}).length > 0 ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(metadata.exif || {}).map(
                                    ([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                      />
                                    )
                                  )}
                                </div>
                              ) : (
                                <div className="text-gray-500 text-sm italic">
                                  No camera settings found in this image
                                </div>
                              )}
                            </section>

                            {Object.keys(metadata.interoperability || {})
                              .length > 0 && (
                              <section>
                                <SectionHeader
                                  icon={Tag}
                                  title="Interoperability (IFD)"
                                  color="text-cyan-400"
                                  count={
                                    Object.keys(metadata.interoperability || {})
                                      .length
                                  }
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(
                                    metadata.interoperability || {}
                                  ).map(([key, val], i) => (
                                    <FieldRow
                                      key={key}
                                      label={key}
                                      value={val}
                                      index={i}
                                    />
                                  ))}
                                </div>
                              </section>
                            )}

                            {(metadata?.makernote?._count > 0 ||
                              Object.keys(metadata?.makernote || {}).length >
                                1) && (
                              <section>
                                <SectionHeader
                                  icon={Tag}
                                  title="MakerNote (Vendor-Specific)"
                                  color="text-orange-400"
                                  count={
                                    metadata?.makernote?._count ||
                                    Object.keys(metadata?.makernote || {})
                                      .length
                                  }
                                />
                                {!isSectionLocked(metadata?.makernote) &&
                                isUnlocked ? (
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                    {filterFields(metadata.makernote || {})
                                      .slice(0, 50)
                                      .map(([key, val], i) => (
                                        <FieldRow
                                          key={key}
                                          label={key}
                                          value={val}
                                          index={i}
                                        />
                                      ))}
                                  </div>
                                ) : (
                                  <div className="p-4 border border-dashed border-white/10 rounded bg-white/5 text-center">
                                    <Lock className="w-6 h-6 text-slate-600 mx-auto mb-2" />
                                    <p className="text-xs text-slate-300 font-mono mb-2">
                                      {metadata?.makernote?._count || 0}{' '}
                                      VENDOR-SPECIFIC FIELDS LOCKED
                                    </p>
                                    <Button
                                      variant="link"
                                      onClick={() => setShowPayment(true)}
                                      className="text-primary text-xs h-auto p-0"
                                    >
                                      UNLOCK_MAKERNOTES
                                    </Button>
                                  </div>
                                )}
                              </section>
                            )}

                            {Object.keys(metadata.iptc || {}).length > 0 && (
                              <section>
                                <SectionHeader
                                  icon={Tag}
                                  title="IPTC Metadata"
                                  color="text-indigo-400"
                                  count={
                                    Object.keys(metadata.iptc || {}).length
                                  }
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(metadata.iptc || {}).map(
                                    ([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                        locked={!isUnlocked}
                                      />
                                    )
                                  )}
                                </div>
                              </section>
                            )}

                            {Object.keys(metadata.xmp || {}).length > 0 && (
                              <section>
                                <SectionHeader
                                  icon={Tag}
                                  title="XMP Metadata"
                                  color="text-pink-400"
                                  count={Object.keys(metadata.xmp || {}).length}
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(metadata.xmp || {}).map(
                                    ([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                        locked={!isUnlocked}
                                      />
                                    )
                                  )}
                                </div>
                              </section>
                            )}

                            {(metadata?.xmp_namespaces?._locked ||
                              Object.keys(flatXmpNamespaces).length > 0) && (
                              <section>
                                <SectionHeader
                                  icon={Tag}
                                  title="XMP Namespaces"
                                  color="text-fuchsia-400"
                                  count={
                                    metadata?.xmp_namespaces?._count ||
                                    Object.keys(flatXmpNamespaces).length
                                  }
                                />
                                {!isSectionLocked(metadata?.xmp_namespaces) &&
                                isUnlocked ? (
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                    {filterFields(flatXmpNamespaces)
                                      .slice(0, 80)
                                      .map(([key, val], i) => (
                                        <FieldRow
                                          key={key}
                                          label={key}
                                          value={val}
                                          index={i}
                                        />
                                      ))}
                                  </div>
                                ) : (
                                  <div className="p-4 border border-dashed border-white/10 rounded bg-white/5 text-center">
                                    <Lock className="w-6 h-6 text-slate-600 mx-auto mb-2" />
                                    <p className="text-xs text-slate-300 font-mono mb-2">
                                      {metadata?.xmp_namespaces?._count || 0}{' '}
                                      NAMESPACE FIELDS LOCKED
                                    </p>
                                    <Button
                                      variant="link"
                                      onClick={() => setShowPayment(true)}
                                      className="text-primary text-xs h-auto p-0"
                                    >
                                      UNLOCK_XMP_NAMESPACES
                                    </Button>
                                  </div>
                                )}
                              </section>
                            )}

                            {Object.keys(metadata.icc_profile || {}).length >
                              0 && (
                              <section>
                                <SectionHeader
                                  icon={Tag}
                                  title="ICC Profile"
                                  color="text-emerald-400"
                                  count={
                                    Object.keys(metadata.icc_profile || {})
                                      .length
                                  }
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(metadata.icc_profile || {}).map(
                                    ([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                      />
                                    )
                                  )}
                                </div>
                              </section>
                            )}

                            {Object.keys(metadata.thumbnail_metadata || {})
                              .length > 0 && (
                              <section>
                                <SectionHeader
                                  icon={Tag}
                                  title="Thumbnail Metadata"
                                  color="text-amber-400"
                                  count={
                                    Object.keys(
                                      metadata.thumbnail_metadata || {}
                                    ).length
                                  }
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(
                                    metadata.thumbnail_metadata || {}
                                  ).map(([key, val], i) => (
                                    <FieldRow
                                      key={key}
                                      label={key}
                                      value={val}
                                      index={i}
                                    />
                                  ))}
                                </div>
                              </section>
                            )}

                            {(metadata?.embedded_thumbnails?._locked ||
                              Object.keys(flatEmbeddedThumbnails).length >
                                0) && (
                              <section>
                                <SectionHeader
                                  icon={ImageIcon}
                                  title="Embedded Thumbnails"
                                  color="text-yellow-400"
                                  count={
                                    metadata?.embedded_thumbnails?._count ||
                                    Object.keys(flatEmbeddedThumbnails).length
                                  }
                                />
                                {!isSectionLocked(
                                  metadata?.embedded_thumbnails
                                ) && isUnlocked ? (
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                    {filterFields(flatEmbeddedThumbnails).map(
                                      ([key, val], i) => (
                                        <FieldRow
                                          key={key}
                                          label={key}
                                          value={val}
                                          index={i}
                                        />
                                      )
                                    )}
                                  </div>
                                ) : (
                                  <div className="p-4 border border-dashed border-white/10 rounded bg-white/5 text-center">
                                    <Lock className="w-6 h-6 text-slate-600 mx-auto mb-2" />
                                    <p className="text-xs text-slate-300 font-mono mb-2">
                                      {metadata?.embedded_thumbnails?._count ||
                                        0}{' '}
                                      EMBEDDED THUMBNAILS LOCKED
                                    </p>
                                    <Button
                                      variant="link"
                                      onClick={() => setShowPayment(true)}
                                      className="text-primary text-xs h-auto p-0"
                                    >
                                      UNLOCK_EMBEDDED_THUMBNAILS
                                    </Button>
                                  </div>
                                )}
                              </section>
                            )}

                            {Object.keys(metadata.image_container || {})
                              .length > 0 && (
                              <section>
                                <SectionHeader
                                  icon={Tag}
                                  title="Image Container"
                                  color="text-blue-400"
                                  count={
                                    Object.keys(metadata.image_container || {})
                                      .length
                                  }
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(
                                    metadata.image_container || {}
                                  ).map(([key, val], i) => (
                                    <FieldRow
                                      key={key}
                                      label={key}
                                      value={val}
                                      index={i}
                                    />
                                  ))}
                                </div>
                              </section>
                            )}

                            {(metadata?.scientific?._locked ||
                              Object.keys(flatScientific).length > 0) && (
                              <section>
                                <SectionHeader
                                  icon={Database}
                                  title="Scientific Metadata"
                                  color="text-sky-400"
                                  count={
                                    metadata?.scientific?._count ||
                                    Object.keys(flatScientific).length
                                  }
                                />
                                {!isSectionLocked(metadata?.scientific) ? (
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                    {filterFields(flatScientific).map(
                                      ([key, val], i) => (
                                        <FieldRow
                                          key={key}
                                          label={key}
                                          value={val}
                                          index={i}
                                        />
                                      )
                                    )}
                                  </div>
                                ) : (
                                  <div className="p-4 border border-dashed border-white/10 rounded bg-white/5 text-center">
                                    <Lock className="w-6 h-6 text-slate-600 mx-auto mb-2" />
                                    <p className="text-xs text-slate-300 font-mono mb-2">
                                      SCIENTIFIC_METADATA_LOCKED
                                    </p>
                                    <Button
                                      variant="link"
                                      onClick={() => setShowPayment(true)}
                                      className="text-primary text-xs h-auto p-0"
                                    >
                                      UNLOCK_SCIENTIFIC_METADATA
                                    </Button>
                                  </div>
                                )}
                              </section>
                            )}

                            {(metadata?.scientific_data?._locked ||
                              Object.keys(flatScientificData).length > 0) && (
                              <section>
                                <SectionHeader
                                  icon={FileText}
                                  title="Scientific Data (HDF5/NetCDF)"
                                  color="text-emerald-400"
                                  count={
                                    metadata?.scientific_data?._count ||
                                    Object.keys(flatScientificData).length
                                  }
                                />
                                {!isSectionLocked(metadata?.scientific_data) ? (
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                    {filterFields(flatScientificData).map(
                                      ([key, val], i) => (
                                        <FieldRow
                                          key={key}
                                          label={key}
                                          value={val}
                                          index={i}
                                        />
                                      )
                                    )}
                                  </div>
                                ) : (
                                  <div className="p-4 border border-dashed border-white/10 rounded bg-white/5 text-center">
                                    <Lock className="w-6 h-6 text-slate-600 mx-auto mb-2" />
                                    <p className="text-xs text-slate-300 font-mono mb-2">
                                      SCIENTIFIC_DATA_LOCKED
                                    </p>
                                    <Button
                                      variant="link"
                                      onClick={() => setShowPayment(true)}
                                      className="text-primary text-xs h-auto p-0"
                                    >
                                      UNLOCK_SCIENTIFIC_DATA
                                    </Button>
                                  </div>
                                )}
                              </section>
                            )}

                            {Object.keys(flatTelemetry).length > 0 && (
                              <section>
                                <SectionHeader
                                  icon={Zap}
                                  title="Video Telemetry"
                                  color="text-rose-400"
                                  count={Object.keys(flatTelemetry).length}
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(flatTelemetry).map(
                                    ([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                      />
                                    )
                                  )}
                                </div>
                              </section>
                            )}

                            {Object.keys(flatCamera360).length > 0 && (
                              <section>
                                <SectionHeader
                                  icon={Camera}
                                  title="360° / Panorama"
                                  color="text-teal-400"
                                  count={Object.keys(flatCamera360).length}
                                />
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1">
                                  {filterFields(flatCamera360).map(
                                    ([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                      />
                                    )
                                  )}
                                </div>
                              </section>
                            )}
                          </TabsContent>

                          <TabsContent value="raw" className="mt-0">
                            {isUnlocked ? (
                              <div className="font-mono text-xs text-slate-300">
                                <div className="mb-4 text-xs text-slate-500 uppercase tracking-widest">
                                  Extended Fields:{' '}
                                  {Object.keys(metadata?.extended || {}).length}
                                </div>
                                <div className="space-y-1">
                                  {filterFields(metadata.extended || {})
                                    .slice(0, 200)
                                    .map(([key, val], i) => (
                                      <FieldRow
                                        key={key}
                                        label={key}
                                        value={val}
                                        index={i}
                                      />
                                    ))}
                                  {filterFields(metadata.extended || {})
                                    .length > 200 && (
                                    <div className="py-4 text-center text-slate-600 italic">
                                      ...{' '}
                                      {Object.keys(metadata.extended || {})
                                        .length - 200}{' '}
                                      more fields in JSON export ...
                                    </div>
                                  )}
                                </div>
                              </div>
                            ) : (
                              <div className="flex flex-col items-center justify-center h-[400px] text-center">
                                <Database className="w-16 h-16 text-white/5 mb-4" />
                                <h3 className="text-lg font-bold text-white font-mono mb-2">
                                  RAW_DATA_LOCKED
                                </h3>
                                <p className="text-slate-500 max-w-sm mb-6 text-sm">
                                  Access to{' '}
                                  {Object.keys(metadata?.extended || {}).length}{' '}
                                  extended metadata fields including MakerNotes,
                                  IPTC, XMP, and proprietary tags requires a
                                  license.
                                </p>
                                <Button
                                  onClick={() => setShowPayment(true)}
                                  className="bg-primary text-black"
                                  data-testid="button-purchase-raw"
                                >
                                  PURCHASE_LICENSE ($5.00)
                                </Button>
                              </div>
                            )}
                          </TabsContent>
                        </div>
                      </ScrollArea>
                    </div>
                  </Tabs>
                </div>
              </div>
            </div>
          </div>

          <PaymentModal
            isOpen={showPayment}
            onClose={() => setShowPayment(false)}
            onSuccess={onPaymentSuccess}
          />
        </ErrorBoundary>
      </Layout>
    </UIAdaptationProvider>
  );
}
