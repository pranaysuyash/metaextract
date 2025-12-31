/**
 * User Preferences Storage
 * 
 * Persist user preferences across sessions using localStorage.
 */

export interface UserPreferences {
  /** Expanded category keys in metadata explorer */
  expandedCategories?: string[];
  
  /** Preferred view mode */
  viewMode?: 'simple' | 'advanced' | 'raw';
  
  /** Show tooltips */
  showTooltips?: boolean;
  
  /** Dark mode preference */
  darkMode?: boolean;
  
  /** Dismissed onboarding */
  dismissedOnboarding?: boolean;
  
  /** Last used tier */
  lastTier?: string;
  
  /** Search history */
  searchHistory?: string[];
  
  /** Custom settings */
  [key: string]: any;
}

const STORAGE_KEY = 'metaextract_preferences';
const MAX_SEARCH_HISTORY = 10;

/**
 * Load user preferences from localStorage
 */
export function loadPreferences(): UserPreferences {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return getDefaultPreferences();
    }
    
    const parsed = JSON.parse(stored);
    return { ...getDefaultPreferences(), ...parsed };
  } catch (error) {
    console.error('Failed to load preferences:', error);
    return getDefaultPreferences();
  }
}

/**
 * Save user preferences to localStorage
 */
export function savePreferences(preferences: UserPreferences): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  } catch (error) {
    console.error('Failed to save preferences:', error);
  }
}

/**
 * Update specific preference
 */
export function updatePreference<K extends keyof UserPreferences>(
  key: K,
  value: UserPreferences[K]
): void {
  const prefs = loadPreferences();
  prefs[key] = value;
  savePreferences(prefs);
}

/**
 * Get default preferences
 */
export function getDefaultPreferences(): UserPreferences {
  return {
    expandedCategories: ['capture', 'location', 'file'], // Default to Phase 1 smart defaults
    viewMode: 'advanced',
    showTooltips: true,
    darkMode: false,
    dismissedOnboarding: false,
    searchHistory: []
  };
}

/**
 * Clear all preferences
 */
export function clearPreferences(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear preferences:', error);
  }
}

/**
 * Add search query to history
 */
export function addToSearchHistory(query: string): void {
  if (!query || query.trim().length === 0) return;
  
  const prefs = loadPreferences();
  const history = prefs.searchHistory || [];
  
  // Remove duplicates
  const filtered = history.filter(h => h !== query);
  
  // Add to front
  filtered.unshift(query);
  
  // Limit size
  prefs.searchHistory = filtered.slice(0, MAX_SEARCH_HISTORY);
  
  savePreferences(prefs);
}

/**
 * Get search history
 */
export function getSearchHistory(): string[] {
  const prefs = loadPreferences();
  return prefs.searchHistory || [];
}

/**
 * Clear search history
 */
export function clearSearchHistory(): void {
  updatePreference('searchHistory', []);
}

/**
 * Toggle expanded category
 */
export function toggleCategory(category: string): string[] {
  const prefs = loadPreferences();
  const expanded = prefs.expandedCategories || [];
  
  const newExpanded = expanded.includes(category)
    ? expanded.filter(c => c !== category)
    : [...expanded, category];
  
  updatePreference('expandedCategories', newExpanded);
  return newExpanded;
}

/**
 * Set expanded categories
 */
export function setExpandedCategories(categories: string[]): void {
  updatePreference('expandedCategories', categories);
}

/**
 * React hook for preferences (if using React)
 */
export function usePreferences() {
  const [prefs, setPrefs] = React.useState<UserPreferences>(loadPreferences);
  
  const update = React.useCallback(<K extends keyof UserPreferences>(
    key: K,
    value: UserPreferences[K]
  ) => {
    setPrefs(prev => {
      const updated = { ...prev, [key]: value };
      savePreferences(updated);
      return updated;
    });
  }, []);
  
  return { preferences: prefs, updatePreference: update };
}

// Export React if available
import React from 'react';
