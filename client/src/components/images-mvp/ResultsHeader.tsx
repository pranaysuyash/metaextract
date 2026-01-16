import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FileImage, Clipboard, ChevronDown, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MvpMetadata } from '@/lib/types';

interface ResultsHeaderProps {
  metadata: MvpMetadata;
  canExport: boolean;
  onCopySummary: () => void;
  onDownloadSummary: () => void;
  onDownloadJson: () => void;
  onDownloadFullTxt: () => void;
}

export const ResultsHeader: React.FC<ResultsHeaderProps> = ({
  metadata,
  canExport,
  onCopySummary,
  onDownloadSummary,
  onDownloadJson,
  onDownloadFullTxt,
}) => {
  const navigate = useNavigate();

  return (
    <div className="mb-8 flex flex-col gap-4">
      <div className="min-w-full">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileImage className="w-6 h-6 text-primary shrink-0" />
          <span title={metadata.filename}>{metadata.filename}</span>
        </h1>
        <p
          data-testid="key-field-mime-type"
          className="text-slate-400 text-sm font-mono mt-1 truncate"
        >
          {metadata.filesize} • {metadata.mime_type}
        </p>
      </div>
      <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap items-center">
        <Button
          variant="outline"
          onClick={() => navigate('/images_mvp')}
          className="border-white/10 hover:bg-white/5"
        >
          Analyze Another Photo
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              className="border-white/10 hover:bg-white/5 flex items-center gap-2"
            >
              <Clipboard className="w-4 h-4" />
              Summary actions
              <ChevronDown className="w-4 h-4 text-slate-400" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            align="start"
            className="border-[#1b1b24] bg-[#050608] text-white"
          >
            <DropdownMenuItem onSelect={onCopySummary}>
              <Clipboard className="w-4 h-4 text-slate-400" />
              Copy summary
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={onDownloadSummary}>
              <Download className="w-4 h-4 text-slate-400" />
              Download summary
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              className="border-white/10 hover:bg-white/5 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export data
              <ChevronDown className="w-4 h-4 text-slate-400" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            align="start"
            className="border-[#1b1b24] bg-[#050608] text-white"
          >
            <DropdownMenuItem
              onSelect={onDownloadJson}
              disabled={!canExport}
            >
              Download JSON
            </DropdownMenuItem>
            <DropdownMenuItem
              onSelect={onDownloadFullTxt}
              disabled={!canExport}
            >
              Download full report (txt)
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};