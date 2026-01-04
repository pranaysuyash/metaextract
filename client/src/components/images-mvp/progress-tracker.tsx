import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Zap, Clock, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ProgressData {
  percentage: number;
  stage: string;
  eta?: number;
  quality_metrics?: {
    confidence_score: number;
    extraction_completeness: number;
  };
}

interface ProgressTrackerProps {
  sessionId: string;
  className?: string;
}

export function ProgressTracker({ sessionId, className }: ProgressTrackerProps) {
  const [progress, setProgress] = useState<ProgressData>({
    percentage: 0,
    stage: 'Initializing extraction...'
  });
  const [isComplete, setIsComplete] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    // WebSocket connection for real-time progress updates
    const ws = new WebSocket(`ws://${window.location.host}/api/images_mvp/progress/${sessionId}`);
    
    ws.onopen = () => {
      console.log('Progress tracker connected');
      setWsConnected(true);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'progress') {
          setProgress({
            percentage: data.percentage,
            stage: data.stage,
            eta: data.estimated_time_remaining,
            quality_metrics: data.quality_metrics
          });
          
          // Check if extraction is complete
          if (data.percentage >= 100) {
            setIsComplete(true);
            setTimeout(() => {
              ws.close();
            }, 1000);
          }
        }
      } catch (error) {
        console.error('Error parsing progress update:', error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsConnected(false);
    };
    
    ws.onclose = () => {
      console.log('Progress tracker disconnected');
      setWsConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, [sessionId]);

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  const getStageIcon = (stage: string) => {
    if (stage.toLowerCase().includes('complete')) return <CheckCircle className="w-4 h-4" />;
    if (stage.toLowerCase().includes('analyzing')) return <Zap className="w-4 h-4" />;
    return <Clock className="w-4 h-4" />;
  };

  return (
    <div className={cn("w-full space-y-4 p-4 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10", className)}>
      {/* Progress Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <motion.div
            animate={{ rotate: isComplete ? 0 : 360 }}
            transition={{ duration: 2, repeat: isComplete ? 0 : Infinity, ease: "linear" }}
          >
            {getStageIcon(progress.stage)}
          </motion.div>
          <span className="text-sm font-medium text-white/80">
            {isComplete ? 'Extraction Complete!' : 'Extracting Metadata...'}
          </span>
        </div>
        <span className="text-sm font-mono text-white/60">
          {progress.percentage.toFixed(0)}%
        </span>
      </div>

      {/* Progress Bar */}
      <div className="relative w-full h-2 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          className={`absolute left-0 top-0 h-full ${getProgressColor(progress.percentage)}`}
          initial={{ width: 0 }}
          animate={{ width: `${progress.percentage}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
        {progress.percentage > 0 && progress.percentage < 100 && (
          <motion.div
            className="absolute right-0 top-0 h-full w-1 bg-white/40"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
      </div>

      {/* Current Stage */}
      <div className="text-center">
        <p className="text-sm text-white/70 mb-1">{progress.stage}</p>
        {progress.eta && progress.eta > 0 && (
          <p className="text-xs text-white/50">
            Estimated time remaining: {Math.ceil(progress.eta / 1000)}s
          </p>
        )}
      </div>

      {/* Quality Metrics */}
      {progress.quality_metrics && (
        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-white/10">
          <div className="text-center">
            <div className="text-xs text-white/50 mb-1">Confidence</div>
            <div className="text-lg font-bold text-green-400">
              {(progress.quality_metrics.confidence_score * 100).toFixed(0)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-white/50 mb-1">Completeness</div>
            <div className="text-lg font-bold text-blue-400">
              {(progress.quality_metrics.extraction_completeness * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      )}

      {/* Connection Status */}
      {!wsConnected && !isComplete && (
        <div className="flex items-center justify-center space-x-2 text-yellow-400 text-xs">
          <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
          <span>Connecting to progress tracker...</span>
        </div>
      )}

      {/* Completion Animation */}
      {isComplete && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="flex items-center justify-center space-x-2 text-green-400"
        >
          <CheckCircle className="w-5 h-5" />
          <span className="text-sm font-medium">Ready to view results!</span>
        </motion.div>
      )}
    </div>
  );
}