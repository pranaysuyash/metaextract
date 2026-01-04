import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Image,
  Video,
  Music,
  FileText,
  MapPin,
  Camera,
  Zap,
  HardDrive,
  Loader2,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';

interface SampleFile {
  id: string;
  name: string;
  filename: string;
  description: string;
  size: string;
  type: string;
  highlights: string[];
  tier_required: string;
}

interface SampleFilesProps {
  onSampleSelect: (sampleId: string) => void;
  currentTier: string;
  className?: string;
}

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) return Image;
  if (type.startsWith('video/')) return Video;
  if (type.startsWith('audio/')) return Music;
  if (type === 'application/pdf') return FileText;
  return FileText;
};

const getFileTypeColor = (type: string) => {
  if (type.startsWith('image/'))
    return 'bg-blue-500/10 text-blue-600 border-blue-200';
  if (type.startsWith('video/'))
    return 'bg-purple-500/10 text-purple-600 border-purple-200';
  if (type.startsWith('audio/'))
    return 'bg-green-500/10 text-green-600 border-green-200';
  if (type === 'application/pdf')
    return 'bg-red-500/10 text-red-600 border-red-200';
  return 'bg-gray-500/10 text-gray-600 border-gray-200';
};

const getTierColor = (tier: string) => {
  switch (tier) {
    case 'free':
      return 'bg-gray-100 text-gray-800';
    case 'professional':
      return 'bg-blue-100 text-blue-800';
    case 'forensic':
      return 'bg-purple-100 text-purple-800';
    case 'enterprise':
      return 'bg-yellow-100 text-yellow-800';
    case 'starter':
      return 'bg-blue-100 text-blue-800';
    case 'premium':
      return 'bg-purple-100 text-purple-800';
    case 'super':
      return 'bg-yellow-100 text-yellow-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getHighlightIcon = (highlight: string) => {
  if (
    highlight.toLowerCase().includes('gps') ||
    highlight.toLowerCase().includes('location')
  )
    return MapPin;
  if (
    highlight.toLowerCase().includes('camera') ||
    highlight.toLowerCase().includes('lens')
  )
    return Camera;
  if (
    highlight.toLowerCase().includes('codec') ||
    highlight.toLowerCase().includes('stream')
  )
    return Video;
  return Zap;
};

export function SampleFiles({
  onSampleSelect,
  currentTier,
  className,
}: SampleFilesProps) {
  const [samples, setSamples] = useState<SampleFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    fetchSamples();
  }, []);

  const fetchSamples = async () => {
    try {
      const response = await fetch('/api/samples');
      if (!response.ok) throw new Error('Failed to fetch samples');

      const data = await response.json();
      setSamples(data.samples);
    } catch (error) {
      console.error('Error fetching samples:', error);
      toast({
        title: 'Error',
        description: 'Failed to load sample files',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSampleSelect = async (sample: SampleFile) => {
    setProcessingId(sample.id);

    try {
      // Download and process the sample file
      const downloadResponse = await fetch(
        `/api/samples/${sample.id}/download`
      );
      if (!downloadResponse.ok) throw new Error('Failed to download sample');

      const blob = await downloadResponse.blob();
      const file = new File([blob], sample.filename, { type: sample.type });

      // Create form data and submit for processing
      const formData = new FormData();
      formData.append('file', file);

      const processResponse = await fetch(`/api/extract?tier=${currentTier}`, {
        method: 'POST',
        body: formData,
      });

      if (!processResponse.ok) throw new Error('Failed to process sample');

      const result = await processResponse.json();

      // Store result and navigate to results
      sessionStorage.setItem('currentMetadata', JSON.stringify(result));
      onSampleSelect(sample.id);

      toast({
        title: 'Sample processed',
        description: `${sample.name} has been analyzed successfully`,
      });
    } catch (error) {
      console.error('Error processing sample:', error);
      toast({
        title: 'Processing failed',
        description:
          error instanceof Error
            ? error.message
            : 'Failed to process sample file',
        variant: 'destructive',
      });
    } finally {
      setProcessingId(null);
    }
  };

  const canAccessSample = (sampleTier: string) => {
    const tierLevels = {
      free: 0,
      professional: 1,
      forensic: 2,
      enterprise: 3,
      starter: 1,
      premium: 2,
      super: 3,
    };
    return (
      tierLevels[currentTier as keyof typeof tierLevels] >=
      tierLevels[sampleTier as keyof typeof tierLevels]
    );
  };

  if (loading) {
    return (
      <div className={cn('flex items-center justify-center p-8', className)}>
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
        <span className="ml-2 text-muted-foreground">
          Loading sample files...
        </span>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold mb-2">Try Sample Files</h3>
        <p className="text-muted-foreground text-sm">
          Explore MetaExtract capabilities with pre-loaded examples
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {samples.map((sample, index) => {
          const FileIcon = getFileIcon(sample.type);
          const canAccess = canAccessSample(sample.tier_required);
          const isProcessing = processingId === sample.id;

          return (
            <motion.div
              key={sample.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card
                className={cn(
                  'h-full transition-all duration-200 hover:shadow-md',
                  !canAccess && 'opacity-60',
                  isProcessing && 'ring-2 ring-primary'
                )}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div
                      className={cn(
                        'w-10 h-10 rounded-lg flex items-center justify-center border',
                        getFileTypeColor(sample.type)
                      )}
                    >
                      <FileIcon className="w-5 h-5" />
                    </div>

                    <Badge
                      variant="outline"
                      className={cn(
                        'text-xs',
                        getTierColor(sample.tier_required)
                      )}
                    >
                      {sample.tier_required}
                    </Badge>
                  </div>

                  <CardTitle className="text-base">{sample.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {sample.description}
                  </p>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {/* File Info */}
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <HardDrive className="w-3 h-3" />
                        {sample.size}
                      </span>
                      <span className="font-mono">{sample.filename}</span>
                    </div>

                    {/* Highlights */}
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-muted-foreground">
                        Key Features:
                      </p>
                      <div className="space-y-1">
                        {sample.highlights.slice(0, 3).map((highlight, i) => {
                          const HighlightIcon = getHighlightIcon(highlight);
                          return (
                            <div
                              key={i}
                              className="flex items-center gap-2 text-xs"
                            >
                              <HighlightIcon className="w-3 h-3 text-primary" />
                              <span>{highlight}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Action Button */}
                    <Button
                      onClick={() => handleSampleSelect(sample)}
                      disabled={!canAccess || isProcessing}
                      className="w-full mt-4"
                      size="sm"
                    >
                      {isProcessing ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : !canAccess ? (
                        <>
                          <Badge className="mr-2">{sample.tier_required}</Badge>
                          Upgrade Required
                        </>
                      ) : (
                        <>
                          <Zap className="w-4 h-4 mr-2" />
                          Analyze Sample
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Tier Upgrade Prompt */}
      {samples.some(s => !canAccessSample(s.tier_required)) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center p-4 bg-muted/50 rounded-lg border border-dashed"
        >
          <p className="text-sm text-muted-foreground mb-2">
            Some samples require higher tier access
          </p>
          <Button variant="outline" size="sm">
            View Pricing Plans
          </Button>
        </motion.div>
      )}
    </div>
  );
}
