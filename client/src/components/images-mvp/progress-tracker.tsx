import React, { useState, useEffect } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Zap, Clock, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProgressBar } from './progress-bar';

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
  uploadComplete?: boolean;
  fallbackPercentage?: number;
  fallbackStage?: string;
  onConnected?: () => void;
  onProgressUpdate?: (hasUpdate: boolean) => void;
}

export function ProgressTracker({
  sessionId,
  className,
  uploadComplete = false,
  fallbackPercentage,
  fallbackStage,
  onConnected,
  onProgressUpdate,
}: ProgressTrackerProps) {
  const shouldReduceMotion = useReducedMotion();
  const [progress, setProgress] = useState<ProgressData>({
    percentage: 0,
    stage: 'Initializing extraction...',
  });
  const [isComplete, setIsComplete] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [hasProgressUpdate, setHasProgressUpdate] = useState(false);

  useEffect(() => {
    // WebSocket connection for real-time progress updates
    // Uses Vite proxy with ws: true, no need for hardcoded port
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Try Vite proxy first (uses same host), if it closes before connecting try backend directly (port 3000)
    let attemptedFallback = false;
    let ws = new WebSocket(
      `${wsProtocol}//${window.location.host}/api/images_mvp/progress/${sessionId}`
    );

    const setupHandlers = (sock: WebSocket) => {
      sock.onopen = () => {
        console.log('Progress tracker connected');
        setWsConnected(true);
        if (typeof onConnected === 'function') onConnected();
      };

      sock.onmessage = event => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'progress') {
            setHasProgressUpdate(true);
            if (typeof onProgressUpdate === 'function') onProgressUpdate(true);
            setProgress({
              percentage: data.percentage ?? 0,
              stage: data.stage,
              eta: data.estimated_time_remaining,
              quality_metrics: data.quality_metrics,
            });

            // Check if extraction is complete
            if ((data.percentage ?? 0) >= 100) {
              setIsComplete(true);
              setTimeout(() => {
                sock.close();
              }, 1000);
            }
          } else if (data.type === 'complete') {
            setHasProgressUpdate(true);
            if (typeof onProgressUpdate === 'function') onProgressUpdate(true);
            setIsComplete(true);
            setProgress(prev => ({
              ...prev,
              percentage: 100,
              stage: 'Processing complete',
            }));
          } else if (data.type === 'error') {
            setHasProgressUpdate(true);
            if (typeof onProgressUpdate === 'function') onProgressUpdate(true);
            setProgress(prev => ({
              ...prev,
              stage: data.error || 'Extraction failed',
            }));
          }
        } catch (error) {
          console.error('Error parsing progress update:', error);
        }
      };

      sock.onerror = error => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
        if (typeof onProgressUpdate === 'function') onProgressUpdate(false);
      };

      sock.onclose = ev => {
        console.log('Progress tracker disconnected', ev);
        setWsConnected(false);
        if (typeof onProgressUpdate === 'function') onProgressUpdate(false);

        // If the socket closed before opening and we haven't tried fallback, try backend host directly
        if (!attemptedFallback && ev && ev.code === 1006) {
          attemptedFallback = true;
          try {
            const backendHost = `${wsProtocol}//${window.location.hostname}:3000`;
            console.log('Attempting fallback WebSocket to', backendHost);
            ws = new WebSocket(
              `${backendHost}/api/images_mvp/progress/${sessionId}`
            );
            setupHandlers(ws);
          } catch (err) {
            console.error('Fallback WebSocket failed:', err);
          }
        }
      };
    };

    setupHandlers(ws);

    // Cleanup on unmount
    return () => {
      try {
        ws.close();
      } catch (e) {
        // ignore
      }
    };
  }, [sessionId]);

  const getStageIcon = (stage: string) => {
    if (stage.toLowerCase().includes('complete'))
      return <CheckCircle className="w-4 h-4" />;
    if (stage.toLowerCase().includes('analyzing'))
      return <Zap className="w-4 h-4" />;
    return <Clock className="w-4 h-4" />;
  };

  const formatStageLabel = (stage: string) => {
    const normalized = stage.trim().toLowerCase();
    const mapped = {
      extraction_start: 'Starting extraction',
      extraction_complete: 'Finalizing metadata',
      upload_complete: 'Upload complete',
      extraction_starting: 'Starting extraction',
      processing: 'Processing metadata',
      complete: 'Processing complete',
    } as Record<string, string>;
    if (mapped[normalized]) return mapped[normalized];
    return stage.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  };

  const effectivePercentage = hasProgressUpdate
    ? (progress.percentage ?? 0)
    : (fallbackPercentage ?? progress.percentage ?? 0);
  const effectiveStage = hasProgressUpdate
    ? progress.stage
    : (fallbackStage ?? progress.stage);
  const showFinalizing = uploadComplete && !hasProgressUpdate && !isComplete;
  const showConnecting = !wsConnected && !isComplete && !showFinalizing;
  const isUploadPhase = !hasProgressUpdate && !isComplete;
  const headline = isComplete
    ? 'Extraction Complete!'
    : isUploadPhase
      ? 'Uploading image...'
      : 'Extracting Metadata...';
  const displayStage = formatStageLabel(effectiveStage || 'Processing');

  return (
    <div>
      <div
        className={cn(
          'w-full space-y-4 p-4 bg-gradient-to-br from-white/10 via-white/5 to-transparent backdrop-blur-sm rounded-lg border border-white/10 shadow-[0_12px_30px_rgba(0,0,0,0.35)]',
          className
        )}
        role="status"
        aria-live="polite"
      >
        {/* Progress Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <motion.div
              animate={{
                rotate: isComplete ? 0 : shouldReduceMotion ? 0 : 360,
              }}
              transition={{
                duration: 2,
                repeat: isComplete ? 0 : Infinity,
                ease: 'linear',
                repeatType: 'loop',
              }}
              style={{ originX: 0.5, originY: 0.5 }}
            >
              {getStageIcon(displayStage)}
            </motion.div>
            <span className="text-sm font-medium text-slate-200">
              {headline}
            </span>
          </div>
          <span className="text-sm font-mono text-slate-200">
            {effectivePercentage.toFixed(0)}%
          </span>
        </div>

        {/* Progress Bar */}
        <ProgressBar
          percentage={effectivePercentage}
          className="h-2.5"
          tone="emerald"
        />

        {/* Current Stage */}
        <div className="text-center">
          <p className="text-sm text-slate-200 mb-1">{displayStage}</p>
          {progress.eta && progress.eta > 0 && (
            <p className="text-xs text-slate-300">
              Estimated time remaining: {Math.ceil(progress.eta / 1000)}s
            </p>
          )}
        </div>

        {/* Quality Metrics */}
        {progress.quality_metrics && (
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-white/10">
            <div className="text-center">
              <div className="text-xs text-slate-200 mb-1">Confidence</div>
              <div className="text-lg font-bold text-green-400">
                {(progress.quality_metrics.confidence_score * 100).toFixed(0)}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-slate-200 mb-1">Completeness</div>
              <div className="text-lg font-bold text-blue-400">
                {(
                  progress.quality_metrics.extraction_completeness * 100
                ).toFixed(0)}
                %
              </div>
            </div>
          </div>
        )}

        {/* Connection Status */}
        {showFinalizing && (
          <div className="flex items-center justify-center space-x-2 text-blue-300 text-xs">
            <div className="w-2 h-2 bg-blue-300 rounded-full animate-pulse" />
            <span>Finalizing upload...</span>
          </div>
        )}

        {showConnecting && (
          <div className="flex items-center justify-center space-x-2 text-yellow-400 text-xs">
            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
            <span>Preparing live updates...</span>
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
    </div>
  );
}
