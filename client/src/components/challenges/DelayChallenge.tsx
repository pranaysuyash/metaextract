import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ChallengeData, ChallengeResponse } from './types';

interface DelayChallengeProps {
  challenge: ChallengeData;
  retryAfter: number;
  onComplete: (response: ChallengeResponse) => void;
  onCancel: () => void;
}

export function DelayChallenge({
  challenge,
  retryAfter,
  onComplete,
  onCancel,
}: DelayChallengeProps) {
  const [timeRemaining, setTimeRemaining] = useState(retryAfter);
  const [isWaiting, setIsWaiting] = useState(true);

  useEffect(() => {
    if (!isWaiting) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isWaiting]);

  const handleContinue = () => {
    onComplete({
      success: true,
      completed: true,
      type: 'delay',
    });
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins > 0) {
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    return `0:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-amber-500/10 mb-4">
          <Clock className="w-10 h-10 text-amber-500" />
        </div>
        <p className="text-sm text-slate-300 mb-2">
          Please wait while we verify your request
        </p>
        <div className="text-3xl font-mono font-bold text-white">
          {formatTime(timeRemaining)}
        </div>
      </div>

      <div className="relative">
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-amber-500"
            initial={{ width: '100%' }}
            animate={{ width: `${(timeRemaining / retryAfter) * 100}%` }}
            transition={{ ease: 'linear', duration: 1 }}
          />
        </div>
      </div>

      {timeRemaining === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-center gap-2 text-green-400 mb-4">
            <CheckCircle className="w-5 h-5" />
            <span className="text-sm">Verification complete</span>
          </div>
          <Button
            onClick={handleContinue}
            className="w-full bg-primary hover:bg-primary/90 text-black font-bold"
          >
            Continue to Upload
          </Button>
        </motion.div>
      ) : (
        <Button
          onClick={onCancel}
          variant="outline"
          className="w-full border-white/20 text-white hover:bg-white/10"
        >
          Cancel
        </Button>
      )}
    </div>
  );
}
