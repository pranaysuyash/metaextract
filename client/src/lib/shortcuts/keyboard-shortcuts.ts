/**
 * Keyboard Shortcuts System - Global and context-aware keyboard shortcuts
 */

import { useEffect, useState, useCallback } from 'react';

export interface Shortcut {
  id: string;
  key: string; // The main key (e.g., 's', 'Enter', 'Escape')
  modifier?: 'ctrl' | 'shift' | 'alt' | 'meta' | 'cmd'; // Modifier key
  combo?: string; // Full combo string (e.g., 'Ctrl+S', 'Cmd+Shift+K')
  description: string;
  context?: string; // Context where shortcut is active (e.g., 'results-page', 'upload-zone')
  action: () => void;
  enabled?: boolean;
  scope?: 'global' | 'local'; // Whether shortcut works globally or only when element is focused
}

export interface ShortcutGroup {
  id: string;
  name: string;
  shortcuts: Shortcut[];
}

export interface ShortcutConfig {
  shortcuts: Shortcut[];
  groups: ShortcutGroup[];
  enabled: boolean;
  showHelp: boolean;
}

class KeyboardShortcutManager {
  private shortcuts: Map<string, Shortcut> = new Map();
  private activeContext: string | null = null;
  private enabled: boolean = true;
  private listeners: Array<() => void> = [];

  constructor() {
    this.init();
  }

  private init() {
    // Register global event listener
    window.addEventListener('keydown', this.handleKeyDown.bind(this));
  }

  private handleKeyDown(event: KeyboardEvent) {
    if (!this.enabled) return;

    // Build the combo string to match against registered shortcuts
    const modifier = this.getModifierFromEvent(event);
    const key = event.key.toLowerCase();
    
    // Special handling for Enter and Escape keys
    let combo = key;
    if (modifier) {
      combo = `${modifier}+${key}`;
    }

    // Look for exact match first
    const exactMatch = Array.from(this.shortcuts.values()).find(
      shortcut => shortcut.combo?.toLowerCase() === combo.toLowerCase()
    );

    if (exactMatch && this.isShortcutActive(exactMatch)) {
      event.preventDefault();
      exactMatch.action();
      return;
    }

    // Look for partial match (just key, ignoring modifier)
    const partialMatch = Array.from(this.shortcuts.values()).find(
      shortcut => shortcut.key.toLowerCase() === key.toLowerCase() && 
                 (!shortcut.modifier || this.eventHasModifier(event, shortcut.modifier))
    );

    if (partialMatch && this.isShortcutActive(partialMatch)) {
      event.preventDefault();
      partialMatch.action();
    }
  }

  private getModifierFromEvent(event: KeyboardEvent): string | null {
    if (event.ctrlKey) return 'ctrl';
    if (event.shiftKey) return 'shift';
    if (event.altKey) return 'alt';
    if (event.metaKey) return 'meta'; // Cmd on Mac, Windows key on PC
    return null;
  }

  private eventHasModifier(event: KeyboardEvent, expected: string): boolean {
    switch (expected) {
      case 'ctrl': return event.ctrlKey;
      case 'shift': return event.shiftKey;
      case 'alt': return event.altKey;
      case 'meta': return event.metaKey;
      case 'cmd': return event.metaKey; // Cmd is meta on Mac
      default: return false;
    }
  }

  private isShortcutActive(shortcut: Shortcut): boolean {
    // Check if shortcut is enabled
    if (shortcut.enabled === false) return false;

    // Check if shortcut context matches active context
    if (shortcut.context && shortcut.context !== this.activeContext) {
      return false;
    }

    return true;
  }

  /**
   * Register a new shortcut
   */
  register(shortcut: Shortcut): () => void {
    // Generate combo if not provided
    if (!shortcut.combo) {
      shortcut.combo = this.buildComboString(shortcut);
    }

    // Generate ID if not provided
    if (!shortcut.id) {
      shortcut.id = `shortcut-${shortcut.combo}`;
    }

    this.shortcuts.set(shortcut.id, shortcut);

    // Return unregister function
    return () => {
      this.shortcuts.delete(shortcut.id);
    };
  }

  /**
   * Build combo string from shortcut definition
   */
  private buildComboString(shortcut: Shortcut): string {
    if (shortcut.combo) return shortcut.combo;

    let combo = shortcut.key.toLowerCase();
    if (shortcut.modifier) {
      combo = `${shortcut.modifier}+${combo}`;
    }

    return combo;
  }

  /**
   * Set the active context for context-aware shortcuts
   */
  setActiveContext(context: string | null) {
    this.activeContext = context;
    this.notifyListeners();
  }

  /**
   * Get the active context
   */
  getActiveContext(): string | null {
    return this.activeContext;
  }

  /**
   * Enable/disable shortcut system
   */
  setEnabled(enabled: boolean) {
    this.enabled = enabled;
  }

  /**
   * Get all registered shortcuts
   */
  getShortcuts(context?: string): Shortcut[] {
    const allShortcuts = Array.from(this.shortcuts.values());
    
    if (context) {
      return allShortcuts.filter(shortcut => 
        !shortcut.context || shortcut.context === context
      );
    }

    return allShortcuts;
  }

  /**
   * Get shortcuts by group
   */
  getShortcutsByGroup(groupId: string): Shortcut[] {
    const group = this.groups.find(g => g.id === groupId);
    if (!group) return [];

    return group.shortcuts.map(id => this.shortcuts.get(id)).filter(Boolean) as Shortcut[];
  }

  /**
   * Toggle help modal visibility
   */
  setShowHelp(show: boolean) {
    this.showHelp = show;
    this.notifyListeners();
  }

  /**
   * Get shortcut help configuration
   */
  getHelpConfig(): ShortcutConfig {
    return {
      shortcuts: this.getShortcuts(),
      groups: this.groups,
      enabled: this.enabled,
      showHelp: this.showHelp
    };
  }

  /**
   * Add a listener for shortcut changes
   */
  subscribe(listener: () => void): () => void {
    this.listeners.push(listener);
    
    return () => {
      const index = this.listeners.indexOf(listener);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener());
  }

  /**
   * Get all shortcut groups
   */
  getGroups(): ShortcutGroup[] {
    return this.groups;
  }

  /**
   * Add a new shortcut group
   */
  addGroup(group: ShortcutGroup) {
    this.groups.push(group);
  }

  // Predefined shortcut groups
  private groups: ShortcutGroup[] = [
    {
      id: 'global',
      name: 'Global Shortcuts',
      shortcuts: [
        {
          id: 'global-search',
          key: 'k',
          modifier: 'cmd',
          description: 'Open global search',
          action: () => {
            // In a real app, this would open the search modal
            console.log('Opening global search...');
          },
          scope: 'global'
        },
        {
          id: 'global-help',
          key: '/',
          description: 'Show keyboard shortcuts help',
          action: () => {
            this.setShowHelp(true);
          },
          scope: 'global'
        },
        {
          id: 'global-dashboard',
          key: 'd',
          modifier: 'cmd',
          description: 'Go to dashboard',
          action: () => {
            window.location.href = '/dashboard';
          },
          scope: 'global'
        }
      ]
    },
    {
      id: 'results',
      name: 'Results Page',
      shortcuts: [
        {
          id: 'results-export-json',
          key: 'e',
          modifier: 'cmd',
          description: 'Export results as JSON',
          context: 'results-page',
          action: () => {
            // Export functionality would go here
            console.log('Exporting results as JSON...');
          },
          scope: 'local'
        },
        {
          id: 'results-export-pdf',
          key: 'p',
          modifier: 'cmd',
          description: 'Export results as PDF',
          context: 'results-page',
          action: () => {
            // Export functionality would go here
            console.log('Exporting results as PDF...');
          },
          scope: 'local'
        },
        {
          id: 'results-toggle-sidebar',
          key: 's',
          modifier: 'cmd',
          description: 'Toggle sidebar',
          context: 'results-page',
          action: () => {
            // Toggle sidebar functionality
            console.log('Toggling sidebar...');
          },
          scope: 'local'
        },
        {
          id: 'results-next-file',
          key: 'ArrowRight',
          description: 'Navigate to next file',
          context: 'results-page',
          action: () => {
            // Navigate to next file
            console.log('Navigating to next file...');
          },
          scope: 'local'
        },
        {
          id: 'results-prev-file',
          key: 'ArrowLeft',
          description: 'Navigate to previous file',
          context: 'results-page',
          action: () => {
            // Navigate to previous file
            console.log('Navigating to previous file...');
          },
          scope: 'local'
        }
      ]
    },
    {
      id: 'upload',
      name: 'Upload Zone',
      shortcuts: [
        {
          id: 'upload-focus',
          key: 'u',
          modifier: 'cmd',
          description: 'Focus upload zone',
          context: 'upload-page',
          action: () => {
            // Focus the upload zone
            const uploadZone = document.querySelector('#upload-zone');
            if (uploadZone) {
              (uploadZone as HTMLElement).focus();
            }
          },
          scope: 'local'
        },
        {
          id: 'upload-clear',
          key: 'Escape',
          description: 'Clear all files',
          context: 'upload-page',
          action: () => {
            // Clear all files functionality
            console.log('Clearing all files...');
          },
          scope: 'local'
        }
      ]
    }
  ];

  // State for help modal
  private showHelp: boolean = false;
}

// Create singleton instance
export const shortcutManager = new KeyboardShortcutManager();

// React hook for using shortcuts in components
export function useKeyboardShortcuts(
  shortcuts: Omit<Shortcut, 'id' | 'combo'>[],
  deps: any[] = []
) {
  useEffect(() => {
    const unregisterFunctions = shortcuts.map(shortcut => {
      // Generate a unique ID based on the action function and key combo
      const id = `shortcut-${shortcut.key}-${shortcut.modifier || 'none'}-${shortcut.context || 'global'}`;
      const combo = shortcut.modifier ? `${shortcut.modifier}+${shortcut.key}` : shortcut.key;
      
      return shortcutManager.register({
        ...shortcut,
        id,
        combo
      });
    });

    // Cleanup function to unregister shortcuts when component unmounts
    return () => {
      unregisterFunctions.forEach(unregister => unregister());
    };
  }, deps);
}

// React hook for managing context
export function useKeyboardContext(context: string) {
  useEffect(() => {
    shortcutManager.setActiveContext(context);

    return () => {
      // Reset context when component unmounts
      shortcutManager.setActiveContext(null);
    };
  }, [context]);
}

// React component for shortcut help modal
export const ShortcutHelpModal: React.FC<{ 
  isOpen: boolean; 
  onClose: () => void 
}> = ({ isOpen, onClose }) => {
  const [groups, setGroups] = useState<ShortcutGroup[]>([]);

  useEffect(() => {
    if (isOpen) {
      setGroups(shortcutManager.getGroups());
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] bg-black/50 flex items-center justify-center p-4">
      <div className="bg-card rounded-xl border border-white/10 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Keyboard Shortcuts</h2>
            <button 
              onClick={onClose}
              className="text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="space-y-6">
            {groups.map(group => (
              <div key={group.id} className="border-b border-white/10 pb-6 last:border-0 last:pb-0">
                <h3 className="text-lg font-semibold text-white mb-4">{group.name}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {group.shortcuts.map(shortcut => (
                    <div key={shortcut.id} className="flex items-start justify-between p-3 bg-muted/20 rounded-lg">
                      <span className="text-slate-300">{shortcut.description}</span>
                      <kbd className="px-2 py-1 bg-background border border-white/20 rounded text-sm font-mono text-white">
                        {shortcut.combo?.replace('cmd', isMac ? '⌘' : 'Ctrl')}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 text-center text-sm text-slate-500">
            Press <kbd className="px-2 py-1 bg-background border border-white/20 rounded text-xs font-mono">/</kbd> to open this help anytime
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to check if user is on Mac
export function isMac(): boolean {
  return navigator.platform.toUpperCase().indexOf('MAC') >= 0;
}

// Export the manager
export default shortcutManager;