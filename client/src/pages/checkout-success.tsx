import { Layout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { CheckCircle2, ArrowRight } from "lucide-react";
import { useLocation } from "wouter";
import { useEffect, useState } from "react";

export default function CheckoutSuccess() {
  const [, navigate] = useLocation();
  const [tier, setTier] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setTier(params.get("tier"));
  }, []);

  const normalizedTier =
    tier === "starter"
      ? "professional"
      : tier === "premium"
      ? "forensic"
      : tier === "super"
      ? "enterprise"
      : tier;

  const tierDisplayNames: Record<string, string> = {
    professional: "Professional",
    forensic: "Forensic",
    enterprise: "Enterprise",
    starter: "Professional",
    premium: "Forensic",
    super: "Enterprise",
  };

  return (
    <Layout>
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-emerald-500/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle2 className="w-10 h-10 text-emerald-500" />
          </div>
          
          <h1 className="text-3xl font-bold text-white mb-4" data-testid="text-success-title">
            Welcome to {normalizedTier ? tierDisplayNames[normalizedTier] || normalizedTier : "MetaExtract"}!
          </h1>
          
          <p className="text-slate-400 mb-8" data-testid="text-success-message">
            Your subscription is now active. You have full access to all {normalizedTier ? tierDisplayNames[normalizedTier] : ""} features.
          </p>

          <div className="bg-white/5 border border-white/10 rounded-lg p-6 mb-8">
            <h3 className="text-white font-semibold mb-4">What's included:</h3>
            <ul className="text-left text-slate-300 space-y-2 text-sm">
              {(normalizedTier === "professional") && (
                <>
                  <li>All images including RAW formats (up to 100MB)</li>
                  <li>Full EXIF + GPS + File Hashes</li>
                  <li>50 extractions per day</li>
                  <li>JSON export</li>
                </>
              )}
              {(normalizedTier === "forensic") && (
                <>
                  <li>All media types including video/audio (up to 500MB)</li>
                  <li>7,000+ metadata fields + MakerNotes</li>
                  <li>Unlimited extractions</li>
                  <li>Batch upload support</li>
                </>
              )}
              {(normalizedTier === "enterprise") && (
                <>
                  <li>All file types (up to 2GB)</li>
                  <li>Complete forensic analysis</li>
                  <li>API access (10,000 calls/month)</li>
                  <li>Priority support</li>
                </>
              )}
            </ul>
          </div>

          <Button
            onClick={() => navigate("/")}
            className="bg-primary hover:bg-primary/90 text-black font-bold px-8 py-3"
            data-testid="button-start-extracting"
          >
            Start Extracting <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </Layout>
  );
}
