import { Layout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { CheckCircle2, ArrowRight, Coins } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { AuthModal } from "@/components/auth-modal";

export default function CreditsSuccess() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [pack, setPack] = useState<string | null>(null);
  const [credits, setCredits] = useState<number>(0);
  const [balanceCredits, setBalanceCredits] = useState<number | null>(null);
  const [claiming, setClaiming] = useState(false);
  const [claimed, setClaimed] = useState(false);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const packName = params.get("pack");
    setPack(packName);

    const loadPacks = async () => {
      try {
        const res = await fetch("/api/credits/packs");
        if (!res.ok) return;
        const data = await res.json();
        const entry = data?.packs?.[packName || ""];
        if (entry && typeof entry.credits === "number") {
          setCredits(entry.credits);
        }
      } catch {
        // Best-effort
      }
    };

    if (packName) loadPacks();
  }, []);

  useEffect(() => {
    const loadBalance = async () => {
      try {
        const res = await fetch("/api/credits/balance", {
          credentials: "include",
        });
        if (!res.ok) return;
        const data = await res.json();
        if (typeof data?.credits === "number") setBalanceCredits(data.credits);
      } catch {
        // Best-effort
      }
    };
    loadBalance();
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated || claimed || claiming) return;
    const claim = async () => {
      setClaiming(true);
      try {
        const res = await fetch("/api/credits/claim", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({}),
        });
        if (res.ok) {
          setClaimed(true);
          const balanceRes = await fetch("/api/credits/balance", {
            credentials: "include",
          });
          if (balanceRes.ok) {
            const data = await balanceRes.json();
            if (typeof data?.credits === "number")
              setBalanceCredits(data.credits);
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
      const params = new URLSearchParams(window.location.search);
      const paymentId = params.get("payment_id");
      const status = params.get("status");
      if (!paymentId || status !== "succeeded") return;

      setConfirming(true);
      try {
        await fetch("/api/payments/confirm", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ paymentId }),
        });
      } catch {
        // Best-effort
      } finally {
        try {
          localStorage.setItem(
            "metaextract_core_purchase_completed",
            JSON.stringify({ paymentId, at: Date.now() })
          );
        } catch {
          // Best-effort
        }
        try {
          const res = await fetch("/api/credits/balance", {
            credentials: "include",
          });
          if (res.ok) {
            const data = await res.json();
            if (typeof data?.credits === "number")
              setBalanceCredits(data.credits);
          }
        } catch {
          // Best-effort
        } finally {
          setConfirming(false);
        }
      }
    };
    void confirmPaymentIfNeeded();
  }, []);

  const packDisplayNames: Record<string, string> = {
    single: "Single Pack",
    batch: "Batch Pack",
    bulk: "Bulk Pack",
  };

  return (
    <Layout>
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
          
          <h1 className="text-3xl font-bold text-white mb-4" data-testid="text-credits-success-title">
            Credits Added!
          </h1>
          
          <p className="text-slate-300 mb-8" data-testid="text-credits-success-message">
            Your {pack ? packDisplayNames[pack] || pack : "credit"} purchase is complete. 
            {credits > 0 && ` ${credits} credits have been added to your balance.`}
          </p>

          <div className="bg-white/5 border border-white/10 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-center gap-2 text-emerald-400 text-sm font-semibold mb-2">
              <CheckCircle2 className="w-4 h-4" />
              Credits do not expire
            </div>
            <h3 className="text-white font-semibold mb-4">Credit Usage:</h3>
            <ul className="text-left text-slate-200 space-y-2 text-sm">
              <li className="flex justify-between">
                <span>Standard Image (JPG/PNG)</span>
                <span className="text-primary font-mono">1 Credit</span>
              </li>
              <li className="flex justify-between">
                <span>RAW Image (CR2/NEF/ARW)</span>
                <span className="text-primary font-mono">2 Credits</span>
              </li>
              <li className="flex justify-between">
                <span>Audio File (MP3/FLAC)</span>
                <span className="text-primary font-mono">2 Credits</span>
              </li>
              <li className="flex justify-between">
                <span>Video File (MP4/MOV)</span>
                <span className="text-primary font-mono">3 Credits</span>
              </li>
            </ul>
            {balanceCredits !== null && (
              <div className="text-xs text-slate-300 mt-4">
                Current balance:{" "}
                <span className="text-white font-semibold">
                  {balanceCredits}
                </span>{" "}
                credits
              </div>
            )}
            {confirming && (
              <div className="text-xs text-slate-300 mt-4">
                Updating your balance…
              </div>
            )}
            <div className="text-xs text-slate-500 mt-2">
              Refunds are available within 7 days for unused credit packs only.
              If any credits are used, the purchase is non-refundable.
            </div>
          </div>

          {!isAuthenticated && (
            <div className="bg-white/5 border border-white/10 rounded-lg p-4 mb-4 text-left">
              <div className="text-sm font-semibold text-white mb-1">
                Save credits to your account
              </div>
              <div className="text-xs text-slate-300">
                To use credits across browsers/devices, sign in or create an
                account now.
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
              {claiming ? "Saving credits to your account…" : "Credits saved to your account."}
            </div>
          )}

          <Button
            onClick={() => navigate("/")}
            className="bg-primary hover:bg-primary/90 text-black font-bold px-8 py-3"
            data-testid="button-start-extracting"
          >
            Start Extracting <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </Layout>
  );
}
