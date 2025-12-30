import React, { useState, useCallback } from "react";
import { useLocation } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, File, CheckCircle2, Loader2, Lock, Cpu, Scan, Database } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface UploadZoneProps {
  onUploadComplete?: () => void;
}

export function UploadZone() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStage, setProcessingStage] = useState("Initializing...");
  const [, setLocation] = useLocation();

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      startUpload(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      startUpload(e.target.files[0]);
    }
  }, []);

  const startUpload = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);

    const stages = [
      "Uploading file to secure enclave...",
      "Analyzing file header...",
      "Extracting EXIF data...",
      "Parsing MakerNotes...",
      "Decoding GPS coordinates...",
      "Scanning for hidden XMP...",
      "Generating forensic report..."
    ];

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append("file", file);

      // Simulate progress during upload
      let progress = 0;
      const progressInterval = setInterval(() => {
        if (progress < 90) {
          progress += Math.random() * 10;
          setUploadProgress(Math.min(progress, 90));

          // Update stage text based on progress
          const stageIndex = Math.floor((progress / 90) * stages.length);
          if (stages[stageIndex]) setProcessingStage(stages[stageIndex]);
        }
      }, 200);

      // Make actual API call to extract metadata
      const response = await fetch("/api/extract", {
        method: "POST",
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const metadata = await response.json();

      // Complete progress
      setUploadProgress(100);
      setProcessingStage("Extraction complete!");

      // Store metadata in sessionStorage for results page
      sessionStorage.setItem("currentMetadata", JSON.stringify(metadata));

      // Navigate to results
      setTimeout(() => {
        setLocation("/results");
      }, 500);

    } catch (error) {
      console.error("Upload error:", error);
      alert("Failed to extract metadata. Please try again.");
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      <AnimatePresence mode="wait">
        {!isUploading ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className={cn(
              "relative group rounded-xl border border-dashed transition-all duration-300 ease-in-out cursor-pointer overflow-hidden backdrop-blur-sm",
              isDragging
                ? "border-primary bg-primary/5 shadow-[0_0_30px_rgba(99,102,241,0.2)]"
                : "border-white/10 bg-white/5 hover:border-primary/50 hover:bg-white/10"
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById("file-upload")?.click()}
          >
            <input
              id="file-upload"
              type="file"
              className="hidden"
              onChange={handleFileSelect}
            />

            {/* Tech Decoration Lines */}
            <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-white/20 group-hover:border-primary transition-colors" />
            <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-white/20 group-hover:border-primary transition-colors" />
            <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-white/20 group-hover:border-primary transition-colors" />
            <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-white/20 group-hover:border-primary transition-colors" />

            <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
              <div className={cn(
                "mb-8 p-4 rounded-full bg-white/5 transition-all duration-300 group-hover:scale-110 group-hover:bg-primary/20",
                isDragging && "bg-primary/20 scale-110"
              )}>
                <Upload className={cn("w-8 h-8 text-slate-400 group-hover:text-primary transition-colors", isDragging && "text-primary")} />
              </div>
              <h3 className="text-xl font-bold text-white mb-2 tracking-tight">
                Upload Evidence
              </h3>
              <p className="text-slate-400 mb-8 max-w-xs mx-auto text-sm">
                Drag & drop media files here or browse to start.
                <br />
                <span className="text-slate-500 text-xs mt-2 block">Supports 400+ formats including RAW, HEIC, MP4</span>
              </p>
              <Button className="h-10 px-8 bg-white/10 text-white hover:bg-primary hover:text-black border border-white/20 hover:border-primary font-bold text-sm rounded transition-all duration-300 shadow-lg">
                Select File
              </Button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-black/40 backdrop-blur-md rounded-xl border border-primary/20 shadow-2xl p-8 relative overflow-hidden"
          >
            {/* Scanning line effect */}
            <div className="absolute inset-0 scanline opacity-20 pointer-events-none"></div>

            <div className="flex items-center gap-4 mb-8 relative z-10">
              <div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
                <Cpu className="w-6 h-6 text-primary animate-pulse" />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="font-mono font-bold text-white flex items-center gap-2">
                  PROCESSING <span className="animate-pulse">_</span>
                </h4>
                <p className="text-xs font-mono text-primary/80 truncate">{processingStage}</p>
              </div>
              <div className="text-right shrink-0 min-w-[60px]">
                <span className="text-2xl font-bold text-white font-mono">{Math.round(uploadProgress)}%</span>
              </div>
            </div>

            <div className="space-y-2 relative z-10">
              <div className="h-1 w-full bg-white/10 overflow-hidden">
                <motion.div
                  className="h-full bg-primary shadow-[0_0_10px_rgba(99,102,241,0.5)]"
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  transition={{ ease: "linear", duration: 0.1 }}
                />
              </div>
              <div className="flex justify-between text-[10px] font-mono text-slate-500 uppercase">
                <span>Sector 01: Header</span>
                <span>Sector 02: Body</span>
                <span>Sector 03: Analysis</span>
              </div>
            </div>

            <div className="mt-8 grid grid-cols-3 gap-2 relative z-10">
              <div className="bg-white/5 p-2 rounded border border-white/5 text-center">
                <Database className="w-4 h-4 text-slate-500 mx-auto mb-1" />
                <span className="text-[10px] text-slate-400 block">7200 Fields</span>
              </div>
              <div className="bg-white/5 p-2 rounded border border-white/5 text-center">
                <Scan className="w-4 h-4 text-slate-500 mx-auto mb-1" />
                <span className="text-[10px] text-slate-400 block">Deep Scan</span>
              </div>
              <div className="bg-white/5 p-2 rounded border border-white/5 text-center">
                <Lock className="w-4 h-4 text-slate-500 mx-auto mb-1" />
                <span className="text-[10px] text-slate-400 block">Encrypted</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
