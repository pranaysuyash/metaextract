import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Eye,
  Camera,
  Zap,
  Palette,
  Settings,
  Star,
  Info,
  TrendingUp,
  AlertTriangle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface CullingScore {
  focus_score: number;
  exposure_score: number;
  composition_score: number;
  technical_score: number;
  aesthetic_score: number;
  overall_score: number;
  confidence: number;
}

interface ScoreDetailProps {
  title: string;
  score: number;
  icon: React.ReactNode;
  description: string;
  color?: string;
  onClick?: () => void;
}

interface PhotoScoreVisualizationProps {
  scores: CullingScore;
  recommendations: string[];
  onScoreClick?: (category: string) => void;
  className?: string;
  compact?: boolean;
  showDetails?: boolean;
}

interface ScoreBreakdownProps {
  scores: CullingScore;
  onCategoryClick?: (category: string) => void;
}

interface ScoreComparisonProps {
  before: CullingScore;
  after: CullingScore;
  improvements: string[];
}

interface ScoreMiniCardProps {
  score: CullingScore;
  filename?: string;
  onClick?: () => void;
  isSelected?: boolean;
  isBestShot?: boolean;
}

export function PhotoScoreVisualization({
  scores,
  recommendations,
  onScoreClick,
  className,
  compact = false,
  showDetails = true,
}: PhotoScoreVisualizationProps) {
  const [activeTab, setActiveTab] = useState<
    'overview' | 'breakdown' | 'recommendations'
  >('overview');

  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const scoreProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getScoreIcon = (category: string) => {
    const icons = {
      focus: <Eye className="w-4 h-4" />,
      exposure: <Zap className="w-4 h-4" />,
      composition: <Camera className="w-4 h-4" />,
      technical: <Settings className="w-4 h-4" />,
      aesthetic: <Palette className="w-4 h-4" />,
    };
    return (
      icons[category as keyof typeof icons] || <Star className="w-4 h-4" />
    );
  };

  const getScoreLabel = (category: string) => {
    const labels = {
      focus: 'Focus Quality',
      exposure: 'Exposure Quality',
      composition: 'Composition',
      technical: 'Technical Quality',
      aesthetic: 'Aesthetic Quality',
    };
    return labels[category as keyof typeof labels] || category;
  };

  const scoreCategories = useMemo(
    () => [
      {
        key: 'focus_score',
        label: 'Focus',
        icon: <Eye className="w-4 h-4" />,
        description: 'Sharpness, AF accuracy, eye focus',
        score: scores.focus_score,
      },
      {
        key: 'exposure_score',
        label: 'Exposure',
        icon: <Zap className="w-4 h-4" />,
        description: 'Proper exposure, highlight/shadow balance',
        score: scores.exposure_score,
      },
      {
        key: 'composition_score',
        label: 'Composition',
        icon: <Camera className="w-4 h-4" />,
        description: 'Framing, subject placement, balance',
        score: scores.composition_score,
      },
      {
        key: 'technical_score',
        label: 'Technical',
        icon: <Settings className="w-4 h-4" />,
        description: 'Resolution, lens quality, camera settings',
        score: scores.technical_score,
      },
      {
        key: 'aesthetic_score',
        label: 'Aesthetic',
        icon: <Palette className="w-4 h-4" />,
        description: 'Artistic merit, visual appeal',
        score: scores.aesthetic_score,
      },
    ],
    [scores]
  );

  if (compact) {
    return (
      <Card className={cn('p-4', className)}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Star className={cn('w-5 h-5', scoreColor(scores.overall_score))} />
            <span className="font-bold text-lg">
              {scores.overall_score.toFixed(0)}
            </span>
          </div>
          <Badge variant="outline" className="text-xs">
            {scores.confidence.toFixed(0)}% confidence
          </Badge>
        </div>
        <div className="space-y-1">
          {scoreCategories.slice(0, 3).map(category => (
            <div
              key={category.key}
              className="flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-1">
                {category.icon}
                <span>{category.label}</span>
              </div>
              <span className={cn('font-medium', scoreColor(category.score))}>
                {category.score.toFixed(0)}
              </span>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Star className="w-5 h-5" />
            Photo Quality Score
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge
              variant={
                scores.overall_score >= 80
                  ? 'default'
                  : scores.overall_score >= 60
                    ? 'secondary'
                    : 'destructive'
              }
            >
              {scores.overall_score >= 80
                ? 'Excellent'
                : scores.overall_score >= 60
                  ? 'Good'
                  : 'Needs Improvement'}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {scores.confidence.toFixed(0)}% confidence
            </Badge>
          </div>
        </div>

        {/* Overall Score Display */}
        <div className="flex items-center gap-4 pt-2">
          <div className="text-center">
            <div
              className={cn(
                'text-3xl font-bold',
                scoreColor(scores.overall_score)
              )}
            >
              {scores.overall_score.toFixed(0)}
            </div>
            <div className="text-sm text-gray-600">Overall Score</div>
          </div>
          <div className="flex-1">
            <Progress
              value={scores.overall_score}
              className="h-3"
              style={{
                backgroundColor: '#e5e7eb',
                backgroundImage: `linear-gradient(to right, ${scoreProgressColor(scores.overall_score).replace('bg-', '#')} ${scores.overall_score}%, transparent ${scores.overall_score}%)`,
              }}
            />
          </div>
        </div>
      </CardHeader>

      {showDetails && (
        <CardContent>
          {/* Tabs */}
          <div className="flex gap-2 mb-4 border-b">
            {['overview', 'breakdown', 'recommendations'].map(tab => (
              <Button
                key={tab}
                variant="ghost"
                size="sm"
                className={cn(
                  'capitalize',
                  activeTab === tab && 'border-b-2 border-blue-500'
                )}
                onClick={() => setActiveTab(tab as any)}
              >
                {tab}
              </Button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <ScoreBreakdown scores={scores} onCategoryClick={onScoreClick} />
            </div>
          )}

          {activeTab === 'breakdown' && (
            <div className="space-y-4">
              {scoreCategories.map(category => (
                <ScoreDetail
                  key={category.key}
                  title={category.label}
                  score={category.score}
                  icon={category.icon}
                  description={category.description}
                  onClick={() => onScoreClick?.(category.key)}
                />
              ))}
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <Info className="w-4 h-4" />
                Recommendations
              </h4>
              {recommendations.length > 0 ? (
                <div className="space-y-2">
                  {recommendations.map((recommendation, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-2 p-2 bg-gray-50 rounded"
                    >
                      <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm">{recommendation}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-600">
                  No specific recommendations for this photo.
                </p>
              )}
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}

function ScoreDetail({
  title,
  score,
  icon,
  description,
  onClick,
}: ScoreDetailProps) {
  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const scoreProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div
      className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon}
          <span className="font-medium">{title}</span>
        </div>
        <span className={cn('font-bold', scoreColor(score))}>
          {score.toFixed(0)}
        </span>
      </div>
      <Progress value={score} className="h-2 mb-2" />
      <p className="text-xs text-gray-600">{description}</p>
    </div>
  );
}

function ScoreBreakdown({ scores, onCategoryClick }: ScoreBreakdownProps) {
  const categories = [
    { key: 'focus_score', label: 'Focus', score: scores.focus_score },
    { key: 'exposure_score', label: 'Exposure', score: scores.exposure_score },
    {
      key: 'composition_score',
      label: 'Composition',
      score: scores.composition_score,
    },
    {
      key: 'technical_score',
      label: 'Technical',
      score: scores.technical_score,
    },
    {
      key: 'aesthetic_score',
      label: 'Aesthetic',
      score: scores.aesthetic_score,
    },
  ];

  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="grid grid-cols-2 gap-3">
      {categories.map(category => (
        <div
          key={category.key}
          className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          onClick={() => onCategoryClick?.(category.key)}
        >
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">{category.label}</span>
          </div>
          <span className={cn('text-sm font-bold', scoreColor(category.score))}>
            {category.score.toFixed(0)}
          </span>
        </div>
      ))}
    </div>
  );
}

export function ScoreComparison({
  before,
  after,
  improvements,
}: ScoreComparisonProps) {
  const categories = [
    { key: 'focus_score', label: 'Focus' },
    { key: 'exposure_score', label: 'Exposure' },
    { key: 'composition_score', label: 'Composition' },
    { key: 'technical_score', label: 'Technical' },
    { key: 'aesthetic_score', label: 'Aesthetic' },
    { key: 'overall_score', label: 'Overall' },
  ];

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Score Comparison
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {categories.map(category => {
            const beforeScore = before[
              category.key as keyof CullingScore
            ] as number;
            const afterScore = after[
              category.key as keyof CullingScore
            ] as number;
            const change = afterScore - beforeScore;

            return (
              <div
                key={category.key}
                className="flex items-center justify-between"
              >
                <span className="text-sm font-medium">{category.label}</span>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-600">
                    {beforeScore.toFixed(0)}
                  </span>
                  <span
                    className={cn(
                      'text-sm font-medium',
                      getChangeColor(change)
                    )}
                  >
                    {change >= 0 ? '+' : ''}
                    {change.toFixed(0)}
                  </span>
                  <span className="text-sm font-bold">
                    {afterScore.toFixed(0)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {improvements.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <h4 className="font-medium mb-2">Key Improvements</h4>
            <div className="space-y-1">
              {improvements.map((improvement, index) => (
                <div
                  key={index}
                  className="text-sm text-green-600 flex items-center gap-2"
                >
                  <TrendingUp className="w-3 h-3" />
                  {improvement}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ScoreMiniCard({
  score,
  filename,
  onClick,
  isSelected,
  isBestShot,
}: ScoreMiniCardProps) {
  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:shadow-md',
        isSelected && 'ring-2 ring-blue-500',
        isBestShot && 'ring-2 ring-yellow-500'
      )}
      onClick={onClick}
    >
      <CardContent className="p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1">
            <Star className={cn('w-4 h-4', scoreColor(score.overall_score))} />
            <span className={cn('font-bold', scoreColor(score.overall_score))}>
              {score.overall_score.toFixed(0)}
            </span>
          </div>
          {isBestShot && (
            <Badge
              variant="outline"
              className="text-xs bg-yellow-50 text-yellow-700 border-yellow-200"
            >
              Best
            </Badge>
          )}
        </div>
        {filename && (
          <p className="text-xs text-gray-600 truncate">{filename}</p>
        )}
        <div className="mt-2 space-y-1">
          <div className="flex justify-between text-xs">
            <span>Focus:</span>
            <span className={cn('font-medium', scoreColor(score.focus_score))}>
              {score.focus_score.toFixed(0)}
            </span>
          </div>
          <div className="flex justify-between text-xs">
            <span>Exposure:</span>
            <span
              className={cn('font-medium', scoreColor(score.exposure_score))}
            >
              {score.exposure_score.toFixed(0)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function ScoreGauge({
  value,
  max = 100,
  label,
}: {
  value: number;
  max?: number;
  label?: string;
}) {
  const percentage = (value / max) * 100;
  const rotation = (percentage * 180) / 100 - 90; // Convert to degrees, -90 to 90

  const getColor = (value: number) => {
    if (value >= 80) return '#10b981'; // green-500
    if (value >= 60) return '#f59e0b'; // yellow-500
    return '#ef4444'; // red-500
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-16">
        {/* Gauge background */}
        <svg className="w-full h-full" viewBox="0 0 100 50">
          <path
            d="M 10 40 A 40 40 0 0 1 90 40"
            stroke="#e5e7eb"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
          />
          {/* Gauge value */}
          <path
            d="M 10 40 A 40 40 0 0 1 90 40"
            stroke={getColor(value)}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={`${percentage * 1.57} 157`} // 1.57 is circumference of quarter circle
            transform={`rotate(-90 50 40)`}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div
              className={cn(
                'text-lg font-bold',
                value >= 80
                  ? 'text-green-600'
                  : value >= 60
                    ? 'text-yellow-600'
                    : 'text-red-600'
              )}
            >
              {value.toFixed(0)}
            </div>
          </div>
        </div>
      </div>
      {label && <div className="text-xs text-gray-600 mt-1">{label}</div>}
    </div>
  );
}
