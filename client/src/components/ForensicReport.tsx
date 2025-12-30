import React, { useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileText, Download, Printer, Shield, AlertTriangle, CheckCircle, Clock, Hash, MapPin, Camera, Info } from "lucide-react";

interface ForensicFinding {
    category: string;
    finding: string;
    severity: "info" | "warning" | "critical";
    confidence: number;
}

interface ForensicReportProps {
    filename: string;
    fileHash: string;
    analysisDate: string;
    overallAssessment: "authentic" | "suspicious" | "manipulated";
    confidenceScore: number;
    findings: ForensicFinding[];
    metadata: {
        device?: string;
        software?: string;
        captureDate?: string;
        gpsLocation?: string;
        dimensions?: string;
    };
    chainOfCustody: Array<{
        timestamp: string;
        action: string;
        actor: string;
    }>;
    onExportPDF?: () => void;
    onExportJSON?: () => void;
    onPrint?: () => void;
}

function getSeverityIcon(severity: ForensicFinding["severity"]) {
    switch (severity) {
        case "critical":
            return <AlertTriangle className="w-4 h-4 text-red-500" />;
        case "warning":
            return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
        default:
            return <Info className="w-4 h-4 text-blue-500" />;
    }
}

function getSeverityColor(severity: ForensicFinding["severity"]) {
    switch (severity) {
        case "critical":
            return "bg-red-500/10 border-red-500/30 text-red-400";
        case "warning":
            return "bg-yellow-500/10 border-yellow-500/30 text-yellow-400";
        default:
            return "bg-blue-500/10 border-blue-500/30 text-blue-400";
    }
}

function getAssessmentDisplay(assessment: ForensicReportProps["overallAssessment"]) {
    switch (assessment) {
        case "authentic":
            return {
                label: "Likely Authentic",
                color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
                icon: <CheckCircle className="w-5 h-5" />,
            };
        case "suspicious":
            return {
                label: "Potentially Suspicious",
                color: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
                icon: <AlertTriangle className="w-5 h-5" />,
            };
        case "manipulated":
            return {
                label: "Evidence of Manipulation",
                color: "bg-red-500/20 text-red-400 border-red-500/30",
                icon: <AlertTriangle className="w-5 h-5" />,
            };
    }
}

export function ForensicReport({
    filename,
    fileHash,
    analysisDate,
    overallAssessment,
    confidenceScore,
    findings,
    metadata,
    chainOfCustody,
    onExportPDF,
    onExportJSON,
    onPrint,
}: ForensicReportProps) {
    const reportRef = useRef<HTMLDivElement>(null);
    const assessment = getAssessmentDisplay(overallAssessment);

    const criticalFindings = findings.filter((f) => f.severity === "critical");
    const warningFindings = findings.filter((f) => f.severity === "warning");
    const infoFindings = findings.filter((f) => f.severity === "info");

    return (
        <Card className="bg-card border-white/10">
            <CardHeader>
                <div className="flex items-start justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2 text-white">
                            <FileText className="w-5 h-5 text-primary" />
                            Forensic Analysis Report
                        </CardTitle>
                        <CardDescription className="text-slate-400">
                            Generated {analysisDate}
                        </CardDescription>
                    </div>
                    <div className="flex gap-2">
                        {onExportPDF && (
                            <Button variant="outline" size="sm" onClick={onExportPDF} className="gap-2">
                                <Download className="w-4 h-4" />
                                PDF
                            </Button>
                        )}
                        {onExportJSON && (
                            <Button variant="outline" size="sm" onClick={onExportJSON} className="gap-2">
                                <Download className="w-4 h-4" />
                                JSON
                            </Button>
                        )}
                        {onPrint && (
                            <Button variant="outline" size="sm" onClick={onPrint} className="gap-2">
                                <Printer className="w-4 h-4" />
                                Print
                            </Button>
                        )}
                    </div>
                </div>
            </CardHeader>

            <CardContent ref={reportRef} className="space-y-6">
                {/* File Summary */}
                <div className="p-4 bg-muted/30 rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-xs text-slate-400 uppercase">File Under Analysis</p>
                            <p className="text-lg font-medium text-white">{filename}</p>
                        </div>
                        <Badge variant="secondary" className={assessment.color}>
                            {assessment.icon}
                            <span className="ml-1">{assessment.label}</span>
                        </Badge>
                    </div>
                    <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                        <Hash className="w-3 h-3" />
                        <span>SHA-256: {fileHash}</span>
                    </div>
                    <div className="text-sm text-white">
                        Confidence Score: <span className="font-bold text-primary">{confidenceScore}%</span>
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-red-500/10 rounded-lg border border-red-500/20">
                        <p className="text-2xl font-bold text-red-400">{criticalFindings.length}</p>
                        <p className="text-xs text-slate-400">Critical</p>
                    </div>
                    <div className="text-center p-3 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                        <p className="text-2xl font-bold text-yellow-400">{warningFindings.length}</p>
                        <p className="text-xs text-slate-400">Warnings</p>
                    </div>
                    <div className="text-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                        <p className="text-2xl font-bold text-blue-400">{infoFindings.length}</p>
                        <p className="text-xs text-slate-400">Info</p>
                    </div>
                </div>

                <Separator className="bg-white/10" />

                {/* Metadata Summary */}
                <div>
                    <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                        <Camera className="w-4 h-4 text-primary" />
                        File Metadata
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                        {metadata.device && (
                            <div className="p-2 bg-muted/30 rounded">
                                <p className="text-xs text-slate-400">Device</p>
                                <p className="text-sm text-white">{metadata.device}</p>
                            </div>
                        )}
                        {metadata.software && (
                            <div className="p-2 bg-muted/30 rounded">
                                <p className="text-xs text-slate-400">Software</p>
                                <p className="text-sm text-white">{metadata.software}</p>
                            </div>
                        )}
                        {metadata.captureDate && (
                            <div className="p-2 bg-muted/30 rounded">
                                <p className="text-xs text-slate-400">Capture Date</p>
                                <p className="text-sm text-white">{metadata.captureDate}</p>
                            </div>
                        )}
                        {metadata.dimensions && (
                            <div className="p-2 bg-muted/30 rounded">
                                <p className="text-xs text-slate-400">Dimensions</p>
                                <p className="text-sm text-white">{metadata.dimensions}</p>
                            </div>
                        )}
                        {metadata.gpsLocation && (
                            <div className="p-2 bg-muted/30 rounded col-span-2 flex items-center gap-2">
                                <MapPin className="w-4 h-4 text-primary" />
                                <div>
                                    <p className="text-xs text-slate-400">GPS Location</p>
                                    <p className="text-sm text-white">{metadata.gpsLocation}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <Separator className="bg-white/10" />

                {/* Findings */}
                <div>
                    <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                        <Shield className="w-4 h-4 text-primary" />
                        Analysis Findings
                    </h3>
                    <ScrollArea className="h-[200px]">
                        <div className="space-y-2 pr-4">
                            {findings.map((finding, i) => (
                                <div
                                    key={i}
                                    className={`p-3 rounded border ${getSeverityColor(finding.severity)}`}
                                >
                                    <div className="flex items-start gap-2">
                                        {getSeverityIcon(finding.severity)}
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <Badge variant="outline" className="text-xs border-white/20">
                                                    {finding.category}
                                                </Badge>
                                                <span className="text-xs text-slate-400">{finding.confidence}% confidence</span>
                                            </div>
                                            <p className="text-sm">{finding.finding}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </ScrollArea>
                </div>

                <Separator className="bg-white/10" />

                {/* Chain of Custody */}
                <div>
                    <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                        <Clock className="w-4 h-4 text-primary" />
                        Chain of Custody
                    </h3>
                    <div className="space-y-2">
                        {chainOfCustody.map((entry, i) => (
                            <div key={i} className="flex items-center gap-4 p-2 bg-muted/30 rounded text-sm">
                                <span className="font-mono text-slate-400 shrink-0 w-32">{entry.timestamp}</span>
                                <span className="text-white flex-1">{entry.action}</span>
                                <span className="text-slate-400">{entry.actor}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Disclaimer */}
                <div className="text-xs text-slate-500 p-3 bg-muted/20 rounded border border-white/5">
                    <p className="font-semibold mb-1">Disclaimer</p>
                    <p>
                        This report is generated based on automated analysis of file metadata and digital
                        artifacts. It should be used as part of a comprehensive investigation and not as
                        sole evidence. Results should be verified by qualified forensic experts.
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}
