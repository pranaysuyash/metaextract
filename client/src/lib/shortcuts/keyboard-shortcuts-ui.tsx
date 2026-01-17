/**
 * Keyboard Shortcuts UI
 *
 * This file contains React/JSX components for the keyboard shortcut system.
 */

import { X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import type { ShortcutGroup } from './keyboard-shortcuts';
import { shortcutManager, isMac } from './keyboard-shortcuts';

export function ShortcutHelpModal(props: { isOpen: boolean; onClose: () => void }) {
  const { isOpen, onClose } = props;
  const [groups, setGroups] = useState<ShortcutGroup[]>([]);

  useEffect(() => {
    if (isOpen) {
      setGroups(shortcutManager.getGroups());
    }
  }, [isOpen]);

  const isMacPlatform = useMemo(() => isMac(), []);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-9999 flex items-center justify-center bg-black/50 p-4">
      <div className="max-h-[80vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-white/10 bg-card">
        <div className="p-6">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white">Keyboard Shortcuts</h2>
            <button
              onClick={onClose}
              className="text-slate-400 transition-colors hover:text-white"
              aria-label="Close keyboard shortcuts"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="space-y-6">
            {groups.map(group => (
              <div
                key={group.id}
                className="border-b border-white/10 pb-6 last:border-0 last:pb-0"
              >
                <h3 className="mb-4 text-lg font-semibold text-white">{group.name}</h3>
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  {group.shortcuts.map(shortcut => (
                    <div
                      key={shortcut.id}
                      className="flex items-start justify-between rounded-lg bg-muted/20 p-3"
                    >
                      <span className="text-slate-300">{shortcut.description}</span>
                      <kbd className="rounded border border-white/20 bg-background px-2 py-1 font-mono text-sm text-white">
                        {(shortcut.combo || shortcut.key)
                          .replace('cmd', isMacPlatform ? '⌘' : 'Ctrl')
                          .replace('meta', isMacPlatform ? '⌘' : 'Win')}
                      </kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 text-center text-sm text-slate-500">
            Press{' '}
            <kbd className="rounded border border-white/20 bg-background px-2 py-1 font-mono text-xs">
              /
            </kbd>{' '}
            to open this help anytime
          </div>
        </div>
      </div>
    </div>
  );
}
