import React, { useEffect, useMemo, useState } from 'react';
import { PRICING_TITLE, PRICING_SUBTITLE } from './strings';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import * as VisuallyHidden from '@radix-ui/react-visually-hidden';
import { Button } from '@/components/ui/button';
import { Loader2, CreditCard } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/lib/auth';
import { AuthModal } from '@/components/auth-modal';
import { showUploadError } from '@/lib/toast-helpers';

interface PricingModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultEmail?: string;
}

interface CreditPack {
  id: string;
  credits: number;
  priceDisplay: string;
  name: string;
  description: string;
}

export function PricingModal({
  isOpen,
  onClose,
  defaultEmail,
}: PricingModalProps) {
  const isLocalhost =
    typeof window !== 'undefined' &&
    (window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1');
  const [packs, setPacks] = useState<CreditPack[]>([]);
  const [loadingPacks, setLoadingPacks] = useState(false);
  const [purchaseLoading, setPurchaseLoading] = useState<string | null>(null);
  const [email, setEmail] = useState(defaultEmail || '');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [pendingPackId, setPendingPackId] = useState<string | null>(null);
  const [pendingCheckoutUrl, setPendingCheckoutUrl] = useState<string | null>(
    null
  );
  const { toast } = useToast();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    setEmail(defaultEmail || '');
  }, [defaultEmail]);

  useEffect(() => {
    if (isOpen) setPendingCheckoutUrl(null);
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const loadPacks = async () => {
      setLoadingPacks(true);
      try {
        const res = await fetch('/api/images_mvp/credits/packs');
        if (!res.ok) {
          throw new Error('Failed to load packs');
        }
        const data = await res.json();
        const packEntries = Object.entries(data.packs || {}).map(
          ([id, pack]) => ({ id, ...(pack as Omit<CreditPack, 'id'>) })
        );
        setPacks(packEntries);
      } catch {
        showUploadError(toast, 'Please try again in a moment.');
      } finally {
        setLoadingPacks(false);
      }
    };

    loadPacks();
  }, [isOpen, toast]);

  const sortedPacks = useMemo(
    () => [...packs].sort((a, b) => a.credits - b.credits),
    [packs]
  );

  const handlePurchase = async (packId: string) => {
    if (purchaseLoading) return;
    if (!isAuthenticated) {
      setPendingPackId(packId);
      setShowAuthModal(true);
      return;
    }
    setPurchaseLoading(packId);
    try {
      const res = await fetch('/api/images_mvp/credits/purchase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          pack: packId,
          email: email || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || 'Purchase failed');
      }

      if (!data.checkout_url) {
        throw new Error('Checkout URL missing');
      }

      try {
        localStorage.setItem(
          'metaextract_images_mvp_purchase_in_progress',
          String(Date.now())
        );
      } catch {
        // Best-effort only
      }

      const opened = window.open(
        data.checkout_url,
        '_blank',
        'noopener,noreferrer'
      );
      if (!opened) {
        setPendingCheckoutUrl(data.checkout_url);
        showUploadError(
          toast,
          'Allow popups for this site, then click "Open Checkout".'
        );
        return;
      }

      onClose();
    } catch (error: any) {
      showUploadError(toast, error?.message || 'Unable to start checkout.');
    } finally {
      setPurchaseLoading(null);
    }
  };

  return (
    <Dialog
      open={isOpen}
      modal={true}
      onOpenChange={open => {
        if (!open) onClose();
      }}
    >
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultTab="login"
        onSuccess={() => {
          setShowAuthModal(false);
          const packId = pendingPackId;
          setPendingPackId(null);
          if (packId) void handlePurchase(packId);
        }}
      />
      <DialogContent
        className="sm:max-w-[520px] p-0 overflow-hidden bg-[#0A0A0A] border border-white/10 shadow-2xl text-white"
        onOpenAutoFocus={event => {
          event.preventDefault();
          setTimeout(() => {
            const emailInput = document.getElementById('pricing-email');
            emailInput?.focus();
          }, 100);
        }}
      >
        <VisuallyHidden.Root>
          <DialogTitle>Buy Credits</DialogTitle>
          <DialogDescription>
            Purchase credits to analyze more images.
          </DialogDescription>
        </VisuallyHidden.Root>

        <div className="p-6 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
              <CreditCard className="w-4 h-4 text-primary" />
            </div>
            <div>
              <div className="font-semibold">{PRICING_TITLE}</div>

              <div className="text-xs text-slate-200">{PRICING_SUBTITLE}</div>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-5">
          {pendingCheckoutUrl && (
            <div className="rounded-lg border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">
                Open Checkout
              </div>
              <div className="text-xs text-slate-300 mt-1">
                Your browser blocked the checkout popup. Enable popups, then
                click below.
              </div>
              <div className="mt-3 flex gap-2">
                <Button
                  className="bg-primary text-black hover:bg-primary/90 font-semibold"
                  onClick={() => {
                    const opened = window.open(
                      pendingCheckoutUrl,
                      '_blank',
                      'noopener,noreferrer'
                    );
                    if (opened) onClose();
                  }}
                >
                  Open Checkout
                </Button>
                <Button
                  variant="outline"
                  className="border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
                  onClick={() => setPendingCheckoutUrl(null)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
          {isLocalhost && (
            <div className="rounded-lg border border-amber-500/20 bg-amber-500/10 p-4">
              <div className="text-xs text-amber-200">
                Local dev uses Dodo test mode. No real money is charged.
              </div>
            </div>
          )}
          <div className="space-y-2">
            <label
              htmlFor="pricing-email"
              className="text-xs font-medium text-slate-200"
            >
              Email (optional)
            </label>
            <input
              id="pricing-email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="name@example.com"
              autoComplete="email"
              className="w-full px-3 py-2 bg-[#1A1A1A] border border-white/10 rounded-md text-sm text-white focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-500"
            />
          </div>

          {loadingPacks ? (
            <div className="flex items-center justify-center py-6">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
            </div>
          ) : (
            <div className="grid gap-4">
              {sortedPacks.map(pack => (
                <div
                  key={pack.id}
                  className="border border-white/10 rounded-lg p-4 flex items-center justify-between gap-4"
                >
                  <div>
                    <div className="text-sm font-semibold text-white">
                      {pack.name}
                    </div>
                    <div className="text-xs text-slate-200">
                      {pack.description}
                    </div>
                    <div className="text-xs text-primary mt-1">
                      {pack.credits} credits
                    </div>
                  </div>
                  <Button
                    onClick={() => handlePurchase(pack.id)}
                    disabled={!!purchaseLoading}
                    className="bg-primary text-black hover:bg-primary/90 font-semibold"
                  >
                    {purchaseLoading === pack.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      pack.priceDisplay
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
