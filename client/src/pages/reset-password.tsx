import React, { useState } from 'react';
import { PublicLayout as Layout } from '@/components/public-layout';
import { Button } from '@/components/ui/button';

type RequestResponse = {
  message?: string;
  token?: string;
};

export default function ResetPasswordPage() {
  const [email, setEmail] = useState('');
  const [requested, setRequested] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const requestReset = async () => {
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch('/api/auth/password-reset/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email }),
      });
      const data = (await res.json().catch(() => null)) as RequestResponse | null;
      setRequested(true);
      if (data?.token) setToken(data.token);
      setStatus(data?.message || 'If an account exists, a reset link was sent.');
    } catch {
      setStatus('Failed to request password reset. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const confirmReset = async () => {
    if (newPassword !== confirmPassword) {
      setStatus('Passwords do not match.');
      return;
    }
    if (!token) {
      setStatus('Missing reset token.');
      return;
    }
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch('/api/auth/password-reset/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ token, password: newPassword }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        setStatus((data as any)?.error || 'Password reset failed.');
        return;
      }
      setStatus('Password updated. You can now sign in.');
    } catch {
      setStatus('Password reset failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout showHeader={true} showFooter={true}>
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <h1 className="text-2xl font-bold text-white mb-2">Reset password</h1>
          <p className="text-sm text-slate-300 mb-6">
            Enter your email to request a password reset. In local dev, we’ll show
            the token on-screen.
          </p>

          <div className="space-y-3">
            <label className="text-xs text-slate-300">Email</label>
            <input
              className="w-full px-3 py-2 bg-[#1A1A1A] border border-white/10 rounded-md text-sm text-white focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
            <Button
              className="w-full bg-primary text-black hover:bg-primary/90 font-semibold"
              disabled={loading || !email}
              onClick={requestReset}
            >
              Request reset
            </Button>
          </div>

          {requested && (
            <div className="mt-6 space-y-3 rounded-lg border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold text-white">Set new password</div>
              <div className="text-xs text-slate-300">
                {token
                  ? 'Dev token populated below.'
                  : 'Check your email for a reset link/token.'}
              </div>
              <label className="text-xs text-slate-300">Reset token</label>
              <input
                className="w-full px-3 py-2 bg-[#1A1A1A] border border-white/10 rounded-md text-sm text-white focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-500"
                value={token || ''}
                onChange={(e) => setToken(e.target.value)}
                placeholder="token"
                autoComplete="off"
              />
              <label className="text-xs text-slate-300">New password</label>
              <input
                type="password"
                className="w-full px-3 py-2 bg-[#1A1A1A] border border-white/10 rounded-md text-sm text-white focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-500"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="new-password"
              />
              <label className="text-xs text-slate-300">Confirm password</label>
              <input
                type="password"
                className="w-full px-3 py-2 bg-[#1A1A1A] border border-white/10 rounded-md text-sm text-white focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-500"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="new-password"
              />
              <Button
                className="w-full bg-primary text-black hover:bg-primary/90 font-semibold"
                disabled={loading}
                onClick={confirmReset}
              >
                Update password
              </Button>
            </div>
          )}

          {status && (
            <div className="mt-4 text-xs text-slate-300">{status}</div>
          )}
        </div>
      </div>
    </Layout>
  );
}

