/**
 * AccountMenu Component - Enhanced Version
 * 
 * Premium UX improvements:
 * - Loading skeleton for credits
 * - Low balance warning indicator
 * - Smooth animations
 * - Better hover states
 * - Tooltip for quick actions
 * - Visual hierarchy with colors
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Settings,
  CreditCard,
  Upload,
  LogOut,
  ChevronDown,
  Coins,
  Zap,
  AlertTriangle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface CreditsResponse {
  credits: number;
  tier: string;
}

const LOW_CREDIT_THRESHOLD = 10;
const CRITICAL_CREDIT_THRESHOLD = 5;

export function AccountMenu() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [credits, setCredits] = useState<number | null>(null);
  const [isLoadingCredits, setIsLoadingCredits] = useState(true);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Fetch credits balance
  useEffect(() => {
    if (!user) return;

    const fetchCredits = async () => {
      try {
        const response = await fetch('/api/images_mvp/credits/balance', {
          credentials: 'include',
        });
        if (response.ok) {
          const data: CreditsResponse = await response.json();
          setCredits(data.credits);
        }
      } catch (error) {
        console.error('Failed to fetch credits:', error);
      } finally {
        setIsLoadingCredits(false);
      }
    };

    void fetchCredits();
  }, [user]);

  if (!user) return null;

  const handleLogout = async () => {
    await logout();
    navigate('/images_mvp');
  };

  // Get user initials for avatar
  const initials = user.username
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  // Format tier display
  const tierDisplay = user.tier
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  // Credit status helpers
  const isLowCredits = credits !== null && credits <= LOW_CREDIT_THRESHOLD;
  const isCriticalCredits = credits !== null && credits <= CRITICAL_CREDIT_THRESHOLD;

  const creditsBadgeColor = isCriticalCredits
    ? 'text-red-400'
    : isLowCredits
      ? 'text-amber-400'
      : 'text-primary';

  const creditsIcon = isCriticalCredits ? (
    <AlertTriangle className="w-4 h-4 text-red-400 animate-pulse" />
  ) : isLowCredits ? (
    <AlertTriangle className="w-4 h-4 text-amber-400" />
  ) : (
    <Coins className="w-4 h-4 text-primary" />
  );

  return (
    <div className="flex items-center gap-2">
      {/* Credits Pill - Enhanced with Tooltip */}
      <TooltipProvider delayDuration={300}>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/credits')}
              className={cn(
                'hidden md:flex items-center gap-1.5 px-3 py-1.5 h-auto transition-all duration-200',
                'border hover:bg-white/10',
                isCriticalCredits
                  ? 'border-red-400/30 hover:border-red-400/50 text-red-400'
                  : isLowCredits
                    ? 'border-amber-400/30 hover:border-amber-400/50 text-amber-400'
                    : 'border-white/10 hover:border-primary/30 text-slate-200 hover:text-white'
              )}
              title={isLowCredits ? 'Low credits - Click to top up' : 'View credits'}
            >
              {creditsIcon}
              <span className={cn('font-mono text-sm font-semibold', creditsBadgeColor)}>
                {isLoadingCredits ? (
                  <span className="inline-block w-6 h-4 bg-white/10 rounded animate-pulse" />
                ) : (
                  credits !== null ? credits : '0'
                )}
              </span>
            </Button>
          </TooltipTrigger>
          <TooltipContent
            side="bottom"
            className="bg-[#0a0a0f] border-white/10 text-slate-200"
          >
            <div className="text-xs">
              {isCriticalCredits ? (
                <div className="flex items-center gap-1 text-red-400">
                  <AlertTriangle className="w-3 h-3" />
                  <span>Critical: Top up now</span>
                </div>
              ) : isLowCredits ? (
                <div className="flex items-center gap-1 text-amber-400">
                  <AlertTriangle className="w-3 h-3" />
                  <span>Running low: Add credits</span>
                </div>
              ) : (
                'Click to manage credits'
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      {/* Account Dropdown */}
      <DropdownMenu open={isDropdownOpen} onOpenChange={setIsDropdownOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className={cn(
              'flex items-center gap-2 hover:bg-white/10 px-2 py-1.5 h-auto transition-colors',
              isDropdownOpen && 'bg-white/10'
            )}
          >
            <Avatar className="h-8 w-8 ring-2 ring-white/10">
              <AvatarFallback className="bg-gradient-to-br from-primary/30 to-purple-500/30 text-primary text-sm font-bold">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="hidden md:flex flex-col items-start text-left">
              <span className="text-sm font-medium text-white leading-none">
                {user.username}
              </span>
              <span className="text-xs text-slate-400 leading-none mt-0.5">
                {tierDisplay}
              </span>
            </div>
            <ChevronDown
              className={cn(
                'w-4 h-4 text-slate-400 transition-transform duration-200',
                isDropdownOpen && 'rotate-180'
              )}
            />
          </Button>
        </DropdownMenuTrigger>

        <DropdownMenuContent
          align="end"
          className="w-64 bg-[#0a0a0f] border-white/10 shadow-xl"
          sideOffset={8}
        >
          {/* User Info Header */}
          <DropdownMenuLabel className="pb-3">
            <div className="flex items-start gap-3">
              <Avatar className="h-12 w-12 ring-2 ring-white/10">
                <AvatarFallback className="bg-gradient-to-br from-primary/30 to-purple-500/30 text-primary text-base font-bold">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white truncate">
                  {user.username}
                </p>
                <p className="text-xs text-slate-400 truncate">{user.email}</p>
                <div className="flex items-center gap-2 mt-1.5">
                  <Badge
                    variant="outline"
                    className="text-xs border-primary/30 text-primary px-2 py-0"
                  >
                    {tierDisplay}
                  </Badge>
                  {user.subscriptionStatus === 'active' && (
                    <Badge
                      variant="outline"
                      className="text-xs border-emerald-500/30 text-emerald-400 px-2 py-0"
                    >
                      <Zap className="w-2.5 h-2.5 mr-1" />
                      Active
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          </DropdownMenuLabel>

          <DropdownMenuSeparator className="bg-white/10" />

          {/* Credits Display (Mobile + Visual Enhancement) */}
          <div className="px-2 py-3 border-b border-white/10 mb-1">
            <div className="flex items-center justify-between p-2 rounded-md bg-white/5 hover:bg-white/10 transition-colors">
              <div className="flex items-center gap-2">
                {creditsIcon}
                <span className="text-sm text-slate-300 font-medium">Credits</span>
                {isLowCredits && (
                  <Badge
                    variant="outline"
                    className={cn(
                      'text-[10px] px-1.5 py-0',
                      isCriticalCredits
                        ? 'border-red-400/30 text-red-400'
                        : 'border-amber-400/30 text-amber-400'
                    )}
                  >
                    Low
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className={cn('font-mono font-bold text-base', creditsBadgeColor)}>
                  {isLoadingCredits ? (
                    <span className="inline-block w-8 h-4 bg-white/10 rounded animate-pulse" />
                  ) : (
                    credits !== null ? credits : '0'
                  )}
                </span>
                <ChevronDown className="w-3 h-3 text-slate-500 -rotate-90" />
              </div>
            </div>
          </div>

          {/* Navigation Items */}
          <DropdownMenuItem
            onClick={() => {
              setIsDropdownOpen(false);
              navigate('/images_mvp');
            }}
            className="cursor-pointer text-slate-200 hover:text-white hover:bg-white/5 focus:bg-white/5 my-0.5"
          >
            <Upload className="w-4 h-4 mr-3 text-primary" />
            <span className="font-medium">Extract Metadata</span>
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={() => {
              setIsDropdownOpen(false);
              navigate('/credits');
            }}
            className="cursor-pointer text-slate-200 hover:text-white hover:bg-white/5 focus:bg-white/5 my-0.5"
          >
            <CreditCard className="w-4 h-4 mr-3 text-emerald-400" />
            <div className="flex items-center justify-between flex-1">
              <span className="font-medium">Credits & Billing</span>
              {isLowCredits && (
                <span className="text-xs text-amber-400">Top up</span>
              )}
            </div>
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={() => {
              setIsDropdownOpen(false);
              navigate('/settings');
            }}
            className="cursor-pointer text-slate-200 hover:text-white hover:bg-white/5 focus:bg-white/5 my-0.5"
          >
            <Settings className="w-4 h-4 mr-3 text-slate-400" />
            <span className="font-medium">Settings</span>
          </DropdownMenuItem>

          <DropdownMenuSeparator className="bg-white/10 my-2" />

          <DropdownMenuItem
            onClick={handleLogout}
            className="cursor-pointer text-slate-200 hover:text-red-400 hover:bg-red-400/10 focus:bg-red-400/10 my-0.5"
          >
            <LogOut className="w-4 h-4 mr-3" />
            <span className="font-medium">Sign Out</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
