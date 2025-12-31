import React from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { AlertTriangle, CheckCircle, Eye, Shield, Clock, Fingerprint } from "lucide-react";

interface AdvancedAnalysisResultsProps {
    steganography?: {
        detected: boolean;
        confidence: number;
        methods_checked: string[];
        findings: string[];
    } | null;
    manipulation?: {
        detected: boolean;
        confidence: number;
        indicators: Array<{
            type: string;
            severity: "low" | "medium" | "high";
            description: string;
        }>;
    } | null;
    aiDetection?: {
        ai_generated: boolean;
        confidence: number;
        model_hints: string[];
    } | null;
    timeline?: {
        events: Array<{
            timestamp: string;
            event_type: string;
            source: string;
        }>;
        gaps_detected: boolean;
        chain_of_custody_complete: boolean;
    } | null;
}

function ConfidenceIndicator({ value, label }: { value: number; label?: string }) {
    return (
        <div className="space-y-1">
            {label && <span className="text-xs text-slate-400">{label}</span>}
            <div className="flex items-center gap-2">
                <Progress value={value} className="h-2 flex-1" />
                <span className="text-sm font-mono text-white">{value}%</span>
            </div>
        </div>
    );
}

function StatusBadge({ detected, label }: { detected: boolean; label: string }) {
    return (
        <Badge
            variant={detected ? "destructive" : "secondary"}
            className={`gap-1 ${detected ? "bg-red-500/20 text-red-400 border-red-500/30" : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"}`}
        >
            {detected ? <AlertTriangle className="w-3 h-3" /> : <CheckCircle className="w-3 h-3" />}
            {label}
        </Badge>
    );
}

export function AdvancedAnalysisResults({
    steganography,
    manipulation,
    aiDetection,
    timeline,
}: AdvancedAnalysisResultsProps) {
    const hasAnyResults = steganography || manipulation || aiDetection || timeline;

    if (!hasAnyResults) {
        return (
            <Card className="bg-card border-white/10">
                <CardContent className="py-8 text-center">
                    <Shield className="w-12 h-12 mx-auto mb-4 text-slate-500" />
                    <p className="text-slate-400">No advanced analysis data available</p>
                    <p className="text-xs text-slate-500 mt-2">Advanced analysis requires Forensic or Enterprise tier</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="bg-card border-white/10">
            <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                    <Fingerprint className="w-5 h-5 text-primary" />
                    Forensic Analysis
                </CardTitle>
                <CardDescription className="text-slate-400">
                    Deep analysis for authenticity and manipulation detection
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Tabs defaultValue="steganography" className="w-full">
                    <TabsList className="grid w-full grid-cols-4 bg-muted/50">
                        <TabsTrigger value="steganography" className="text-xs">Steganography</TabsTrigger>
                        <TabsTrigger value="manipulation" className="text-xs">Manipulation</TabsTrigger>
                        <TabsTrigger value="ai" className="text-xs">AI Detection</TabsTrigger>
                        <TabsTrigger value="timeline" className="text-xs">Timeline</TabsTrigger>
                    </TabsList>

                    {/* Steganography Tab */}
                    <TabsContent value="steganography" className="mt-4 space-y-4">
                        {steganography ? (
                            <>
                                <div className="flex items-center justify-between">
                                    <StatusBadge
                                        detected={steganography.detected}
                                        label={steganography.detected ? "Hidden Data Detected" : "No Hidden Data"}
                                    />
                                    <ConfidenceIndicator value={steganography.confidence} label="Confidence" />
                                </div>
                                {steganography.methods_checked.length > 0 && (
                                    <div>
                                        <p className="text-xs text-slate-400 mb-2">Methods Analyzed:</p>
                                        <div className="flex flex-wrap gap-1">
                                            {steganography.methods_checked.map((method, i) => (
                                                <Badge key={i} variant="outline" className="text-xs border-white/20">
                                                    {method}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {steganography.findings.length > 0 && (
                                    <div className="bg-muted/50 p-3 rounded space-y-1">
                                        {steganography.findings.map((finding, i) => (
                                            <p key={i} className="text-sm text-slate-300 flex items-start gap-2">
                                                <Eye className="w-4 h-4 mt-0.5 text-primary shrink-0" />
                                                {finding}
                                            </p>
                                        ))}
                                    </div>
                                )}
                            </>
                        ) : (
                            <p className="text-slate-500 text-sm">Steganography analysis not available</p>
                        )}
                    </TabsContent>

                    {/* Manipulation Tab */}
                    <TabsContent value="manipulation" className="mt-4 space-y-4">
                        {manipulation ? (
                            <>
                                <div className="flex items-center justify-between">
                                    <StatusBadge
                                        detected={manipulation.detected}
                                        label={manipulation.detected ? "Manipulation Detected" : "No Manipulation"}
                                    />
                                    <ConfidenceIndicator value={manipulation.confidence} label="Confidence" />
                                </div>
                                {manipulation.indicators.length > 0 && (
                                    <div className="space-y-2">
                                        {manipulation.indicators.map((indicator, i) => (
                                            <div
                                                key={i}
                                                className={`p-3 rounded border ${indicator.severity === "high"
                                                        ? "bg-red-500/10 border-red-500/30"
                                                        : indicator.severity === "medium"
                                                            ? "bg-yellow-500/10 border-yellow-500/30"
                                                            : "bg-slate-500/10 border-slate-500/30"
                                                    }`}
                                            >
                                                <div className="flex items-center gap-2 mb-1">
                                                    <Badge
                                                        variant="outline"
                                                        className={`text-xs ${indicator.severity === "high"
                                                                ? "border-red-500 text-red-400"
                                                                : indicator.severity === "medium"
                                                                    ? "border-yellow-500 text-yellow-400"
                                                                    : "border-slate-500 text-slate-400"
                                                            }`}
                                                    >
                                                        {indicator.severity.toUpperCase()}
                                                    </Badge>
                                                    <span className="text-sm font-medium text-white">{indicator.type}</span>
                                                </div>
                                                <p className="text-xs text-slate-400">{indicator.description}</p>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        ) : (
                            <p className="text-slate-500 text-sm">Manipulation detection not available</p>
                        )}
                    </TabsContent>

                    {/* AI Detection Tab */}
                    <TabsContent value="ai" className="mt-4 space-y-4">
                        {aiDetection ? (
                            <>
                                <div className="flex items-center justify-between">
                                    <StatusBadge
                                        detected={aiDetection.ai_generated}
                                        label={aiDetection.ai_generated ? "AI-Generated" : "Likely Authentic"}
                                    />
                                    <ConfidenceIndicator value={aiDetection.confidence} label="Confidence" />
                                </div>
                                {aiDetection.model_hints.length > 0 && (
                                    <div>
                                        <p className="text-xs text-slate-400 mb-2">Model Indicators:</p>
                                        <div className="flex flex-wrap gap-1">
                                            {aiDetection.model_hints.map((hint, i) => (
                                                <Badge key={i} variant="outline" className="text-xs border-white/20">
                                                    {hint}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </>
                        ) : (
                            <p className="text-slate-500 text-sm">AI detection not available</p>
                        )}
                    </TabsContent>

                    {/* Timeline Tab */}
                    <TabsContent value="timeline" className="mt-4 space-y-4">
                        {timeline ? (
                            <>
                                <div className="flex gap-4">
                                    <StatusBadge
                                        detected={timeline.gaps_detected}
                                        label={timeline.gaps_detected ? "Gaps Detected" : "No Gaps"}
                                    />
                                    <StatusBadge
                                        detected={!timeline.chain_of_custody_complete}
                                        label={timeline.chain_of_custody_complete ? "Chain Complete" : "Chain Incomplete"}
                                    />
                                </div>
                                {timeline.events.length > 0 && (
                                    <div className="space-y-2">
                                        {timeline.events.map((event, i) => (
                                            <div key={i} className="flex items-center gap-3 p-2 bg-muted/30 rounded">
                                                <Clock className="w-4 h-4 text-primary shrink-0" />
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm text-white truncate">{event.event_type}</p>
                                                    <p className="text-xs text-slate-500">{event.source}</p>
                                                </div>
                                                <span className="text-xs font-mono text-slate-400">{event.timestamp}</span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        ) : (
                            <p className="text-slate-500 text-sm">Timeline analysis not available</p>
                        )}
                    </TabsContent>
                </Tabs>
            </CardContent>
        </Card>
    );
}
