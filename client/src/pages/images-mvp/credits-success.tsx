import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PublicLayout as Layout } from '@/components/public-layout';
import { Button } from '@/components/ui/button';
import { CheckCircle2, ArrowRight, Coins } from 'lucide-react';
import { trackImagesMvpEvent } from '@/lib/images-mvp-analytics';
import { useAuth } from '@/lib/auth';
import { AuthModal } from '@/components/auth-modal';

interface CreditPack {
  id: string;
  credits: number;
  name: string;
}

export default function ImagesMvpCreditsSuccess() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [pack, setPack] = useState<string | null>(null);
  const [credits, setCredits] = useState<number | null>(null);
  const [balanceCredits, setBalanceCredits] = useState<number | null>(null);
  const [claiming, setClaiming] = useState(false);
  const [claimed, setClaimed] = useState(false);
  const purchaseLogged = useRef(false);
  const paymentConfirmed = useRef(false);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const packName = params.get('pack');
    setPack(packName);

    const loadPacks = async () => {
      try {
        const res = await fetch('/api/images_mvp/credits/packs');
        if (!res.ok) return;
        const data = await res.json();
        const packs = Object.entries(data.packs || {}).map(
          ([id, packData]) => ({ id, ...(packData as Omit<CreditPack, 'id'>) })
        );
        const match = packs.find((p) => p.id === packName);
        if (match) {
          setCredits(match.credits);
        }
      } catch {
        // Best-effort only; fall back to generic message
      }
    };

    if (packName) {
      loadPacks();
    }
  }, []);

  useEffect(() => {
    if (!pack || purchaseLogged.current) return;
    trackImagesMvpEvent('purchase_completed', {
      pack,
      credits,
    });
    purchaseLogged.current = true;
  }, [pack, credits]);

  useEffect(() => {
    const loadBalance = async () => {
      try {
        const res = await fetch('/api/images_mvp/credits/balance', {
          credentials: 'include',
        });
        if (!res.ok) return;
        const data = await res.json();
        if (typeof data?.credits === 'number') setBalanceCredits(data.credits);
      } catch {
        // Best-effort only
      }
    };
    loadBalance();
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated || claimed || claiming) return;
    const claim = async () => {
      setClaiming(true);
      try {
        const res = await fetch('/api/images_mvp/credits/claim', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({}),
        });
        if (res.ok) {
          setClaimed(true);
          // Refresh balance after claim
          const balanceRes = await fetch('/api/images_mvp/credits/balance', {
            credentials: 'include',
          });
          if (balanceRes.ok) {
            const data = await balanceRes.json();
            if (typeof data?.credits === 'number') setBalanceCredits(data.credits);
          }
        }
      } finally {
        setClaiming(false);
      }
    };
    claim();
  }, [isAuthenticated, claimed, claiming]);

  useEffect(() => {
    const confirmPaymentIfNeeded = async () => {
      if (paymentConfirmed.current) return;
      const params = new URLSearchParams(window.location.search);
      const paymentId = params.get('payment_id');
      const status = params.get('status');
      if (!paymentId || status !== 'succeeded') return;

      paymentConfirmed.current = true;
      setConfirming(true);
      try {
        await fetch('/api/payments/confirm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ paymentId }),
        });
      } catch {
        // Best-effort only
      } finally {
        try {
          localStorage.setItem(
            'metaextract_images_mvp_purchase_completed',
            JSON.stringify({ paymentId, at: Date.now() })
          );
        } catch {
          // Best-effort only
        }
        // Refresh balance after confirmation attempt.
        try {
          const res = await fetch('/api/images_mvp/credits/balance', {
            credentials: 'include',
          });
          if (res.ok) {
            const data = await res.json();
            if (typeof data?.credits === 'number') setBalanceCredits(data.credits);
          }
        } catch {
          // Best-effort only
        } finally {
          setConfirming(false);
        }
      }
    };
    void confirmPaymentIfNeeded();
  }, []);

  return (
    <Layout showHeader={true} showFooter={true}>
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <AuthModal
            isOpen={showAuthModal}
            onClose={() => setShowAuthModal(false)}
            defaultTab="login"
          />
          <div className="bg-primary/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <Coins className="w-10 h-10 text-primary" />
          </div>

          <h1 className="text-3xl font-bold text-white mb-4">
            Credits Added
          </h1>

          <p className="text-slate-300 mb-8">
            Your {pack ? `${pack} pack` : 'credit'} purchase is complete.
            {credits !== null && ` ${credits} credits have been added.`}
          </p>

          <div className="bg-white/5 border border-white/10 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-center gap-2 text-emerald-400 text-sm font-semibold mb-2">
              <CheckCircle2 className="w-4 h-4" />
              1 credit = 1 standard image (JPG, PNG, HEIC, WebP)
            </div>
            <p className="text-xs text-slate-500">
              Credits apply only to the Images MVP tool.
            </p>
            <p className="text-xs text-slate-500 mt-2">
              Credits do not expire.
            </p>
            {confirming && (
              <p className="text-xs text-slate-300 mt-2">
                Updating your balance…
              </p>
            )}
            {balanceCredits !== null && (
              <p className="text-xs text-slate-300 mt-2">
                Current balance: <span className="text-white font-semibold">{balanceCredits}</span> credits
              </p>
            )}
            <p className="text-xs text-slate-500 mt-2">
              Refunds are available within 7 days for unused credit packs only. If any credits are used, the purchase is non-refundable.
            </p>
          </div>

          {!isAuthenticated && (
            <div className="bg-white/5 border border-white/10 rounded-lg p-4 mb-4 text-left">
              <div className="text-sm font-semibold text-white mb-1">
                Save credits to your account
              </div>
              <div className="text-xs text-slate-300">
                To use credits across browsers/devices, sign in or create an account now.
              </div>
              <div className="flex gap-2 mt-3">
                <Button
                  onClick={() => {
                    setShowAuthModal(true);
                  }}
                  variant="outline"
                  className="border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
                >
                  Sign In
                </Button>
                <Button
                  onClick={() => {
                    setShowAuthModal(true);
                  }}
                  className="bg-primary hover:bg-primary/90 text-black font-semibold"
                >
                  Create Account
                </Button>
              </div>
            </div>
          )}

          {isAuthenticated && (claiming || claimed) && (
            <div className="text-xs text-slate-300 mb-4">
              {claiming ? 'Saving credits to your account…' : 'Credits saved to your account.'}
            </div>
          )}

          <Button
            onClick={() => navigate('/images_mvp')}
            className="bg-primary hover:bg-primary/90 text-black font-bold px-8 py-3"
          >
            Analyze More Photos <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </Layout>
  );
}
