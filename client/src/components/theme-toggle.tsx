/**
 * Theme Toggle Component
 *
 * Provides a button to toggle between light, dark, and system themes.
 * Integrates with the ThemeProvider for consistent theme management.
 * Enhanced with accessibility features for keyboard navigation and screen readers.
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { useTheme, type ThemeMode } from '@/lib/theme-provider';
import { Moon, Sun, Monitor } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
} from '@/components/ui/dropdown-menu';

export function ThemeToggle() {
  const { mode, setMode } = useTheme();

  const getIcon = () => {
    switch (mode) {
      case 'light':
        return <Sun className='h-4 w-4' aria-hidden="true" />;
      case 'dark':
        return <Moon className='h-4 w-4' aria-hidden="true" />;
      case 'system':
        return <Monitor className='h-4 w-4' aria-hidden="true" />;
      default:
        return <Monitor className='h-4 w-4' aria-hidden="true" />;
    }
  };

  const getThemeLabel = () => {
    switch (mode) {
      case 'light':
        return 'Light theme';
      case 'dark':
        return 'Dark theme';
      case 'system':
        return 'System theme';
      default:
        return 'Theme';
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant='ghost'
          size='sm'
          className='h-8 w-8 px-0'
          aria-label={`Current theme: ${getThemeLabel()}. Toggle theme menu.`}
        >
          {getIcon()}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align='end'
        className="min-w-[160px]"
        aria-label="Theme selection menu"
      >
        <DropdownMenuRadioGroup
          value={mode}
          onValueChange={(v) => setMode(v as ThemeMode)}
        >
          <DropdownMenuRadioItem
            value="light"
            className={mode === 'light' ? 'bg-accent' : ''}
          >
            <Sun className='mr-2 h-4 w-4' aria-hidden="true" />
            Light
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem
            value="dark"
            className={mode === 'dark' ? 'bg-accent' : ''}
          >
            <Moon className='mr-2 h-4 w-4' aria-hidden="true" />
            Dark
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem
            value="system"
            className={mode === 'system' ? 'bg-accent' : ''}
          >
            <Monitor className='mr-2 h-4 w-4' aria-hidden="true" />
            System
          </DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
