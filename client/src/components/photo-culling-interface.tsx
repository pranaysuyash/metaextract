import React, { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Star,
  Camera,
  Eye,
  Zap,
  CheckCircle,
  XCircle,
  AlertCircle,
  Filter,
  Download,
  Share,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types for AI culling system
interface CullingScore {
  focus_score: number;
  exposure_score: number;
  composition_score: number;
  technical_score: number;
  aesthetic_score: number;
  overall_score: number;
  confidence: number;
}

interface PhotoMetadata {
  filename: string;
  filepath: string;
  width: number;
  height: number;
  exif?: Record<string, any>;
  image_quality_analysis?: {
    quality_factors?: {
      focus?: number;
      exposure?: number;
    };
  };
}

interface PhotoGroup {
  group_id: string;
  photos: PhotoMetadata[];
  similarity_reason: string;
  best_shot_index: number | null;
  culling_scores: CullingScore[];
}

interface AICullingRecommendation {
  type: 'single_photo' | 'group_best' | 'group_alternative';
  group_id: string;
  photo_index: number;
  action: 'keep' | 'cull' | 'review' | 'consider';
  reason: string;
  score: CullingScore;
}

interface AICullingResults {
  groups: PhotoGroup[];
  total_photos: number;
  recommendations: AICullingRecommendation[];
  processing_time: number;
  success: boolean;
  scoring_weights: {
    focus: number;
    exposure: number;
    composition: number;
    technical: number;
    aesthetic: number;
  };
  error?: string;
}

interface PhotoCullingInterfaceProps {
  photos: PhotoMetadata[];
  onCullingComplete?: (results: AICullingResults) => void;
  onSelectionChange?: (selectedPhotos: string[]) => void;
  className?: string;
}

export function PhotoCullingInterface({
  photos,
  onCullingComplete,
  onSelectionChange,
  className,
}: PhotoCullingInterfaceProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [cullingResults, setCullingResults] = useState<AICullingResults | null>(
    null
  );
  const [selectedPhotos, setSelectedPhotos] = useState<Set<string>>(new Set());
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  // Filter options
  const filterOptions = [
    { id: 'all', label: 'All Photos', count: photos.length },
    {
      id: 'keep',
      label: 'Recommended',
      count:
        cullingResults?.recommendations.filter(r => r.action === 'keep')
          .length || 0,
    },
    {
      id: 'review',
      label: 'Review',
      count:
        cullingResults?.recommendations.filter(r => r.action === 'review')
          .length || 0,
    },
    {
      id: 'cull',
      label: 'Cull',
      count:
        cullingResults?.recommendations.filter(r => r.action === 'cull')
          .length || 0,
    },
  ];

  // Trigger AI culling analysis
  const triggerCullingAnalysis = useCallback(async () => {
    if (photos.length === 0) return;

    setIsProcessing(true);

    try {
      const response = await fetch('/api/ai-culling/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ photos }),
      });

      const results: AICullingResults = await response.json();

      if (results.success) {
        setCullingResults(results);
        onCullingComplete?.(results);

        // Auto-select recommended photos
        const recommendedPhotos = new Set(
          results.recommendations
            .filter(r => r.action === 'keep')
            .map(r => r.group_id + '_' + r.photo_index)
        );
        setSelectedPhotos(recommendedPhotos);
      } else {
        console.error('Culling analysis failed:', results.error);
      }
    } catch (error) {
      console.error('Error during culling analysis:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [photos, onCullingComplete]);

  // Toggle photo selection
  const togglePhotoSelection = useCallback(
    (groupId: string, photoIndex: number) => {
      const photoKey = `${groupId}_${photoIndex}`;
      const newSelection = new Set(selectedPhotos);

      if (newSelection.has(photoKey)) {
        newSelection.delete(photoKey);
      } else {
        newSelection.add(photoKey);
      }

      setSelectedPhotos(newSelection);

      // Notify parent component
      const selectedPhotoPaths = Array.from(newSelection)
        .map(key => {
          const [gId, pIndex] = key.split('_');
          const group = cullingResults?.groups.find(g => g.group_id === gId);
          return group?.photos[parseInt(pIndex)]?.filepath || '';
        })
        .filter(Boolean);

      onSelectionChange?.(selectedPhotoPaths);
    },
    [selectedPhotos, cullingResults, onSelectionChange]
  );

  // Toggle group expansion
  const toggleGroupExpansion = useCallback(
    (groupId: string) => {
      const newExpanded = new Set(expandedGroups);
      if (newExpanded.has(groupId)) {
        newExpanded.delete(groupId);
      } else {
        newExpanded.add(groupId);
      }
      setExpandedGroups(newExpanded);
    },
    [expandedGroups]
  );

  // Get action badge color
  const getActionBadgeColor = (action: string) => {
    switch (action) {
      case 'keep':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cull':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'review':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'consider':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Filter photos based on active filter
  const filteredPhotos = useMemo(() => {
    if (!cullingResults) return [];

    if (activeFilter === 'all') {
      return cullingResults.groups;
    }

    const filteredRecommendations = cullingResults.recommendations.filter(
      r => r.action === activeFilter
    );

    return cullingResults.groups
      .map(group => ({
        ...group,
        culling_scores:
          group.culling_scores?.filter((_, index) =>
            filteredRecommendations.some(
              r => r.group_id === group.group_id && r.photo_index === index
            )
          ) || [],
      }))
      .filter(group => group.culling_scores && group.culling_scores.length > 0);
  }, [cullingResults, activeFilter]);

  // Get recommendation for a photo
  const getRecommendation = (groupId: string, photoIndex: number) => {
    return cullingResults?.recommendations.find(
      r => r.group_id === groupId && r.photo_index === photoIndex
    );
  };

  // Render score breakdown
  const renderScoreBreakdown = (score: CullingScore) => (
    <div className="grid grid-cols-2 gap-2 text-xs">
      <div className="flex justify-between">
        <span>Focus:</span>
        <span className={cn('font-medium', getScoreColor(score.focus_score))}>
          {score.focus_score.toFixed(0)}
        </span>
      </div>
      <div className="flex justify-between">
        <span>Exposure:</span>
        <span
          className={cn('font-medium', getScoreColor(score.exposure_score))}
        >
          {score.exposure_score.toFixed(0)}
        </span>
      </div>
      <div className="flex justify-between">
        <span>Composition:</span>
        <span
          className={cn('font-medium', getScoreColor(score.composition_score))}
        >
          {score.composition_score.toFixed(0)}
        </span>
      </div>
      <div className="flex justify-between">
        <span>Technical:</span>
        <span
          className={cn('font-medium', getScoreColor(score.technical_score))}
        >
          {score.technical_score.toFixed(0)}
        </span>
      </div>
      <div className="flex justify-between">
        <span>Aesthetic:</span>
        <span
          className={cn('font-medium', getScoreColor(score.aesthetic_score))}
        >
          {score.aesthetic_score.toFixed(0)}
        </span>
      </div>
      <div className="flex justify-between">
        <span>Overall:</span>
        <span className={cn('font-bold', getScoreColor(score.overall_score))}>
          {score.overall_score.toFixed(0)}
        </span>
      </div>
    </div>
  );

  // Render photo card
  const renderPhotoCard = (group: PhotoGroup, photoIndex: number) => {
    const photo = group.photos[photoIndex];
    const score = group.culling_scores?.[photoIndex];
    const recommendation = getRecommendation(group.group_id, photoIndex);
    const isSelected = selectedPhotos.has(`${group.group_id}_${photoIndex}`);
    const isBestShot = group.best_shot_index === photoIndex;

    return (
      <Card
        key={photoIndex}
        className={cn(
          'relative cursor-pointer transition-all hover:shadow-md',
          isSelected && 'ring-2 ring-blue-500',
          isBestShot && 'ring-2 ring-green-500'
        )}
        onClick={() => togglePhotoSelection(group.group_id, photoIndex)}
      >
        <CardContent className="p-4">
          <div className="aspect-video bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
            <Camera className="w-8 h-8 text-gray-400" />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium truncate">{photo.filename}</h4>
              {isSelected && <CheckCircle className="w-4 h-4 text-blue-500" />}
              {isBestShot && <Star className="w-4 h-4 text-yellow-500" />}
            </div>

            <div className="flex items-center gap-1">
              <span className="text-xs text-gray-500">
                {photo.width}×{photo.height}
              </span>
              {recommendation && (
                <Badge
                  variant="outline"
                  className={cn(
                    'text-xs',
                    getActionBadgeColor(recommendation.action)
                  )}
                >
                  {recommendation.action}
                </Badge>
              )}
            </div>

            {score && (
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600">Quality</span>
                  <span
                    className={cn(
                      'text-xs font-medium',
                      getScoreColor(score.overall_score)
                    )}
                  >
                    {score.overall_score.toFixed(0)}
                  </span>
                </div>
                <Progress value={score.overall_score} className="h-1" />
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  };

  // Render photo group
  const renderPhotoGroup = (group: PhotoGroup) => {
    const isExpanded = expandedGroups.has(group.group_id);
    const groupRecommendation = getRecommendation(
      group.group_id,
      group.best_shot_index || 0
    );

    return (
      <Card key={group.group_id} className="mb-4">
        <CardHeader
          className="pb-2 cursor-pointer"
          onClick={() => toggleGroupExpansion(group.group_id)}
        >
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">
                {group.similarity_reason === 'time_sequence'
                  ? 'Time Sequence'
                  : 'Similar Photos'}
              </CardTitle>
              <p className="text-sm text-gray-600">
                {group.photos.length} photos • {groupRecommendation?.reason}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{group.photos.length}</Badge>
              <Button variant="ghost" size="sm">
                {isExpanded ? 'Collapse' : 'Expand'}
              </Button>
            </div>
          </div>
        </CardHeader>

        {isExpanded && (
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {group.photos.map((_, photoIndex) =>
                renderPhotoCard(group, photoIndex)
              )}
            </div>
          </CardContent>
        )}
      </Card>
    );
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">AI Photo Culling</h2>
          <p className="text-gray-600">
            Automatically select the best shots based on focus, exposure, and
            composition
          </p>
        </div>
        <Button
          onClick={triggerCullingAnalysis}
          disabled={isProcessing || photos.length === 0}
          className="flex items-center gap-2"
        >
          <Zap className="w-4 h-4" />
          {isProcessing ? 'Analyzing...' : 'Start AI Culling'}
        </Button>
      </div>

      {/* Processing State */}
      {isProcessing && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <div>
                <p className="font-medium">Analyzing photos...</p>
                <p className="text-sm text-gray-600">
                  AI is evaluating focus, exposure, and composition
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {cullingResults && cullingResults.success && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Eye className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="text-2xl font-bold">
                      {cullingResults.total_photos}
                    </p>
                    <p className="text-sm text-gray-600">Total Photos</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-2xl font-bold">
                      {
                        cullingResults.recommendations.filter(
                          r => r.action === 'keep'
                        ).length
                      }
                    </p>
                    <p className="text-sm text-gray-600">Recommended</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-500" />
                  <div>
                    <p className="text-2xl font-bold">
                      {
                        cullingResults.recommendations.filter(
                          r => r.action === 'review'
                        ).length
                      }
                    </p>
                    <p className="text-sm text-gray-600">Review</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <XCircle className="w-5 h-5 text-red-500" />
                  <div>
                    <p className="text-2xl font-bold">
                      {
                        cullingResults.recommendations.filter(
                          r => r.action === 'cull'
                        ).length
                      }
                    </p>
                    <p className="text-sm text-gray-600">Cull</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filter Tabs */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            {filterOptions.map(option => (
              <Button
                key={option.id}
                variant={activeFilter === option.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter(option.id)}
              >
                {option.label} ({option.count})
              </Button>
            ))}
          </div>

          {/* Photo Groups */}
          <div className="space-y-4">
            {filteredPhotos.map(group => renderPhotoGroup(group))}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between border-t pt-4">
            <div className="text-sm text-gray-600">
              {selectedPhotos.size} photos selected
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Export Selection
              </Button>
              <Button>
                <Share className="w-4 h-4 mr-2" />
                Share Results
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {cullingResults && !cullingResults.success && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2 text-red-600">
              <XCircle className="w-5 h-5" />
              <div>
                <p className="font-medium">Analysis Failed</p>
                <p className="text-sm">{cullingResults.error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default PhotoCullingInterface;
