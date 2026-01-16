import { useState, useEffect } from 'react';

/**
 * Hook to detect mobile viewport based on screen width
 * Defaults to 640px breakpoint (Tailwind's sm breakpoint)
 */
export const useMobileDetection = (breakpoint = 640) => {
  const [isMobile, setIsMobile] = useState(() => {
    // Initialize state on client-side only to avoid hydration mismatch
    if (typeof window === 'undefined') return false;
    return window.innerWidth < breakpoint;
  });

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < breakpoint);
    };

    // Set initial state on mount (in case it was different from server)
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoint]);

  return { isMobile };
};