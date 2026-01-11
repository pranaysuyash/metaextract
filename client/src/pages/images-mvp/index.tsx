import React, { useEffect } from "react";
import { PublicLayout as Layout } from "@/components/public-layout";
import { SimpleUploadZone } from "@/components/images-mvp/simple-upload";
import { motion, useReducedMotion } from "framer-motion";
import { ShieldCheck, Eye, Fingerprint, Zap } from "lucide-react";
import { trackImagesMvpEvent } from "@/lib/images-mvp-analytics";
import { useAuth } from "@/lib/auth";

export default function ImagesMvpLanding() {
    const { isAuthenticated, user } = useAuth();
    
    useEffect(() => {
        trackImagesMvpEvent("images_landing_viewed", { location: "images_mvp" });
    }, []);

    const shouldReduceMotion = useReducedMotion();

    useEffect(() => {
        document.title = "MetaExtract | Images MVP";
    }, []);

    return (
        <Layout showHeader={true} showFooter={false}>
            <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4 focus:bg-white focus:text-black focus:top-0 focus:left-0 transition-all">
                Skip to main content
            </a>
            <div className="min-h-screen bg-[#0B0C10] text-white selection:bg-primary/30 pt-20" role="main" id="main-content">

                {/* Hero Section */}
                <section className="container mx-auto px-4 py-20 flex flex-col items-center justify-center min-h-[80vh] relative z-10">

                    {/* Background decorative elements */}
                    <div className="absolute inset-0 overflow-hidden pointer-events-none">
                        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl opacity-30 animate-pulse"></div>
                        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl opacity-30 animate-pulse" style={{ animationDelay: '1s' }}></div>
                    </div>

                    <motion.div
                        initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-12 max-w-2xl relative z-10"
                    >
                        <div className="inline-block px-3 py-1 mb-6 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-primary">
                            BETA ACCESS // IMAGES_ONLY
                        </div>
                        
                        {isAuthenticated && user ? (
                            // Logged-in version
                            <>
                                <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
                                    Extract <span className="text-primary">Metadata</span>
                                </h1>
                                <p className="text-lg text-slate-200 leading-relaxed">
                                    Welcome back, {user.username}. Upload your images to analyze hidden metadata.
                                </p>
                            </>
                        ) : (
                            // Logged-out version (marketing copy)
                            <>
                                <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/60">
                                    Metadata for <span className="text-primary">Humans.</span>
                                </h1>
                                <p className="text-lg text-slate-200 leading-relaxed">
                                    Check your photos for hidden location data, device serial numbers, and personal information before you share.
                                </p>
                            </>
                        )}
                    </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="w-full max-w-lg relative z-10"
                >
                    <section aria-labelledby="upload-heading">
                        <h2 id="upload-heading" className="sr-only">Upload Analysis</h2>
                        <SimpleUploadZone />
                    </section>

                    <div className="mt-8 flex justify-center gap-8 text-sm text-slate-500 font-mono">
                        <div className="flex items-center gap-2">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            <span>Instant Check</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <ShieldCheck className="w-4 h-4 text-emerald-500" aria-hidden="true" />
                            <span>100% Private</span>
                        </div>
                    </div>
                </motion.div>
            </section>

            {/* Features / "Why check?" Section - Only show for logged-out users */}
            {!isAuthenticated && (
                <section className="py-24 border-t border-white/5 bg-white/[0.02]" aria-labelledby="features-heading">
                    <div className="container mx-auto px-4 max-w-5xl">
                        <h2 id="features-heading" className="sr-only">Key Features</h2>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                            <div className="space-y-4">
                                <div className="w-12 h-12 bg-white/5 rounded-lg flex items-center justify-center border border-white/10 text-primary">
                                    <Fingerprint className="w-6 h-6" aria-hidden="true" />
                                </div>
                                <h3 className="text-xl font-bold text-white">Device Fingerprints</h3>
                                <p className="text-slate-200 leading-relaxed">
                                    Photos contain unique serial numbers ("MakerNotes") that link images back to your specific camera or phone.
                                </p>
                            </div>
                            <div className="space-y-4">
                                <div className="w-12 h-12 bg-white/5 rounded-lg flex items-center justify-center border border-white/10 text-purple-400">
                                    <Eye className="w-6 h-6" aria-hidden="true" />
                                </div>
                                <h3 className="text-xl font-bold text-white">Hidden Location</h3>
                                <p className="text-slate-200 leading-relaxed">
                                    GPS coordinates are often embedded by default. See exactly where a photo was taken before posting it online.
                                </p>
                            </div>
                            <div className="space-y-4">
                                <div className="w-12 h-12 bg-white/5 rounded-lg flex items-center justify-center border border-white/10 text-emerald-400">
                                    <ShieldCheck className="w-6 h-6" aria-hidden="true" />
                                </div>
                                <h3 className="text-xl font-bold text-white">Safe Sharing</h3>
                                <p className="text-slate-200 leading-relaxed">
                                    Understand what you're revealing. We extract the hidden layer so you can decide what stays private.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>
            )}
        </div>
        </Layout>
    );
}
