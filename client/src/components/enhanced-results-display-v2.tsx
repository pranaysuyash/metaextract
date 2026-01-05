import React, { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import {
  Search,
  Download,
  Copy,
  Eye,
  EyeOff,
  Filter,
  FileJson,
  Database,
  Image,
  Video,
  Music,
  FileText,
  Globe,
  Lock,
  Shield,
  Calendar,
  MapPin,
  Camera,
  Smartphone,
  Palette,
  Ruler,
  Clock,
  Hash,
  EyeIcon,
  Mail,
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface MetadataResult {
  filename: string;
  filesize: string;
  filetype: string;
  mime_type: string;
  tier: string;
  fields_extracted: number;
  processing_ms: number;
  file_integrity: Record<string, string>;
  filesystem: Record<string, any>;
  calculated: Record<string, any>;
  gps: Record<string, any> | null;
  summary: Record<string, any>;
  forensic: Record<string, any>;
  exif: Record<string, any>;
  image: Record<string, any> | null;
  video: Record<string, any> | null;
  audio: Record<string, any> | null;
  pdf: Record<string, any> | null;
  svg: Record<string, any> | null;
  makernote: Record<string, any> | null;
  iptc: Record<string, any> | null;
  xmp: Record<string, any> | null;
  normalized?: Record<string, any> | null;
  web_metadata?: Record<string, any> | null;
  social_media?: Record<string, any> | null;
  mobile_metadata?: Record<string, any> | null;
  forensic_security?: Record<string, any> | null;
  action_camera?: Record<string, any> | null;
  print_publishing?: Record<string, any> | null;
  workflow_dam?: Record<string, any> | null;
  audio_advanced?: Record<string, any> | null;
  video_advanced?: Record<string, any> | null;
  steganography_analysis?: Record<string, any> | null;
  manipulation_detection?: Record<string, any> | null;
  ai_detection?: Record<string, any> | null;
  timeline_analysis?: Record<string, any> | null;
  iptc_raw?: Record<string, any> | null;
  xmp_raw?: Record<string, any> | null;
  thumbnail?: Record<string, any> | null;
  perceptual_hashes?: Record<string, any> | null;
  locked_fields: string[];
  burned_metadata?: Record<string, any> | null;
  metadata_comparison?: Record<string, any> | null;
  advanced_analysis?: {
    enabled: boolean;
    processing_time_ms: number;
    modules_run: string[];
    forensic_score: number;
    authenticity_assessment: string;
  } | null;
  // Specialized Modules
  medical_imaging?: Record<string, any> | null;
  astronomical_data?: Record<string, any> | null;
  geospatial_analysis?: Record<string, any> | null;
  scientific_instruments?: Record<string, any> | null;
  drone_telemetry?: Record<string, any> | null;
  blockchain_provenance?: Record<string, any> | null;
  emerging_technology?: Record<string, any> | null;
  document_analysis?: Record<string, any> | null;
  scientific_research?: Record<string, any> | null;
  multimedia_entertainment?: Record<string, any> | null;
  industrial_manufacturing?: Record<string, any> | null;
  financial_business?: Record<string, any> | null;
  healthcare_medical?: Record<string, any> | null;
  transportation_logistics?: Record<string, any> | null;
  education_academic?: Record<string, any> | null;
  legal_compliance?: Record<string, any> | null;
  environmental_sustainability?: Record<string, any> | null;
  social_media_digital?: Record<string, any> | null;
  gaming_entertainment?: Record<string, any> | null;
  // Email metadata
  email?: Record<string, any> | null;
  [key: string]: any;
}

interface EnhancedResultsDisplayProps {
  result: MetadataResult;
}

/**
 * Enhanced Results Display Component
 * Provides an improved interface for displaying metadata extraction results
 * with better organization, filtering, and visualization.
 */
export function EnhancedResultsDisplayV2({
  result,
}: EnhancedResultsDisplayProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('summary');
  const [expandedCategories, setExpandedCategories] = useState<
    Record<string, boolean>
  >({});
  const [visibleFields, setVisibleFields] = useState<Record<string, boolean>>(
    {}
  );

  // Toggle category expansion
  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category],
    }));
  };

  // Toggle field visibility
  const toggleFieldVisibility = (category: string, field: string) => {
    const key = `${category}.${field}`;
    setVisibleFields(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Filter metadata based on search term
  const filteredMetadata = useMemo(() => {
    if (!searchTerm) return result;

    const filtered: any = { ...result };
    const lowerSearch = searchTerm.toLowerCase();

    // Filter each category
    Object.entries(result).forEach(([key, value]) => {
      if (
        typeof value === 'object' &&
        value !== null &&
        !Array.isArray(value)
      ) {
        const filteredValue: any = {};
        Object.entries(value).forEach(([field, fieldValue]) => {
          if (
            field.toLowerCase().includes(lowerSearch) ||
            String(fieldValue).toLowerCase().includes(lowerSearch)
          ) {
            filteredValue[field] = fieldValue;
          }
        });
        filtered[key] = filteredValue;
      }
    });

    return filtered;
  }, [result, searchTerm]);

  // Get category icon
  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'exif':
        return <Camera className="w-4 h-4" />;
      case 'gps':
        return <MapPin className="w-4 h-4" />;
      case 'image':
        return <Image className="w-4 h-4" />;
      case 'video':
        return <Video className="w-4 h-4" />;
      case 'audio':
        return <Music className="w-4 h-4" />;
      case 'pdf':
        return <FileText className="w-4 h-4" />;
      case 'file_integrity':
        return <Shield className="w-4 h-4" />;
      case 'forensic':
        return <EyeIcon className="w-4 h-4" />;
      case 'makernote':
        return <Smartphone className="w-4 h-4" />;
      case 'iptc':
      case 'xmp':
        return <Database className="w-4 h-4" />;
      case 'web_metadata':
        return <Globe className="w-4 h-4" />;
      case 'social_media':
        return <Globe className="w-4 h-4" />;
      case 'mobile_metadata':
        return <Smartphone className="w-4 h-4" />;
      case 'blockchain_provenance':
        return <Hash className="w-4 h-4" />;
      case 'medical_imaging':
        return <Shield className="w-4 h-4" />;
      case 'astronomical_data':
        return <Globe className="w-4 h-4" />;
      case 'geospatial_analysis':
        return <MapPin className="w-4 h-4" />;
      case 'drone_telemetry':
        return <MapPin className="w-4 h-4" />;
      case 'email':
        return <Mail className="w-4 h-4" />;
      default:
        return <Database className="w-4 h-4" />;
    }
  };

  // Render metadata table for a category
  const renderMetadataTable = (data: Record<string, any>, category: string) => {
    if (!data || typeof data !== 'object') return null;

    const entries = Object.entries(data).filter(
      ([key, value]) =>
        key.toLowerCase().includes(searchTerm.toLowerCase()) ||
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (entries.length === 0) return null;

    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-1/3">Field</TableHead>
            <TableHead>Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {entries.map(([key, value]) => (
            <TableRow key={key}>
              <TableCell className="font-medium">
                <div className="flex items-center gap-2">
                  <span>{key}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleFieldVisibility(category, key)}
                  >
                    {visibleFields[`${category}.${key}`] ? (
                      <Eye className="w-3 h-3" />
                    ) : (
                      <EyeOff className="w-3 h-3" />
                    )}
                  </Button>
                </div>
              </TableCell>
              <TableCell>
                {visibleFields[`${category}.${key}`] !== false ? (
                  <pre className="text-sm max-w-full overflow-x-auto whitespace-pre-wrap break-words">
                    {typeof value === 'object'
                      ? JSON.stringify(value, null, 2)
                      : String(value)}
                  </pre>
                ) : (
                  <span className="text-muted-foreground italic">Hidden</span>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  };

  // Get all metadata categories
  const metadataCategories = Object.keys(result).filter(
    key =>
      typeof result[key as keyof MetadataResult] === 'object' &&
      result[key as keyof MetadataResult] !== null &&
      !['locked_fields', 'error'].includes(key) &&
      !Array.isArray(result[key as keyof MetadataResult])
  );

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileJson className="w-5 h-5" />
                Metadata Extraction Results
              </CardTitle>
              <CardDescription>
                Detailed analysis of {result.filename} (
                {result.fields_extracted} fields extracted)
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">Tier: {result.tier.toUpperCase()}</Badge>
              <Badge variant="secondary">
                {result.fields_extracted} fields
              </Badge>
              <Badge variant="secondary">{result.processing_ms}ms</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search metadata fields..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
            <Button variant="outline">
              <Filter className="w-4 h-4 mr-2" />
              Filter
            </Button>
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">File Info</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <p className="text-sm">
                <span className="font-medium">Name:</span> {result.filename}
              </p>
              <p className="text-sm">
                <span className="font-medium">Size:</span> {result.filesize}
              </p>
              <p className="text-sm">
                <span className="font-medium">Type:</span> {result.filetype}
              </p>
              <p className="text-sm">
                <span className="font-medium">MIME:</span> {result.mime_type}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Processing</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <p className="text-sm">
                <span className="font-medium">Fields:</span>{' '}
                {result.fields_extracted}
              </p>
              <p className="text-sm">
                <span className="font-medium">Time:</span>{' '}
                {result.processing_ms}ms
              </p>
              <p className="text-sm">
                <span className="font-medium">Tier:</span> {result.tier}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Integrity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {result.file_integrity &&
                Object.entries(result.file_integrity).map(([key, value]) => (
                  <p key={key} className="text-sm">
                    <span className="font-medium">{key}:</span> {String(value)}
                  </p>
                ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Categories</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <p className="text-sm">
                <span className="font-medium">Available:</span>{' '}
                {metadataCategories.length}
              </p>
              <p className="text-sm">
                <span className="font-medium">Locked:</span>{' '}
                {result.locked_fields.length}
              </p>
              <p className="text-sm">
                <span className="font-medium">Status:</span>
                <Badge
                  variant={result.error ? 'destructive' : 'default'}
                  className="ml-2"
                >
                  {result.error ? 'Error' : 'Success'}
                </Badge>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Metadata Categories Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6 overflow-x-auto">
          {metadataCategories.slice(0, 6).map(category => (
            <TabsTrigger
              key={category}
              value={category}
              className="whitespace-nowrap"
            >
              <div className="flex items-center gap-1">
                {getCategoryIcon(category)}
                <span className="capitalize">{category.replace('_', ' ')}</span>
              </div>
            </TabsTrigger>
          ))}
          {metadataCategories.length > 6 && (
            <TabsTrigger value="more" className="whitespace-nowrap">
              More...
            </TabsTrigger>
          )}
        </TabsList>

        {metadataCategories.map(category => (
          <TabsContent key={category} value={category} className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getCategoryIcon(category)}
                  <span className="capitalize">
                    {category.replace('_', ' ')}
                  </span>
                  <Badge variant="secondary" className="ml-2">
                    {
                      Object.keys(
                        result[category as keyof MetadataResult] as Record<
                          string,
                          any
                        >
                      ).length
                    }{' '}
                    fields
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {renderMetadataTable(
                  result[category as keyof MetadataResult] as Record<
                    string,
                    any
                  >,
                  category
                )}
              </CardContent>
            </Card>
          </TabsContent>
        ))}

        {metadataCategories.length > 6 && (
          <TabsContent value="more">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {metadataCategories.slice(6).map(category => (
                <Card key={category}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      {getCategoryIcon(category)}
                      <span className="capitalize">
                        {category.replace('_', ' ')}
                      </span>
                      <Badge variant="secondary" className="ml-2">
                        {
                          Object.keys(
                            result[category as keyof MetadataResult] as Record<
                              string,
                              any
                            >
                          ).length
                        }{' '}
                        fields
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderMetadataTable(
                      result[category as keyof MetadataResult] as Record<
                        string,
                        any
                      >,
                      category
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        )}
      </Tabs>

      {/* Collapsible Categories View */}
      <Card>
        <CardHeader>
          <CardTitle>Expandable Categories View</CardTitle>
          <CardDescription>
            Expand each category to view its metadata fields
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            {metadataCategories.map(category => (
              <AccordionItem key={category} value={category}>
                <AccordionTrigger className="flex items-center gap-2">
                  <div className="flex items-center gap-2">
                    {getCategoryIcon(category)}
                    <span className="capitalize">
                      {category.replace('_', ' ')}
                    </span>
                    <Badge variant="secondary" className="ml-2">
                      {
                        Object.keys(
                          result[category as keyof MetadataResult] as Record<
                            string,
                            any
                          >
                        ).length
                      }{' '}
                      fields
                    </Badge>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <ScrollArea className="h-80 rounded-md border p-4">
                    {renderMetadataTable(
                      result[category as keyof MetadataResult] as Record<
                        string,
                        any
                      >,
                      category
                    )}
                  </ScrollArea>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2 justify-end pt-4">
        <Button variant="outline">
          <Copy className="w-4 h-4 mr-2" />
          Copy All Data
        </Button>
        <Button variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export JSON
        </Button>
        <Button variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
        <Button>
          <FileJson className="w-4 h-4 mr-2" />
          View Raw
        </Button>
      </div>
    </div>
  );
}
