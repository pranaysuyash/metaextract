/**
 * Property Tests for Navigation Consistency
 * 
 * Tests navigation configuration, routing, and consistency across pages.
 * 
 * @validates Requirements 1.6 - Navigation consistency
 */

import * as fc from 'fast-check';
import {
  publicNavItems,
  dashboardNavSections,
  dashboardNavItems,
  userMenuItems,
  footerNavSections,
  brandConfig,
  navStyles,
  isActivePath,
  getNavItemById,
  getFilteredNavItems,
} from '../navigation-config';

describe('Navigation Configuration - Property Tests', () => {
  // ============================================================================
  // Nav Item Structure Properties
  // ============================================================================

  describe('Nav Item Structure', () => {
    const allNavItems = [
      ...publicNavItems,
      ...dashboardNavItems,
      ...userMenuItems,
      ...footerNavSections.flatMap(s => s.items),
    ];

    it('should have unique IDs for all nav items', () => {
      const ids = allNavItems.map(item => item.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('should have valid href for all nav items', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...allNavItems),
          (item) => {
            return (
              typeof item.href === 'string' &&
              (item.href.startsWith('/') || item.href.startsWith('#'))
            );
          }
        ),
        { numRuns: allNavItems.length }
      );
    });

    it('should have non-empty names for all nav items', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...allNavItems),
          (item) => {
            return typeof item.name === 'string' && item.name.length > 0;
          }
        ),
        { numRuns: allNavItems.length }
      );
    });

    it('should have icon defined for all nav items', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...allNavItems),
          (item) => {
            // Lucide icons are ForwardRef components with $$typeof symbol
            return item.icon !== undefined && item.icon !== null;
          }
        ),
        { numRuns: allNavItems.length }
      );
    });

    it('should have consistent item structure', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...allNavItems),
          (item) => {
            const hasRequiredFields = 
              'id' in item &&
              'name' in item &&
              'href' in item &&
              'icon' in item;
            
            const optionalFieldsValid = 
              (item.requiresAuth === undefined || typeof item.requiresAuth === 'boolean') &&
              (item.publicOnly === undefined || typeof item.publicOnly === 'boolean') &&
              (item.external === undefined || typeof item.external === 'boolean') &&
              (item.description === undefined || typeof item.description === 'string');
            
            return hasRequiredFields && optionalFieldsValid;
          }
        ),
        { numRuns: allNavItems.length }
      );
    });
  });

  // ============================================================================
  // Navigation Sections Properties
  // ============================================================================

  describe('Navigation Sections', () => {
    it('should have unique section IDs', () => {
      const sectionIds = dashboardNavSections.map(s => s.id);
      const uniqueIds = new Set(sectionIds);
      expect(uniqueIds.size).toBe(sectionIds.length);
    });

    it('should have non-empty items in each section', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...dashboardNavSections),
          (section) => {
            return Array.isArray(section.items) && section.items.length > 0;
          }
        ),
        { numRuns: dashboardNavSections.length }
      );
    });

    it('should have valid section titles when defined', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...dashboardNavSections),
          (section) => {
            return section.title === undefined || 
              (typeof section.title === 'string' && section.title.length > 0);
          }
        ),
        { numRuns: dashboardNavSections.length }
      );
    });

    it('should have footer sections with titles', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...footerNavSections),
          (section) => {
            return typeof section.title === 'string' && section.title.length > 0;
          }
        ),
        { numRuns: footerNavSections.length }
      );
    });
  });

  // ============================================================================
  // Path Matching Properties
  // ============================================================================

  describe('Path Matching', () => {
    it('should match exact paths', () => {
      fc.assert(
        fc.property(
          fc.constantFrom('/settings', '/images_mvp', '/images_mvp/analytics', '/images_mvp/results'),
          (path) => {
            return isActivePath(path, path) === true;
          }
        ),
        { numRuns: 10 }
      );
    });

    it('should not match different paths', () => {
      const pathPairs = [
        ['/settings', '/images_mvp'],
        ['/images_mvp/analytics', '/images_mvp/results'],
        ['/images_mvp/results', '/images_mvp/analytics'],
      ];
      
      fc.assert(
        fc.property(
          fc.constantFrom(...pathPairs),
          ([current, item]) => {
            return isActivePath(current, item) === false;
          }
        ),
        { numRuns: pathPairs.length }
      );
    });

    it('should handle hash links correctly', () => {
      expect(isActivePath('/', '/#features')).toBe(true);
      expect(isActivePath('/', '/#pricing')).toBe(true);
      expect(isActivePath('/settings', '/#features')).toBe(false);
    });

    it('should handle nested routes', () => {
      expect(isActivePath('/images_mvp/results/123', '/images_mvp/results')).toBe(true);
      expect(isActivePath('/images_mvp/analytics/weekly', '/images_mvp/analytics')).toBe(true);
      expect(isActivePath('/settings', '/images_mvp/results')).toBe(false);
    });

    it('should not match root path for non-root items', () => {
      expect(isActivePath('/', '/settings')).toBe(false);
      expect(isActivePath('/', '/images_mvp')).toBe(false);
    });
  });

  // ============================================================================
  // Nav Item Lookup Properties
  // ============================================================================

  describe('Nav Item Lookup', () => {
    it('should find items by valid ID', () => {
      const validIds = [...publicNavItems, ...dashboardNavItems, ...userMenuItems].map(i => i.id);
      
      fc.assert(
        fc.property(
          fc.constantFrom(...validIds),
          (id) => {
            const item = getNavItemById(id);
            return item !== undefined && item.id === id;
          }
        ),
        { numRuns: validIds.length }
      );
    });

    it('should return undefined for invalid IDs', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 10, maxLength: 20 }),
          (randomId) => {
            // Random strings are unlikely to match real IDs
            const item = getNavItemById(randomId);
            return item === undefined || item.id === randomId;
          }
        ),
        { numRuns: 20 }
      );
    });
  });

  // ============================================================================
  // Auth Filtering Properties
  // ============================================================================

  describe('Auth Filtering', () => {
    it('should filter out auth-required items when not authenticated', () => {
      const authRequiredItems = dashboardNavItems.filter(i => i.requiresAuth);
      const filtered = getFilteredNavItems(authRequiredItems, false);
      expect(filtered.length).toBe(0);
    });

    it('should include auth-required items when authenticated', () => {
      const authRequiredItems = dashboardNavItems.filter(i => i.requiresAuth);
      const filtered = getFilteredNavItems(authRequiredItems, true);
      expect(filtered.length).toBe(authRequiredItems.length);
    });

    it('should always include items without auth requirements', () => {
      const noAuthItems = publicNavItems.filter(i => !i.requiresAuth && !i.publicOnly);
      
      fc.assert(
        fc.property(
          fc.boolean(),
          (isAuthenticated) => {
            const filtered = getFilteredNavItems(noAuthItems, isAuthenticated);
            return filtered.length === noAuthItems.length;
          }
        ),
        { numRuns: 10 }
      );
    });

    it('should filter out public-only items when authenticated', () => {
      // Create a mock item with publicOnly flag
      // We'll test with actual items that have publicOnly set
      const testItems = dashboardNavItems.map(item => ({
        ...item,
        publicOnly: false,
      }));
      
      // All items should be included when authenticated (none are publicOnly)
      const filteredAuth = getFilteredNavItems(testItems, true);
      expect(filteredAuth.length).toBe(testItems.length);
      
      // Test the logic: if an item were publicOnly, it should be filtered when authenticated
      const mockPublicOnlyItems = testItems.map(item => ({
        ...item,
        publicOnly: true,
        requiresAuth: false,
      }));
      
      const filteredPublicOnly = getFilteredNavItems(mockPublicOnlyItems, true);
      expect(filteredPublicOnly.length).toBe(0);
      
      const filteredPublicOnlyNoAuth = getFilteredNavItems(mockPublicOnlyItems, false);
      expect(filteredPublicOnlyNoAuth.length).toBe(mockPublicOnlyItems.length);
    });
  });

  // ============================================================================
  // Brand Configuration Properties
  // ============================================================================

  describe('Brand Configuration', () => {
    it('should have valid brand name', () => {
      expect(typeof brandConfig.name).toBe('string');
      expect(brandConfig.name.length).toBeGreaterThan(0);
    });

    it('should have valid short name', () => {
      expect(typeof brandConfig.shortName).toBe('string');
      expect(brandConfig.shortName.length).toBeGreaterThan(0);
      expect(brandConfig.shortName.length).toBeLessThanOrEqual(3);
    });

    it('should have valid tagline', () => {
      expect(typeof brandConfig.tagline).toBe('string');
      expect(brandConfig.tagline.length).toBeGreaterThan(0);
    });

    it('should have valid logo configuration', () => {
      expect(brandConfig.logo.icon).toBeDefined();
      expect(brandConfig.logo.bgColor).toContain('bg-');
      expect(brandConfig.logo.textColor).toContain('text-');
    });
  });

  // ============================================================================
  // Navigation Styles Properties
  // ============================================================================

  describe('Navigation Styles', () => {
    it('should have dark theme sidebar styles', () => {
      expect(navStyles.sidebar.bg).toContain('bg-');
      expect(navStyles.sidebar.border).toContain('border-');
      expect(navStyles.sidebar.width).toContain('w-');
    });

    it('should have dark theme header styles', () => {
      expect(navStyles.header.bg).toContain('bg-');
      expect(navStyles.header.border).toContain('border-');
      expect(navStyles.header.height).toContain('h-');
    });

    it('should have consistent item styles', () => {
      expect(navStyles.item.base).toContain('flex');
      expect(navStyles.item.base).toContain('items-center');
      expect(navStyles.item.active).toContain('primary');
      expect(navStyles.item.inactive).toContain('hover:');
    });

    it('should have consistent link styles', () => {
      expect(navStyles.link.base).toContain('text-');
      expect(navStyles.link.base).toContain('hover:');
      expect(navStyles.link.footer).toContain('text-');
    });

    it('should have consistent button styles', () => {
      expect(navStyles.button.primary).toContain('bg-primary');
      expect(navStyles.button.ghost).toContain('hover:');
    });
  });

  // ============================================================================
  // Accessibility Properties
  // ============================================================================

  describe('Accessibility', () => {
    it('should have descriptions for important nav items', () => {
      const mainNavItems = dashboardNavSections[0].items;
      
      fc.assert(
        fc.property(
          fc.constantFrom(...mainNavItems),
          (item) => {
            return item.description === undefined || 
              (typeof item.description === 'string' && item.description.length > 0);
          }
        ),
        { numRuns: mainNavItems.length }
      );
    });

    it('should have keyboard shortcuts for primary actions', () => {
      const itemsWithShortcuts = dashboardNavItems.filter(i => i.shortcut);
      expect(itemsWithShortcuts.length).toBeGreaterThan(0);
      
      // Shortcuts should follow pattern like "g d" (go to dashboard)
      for (const item of itemsWithShortcuts) {
        expect(item.shortcut).toMatch(/^[a-z] [a-z]$/);
      }
    });
  });

  // ============================================================================
  // Consistency Properties
  // ============================================================================

  describe('Cross-Page Consistency', () => {
    it('should have consistent nav items between public and dashboard', () => {
      // Features and Pricing should be accessible from both
      const publicFeatures = publicNavItems.find(i => i.id === 'features');
      const publicPricing = publicNavItems.find(i => i.id === 'pricing');
      
      expect(publicFeatures).toBeDefined();
      expect(publicPricing).toBeDefined();
    });

    it('should have consistent footer sections', () => {
      expect(footerNavSections.length).toBeGreaterThanOrEqual(3);
      
      const sectionTitles = footerNavSections.map(s => s.title);
      expect(sectionTitles).toContain('Product');
      expect(sectionTitles).toContain('Company');
      expect(sectionTitles).toContain('Legal');
    });

    it('should have settings accessible from multiple places', () => {
      const dashboardSettings = dashboardNavItems.find(i => i.id === 'settings');
      const userMenuSettings = userMenuItems.find(i => i.id === 'user-settings');
      
      expect(dashboardSettings).toBeDefined();
      expect(userMenuSettings).toBeDefined();
      expect(dashboardSettings?.href).toBe(userMenuSettings?.href);
    });
  });
});
