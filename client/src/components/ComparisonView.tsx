import React from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowLeftRight, Equal, Info, AlertTriangle, Download } from "lucide-react";

interface FileMetadata {
    filename: string;
    fields: Record<string, any>;
}

interface ComparisonDifference {
    field: string;
    file1_value: any;
    file2_value: any;
    status: "match" | "different" | "only_in_file1" | "only_in_file2";
}

interface ComparisonViewProps {
    file1: FileMetadata;
    file2: FileMetadata;
    differences: ComparisonDifference[];
    similarityScore: number;
    onExport?: () => void;
}

function formatValue(value: any): string {
    if (value === null || value === undefined) return "—";
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
}

function DifferenceRow({ diff }: { diff: ComparisonDifference }) {
    const getStatusIcon = () => {
        switch (diff.status) {
            case "match":
                return <Equal className="w-4 h-4 text-emerald-500" />;
            case "different":
                return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
            case "only_in_file1":
            case "only_in_file2":
                return <Info className="w-4 h-4 text-blue-500" />;
        }
    };

    const getBgColor = () => {
        switch (diff.status) {
            case "match":
                return "bg-emerald-500/5";
            case "different":
                return "bg-yellow-500/10";
            case "only_in_file1":
            case "only_in_file2":
                return "bg-blue-500/5";
        }
    };

    return (
        <div className={`grid grid-cols-3 gap-4 p-3 border-b border-white/5 ${getBgColor()}`}>
            <div className="flex items-center gap-2">
                {getStatusIcon()}
                <span className="text-sm font-mono text-slate-300 truncate">{diff.field}</span>
            </div>
            <div className="text-sm text-white truncate" title={formatValue(diff.file1_value)}>
                {diff.status === "only_in_file2" ? (
                    <span className="text-slate-500">—</span>
                ) : (
                    formatValue(diff.file1_value)
                )}
            </div>
            <div className="text-sm text-white truncate" title={formatValue(diff.file2_value)}>
                {diff.status === "only_in_file1" ? (
                    <span className="text-slate-500">—</span>
                ) : (
                    formatValue(diff.file2_value)
                )}
            </div>
        </div>
    );
}

export function ComparisonView({
    file1,
    file2,
    differences,
    similarityScore,
    onExport,
}: ComparisonViewProps) {
    const matchCount = differences.filter((d) => d.status === "match").length;
    const diffCount = differences.filter((d) => d.status === "different").length;
    const file1OnlyCount = differences.filter((d) => d.status === "only_in_file1").length;
    const file2OnlyCount = differences.filter((d) => d.status === "only_in_file2").length;

    return (
        <Card className="bg-card border-white/10">
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center gap-2 text-white">
                            <ArrowLeftRight className="w-5 h-5 text-primary" />
                            Metadata Comparison
                        </CardTitle>
                        <CardDescription className="text-slate-400">
                            Side-by-side analysis of {file1.filename} vs {file2.filename}
                        </CardDescription>
                    </div>
                    {onExport && (
                        <Button variant="outline" size="sm" onClick={onExport} className="gap-2">
                            <Download className="w-4 h-4" />
                            Export
                        </Button>
                    )}
                </div>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Similarity Score */}
                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                    <div className="space-y-1">
                        <p className="text-sm text-slate-400">Similarity Score</p>
                        <p className="text-3xl font-bold text-white">{similarityScore}%</p>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-center">
                        <div>
                            <p className="text-2xl font-bold text-emerald-500">{matchCount}</p>
                            <p className="text-xs text-slate-400">Matching</p>
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-yellow-500">{diffCount}</p>
                            <p className="text-xs text-slate-400">Different</p>
                        </div>
                    </div>
                </div>

                {/* Stats */}
                <div className="flex gap-2 flex-wrap">
                    <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                        {matchCount} Matching
                    </Badge>
                    <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                        {diffCount} Different
                    </Badge>
                    {file1OnlyCount > 0 && (
                        <Badge variant="secondary" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                            {file1OnlyCount} Only in File 1
                        </Badge>
                    )}
                    {file2OnlyCount > 0 && (
                        <Badge variant="secondary" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                            {file2OnlyCount} Only in File 2
                        </Badge>
                    )}
                </div>

                {/* Comparison Table */}
                <div className="border border-white/10 rounded-lg overflow-hidden">
                    {/* Header */}
                    <div className="grid grid-cols-3 gap-4 p-3 bg-muted/50 border-b border-white/10">
                        <span className="text-xs font-semibold text-slate-400 uppercase">Field</span>
                        <span className="text-xs font-semibold text-slate-400 uppercase truncate" title={file1.filename}>
                            {file1.filename}
                        </span>
                        <span className="text-xs font-semibold text-slate-400 uppercase truncate" title={file2.filename}>
                            {file2.filename}
                        </span>
                    </div>

                    {/* Rows */}
                    <ScrollArea className="h-[400px]">
                        {differences.map((diff, i) => (
                            <DifferenceRow key={i} diff={diff} />
                        ))}
                    </ScrollArea>
                </div>
            </CardContent>
        </Card>
    );
}
