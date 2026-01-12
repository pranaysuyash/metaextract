import React from 'react';
import { Outlet } from 'react-router-dom';

/**
 * Dashboard Layout Component
 *
 * Provides a consistent layout structure for dashboard pages with:
 * - Responsive sidebar navigation
 * - Top navigation bar with user menu
 * - Main content area with proper spacing
 * - Mobile-friendly collapsible sidebar
 * - Breadcrumb navigation
 * - Quick actions menu
 *
 * Used by: Dashboard, Analytics, Settings, and other authenticated pages
 */

interface DashboardLayoutProps {
  children?: React.ReactNode;
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
  breadcrumbs?: Array<{ label: string; href?: string }>;
  actions?: React.ReactNode;
}

export function DashboardLayout({
  children,
  sidebar,
  header,
  breadcrumbs,
  actions,
}: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const [isMobile, setIsMobile] = React.useState(false);

  // Detect mobile viewport
  React.useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="dashboard-layout min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      {sidebar && (
        <>
          {/* Mobile overlay */}
          {isMobile && sidebarOpen && (
            <div
              className="fixed inset-0 bg-black/50 z-40"
              role="button"
              tabIndex={0}
              aria-label="Close sidebar"
              onKeyDown={e => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSidebarOpen(false);
                }
              }}
              onClick={() => setSidebarOpen(false)}
            />
          )}

          {/* Sidebar content */}
          <aside
            className={`
              fixed top-0 left-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
              transition-transform duration-300 z-50
              ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
              ${isMobile ? 'w-64' : 'w-64 md:w-72'}
            `}
          >
            <div className="h-full flex flex-col">
              {/* Sidebar header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    MetaExtract
                  </h2>
                  {isMobile && (
                    <button
                      onClick={() => setSidebarOpen(false)}
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                    >
                      <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              </div>

              {/* Sidebar content */}
              <div className="flex-1 overflow-y-auto p-4">{sidebar}</div>
            </div>
          </aside>
        </>
      )}

      {/* Main content area */}
      <div
        className={`
          transition-all duration-300
          ${sidebarOpen && !isMobile ? 'md:ml-64 lg:ml-72' : ''}
        `}
      >
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="px-4 py-3 flex items-center justify-between">
            {/* Left section - Menu toggle */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                aria-label="Toggle sidebar"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </button>

              {/* Breadcrumbs */}
              {breadcrumbs && breadcrumbs.length > 0 && (
                <nav className="flex items-center text-sm">
                  {breadcrumbs.map((crumb, index) => (
                    <React.Fragment key={index}>
                      {index > 0 && (
                        <span className="mx-2 text-gray-400">/</span>
                      )}
                      {crumb.href ? (
                        <a
                          href={crumb.href}
                          className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                        >
                          {crumb.label}
                        </a>
                      ) : (
                        <span className="text-gray-900 dark:text-white font-medium">
                          {crumb.label}
                        </span>
                      )}
                    </React.Fragment>
                  ))}
                </nav>
              )}
            </div>

            {/* Right section - Actions & Header */}
            <div className="flex items-center gap-4">
              {actions}
              {header}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 md:p-6 lg:p-8">{children || <Outlet />}</main>
      </div>
    </div>
  );
}

// Example usage:
// import { DashboardLayout } from '@/components/dashboard-layout';
//
// function DashboardPage() {
//   return (
//     <DashboardLayout
//       sidebar={<DashboardSidebar />}
//       header={<UserMenu />}
//       breadcrumbs={[
//         { label: 'Dashboard', href: '/dashboard' },
//         { label: 'Analytics' }
//       ]}
//       actions={
//         <button>New Extraction</button>
//       }
//     >
//       <YourPageContent />
//     </DashboardLayout>
//   );
// }
