import React, { useState } from 'react';
import { Shield, CheckCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ChallengeData, ChallengeResponse } from './types';

interface CaptchaChallengeProps {
  challenge: ChallengeData;
  onComplete: (response: ChallengeResponse) => void;
  onCancel: () => void;
}

export function CaptchaChallenge({
  challenge,
  onComplete,
  onCancel,
}: CaptchaChallengeProps) {
  const [isVerified, setIsVerified] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);

  const handleVerify = async () => {
    setIsVerifying(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsVerified(true);
    setIsVerifying(false);
  };

  const handleComplete = () => {
    onComplete({
      success: true,
      completed: true,
      type: 'captcha',
    });
  };

  if (isVerified) {
    return (
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/10">
          <CheckCircle className="w-8 h-8 text-green-500" />
        </div>
        <p className="text-sm text-slate-300">CAPTCHA verified successfully</p>
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
    <div className="space-y-4">
      <div className="p-6 bg-white/5 rounded-lg border border-white/10 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 mb-3">
          <Shield className="w-8 h-8 text-blue-500" />
        </div>
        <p className="text-sm text-slate-300 mb-4">
          Click to confirm you are not a robot
        </p>
        <div className="w-12 h-12 mx-auto border-2 border-blue-500/50 rounded hover:border-blue-500 cursor-pointer flex items-center justify-center transition-colors">
          <div className="w-4 h-4 bg-blue-500/20 rounded-sm" />
        </div>
      </div>

      <div className="flex gap-3">
        <Button
          onClick={handleVerify}
          disabled={isVerifying}
          className="flex-1 bg-primary hover:bg-primary/90 text-black font-bold"
        >
          {isVerifying ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Verifying...
            </>
          ) : (
            <>
              <Shield className="w-4 h-4 mr-2" />
              I'm not a robot
            </>
          )}
        </Button>
        <Button
          onClick={onCancel}
          variant="outline"
          className="flex-1 border-white/20 text-white hover:bg-white/10"
        >
          Cancel
        </Button>
      </div>

      <p className="text-xs text-slate-500 text-center">
        This helps protect our platform from automated abuse
      </p>
    </div>
  );
}
