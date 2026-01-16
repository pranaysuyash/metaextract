/**
 * Hook to handle keyboard interactions with toasts
 * - ESC key dismisses the most recent toast
 * - Tab navigation focuses the close button
 */

import { useEffect } from 'react';

export function useToastKeyboardHandler() {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // ESC key dismisses the most recent toast
      if (event.key === 'Escape') {
        // Find the most recent toast close button and click it
        const closeButtons = document.querySelectorAll('[toast-close]');
        if (closeButtons.length > 0) {
          const lastButton = closeButtons[
            closeButtons.length - 1
          ] as HTMLElement;
          lastButton.click();
          event.preventDefault();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
}
