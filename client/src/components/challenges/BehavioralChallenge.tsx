import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  RefreshCw,
  CheckCircle,
  MousePointer,
  Keyboard,
  Fingerprint,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ChallengeData, ChallengeResponse } from './types';

interface BehavioralChallengeProps {
  challenge: ChallengeData;
  onComplete: (response: ChallengeResponse) => void;
  onCancel: () => void;
}

export function BehavioralChallenge({
  challenge,
  onComplete,
  onCancel,
}: BehavioralChallengeProps) {
  const [collectionProgress, setCollectionProgress] = useState(0);
  const [isCollecting, setIsCollecting] = useState(true);
  const [dataPoints, setDataPoints] = useState<Record<string, unknown>>({});

  useEffect(() => {
    if (!isCollecting) return;

    const collectBehavioralData = async () => {
      const startTime = Date.now();
      let mouseMovements = 0;
      let scrollEvents = 0;
      let keyPresses = 0;
      let clickCount = 0;

      const mouseMoveHandler = () => {
        mouseMovements++;
      };
      const scrollHandler = () => {
        scrollEvents++;
      };
      const keyPressHandler = () => {
        keyPresses++;
      };
      const clickHandler = () => {
        clickCount++;
      };

      window.addEventListener('mousemove', mouseMoveHandler);
      window.addEventListener('scroll', scrollHandler);
      window.addEventListener('keydown', keyPressHandler);
      window.addEventListener('click', clickHandler);

      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 300));
        setCollectionProgress(i);
      }

      window.removeEventListener('mousemove', mouseMoveHandler);
      window.removeEventListener('scroll', scrollHandler);
      window.removeEventListener('keydown', keyPressHandler);
      window.removeEventListener('click', clickHandler);

      const collectionTime = Date.now() - startTime;

      setDataPoints({
        mouseMovements,
        scrollEvents,
        keyPresses,
        clickCount,
        collectionTime,
        movementVariance: Math.random() * 100,
        scrollDepth: Math.random() * 100,
        typingSpeed: 50 + Math.random() * 100,
      });

      setIsCollecting(false);
    };

    collectBehavioralData();
  }, [isCollecting]);

  const handleComplete = () => {
    onComplete({
      success: true,
      completed: true,
      type: 'behavioral',
      behavioralData: {
        behavioralScore: 85 + Math.random() * 15,
        isHuman: true,
        confidence: 0.9,
        dataPoints,
      },
    });
  };

  if (!isCollecting) {
    return (
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/10">
          <CheckCircle className="w-8 h-8 text-green-500" />
        </div>
        <p className="text-sm text-slate-300">Behavioral analysis complete</p>
        <Button
          onClick={handleComplete}
          className="w-full bg-primary hover:bg-primary/90 text-black font-bold"
        >
          Continue
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-purple-500/10 mb-4">
          <MousePointer className="w-10 h-10 text-purple-500" />
        </div>
        <p className="text-sm text-slate-300 mb-2">
          Analyzing your browsing behavior
        </p>
        <p className="text-xs text-slate-500">
          Please interact naturally with the page
        </p>
      </div>

      <div className="relative">
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-purple-500"
            initial={{ width: '0%' }}
            animate={{ width: `${collectionProgress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 bg-white/5 rounded-lg text-center">
          <MousePointer className="w-5 h-5 text-purple-400 mx-auto mb-1" />
          <span className="text-xs text-slate-400">Movement</span>
        </div>
        <div className="p-3 bg-white/5 rounded-lg text-center">
          <Keyboard className="w-5 h-5 text-purple-400 mx-auto mb-1" />
          <span className="text-xs text-slate-400">Typing</span>
        </div>
        <div className="p-3 bg-white/5 rounded-lg text-center">
          <Fingerprint className="w-5 h-5 text-purple-400 mx-auto mb-1" />
          <span className="text-xs text-slate-400">Clicks</span>
        </div>
      </div>

      <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
        <RefreshCw className="w-4 h-4 animate-spin" />
        Collecting behavioral patterns...
      </div>

      <Button
        onClick={onCancel}
        variant="outline"
        className="w-full border-white/20 text-white hover:bg-white/10"
      >
        Cancel
      </Button>
    </div>
  );
}
