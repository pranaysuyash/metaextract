/**
 * Public Layout Component
 * 
 * Clean layout for public-facing pages (landing, pricing, about).
 * No sidebar, minimal header with logo and auth buttons.
 * Uses the dark forensic theme consistent with the landing page design.
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/auth';
import { LogIn, UserPlus, User, LogOut, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { AuthModal } from './auth-modal';

interface PublicLayoutProps {
  children: React.ReactNode;
  /** Whether to show the header (default: true) */
  showHeader?: boolean;
  /** Whether to show the footer (default: true) */
  showFooter?: boolean;
  /** Custom header content */
  headerContent?: React.ReactNode;
}

export function PublicLayout({ 
  children, 
  showHeader = true, 
  showFooter = true,
  headerContent 
}: PublicLayoutProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<'login' | 'register'>('login');

  const openLogin = () => {
    setAuthModalMode('login');
    setAuthModalOpen(true);
  };

  const openRegister = () => {
    setAuthModalMode('register');
    setAuthModalOpen(true);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#0B0C10] text-white flex flex-col">
      {/* Header */}
      {showHeader && (
        <header className="fixed top-0 left-0 right-0 z-50 bg-[#0B0C10]/80 backdrop-blur-xl border-b border-white/5">
          <div className="container mx-auto px-4 md:px-6">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <Link to="/" className="flex items-center gap-2 group">
                <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
                  <span className="text-black font-bold text-sm">M</span>
                </div>
                <span className="font-bold text-lg tracking-tight">
                  Meta<span className="text-primary">Extract</span>
                </span>
              </Link>

              {/* Desktop Navigation */}
              <nav className="hidden md:flex items-center gap-6">
                <Link 
                  to="/#features" 
                  className="text-sm text-slate-300 hover:text-white transition-colors"
                >
                  Features
                </Link>
                <Link 
                  to="/#pricing" 
                  className="text-sm text-slate-300 hover:text-white transition-colors"
                >
                  Pricing
                </Link>
                <Link 
                  to="/docs" 
                  className="text-sm text-slate-300 hover:text-white transition-colors"
                >
                  Docs
                </Link>
              </nav>

              {/* Auth Buttons */}
              <div className="hidden md:flex items-center gap-3">
                {isAuthenticated && user ? (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate('/dashboard')}
                      className="text-slate-300 hover:text-white hover:bg-white/10"
                    >
                      <User className="w-4 h-4 mr-2" />
                      Dashboard
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleLogout}
                      className="text-slate-300 hover:text-white hover:bg-white/10"
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Logout
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={openLogin}
                      className="text-slate-300 hover:text-white hover:bg-white/10"
                      data-auth="login"
                    >
                      <LogIn className="w-4 h-4 mr-2" />
                      Sign In
                    </Button>
                    <Button
                      size="sm"
                      onClick={openRegister}
                      className="bg-primary hover:bg-primary/90 text-black font-medium"
                      data-auth="register"
                    >
                      <UserPlus className="w-4 h-4 mr-2" />
                      Get Started
                    </Button>
                  </>
                )}
              </div>

              {/* Mobile Menu Button */}
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden text-white"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden bg-[#0B0C10] border-t border-white/5">
              <div className="container mx-auto px-4 py-4 space-y-4">
                <nav className="flex flex-col gap-2">
                  {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                  <Link 
                    to="/#features" 
                    className="text-sm text-slate-300 hover:text-white py-2"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Features
                  </Link>
                  {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                  <Link 
                    to="/#pricing" 
                    className="text-sm text-slate-300 hover:text-white py-2"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Pricing
                  </Link>
                  {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                  <Link 
                    to="/docs" 
                    className="text-sm text-slate-300 hover:text-white py-2"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Docs
                  </Link>
                </nav>
                
                <div className="flex flex-col gap-2 pt-4 border-t border-white/10">
                  {isAuthenticated && user ? (
                    <>
                      <Button
                        variant="ghost"
                        onClick={() => { navigate('/dashboard'); setMobileMenuOpen(false); }}
                        className="justify-start text-slate-300 hover:text-white hover:bg-white/10"
                      >
                        <User className="w-4 h-4 mr-2" />
                        Dashboard
                      </Button>
                      <Button
                        variant="ghost"
                        onClick={() => { handleLogout(); setMobileMenuOpen(false); }}
                        className="justify-start text-slate-300 hover:text-white hover:bg-white/10"
                      >
                        <LogOut className="w-4 h-4 mr-2" />
                        Logout
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button
                        variant="ghost"
                        onClick={() => { openLogin(); setMobileMenuOpen(false); }}
                        className="justify-start text-slate-300 hover:text-white hover:bg-white/10"
                      >
                        <LogIn className="w-4 h-4 mr-2" />
                        Sign In
                      </Button>
                      <Button
                        onClick={() => { openRegister(); setMobileMenuOpen(false); }}
                        className="bg-primary hover:bg-primary/90 text-black font-medium"
                      >
                        <UserPlus className="w-4 h-4 mr-2" />
                        Get Started
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </header>
      )}

      {/* Main Content */}
      <main className={showHeader ? 'pt-16 flex-1' : 'flex-1'}>
        {headerContent}
        {children}
      </main>

      {/* Footer */}
      {showFooter && (
        <footer className="bg-[#0B0C10] border-t border-white/5 py-12">
          <div className="container mx-auto px-4 md:px-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {/* Brand */}
              <div className="space-y-4">
                <Link to="/" className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
                    <span className="text-black font-bold text-sm">M</span>
                  </div>
                  <span className="font-bold text-lg">
                    Meta<span className="text-primary">Extract</span>
                  </span>
                </Link>
                <p className="text-sm text-slate-400">
                  The world's most comprehensive metadata extraction system.
                </p>
              </div>

              {/* Product */}
              <div>
                <h4 className="font-semibold text-white mb-4">Product</h4>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li><Link to="/#features" className="hover:text-white transition-colors">Features</Link></li>
                  <li><Link to="/#pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                  <li><Link to="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
                  <li><Link to="/api" className="hover:text-white transition-colors">API</Link></li>
                </ul>
              </div>

              {/* Company */}
              <div>
                <h4 className="font-semibold text-white mb-4">Company</h4>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li><Link to="/about" className="hover:text-white transition-colors">About</Link></li>
                  <li><Link to="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                  <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                </ul>
              </div>

              {/* Legal */}
              <div>
                <h4 className="font-semibold text-white mb-4">Legal</h4>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                  <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
                  <li><Link to="/security" className="hover:text-white transition-colors">Security</Link></li>
                </ul>
              </div>
            </div>

            <div className="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-sm text-slate-500">
                © {new Date().getFullYear()} MetaExtract. All rights reserved.
              </p>
              <div className="flex items-center gap-4 text-sm text-slate-500">
                <span>Zero Data Retention</span>
                <span>•</span>
                <span>GDPR Compliant</span>
                <span>•</span>
                <span>SOC 2 Type II</span>
              </div>
            </div>
          </div>
        </footer>
      )}

      {/* Auth Modal */}
      <AuthModal 
        isOpen={authModalOpen} 
        onClose={() => setAuthModalOpen(false)}
        defaultTab={authModalMode}
      />
    </div>
  );
}

export default PublicLayout;
