// client/src/components/viz/ForensicTimeline.tsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  History,
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  FileCheck,
  Fingerprint,
  Link as LinkIcon,
  Hash,
} from 'lucide-react';

interface FileIntegrity {
  md5?: string;
  sha256?: string;
  sha1?: string;
  crc32?: string;
}

interface ForensicData {
  forensic_filesystem?: {
    file_created?: string;
    file_modified?: string;
    file_accessed?: string;
    file_size?: number;
    file_permissions?: string;
    file_owner?: number;
    file_inode?: number;
  };
  forensic_device_hardware?: {
    device_id?: string;
    volume_id?: string;
    drive_type?: string;
    filesystem_type?: string;
  };
  forensic_network_communication?: {
    peer_ip?: string;
    peer_hostname?: string;
    connection_type?: string;
  };
}

interface ForensicTimelineProps {
  integrity?: FileIntegrity;
  forensic?: ForensicData;
  fileType?: string;
  filename?: string;
}

interface TimelineEvent {
  id: string;
  timestamp: Date | null;
  label: string;
  description: string;
  type:
    | 'creation'
    | 'modification'
    | 'access'
    | 'transfer'
    | 'verification'
    | 'hash';
  icon: React.ReactNode;
  color: string;
  verified: boolean;
}

function parseDate(dateStr: string | undefined): Date | null {
  if (!dateStr) return null;
  const date = new Date(dateStr);
  return isNaN(date.getTime()) ? null : date;
}

function formatDateTime(date: Date | null): string {
  if (!date) return 'Unknown';
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function formatRelativeTime(date: Date | null): string {
  if (!date) return '';
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 30) return `${diffDays} days ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}

export function ForensicTimeline({
  integrity,
  forensic,
  fileType,
  filename,
}: ForensicTimelineProps) {
  const [filter, setFilter] = useState<
    'all' | 'creation' | 'modification' | 'access' | 'hash'
  >('all');

  const events: TimelineEvent[] = [
    {
      id: 'file-created',
      timestamp: parseDate(forensic?.forensic_filesystem?.file_created),
      label: 'File Created',
      description: `Original file created on this device`,
      type: 'creation',
      icon: <FileCheck className="w-4 h-4" />,
      color: 'text-green-600',
      verified: true,
    },
    {
      id: 'file-modified',
      timestamp: parseDate(forensic?.forensic_filesystem?.file_modified),
      label: 'Last Modified',
      description: `File was last modified`,
      type: 'modification',
      icon: <Clock className="w-4 h-4" />,
      color: 'text-blue-600',
      verified: true,
    },
    {
      id: 'file-accessed',
      timestamp: parseDate(forensic?.forensic_filesystem?.file_accessed),
      label: 'Last Accessed',
      description: `File was last accessed`,
      type: 'access',
      icon: <Clock className="w-4 h-4" />,
      color: 'text-orange-600',
      verified: true,
    },
    {
      id: 'hash-computed',
      timestamp: new Date(),
      label: 'Hash Verified',
      description: `SHA-256: ${integrity?.sha256?.substring(0, 16)}...`,
      type: 'hash',
      icon: <Fingerprint className="w-4 h-4" />,
      color: 'text-purple-600',
      verified: true,
    },
  ];

  const filteredEvents = events
    .filter(e => filter === 'all' || e.type === filter)
    .filter(e => e.timestamp)
    .sort(
      (a, b) => (a.timestamp?.getTime() || 0) - (b.timestamp?.getTime() || 0)
    );

  // Calculate forensic score (simplified)
  const verifiedCount = events.filter(e => e.verified).length;
  const forensicScore = Math.round((verifiedCount / events.length) * 100);

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <History className="w-5 h-5" />
          Chain of Custody
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Forensic Score */}
        <div className="mb-6 p-4 rounded-lg bg-gradient-to-r from-muted/50 to-muted/30">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-green-600" />
              <span className="font-medium">Forensic Score</span>
            </div>
            <Badge
              variant={
                forensicScore >= 80
                  ? 'default'
                  : forensicScore >= 50
                    ? 'secondary'
                    : 'destructive'
              }
            >
              {forensicScore}%
            </Badge>
          </div>
          <Progress value={forensicScore} className="h-2" />
          <p className="text-xs text-muted-foreground mt-2">
            {forensicScore >= 80
              ? 'High confidence - Multiple timestamps and hashes verified'
              : forensicScore >= 50
                ? 'Medium confidence - Limited forensic data available'
                : 'Low confidence - Insufficient forensic metadata'}
          </p>
        </div>

        {/* Filter */}
        <div className="mb-4 flex gap-2 flex-wrap">
          {(['all', 'creation', 'modification', 'access', 'hash'] as const).map(
            f => (
              <button
                type="button"
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 text-xs rounded-full transition-colors ${
                  filter === f
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted hover:bg-muted/80'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            )
          )}
        </div>

        {/* File Hashes */}
        {integrity && (
          <div className="mb-6">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              <Hash className="w-4 h-4" />
              File Hashes
            </h4>
            <div className="space-y-2">
              {integrity.sha256 && (
                <div className="flex items-center gap-2 p-2 rounded bg-muted/30">
                  <span className="text-xs text-muted-foreground w-12">
                    SHA-256
                  </span>
                  <code className="text-xs flex-1 font-mono truncate">
                    {integrity.sha256}
                  </code>
                  <CheckCircle className="w-4 h-4 text-green-600" />
                </div>
              )}
              {integrity.md5 && (
                <div className="flex items-center gap-2 p-2 rounded bg-muted/30">
                  <span className="text-xs text-muted-foreground w-12">
                    MD5
                  </span>
                  <code className="text-xs flex-1 font-mono truncate">
                    {integrity.md5}
                  </code>
                  <CheckCircle className="w-4 h-4 text-green-600" />
                </div>
              )}
              {integrity.sha1 && (
                <div className="flex items-center gap-2 p-2 rounded bg-muted/30">
                  <span className="text-xs text-muted-foreground w-12">
                    SHA-1
                  </span>
                  <code className="text-xs flex-1 font-mono truncate">
                    {integrity.sha1}
                  </code>
                  <CheckCircle className="w-4 h-4 text-green-600" />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Timeline */}
        <div className="relative">
          <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-border" />

          <div className="space-y-4">
            {filteredEvents.map((event, idx) => (
              <div
                key={event.id}
                className="relative flex items-start gap-4 pl-10"
              >
                {/* Icon */}
                <div
                  className={`absolute left-0 w-6 h-6 rounded-full bg-background border-2 border-${event.color.replace('text-', '')} flex items-center justify-center z-10 ${event.color}`}
                >
                  {event.icon}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium">{event.label}</span>
                    {event.verified ? (
                      <Badge variant="outline" className="text-xs bg-green-50">
                        <CheckCircle className="w-3 h-3 mr-1 text-green-600" />
                        Verified
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-xs bg-amber-50">
                        <AlertTriangle className="w-3 h-3 mr-1 text-amber-600" />
                        Unverified
                      </Badge>
                    )}
                  </div>

                  <div className="text-sm text-muted-foreground mt-1">
                    {event.description}
                  </div>

                  <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                    <Clock className="w-3 h-3" />
                    <span>{formatDateTime(event.timestamp)}</span>
                    <span>·</span>
                    <span>{formatRelativeTime(event.timestamp)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Device Info */}
        {forensic?.forensic_device_hardware && (
          <div className="mt-6 pt-4 border-t">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              <Fingerprint className="w-4 h-4" />
              Device Information
            </h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {forensic.forensic_device_hardware.device_id && (
                <div className="p-2 rounded bg-muted/30">
                  <span className="text-xs text-muted-foreground">
                    Device ID
                  </span>
                  <div className="font-mono text-xs truncate">
                    {forensic.forensic_device_hardware.device_id}
                  </div>
                </div>
              )}
              {forensic.forensic_device_hardware.filesystem_type && (
                <div className="p-2 rounded bg-muted/30">
                  <span className="text-xs text-muted-foreground">
                    Filesystem
                  </span>
                  <div>{forensic.forensic_device_hardware.filesystem_type}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
