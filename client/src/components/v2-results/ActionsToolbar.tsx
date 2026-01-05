/**
 * Actions Toolbar Component
 *
 * Provides action buttons for metadata manipulation:
 * - Export (JSON, PDF)
 * - Compare with another file
 * - Share results
 */

import React, { useState } from 'react';
import { Download, FileText, Share2, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface ActionsToolbarProps {
  filename: string;
  metadata: Record<string, any>;
  onCompare?: () => void;
  onShare?: () => void;
  className?: string;
}

export function ActionsToolbar({
  filename,
  metadata,
  onCompare,
  onShare,
  className
}: ActionsToolbarProps): React.ReactElement {
  const { toast } = useToast();
  const [copiedJson, setCopiedJson] = useState(false);

  const handleExportJSON = () => {
    try {
      const dataStr = JSON.stringify(metadata, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}_metadata.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast({
        title: 'Download started',
        description: 'Metadata JSON file is being downloaded',
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: 'Could not export metadata',
        variant: 'destructive',
      });
    }
  };

  const handleExportPDF = () => {
    toast({
      title: 'PDF export coming soon',
      description: 'PDF export functionality will be available shortly',
    });
  };

  const handleCopyJSON = async () => {
    try {
      const dataStr = JSON.stringify(metadata, null, 2);
      await navigator.clipboard.writeText(dataStr);
      setCopiedJson(true);
      toast({
        title: 'Copied!',
        description: 'Metadata copied to clipboard',
      });
      setTimeout(() => setCopiedJson(false), 2000);
    } catch (error) {
      toast({
        title: 'Copy failed',
        description: 'Could not copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  const handleCompare = () => {
    onCompare?.();
    toast({
      title: 'Compare functionality coming soon',
      description: 'Compare with another file will be available soon',
    });
  };

  const handleShare = () => {
    onShare?.();
    toast({
      title: 'Share functionality coming soon',
      description: 'Share results will be available soon',
    });
  };

  return (
    <div
      className={cn(
        'flex flex-wrap gap-2',
        'p-4 rounded-lg',
        'bg-white/5 dark:bg-black/40',
        'border border-white/10 dark:border-white/10',
        className
      )}
    >
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase">
          Actions
        </span>
      </div>

      <div className="flex-1" />

      <div className="flex flex-wrap gap-2">
        {/* Export Actions */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleExportJSON}
          className="gap-2 text-xs min-h-[44px]"
          title="Download metadata as JSON"
        >
          <Download className="w-4 h-4" aria-hidden="true" />
          JSON
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={handleExportPDF}
          className="gap-2 text-xs min-h-[44px]"
          title="Export as PDF (coming soon)"
        >
          <FileText className="w-4 h-4" aria-hidden="true" />
          PDF
        </Button>

        {/* Copy JSON */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleCopyJSON}
          className="gap-2 text-xs min-h-[44px]"
          title="Copy JSON to clipboard"
        >
          {copiedJson ? (
            <>
              <Check className="w-4 h-4" aria-hidden="true" />
              Copied
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" aria-hidden="true" />
              Copy
            </>
          )}
        </Button>

        {/* Compare */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleCompare}
          className="gap-2 text-xs min-h-[44px]"
          title="Compare with another file (coming soon)"
        >
          Compare
        </Button>

        {/* Share */}
        <Button
          variant="outline"
          size="sm"
          onClick={handleShare}
          className="gap-2 text-xs min-h-[44px]"
          title="Share results (coming soon)"
        >
          <Share2 className="w-4 h-4" aria-hidden="true" />
          Share
        </Button>
      </div>
    </div>
  );
}

/**
 * Compact variant for mobile
 */
export function ActionsToolbarCompact({
  filename,
  metadata,
  onCompare,
  onShare,
  className
}: ActionsToolbarProps): React.ReactElement {
  const { toast } = useToast();
  const [copiedJson, setCopiedJson] = useState(false);

  const handleExportJSON = () => {
    try {
      const dataStr = JSON.stringify(metadata, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}_metadata.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast({
        title: 'Download started',
        description: 'Metadata JSON file is being downloaded',
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: 'Could not export metadata',
        variant: 'destructive',
      });
    }
  };

  const handleCopyJSON = async () => {
    try {
      const dataStr = JSON.stringify(metadata, null, 2);
      await navigator.clipboard.writeText(dataStr);
      setCopiedJson(true);
      toast({
        title: 'Copied!',
        description: 'Metadata copied to clipboard',
      });
      setTimeout(() => setCopiedJson(false), 2000);
    } catch (error) {
      toast({
        title: 'Copy failed',
        description: 'Could not copy to clipboard',
        variant: 'destructive',
      });
    }
  };

  return (
    <div
      className={cn(
        'grid grid-cols-2 gap-2',
        'p-3 rounded-lg',
        'bg-white/5 dark:bg-black/40',
        'border border-white/10 dark:border-white/10',
        className
      )}
    >
      <Button
        variant="outline"
        size="sm"
        onClick={handleExportJSON}
        className="gap-2 text-xs min-h-[44px]"
      >
        <Download className="w-4 h-4" aria-hidden="true" />
        Export
      </Button>

      <Button
        variant="outline"
        size="sm"
        onClick={handleCopyJSON}
        className="gap-2 text-xs min-h-[44px]"
      >
        {copiedJson ? (
          <>
            <Check className="w-4 h-4" aria-hidden="true" />
            Copied
          </>
        ) : (
          <>
            <Copy className="w-4 h-4" aria-hidden="true" />
            Copy
          </>
        )}
      </Button>
    </div>
  );
}
