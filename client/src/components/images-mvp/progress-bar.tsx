import React from 'react';
import { motion } from 'framer-motion';

interface ProgressBarProps {
  percentage: number;
  className?: string;
  tone?: 'auto' | 'emerald' | 'blue' | 'amber';
}

export function ProgressBar({
  percentage = 0,
  className = '',
  tone = 'auto',
}: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, percentage));
  const isIdle = pct <= 0;
  const getColor = (p: number) => {
    if (tone === 'emerald') return 'bg-emerald-500';
    if (tone === 'blue') return 'bg-blue-500';
    if (tone === 'amber') return 'bg-amber-500';
    if (p >= 80) return 'bg-emerald-500';
    if (p >= 60) return 'bg-amber-500';
    return 'bg-blue-500';
  };

  return (
    <div
      className={`relative w-full h-2 bg-white/10 rounded-full overflow-hidden ${className}`}
      role="presentation"
    >
      <motion.div
        data-testid="progress-bar-fill"
        className={`absolute left-0 top-0 h-full ${getColor(pct)}`}
        initial={{ width: 0, opacity: 0.7 }}
        animate={{
          width: `${isIdle ? 6 : pct}%`,
          opacity: isIdle ? [0.4, 0.9, 0.4] : 1,
        }}
        transition={{
          duration: isIdle ? 1.4 : 0.5,
          ease: 'easeOut',
          repeat: isIdle ? Infinity : 0,
        }}
      />

      {pct > 0 && pct < 100 && (
        <motion.div
          data-testid="progress-bar-indicator"
          className="absolute right-0 top-0 h-full w-1 bg-white/40"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      )}
    </div>
  );
}
