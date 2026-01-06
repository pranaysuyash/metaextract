/**
 * Navigation Configuration
 * 
 * Centralized navigation configuration for consistent navigation across all pages.
 * Defines nav items, routes, and navigation behavior.
 * 
 * @module navigation-config
 * @validates Requirements 1.6 - Navigation consistency
 */

import { 
  BarChart3, 
  Upload, 
  FileText, 
  TrendingUp, 
  Activity, 
  Shield, 
  Settings,
  Home,
  HelpCircle,
  CreditCard,
  User,
  Cpu,
  type LucideIcon
} from 'lucide-react';

// ============================================================================
// Navigation Item Types
// ============================================================================

export interface NavItem {
  /** Unique identifier */
  id: string;
  /** Display name */
  name: string;
  /** Route path */
  href: string;
  /** Lucide icon component */
  icon: LucideIcon;
  /** Whether this item requires authentication */
  requiresAuth?: boolean;
  /** Whether this item is only for public (non-authenticated) users */
  publicOnly?: boolean;
  /** Badge content (e.g., notification count) */
  badge?: string | number;
  /** Whether this is an external link */
  external?: boolean;
  /** Description for tooltips/accessibility */
  description?: string;
  /** Keyboard shortcut */
  shortcut?: string;
}

export interface NavSection {
  /** Section identifier */
  id: string;
  /** Section title (optional, for grouped navigation) */
  title?: string;
  /** Navigation items in this section */
  items: NavItem[];
}

// ============================================================================
// Public Navigation (Landing, Marketing Pages)
// ============================================================================

export const publicNavItems: NavItem[] = [
  {
    id: 'features',
    name: 'Features',
    href: '/#features',
    icon: Cpu,
    description: 'Explore our metadata extraction capabilities',
  },
  {
    id: 'pricing',
    name: 'Pricing',
    href: '/#pricing',
    icon: CreditCard,
    description: 'View pricing plans and features',
  },
  {
    id: 'docs',
    name: 'Docs',
    href: '/docs',
    icon: FileText,
    description: 'Read the documentation',
  },
];

// ============================================================================
// Dashboard Navigation (Authenticated Users)
// ============================================================================

export const dashboardNavSections: NavSection[] = [
  {
    id: 'main',
    items: [
      {
        id: 'extract',
        name: 'Extract',
        href: '/images_mvp',
        icon: Upload,
        description: 'Upload and extract metadata',
        shortcut: 'g e',
      },
      {
        id: 'credits',
        name: 'Credits',
        href: '/credits',
        icon: CreditCard,
        requiresAuth: true,
        description: 'Balances and recent transactions',
      },
      {
        id: 'results',
        name: 'Results',
        href: '/images_mvp/results',
        icon: FileText,
        requiresAuth: true,
        description: 'View extraction results',
        shortcut: 'g r',
      },
      {
        id: 'analytics',
        name: 'Analytics',
        href: '/images_mvp/analytics',
        icon: TrendingUp,
        requiresAuth: true,
        description: 'Usage analytics and insights',
      },
      {
        id: 'settings',
        name: 'Settings',
        href: '/settings',
        icon: Settings,
        requiresAuth: true,
        description: 'Account, plan, and preferences',
        shortcut: 'g s',
      },
    ],
  },
];

/** Flat list of all dashboard nav items */
export const dashboardNavItems: NavItem[] = dashboardNavSections.flatMap(
  section => section.items
);

// ============================================================================
// User Menu Items
// ============================================================================

export const userMenuItems: NavItem[] = [
  {
    id: 'profile',
    name: 'Profile',
    href: '/profile',
    icon: User,
    requiresAuth: true,
    description: 'View and edit your profile',
  },
  {
    id: 'user-settings',
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    requiresAuth: true,
    description: 'Account settings',
  },
  {
    id: 'help',
    name: 'Help',
    href: '/help',
    icon: HelpCircle,
    description: 'Get help and support',
  },
];

// ============================================================================
// Footer Navigation
// ============================================================================

export const footerNavSections: NavSection[] = [
  {
    id: 'product',
    title: 'Product',
    items: [
      { id: 'footer-features', name: 'Features', href: '/#features', icon: Cpu },
      { id: 'footer-pricing', name: 'Pricing', href: '/#pricing', icon: CreditCard },
      { id: 'footer-docs', name: 'Documentation', href: '/docs', icon: FileText },
      { id: 'footer-api', name: 'API', href: '/api', icon: Activity },
    ],
  },
  {
    id: 'company',
    title: 'Company',
    items: [
      { id: 'footer-about', name: 'About', href: '/about', icon: Home },
      { id: 'footer-blog', name: 'Blog', href: '/blog', icon: FileText },
      { id: 'footer-contact', name: 'Contact', href: '/contact', icon: HelpCircle },
    ],
  },
  {
    id: 'legal',
    title: 'Legal',
    items: [
      { id: 'footer-privacy', name: 'Privacy Policy', href: '/privacy', icon: Shield },
      { id: 'footer-terms', name: 'Terms of Service', href: '/terms', icon: FileText },
      { id: 'footer-security', name: 'Security', href: '/security', icon: Shield },
    ],
  },
];

// ============================================================================
// Navigation Utilities
// ============================================================================

/**
 * Check if a path matches the current location
 */
export function isActivePath(currentPath: string, itemPath: string): boolean {
  // Exact match
  if (currentPath === itemPath) return true;
  
  // Handle hash links
  if (itemPath.includes('#')) {
    const [basePath] = itemPath.split('#');
    return currentPath === basePath || currentPath === '/';
  }
  
  // Handle nested routes (e.g., /settings/profile matches /settings)
  if (itemPath !== '/' && currentPath.startsWith(itemPath)) {
    return true;
  }
  
  return false;
}

/**
 * Get nav item by ID
 */
export function getNavItemById(id: string): NavItem | undefined {
  return [...publicNavItems, ...dashboardNavItems, ...userMenuItems].find(
    item => item.id === id
  );
}

/**
 * Get nav items filtered by authentication state
 */
export function getFilteredNavItems(
  items: NavItem[],
  isAuthenticated: boolean
): NavItem[] {
  return items.filter(item => {
    if (item.requiresAuth && !isAuthenticated) return false;
    if (item.publicOnly && isAuthenticated) return false;
    return true;
  });
}

/**
 * Brand configuration
 */
export const brandConfig = {
  name: 'MetaExtract',
  shortName: 'M',
  tagline: 'The world\'s most comprehensive metadata extraction system.',
  logo: {
    icon: Cpu,
    bgColor: 'bg-primary',
    textColor: 'text-black',
  },
} as const;

// ============================================================================
// Navigation Styles (Dark Forensic Theme)
// ============================================================================

export const navStyles = {
  // Sidebar styles
  sidebar: {
    bg: 'bg-[#0a0a0f]',
    border: 'border-white/5',
    width: 'w-64',
  },
  
  // Header styles
  header: {
    bg: 'bg-[#0B0C10]/80',
    bgSolid: 'bg-[#0B0C10]',
    border: 'border-white/5',
    height: 'h-16',
    heightMobile: 'h-14',
  },
  
  // Nav item styles
  item: {
    base: 'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
    active: 'bg-primary/10 text-primary border border-primary/20',
    inactive: 'text-slate-400 hover:text-white hover:bg-white/5',
    icon: 'w-4 h-4',
    iconActive: 'text-primary',
  },
  
  // Link styles
  link: {
    base: 'text-sm text-slate-300 hover:text-white transition-colors',
    footer: 'text-sm text-slate-400 hover:text-white transition-colors',
  },
  
  // Button styles
  button: {
    primary: 'bg-primary hover:bg-primary/90 text-black font-medium',
    ghost: 'text-slate-300 hover:text-white hover:bg-white/10',
  },
} as const;

// ============================================================================
// Export All
// ============================================================================

export const navigationConfig = {
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
} as const;

export default navigationConfig;
