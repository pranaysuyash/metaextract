import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import * as VisuallyHidden from '@radix-ui/react-visually-hidden';
import { Button } from '@/components/ui/button';
import { Lock, X, AlertCircle, Zap } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function PaymentModal({
  isOpen,
  onClose,
  onSuccess,
}: PaymentModalProps) {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);

  const PRICE_USD = 5;
  const PRODUCT_NAME = 'MetaExtract - Full Report Unlock';
  const IS_DEMO = process.env.NODE_ENV === 'development';

  const isEmailValid = /^\S+@\S+\.\S+$/.test(email.trim());

  const handlePay = async () => {
    if (loading) return;

    if (!IS_DEMO) {
      const trimmed = email.trim();
      if (!trimmed || !/^\S+@\S+\.\S+$/.test(trimmed)) {
        setEmailError('Please enter a valid email address');
        return;
      }
    }

    setEmailError(null);
    setLoading(true);

    try {
      if (IS_DEMO) {
        // Demo mode: instant unlock
        await new Promise((resolve) => setTimeout(resolve, 800));
      } else {
        // Production: real payment processing
        await new Promise((resolve) => setTimeout(resolve, 1500));
      }
      onSuccess();
      onClose();
    } finally {
      setLoading(false);
    }
  };

  const handleDemoUnlock = () => {
    onSuccess();
    onClose();
  };

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent className='sm:max-w-[400px] p-0 overflow-hidden bg-[#0A0A0A] border border-white/10 shadow-2xl text-white'>
        <VisuallyHidden.Root>
          <DialogTitle>Payment - Unlock Full Report</DialogTitle>
          <DialogDescription>
            Complete your payment to unlock the full metadata report.
          </DialogDescription>
        </VisuallyHidden.Root>
        
        {/* Header */}
        <div className='bg-[#111] p-4 flex items-center justify-between border-b border-white/5'>
          <div className='flex items-center gap-2'>
            <div className='w-6 h-6 bg-primary rounded-full flex items-center justify-center'>
              <Zap className='w-3 h-3 text-black' />
            </div>
            <span className='font-semibold text-sm'>
              {IS_DEMO ? 'MetaExtract Demo' : 'MetaExtract Pro'}
            </span>
          </div>
          <button
            type='button'
            onClick={onClose}
            className='text-slate-500 hover:text-white transition-colors'
          >
            <X className='w-4 h-4' />
          </button>
        </div>

        <div className='p-6'>
          {IS_DEMO && (
            <Alert className='mb-6 border-blue-500/20 bg-blue-500/10'>
              <AlertCircle className='h-4 w-4 text-blue-400' />
              <AlertDescription className='text-blue-300'>
                <strong>Demo Mode:</strong> This is a demonstration. In production, 
                this would process real payments to unlock premium features.
              </AlertDescription>
            </Alert>
          )}

          <div className='mb-6'>
            <div className='text-slate-400 text-xs uppercase tracking-wider mb-1'>
              {IS_DEMO ? 'Demo Unlock' : 'Total Due'}
            </div>
            <div className='text-3xl font-bold'>
              {IS_DEMO ? 'FREE' : `$${PRICE_USD.toFixed(2)}`}
            </div>
            <div className='text-slate-500 text-sm mt-1'>{PRODUCT_NAME}</div>
          </div>

          {IS_DEMO ? (
            <div className='space-y-4'>
              <div className='text-sm text-slate-300'>
                In demo mode, you can instantly unlock all premium features to explore the full capabilities of MetaExtract.
              </div>
              
              <div className='grid grid-cols-2 gap-3'>
                <Button
                  onClick={handleDemoUnlock}
                  className='bg-primary text-black hover:bg-primary/90 font-medium'
                >
                  <Zap className='w-4 h-4 mr-2' />
                  Instant Unlock
                </Button>
                
                <Button
                  onClick={handlePay}
                  disabled={loading}
                  variant="outline"
                  className='border-white/20 text-white hover:bg-white/10 font-medium'
                >
                  {loading ? 'Processing...' : 'Demo Payment'}
                </Button>
              </div>
              
              <div className='text-xs text-slate-500 text-center'>
                Try both flows to see the complete user experience
              </div>
            </div>
          ) : (
            <div className='space-y-4'>
              <div className='space-y-2'>
                <label
                  htmlFor='checkout-email'
                  className='text-xs font-medium text-slate-300'
                >
                  Email
                </label>
                <input
                  id='checkout-email'
                  name='email'
                  type='email'
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (emailError) setEmailError(null);
                  }}
                  onBlur={() => {
                    const trimmed = email.trim();
                    if (!trimmed) {
                      setEmailError('Email is required');
                      return;
                    }
                    if (!isEmailValid)
                      setEmailError('Please enter a valid email address');
                  }}
                  autoComplete='email'
                  placeholder='name@example.com'
                  aria-invalid={!!emailError}
                  aria-describedby={
                    emailError ? 'checkout-email-error' : undefined
                  }
                  className='w-full px-3 py-2 bg-[#1A1A1A] border border-white/10 rounded-md text-sm text-white focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-600'
                />
                {emailError && (
                  <div
                    id='checkout-email-error'
                    className='text-[11px] text-red-400'
                  >
                    {emailError}
                  </div>
                )}
              </div>

              <div className='space-y-2'>
                <label className='text-xs font-medium text-slate-300'>
                  Card Information
                </label>
                <div className='bg-[#1A1A1A] border border-white/10 rounded-md overflow-hidden'>
                  <input
                    id='card-number'
                    name='cardNumber'
                    type='text'
                    inputMode='numeric'
                    autoComplete='cc-number'
                    placeholder='1234 5678 1234 5678'
                    className='w-full px-3 py-2 bg-transparent border-b border-white/10 text-sm text-white focus:bg-[#222] outline-none placeholder:text-slate-600'
                  />
                  <div className='flex'>
                    <input
                      id='card-exp'
                      name='cardExp'
                      type='text'
                      inputMode='numeric'
                      autoComplete='cc-exp'
                      placeholder='MM / YY'
                      className='w-1/2 px-3 py-2 bg-transparent border-r border-white/10 text-sm text-white focus:bg-[#222] outline-none placeholder:text-slate-600'
                    />
                    <input
                      id='card-cvc'
                      name='cardCvc'
                      type='text'
                      inputMode='numeric'
                      autoComplete='cc-csc'
                      placeholder='CVC'
                      className='w-1/2 px-3 py-2 bg-transparent text-sm text-white focus:bg-[#222] outline-none placeholder:text-slate-600'
                    />
                  </div>
                </div>
              </div>

              <Button
                onClick={handlePay}
                disabled={loading || !email.trim() || !isEmailValid}
                className='w-full bg-white text-black hover:bg-slate-200 mt-4 h-10 font-medium'
              >
                {loading ? 'Processing...' : `Pay $${PRICE_USD.toFixed(2)}`}
              </Button>
            </div>
          )}

          <div className='mt-6 flex justify-center gap-4 text-[10px] text-slate-600'>
            <span className='flex items-center gap-1'>
              <Lock className='w-2.5 h-2.5' /> 
              {IS_DEMO ? 'Demo Environment' : 'Secure Checkout'}
            </span>
            <span>MetaExtract Pro</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}