import { useState, useEffect, useCallback } from 'react';

interface LazyLoadOptions {
  root?: Element | null;
  rootMargin?: string;
  threshold?: number;
}

/**
 * Custom hook for implementing lazy loading functionality
 * Can be used for components, images, or data loading
 */
export const useLazyLoad = <T,>(loader: () => Promise<T>, options?: LazyLoadOptions) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [isIntersecting, setIsIntersecting] = useState<boolean>(false);

  const executeLoader = useCallback(async () => {
    if (isIntersecting || !options) { // If no options, load immediately
      try {
        setLoading(true);
        const result = await loader();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    }
  }, [isIntersecting, loader, options]);

  useEffect(() => {
    executeLoader();
  }, [executeLoader]);

  // Set up Intersection Observer if options are provided
  useEffect(() => {
    if (!options) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true);
        }
      },
      {
        root: options.root,
        rootMargin: options.rootMargin || '0px',
        threshold: options.threshold || 0.1,
      }
    );

    // We'll return a ref function from this hook to observe elements
    return () => {
      observer.disconnect();
    };
  }, [options]);

  const reset = useCallback(() => {
    setData(null);
    setLoading(true);
    setError(null);
    setIsIntersecting(false);
    executeLoader();
  }, [executeLoader]);

  return {
    data,
    loading,
    error,
    isIntersecting,
    ref: (element: HTMLElement | null) => {
      if (element && options) {
        const observer = new IntersectionObserver(
          ([entry]) => {
            if (entry.isIntersecting) {
              setIsIntersecting(true);
            }
          },
          {
            root: options.root,
            rootMargin: options.rootMargin || '0px',
            threshold: options.threshold || 0.1,
          }
        );
        observer.observe(element);
        
        // Cleanup observer on unmount or when element changes
        return () => {
          observer.disconnect();
        };
      }
    },
    reset,
  };
};

/**
 * Hook for lazy loading images
 */
export const useLazyImage = (src: string) => {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!src) return;

    const img = new Image();
    
    img.onload = () => {
      setImageSrc(src);
      setLoading(false);
    };
    
    img.onerror = () => {
      setError(new Error(`Failed to load image: ${src}`));
      setLoading(false);
    };
    
    img.src = src;
  }, [src]);

  return {
    imageSrc,
    loading,
    error,
  };
};

/**
 * Hook for lazy loading content based on viewport visibility
 */
export const useViewportLazyLoad = (threshold: number = 0.1) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasBeenVisible, setHasBeenVisible] = useState(false);

  const ref = useCallback((node: HTMLElement | null) => {
    if (node === null) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          setHasBeenVisible(true);
        } else {
          setIsVisible(false);
        }
      },
      { threshold }
    );

    observer.observe(node);

    return () => {
      observer.disconnect();
    };
  }, [threshold]);

  return { ref, isVisible, hasBeenVisible };
};