import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { KeyFindings } from '@/components/v2-results/KeyFindings';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, FileText, Cpu } from 'lucide-react';
import generatedBackground from '@assets/generated_images/chaotic_dark_forensic_data_visualization_with_connecting_lines.png';
import { cn } from '@/lib/utils';

interface MetadataResponse {
  filename: string;
  filesize: string;
  filetype: string;
  mime_type: string;
  tier: string;
  fields_extracted: number;
  fields_available: number;
  processing_ms: number;
  file_integrity?: {
    md5: string;
    sha256: string;
    sha1?: string;
    crc32?: string;
  };
  gps?: any;
  exif?: any;
  filesystem?: any;
  summary?: any;
  [key: string]: any;
}

export default function ResultsV2() {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [metadata, setMetadata] = useState<MetadataResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load metadata from navigation state - handle both array and single object
    let metadataData = null;

    if (location.state?.metadata) {
      console.log('[ResultsV2] Loaded metadata from navigation state:', location.state.metadata);
      metadataData = location.state.metadata;
    } else if (location.state?.results) {
      console.log('[ResultsV2] Loaded results from navigation state:', location.state.results);
      metadataData = location.state.results;
    }

    // Handle if data is an array
    if (Array.isArray(metadataData)) {
      console.log('[ResultsV2] Data is array, taking first element:', metadataData[0]);
      setMetadata(metadataData[0]);
    } else if (metadataData) {
      console.log('[ResultsV2] Data is object:', metadataData);
      setMetadata(metadataData);
    } else {
      console.error('[ResultsV2] No metadata found in navigation state');
    }

    setIsLoading(false);
  }, [location.state]);

  const handleDownload = () => {
    if (!metadata) return;

    const dataStr = JSON.stringify(metadata, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${metadata.filename}_metadata.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    toast({
      title: 'Download started',
      description: 'Your metadata file is being downloaded'
    });
  };

  if (isLoading) {
    return (
      <div className='relative min-h-screen overflow-hidden'>
        <div className='absolute inset-0 z-0'>
          <div className='absolute inset-0 bg-background/90 z-10'></div>
          <img
            src={generatedBackground}
            alt='Background'
            className='w-full h-full object-cover opacity-10 mix-blend-screen scale-110'
          />
        </div>
        <div className='relative z-10 flex items-center justify-center min-h-screen'>
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-white font-mono">Loading your results...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!metadata) {
    return (
      <div className='relative min-h-screen overflow-hidden'>
        <div className='absolute inset-0 z-0'>
          <div className='absolute inset-0 bg-background/90 z-10'></div>
          <img
            src={generatedBackground}
            alt='Background'
            className='w-full h-full object-cover opacity-10 mix-blend-screen scale-110'
          />
        </div>
        <div className='relative z-10 flex items-center justify-center min-h-screen'>
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4 font-mono">No Results Found</h2>
            <Button onClick={() => navigate('/')} variant="default" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Go Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className='relative min-h-[calc(100vh-64px)] overflow-hidden'>
      {/* Background */}
      <div className='absolute inset-0 z-0 pointer-events-none'>
        <div className='absolute inset-0 bg-background/90 z-10'></div>
        <img
          src={generatedBackground}
          alt='Background'
          className='w-full h-full object-cover opacity-10 mix-blend-screen scale-110'
        />
      </div>

      {/* Header */}
      <div className='relative z-10 border-b border-white/10'>
        <div className='container mx-auto px-4 py-4'>
          <div className='flex items-center justify-between'>
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="gap-2 text-white hover:text-white hover:bg-white/10"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Button>

            <div className='flex gap-3'>
              <div className="flex items-center gap-2 px-3 py-2 bg-blue-600/20 border border-blue-500/30 rounded text-blue-300 text-xs font-mono">
                <Cpu className="w-4 h-4" />
                V2 RESULTS
              </div>

              <Button
                variant="outline"
                onClick={handleDownload}
                className="gap-2 font-mono text-xs border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/10"
              >
                <Download className="w-4 h-4" />
                JSON
              </Button>
              <Button
                variant="outline"
                onClick={() => toast({ title: 'PDF export coming soon to V2' })}
                className="gap-2 font-mono text-xs border-emerald-500/50 text-emerald-300 hover:bg-emerald-500/10"
              >
                <FileText className="w-4 h-4" />
                PDF
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className='container mx-auto px-4 py-8 relative z-10'>
        <div className="max-w-7xl mx-auto space-y-8">

          {/* File Header - Matching your forensic theme */}
          <div className="flex items-center justify-between pb-6 border-b border-white/10">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white/5 rounded border border-white/10 flex items-center justify-center">
                <Cpu className='w-6 h-6 text-primary' />
              </div>
              <div>
                <h1 className='text-xl font-bold text-white font-mono tracking-tight'>
                  {metadata.filename}
                </h1>
                <div className='flex gap-4 text-xs text-slate-500 font-mono mt-1'>
                  <span>SIZE: {metadata.filesize}</span>
                  <span>TYPE: {metadata.filetype}</span>
                  <span className="text-primary">
                    SHA256: {metadata.file_integrity?.sha256?.substring(0, 12) || 'N/A'}...
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* V2 Key Findings Section */}
          <div className="bg-black/40 backdrop-blur-md border border-white/10 rounded-lg p-6 shadow-lg">
            <KeyFindings metadata={metadata} />
          </div>

          {/* More V2 sections coming soon */}
          <div className="bg-black/40 backdrop-blur-md border border-white/10 rounded-lg p-8 shadow-lg">
            <div className="text-center">
              <p className="text-slate-400 font-mono text-sm">
                [ Additional V2 features coming soon: Quick Details, Location Map, Camera Info, etc. ]
              </p>
              <div className="mt-4 text-xs text-slate-600 font-mono">
                Current view: V2 Key Findings • Toggle to V1 for comparison
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}