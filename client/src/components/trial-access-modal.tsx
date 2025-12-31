import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import * as VisuallyHidden from '@radix-ui/react-visually-hidden';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Mail } from 'lucide-react';

interface TrialAccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (email: string) => void;
}

export function TrialAccessModal({
  isOpen,
  onClose,
  onConfirm,
}: TrialAccessModalProps) {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const isEmailValid = /^\S+@\S+\.\S+$/.test(email.trim());

  const handleConfirm = () => {
    const trimmed = email.trim();
    if (!trimmed || !isEmailValid) {
      setError('Enter a valid email to unlock your free full report.');
      return;
    }
    setError(null);
    onConfirm(trimmed);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className='sm:max-w-[420px] p-0 overflow-hidden bg-[#0A0A0A] border border-white/10 shadow-2xl text-white'>
        <VisuallyHidden.Root>
          <DialogTitle>Unlock Your Free Report</DialogTitle>
          <DialogDescription>
            Enter your email to access a one-time full report.
          </DialogDescription>
        </VisuallyHidden.Root>

        <div className='bg-[#111] p-4 border-b border-white/5'>
          <div className='text-sm font-semibold'>Unlock your free full report</div>
          <div className='text-xs text-slate-400'>
            One file, all fields. No other free reports.
          </div>
        </div>

        <div className='p-6 space-y-4'>
          <div className='space-y-2'>
            <Label htmlFor='trial-email' className='text-xs text-slate-300'>
              Email
            </Label>
            <div className='relative'>
              <Mail className='absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500' />
              <Input
                id='trial-email'
                type='email'
                placeholder='you@example.com'
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError(null);
                }}
                className='pl-10 bg-[#1A1A1A] border border-white/10 text-white placeholder:text-slate-600'
              />
            </div>
          </div>

          {error && (
            <Alert className='border-red-500/20 bg-red-500/10'>
              <AlertCircle className='h-4 w-4 text-red-400' />
              <AlertDescription className='text-red-300'>
                {error}
              </AlertDescription>
            </Alert>
          )}

          <div className='flex gap-3'>
            <Button
              onClick={handleConfirm}
              className='flex-1 bg-primary text-black hover:bg-primary/90 font-medium'
            >
              Continue
            </Button>
            <Button
              onClick={onClose}
              variant='outline'
              className='flex-1 border-white/20 text-white hover:bg-white/10'
            >
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
