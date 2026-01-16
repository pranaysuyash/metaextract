import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, Lock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface LimitedAccessBannerProps {
  isLimited: boolean;
  lockedTotal: number;
  lockedGroups: Array<{ key: string; label: string; count: number }>;
  onPaywallCta: () => void;
  onNavigateToUpload: () => void;
}

export const LimitedAccessBanner: React.FC<LimitedAccessBannerProps> = ({
  isLimited,
  lockedTotal,
  lockedGroups,
  onPaywallCta,
  onNavigateToUpload,
}) => {
  if (!isLimited || lockedTotal === 0) return null;

  return (
    <Card className="mb-6 bg-[#121217] border-white/10">
      <CardHeader>
        <CardTitle className="text-sm font-mono text-slate-400">
          UNLOCK FULL REPORT
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <div className="text-slate-200">
          Unlock {lockedTotal} additional fields for this file.
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {lockedGroups.slice(0, 6).map(group => (
            <div
              key={group.key}
              className="flex items-center justify-between border border-white/5 rounded px-3 py-2 bg-white/5"
            >
              <span className="text-slate-400">{group.label}</span>
              <span className="text-slate-200 font-mono">
                {group.count}
              </span>
            </div>
          ))}
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={onPaywallCta}
            className="bg-primary text-black hover:bg-primary/90"
          >
            Get credits
          </Button>
          <Button
            variant="outline"
            className="border-white/10 hover:bg-white/5"
            onClick={onNavigateToUpload}
          >
            Analyze another file
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

interface DeviceFreeBannerProps {
  accessMode?: string;
  freeUsed?: number;
}

export const DeviceFreeBanner: React.FC<DeviceFreeBannerProps> = ({
  accessMode,
  freeUsed,
}) => {
  if (accessMode !== 'device_free') return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8 p-4 bg-primary/10 border border-primary/20 rounded-lg flex items-start gap-3"
    >
      <div className="w-5 h-5 text-primary shrink-0 mt-0.5 flex items-center justify-center rounded-full border border-primary/30 text-xs">
        i
      </div>
      <div>
        <h4 className="font-bold text-primary text-sm mb-1">
          Free check used ({freeUsed ?? 1}/2). Credits not used yet.
        </h4>
        <p className="text-slate-200 text-xs leading-relaxed">
          Sensitive identifiers hidden: exact GPS, device IDs,
          owner/contact fields, and OCR-extracted address text. Credits
          are charged after 2 free checks.
        </p>
      </div>
    </motion.div>
  );
};

interface LimitedWarningBannerProps {
  isLimited: boolean;
}

export const LimitedWarningBanner: React.FC<LimitedWarningBannerProps> = ({
  isLimited,
}) => {
  if (!isLimited) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8 p-4 bg-primary/10 border border-primary/20 rounded-lg flex items-start gap-3"
    >
      <ShieldAlert className="w-5 h-5 text-primary shrink-0 mt-0.5" />
      <div>
        <h4 className="font-bold text-primary text-sm mb-1">
          Limited report active
        </h4>
        <p className="text-slate-300 text-xs leading-relaxed">
          You are viewing a limited report. Raw IPTC and XMP data has
          been summarized or redacted. Unlock credits to view the full
          report and raw exports.
        </p>
      </div>
    </motion.div>
  );
};