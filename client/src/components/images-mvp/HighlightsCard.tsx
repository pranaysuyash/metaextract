import React from 'react';
import { MapPin, Camera, Fingerprint, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Highlight, TabValue } from '@/lib/types';

interface HighlightsCardProps {
  highlights: Highlight[];
  orderedHighlights: Highlight[];
  fieldsExtracted: number | null;
  processingMs: number | null;
  onScrollTo: (tab: TabValue, anchorId: string) => void;
}

export const HighlightsCard: React.FC<HighlightsCardProps> = ({
  highlights,
  orderedHighlights,
  fieldsExtracted,
  processingMs,
  onScrollTo,
}) => {
  const highlightIcon = (intent: 'Privacy' | 'Authenticity' | 'Photography') => {
    if (intent === 'Privacy') return <MapPin className="w-4 h-4" />;
    if (intent === 'Authenticity') return <Fingerprint className="w-4 h-4" />;
    return <Camera className="w-4 h-4" />;
  };

  const highlightAccent = (intent: 'Privacy' | 'Authenticity' | 'Photography') => {
    if (intent === 'Privacy')
      return 'border-emerald-500/20 bg-emerald-500/5 text-emerald-200';
    if (intent === 'Authenticity')
      return 'border-purple-500/20 bg-purple-500/5 text-purple-200';
    return 'border-blue-500/20 bg-blue-500/5 text-blue-200';
  };

  return (
    <Card className="bg-[#121217] border-white/5 mb-6">
      <CardHeader>
        <CardTitle className="text-sm font-mono text-slate-400">
          HIGHLIGHTS
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {orderedHighlights.slice(0, 6).map((h, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() =>
              h.target
                ? onScrollTo(h.target.tab, h.target.anchorId)
                : undefined
            }
            className={`w-full text-left flex items-start gap-3 rounded-lg border px-3 py-2 transition-colors ${highlightAccent(h.intent)} ${h.target ? 'hover:bg-white/5' : ''}`}
          >
            <div className="mt-0.5 opacity-90">{highlightIcon(h.intent)}</div>
            <div className="flex-1">
              <div className="text-sm">{h.text}</div>
              <div className="mt-2 flex flex-wrap gap-2 text-[10px] font-mono">
                <span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 text-slate-200">
                  Impact: {h.impact}
                </span>
                <span className="px-2 py-1 rounded-full bg-white/5 border border-white/10 text-slate-200">
                  Confidence: {h.confidence}
                </span>
              </div>
            </div>
          </button>
        ))}
        <div className="text-xs text-slate-500">
          Limitations: Metadata can be missing or stripped. Absence is not
          proof.
        </div>
        {(fieldsExtracted || processingMs) && (
          <div className="pt-2 text-xs text-slate-500 font-mono">
            {fieldsExtracted
              ? `${fieldsExtracted} fields extracted`
              : null}
            {fieldsExtracted && processingMs ? ' • ' : null}
            {processingMs ? `${Math.round(processingMs)} ms` : null}
          </div>
        )}
      </CardContent>
    </Card>
  );
};