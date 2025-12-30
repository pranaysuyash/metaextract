import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { ShieldCheck, Menu, Cpu, Github, Twitter, User, LogOut, ChevronDown, CreditCard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { AuthModal } from "@/components/auth-modal";
import { useAuth } from "@/lib/auth";

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState<"login" | "register">("login");
  const { user, isAuthenticated, logout, isLoading } = useAuth();

  const openLogin = () => {
    setAuthModalTab("login");
    setAuthModalOpen(true);
  };

  const openRegister = () => {
    setAuthModalTab("register");
    setAuthModalOpen(true);
  };

  const getTierBadgeColor = (tier: string) => {
    switch (tier) {
      case "professional": return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "forensic": return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      case "enterprise": return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      default: return "bg-slate-500/20 text-slate-400 border-slate-500/30";
    }
  };

  return (
    <div className="min-h-screen bg-background font-sans text-foreground flex flex-col">
      {/* Tech Grid Background Overlay */}
      <div className="fixed inset-0 bg-grid opacity-20 pointer-events-none z-0"></div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        defaultTab={authModalTab}
      />

      {/* Navbar */}
      <nav className="sticky top-0 z-50 w-full border-b border-white/5 bg-background/80 backdrop-blur-md">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/">
            <div className="flex items-center gap-2 cursor-pointer group">
              <div className="relative">
                <div className="absolute inset-0 bg-primary/20 blur-md rounded-full group-hover:bg-primary/40 transition-all"></div>
                <div className="relative bg-black border border-white/20 p-2 rounded-lg shadow-lg group-hover:border-primary/50 transition-colors">
                  <Cpu className="w-5 h-5 text-primary" />
                </div>
              </div>
              <span className="font-mono font-bold text-lg tracking-tight text-white group-hover:text-primary transition-colors">
                META<span className="text-primary">EXTRACT</span>
              </span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm font-semibold text-slate-200 hover:text-white transition-colors hover:bg-white/10 px-3 py-2 rounded-md">Capabilities</a>
            <a href="#pricing" className="text-sm font-semibold text-slate-200 hover:text-white transition-colors hover:bg-white/10 px-3 py-2 rounded-md">Pricing</a>
            <a href="#api" className="text-sm font-semibold text-slate-200 hover:text-white transition-colors hover:bg-white/10 px-3 py-2 rounded-md">API</a>
            <div className="h-4 w-px bg-white/20"></div>

            {isLoading ? (
              <div className="w-20 h-8 bg-white/5 animate-pulse rounded"></div>
            ) : isAuthenticated && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="text-slate-200 hover:text-white hover:bg-white/10 font-semibold gap-2">
                    <div className="w-7 h-7 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
                      <User className="w-4 h-4 text-primary" />
                    </div>
                    <span className="max-w-[100px] truncate">{user.username}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border font-mono ${getTierBadgeColor(user.tier)}`}>
                      {user.tier.toUpperCase()}
                    </span>
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56 bg-[#0B0C10] border border-white/10">
                  <div className="px-3 py-2 border-b border-white/5">
                    <p className="text-sm font-medium text-white">{user.username}</p>
                    <p className="text-xs text-slate-500">{user.email}</p>
                  </div>
                  <DropdownMenuItem className="text-slate-300 focus:text-white focus:bg-white/5 cursor-pointer">
                    <User className="w-4 h-4 mr-2" />
                    Account Settings
                  </DropdownMenuItem>
                  <DropdownMenuItem className="text-slate-300 focus:text-white focus:bg-white/5 cursor-pointer">
                    <CreditCard className="w-4 h-4 mr-2" />
                    Billing
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-white/5" />
                  <DropdownMenuItem
                    className="text-red-400 focus:text-red-300 focus:bg-red-500/10 cursor-pointer"
                    onClick={() => logout()}
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Sign Out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <>
                <Button
                  variant="ghost"
                  className="text-slate-200 hover:text-white hover:bg-white/10 font-semibold"
                  onClick={openLogin}
                  data-auth="login"
                >
                  Sign In
                </Button>
                <Button
                  className="bg-primary hover:bg-primary/90 text-black font-bold rounded px-6 shadow-[0_0_15px_rgba(99,102,241,0.3)] transition-all hover:shadow-[0_0_25px_rgba(99,102,241,0.5)] tracking-tight"
                  onClick={openRegister}
                  data-auth="register"
                >
                  Get Started
                </Button>
              </>
            )}
          </div>

          {/* Mobile Nav */}
          <div className="md:hidden">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="text-slate-400">
                  <Menu className="w-5 h-5" />
                </Button>
              </SheetTrigger>
              <SheetContent className="bg-card border-l-white/10">
                <div className="flex flex-col gap-4 mt-8">
                  <Link to="/"><span className="text-lg font-medium text-white">Home</span></Link>
                  <a href="#features" className="text-lg font-medium text-slate-300">Capabilities</a>
                  <a href="#pricing" className="text-lg font-medium text-slate-300">Pricing</a>
                  <a href="#api" className="text-lg font-medium text-slate-300">API</a>

                  {isAuthenticated && user ? (
                    <>
                      <div className="pt-4 border-t border-white/10">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
                            <User className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <p className="text-white font-medium">{user.username}</p>
                            <p className="text-xs text-slate-500">{user.email}</p>
                          </div>
                        </div>
                        <Button
                          variant="outline"
                          className="w-full border-red-500/30 text-red-400 hover:bg-red-500/10"
                          onClick={() => logout()}
                        >
                          <LogOut className="w-4 h-4 mr-2" />
                          Sign Out
                        </Button>
                      </div>
                    </>
                  ) : (
                    <>
                      <Button
                        variant="outline"
                        className="w-full mt-4"
                        onClick={openLogin}
                      >
                        Sign In
                      </Button>
                      <Button
                        className="w-full bg-primary text-black"
                        onClick={openRegister}
                      >
                        Get Started
                      </Button>
                    </>
                  )}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </nav>

      <main className="relative z-10 flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-black/40 py-12 mt-20 relative z-10">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-primary" />
                <span className="font-mono font-bold text-lg text-white">METAEXTRACT</span>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">
                Advanced forensic metadata extraction engine.
                Process 7000+ fields across 400+ file formats.
                Zero data retention policy.
              </p>
            </div>

            <div>
              <h4 className="font-mono font-semibold mb-4 text-white">Product</h4>
              <ul className="space-y-2 text-sm text-slate-300 font-mono">
                <li><a href="#" className="hover:text-primary transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">API Reference</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">Status</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-mono font-semibold mb-4 text-white">Legal</h4>
              <ul className="space-y-2 text-sm text-slate-300 font-mono">
                <li><a href="#" className="hover:text-primary transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">Terms & Conditions</a></li>
                <li><a href="#" className="hover:text-primary transition-colors">Payment & Refund Policy</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-mono font-semibold mb-4 text-white">Connect</h4>
              <div className="flex gap-4">
                <a href="#" className="text-slate-400 hover:text-white transition-colors"><Github className="w-5 h-5" /></a>
                <a href="#" className="text-slate-400 hover:text-white transition-colors"><Twitter className="w-5 h-5" /></a>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center text-sm text-slate-300 font-mono">
            <p>&copy; 2025 MetaExtract Inc. System Version 3.0.0</p>
            <div className="flex items-center gap-4 mt-4 md:mt-0">
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
              <span>Secure Enclave Processing</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
