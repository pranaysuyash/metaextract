import React, { useRef, useState, useEffect } from "react";
import { Layout } from "@/components/layout";
import { EnhancedUploadZone } from "@/components/enhanced-upload-zone";
import { PRICING_TIERS, CREDIT_PACKS, CREDIT_EXPLANATION } from "@/lib/mockData";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Database, Lock, Globe, Info, MoveRight, ScanLine, Terminal, Cpu, Share2, FileCode, ShieldAlert, Zap, CheckCircle2, Loader2, Coins, User, LogIn, UserPlus } from "lucide-react";
import { motion, useScroll, useTransform, useSpring } from "framer-motion";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import generatedBackground from '@assets/generated_images/chaotic_dark_forensic_data_visualization_with_connecting_lines.png';
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/lib/auth";

function getSessionId(): string {
  let sessionId = localStorage.getItem("metaextract_session_id");
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem("metaextract_session_id", sessionId);
  }
  return sessionId;
}

// Custom hook for mouse parallax
function useParallax(sensitivity = 20) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPosition({
        x: (e.clientX - window.innerWidth / 2) / sensitivity,
        y: (e.clientY - window.innerHeight / 2) / sensitivity,
      });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, [sensitivity]);

  return position;
}

export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null);
  const parallax = useParallax(30);
  const parallaxBg = useParallax(80);
  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
  const [creditPackLoading, setCreditPackLoading] = useState<string | null>(null);
  const { toast } = useToast();
  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading } = useAuth();

  const handleUploadResults = (results: any[]) => {
    if (results.length > 0) {
      // Store the first result in session storage and navigate to results
      sessionStorage.setItem('currentMetadata', JSON.stringify(results[0]));
      navigate('/results');
    }
  };

  const handleCreditPurchase = async (packName: string) => {
    const packKey = packName.toLowerCase() as "single" | "batch" | "bulk";
    setCreditPackLoading(packKey);

    try {
      const sessionId = getSessionId();
      const response = await fetch("/api/credits/purchase", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pack: packKey, sessionId }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to create checkout session");
      }

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error("No checkout URL received");
      }
    } catch (error) {
      toast({
        title: "Checkout Error",
        description: error instanceof Error ? error.message : "Failed to start checkout",
        variant: "destructive",
      });
    } finally {
      setCreditPackLoading(null);
    }
  };

  const handleCheckout = async (tier: string) => {
    if (tier === "free") {
      document.getElementById("enhanced-upload")?.scrollIntoView({ behavior: 'smooth' });
      return;
    }

    setCheckoutLoading(tier);
    try {
      const response = await fetch("/api/checkout/create-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to create checkout session");
      }

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error("No checkout URL received");
      }
    } catch (error) {
      toast({
        title: "Checkout Error",
        description: error instanceof Error ? error.message : "Failed to start checkout",
        variant: "destructive",
      });
    } finally {
      setCheckoutLoading(null);
    }
  };

  return (
    <Layout>
      <div ref={containerRef} className="relative min-h-[200vh] bg-[#0B0C10] overflow-hidden selection:bg-primary/30">

        {/* Global animated background elements */}
        <div className="fixed inset-0 z-0 pointer-events-none">
          <motion.div
            style={{ x: parallaxBg.x, y: parallaxBg.y }}
            className="absolute inset-0 opacity-20"
          >
            <img
              src={generatedBackground}
              alt="Background"
              className="w-full h-full object-cover mix-blend-screen scale-110"
            />
          </motion.div>
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay"></div>

          {/* Floating data shards */}
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute border border-white/5 bg-black/40 backdrop-blur-sm p-4 font-mono text-[10px] text-primary/60"
              style={{
                top: `${Math.random() * 80 + 10}%`,
                left: `${Math.random() * 80 + 10}%`,
                rotate: `${Math.random() * 20 - 10}deg`
              }}
              animate={{
                y: [0, -20, 0],
                opacity: [0.3, 0.6, 0.3]
              }}
              transition={{
                duration: 5 + Math.random() * 5,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              0x{Math.floor(Math.random() * 16777215).toString(16).toUpperCase()} // SEGMENT_{i}
            </motion.div>
          ))}
        </div>

        {/* SECTION 1: HERO */}
        <section className="relative min-h-screen flex flex-col justify-center px-6 md:px-20 z-10 pt-20">
          <div className="max-w-[1400px] mx-auto w-full grid grid-cols-1 md:grid-cols-12 gap-8 items-center">

            {/* Left text block */}
            <div className="md:col-span-7 relative">
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                className="relative z-20"
              >

                <h1 className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl font-bold text-white tracking-tight leading-tight mb-6">
                  Extract forensic metadata <span className="text-primary">competitors miss.</span>
                </h1>

                <p className="text-base md:text-lg lg:text-xl text-slate-300 max-w-xl leading-relaxed mb-8">
                  Courts, journalists, and security teams trust MetaExtract to uncover 7,000+ hidden fields, detect manipulation, and preserve digital evidence.
                </p>

                <div className="flex flex-wrap gap-4 items-center mb-12">
                  <div className="flex items-center gap-2 text-sm text-slate-200">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Canon MakerNotes</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-200">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Sony Encrypted Data</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-slate-200">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Photoshop History</span>
                  </div>
                </div>

                <div className="flex gap-4 items-center">
                  <Button
                    onClick={() => document.getElementById("enhanced-upload")?.scrollIntoView({ behavior: 'smooth' })}
                    className="h-14 px-8 bg-primary hover:bg-white text-black font-bold text-lg rounded shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_30px_rgba(255,255,255,0.4)] transition-all transform hover:-translate-y-1"
                  >
                    START EXTRACTION
                  </Button>
                  <div className="flex flex-col gap-1 text-sm text-slate-400">
                    <span>No sign-up required for free scan.</span>
                    <a href="#pricing" className="text-primary hover:underline text-xs">Plans start at FREE</a>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Right Interactive Zone */}
            <motion.div
              style={{ x: parallax.x, y: parallax.y }}
              className="md:col-span-5 relative h-[500px] flex items-center justify-center"
            >
              <div className="absolute inset-0 border border-white/10 rounded-3xl bg-black/20 backdrop-blur-sm -rotate-6 z-0"></div>
              <div id="enhanced-upload" className="relative z-10 w-full transform rotate-3 transition-transform hover:rotate-0 duration-500">
                <EnhancedUploadZone 
                  onResults={handleUploadResults}
                  tier="free"
                  maxFiles={1}
                />

                {/* Decorative orbiting elements */}
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                  className="absolute -top-10 -right-10 w-32 h-32 border border-dashed border-primary/30 rounded-full"
                ></motion.div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* AUTHENTICATION STATUS SECTION */}
        <section className="relative py-12 z-10">
          <div className="container mx-auto px-4 max-w-4xl">
            <Card className="bg-[#1a1a2e] border-white/10 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Authentication Status
                </CardTitle>
                <CardDescription className="text-slate-400">
                  {isAuthenticated ? "You are logged in and can access all features" : "Login to access advanced features and save your work"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Checking authentication...</span>
                  </div>
                ) : isAuthenticated && user ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-green-500/20 rounded-full flex items-center justify-center">
                          <CheckCircle2 className="w-5 h-5 text-green-500" />
                        </div>
                        <div>
                          <p className="font-medium">Welcome back, {user.username}!</p>
                          <p className="text-sm text-slate-400">{user.email}</p>
                        </div>
                      </div>
                      <Badge className={`${user.tier === 'professional' ? 'bg-blue-600' : user.tier === 'forensic' ? 'bg-purple-600' : user.tier === 'enterprise' ? 'bg-green-600' : 'bg-gray-600'} text-white`}>
                        {user.tier.toUpperCase()}
                      </Badge>
                    </div>
                    
                    <div className="flex gap-3">
                      <Button 
                        onClick={() => navigate('/dashboard')}
                        className="bg-[#6366f1] hover:bg-[#5855eb] text-white"
                      >
                        <User className="w-4 h-4 mr-2" />
                        Go to Dashboard
                      </Button>
                      <Button 
                        onClick={() => navigate('/results')}
                        variant="outline"
                        className="border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
                      >
                        View Results
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                      <h4 className="font-medium mb-2">Test the Authentication System</h4>
                      <p className="text-sm text-slate-400 mb-4">
                        Use these test credentials to login and explore different subscription tiers:
                      </p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                        <div className="p-3 bg-white/5 rounded border border-white/10">
                          <p className="text-xs font-mono text-blue-400 mb-1">PROFESSIONAL</p>
                          <p className="text-xs font-mono">test@metaextract.com</p>
                          <p className="text-xs font-mono">testpassword123</p>
                        </div>
                        <div className="p-3 bg-white/5 rounded border border-white/10">
                          <p className="text-xs font-mono text-purple-400 mb-1">FORENSIC</p>
                          <p className="text-xs font-mono">forensic@metaextract.com</p>
                          <p className="text-xs font-mono">forensicpassword123</p>
                        </div>
                        <div className="p-3 bg-white/5 rounded border border-white/10">
                          <p className="text-xs font-mono text-green-400 mb-1">ENTERPRISE</p>
                          <p className="text-xs font-mono">admin@metaextract.com</p>
                          <p className="text-xs font-mono">adminpassword123</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-3">
                      <Button 
                        onClick={() => {
                          // Trigger login modal - this will be handled by the Layout component
                          const loginButton = document.querySelector('[data-auth="login"]') as HTMLButtonElement;
                          if (loginButton) loginButton.click();
                        }}
                        className="bg-[#6366f1] hover:bg-[#5855eb] text-white"
                      >
                        <LogIn className="w-4 h-4 mr-2" />
                        Sign In
                      </Button>
                      <Button 
                        onClick={() => {
                          // Trigger register modal
                          const registerButton = document.querySelector('[data-auth="register"]') as HTMLButtonElement;
                          if (registerButton) registerButton.click();
                        }}
                        variant="outline"
                        className="border-white/20 text-slate-300 hover:text-white hover:bg-white/10"
                      >
                        <UserPlus className="w-4 h-4 mr-2" />
                        Register
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </section>

        {/* SECTION 2: COMPACT FEATURE GRID */}
        <section className="relative py-20 z-10">
          <div className="container mx-auto px-4 max-w-7xl">
            <div className="flex items-end justify-between mb-8">
              <div>
                <h2 className="text-2xl sm:text-3xl md:text-4xl font-black text-white mb-2 tracking-tighter">CORE CAPABILITIES</h2>
                <p className="font-mono text-slate-300 text-sm">SYSTEM_MODULES // V2.4</p>
              </div>
            </div>

            {/* Tighter Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 h-auto md:h-[500px]">

              {/* Feature 1: Deep Extract (Wide) */}
              <motion.div
                whileHover={{ scale: 0.99 }}
                className="md:col-span-5 bg-[#121217] border border-white/5 p-8 relative group overflow-hidden flex flex-col justify-between"
              >
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-100 transition-opacity duration-500">
                  <Database className="w-32 h-32 text-primary -rotate-12 translate-x-10 -translate-y-10" />
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-4 text-primary font-mono text-xs">
                    <ScanLine className="w-4 h-4" />
                    <span>DEEP_PACKET_INSPECTION</span>
                  </div>
                  <h3 className="text-2xl md:text-3xl font-bold text-white mb-4">Forensic Deep-Dive</h3>
                  <p className="text-slate-300 leading-relaxed max-w-md">
                    Bypass standard EXIF viewers. Our engine reconstructs 7,000+ data points including Canon MakerNotes, Sony Encrypted Data, and Photoshop History logs to build a complete chain of custody.
                  </p>
                </div>

                <div className="mt-8 flex flex-wrap gap-2">
                  {["MAKERNOTES", "IPTC-IIM", "XMP-EXT", "ICC_PROFILE"].map((tag, i) => (
                    <span key={i} className="px-2 py-1 bg-white/10 text-[10px] font-mono text-slate-200 border border-white/20 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </motion.div>

              {/* Center Column: Stacked */}
              <div className="md:col-span-3 flex flex-col gap-4">
                {/* Zero Trace */}
                <motion.div
                  whileHover={{ scale: 0.99 }}
                  className="flex-1 bg-primary text-black p-6 relative overflow-hidden group flex flex-col justify-center"
                >
                  <ShieldAlert className="w-8 h-8 mb-4 opacity-80" />
                  <h3 className="text-xl font-bold mb-2">No Data Retention</h3>
                  <p className="text-black/80 text-sm font-medium leading-tight">
                    Files are processed in temporary RAM and permanently deleted immediately after analysis. We never store your evidence.
                  </p>
                </motion.div>

                {/* Compliance */}
                <motion.div
                  whileHover={{ scale: 0.99 }}
                  className="flex-1 border border-white/10 bg-black/50 backdrop-blur-md p-6 flex flex-col justify-center"
                >
                  <div className="flex items-center gap-2 mb-2 text-slate-200 font-mono text-xs">
                    <Globe className="w-4 h-4" />
                    <span>GLOBAL_STANDARDS</span>
                  </div>
                  <p className="text-slate-300 text-sm leading-tight">
                    Full compliance with C2PA, Dublin Core, and GDPR Right-to-Erasure protocols.
                  </p>
                </motion.div>
              </div>

              {/* Feature 3: Raw Analysis (Tall Right) */}
              <motion.div
                whileHover={{ scale: 0.99 }}
                className="md:col-span-4 bg-[#0f0f13] border border-white/10 p-8 flex flex-col relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-overlay"></div>

                <div className="flex items-center gap-2 mb-4 text-emerald-500 font-mono text-xs">
                  <FileCode className="w-4 h-4" />
                  <span>BINARY_LEVEL_ACCESS</span>
                </div>

                <h3 className="text-xl md:text-2xl font-bold text-white mb-4">Hex & Entropy Analysis</h3>
                <p className="text-slate-300 text-sm leading-relaxed mb-8">
                  Direct hex-level access allows you to inspect raw file headers. Entropy analysis helps detect if a file has been artificially manipulated or edited.
                </p>

                <div className="mt-auto space-y-3 font-mono text-xs">
                  <div className="flex justify-between items-center p-2 bg-white/5 border-l-2 border-emerald-500">
                    <span className="text-slate-400">HEX_DUMP</span>
                    <span className="text-emerald-500">AVAILABLE</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-white/5 border-l-2 border-emerald-500">
                    <span className="text-slate-400">ENTROPY_MAP</span>
                    <span className="text-emerald-500">GENERATING...</span>
                  </div>
                  <div className="flex justify-between items-center p-2 bg-white/5 border-l-2 border-emerald-500">
                    <span className="text-slate-400">GPS_RECON</span>
                    <span className="text-emerald-500">PRECISE</span>
                  </div>
                </div>

                <Button variant="link" className="text-primary p-0 h-auto justify-start mt-6 group hover:no-underline">
                  View Technical Specs <MoveRight className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform" />
                </Button>
              </motion.div>
            </div>
          </div>
        </section>

        {/* SECTION 3: PRICING */}
        <section className="relative py-20 bg-white/5 border-y border-white/5 overflow-hidden">
          <div className="container mx-auto px-4 max-w-7xl">
            <div className="flex items-end justify-between mb-12">
              <div>
                <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-2">ACCESS</h2>
                <p className="font-mono text-primary text-sm">// SELECT_TIER</p>
              </div>
              <div className="hidden md:block w-1/3 h-px bg-white/20"></div>
            </div>

            {/* Pricing Cards with Hover Expansion */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {PRICING_TIERS.map((tier, i) => (
                <motion.div
                  key={i}
                  whileHover={{ y: -5 }}
                  className={`relative p-6 flex flex-col h-[400px] transition-all duration-300 group ${tier.recommended ? 'bg-primary text-black' : 'bg-black border border-white/10 hover:border-white/30'}`}
                >
                  <div className="flex justify-between items-start mb-8">
                    <h3 className={`font-mono text-xl font-bold ${tier.recommended ? 'text-black' : 'text-white'}`}>{tier.name}</h3>
                    {tier.recommended && <Zap className="w-5 h-5 text-black animate-pulse" />}
                  </div>

                  <div className="mb-auto">
                    <div className="text-4xl font-bold mb-1 tracking-tighter">{tier.price}<span className="text-sm font-normal opacity-60">{tier.period}</span></div>
                    <p className={`text-xs ${tier.recommended ? 'text-black/80' : 'text-slate-400'} mb-6`}>{tier.description}</p>

                    <ul className="space-y-3">
                      {tier.features.map((feat, j) => (
                        <li key={j} className="flex items-center gap-2 text-xs font-mono">
                          <div className={`w-1 h-1 ${tier.recommended ? 'bg-black' : 'bg-primary'}`}></div>
                          <span className={tier.recommended ? 'text-black/90' : 'text-slate-300'}>{feat}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <Button
                    onClick={() => handleCheckout(tier.tier)}
                    disabled={checkoutLoading === tier.tier}
                    data-testid={`button-checkout-${tier.tier}`}
                    className={`w-full mt-6 rounded-sm font-bold tracking-wide border ${tier.recommended ? 'bg-black text-white hover:bg-black/80 border-black' : 'bg-transparent text-white hover:bg-white hover:text-black border-white/20'}`}
                  >
                    {checkoutLoading === tier.tier ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Processing...</>
                    ) : tier.cta}
                  </Button>
                </motion.div>
              ))}
            </div>

            {/* Adhoc Credits Strip */}
            <div className="mt-20 border-t border-white/10 pt-10">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-8">
                <div className="flex items-center gap-4">
                  <div className="bg-white/10 p-3 rounded">
                    <CreditCard className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h4 className="text-white font-bold font-mono">PAY-AS-YOU-GO CREDITS</h4>
                    <p className="text-slate-400 text-xs max-w-sm mb-2">No subscription required. Buy credits for one-off forensic extractions.</p>
                    <p className="text-primary text-xs font-mono border-l-2 border-primary/30 pl-2">
                      1 Credit = 1 Standard File Extraction <span className="text-slate-500">(Video = 3 Credits)</span>
                    </p>
                  </div>
                </div>

                <div className="flex gap-4 overflow-x-auto pb-4 md:pb-0">
                  {CREDIT_PACKS.map((pack, i) => {
                    const packKey = pack.name.toLowerCase() as "single" | "batch" | "bulk";
                    const isLoading = creditPackLoading === packKey;
                    return (
                      <button
                        key={i}
                        onClick={() => handleCreditPurchase(pack.name)}
                        disabled={isLoading}
                        data-testid={`button-credits-${packKey}`}
                        className="flex-shrink-0 bg-black border border-white/10 p-4 min-w-[160px] hover:border-primary/50 transition-colors cursor-pointer group text-left disabled:opacity-50"
                      >
                        {isLoading ? (
                          <div className="flex items-center justify-center h-full">
                            <Loader2 className="w-6 h-6 animate-spin text-primary" />
                          </div>
                        ) : (
                          <>
                            <div className="text-xs text-slate-400 mb-1">{pack.name}</div>
                            <div className="text-xl font-bold text-white group-hover:text-primary">{pack.price}</div>
                            <div className="text-[10px] text-slate-500 font-mono mt-1">{pack.credits} Credits</div>
                            <div className="text-[10px] text-primary/80 font-mono mt-2 border-t border-white/10 pt-2">{pack.per_credit}</div>
                          </>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </section>

      </div>
    </Layout>
  );
}

function CreditCard(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect width="20" height="14" x="2" y="5" rx="2" />
      <line x1="2" x2="22" y1="10" y2="10" />
    </svg>
  )
}
