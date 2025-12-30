import { Layout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { CheckCircle2, ArrowRight, Coins } from "lucide-react";
import { useLocation } from "wouter";
import { useEffect, useState } from "react";
import { CREDIT_PACKS } from "@/lib/mockData";

export default function CreditsSuccess() {
  const [, navigate] = useLocation();
  const [pack, setPack] = useState<string | null>(null);
  const [credits, setCredits] = useState<number>(0);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const packName = params.get("pack");
    setPack(packName);
    
    const packInfo = CREDIT_PACKS.find(p => p.name.toLowerCase() === packName);
    if (packInfo) {
      setCredits(packInfo.credits);
    }
  }, []);

  const packDisplayNames: Record<string, string> = {
    single: "Single Pack",
    batch: "Batch Pack",
    bulk: "Bulk Pack",
  };

  return (
    <Layout>
      <div className="min-h-screen bg-[#0B0C10] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="bg-primary/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
            <Coins className="w-10 h-10 text-primary" />
          </div>
          
          <h1 className="text-3xl font-bold text-white mb-4" data-testid="text-credits-success-title">
            Credits Added!
          </h1>
          
          <p className="text-slate-400 mb-8" data-testid="text-credits-success-message">
            Your {pack ? packDisplayNames[pack] || pack : "credit"} purchase is complete. 
            {credits > 0 && ` ${credits} credits have been added to your balance.`}
          </p>

          <div className="bg-white/5 border border-white/10 rounded-lg p-6 mb-8">
            <h3 className="text-white font-semibold mb-4">Credit Usage:</h3>
            <ul className="text-left text-slate-300 space-y-2 text-sm">
              <li className="flex justify-between">
                <span>Standard Image (JPG/PNG)</span>
                <span className="text-primary font-mono">1 Credit</span>
              </li>
              <li className="flex justify-between">
                <span>RAW Image (CR2/NEF/ARW)</span>
                <span className="text-primary font-mono">2 Credits</span>
              </li>
              <li className="flex justify-between">
                <span>Audio File (MP3/FLAC)</span>
                <span className="text-primary font-mono">2 Credits</span>
              </li>
              <li className="flex justify-between">
                <span>Video File (MP4/MOV)</span>
                <span className="text-primary font-mono">3 Credits</span>
              </li>
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
