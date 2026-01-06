import React from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from "@/components/ui/tooltip";
import { Clock, Camera, Edit, Save, AlertTriangle, CheckCircle, Circle } from "lucide-react";

interface TimelineEvent {
    timestamp: string;
    event_type: string;
    source: string;
    description?: string;
    confidence?: number;
}

interface TimelineGap {
    start: string;
    end: string;
    duration_readable: string;
    suspicious: boolean;
}

interface TimelineVisualizationProps {
    events: TimelineEvent[];
    gaps?: TimelineGap[];
    chainOfCustodyComplete: boolean;
    firstTimestamp?: string;
    lastTimestamp?: string;
}

function getEventIcon(eventType: string) {
    switch (eventType.toLowerCase()) {
        case "created":
        case "capture":
        case "original":
            return <Camera className="w-4 h-4" />;
        case "modified":
        case "edited":
        case "saved":
            return <Edit className="w-4 h-4" />;
        case "exported":
        case "save":
            return <Save className="w-4 h-4" />;
        default:
            return <Circle className="w-4 h-4" />;
    }
}

function getEventColor(eventType: string) {
    switch (eventType.toLowerCase()) {
        case "created":
        case "capture":
        case "original":
            return "text-emerald-500 border-emerald-500";
        case "modified":
        case "edited":
            return "text-yellow-500 border-yellow-500";
        case "exported":
        case "save":
        case "saved":
            return "text-blue-500 border-blue-500";
        default:
            return "text-slate-300 border-slate-400";
    }
}

function formatTimestamp(timestamp: string): { date: string; time: string } {
    try {
        const date = new Date(timestamp);
        return {
            date: date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }),
            time: date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        };
    } catch {
        return { date: timestamp, time: "" };
    }
}

export function TimelineVisualization({
    events,
    gaps = [],
    chainOfCustodyComplete,
    firstTimestamp,
    lastTimestamp,
}: TimelineVisualizationProps) {
    const sortedEvents = [...events].sort(
        (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );

    return (
        <TooltipProvider>
            <Card className="bg-card border-white/10">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                        <Clock className="w-5 h-5 text-primary" />
                        File Timeline
                    </CardTitle>
                    <CardDescription className="text-slate-300">
                        Chronological history of file events from metadata
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {/* Chain of Custody Status */}
                    <div className="flex items-center gap-4">
                        <Badge
                            variant="secondary"
                            className={
                                chainOfCustodyComplete
                                    ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                    : "bg-red-500/20 text-red-400 border-red-500/30"
                            }
                        >
                            {chainOfCustodyComplete ? (
                                <CheckCircle className="w-3 h-3 mr-1" />
                            ) : (
                                <AlertTriangle className="w-3 h-3 mr-1" />
                            )}
                            {chainOfCustodyComplete ? "Chain Complete" : "Chain Incomplete"}
                        </Badge>
                        {gaps.length > 0 && (
                            <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                                {gaps.length} Gap{gaps.length > 1 ? "s" : ""} Detected
                            </Badge>
                        )}
                    </div>

                    {/* Time Range */}
                    {firstTimestamp && lastTimestamp && (
                        <div className="flex items-center justify-between text-xs text-slate-300 font-mono p-2 bg-muted/30 rounded">
                            <span>{formatTimestamp(firstTimestamp).date}</span>
                            <span>→</span>
                            <span>{formatTimestamp(lastTimestamp).date}</span>
                        </div>
                    )}

                    {/* Timeline */}
                    <ScrollArea className="h-[400px] pr-4">
                        <div className="relative pl-6 space-y-0">
                            {/* Vertical line */}
                            <div className="absolute left-[11px] top-0 bottom-0 w-px bg-white/10" />

                            {sortedEvents.map((event, i) => {
                                const { date, time } = formatTimestamp(event.timestamp);
                                const colorClass = getEventColor(event.event_type);

                                return (
                                    <div key={i} className="relative pb-6 last:pb-0">
                                        {/* Node */}
                                        <div
                                            className={`absolute left-0 w-[22px] h-[22px] rounded-full bg-card border-2 flex items-center justify-center ${colorClass}`}
                                        >
                                            {getEventIcon(event.event_type)}
                                        </div>

                                        {/* Content */}
                                        <div className="ml-8 p-3 bg-muted/30 rounded-lg border border-white/5 hover:border-white/20 transition-colors">
                                            <div className="flex items-start justify-between gap-4">
                                                <div>
                                                    <p className="font-medium text-white capitalize">{event.event_type}</p>
                                                    {event.description && (
                                                        <p className="text-sm text-slate-300 mt-1">{event.description}</p>
                                                    )}
                                                    <p className="text-xs text-slate-500 mt-1">Source: {event.source}</p>
                                                </div>
                                                <div className="text-right shrink-0">
                                                    <p className="text-sm font-mono text-slate-200">{date}</p>
                                                    {time && <p className="text-xs font-mono text-slate-500">{time}</p>}
                                                </div>
                                            </div>
                                            {event.confidence !== undefined && (
                                                <div className="mt-2">
                                                    <Tooltip>
                                                        <TooltipTrigger asChild>
                                                            <Badge variant="outline" className="text-xs border-white/20">
                                                                {event.confidence}% confidence
                                                            </Badge>
                                                        </TooltipTrigger>
                                                        <TooltipContent>
                                                            <p>Reliability of this timestamp</p>
                                                        </TooltipContent>
                                                    </Tooltip>
                                                </div>
                                            )}
                                        </div>

                                        {/* Gap indicator */}
                                        {i < sortedEvents.length - 1 &&
                                            gaps.find(
                                                (g) =>
                                                    new Date(g.start).getTime() === new Date(event.timestamp).getTime()
                                            ) && (
                                                <div className="ml-8 my-2 p-2 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-400 flex items-center gap-2">
                                                    <AlertTriangle className="w-3 h-3" />
                                                    <span>
                                                        Gap detected:{" "}
                                                        {gaps.find(
                                                            (g) =>
                                                                new Date(g.start).getTime() === new Date(event.timestamp).getTime()
                                                        )?.duration_readable}
                                                    </span>
                                                </div>
                                            )}
                                    </div>
                                );
                            })}

                            {sortedEvents.length === 0 && (
                                <div className="text-center py-8 text-slate-500">
                                    <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                    <p>No timeline events found</p>
                                </div>
                            )}
                        </div>
                    </ScrollArea>
                </CardContent>
            </Card>
        </TooltipProvider>
    );
}
