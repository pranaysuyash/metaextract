import React, { useEffect, useState } from 'react';
import { Layout } from '@/components/layout';
import { Button } from '@/components/ui/button';

type BalanceResponse = { credits?: number; balanceId?: string | null };
type Tx = {
  id: string;
  type: string;
  amount: number;
  description: string | null;
  createdAt: string;
  dodoPaymentId: string | null;
};

async function fetchJson(path: string) {
  const res = await fetch(path, { credentials: 'include' });
  const data = await res.json().catch(() => null);
  return { ok: res.ok, status: res.status, data };
}

export default function CreditsPage() {
  const [loading, setLoading] = useState(true);
  const [coreBalance, setCoreBalance] = useState<{ credits: number; balanceId: string | null }>({
    credits: 0,
    balanceId: null,
  });
  const [imagesBalance, setImagesBalance] = useState<{ credits: number; balanceId: string | null }>({
    credits: 0,
    balanceId: null,
  });
  const [coreTx, setCoreTx] = useState<Tx[]>([]);
  const [imagesTx, setImagesTx] = useState<Tx[]>([]);
  const [error, setError] = useState<string | null>(null);
  const isLocalDev =
    typeof window !== 'undefined' &&
    import.meta.env.DEV &&
    (window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1');

  const loadAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [core, images] = await Promise.all([
        fetchJson('/api/credits/balance'),
        fetchJson('/api/images_mvp/credits/balance'),
      ]);

      if (!core.ok || !images.ok) {
        setError('Failed to load balances.');
        return;
      }

      const coreData = (core.data || {}) as BalanceResponse;
      const imagesData = (images.data || {}) as BalanceResponse;
      const coreCredits = typeof coreData.credits === 'number' ? coreData.credits : 0;
      const imagesCredits = typeof imagesData.credits === 'number' ? imagesData.credits : 0;
      const coreBalanceId = typeof coreData.balanceId === 'string' ? coreData.balanceId : null;
      const imagesBalanceId = typeof imagesData.balanceId === 'string' ? imagesData.balanceId : null;

      setCoreBalance({ credits: coreCredits, balanceId: coreBalanceId });
      setImagesBalance({ credits: imagesCredits, balanceId: imagesBalanceId });

      const [coreTxRes, imagesTxRes] = await Promise.all([
        coreBalanceId ? fetchJson(`/api/credits/transactions?balanceId=${encodeURIComponent(coreBalanceId)}`) : Promise.resolve({ ok: true, data: { transactions: [] } }),
        imagesBalanceId ? fetchJson(`/api/images_mvp/credits/transactions?balanceId=${encodeURIComponent(imagesBalanceId)}`) : Promise.resolve({ ok: true, data: { transactions: [] } }),
      ]);

      const coreList = (coreTxRes.data as any)?.transactions;
      const imagesList = (imagesTxRes.data as any)?.transactions;
      setCoreTx(Array.isArray(coreList) ? coreList : []);
      setImagesTx(Array.isArray(imagesList) ? imagesList : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadAll();
  }, []);

  const grantDevCredits = async (scope: 'core' | 'images') => {
    try {
      const endpoint =
        scope === 'core'
          ? '/api/dev/credits/grant'
          : '/api/dev/images_mvp/credits/grant';
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ credits: 100 }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.error || 'Failed to grant credits');
      }
      await loadAll();
    } catch (e: any) {
      setError(e?.message || 'Failed to grant credits.');
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-[#0B0C10] text-white">
        <div className="max-w-5xl mx-auto px-4 py-10">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold">Credits</h1>
              <p className="text-sm text-slate-300 mt-1">
                Balances are tracked separately for Images MVP and Core.
              </p>
            </div>
            <Button
              variant="outline"
              className="border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
              onClick={() => void loadAll()}
              disabled={loading}
            >
              Refresh
            </Button>
          </div>

          {error && (
            <div className="mt-6 rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-200">
              {error}
            </div>
          )}

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-lg border border-white/10 bg-white/5 p-5">
              <div className="text-sm font-semibold">Images credits (launch)</div>
              <div className="mt-2 text-3xl font-bold">
                {loading ? '…' : imagesBalance.credits}
              </div>
              <div className="mt-1 text-xs text-slate-400">
                Used by `Images MVP` uploads.
              </div>
              <div className="mt-4">
                <div className="text-xs text-slate-300 mb-2">Recent activity</div>
                <div className="space-y-2">
                  {(imagesTx.slice(0, 5) || []).map(t => (
                    <div
                      key={t.id}
                      className="flex items-center justify-between text-xs border border-white/10 bg-black/20 rounded px-3 py-2"
                    >
                      <div className="truncate pr-2">
                        <div className="text-slate-200 truncate">{t.description || t.type}</div>
                        <div className="text-slate-500">{new Date(t.createdAt).toLocaleString()}</div>
                      </div>
                      <div className="font-mono text-slate-200">
                        {t.type === 'usage' ? '-' : '+'}
                        {Math.abs(t.amount)}
                      </div>
                    </div>
                  ))}
                  {(!loading && imagesTx.length === 0) && (
                    <div className="text-xs text-slate-500">No transactions yet.</div>
                  )}
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-white/10 bg-white/5 p-5">
              <div className="text-sm font-semibold">Core credits (internal)</div>
              <div className="mt-2 text-3xl font-bold">
                {loading ? '…' : coreBalance.credits}
              </div>
              <div className="mt-1 text-xs text-slate-400">
                Used by the Core extractor routes.
              </div>
              <div className="mt-4">
                <div className="text-xs text-slate-300 mb-2">Recent activity</div>
                <div className="space-y-2">
                  {(coreTx.slice(0, 5) || []).map(t => (
                    <div
                      key={t.id}
                      className="flex items-center justify-between text-xs border border-white/10 bg-black/20 rounded px-3 py-2"
                    >
                      <div className="truncate pr-2">
                        <div className="text-slate-200 truncate">{t.description || t.type}</div>
                        <div className="text-slate-500">{new Date(t.createdAt).toLocaleString()}</div>
                      </div>
                      <div className="font-mono text-slate-200">
                        {t.type === 'usage' ? '-' : '+'}
                        {Math.abs(t.amount)}
                      </div>
                    </div>
                  ))}
                  {(!loading && coreTx.length === 0) && (
                    <div className="text-xs text-slate-500">No transactions yet.</div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {isLocalDev && (
            <div className="mt-6 rounded-lg border border-amber-500/20 bg-amber-500/10 p-4">
              <div className="text-sm font-semibold text-amber-200">
                Dev tools
              </div>
              <div className="mt-1 text-xs text-amber-200/90">
                Grants +100 credits for quick testing (dev-only endpoints).
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <Button
                  variant="outline"
                  className="border-amber-400/30 text-amber-100 hover:text-amber-50 hover:bg-amber-500/10"
                  onClick={() => void grantDevCredits('images')}
                  disabled={loading}
                >
                  +100 Images MVP credits
                </Button>
                <Button
                  variant="outline"
                  className="border-amber-400/30 text-amber-100 hover:text-amber-50 hover:bg-amber-500/10"
                  onClick={() => void grantDevCredits('core')}
                  disabled={loading}
                >
                  +100 Core credits
                </Button>
              </div>
            </div>
          )}

          <div className="mt-6 text-xs text-slate-500">
            Refunds are available within 7 days for unused credit packs only. Credits do not expire.
          </div>
        </div>
      </div>
    </Layout>
  );
}
