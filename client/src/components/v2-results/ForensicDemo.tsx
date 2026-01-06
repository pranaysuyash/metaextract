import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Fingerprint, 
  Shield, 
  AlertTriangle, 
  Eye, 
  Camera, 
  Upload,
  Play,
  RotateCcw,
  Download,
  FileText,
  Settings,
  Zap
} from 'lucide-react';
import { ForensicAnalysis } from './ForensicAnalysis';
import { ProgressiveDisclosure } from './ProgressiveDisclosure';
import { KeyFindings } from './KeyFindings';
import { AuthenticityBadge, ForensicConfidenceIndicator } from './AuthenticityBadge';
import { cn } from '@/lib/utils';

// Demo data showcasing different forensic scenarios
const demoScenarios = {
  authentic: {
    title: 'Authentic Image',
    description: 'Clean, unedited photograph with complete metadata',
    forensicScore: 92,
    keyFindings: {
      when: 'January 15, 2025 at 2:30 PM',
      where: 'Central Park, New York',
      device: 'iPhone 15 Pro',
      edited: false,
      authenticity: 'Appears authentic',
      confidence: 'high' as const
    },
    forensicAnalysis: {
      steganography: {
        detected: false,
        confidence: 96,
        methodsChecked: ['LSB Analysis', 'DCT Transform', 'Echo Hiding', 'Spread Spectrum'],
        findings: ['No hidden data detected in any channel'],
        details: 'Comprehensive steganography analysis using multiple detection algorithms'
      },
      manipulation: {
        detected: false,
        confidence: 89,
        indicators: [],
        originalityScore: 94
      },
      aiDetection: {
        aiGenerated: false,
        confidence: 93,
        modelHints: [],
        detectionMethods: ['Frequency Analysis', 'Artifact Detection', 'Noise Pattern Analysis']
      },
      authenticityScore: 92
    }
  },
  
  suspicious: {
    title: 'Suspicious Image',
    description: 'Potential manipulation and AI generation detected',
    forensicScore: 34,
    keyFindings: {
      when: 'Unknown date and time',
      where: 'No location data',
      device: 'Unknown device',
      edited: true,
      authenticity: 'Suspicious - requires review',
      confidence: 'low' as const
    },
    forensicAnalysis: {
      steganography: {
        detected: true,
        confidence: 78,
        methodsChecked: ['LSB Analysis', 'DCT Transform'],
        findings: ['Potential hidden data in blue channel', 'Anomalous noise patterns detected'],
        details: 'Evidence of data hiding techniques'
      },
      manipulation: {
        detected: true,
        confidence: 82,
        indicators: [
          {
            type: 'Clone Detection',
            severity: 'high' as const,
            description: 'Evidence of cloning tool usage in upper right region',
            confidence: 85
          },
          {
            type: 'Resampling Artifacts',
            severity: 'medium' as const,
            description: 'Unusual resampling patterns suggest scaling operations',
            confidence: 73
          }
        ],
        originalityScore: 31
      },
      aiDetection: {
        aiGenerated: true,
        confidence: 76,
        modelHints: ['Midjourney v6', 'Stable Diffusion'],
        detectionMethods: ['GAN Artifact Detection', 'Frequency Analysis']
      },
      authenticityScore: 34
    }
  },
  
  questionable: {
    title: 'Questionable Image',
    description: 'Mixed signals - requires further investigation',
    forensicScore: 67,
    keyFindings: {
      when: 'January 10, 2025 at 4:15 PM (approximate)',
      where: 'Los Angeles, California (estimated)',
      device: 'Professional camera (model unclear)',
      edited: true,
      authenticity: 'Questionable - metadata inconsistencies',
      confidence: 'medium' as const
    },
    forensicAnalysis: {
      steganography: {
        detected: false,
        confidence: 64,
        methodsChecked: ['Basic LSB', 'DCT Transform'],
        findings: ['Inconclusive results due to compression artifacts'],
        details: 'Limited analysis possible due to image quality'
      },
      manipulation: {
        detected: false,
        confidence: 58,
        indicators: [
          {
            type: 'Compression Artifacts',
            severity: 'low' as const,
            description: 'Heavy compression may mask manipulation signs',
            confidence: 62
          }
        ],
        originalityScore: 71
      },
      aiDetection: {
        aiGenerated: false,
        confidence: 45,
        modelHints: [],
        detectionMethods: ['Basic Frequency Analysis']
      },
      authenticityScore: 67
    }
  }
};

interface ForensicDemoProps {
  className?: string;
  defaultScenario?: keyof typeof demoScenarios;
  showControls?: boolean;
  showComparison?: boolean;
}

export const ForensicDemo: React.FC<ForensicDemoProps> = ({
  className,
  defaultScenario = 'authentic',
  showControls = true,
  showComparison = false
}) => {
  const [activeScenario, setActiveScenario] = useState<keyof typeof demoScenarios>(defaultScenario);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const currentScenario = demoScenarios[activeScenario];

  const handleScenarioChange = (scenario: keyof typeof demoScenarios) => {
    setIsAnalyzing(true);
    setActiveScenario(scenario);
    
    // Simulate analysis delay
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 1500);
  };

  const handleReanalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 2000);
  };

  const progressiveDisclosureData = {
    keyFindings: currentScenario.keyFindings,
    quickDetails: {
      resolution: '12.2 megapixels',
      fileSize: '3.2 MB',
      cameraSettings: 'f/1.6, 1/120s, ISO 64',
      colorSpace: 'sRGB',
      dimensions: '4032 x 3024'
    },
    location: {
      latitude: 37.7749,
      longitude: -122.4194
    },
    advancedMetadata: {
      exif: {
        Make: 'Apple',
        Model: 'iPhone 15 Pro',
        Software: 'iOS 17.1'
      },
      fileSystem: {
        created: '2025-01-15T14:30:00Z',
        modified: '2025-01-15T14:30:00Z'
      }
    },
    forensicAnalysis: currentScenario.forensicAnalysis
  };

  return (
    <div className={cn("w-full space-y-6", className)}>
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3">
          <Fingerprint className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Forensic Analysis Demo
          </h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Explore advanced forensic analysis capabilities with different image scenarios. 
          See how our AI-powered detection identifies manipulation, steganography, and AI generation.
        </p>
      </div>

      {/* Scenario Controls */}
      {showControls && (
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white">Demo Scenarios</CardTitle>
            <p className="text-sm text-slate-300">Test different forensic analysis scenarios</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(demoScenarios).map(([key, scenario]) => (
                <Button
                  key={key}
                  variant={activeScenario === key ? "default" : "outline"}
                  onClick={() => handleScenarioChange(key as keyof typeof demoScenarios)}
                  disabled={isAnalyzing}
                  className={cn(
                    "justify-start text-left h-auto py-3 px-4",
                    scenario.forensicScore >= 80 && "border-emerald-500/50 text-emerald-300",
                    scenario.forensicScore >= 60 && scenario.forensicScore < 80 && "border-yellow-500/50 text-yellow-300",
                    scenario.forensicScore < 60 && "border-red-500/50 text-red-300"
                  )}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <div className={cn(
                        "w-3 h-3 rounded-full",
                        scenario.forensicScore >= 80 ? "bg-emerald-500" :
                        scenario.forensicScore >= 60 ? "bg-yellow-500" :
                        "bg-red-500"
                      )} />
                      <span className="font-medium">{scenario.title}</span>
                    </div>
                    <p className="text-xs text-slate-400">{scenario.description}</p>
                    <AuthenticityBadge score={scenario.forensicScore} variant="compact" />
                  </div>
                </Button>
              ))}
            </div>
            
            <div className="flex items-center justify-between pt-4 border-t border-white/10">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-yellow-500" />
                <span className="text-sm text-slate-300">
                  {isAnalyzing ? 'Analyzing...' : 'Analysis complete'}
                </span>
              </div>
              <Button
                variant="outline"
                onClick={handleReanalyze}
                disabled={isAnalyzing}
                className="gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Re-analyze
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Scenario Display */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Key Findings */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Key Findings
            </CardTitle>
            <p className="text-sm text-slate-300">{currentScenario.description}</p>
          </CardHeader>
          <CardContent>
            <KeyFindings
              findings={currentScenario.keyFindings}
              forensicScore={currentScenario.forensicScore}
              forensicAnalysis={currentScenario.forensicAnalysis}
              showForensicIndicators={true}
            />
          </CardContent>
        </Card>

        {/* Forensic Score */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Fingerprint className="w-5 h-5" />
              Forensic Assessment
            </CardTitle>
            <p className="text-sm text-slate-300">Overall authenticity analysis</p>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex flex-col items-center justify-center py-8">
              <div className={cn(
                "text-6xl font-bold mb-2",
                currentScenario.forensicScore >= 80 ? "text-emerald-500" :
                currentScenario.forensicScore >= 60 ? "text-yellow-500" :
                "text-red-500"
              )}>
                {currentScenario.forensicScore}%
              </div>
              <AuthenticityBadge 
                score={currentScenario.forensicScore} 
                variant="detailed"
                size="lg"
              />
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Steganography Risk</span>
                <ForensicConfidenceIndicator
                  confidence={currentScenario.forensicAnalysis.steganography?.confidence || 0}
                  type="manipulation"
                  size="sm"
                />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Manipulation Risk</span>
                <ForensicConfidenceIndicator
                  confidence={currentScenario.forensicAnalysis.manipulation?.confidence || 0}
                  type="manipulation"
                  size="sm"
                />
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">AI Generation Risk</span>
                <ForensicConfidenceIndicator
                  confidence={currentScenario.forensicAnalysis.aiDetection?.confidence || 0}
                  type="ai-detection"
                  size="sm"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Forensic Analysis */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                <Fingerprint className="w-5 h-5" />
                Detailed Forensic Analysis
              </CardTitle>
              <p className="text-sm text-slate-300">
                Comprehensive analysis breakdown
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <Settings className="w-4 h-4 mr-1" />
                {showAdvanced ? 'Simple' : 'Advanced'}
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <Download className="w-4 h-4" />
                Export
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <FileText className="w-4 h-4" />
                Report
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isAnalyzing ? (
            <div className="py-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
              <p className="text-slate-300">Analyzing image forensics...</p>
            </div>
          ) : (
            showAdvanced ? (
              <ForensicAnalysis
                steganography={currentScenario.forensicAnalysis.steganography}
                manipulation={currentScenario.forensicAnalysis.manipulation}
                aiDetection={currentScenario.forensicAnalysis.aiDetection}
                authenticityScore={currentScenario.forensicScore}
                onReanalyze={handleReanalyze}
              />
            ) : (
              <ProgressiveDisclosure
                data={progressiveDisclosureData}
                showForensicAnalysis={true}
                defaultTab="forensic"
              />
            )
          )}
        </CardContent>
      </Card>

      {/* Comparison View */}
      {showComparison && (
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white">Scenario Comparison</CardTitle>
            <p className="text-sm text-slate-300">Compare forensic results across different scenarios</p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(demoScenarios).map(([key, scenario]) => (
                <div
                  key={key}
                  className={cn(
                    "p-4 rounded-lg border",
                    "bg-slate-50 dark:bg-slate-900",
                    "border-slate-200 dark:border-slate-700"
                  )}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-slate-900 dark:text-white">
                      {scenario.title}
                    </h4>
                    <AuthenticityBadge score={scenario.forensicScore} variant="compact" />
                  </div>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-600 dark:text-slate-400">Steganography:</span>
                      <span className={cn(
                        scenario.forensicAnalysis.steganography?.detected ? "text-red-500" : "text-emerald-500"
                      )}>
                        {scenario.forensicAnalysis.steganography?.detected ? 'Detected' : 'Clean'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600 dark:text-slate-400">Manipulation:</span>
                      <span className={cn(
                        scenario.forensicAnalysis.manipulation?.detected ? "text-red-500" : "text-emerald-500"
                      )}>
                        {scenario.forensicAnalysis.manipulation?.detected ? 'Detected' : 'Clean'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-600 dark:text-slate-400">AI Generated:</span>
                      <span className={cn(
                        scenario.forensicAnalysis.aiDetection?.aiGenerated ? "text-red-500" : "text-emerald-500"
                      )}>
                        {scenario.forensicAnalysis.aiDetection?.aiGenerated ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upload Your Own */}
      <div className="text-center p-8 bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
        <Upload className="w-12 h-12 mx-auto mb-4 text-slate-500" />
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          Try Your Own Image
        </h3>
        <p className="text-slate-600 dark:text-slate-400 mb-4">
          Upload an image to see real forensic analysis in action
        </p>
        <Button className="gap-2">
          <Upload className="w-4 h-4" />
          Upload Image
        </Button>
      </div>
    </div>
  );
};

export default ForensicDemo;
