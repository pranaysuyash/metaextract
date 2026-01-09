/**
 * Dashboard Page
 * 
 * Protected dashboard showing user information and system status
 */

import React, { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  User, 
  Shield, 
  Activity, 
  FileText, 
  Upload, 
  Settings,
  CheckCircle2,
  AlertCircle,
  Clock
} from "lucide-react";
import Navigation from "@/components/navigation";

interface SystemStatus {
  server: "online" | "offline" | "checking";
  auth: "active" | "inactive" | "checking";
  processing: "ready" | "busy" | "checking";
}

export default function Dashboard() {
  const { user, isAuthenticated } = useAuth();
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    server: "checking",
    auth: "checking", 
    processing: "checking"
  });

  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      // Check server health
      const healthResponse = await fetch("/api/health");
      const serverStatus = healthResponse.ok ? "online" : "offline";

      // Check auth status
      const authResponse = await fetch("/api/auth/me");
      const authData = await authResponse.json();
      const authStatus = authData.authenticated ? "active" : "inactive";

      setSystemStatus({
        server: serverStatus,
        auth: authStatus,
        processing: "ready"
      });
    } catch (error) {
      setSystemStatus({
        server: "offline",
        auth: "inactive",
        processing: "ready"
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
      case "active":
      case "ready":
        return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case "offline":
      case "inactive":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case "busy":
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
      case "active":
      case "ready":
        return "bg-green-500/10 text-green-500 border-green-500/20";
      case "offline":
      case "inactive":
        return "bg-red-500/10 text-red-500 border-red-500/20";
      case "busy":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/20";
    }
  };

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

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-[#0B0C10]">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-64px)]">
          <Card className="bg-[#1a1a2e] border-white/10 text-white">
            <CardContent className="p-6 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold mb-2">Access Denied</h2>
              <p className="text-slate-300">Please log in to access the dashboard.</p>
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
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-slate-300">Welcome back, {user.username}! Here's your account overview.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* User Information */}
          <Card className="bg-[#1a1a2e] border-white/10 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Account Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm text-slate-300">Username</label>
                <p className="font-medium">{user.username}</p>
              </div>
              <div>
                <label className="text-sm text-slate-300">Email</label>
                <p className="font-medium">{user.email}</p>
              </div>
              <div>
                <label className="text-sm text-slate-300">Subscription Tier</label>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={`${getTierColor(user.tier)} text-white`}>
                    {user.tier.toUpperCase()}
                  </Badge>
                  <span className="text-sm text-slate-300">
                    ({user.subscriptionStatus || "active"})
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Status */}
          <Card className="bg-[#1a1a2e] border-white/10 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                System Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Server</span>
                <div className="flex items-center gap-2">
                  {getStatusIcon(systemStatus.server)}
                  <Badge className={getStatusColor(systemStatus.server)}>
                    {systemStatus.server}
                  </Badge>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Authentication</span>
                <div className="flex items-center gap-2">
                  {getStatusIcon(systemStatus.auth)}
                  <Badge className={getStatusColor(systemStatus.auth)}>
                    {systemStatus.auth}
                  </Badge>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Processing</span>
                <div className="flex items-center gap-2">
                  {getStatusIcon(systemStatus.processing)}
                  <Badge className={getStatusColor(systemStatus.processing)}>
                    {systemStatus.processing}
                  </Badge>
                </div>
              </div>
              <Button 
                onClick={checkSystemStatus}
                variant="outline" 
                size="sm" 
                className="w-full border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
              >
                Refresh Status
              </Button>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="bg-[#1a1a2e] border-white/10 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                className="w-full bg-[#6366f1] hover:bg-[#5855eb] text-white"
                onClick={() => window.location.href = "/"}
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload Files
              </Button>
              <Button 
                variant="outline" 
                className="w-full border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
                onClick={() => window.location.href = "/images_mvp/results"}
              >
                <FileText className="w-4 h-4 mr-2" />
                View Results
              </Button>
              {process.env.NODE_ENV === 'development' && (
                <Button 
                  variant="outline" 
                  className="w-full border-white/20 text-slate-200 hover:text-white hover:bg-white/10"
                  onClick={() => window.open("/api/dev/auth-test", "_blank")}
                >
                  <Shield className="w-4 h-4 mr-2" />
                  Test Authentication (Dev)
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Tier Features */}
        <Card className="bg-[#1a1a2e] border-white/10 text-white mt-6">
          <CardHeader>
            <CardTitle>Your {user.tier.charAt(0).toUpperCase() + user.tier.slice(1)} Features</CardTitle>
            <CardDescription className="text-slate-300">
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
