import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import {
  Zap,
  Clock,
  CheckCircle,
  Wifi,
  WifiOff,
  AlertTriangle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ProgressBar } from './progress-bar';
import websocketManager, {
  type WebSocketMessage,
  type ConnectionMetrics,
} from '@/lib/websocket-manager';

interface ProgressData {
  percentage: number;
  stage: string;
  eta?: number;
  quality_metrics?: {
    confidence_score: number;
    extraction_completeness: number;
  };
}

interface ProgressTrackerEnhancedProps {
  sessionId: string;
  className?: string;
  uploadComplete?: boolean;
  fallbackPercentage?: number;
  fallbackStage?: string;
  onConnected?: () => void;
  onProgressUpdate?: (hasUpdate: boolean) => void;
  onError?: (error: string) => void;
}

export function ProgressTrackerEnhanced({
  sessionId,
  className,
  uploadComplete = false,
  fallbackPercentage,
  fallbackStage,
  onConnected,
  onProgressUpdate,
  onError,
}: ProgressTrackerEnhancedProps) {
  const shouldReduceMotion = useReducedMotion();
  const [progress, setProgress] = useState<ProgressData>({
    percentage: 0,
    stage: 'Initializing extraction...',
  });
  const [isComplete, setIsComplete] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [hasProgressUpdate, setHasProgressUpdate] = useState(false);
  const [connectionMetrics, setConnectionMetrics] =
    useState<ConnectionMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [showFallback, setShowFallback] = useState(false);

  const connectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const fallbackTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const cleanup = useCallback(() => {
    if (connectionTimeoutRef.current) {
      clearTimeout(connectionTimeoutRef.current);
    }
    if (fallbackTimeoutRef.current) {
      clearTimeout(fallbackTimeoutRef.current);
    }
    websocketManager.disconnect();
  }, []);

  const handleWebSocketMessage = useCallback(
    (message: WebSocketMessage) => {
      setConnectionMetrics(websocketManager.getMetrics());

      switch (message.type) {
        case 'connected':
          setIsConnected(true);
          setError(null);
          setReconnectAttempts(0);
          if (typeof onConnected === 'function') {
            onConnected();
          }
          break;

        case 'progress':
          setHasProgressUpdate(true);
          if (typeof onProgressUpdate === 'function') {
            onProgressUpdate(true);
          }
          setProgress({
            percentage: message.percentage ?? 0,
            stage: message.stage,
            eta: message.estimated_time_remaining,
            quality_metrics: message.quality_metrics,
          });

          // Check if extraction is complete
          if ((message.percentage ?? 0) >= 100) {
            setIsComplete(true);
            // Give time for completion animation before disconnecting
            setTimeout(() => {
              cleanup();
            }, 2000);
          }
          break;

        case 'complete':
          setHasProgressUpdate(true);
          if (typeof onProgressUpdate === 'function') {
            onProgressUpdate(true);
          }
          setIsComplete(true);
          setProgress(prev => ({
            ...prev,
            percentage: 100,
            stage: 'Processing complete',
          }));
          // Give time for completion animation before disconnecting
          setTimeout(() => {
            cleanup();
          }, 2000);
          break;

        case 'error': {
          setHasProgressUpdate(true);
          if (typeof onProgressUpdate === 'function') {
            onProgressUpdate(true);
          }
          const errorMessage = message.error || 'Extraction failed';
          setError(errorMessage);
          if (typeof onError === 'function') {
            onError(errorMessage);
          }
          setProgress(prev => ({
            ...prev,
            stage: errorMessage,
          }));
          break;
        }

        case 'heartbeat':
          // Keep connection alive indicator
          break;
      }
    },
    [onConnected, onProgressUpdate, onError, cleanup]
  );

  const handleConnection = useCallback(() => {
    console.log('[ProgressTracker] WebSocket connected');
    setIsConnected(true);
    setError(null);
  }, []);

  const handleDisconnection = useCallback(() => {
    console.log('[ProgressTracker] WebSocket disconnected');
    setIsConnected(false);

    // Update reconnect attempts from manager
    const metrics = websocketManager.getMetrics();
    setReconnectAttempts(metrics.reconnectAttempts);
  }, []);

  const handleError = useCallback(
    (error: Event) => {
      console.error('[ProgressTracker] WebSocket error:', error);
      const errorMessage = 'Connection error occurred';
      setError(errorMessage);
      if (typeof onError === 'function') {
        onError(errorMessage);
      }
      setIsConnected(false);
    },
    [onError]
  );

  useEffect(() => {
    if (!sessionId) return;

    // Reset state for new session
    setProgress({ percentage: 0, stage: 'Initializing extraction...' });
    setIsComplete(false);
    setIsConnected(false);
    setHasProgressUpdate(false);
    setError(null);
    setReconnectAttempts(0);
    setShowFallback(false);

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/api/images_mvp/progress/${sessionId}`;

    let messageHandlerId: string;
    let connectHandlerId: string;
    let disconnectHandlerId: string;
    let errorHandlerId: string;

    const connectWebSocket = async () => {
      try {
        // Set fallback timeout - if no real progress after 15 seconds, show fallback
        fallbackTimeoutRef.current = setTimeout(() => {
          if (!hasProgressUpdate && !isComplete) {
            console.log('[ProgressTracker] Showing fallback progress');
            setShowFallback(true);
          }
        }, 15000);

        // Set connection timeout - if not connected after 10 seconds, show error
        connectionTimeoutRef.current = setTimeout(() => {
          if (!isConnected) {
            const timeoutError =
              'Connection timeout - please refresh and try again';
            setError(timeoutError);
            if (typeof onError === 'function') {
              onError(timeoutError);
            }
          }
        }, 10000);

        // Register handlers
        messageHandlerId = websocketManager.onMessage(handleWebSocketMessage);
        connectHandlerId = websocketManager.onConnect(handleConnection);
        disconnectHandlerId =
          websocketManager.onDisconnect(handleDisconnection);
        errorHandlerId = websocketManager.onError(handleError);

        // Connect
        await websocketManager.connect(wsUrl, sessionId);
      } catch (error) {
        console.error('[ProgressTracker] Failed to connect:', error);
        const connectionError = 'Failed to establish connection';
        setError(connectionError);
        if (typeof onError === 'function') {
          onError(connectionError);
        }
      }
    };

    connectWebSocket();

    // Cleanup function
    return () => {
      if (connectionTimeoutRef.current) {
        clearTimeout(connectionTimeoutRef.current);
      }
      if (fallbackTimeoutRef.current) {
        clearTimeout(fallbackTimeoutRef.current);
      }

      // Remove handlers
      if (messageHandlerId) websocketManager.removeHandler(messageHandlerId);
      if (connectHandlerId) websocketManager.removeHandler(connectHandlerId);
      if (disconnectHandlerId)
        websocketManager.removeHandler(disconnectHandlerId);
      if (errorHandlerId) websocketManager.removeHandler(errorHandlerId);

      // Disconnect
      websocketManager.disconnect();
    };
  }, [
    sessionId,
    handleWebSocketMessage,
    handleConnection,
    handleDisconnection,
    handleError,
    onError,
  ]);

  const getStageIcon = useCallback((stage: string) => {
    if (stage.toLowerCase().includes('complete'))
      return <CheckCircle className="w-4 h-4" />;
    if (stage.toLowerCase().includes('analyzing'))
      return <Zap className="w-4 h-4" />;
    return <Clock className="w-4 h-4" />;
  }, []);

  const formatStageLabel = useCallback((stage: string) => {
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
  }, []);

  const effectivePercentage = hasProgressUpdate
    ? (progress.percentage ?? 0)
    : showFallback
      ? (fallbackPercentage ?? progress.percentage ?? 0)
      : (progress.percentage ?? 0);

  const effectiveStage = hasProgressUpdate
    ? progress.stage
    : showFallback
      ? (fallbackStage ?? progress.stage)
      : progress.stage;

  const showFinalizing =
    uploadComplete && !hasProgressUpdate && !isComplete && !showFallback;
  const showConnecting =
    !isConnected && !isComplete && !showFinalizing && !showFallback && !error;
  const showError = !!error && !isComplete;

  const headline = isComplete
    ? 'Extraction Complete!'
    : showError
      ? 'Connection Error'
      : isConnected
        ? 'Extracting Metadata...'
        : showConnecting
          ? 'Preparing connection...'
          : 'Uploading image...';

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
              {showError ? (
                <AlertTriangle className="w-4 h-4 text-red-400" />
              ) : (
                getStageIcon(displayStage)
              )}
            </motion.div>
            <span className="text-sm font-medium text-slate-200">
              {headline}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <Wifi className="w-4 h-4 text-green-400" />
            ) : (
              <WifiOff className="w-4 h-4 text-yellow-400" />
            )}
            <span className="text-sm font-mono text-slate-200">
              {effectivePercentage.toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <ProgressBar
          percentage={effectivePercentage}
          className="h-2.5"
          tone={showError ? 'amber' : 'emerald'}
        />

        {/* Current Stage */}
        <div className="text-center">
          <p className="text-sm text-slate-200 mb-1">{displayStage}</p>
          {progress.eta && progress.eta > 0 && (
            <p className="text-xs text-slate-300">
              Estimated time remaining: {Math.ceil(progress.eta / 1000)}s
            </p>
          )}
          {showError && (
            <p className="text-xs text-red-400 mt-1">
              {error}{' '}
              {reconnectAttempts > 0 &&
                `(reconnecting... attempt ${reconnectAttempts})`}
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

        {showFallback && !hasProgressUpdate && (
          <div className="flex items-center justify-center space-x-2 text-blue-300 text-xs">
            <div className="w-2 h-2 bg-blue-300 rounded-full animate-pulse" />
            <span>Processing... (fallback mode)</span>
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

        {/* Connection Metrics (Debug Info) */}
        {connectionMetrics && process.env.NODE_ENV === 'development' && (
          <div className="pt-3 border-t border-white/10 text-xs text-slate-400">
            <div className="flex justify-between">
              <span>Connection ID:</span>
              <span className="font-mono">
                {connectionMetrics.connectionId.slice(-8)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Messages:</span>
              <span>{connectionMetrics.messagesReceived}</span>
            </div>
            <div className="flex justify-between">
              <span>Reconnects:</span>
              <span>{connectionMetrics.reconnectAttempts}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
