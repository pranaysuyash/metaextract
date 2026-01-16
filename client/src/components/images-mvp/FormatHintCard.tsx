import React from 'react';
import { Info } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { FormatHint } from '@/lib/types';

interface FormatHintCardProps {
  formatHint: FormatHint | null;
}

export const FormatHintCard: React.FC<FormatHintCardProps> = ({ formatHint }) => {
  if (!formatHint) return null;

  const formatToneClass =
    formatHint.tone === 'emerald'
      ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-100'
      : 'border-amber-500/20 bg-amber-500/5 text-amber-100';

  return (
    <Card className={`mb-6 border ${formatToneClass}`}>
      <CardContent className="pt-6 flex items-start gap-3 text-sm">
        <Info className="w-5 h-5 mt-0.5" />
        <div>
          <div className="font-semibold text-white">
            {formatHint.title}
          </div>
          <div className="text-xs text-slate-300 mt-1">
            {formatHint.body}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};