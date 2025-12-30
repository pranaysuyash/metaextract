/**
 * Navigation Component
 * 
 * Provides navigation links and authentication-aware routing
 */

import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Home, FileText, User, LogOut, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

export function Navigation() {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const navItems = [
    {
      to: "/",
      label: "Home",
      icon: Home,
      public: true
    },
    {
      to: "/dashboard",
      label: "Dashboard", 
      icon: Settings,
      public: false
    },
    {
      to: "/results",
      label: "Results",
      icon: FileText,
      public: false
    }
  ];

  const handleLogout = async () => {
    await logout();
  };

  return (
    <nav className="bg-[#1a1a2e] border-b border-white/10 px-4 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo/Brand */}
        <Link to="/" className="flex items-center gap-2 text-white font-bold text-xl">
          <div className="w-8 h-8 bg-gradient-to-br from-[#6366f1] to-[#8b5cf6] rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">ME</span>
          </div>
          MetaExtract
        </Link>

        {/* Navigation Links */}
        <div className="flex items-center gap-4">
          {navItems.map((item) => {
            // Show public items always, private items only when authenticated
            if (!item.public && !isAuthenticated) return null;
            
            const isActive = location.pathname === item.to;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-[#6366f1] text-white"
                    : "text-slate-300 hover:text-white hover:bg-white/10"
                )}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Link>
            );
          })}
        </div>

        {/* User Section */}
        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <>
              {/* User Info */}
              <div className="flex items-center gap-2 text-sm">
                <div className="flex items-center gap-2 px-3 py-1 bg-white/10 rounded-lg">
                  <User className="w-4 h-4 text-slate-300" />
                  <span className="text-white font-medium">{user.username}</span>
                  <span className={cn(
                    "px-2 py-0.5 rounded text-xs font-bold",
                    user.tier === "free" && "bg-gray-600 text-white",
                    user.tier === "professional" && "bg-blue-600 text-white",
                    user.tier === "forensic" && "bg-purple-600 text-white",
                    user.tier === "enterprise" && "bg-green-600 text-white"
                  )}>
                    {user.tier.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Logout Button */}
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </>
          ) : (
            <div className="text-slate-400 text-sm">
              Not authenticated
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navigation;