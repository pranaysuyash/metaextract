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

interface LimitedAccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (email: string) => void;
}

export function LimitedAccessModal({
  isOpen,
  onClose,
  onConfirm,
}: LimitedAccessModalProps) {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const isEmailValid = /^\S+@\S+\.\S+$/.test(email.trim());

  const handleConfirm = () => {
    const trimmed = email.trim();
    if (!trimmed || !isEmailValid) {
      setError('Enter a valid email to unlock the full report.');
      return;
    }
    setError(null);
    onConfirm(trimmed);
  };

  return (
    <Dialog
      open={isOpen}
      modal={true}
      onOpenChange={open => !open && onClose()}
    >
      <DialogContent
        className="sm:max-w-[420px] p-0 overflow-hidden bg-[#0A0A0A] border border-white/10 shadow-2xl text-white"
        onOpenAutoFocus={event => {
          event.preventDefault();
          // Focus the email input when modal opens
          setTimeout(() => {
            const emailInput = document.getElementById('access-email');
            emailInput?.focus();
          }, 100);
        }}
      >
        <VisuallyHidden.Root>
          <DialogTitle>Unlock the full report</DialogTitle>
          <DialogDescription>
            Enter your email to access a one-time full report.
          </DialogDescription>
        </VisuallyHidden.Root>

        <div className="bg-[#111] p-4 border-b border-white/5">
          <div className="text-sm font-semibold">Unlock the full report</div>
          <div className="text-xs text-slate-200">
            One file, full details. This unlock is for a single report.
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="access-email" className="text-xs text-slate-200">
              Email
            </Label>
            <div className="relative">
              <Mail
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500"
                aria-hidden="true"
              />
              <Input
                id="access-email"
                type="email"
                placeholder="you@example.com"
                value={email}
                autoComplete="email"
                onChange={e => {
                  setEmail(e.target.value);
                  if (error) setError(null);
                }}
                className="pl-10 bg-[#1A1A1A] border border-white/10 text-white placeholder:text-slate-600"
              />
            </div>
          </div>

          {error && (
            <div role="alert">
              <Alert className="border-red-500/20 bg-red-500/10">
                <AlertCircle className="h-4 w-4 text-red-400" />
                <AlertDescription className="text-red-300">
                  {error}
                </AlertDescription>
              </Alert>
            </div>
          )}

          <div className="flex gap-3">
            <Button
              onClick={handleConfirm}
              className="flex-1 bg-primary text-black hover:bg-primary/90 font-medium"
            >
              Continue
            </Button>
            <Button
              onClick={onClose}
              variant="outline"
              className="flex-1 border-white/20 text-white hover:bg-white/10"
            >
              Cancel
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
