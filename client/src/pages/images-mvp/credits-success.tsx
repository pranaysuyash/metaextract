import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PublicLayout as Layout } from '@/components/public-layout';
import { Button } from '@/components/ui/button';
import { CheckCircle2, ArrowRight, Coins } from 'lucide-react';

interface CreditPack {
  id: string;
  credits: number;
  name: string;
}

export default function ImagesMvpCreditsSuccess() {
  const navigate = useNavigate();
  const [pack, setPack] = useState<string | null>(null);
  const [credits, setCredits] = useState<number | null>(null);

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

  return (
    <Layout showHeader={true} showFooter={true}>
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-primary/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <Coins className="w-10 h-10 text-primary" />
          </div>

          <h1 className="text-3xl font-bold text-white mb-4">
            Credits Added
          </h1>

          <p className="text-slate-400 mb-8">
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
          </div>

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
