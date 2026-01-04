/**
 * Three-Pane Metadata Explorer
 *
 * A comprehensive interface for exploring metadata with:
 * - Left Pane: Smart File Browser with metadata density indicators
 * - Middle Pane: Context-Aware Metadata Tree with progressive disclosure
 * - Right Pane: Drill-Down Detail View with rich visualizations
 */

import React, {
  useEffect,
  useState,
  useMemo,
  useCallback,
  useRef,
} from 'react';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Search,
  FileImage,
  FileVideo,
  FileAudio,
  FileText,
  File,
  Camera,
  MapPin,
  Clock,
  Shield,
  Tag,
  ExternalLink,
  Copy,
  Eye,
  Layers,
  Info,
  Lock,
} from 'lucide-react';
import { getFieldExplanation, hasExplanation } from '@/utils/fieldExplanations';
import { getCategoryDefinition } from '@/utils/metadataCategories';
import { loadPreferences, savePreferences } from '@/utils/userPreferences';
import { searchMetadata } from '@/utils/metadataSearch';
import { EducationalExamples } from '@/components/educational-examples';
import { AdvancedAnalysisResults } from '@/components/AdvancedAnalysisResults';

// ============================================================================
// Types
// ============================================================================

interface MetadataField {
  key: string;
  value: any;
  category: string;
  description?: string;
  significance?: string;
  locked?: boolean;
  highlightedKey?: string; // HTML string with <mark> tags
  highlightedValue?: string; // HTML string with <mark> tags
}

/**
 * Runtime type guard for MetadataField
 * Validates that an object has all required fields of MetadataField
 */
const isMetadataField = (obj: unknown): obj is MetadataField => {
  return (
    obj !== null &&
    typeof obj === 'object' &&
    'key' in obj &&
    typeof (obj as any).key === 'string' &&
    'value' in obj &&
    'category' in obj &&
    typeof (obj as any).category === 'string'
  );
};

interface MetadataCategory {
  name: string;
  displayName: string;
  icon: React.ReactNode;
  fields: MetadataField[];
  fieldCount: number;
  locked?: boolean;
}

interface ProcessedFile {
  id: string;
  name: string;
  type: string;
  size: string;
  metadataDensity: 'low' | 'medium' | 'high';
  fieldCount: number;
  categories: MetadataCategory[];
  rawMetadata: Record<string, any>;
  tier: string;
  processedAt: string;
  advancedAnalysis?: {
    enabled: boolean;
    processing_time_ms: number;
    modules_run: string[];
    forensic_score: number;
    authenticity_assessment: string;
  };
}

interface MetadataExplorerProps {
  files: ProcessedFile[];
  selectedFileId?: string;
  onFileSelect?: (fileId: string) => void;
  viewMode?: 'simple' | 'advanced' | 'raw';
  onViewModeChange?: (mode: 'simple' | 'advanced' | 'raw') => void;
}

// ============================================================================
// Field Significance Tooltips
// ============================================================================

const FIELD_SIGNIFICANCE: Record<string, string> = {
  Make: 'Camera manufacturer - useful for identifying device',
  Model: 'Camera model - helps determine capabilities and age',
  DateTimeOriginal: 'When the photo was actually taken',
  GPSLatitude: 'Geographic latitude where photo was taken',
  GPSLongitude: 'Geographic longitude where photo was taken',
  ShutterCount: 'Number of actuations - indicates camera wear',
  SerialNumber: 'Unique device identifier - forensic evidence',
  Software: 'Software used to process/edit the image',
  ExposureTime: 'How long the sensor was exposed - affects motion blur',
  FNumber: 'Aperture setting - affects depth of field',
  ISO: 'Sensor sensitivity - affects noise levels',
  FocalLength: 'Lens focal length - affects perspective',
  LensModel: 'Specific lens used - affects optical characteristics',
  ColorSpace: 'Color encoding standard - affects color accuracy',
  WhiteBalance: 'Color temperature compensation setting',
  Flash: 'Flash mode used when photo was taken',
  MeteringMode: 'How camera measured light for exposure',
  ExposureMode: 'Auto, manual, or program exposure setting',
  ExposureCompensation: 'User adjustment to auto exposure',
  SceneType: 'What the camera detected the scene to be',
  ImageWidth: 'Pixel width of the image',
  ImageHeight: 'Pixel height of the image',
  BitsPerSample: 'Color depth per channel',
  Compression: 'Image compression method used',
  Orientation: 'How image should be rotated for display',
  XResolution: 'Intended horizontal print resolution',
  YResolution: 'Intended vertical print resolution',
  Artist: 'Photographer or creator name',
  Copyright: 'Copyright notice for the image',
  UserComment: 'User-supplied comment or note',
};

// ============================================================================
// Helper Functions
// ============================================================================

function getFileIcon(type: string) {
  if (type.startsWith('image/')) return <FileImage className="h-4 w-4" />;
  if (type.startsWith('video/')) return <FileVideo className="h-4 w-4" />;
  if (type.startsWith('audio/')) return <FileAudio className="h-4 w-4" />;
  if (type === 'application/pdf') return <FileText className="h-4 w-4" />;
  return <File className="h-4 w-4" />;
}

function getDensityColor(density: 'low' | 'medium' | 'high') {
  switch (density) {
    case 'low':
      return 'bg-yellow-500';
    case 'medium':
      return 'bg-blue-500';
    case 'high':
      return 'bg-green-500';
  }
}

function getDensityLabel(density: 'low' | 'medium' | 'high') {
  switch (density) {
    case 'low':
      return 'Basic metadata';
    case 'medium':
      return 'Standard metadata';
    case 'high':
      return 'Rich metadata';
  }
}

function getCategoryIcon(category: string) {
  switch (category.toLowerCase()) {
    case 'exif':
    case 'camera':
      return <Camera className="h-4 w-4" />;
    case 'gps':
    case 'location':
      return <MapPin className="h-4 w-4" />;
    case 'filesystem':
    case 'dates':
      return <Clock className="h-4 w-4" />;
    case 'forensic':
    case 'security':
      return <Shield className="h-4 w-4" />;
    case 'iptc':
    case 'xmp':
    case 'tags':
      return <Tag className="h-4 w-4" />;
    default:
      return <Layers className="h-4 w-4" />;
  }
}

function formatValue(value: any): string {
  if (value === null || value === undefined) return 'N/A';
  if (typeof value === 'object') {
    if (Array.isArray(value)) return value.join(', ');
    return JSON.stringify(value, null, 2);
  }
  return String(value);
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text);
}

/**
 * Component to safely render HTML with highlighted matches
 */
const HighlightedText = ({
  text,
  className,
}: {
  text: string;
  className?: string;
}) => {
  return (
    <span className={className} dangerouslySetInnerHTML={{ __html: text }} />
  );
};

// ============================================================================
// Components
// ============================================================================

/**
 * Left Pane: File Browser with metadata density indicators
 */
function FileBrowser({
  files,
  selectedFileId,
  onFileSelect,
}: {
  files: ProcessedFile[];
  selectedFileId?: string;
  onFileSelect: (id: string) => void;
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFiles = useMemo(() => {
    if (!searchQuery) return files;
    const query = searchQuery.toLowerCase();
    return files.filter(
      file =>
        file.name.toLowerCase().includes(query) ||
        file.type.toLowerCase().includes(query)
    );
  }, [files, searchQuery]);

  return (
    <div className="flex h-full flex-col" data-testid="metadata-file-browser">
      <div className="border-b p-3">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search files..."
            aria-label="Search files"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="pl-8"
          />
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2">
          {filteredFiles.map(file => (
            <button
              key={file.id}
              onClick={() => onFileSelect(file.id)}
              className={`mb-1 flex w-full items-center gap-3 rounded-lg p-3 text-left transition-colors ${
                selectedFileId === file.id
                  ? 'bg-primary/10 text-primary'
                  : 'hover:bg-muted'
              }`}
            >
              <div className="shrink-0">{getFileIcon(file.type)}</div>

              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {file.size} • {file.fieldCount} fields
                </p>
              </div>

              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span
                      className={`h-3 w-3 rounded-full ${getDensityColor(
                        file.metadataDensity
                      )}`}
                    />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{getDensityLabel(file.metadataDensity)}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </button>
          ))}

          {filteredFiles.length === 0 && (
            <div className="py-8 text-center text-sm text-muted-foreground">
              No files match your search
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

/**
 * Middle Pane: Metadata Tree with categories and fields
 */
function MetadataTree({
  file,
  viewMode,
  onFieldSelect,
  selectedField,
}: {
  file: ProcessedFile | null;
  viewMode: 'simple' | 'advanced' | 'raw';
  onFieldSelect: (field: MetadataField | null) => void;
  selectedField: MetadataField | null;
}) {
  const [searchQuery, setSearchQuery] = useState('');

  // Load user preferences for expanded categories
  const [expandedCategories, setExpandedCategories] = useState<string[]>(() => {
    const prefs = loadPreferences();
    const expanded = prefs.expandedCategories;

    // Historical note: preferences may contain Phase-1 "smart category" keys
    // (e.g. "capture", "location", "file"). This explorer’s accordion uses
    // top-level metadata sections (e.g. "summary", "exif", "gps"). If the
    // stored preferences don't match the current section naming scheme, fall
    // back to runtime defaults based on the current file.
    const expandedStrings = Array.isArray(expanded)
      ? expanded.filter((c): c is string => typeof c === 'string')
      : [];

    // If we already know the active file on first render, validate immediately
    // so the accordion isn't rendered collapsed in cases where the defaults are
    // legacy keys.
    if (file) {
      const available = new Set(file.categories.map(c => c.name));
      const valid = expandedStrings.filter(c => available.has(c));
      if (valid.length > 0) return valid;

      const preferredOrder = ['summary', 'exif', 'gps', 'image', 'filesystem'];
      const defaults = preferredOrder.filter(name => available.has(name));
      const fallback = file.categories.slice(0, 3).map(c => c.name);
      return defaults.length > 0 ? defaults : fallback;
    }

    return expandedStrings;
  });

  // If we have no valid stored expansion state (or it doesn't match this file),
  // expand a sensible set by default.
  useEffect(() => {
    if (!file) return;
    const preferredOrder = ['summary', 'exif', 'gps', 'image', 'filesystem'];
    const available = new Set(file.categories.map(c => c.name));
    const hasAnyValid = expandedCategories.some(c => available.has(c));
    if (expandedCategories.length > 0 && hasAnyValid) return;

    const defaults = preferredOrder.filter(name => available.has(name));

    // If none of our preferred categories exist (custom test fixtures, new formats),
    // expand the first few categories so the UI isn't an empty accordion.
    const fallback = file.categories.slice(0, 3).map(c => c.name);
    setExpandedCategories(defaults.length > 0 ? defaults : fallback);
  }, [file, expandedCategories]);

  // Persist category expansion state
  const handleCategoryExpand = useCallback((categories: string[]) => {
    setExpandedCategories(categories);
    const prefs = loadPreferences();
    savePreferences({ ...prefs, expandedCategories: categories });
  }, []);

  // Filter categories based on viewMode and search query
  const visibleCategories = useMemo(() => {
    if (!file) return [];

    let categories = [...file.categories];

    // Simple mode: only show key categories
    if (viewMode === 'simple') {
      const simpleCategories = [
        'summary',
        'exif',
        'camera',
        'gps',
        'image',
        'filesystem',
      ];
      categories = categories.filter(c =>
        simpleCategories.includes(c.name.toLowerCase())
      );
    }

    // Apply active search
    if (searchQuery.trim()) {
      return categories
        .map(category => {
          // Build data record for search util
          const categoryData: Record<string, any> = {};
          const fieldMap = new Map<string, MetadataField>();

          category.fields.forEach(field => {
            categoryData[field.key] = field.value;
            fieldMap.set(field.key, field);
          });

          const results = searchMetadata(categoryData, {
            query: searchQuery,
            fuzzyMatch: true,
            caseSensitive: false,
          });

          // Reconstruct fields with highlighting
          const matchedFields = results
            .map(result => {
              const originalField = fieldMap.get(result.fieldKey);
              if (!originalField) return null;

              return {
                ...originalField,
                highlightedKey: result.highlightedField,
                highlightedValue: result.highlightedValue,
              };
            })
            .filter(isMetadataField);

          return {
            ...category,
            fields: matchedFields,
          };
        })
        .filter(cat => cat.fields.length > 0);
    }

    return categories;
  }, [file, viewMode, searchQuery]);

  // Auto-expand on search
  useEffect(() => {
    if (searchQuery.trim() && visibleCategories.length > 0) {
      setExpandedCategories(visibleCategories.map(c => c.name));
    }
  }, [searchQuery, visibleCategories.length]);

  if (!file) {
    return (
      <div className="flex h-full items-center justify-center overflow-auto bg-muted/5">
        <EducationalExamples />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col" data-testid="metadata-tree">
      <div className="border-b p-3">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search fields..."
            aria-label="Search fields"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="pl-8"
          />
        </div>
      </div>

      {/* Advanced Analysis Results */}
      {file.advancedAnalysis && (
        <div className="border-b p-4">
          <AdvancedAnalysisResults
            steganography={file.rawMetadata.steganography_analysis}
            manipulation={file.rawMetadata.manipulation_detection}
            aiDetection={file.rawMetadata.ai_detection}
            timeline={file.rawMetadata.timeline_analysis}
          />
        </div>
      )}

      <ScrollArea className="flex-1">
        <Accordion
          type="multiple"
          value={expandedCategories}
          onValueChange={handleCategoryExpand}
          className="p-2"
        >
          {visibleCategories.map(category => (
            <AccordionItem
              key={category.name}
              value={category.name}
              className="border-none"
            >
              <AccordionTrigger className="rounded-lg px-3 py-2 hover:bg-muted hover:no-underline">
                <div className="flex flex-col items-start gap-1 flex-1">
                  <div className="flex items-center gap-2 w-full">
                    {getCategoryIcon(category.name)}
                    <span className="font-medium">{category.displayName}</span>
                    <Badge variant="secondary" className="ml-auto">
                      {category.fieldCount > category.fields.length
                        ? `${category.fields.length}/${category.fieldCount}`
                        : category.fieldCount}
                    </Badge>
                    {category.locked && (
                      <Lock className="h-3 w-3 text-muted-foreground" />
                    )}
                  </div>
                  {(() => {
                    const catDef = getCategoryDefinition(category.name);
                    return (
                      catDef?.description && (
                        <span className="text-xs text-muted-foreground">
                          {catDef.description}
                        </span>
                      )
                    );
                  })()}
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-1 pl-4">
                  {category.fields.map(field => {
                    if (!field) return null;
                    return (
                      <button
                        key={field.key}
                        onClick={() => onFieldSelect(field)}
                        className={`flex w-full items-center justify-between rounded-md p-2 text-left text-sm transition-colors ${
                          selectedField?.key === field.key
                            ? 'bg-primary/10 text-primary'
                            : 'hover:bg-muted'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          {field.highlightedKey ? (
                            <HighlightedText
                              text={field.highlightedKey}
                              className="font-medium [&>mark]:bg-yellow-200 [&>mark]:text-black dark:[&>mark]:bg-yellow-800 dark:[&>mark]:text-white"
                            />
                          ) : (
                            <span className="font-medium">{field.key}</span>
                          )}
                          {(hasExplanation(field.key) ||
                            field.significance) && (
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <span className="inline-flex items-center">
                                    <Info className="h-3 w-3 text-muted-foreground" />
                                  </span>
                                </TooltipTrigger>
                                <TooltipContent className="max-w-sm">
                                  {(() => {
                                    const explanation = getFieldExplanation(
                                      field.key
                                    );
                                    if (explanation) {
                                      return (
                                        <div className="space-y-2">
                                          <div>
                                            <p className="font-semibold">
                                              {explanation.title}
                                            </p>
                                            <p className="text-sm mt-1">
                                              {explanation.description}
                                            </p>
                                          </div>
                                          {explanation.details &&
                                            explanation.details.length > 0 && (
                                              <div>
                                                <p className="text-xs font-semibold mb-1">
                                                  Details:
                                                </p>
                                                <ul className="text-xs space-y-1">
                                                  {explanation.details.map(
                                                    (detail, idx) => (
                                                      <li key={idx}>
                                                        • {detail}
                                                      </li>
                                                    )
                                                  )}
                                                </ul>
                                              </div>
                                            )}
                                          {explanation.useCases &&
                                            explanation.useCases.length > 0 && (
                                              <div>
                                                <p className="text-xs font-semibold mb-1">
                                                  Use Cases:
                                                </p>
                                                <ul className="text-xs space-y-1">
                                                  {explanation.useCases.map(
                                                    (useCase, idx) => (
                                                      <li key={idx}>
                                                        • {useCase}
                                                      </li>
                                                    )
                                                  )}
                                                </ul>
                                              </div>
                                            )}
                                        </div>
                                      );
                                    } else if (field.significance) {
                                      return <p>{field.significance}</p>;
                                    }
                                    return null;
                                  })()}
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          )}
                        </div>
                        <span className="truncate text-muted-foreground max-w-30">
                          {field.highlightedValue ? (
                            <HighlightedText
                              text={field.highlightedValue}
                              className="[&>mark]:bg-yellow-200 [&>mark]:text-black dark:[&>mark]:bg-yellow-800 dark:[&>mark]:text-white"
                            />
                          ) : (
                            formatValue(field.value)
                          )}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </ScrollArea>
    </div>
  );
}

/**
 * Right Pane: Detail View with rich visualizations
 */
function DetailView({
  field,
  file,
}: {
  field: MetadataField | null;
  file: ProcessedFile | null;
}) {
  if (!field) {
    return (
      <div
        className="flex h-full items-center justify-center p-8 text-center text-muted-foreground"
        data-testid="metadata-detail-view"
      >
        <div>
          <Layers className="mx-auto mb-4 h-12 w-12 opacity-50" />
          <p>Select a field to see details</p>
        </div>
      </div>
    );
  }

  const formattedValue = formatValue(field.value);
  const isLongValue = formattedValue.length > 100;
  const isGPS =
    field.key.toLowerCase().includes('gps') ||
    field.key.toLowerCase().includes('latitude') ||
    field.key.toLowerCase().includes('longitude');
  const isUrl =
    typeof field.value === 'string' && field.value.startsWith('http');

  return (
    <div className="flex h-full flex-col" data-testid="metadata-detail-view">
      <div className="border-b p-4">
        <h3 className="text-lg font-semibold">{field.key}</h3>
        <p className="text-sm text-muted-foreground">{field.category}</p>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {/* Value Display */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center justify-between text-sm">
                Value
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(formattedValue)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLongValue ? (
                <pre className="overflow-x-auto rounded-md bg-muted p-3 text-sm">
                  {formattedValue}
                </pre>
              ) : (
                <p className="text-lg font-medium">{formattedValue}</p>
              )}
            </CardContent>
          </Card>

          {/* Significance */}
          {field.significance && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Why This Matters</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {field.significance}
                </p>
              </CardContent>
            </Card>
          )}

          {/* GPS Link */}
          {isGPS && file?.rawMetadata?.gps && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <MapPin className="h-4 w-4" />
                  Location
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {file.rawMetadata.gps.google_maps_url && (
                    <a
                      href={file.rawMetadata.gps.google_maps_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-primary hover:underline"
                    >
                      <ExternalLink className="h-4 w-4" />
                      Open in Google Maps
                    </a>
                  )}
                  {file.rawMetadata.gps.coordinates && (
                    <p className="text-sm text-muted-foreground">
                      {file.rawMetadata.gps.coordinates}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* URL Link */}
          {isUrl && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Link</CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href={field.value}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm text-primary hover:underline"
                >
                  <ExternalLink className="h-4 w-4" />
                  Open Link
                </a>
              </CardContent>
            </Card>
          )}

          {/* Technical Info */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Technical Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Category</span>
                <span>{field.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Type</span>
                <span>{typeof field.value}</span>
              </div>
              {typeof field.value === 'string' && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Length</span>
                  <span>{field.value.length} characters</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    </div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

export function MetadataExplorer({
  files,
  selectedFileId,
  onFileSelect,
  viewMode,
  onViewModeChange,
}: MetadataExplorerProps) {
  const [internalSelectedFileId, setInternalSelectedFileId] = useState<
    string | undefined
  >(selectedFileId);
  const [selectedField, setSelectedField] = useState<MetadataField | null>(
    null
  );
  const [internalViewMode, setInternalViewMode] = useState<
    'simple' | 'advanced' | 'raw'
  >(viewMode ?? 'advanced');

  const activeFileId = selectedFileId ?? internalSelectedFileId;
  const isViewModeControlled = viewMode !== undefined;
  const activeViewMode = isViewModeControlled ? viewMode : internalViewMode;

  // Radix Tabs value-change can be finicky under jsdom + synthetic events.
  // Track the last emitted view mode so clicks / onValueChange don't double-fire.
  const lastEmittedViewModeRef = useRef<'simple' | 'advanced' | 'raw'>(
    activeViewMode
  );
  useEffect(() => {
    lastEmittedViewModeRef.current = activeViewMode;
  }, [activeViewMode]);

  const selectedFile = useMemo(
    () => files.find(f => f.id === activeFileId) ?? null,
    [files, activeFileId]
  );

  const handleFileSelect = useCallback(
    (id: string) => {
      setInternalSelectedFileId(id);
      setSelectedField(null);
      onFileSelect?.(id);
    },
    [onFileSelect]
  );

  const handleViewModeChange = useCallback(
    (mode: 'simple' | 'advanced' | 'raw') => {
      if (lastEmittedViewModeRef.current === mode) return;
      lastEmittedViewModeRef.current = mode;
      if (!isViewModeControlled) {
        setInternalViewMode(mode);
      }
      onViewModeChange?.(mode);
    },
    [isViewModeControlled, onViewModeChange]
  );

  return (
    <div className="flex h-full flex-col">
      {/* View Mode Tabs */}
      <div className="flex items-center justify-between border-b px-4 py-2">
        <h2 className="font-semibold">Metadata Explorer</h2>
        <Tabs
          value={activeViewMode}
          onValueChange={v =>
            handleViewModeChange(v as 'simple' | 'advanced' | 'raw')
          }
        >
          <TabsList>
            <TabsTrigger
              value="simple"
              className="flex items-center gap-1"
              onClick={() => handleViewModeChange('simple')}
            >
              <Eye className="h-3 w-3" />
              Simple
            </TabsTrigger>
            <TabsTrigger
              value="advanced"
              className="flex items-center gap-1"
              onClick={() => handleViewModeChange('advanced')}
            >
              <Layers className="h-3 w-3" />
              Advanced
            </TabsTrigger>
            <TabsTrigger
              value="raw"
              className="flex items-center gap-1"
              onClick={() => handleViewModeChange('raw')}
            >
              <FileText className="h-3 w-3" />
              Raw
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Three-Pane Layout */}
      <ResizablePanelGroup direction="horizontal" className="flex-1">
        {/* Left Pane: File Browser */}
        <ResizablePanel defaultSize={20} minSize={15} maxSize={30}>
          <FileBrowser
            files={files}
            selectedFileId={activeFileId}
            onFileSelect={handleFileSelect}
          />
        </ResizablePanel>

        <ResizableHandle withHandle />

        {/* Middle Pane: Metadata Tree */}
        <ResizablePanel defaultSize={40} minSize={30}>
          {activeViewMode === 'raw' ? (
            <ScrollArea className="h-full p-4">
              <pre className="text-xs" data-testid="metadata-raw-json">
                {JSON.stringify(selectedFile?.rawMetadata ?? {}, null, 2)}
              </pre>
            </ScrollArea>
          ) : (
            <MetadataTree
              file={selectedFile}
              viewMode={activeViewMode}
              onFieldSelect={setSelectedField}
              selectedField={selectedField}
            />
          )}
        </ResizablePanel>

        <ResizableHandle withHandle />

        {/* Right Pane: Detail View */}
        <ResizablePanel defaultSize={40} minSize={25}>
          <DetailView field={selectedField} file={selectedFile} />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
}

// ============================================================================
// Helper to convert API response to ProcessedFile format
// ============================================================================

export function convertMetadataToProcessedFile(
  metadata: Record<string, any>,
  id: string
): ProcessedFile {
  const categories: MetadataCategory[] = [];

  // Helper to add category
  const addCategory = (
    name: string,
    displayName: string,
    data: Record<string, any> | null | undefined,
    locked?: boolean
  ) => {
    // Missing sections should simply be omitted. A section is considered "locked"
    // only when the backend explicitly marks it as such.
    if (!data) return;

    if (typeof data === 'object' && (data as any)._locked) {
      categories.push({
        name,
        displayName,
        icon: getCategoryIcon(name),
        fields: [],
        fieldCount: 0,
        locked: true,
      });
      return;
    }

    const fields: MetadataField[] = Object.entries(data)
      .filter(([key]) => !key.startsWith('_'))
      .map(([key, value]) => ({
        key,
        value,
        category: displayName,
        significance: FIELD_SIGNIFICANCE[key],
      }));

    categories.push({
      name,
      displayName,
      icon: getCategoryIcon(name),
      fields,
      fieldCount: fields.length,
      locked,
    });
  };

  // Add categories from metadata
  addCategory('summary', 'Summary', metadata.summary);
  addCategory('exif', 'Camera & EXIF', metadata.exif);
  addCategory('image', 'Image Properties', metadata.image);
  addCategory('gps', 'Location', metadata.gps);
  addCategory('filesystem', 'File System', metadata.filesystem);
  addCategory('hashes', 'File Integrity', metadata.file_integrity);
  addCategory('calculated', 'Calculated', metadata.calculated);
  addCategory('forensic', 'Forensic', metadata.forensic);
  addCategory('makernote', 'MakerNotes', metadata.makernote);
  addCategory('iptc', 'IPTC', metadata.iptc);
  addCategory('xmp', 'XMP', metadata.xmp);
  addCategory('video', 'Video', metadata.video);
  addCategory('audio', 'Audio', metadata.audio);
  addCategory('pdf', 'PDF', metadata.pdf);

  // Calculate metadata density
  const totalFields = categories.reduce((sum, cat) => sum + cat.fieldCount, 0);
  let density: 'low' | 'medium' | 'high' = 'low';
  if (totalFields > 100) density = 'high';
  else if (totalFields > 30) density = 'medium';

  return {
    id,
    name: metadata.filename || 'Unknown',
    type: metadata.mime_type || 'application/octet-stream',
    size: metadata.filesize || 'Unknown',
    metadataDensity: density,
    fieldCount: totalFields,
    categories: categories.filter(c => c.fieldCount > 0 || c.locked),
    rawMetadata: metadata,
    tier: metadata.tier || 'free',
    processedAt: new Date().toISOString(),
  };
}

export default MetadataExplorer;
