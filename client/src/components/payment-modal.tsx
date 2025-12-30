import React, { useState } from "react";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import * as VisuallyHidden from "@radix-ui/react-visually-hidden";
import { Button } from "@/components/ui/button";
import { Check, Lock, X } from "lucide-react";
import { motion } from "framer-motion";

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function PaymentModal({ isOpen, onClose, onSuccess }: PaymentModalProps) {
  const [loading, setLoading] = useState(false);

  const handlePay = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      onSuccess();
      onClose();
    }, 1500);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[400px] p-0 overflow-hidden bg-[#0A0A0A] border border-white/10 shadow-2xl text-white">
        <VisuallyHidden.Root>
          <DialogTitle>Payment - Unlock Full Report</DialogTitle>
          <DialogDescription>Complete your payment to unlock the full metadata report.</DialogDescription>
        </VisuallyHidden.Root>
        {/* Dodo Payments Header Style */}
        <div className="bg-[#111] p-4 flex items-center justify-between border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
              <span className="text-black font-bold text-xs">D</span>
            </div>
            <span className="font-semibold text-sm">Dodo Payments</span>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <div className="text-slate-400 text-xs uppercase tracking-wider mb-1">Total Due</div>
            <div className="text-3xl font-bold">$5.00</div>
            <div className="text-slate-500 text-sm mt-1">MetaExtract - Full Report Unlock</div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-300">Email</label>
              <input
                type="email"
                placeholder="name@example.com"
                className="w-full px-3 py-2 bg-[#1A1A1A] border border-white/10 rounded-md text-sm text-white focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-600"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-slate-300">Card Information</label>
              <div className="bg-[#1A1A1A] border border-white/10 rounded-md overflow-hidden">
                <input
                  type="text"
                  placeholder="1234 5678 1234 5678"
                  className="w-full px-3 py-2 bg-transparent border-b border-white/10 text-sm text-white focus:bg-[#222] outline-none placeholder:text-slate-600"
                />
                <div className="flex">
                  <input
                    type="text"
                    placeholder="MM / YY"
                    className="w-1/2 px-3 py-2 bg-transparent border-r border-white/10 text-sm text-white focus:bg-[#222] outline-none placeholder:text-slate-600"
                  />
                  <input
                    type="text"
                    placeholder="CVC"
                    className="w-1/2 px-3 py-2 bg-transparent text-sm text-white focus:bg-[#222] outline-none placeholder:text-slate-600"
                  />
                </div>
              </div>
            </div>

            <Button
              onClick={handlePay}
              disabled={loading}
              className="w-full bg-white text-black hover:bg-slate-200 mt-4 h-10 font-medium"
            >
              {loading ? "Processing..." : "Pay $5.00"}
            </Button>
          </div>

          <div className="mt-6 flex justify-center gap-4 text-[10px] text-slate-600">
            <span className="flex items-center gap-1"><Lock className="w-2.5 h-2.5" /> Secure Checkout</span>
            <span>Powered by Dodo</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
