/**
 * Navigation Component
 * 
 * Consistent navigation component using the dark forensic theme.
 * Uses centralized navigation configuration for consistency across pages.
 * 
 * @validates Requirements 1.6 - Navigation consistency
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Cpu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { 
  dashboardNavSections, 
  navStyles, 
  brandConfig,
  isActivePath 
} from '@/lib/navigation-config';

interface NavigationProps {
  /** Whether to show section titles */
  showSectionTitles?: boolean;
  /** Custom class name */
  className?: string;
  /** Callback when nav item is clicked (useful for mobile menu close) */
  onNavClick?: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ 
  showSectionTitles = false,
  className,
  onNavClick 
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const handleNavClick = () => {
    setIsMobileMenuOpen(false);
    onNavClick?.();
  };

  const renderNavItems = (closeMobileMenu: boolean = false) => (
    <div className="space-y-6">
      {dashboardNavSections.map((section) => (
        <div key={section.id}>
          {showSectionTitles && section.title && (
            <h3 className="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {section.title}
            </h3>
          )}
          <div className="space-y-1">
            {section.items.map((item) => {
              const Icon = item.icon;
              const active = isActivePath(location.pathname, item.href);
              return (
                // eslint-disable-next-line jsx-a11y/anchor-is-valid
                <Link
                  key={item.id}
                  to={item.href}
                  onClick={closeMobileMenu ? handleNavClick : undefined}
                  className={cn(
                    navStyles.item.base,
                    active ? navStyles.item.active : navStyles.item.inactive
                  )}
                  title={item.description}
                  aria-current={active ? 'page' : undefined}
                >
                  <Icon className={cn(navStyles.item.icon, active && navStyles.item.iconActive)} />
                  <span>{item.name}</span>
                  {item.badge && (
                    <span className="ml-auto bg-primary/20 text-primary text-xs px-2 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <nav className={cn('h-full', navStyles.sidebar.bg, className)} role="navigation" aria-label="Main navigation">
      {/* Mobile menu button */}
      <div className="lg:hidden p-4 border-b border-white/5">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="text-white hover:bg-white/10"
          aria-expanded={isMobileMenuOpen}
          aria-controls="mobile-navigation"
          aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
        >
          {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>
      </div>

      {/* Desktop Navigation */}
      <div className="hidden lg:flex lg:flex-col lg:px-3 lg:py-4">
        {renderNavItems()}
      </div>

      {/* Mobile Navigation Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          role="button"
          tabIndex={0}
          onClick={() => setIsMobileMenuOpen(false)}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setIsMobileMenuOpen(false); }}
          aria-label="Close menu"
        />
      )}

      {/* Mobile Navigation Panel */}
      <div 
        id="mobile-navigation"
        className={cn(
          'lg:hidden fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300',
          navStyles.sidebar.bg,
          'border-r border-white/5',
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Mobile Header */}
        <div className="flex items-center justify-between px-4 h-14 border-b border-white/5">
          {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
          <Link to="/" className="flex items-center gap-2" onClick={handleNavClick}>
            <div className={cn('w-7 h-7 rounded flex items-center justify-center', brandConfig.logo.bgColor)}>
              <Cpu className={cn('w-4 h-4', brandConfig.logo.textColor)} />
            </div>
            <span className="font-bold text-sm text-white">
              Meta<span className="text-primary">Extract</span>
            </span>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsMobileMenuOpen(false)}
            className="text-white hover:bg-white/10"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Mobile Nav Items */}
        <div className="px-3 py-4 overflow-y-auto h-[calc(100%-3.5rem)]">
          {renderNavItems(true)}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;