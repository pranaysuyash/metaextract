
import React, { useEffect, useState } from "react";
import { PublicLayout as Layout } from "@/components/public-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MapPin, Camera, Calendar, FileImage, ShieldAlert, Lock, ArrowRight, Share2, CheckCircle2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

interface MvpMetadata {
    filename: string;
    filesize: string;
    filetype: string;
    mime_type: string;
    gps: Record<string, any> | null;
    exif: Record<string, any>;
    filesystem?: { created?: string; modified?: string };
    hashes?: Record<string, any>;
    file_integrity?: Record<string, any>;
    perceptual_hashes?: Record<string, any>;
    burned_metadata?: {
        has_burned_metadata: boolean;
        extracted_text?: string | null;
        confidence?: string;
        parsed_data?: {
            gps?: { latitude: number; longitude: number; google_maps_url?: string };
            timestamp?: string;
            plus_code?: string;
            address?: string;
        };
    } | null;
    metadata_comparison?: {
        warnings?: string[];
        summary?: { overall_status?: string; gps_comparison?: string; timestamp_comparison?: string };
    } | null;
    normalized?: Record<string, any> | null;
    calculated?: Record<string, any> | null;
    processing_ms?: number;
    fields_extracted?: number;
    access: { trial_granted: boolean; trial_email_present: boolean };
    _trial_limited?: boolean;
    client_last_modified_iso?: string;
    registry_summary?: Record<string, any>;
}

export default function ImagesMvpResults() {
    const [metadata, setMetadata] = useState<MvpMetadata | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const stored = sessionStorage.getItem('currentMetadata');
        if (!stored) {
            navigate('/images_mvp');
            return;
        }
        try {
            setMetadata(JSON.parse(stored));
        } catch (e) {
            console.error("Failed to parse metadata", e);
            navigate('/images_mvp');
        }
    }, [navigate]);

    if (!metadata) return null;

    const isTrialLimited = metadata._trial_limited || (metadata.access?.trial_granted);
    const canExport = !isTrialLimited;

    const handleDownloadJson = () => {
        if (!canExport) {
            return;
        }
        const payload = JSON.stringify(metadata, null, 2);
        const blob = new Blob([payload], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        const baseName = metadata.filename?.replace(/\.[^/.]+$/, "") || "metadata";
        link.href = url;
        link.download = `${baseName}.json`;
        link.click();
        URL.revokeObjectURL(url);
    };

    // Format Date Helper
    const formatDate = (dateStr?: string) => {
        if (!dateStr) return "Not available";
        try {
            return new Date(dateStr).toLocaleString();
        } catch {
            return dateStr;
        }
    };

    const hasValue = (value: any): boolean => {
        if (value === null || value === undefined) return false;
        if (typeof value === "string") {
            const trimmed = value.trim();
            return trimmed.length > 0 && trimmed.toLowerCase() !== "n/a" && trimmed.toLowerCase() !== "unknown";
        }
        if (Array.isArray(value)) return value.length > 0;
        if (typeof value === "object") return Object.keys(value).length > 0;
        return true;
    };

    const labelOrNotEmbedded = (value: any) => (hasValue(value) ? String(value) : "Not embedded");

    const getGpsCoords = (gps: Record<string, any> | null | undefined) => {
        if (!gps || typeof gps !== 'object') return null;
        const latRaw = gps.latitude ?? gps.lat ?? gps.GPSLatitude ?? gps.gps_latitude ?? gps.Latitude;
        const lonRaw = gps.longitude ?? gps.lon ?? gps.lng ?? gps.GPSLongitude ?? gps.gps_longitude ?? gps.Longitude;
        const lat = typeof latRaw === "number" ? latRaw : parseFloat(String(latRaw));
        const lon = typeof lonRaw === "number" ? lonRaw : parseFloat(String(lonRaw));
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
        return { latitude: lat, longitude: lon };
    };

    const parseOverlayGps = (burned?: any) => {
        const raw = burned?.parsed_data?.gps;
        if (!raw) return null;
        const lat = typeof raw.latitude === 'number' ? raw.latitude : parseFloat(String(raw.latitude));
        const lon = typeof raw.longitude === 'number' ? raw.longitude : parseFloat(String(raw.longitude));
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
        return { latitude: lat, longitude: lon, google_maps_url: raw.google_maps_url };
    };

    const gpsCoords = getGpsCoords(metadata.gps);
    const overlayGps = parseOverlayGps(metadata.burned_metadata);
    const hasGps = !!gpsCoords;
    const gpsMapUrl = gpsCoords
        ? (metadata.gps?.google_maps_url || `https://maps.google.com/?q=${gpsCoords.latitude},${gpsCoords.longitude}`)
        : overlayGps
        ? (overlayGps.google_maps_url || `https://maps.google.com/?q=${overlayGps.latitude},${overlayGps.longitude}`)
        : '';
    const parseWhatsappFilenameDate = (name?: string) => {
        if (!name) return null;
        const match = name.match(/WhatsApp Image (\d{4})-(\d{2})-(\d{2}) at (\d{2})\.(\d{2})\.(\d{2})/i);
        if (!match) return null;
        const [, year, month, day, hour, minute, second] = match;
        return new Date(`${year}-${month}-${day}T${hour}:${minute}:${second}`);
    };
    const parseExifDate = (value?: string | null) => {
        if (!value) return null;
        // Handle EXIF format: YYYY:MM:DD HH:MM:SS
        const match = value.match(/(\\d{4}):(\\d{2}):(\\d{2})[ T](\\d{2}):(\\d{2}):(\\d{2})/);
        if (match) {
            const [, y, m, d, hh, mm, ss] = match;
            return new Date(`${y}-${m}-${d}T${hh}:${mm}:${ss}`);
        }
        const dt = new Date(value);
        return Number.isNaN(dt.getTime()) ? null : dt;
    };
    const filenameDate = parseWhatsappFilenameDate(metadata.filename);
    const captureDateFromExif = parseExifDate(metadata.exif?.DateTimeOriginal || metadata.exif?.CreateDate);
    const captureDateLabel = captureDateFromExif
        ? "CAPTURE DATE"
        : filenameDate
        ? "FILENAME DATE"
        : "CAPTURE DATE";
    const captureDateValue = captureDateFromExif
        ? captureDateFromExif.toISOString()
        : filenameDate
        ? filenameDate.toISOString()
        : "Not embedded";
    const localModifiedValue = metadata.client_last_modified_iso || null;

    const embeddedGpsState = hasGps ? "embedded" : overlayGps ? "overlay" : "none";
    const burnedTimestamp = metadata.burned_metadata?.parsed_data?.timestamp || null;
    const hashSha256 = metadata.hashes?.sha256 || metadata.file_integrity?.sha256 || null;
    const fieldsExtracted = metadata.fields_extracted ?? null;
    const processingMs = metadata.processing_ms ?? null;
    const software = metadata.exif?.Software || null;

    const highlights: Array<{ text: string; chip: "Privacy" | "Authenticity" | "Photography"; detail?: string }> = [];
    if (captureDateValue !== "Not embedded") {
        highlights.push({ text: "Capture time found.", chip: "Photography", detail: captureDateLabel === "FILENAME DATE" ? "From filename" : "From EXIF" });
    } else {
        highlights.push({ text: "No embedded capture time found (common after sharing apps).", chip: "Photography" });
    }
    if (embeddedGpsState === "embedded") {
        highlights.push({ text: "Location is embedded in EXIF.", chip: "Privacy" });
    } else if (embeddedGpsState === "overlay") {
        highlights.push({ text: "Location not embedded in EXIF, but found in overlay text (pixels).", chip: "Privacy" });
    } else {
        highlights.push({ text: "Location not embedded in this file.", chip: "Privacy" });
    }
    if (hasValue(metadata.exif?.Make) || hasValue(metadata.exif?.Model)) {
        highlights.push({ text: `Device detected: ${[metadata.exif?.Make, metadata.exif?.Model].filter(Boolean).join(" ")}`, chip: "Photography" });
    }
    if (hasValue(software)) {
        highlights.push({ text: `Software tag present: ${software}`, chip: "Authenticity" });
    } else {
        highlights.push({ text: "No editing software tag found (inconclusive).", chip: "Authenticity" });
    }
    if (hasValue(hashSha256)) {
        highlights.push({ text: "SHA-256 hash computed for integrity.", chip: "Authenticity" });
    }

    return (
        <Layout showHeader={true} showFooter={true}>
            <div className="min-h-screen bg-[#0B0C10] text-white pt-20 pb-20">
                <div className="container mx-auto px-4 max-w-4xl">

                    {/* Header */}
                    <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                            <h1 className="text-2xl font-bold flex items-center gap-2">
                                <FileImage className="w-6 h-6 text-primary" />
                                {metadata.filename}
                            </h1>
                            <p className="text-slate-400 text-sm font-mono mt-1">
                                {metadata.filesize} • {metadata.mime_type}
                            </p>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-3">
                            <Button
                                variant="outline"
                                onClick={() => navigate('/images_mvp')}
                                className="border-white/10 hover:bg-white/5"
                            >
                                Analyze Another Photo
                            </Button>
                            <Button
                                variant="outline"
                                onClick={handleDownloadJson}
                                disabled={!canExport}
                                className="border-white/10 hover:bg-white/5"
                            >
                                <Share2 className="w-4 h-4 mr-2" />
                                Download JSON
                            </Button>
                        </div>
                    </div>
                    {!canExport && (
                        <p className="text-xs text-slate-500 mb-6">
                            JSON export is available after the trial. Unlock credits to download the full report.
                        </p>
                    )}

                    {/* Trial Warning Banner */}
                    {isTrialLimited && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="mb-8 p-4 bg-primary/10 border border-primary/20 rounded-lg flex items-start gap-3"
                        >
                            <ShieldAlert className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                            <div>
                                <h4 className="font-bold text-primary text-sm mb-1">Trial Report Active</h4>
                                <p className="text-slate-300 text-xs leading-relaxed">
                                    You are viewing a limited trial report. Raw IPTC and XMP data has been summarized or redacted.
                                    Upgrade to Professional for full forensic access.
                                </p>
                            </div>
                            {/* TODO: Add Upgrade Button if this was a paid feature MVP */}
                        </motion.div>
                    )}

                    <Card className="bg-[#121217] border-white/5 mb-6">
                        <CardHeader>
                            <CardTitle className="text-sm font-mono text-slate-400">HIGHLIGHTS</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {highlights.slice(0, 6).map((h, idx) => (
                                <div key={idx} className="flex items-start justify-between gap-3">
                                    <div className="text-sm text-slate-200">{h.text}</div>
                                    <span className="shrink-0 text-[10px] px-2 py-1 rounded-full bg-white/5 border border-white/10 text-slate-300 font-mono">
                                        {h.chip}
                                    </span>
                                </div>
                            ))}
                            {(fieldsExtracted || processingMs) && (
                                <div className="pt-2 text-xs text-slate-500 font-mono">
                                    {fieldsExtracted ? `${fieldsExtracted} fields extracted` : null}
                                    {fieldsExtracted && processingMs ? " • " : null}
                                    {processingMs ? `${Math.round(processingMs)} ms` : null}
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    <Tabs defaultValue="privacy" className="w-full">
                        <TabsList className="bg-[#121217] border border-white/5">
                            <TabsTrigger value="privacy">Privacy</TabsTrigger>
                            <TabsTrigger value="authenticity">Authenticity</TabsTrigger>
                            <TabsTrigger value="photography">Photography</TabsTrigger>
                            <TabsTrigger value="raw" disabled={!canExport}>Raw</TabsTrigger>
                        </TabsList>

                        <TabsContent value="privacy" className="mt-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Location Card */}
                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
                                            <MapPin className="w-4 h-4" /> LOCATION DATA
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        {hasGps && gpsCoords ? (
                                            <div className="space-y-4">
                                                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-200 text-sm flex items-center gap-2">
                                                    <ShieldAlert className="w-5 h-5" />
                                                    <span>Location Found! This photo contains GPS coordinates.</span>
                                                </div>
                                                <div className="grid grid-cols-2 gap-4 text-sm font-mono text-white">
                                                    <div>
                                                        <span className="text-slate-500 block text-xs">LATITUDE</span>
                                                        {gpsCoords.latitude}
                                                    </div>
                                                    <div>
                                                        <span className="text-slate-500 block text-xs">LONGITUDE</span>
                                                        {gpsCoords.longitude}
                                                    </div>
                                                </div>
                                                {gpsMapUrl && (
                                                    <a
                                                        href={gpsMapUrl}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="block w-full py-2 bg-white/5 hover:bg-white/10 text-center rounded text-sm transition-colors text-primary"
                                                    >
                                                        View on Google Maps <ArrowRight className="w-3 h-3 inline ml-1" />
                                                    </a>
                                                )}
                                            </div>
                                        ) : overlayGps ? (
                                            <div className="space-y-4">
                                                <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-200 text-sm flex items-center gap-2">
                                                    <ShieldAlert className="w-5 h-5" />
                                                    <span>Overlay GPS detected from burned-in text (pixels).</span>
                                                </div>
                                                <div className="grid grid-cols-2 gap-4 text-sm font-mono text-white">
                                                    <div>
                                                        <span className="text-slate-500 block text-xs">LATITUDE (Overlay)</span>
                                                        {overlayGps.latitude}
                                                    </div>
                                                    <div>
                                                        <span className="text-slate-500 block text-xs">LONGITUDE (Overlay)</span>
                                                        {overlayGps.longitude}
                                                    </div>
                                                </div>
                                                {gpsMapUrl && (
                                                    <a
                                                        href={gpsMapUrl}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="block w-full py-2 bg-white/5 hover:bg-white/10 text-center rounded text-sm transition-colors text-primary"
                                                    >
                                                        View on Google Maps <ArrowRight className="w-3 h-3 inline ml-1" />
                                                    </a>
                                                )}
                                            </div>
                                        ) : (
                                            <div className="py-8 text-center">
                                                <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3 opacity-20" />
                                                <p className="text-emerald-500 font-bold">Location Not Embedded</p>
                                                <p className="text-slate-500 text-xs mt-1">No EXIF GPS coordinates were found in this file.</p>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>

                                {/* Device Info */}
                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
                                            <Camera className="w-4 h-4" /> DEVICE INFORMATION
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div className="grid grid-cols-1 gap-4">
                                            <div className="pb-3 border-b border-white/5">
                                                <span className="text-slate-500 block text-xs font-mono mb-1">CAMERA MAKE</span>
                                                <span className="text-white font-medium">{labelOrNotEmbedded(metadata.exif?.Make)}</span>
                                            </div>
                                            <div className="pb-3 border-b border-white/5">
                                                <span className="text-slate-500 block text-xs font-mono mb-1">CAMERA MODEL</span>
                                                <span className="text-white font-medium">{labelOrNotEmbedded(metadata.exif?.Model)}</span>
                                            </div>
                                            {hasValue(software) && (
                                                <div>
                                                    <span className="text-slate-500 block text-xs font-mono mb-1">SOFTWARE</span>
                                                    <span className="text-white font-medium">{software}</span>
                                                </div>
                                            )}
                                        </div>
                                    </CardContent>
                                </Card>

                                {/* Timestamps */}
                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
                                            <Calendar className="w-4 h-4" /> TIMESTAMPS
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div className="grid grid-cols-1 gap-4">
                                            <div className="pb-3 border-b border-white/5">
                                                <span className="text-slate-500 block text-xs font-mono mb-1">{captureDateLabel}</span>
                                                <span className="text-white font-medium">
                                                    {captureDateValue === "Not embedded" ? "Not embedded" : formatDate(captureDateValue)}
                                                </span>
                                            </div>
                                            {hasValue(burnedTimestamp) && (
                                                <div className="pb-3 border-b border-white/5">
                                                    <span className="text-slate-500 block text-xs font-mono mb-1">OVERLAY TIMESTAMP</span>
                                                    <span className="text-white font-medium">{burnedTimestamp}</span>
                                                </div>
                                            )}
                                            <div>
                                                <span className="text-slate-500 block text-xs font-mono mb-1">LOCAL FILE MODIFIED</span>
                                                <span className="text-white font-medium">{formatDate(localModifiedValue || undefined)}</span>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>

                                {/* Hidden Data Summary */}
                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
                                            <Lock className="w-4 h-4" /> HIDDEN DATA
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <ul className="space-y-3">
                                            <li className="flex justify-between text-sm">
                                                <span className="text-slate-400">MakerNotes</span>
                                                <span className={metadata.exif?.MakerNote || (Object.keys(metadata.exif || {}).some((k) => k.toLowerCase().includes('maker'))) ? "text-red-400" : "text-slate-600"}>
                                                    {metadata.exif?.MakerNote || (Object.keys(metadata.exif || {}).some((k) => k.toLowerCase().includes('maker'))) ? "Detected" : "Not embedded"}
                                                </span>
                                            </li>
                                            <li className="flex justify-between text-sm">
                                                <span className="text-slate-400">Serial Numbers</span>
                                                <span className="text-slate-600">{metadata.exif?.BodySerialNumber || metadata.exif?.LensSerialNumber || metadata.exif?.SerialNumber || "Not embedded"}</span>
                                            </li>
                                            <li className="flex justify-between text-sm">
                                                <span className="text-slate-400">Color Profile</span>
                                                <span className="text-white">{metadata.exif?.ColorSpace === 1 ? 'sRGB' : (metadata.exif?.ColorSpace || 'Unspecified')}</span>
                                            </li>
                                        </ul>
                                    </CardContent>
                                </Card>

                                {/* Overlay / Burned Metadata */}
                                {metadata.burned_metadata?.has_burned_metadata && (
                                    <Card className="bg-[#121217] border-white/5">
                                        <CardHeader>
                                            <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
                                                <ShieldAlert className="w-4 h-4" /> OVERLAY TEXT (OCR)
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-3 text-sm">
                                            <div className="text-slate-300">
                                                <span className="block text-xs text-slate-500 mb-1">EXTRACTED TEXT</span>
                                                <span className="block bg-white/5 rounded p-2 max-h-32 overflow-y-auto">
                                                    {metadata.burned_metadata.extracted_text?.slice(0, 400) || 'Text not available'}
                                                </span>
                                            </div>
                                            {metadata.burned_metadata.parsed_data?.gps && (
                                                <div className="grid grid-cols-2 gap-4 font-mono">
                                                    <div>
                                                        <span className="text-slate-500 block text-xs">LATITUDE (Overlay)</span>
                                                        {metadata.burned_metadata.parsed_data.gps.latitude}
                                                    </div>
                                                    <div>
                                                        <span className="text-slate-500 block text-xs">LONGITUDE (Overlay)</span>
                                                        {metadata.burned_metadata.parsed_data.gps.longitude}
                                                    </div>
                                                </div>
                                            )}
                                            {metadata.burned_metadata.parsed_data?.timestamp && (
                                                <div className="text-slate-300">
                                                    <span className="text-slate-500 block text-xs">TIMESTAMP (Overlay)</span>
                                                    <span>{metadata.burned_metadata.parsed_data.timestamp}</span>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                )}

                                {/* Integrity */}
                                {(hasValue(metadata.hashes) || hasValue(metadata.file_integrity)) && (
                                    <Card className="bg-[#121217] border-white/5">
                                        <CardHeader>
                                            <CardTitle className="flex items-center gap-2 text-sm font-mono text-slate-400">
                                                <Lock className="w-4 h-4" /> INTEGRITY
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-3 text-sm font-mono">
                                            <div className="flex justify-between gap-3">
                                                <span className="text-slate-400">SHA256</span>
                                                <span className="text-slate-200 truncate max-w-[60%]">{labelOrNotEmbedded(metadata.hashes?.sha256 || metadata.file_integrity?.sha256)}</span>
                                            </div>
                                            <div className="flex justify-between gap-3">
                                                <span className="text-slate-400">MD5</span>
                                                <span className="text-slate-200 truncate max-w-[60%]">{labelOrNotEmbedded(metadata.hashes?.md5 || metadata.file_integrity?.md5)}</span>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}
                            </div>
                        </TabsContent>

                        <TabsContent value="authenticity" className="mt-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="text-sm font-mono text-slate-400">AUTHENTICITY SIGNALS</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-3 text-sm">
                                        <div className="text-slate-300">
                                            <span className="text-slate-500 block text-xs font-mono mb-1">EDIT SOFTWARE</span>
                                            <span className="text-white">{hasValue(software) ? software : "No tag found (inconclusive)"}</span>
                                        </div>
                                        <div className="text-slate-300">
                                            <span className="text-slate-500 block text-xs font-mono mb-1">METADATA STATE</span>
                                            <span className="text-white">{metadata.metadata_comparison?.summary?.overall_status || "Unknown"}</span>
                                        </div>
                                        {metadata.metadata_comparison?.warnings?.length ? (
                                            <ul className="list-disc pl-5 text-slate-400 text-xs space-y-1">
                                                {metadata.metadata_comparison.warnings.slice(0, 3).map((w, i) => (
                                                    <li key={i}>{w}</li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <div className="text-xs text-slate-500">No additional authenticity warnings found.</div>
                                        )}
                                    </CardContent>
                                </Card>

                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="text-sm font-mono text-slate-400">FINGERPRINTS</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-3 text-sm font-mono">
                                        {hasValue(metadata.perceptual_hashes?.phash) && (
                                            <div className="flex justify-between gap-3">
                                                <span className="text-slate-400">pHash</span>
                                                <span className="text-slate-200 truncate max-w-[60%]">{metadata.perceptual_hashes.phash}</span>
                                            </div>
                                        )}
                                        {hasValue(metadata.perceptual_hashes?.dhash) && (
                                            <div className="flex justify-between gap-3">
                                                <span className="text-slate-400">dHash</span>
                                                <span className="text-slate-200 truncate max-w-[60%]">{metadata.perceptual_hashes.dhash}</span>
                                            </div>
                                        )}
                                        {!hasValue(metadata.perceptual_hashes?.phash) && !hasValue(metadata.perceptual_hashes?.dhash) && (
                                            <div className="text-xs text-slate-500">Perceptual hashes not available for this file.</div>
                                        )}
                                    </CardContent>
                                </Card>
                            </div>
                        </TabsContent>

                        <TabsContent value="photography" className="mt-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="text-sm font-mono text-slate-400">CAMERA SETTINGS</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-3 text-sm">
                                        {hasValue(metadata.normalized?.exposure_triangle) && (
                                            <div className="text-slate-300">
                                                <span className="text-slate-500 block text-xs font-mono mb-1">EXPOSURE</span>
                                                <span className="text-white">{metadata.normalized?.exposure_triangle}</span>
                                            </div>
                                        )}
                                        <div className="grid grid-cols-2 gap-4 font-mono text-xs">
                                            {hasValue(metadata.exif?.ISO) && (
                                                <div>
                                                    <span className="text-slate-500 block">ISO</span>
                                                    <span className="text-slate-200">{metadata.exif.ISO}</span>
                                                </div>
                                            )}
                                            {hasValue(metadata.exif?.FNumber) && (
                                                <div>
                                                    <span className="text-slate-500 block">APERTURE</span>
                                                    <span className="text-slate-200">f/{metadata.exif.FNumber}</span>
                                                </div>
                                            )}
                                            {hasValue(metadata.exif?.ExposureTime) && (
                                                <div>
                                                    <span className="text-slate-500 block">SHUTTER</span>
                                                    <span className="text-slate-200">{metadata.exif.ExposureTime}s</span>
                                                </div>
                                            )}
                                            {hasValue(metadata.exif?.FocalLength) && (
                                                <div>
                                                    <span className="text-slate-500 block">FOCAL LENGTH</span>
                                                    <span className="text-slate-200">{metadata.exif.FocalLength}mm</span>
                                                </div>
                                            )}
                                        </div>
                                        {!hasValue(metadata.exif?.ISO) && !hasValue(metadata.exif?.FNumber) && !hasValue(metadata.exif?.ExposureTime) && !hasValue(metadata.exif?.FocalLength) && (
                                            <div className="text-xs text-slate-500">No camera setting fields embedded.</div>
                                        )}
                                    </CardContent>
                                </Card>

                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="text-sm font-mono text-slate-400">IMAGE INFO</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-3 text-sm">
                                        <div className="text-slate-300">
                                            <span className="text-slate-500 block text-xs font-mono mb-1">DIMENSIONS</span>
                                            <span className="text-white">{metadata.exif?.ImageWidth && (metadata.exif?.ImageHeight || metadata.exif?.ImageLength) ? `${metadata.exif.ImageWidth} × ${(metadata.exif.ImageHeight || metadata.exif.ImageLength)}` : "Not available"}</span>
                                        </div>
                                        <div className="text-slate-300">
                                            <span className="text-slate-500 block text-xs font-mono mb-1">MEGAPIXELS</span>
                                            <span className="text-white">{metadata.calculated?.megapixels || "Not available"}</span>
                                        </div>
                                        <div className="text-slate-300">
                                            <span className="text-slate-500 block text-xs font-mono mb-1">COLOR SPACE</span>
                                            <span className="text-white">{metadata.exif?.ColorSpace === 1 ? "sRGB" : (metadata.exif?.ColorSpace || "Unspecified")}</span>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        </TabsContent>

                        <TabsContent value="raw" className="mt-6">
                            {!canExport ? (
                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="text-sm font-mono text-slate-400">RAW JSON (LOCKED)</CardTitle>
                                    </CardHeader>
                                    <CardContent className="text-sm text-slate-400">
                                        Raw JSON view is available after the trial. Purchase credits to unlock.
                                    </CardContent>
                                </Card>
                            ) : (
                                <Card className="bg-[#121217] border-white/5">
                                    <CardHeader>
                                        <CardTitle className="text-sm font-mono text-slate-400">RAW JSON</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <pre className="text-xs text-slate-200 bg-black/30 border border-white/5 rounded p-3 overflow-auto max-h-[520px]">
                                            {JSON.stringify(metadata, null, 2)}
                                        </pre>
                                    </CardContent>
                                </Card>
                            )}
                        </TabsContent>
                    </Tabs>
                </div>
            </div>
        </Layout>
    );
}
