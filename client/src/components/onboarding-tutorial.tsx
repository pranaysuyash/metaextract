import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  ChevronRight,
  ChevronLeft,
  Upload,
  Search,
  Download,
  Zap,
  CheckCircle2,
  Play,
  X,
  ArrowRight,
  FileText,
  Camera,
  MapPin,
  Hash
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

interface TutorialStep {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  content: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface OnboardingTutorialProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
  userTier: string;
}

export function OnboardingTutorial({
  isOpen,
  onClose,
  onComplete,
  userTier
}: OnboardingTutorialProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const normalizedTier =
    userTier === 'starter'
      ? 'professional'
      : userTier === 'premium'
      ? 'forensic'
      : userTier === 'super'
      ? 'enterprise'
      : userTier;

  const steps: TutorialStep[] = [
    {
      id: "welcome",
      title: "Welcome to MetaExtract",
      description: "Your forensic-grade metadata extraction platform",
      icon: Zap,
      content: (
        <div className="space-y-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <Zap className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Extract Hidden Data</h3>
            <p className="text-muted-foreground">
              Uncover 7,000+ metadata fields from images, videos, audio, and documents.
              Used by forensic professionals, journalists, and photographers worldwide.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="text-center p-3 bg-muted/50 rounded-lg">
              <Camera className="w-6 h-6 text-blue-500 mx-auto mb-2" />
              <p className="text-sm font-medium">Camera Data</p>
              <p className="text-xs text-muted-foreground">EXIF, MakerNotes</p>
            </div>
            <div className="text-center p-3 bg-muted/50 rounded-lg">
              <MapPin className="w-6 h-6 text-green-500 mx-auto mb-2" />
              <p className="text-sm font-medium">GPS Location</p>
              <p className="text-xs text-muted-foreground">Coordinates, Maps</p>
            </div>
            <div className="text-center p-3 bg-muted/50 rounded-lg">
              <Hash className="w-6 h-6 text-purple-500 mx-auto mb-2" />
              <p className="text-sm font-medium">File Integrity</p>
              <p className="text-xs text-muted-foreground">MD5, SHA256</p>
            </div>
            <div className="text-center p-3 bg-muted/50 rounded-lg">
              <FileText className="w-6 h-6 text-orange-500 mx-auto mb-2" />
              <p className="text-sm font-medium">Forensic Reports</p>
              <p className="text-xs text-muted-foreground">Court-ready PDFs</p>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "upload",
      title: "Upload Your Files",
      description: "Drag & drop or click to select files for analysis",
      icon: Upload,
      content: (
        <div className="space-y-4">
          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
            <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h4 className="font-medium mb-2">Drop files here</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Or click to browse your computer
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              <Badge variant="outline">Images</Badge>
              <Badge variant="outline">Video</Badge>
              <Badge variant="outline">Audio</Badge>
              <Badge variant="outline">PDF</Badge>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h5 className="font-medium text-blue-900 mb-2">Your Current Plan: {normalizedTier}</h5>
            <div className="text-sm text-blue-800">
              {normalizedTier === 'free' && (
                <>
                  <p>• Up to 10MB per file</p>
                  <p>• Images only (JPEG, PNG, GIF, WebP)</p>
                  <p>• Basic EXIF data (~200 fields)</p>
                </>
              )}
              {normalizedTier === 'professional' && (
                <>
                  <p>• Up to 100MB per file</p>
                  <p>• Images + RAW + HEIC formats</p>
                  <p>• 1,000+ metadata fields including GPS</p>
                </>
              )}
              {normalizedTier === 'forensic' && (
                <>
                  <p>• Up to 500MB per file</p>
                  <p>• All formats including video</p>
                  <p>• 15,000+ fields with advanced forensics</p>
                </>
              )}
              {normalizedTier === 'enterprise' && (
                <>
                  <p>• Up to 2GB per file</p>
                  <p>• All formats + scientific/medical metadata</p>
                  <p>• 45,000+ fields with full forensic analysis</p>
                </>
              )}
            </div>
          </div>
        </div>
      )
    },
    {
      id: "analyze",
      title: "Metadata Extraction",
      description: "Our engine analyzes your files and extracts hidden data",
      icon: Search,
      content: (
        <div className="space-y-4">
          <div className="text-center">
            <div className="relative w-24 h-24 mx-auto mb-4">
              <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
              <Search className="absolute inset-0 w-8 h-8 text-primary m-auto" />
            </div>
            <h4 className="font-medium mb-2">Processing Your File</h4>
            <p className="text-sm text-muted-foreground">
              Our forensic engine extracts metadata in seconds
            </p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <div>
                <p className="font-medium text-green-900">File Analysis</p>
                <p className="text-sm text-green-700">Format detection and validation</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <div>
                <p className="font-medium text-blue-900">Metadata Extraction</p>
                <p className="text-sm text-blue-700">Extracting EXIF, GPS, and technical data</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-muted/50 border border-muted rounded-lg">
              <div className="w-5 h-5 border-2 border-muted-foreground/30 rounded-full"></div>
              <div>
                <p className="font-medium text-muted-foreground">Report Generation</p>
                <p className="text-sm text-muted-foreground">Formatting results for display</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "explore",
      title: "Explore Results",
      description: "Navigate through extracted metadata organized by category",
      icon: FileText,
      content: (
        <div className="space-y-4">
          <div className="border rounded-lg overflow-hidden">
            <div className="bg-muted/50 p-3 border-b">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="ml-2 text-sm font-mono">IMG_2847.jpg</span>
              </div>
            </div>

            <div className="p-4 space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Camera className="w-4 h-4 text-blue-500" />
                <span className="font-medium">Camera & EXIF</span>
                <Badge variant="outline" className="ml-auto">45 fields</Badge>
              </div>

              <div className="flex items-center gap-2 text-sm">
                <MapPin className="w-4 h-4 text-green-500" />
                <span className="font-medium">GPS Location</span>
                <Badge variant="outline" className="ml-auto">8 fields</Badge>
              </div>

              <div className="flex items-center gap-2 text-sm">
                <Hash className="w-4 h-4 text-purple-500" />
                <span className="font-medium">File Integrity</span>
                <Badge variant="outline" className="ml-auto">4 fields</Badge>
              </div>

              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="w-4 h-4" />
                <span className="font-medium">MakerNotes</span>
                <Badge variant="outline" className="ml-auto bg-yellow-100">Locked</Badge>
              </div>
            </div>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <h5 className="font-medium text-amber-900 mb-2">💡 Pro Tip</h5>
            <p className="text-sm text-amber-800">
              Use the search box to quickly find specific metadata fields.
              Try searching for "GPS", "camera", or "date".
            </p>
          </div>
        </div>
      )
    },
    {
      id: "export",
      title: "Export & Share",
      description: "Download results in multiple formats for your workflow",
      icon: Download,
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-3">
            <div className="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium">JSON Export</p>
                <p className="text-sm text-muted-foreground">Complete metadata for developers</p>
              </div>
              <ArrowRight className="w-4 h-4 text-muted-foreground" />
            </div>

            <div className="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-green-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium">CSV Export</p>
                <p className="text-sm text-muted-foreground">Spreadsheet-friendly format</p>
              </div>
              <ArrowRight className="w-4 h-4 text-muted-foreground" />
            </div>

            <div className="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-red-600" />
              </div>
              <div className="flex-1">
                <p className="font-medium">PDF Report</p>
                <p className="text-sm text-muted-foreground">Court-ready forensic documentation</p>
              </div>
              <Badge variant="outline" className="bg-yellow-100">Pro</Badge>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h5 className="font-medium text-green-900 mb-2">🔒 Privacy Guarantee</h5>
            <p className="text-sm text-green-800">
              Your files are processed in memory and permanently deleted after analysis.
              We never store your data.
            </p>
          </div>
        </div>
      )
    }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCompletedSteps(prev => new Set([...prev, currentStep]));
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToStep = (stepIndex: number) => {
    setCurrentStep(stepIndex);
  };

  const handleComplete = () => {
    setCompletedSteps(prev => new Set([...prev, currentStep]));
    onComplete();
    onClose();
  };

  const progress = ((currentStep + 1) / steps.length) * 100;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-background rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-primary" />
            </div>
            <div>
              <h2 className="font-semibold">Getting Started</h2>
              <p className="text-sm text-muted-foreground">
                Step {currentStep + 1} of {steps.length}
              </p>
            </div>
          </div>

          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Progress */}
        <div className="px-6 py-3 border-b">
          <Progress value={progress} className="h-2" />
          <div className="flex justify-between mt-2">
            {steps.map((step, index) => (
              <button
                key={step.id}
                onClick={() => goToStep(index)}
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium transition-colors",
                  index <= currentStep
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                )}
              >
                {completedSteps.has(index) ? (
                  <CheckCircle2 className="w-4 h-4" />
                ) : (
                  index + 1
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 min-h-[400px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              <div className="text-center mb-6">
                {(() => {
                  const IconComponent = steps[currentStep].icon;
                  return (
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <IconComponent className="w-6 h-6 text-primary" />
                    </div>
                  );
                })()}
                <h3 className="text-xl font-semibold mb-2">
                  {steps[currentStep].title}
                </h3>
                <p className="text-muted-foreground">
                  {steps[currentStep].description}
                </p>
              </div>

              {steps[currentStep].content}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-muted/50">
          <Button
            variant="outline"
            onClick={prevStep}
            disabled={currentStep === 0}
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={onClose}>
              Skip Tutorial
            </Button>

            <Button onClick={nextStep}>
              {currentStep === steps.length - 1 ? (
                <>
                  Get Started
                  <CheckCircle2 className="w-4 h-4 ml-2" />
                </>
              ) : (
                <>
                  Next
                  <ChevronRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
