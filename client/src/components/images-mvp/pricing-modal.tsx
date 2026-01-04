import React, { useEffect, useMemo, useState } from 'react';
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
  const [packs, setPacks] = useState<CreditPack[]>([]);
  const [loadingPacks, setLoadingPacks] = useState(false);
  const [purchaseLoading, setPurchaseLoading] = useState<string | null>(null);
  const [email, setEmail] = useState(defaultEmail || '');
  const { toast } = useToast();

  useEffect(() => {
    setEmail(defaultEmail || '');
  }, [defaultEmail]);

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
        toast({
          title: 'Unable to load pricing',
          description: 'Please try again in a moment.',
          variant: 'destructive',
        });
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

  const getSessionId = (): string => {
    let sessionId = localStorage.getItem('metaextract_session_id');
    if (!sessionId) {
      sessionId = crypto.randomUUID();
      localStorage.setItem('metaextract_session_id', sessionId);
    }
    return sessionId;
  };

  const handlePurchase = async (packId: string) => {
    if (purchaseLoading) return;
    setPurchaseLoading(packId);
    try {
      const res = await fetch('/api/images_mvp/credits/purchase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pack: packId,
          sessionId: getSessionId(),
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

      window.location.href = data.checkout_url;
    } catch (error: any) {
      toast({
        title: 'Payment failed',
        description: error?.message || 'Unable to start checkout.',
        variant: 'destructive',
      });
    } finally {
      setPurchaseLoading(null);
    }
  };

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent className="sm:max-w-[520px] p-0 overflow-hidden bg-[#0A0A0A] border border-white/10 shadow-2xl text-white">
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
              <div className="font-semibold">Buy Image Credits</div>
              <div className="text-xs text-slate-400">
                1 credit = 1 standard image (JPG, PNG, HEIC, WebP)
              </div>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-5">
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-300">
              Email (optional)
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              className="w-full px-3 py-2 bg-[#1A1A1A] border border-white/10 rounded-md text-sm text-white focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-600"
            />
          </div>

          {loadingPacks ? (
            <div className="flex items-center justify-center py-6">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
            </div>
          ) : (
            <div className="grid gap-4">
              {sortedPacks.map((pack) => (
                <div
                  key={pack.id}
                  className="border border-white/10 rounded-lg p-4 flex items-center justify-between gap-4"
                >
                  <div>
                    <div className="text-sm font-semibold text-white">
                      {pack.name}
                    </div>
                    <div className="text-xs text-slate-400">
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
