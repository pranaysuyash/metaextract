/**
 * Settings Page
 *
 * Account, subscription, and preference management for authenticated users.
 */

import React from "react";
import { useAuth } from "@/lib/auth";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  User, 
  CreditCard,
  Shield,
  LogOut,
  Upload,
  BarChart3,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import Navigation from "@/components/navigation";

export default function DashboardImproved() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const getTierColor = (tier: string) => {
    switch (tier) {
      case "free":
        return "bg-gray-600";
      case "professional":
        return "bg-blue-600";
      case "forensic":
        return "bg-purple-600";
      case "enterprise":
        return "bg-green-600";
      default:
        return "bg-gray-600";
    }
  };

  const getTierFeatures = (tier: string) => {
    switch (tier) {
      case "professional":
        return [
          "Advanced metadata extraction",
          "Batch processing",
          "Export capabilities",
          "Priority support"
        ];
      case "forensic":
        return [
          "All Professional features",
          "Forensic analysis tools",
          "Timeline reconstruction",
          "Evidence reporting"
        ];
      case "enterprise":
        return [
          "All Forensic features",
          "API access",
          "Custom integrations",
          "Dedicated support"
        ];
      default:
        return [
          "Basic metadata extraction",
          "Single file processing",
          "Standard formats"
        ];
    }
  };

  const handleNavigate = (path: string) => {
    navigate(path, { replace: false });
  };

  const handleLogout = async () => {
    await logout();
    navigate('/', { replace: true });
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-64px)]">
          <Card className="bg-[#1a1a2e] border-white/10 text-white">
            <CardContent className="p-6 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold mb-2">Access Denied</h2>
              <p className="text-slate-400">Please log in to access settings.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0C10]">
      <Navigation />
      
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
          <p className="text-slate-400">Manage your account, subscription, and preferences.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* User Information */}
          <Card className="bg-[#1a1a2e] border-white/10 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Account
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm text-slate-400">Username</label>
                <p className="font-medium">{user.username}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Email</label>
                <p className="font-medium">{user.email}</p>
              </div>
              <div>
                <label className="text-sm text-slate-400">Subscription Tier</label>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={`${getTierColor(user.tier)} text-white`}>
                    {user.tier.toUpperCase()}
                  </Badge>
                  <span className="text-sm text-slate-400">
                    ({user.subscriptionStatus || "active"})
                  </span>
                </div>
              </div>
              <div className="flex flex-col gap-2 pt-2">
                <Button
                  variant="outline"
                  className="border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
                  onClick={() => handleNavigate('/images_mvp')}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Start New Extraction
                </Button>
                <Button
                  variant="ghost"
                  className="justify-start text-slate-400 hover:text-white hover:bg-white/10"
                  onClick={handleLogout}
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Plan & Credits */}
          <Card className="bg-[#1a1a2e] border-white/10 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="w-5 h-5" />
                Plan & Credits
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Current Plan</span>
                <Badge className={`${getTierColor(user.tier)} text-white`}>
                  {user.tier.toUpperCase()}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Status</span>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-green-400">
                    {user.subscriptionStatus || "active"}
                  </span>
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <Button
                  variant="outline"
                  className="w-full border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
                  onClick={() => handleNavigate('/#pricing')}
                >
                  View Pricing & Credits
                </Button>
                <Button
                  variant="outline"
                  className="w-full border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
                  onClick={() => handleNavigate('/images_mvp/analytics')}
                >
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Usage Analytics
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Security */}
          <Card className="bg-[#1a1a2e] border-white/10 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Security
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-sm text-slate-400">
                Security controls are coming soon. For now, you can sign out and manage your plan.
              </div>
              <Button
                variant="outline"
                className="w-full border-white/20 text-slate-400"
                disabled
              >
                Change Password
              </Button>
              <Button
                variant="outline"
                className="w-full border-white/20 text-slate-400"
                disabled
              >
                Manage Devices
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Tier Features */}
        <Card className="bg-[#1a1a2e] border-white/10 text-white mt-6">
          <CardHeader>
            <CardTitle>Your {user.tier.charAt(0).toUpperCase() + user.tier.slice(1)} Features</CardTitle>
            <CardDescription className="text-slate-400">
              Features available with your current subscription tier
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {getTierFeatures(user.tier).map((feature, index) => (
                <div key={index} className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
