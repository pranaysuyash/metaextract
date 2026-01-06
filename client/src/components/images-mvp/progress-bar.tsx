import React from 'react';
import { motion } from 'framer-motion';

interface ProgressBarProps {
  percentage: number;
  className?: string;
}

export function ProgressBar({
  percentage = 0,
  className = '',
}: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, percentage));
  const getColor = (p: number) => {
    if (p >= 80) return 'bg-green-500';
    if (p >= 60) return 'bg-yellow-500';
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
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
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
