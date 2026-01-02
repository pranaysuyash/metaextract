/**
 * Layout Component
 *
 * Main layout wrapper for authenticated/internal pages.
 * Uses the dark forensic theme consistent with the app design.
 *
 * For public pages (landing, pricing), use PublicLayout instead.
 */

import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { LogOut, User, Menu, X, Cpu } from 'lucide-react';
import { useState } from 'react';
import { ThemeToggle } from '@/components/theme-toggle';
import { cn } from '@/lib/utils';
import {
  dashboardNavSections,
  navStyles,
  brandConfig,
  isActivePath,
} from '@/lib/navigation-config';

interface LayoutProps {
  children?: React.ReactNode;
  /** Hide sidebar for full-width content */
  hideSidebar?: boolean;
  /** Hide header */
  hideHeader?: boolean;
}

export const Layout = ({
  children,
  hideSidebar = false,
  hideHeader = false,
}: LayoutProps) => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = dashboardNavSections.flatMap((section) => section.items);

  const isActive = (path: string) => isActivePath(location.pathname, path);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  // For public pages (landing), render without the dashboard chrome
  if (location.pathname === '/' && !isAuthenticated) {
    return <>{children ?? <Outlet />}</>;
  }

  return (
    <div className='min-h-screen bg-[#0B0C10] text-white'>
      {/* Mobile Header */}
      {!hideHeader && (
        <header className='lg:hidden fixed top-0 left-0 right-0 z-50 bg-[#0B0C10]/95 backdrop-blur-xl border-b border-white/5'>
          <div className='flex items-center justify-between px-4 h-14'>
            <Link to='/' className='flex items-center gap-2'>
              <div className='w-7 h-7 bg-primary rounded flex items-center justify-center'>
                <Cpu className='w-4 h-4 text-black' />
              </div>
              <span className='font-bold text-sm'>
                Meta<span className='text-primary'>Extract</span>
              </span>
            </Link>

            <Button
              variant='ghost'
              size='icon'
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className='text-white hover:bg-white/10'
            >
              {sidebarOpen ? (
                <X className='w-5 h-5' />
              ) : (
                <Menu className='w-5 h-5' />
              )}
            </Button>
          </div>
        </header>
      )}

      <div className='flex'>
        {/* Sidebar */}
        {!hideSidebar && (
          <>
            {/* Desktop Sidebar */}
            <aside className='hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 bg-[#0a0a0f] border-r border-white/5'>
              {/* Logo */}
              <div className='flex items-center gap-3 px-6 h-16 border-b border-white/5'>
                <div className='w-8 h-8 bg-primary rounded flex items-center justify-center'>
                  <Cpu className='w-5 h-5 text-black' />
                </div>
                <span className='font-bold text-lg tracking-tight'>
                  Meta<span className='text-primary'>Extract</span>
                </span>
              </div>

              {/* Navigation */}
              <nav className='flex-1 px-3 py-4 space-y-1 overflow-y-auto'>
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  return (
                    <Link
                      key={item.id}
                      to={item.href}
                      className={cn(
                        navStyles.item.base,
                        active ? navStyles.item.active : navStyles.item.inactive
                      )}
                      title={item.description}
                    >
                      <Icon
                        className={cn(
                          navStyles.item.icon,
                          active && navStyles.item.iconActive
                        )}
                      />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>

              {/* User Section */}
              {isAuthenticated && user && (
                <div className='p-4 border-t border-white/5'>
                  <div className='flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5'>
                    <div className='w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center'>
                      <User className='w-4 h-4 text-primary' />
                    </div>
                    <div className='flex-1 min-w-0'>
                      <p className='text-sm font-medium text-white truncate'>
                        {user.username}
                      </p>
                      <p className='text-xs text-slate-500 truncate'>
                        {user.tier}
                      </p>
                    </div>
                  </div>
                  <div className='mt-2 flex items-center justify-between'>
                    <span className='text-xs text-slate-500'>Theme</span>
                    <ThemeToggle />
                  </div>
                  <Button
                    variant='ghost'
                    size='sm'
                    onClick={handleLogout}
                    className='w-full mt-2 text-slate-400 hover:text-white hover:bg-white/5 justify-start'
                  >
                    <LogOut className='w-4 h-4 mr-2' />
                    Sign Out
                  </Button>
                </div>
              )}
            </aside>

            {/* Mobile Sidebar Overlay */}
            {sidebarOpen && (
              <div
                className='lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm'
                onClick={() => setSidebarOpen(false)}
              />
            )}

            {/* Mobile Sidebar */}
            <aside
              className={cn(
                'lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-[#0a0a0f] border-r border-white/5 transform transition-transform duration-300',
                sidebarOpen ? 'translate-x-0' : '-translate-x-full'
              )}
            >
              {/* Logo */}
              <div className='flex items-center justify-between px-4 h-14 border-b border-white/5'>
                <Link
                  to='/'
                  className='flex items-center gap-2'
                  onClick={() => setSidebarOpen(false)}
                >
                  <div className='w-7 h-7 bg-primary rounded flex items-center justify-center'>
                    <Cpu className='w-4 h-4 text-black' />
                  </div>
                  <span className='font-bold text-sm'>
                    Meta<span className='text-primary'>Extract</span>
                  </span>
                </Link>
                <Button
                  variant='ghost'
                  size='icon'
                  onClick={() => setSidebarOpen(false)}
                  className='text-white hover:bg-white/10'
                >
                  <X className='w-5 h-5' />
                </Button>
              </div>

              {/* Navigation */}
              <nav className='flex-1 px-3 py-4 space-y-1 overflow-y-auto'>
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  return (
                    <Link
                      key={item.id}
                      to={item.href}
                      onClick={() => setSidebarOpen(false)}
                      className={cn(
                        navStyles.item.base,
                        active ? navStyles.item.active : navStyles.item.inactive
                      )}
                      title={item.description}
                    >
                      <Icon
                        className={cn(
                          navStyles.item.icon,
                          active && navStyles.item.iconActive
                        )}
                      />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>

              {/* User Section */}
              {isAuthenticated && user && (
                <div className='p-4 border-t border-white/5'>
                  <div className='flex items-center gap-3 px-3 py-2 rounded-lg bg-white/5'>
                    <div className='w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center'>
                      <User className='w-4 h-4 text-primary' />
                    </div>
                    <div className='flex-1 min-w-0'>
                      <p className='text-sm font-medium text-white truncate'>
                        {user.username}
                      </p>
                      <p className='text-xs text-slate-500 truncate'>
                        {user.tier}
                      </p>
                    </div>
                  </div>
                  <div className='mt-3'>
                    <p className='text-xs text-slate-500 mb-2'>Theme</p>
                    <ThemeToggle />
                  </div>
                  <Button
                    variant='ghost'
                    size='sm'
                    onClick={() => {
                      handleLogout();
                      setSidebarOpen(false);
                    }}
                    className='w-full mt-2 text-slate-400 hover:text-white hover:bg-white/5 justify-start'
                  >
                    <LogOut className='w-4 h-4 mr-2' />
                    Sign Out
                  </Button>
                </div>
              )}
            </aside>
          </>
        )}

        {/* Main Content */}
        <main
          className={cn(
            'flex-1 min-h-screen',
            !hideSidebar && 'lg:pl-64',
            !hideHeader && 'pt-14 lg:pt-0'
          )}
        >
          {children ?? <Outlet />}
        </main>
      </div>
    </div>
  );
};

export default Layout;
