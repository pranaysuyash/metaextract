import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  Clock,
  RefreshCw,
  X,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ChallengeData, ChallengeResponse } from './types';
import { DelayChallenge } from './DelayChallenge';
import { CaptchaChallenge } from './CaptchaChallenge';
import { BehavioralChallenge } from './BehavioralChallenge';

interface ChallengeUIProps {
  challenge: ChallengeData;
  retryAfter: number;
  fileName?: string;
  onComplete: (response: ChallengeResponse) => void;
  onCancel: () => void;
}

const challengeIcons: Record<ChallengeData['type'], React.ReactNode> = {
  behavioral: <RefreshCw className="w-6 h-6" data-testid="refresh-icon" />,
  captcha: <Shield className="w-6 h-6" data-testid="shield-icon" />,
  device_verification: <Shield className="w-6 h-6" data-testid="shield-icon" />,
  standard: <AlertTriangle className="w-6 h-6" data-testid="alert-icon" />,
  delay: <Clock className="w-6 h-6" data-testid="clock-icon" />,
};

const challengeTitles: Record<ChallengeData['type'], string> = {
  behavioral: 'Behavioral Verification',
  captcha: 'CAPTCHA Verification',
  device_verification: 'Device Verification',
  standard: 'Security Check',
  delay: 'Security Verification',
};

export function ChallengeUI({
  challenge,
  retryAfter,
  fileName,
  onComplete,
  onCancel,
}: ChallengeUIProps) {
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChallengeComplete = useCallback(
    async (challengeResponse: ChallengeResponse) => {
      setIsVerifying(true);
      setError(null);

      try {
        const response = await fetch(
          '/api/enhanced-protection/verify-challenge',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              challengeResponse,
              sessionId: challenge.data.sessionId,
              incidentId: challenge.incidentId,
            }),
          }
        );

        const result = await response.json();

        if (result.success) {
          onComplete({
            success: true,
            message: result.message,
            incidentId: result.incidentId,
          });
        } else {
          setError(result.error || 'Verification failed. Please try again.');
        }
      } catch (err) {
        setError('Network error. Please check your connection and try again.');
      } finally {
        setIsVerifying(false);
      }
    },
    [challenge, onComplete]
  );

  const renderChallengeComponent = () => {
    switch (challenge.type) {
      case 'delay':
        return (
          <DelayChallenge
            challenge={challenge}
            retryAfter={retryAfter}
            onComplete={handleChallengeComplete}
            onCancel={onCancel}
          />
        );
      case 'captcha':
        return (
          <CaptchaChallenge
            challenge={challenge}
            onComplete={handleChallengeComplete}
            onCancel={onCancel}
          />
        );
      case 'behavioral':
        return (
          <BehavioralChallenge
            challenge={challenge}
            onComplete={handleChallengeComplete}
            onCancel={onCancel}
          />
        );
      default:
        return (
          <StandardChallenge
            challenge={challenge}
            onComplete={handleChallengeComplete}
            onCancel={onCancel}
          />
        );
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-black/40 backdrop-blur-md rounded-xl border border-amber-500/30 shadow-2xl overflow-hidden"
      >
        <div className="p-6 border-b border-amber-500/20">
          <div className="flex items-center gap-4">
            <div
              className={cn(
                'p-3 rounded-lg',
                challenge.type === 'captcha'
                  ? 'bg-blue-500/10 text-blue-500'
                  : challenge.type === 'delay'
                    ? 'bg-amber-500/10 text-amber-500'
                    : challenge.type === 'behavioral'
                      ? 'bg-purple-500/10 text-purple-500'
                      : 'bg-amber-500/10 text-amber-500'
              )}
            >
              {challengeIcons[challenge.type]}
            </div>
            <div className="flex-1">
              <h3 className="font-mono font-bold text-white">
                {challengeTitles[challenge.type]}
              </h3>
              <p className="text-sm text-slate-400">
                Security verification required
              </p>
            </div>
            <button
              onClick={onCancel}
              className="p-2 text-slate-500 hover:text-white transition-colors"
              aria-label="Cancel verification"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="mb-6 p-4 bg-white/5 rounded-lg border border-white/10">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-slate-300 mb-2">
                  {challenge.instructions ||
                    'Please complete the security verification below to continue.'}
                </p>
                {challenge.reasons.length > 0 && (
                  <div className="text-xs text-slate-500">
                    <span className="font-medium text-slate-400">Reason: </span>
                    {challenge.reasons[0]}
                  </div>
                )}
              </div>
            </div>
          </div>

          {fileName && (
            <div className="mb-4 p-3 bg-white/5 rounded-lg border border-white/10">
              <div className="text-xs text-slate-300 font-mono">
                <span className="text-slate-500">FILE:</span> {fileName}
              </div>
            </div>
          )}

          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg"
              >
                <p className="text-sm text-red-400">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {renderChallengeComponent()}

          {isVerifying && (
            <div className="mt-4 flex items-center justify-center gap-2 text-sm text-slate-400">
              <RefreshCw className="w-4 h-4 animate-spin" />
              Verifying your response...
            </div>
          )}
        </div>

        <div className="px-6 py-3 bg-white/5 border-t border-white/10">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Incident ID: {challenge.incidentId.slice(0, 8)}...</span>
            <span>Retry after: {retryAfter}s</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

interface StandardChallengeProps {
  challenge: ChallengeData;
  onComplete: (response: ChallengeResponse) => void;
  onCancel: () => void;
}

function StandardChallenge({
  challenge,
  onComplete,
  onCancel,
}: StandardChallengeProps) {
  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-300">
        Please confirm you are not a bot by clicking the button below.
      </p>
      <div className="flex gap-3">
        <Button
          onClick={() => onComplete({ success: true, completed: true })}
          className="flex-1 bg-primary hover:bg-primary/90 text-black font-bold"
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          Confirm Human
        </Button>
        <Button
          onClick={onCancel}
          variant="outline"
          className="flex-1 border-white/20 text-white hover:bg-white/10"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
}
