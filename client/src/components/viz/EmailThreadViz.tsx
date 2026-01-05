// client/src/components/viz/EmailThreadViz.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Button } from '@/components/ui/button';
import {
  Mail,
  Reply,
  Forward,
  ReplyAll,
  Paperclip,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowRight,
  ArrowDown,
  ArrowUp,
  Users,
  Calendar,
} from 'lucide-react';

interface EmailThreadVizProps {
  email: {
    email_from?: string;
    email_from_name?: string;
    email_from_address?: string;
    email_to?: string;
    email_to_addresses?: string[];
    email_cc?: string;
    email_cc_addresses?: string[];
    email_bcc?: string;
    email_bcc_addresses?: string[];
    email_subject?: string;
    email_date?: string;
    email_datetime_parsed?: string;
    email_timestamp?: number;
    email_message_id?: string;
    email_in_reply_to?: string;
    email_references?: string;
    email_is_reply?: boolean;
    email_is_direct_reply?: boolean;
    email_is_forward?: boolean;
    email_thread_level?: number;
    email_priority?: string;
    email_dkim_present?: boolean;
    email_spf_result?: string;
    email_authentication_results?: string;
    email_spam_status?: string;
    email_attachment_count?: number;
    email_attachments?: Array<{
      filename: string;
      content_type: string;
      size: number;
    }>;
  };
}

interface Participant {
  name: string;
  email: string;
  type: 'from' | 'to' | 'cc' | 'bcc';
  avatar?: string;
}

interface ThreadNode {
  id: string;
  subject: string;
  from: Participant;
  to: Participant[];
  cc: Participant[];
  date: string;
  isReply: boolean;
  isForward: boolean;
  threadLevel: number;
  hasAttachments: boolean;
  security: {
    dkim: boolean;
    spf: string;
    spamScore: string;
  };
}

function extractEmail(str: string | undefined): string {
  if (!str) return '';
  const match = str.match(/<([^>]+)>/);
  return match ? match[1] : str;
}

function extractName(str: string | undefined): string {
  if (!str) return '';
  const match = str.match(/^"?([^"<]+)"?\s*</);
  if (match) return match[1].trim();
  return str.split('@')[0] || str;
}

function getAvatarColor(type: string): string {
  switch (type) {
    case 'from':
      return 'bg-blue-500';
    case 'to':
      return 'bg-green-500';
    case 'cc':
      return 'bg-amber-500';
    case 'bcc':
      return 'bg-gray-500';
    default:
      return 'bg-gray-400';
  }
}

function getSecurityBadge(dkim: boolean, spf: string): React.ReactNode {
  if (dkim && spf === 'pass') {
    return (
      <Badge className="bg-green-100 text-green-800 hover:bg-green-100">
        <CheckCircle className="w-3 h-3 mr-1" />
        Verified
      </Badge>
    );
  }
  if (spf === 'fail' || spf === 'softfail') {
    return (
      <Badge className="bg-red-100 text-red-800 hover:bg-red-100">
        <AlertTriangle className="w-3 h-3 mr-1" />
        Failed
      </Badge>
    );
  }
  return (
    <Badge variant="outline">
      <Shield className="w-3 h-3 mr-1" />
      Unknown
    </Badge>
  );
}

function getPriorityBadge(priority: string | undefined): React.ReactNode {
  if (!priority) return null;

  switch (priority.toLowerCase()) {
    case 'high':
    case 'urgent':
      return (
        <Badge variant="destructive" className="text-xs">
          <ArrowUp className="w-3 h-3 mr-1" />
          High Priority
        </Badge>
      );
    case 'low':
    case 'non-urgent':
      return (
        <Badge variant="secondary" className="text-xs">
          Low Priority
        </Badge>
      );
    default:
      return (
        <Badge variant="outline" className="text-xs">
          Normal
        </Badge>
      );
  }
}

export function EmailThreadViz({ email }: EmailThreadVizProps) {
  // Build thread nodes
  const nodes: ThreadNode[] = [];

  const mainNode: ThreadNode = {
    id: email.email_message_id || 'main',
    subject: email.email_subject || '(No Subject)',
    from: {
      name: email.email_from_name || extractName(email.email_from),
      email: extractEmail(email.email_from),
      type: 'from',
    },
    to: (email.email_to_addresses || []).map(e => ({
      name: extractName(e),
      email: extractEmail(e),
      type: 'to' as const,
    })),
    cc: (email.email_cc_addresses || []).map(e => ({
      name: extractName(e),
      email: extractEmail(e),
      type: 'cc' as const,
    })),
    date: email.email_datetime_parsed || email.email_date || '',
    isReply: email.email_is_reply || false,
    isForward: email.email_is_forward || false,
    threadLevel: email.email_thread_level || 0,
    hasAttachments: (email.email_attachment_count || 0) > 0,
    security: {
      dkim: email.email_dkim_present || false,
      spf: email.email_spf_result || 'unknown',
      spamScore: email.email_spam_status || 'Unknown',
    },
  };

  nodes.push(mainNode);

  const maxLevel = Math.max(...nodes.map(n => n.threadLevel));

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <Mail className="w-5 h-5" />
          Email Thread
          {getPriorityBadge(email.email_priority)}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Subject line */}
        <div className="mb-4 p-3 rounded-lg bg-muted/50">
          <div className="flex items-center gap-2 flex-wrap">
            {mainNode.isReply && <Reply className="w-4 h-4 text-blue-600" />}
            {mainNode.isForward && (
              <Forward className="w-4 h-4 text-orange-600" />
            )}
            <span className="font-medium">{mainNode.subject}</span>
          </div>
          {maxLevel > 0 && (
            <div className="text-xs text-muted-foreground mt-1">
              Thread level: {mainNode.threadLevel}
            </div>
          )}
        </div>

        {/* Participants */}
        <div className="mb-4">
          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
            <Users className="w-4 h-4" />
            Participants
          </h4>

          <div className="space-y-2">
            {/* From */}
            <div className="flex items-center gap-2">
              <div
                className={`w-8 h-8 rounded-full ${getAvatarColor('from')} flex items-center justify-center text-white text-sm font-medium`}
              >
                {mainNode.from.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="text-sm font-medium">{mainNode.from.name}</div>
                <div className="text-xs text-muted-foreground">
                  {mainNode.from.email}
                </div>
              </div>
              <Badge variant="outline" className="text-xs ml-auto">
                From
              </Badge>
            </div>

            {/* To */}
            {mainNode.to.map((recipient, idx) => (
              <div
                key={`to-${recipient.email}-${idx}`}
                className="flex items-center gap-2"
              >
                <div
                  className={`w-8 h-8 rounded-full ${getAvatarColor('to')} flex items-center justify-center text-white text-sm font-medium`}
                >
                  {recipient.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="text-sm font-medium">{recipient.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {recipient.email}
                  </div>
                </div>
                <Badge variant="outline" className="text-xs ml-auto">
                  To
                </Badge>
              </div>
            ))}

            {/* CC */}
            {mainNode.cc.length > 0 && (
              <div className="mt-2">
                <div className="text-xs text-muted-foreground mb-1">CC:</div>
                {mainNode.cc.map((recipient, idx) => (
                  <div
                    key={`cc-${recipient.email}-${idx}`}
                    className="flex items-center gap-2 ml-4"
                  >
                    <div
                      className={`w-6 h-6 rounded-full ${getAvatarColor('cc')} flex items-center justify-center text-white text-xs font-medium`}
                    >
                      {recipient.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="text-sm">{recipient.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {recipient.email}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Date & Time */}
        <div className="mb-4 p-3 rounded-lg bg-muted/50">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm">{mainNode.date}</span>
          </div>
        </div>

        {/* Attachments */}
        {mainNode.hasAttachments &&
          email.email_attachments &&
          email.email_attachments.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                <Paperclip className="w-4 h-4" />
                Attachments ({email.email_attachments.length})
              </h4>
              <div className="space-y-1">
                {email.email_attachments.map((att, idx) => (
                  <div
                    key={`attachment-${att.filename}-${idx}`}
                    className="flex items-center gap-2 p-2 rounded bg-muted/30"
                  >
                    <Paperclip className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm flex-1">{att.filename}</span>
                    <span className="text-xs text-muted-foreground">
                      {att.size ? `${(att.size / 1024).toFixed(1)} KB` : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

        {/* Security Status */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Security Verification
          </h4>
          <div className="grid grid-cols-2 gap-2">
            <div className="flex items-center gap-2 p-2 rounded bg-muted/30">
              <CheckCircle
                className={`w-4 h-4 ${mainNode.security.dkim ? 'text-green-600' : 'text-gray-400'}`}
              />
              <span className="text-sm">DKIM</span>
              {mainNode.security.dkim ? (
                <Badge className="ml-auto text-xs">Valid</Badge>
              ) : (
                <Badge variant="outline" className="ml-auto text-xs">
                  Not found
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2 p-2 rounded bg-muted/30">
              <CheckCircle
                className={`w-4 h-4 ${mainNode.security.spf === 'pass' ? 'text-green-600' : 'text-gray-400'}`}
              />
              <span className="text-sm">SPF</span>
              <Badge
                className={`ml-auto text-xs ${mainNode.security.spf === 'pass' ? 'bg-green-100 text-green-800' : 'bg-gray-100'}`}
              >
                {mainNode.security.spf}
              </Badge>
            </div>
          </div>
          {email.email_spam_status && (
            <div className="mt-2 p-2 rounded bg-muted/30 text-sm">
              <span className="text-muted-foreground">Spam status: </span>
              {email.email_spam_status}
            </div>
          )}
        </div>

        {/* Thread visualization */}
        {maxLevel > 0 && (
          <div className="border-t pt-4 mt-4">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              <ArrowRight className="w-4 h-4" />
              Thread Structure
            </h4>
            <div className="space-y-2">
              {nodes.map((node, idx) => (
                <div
                  key={node.id}
                  className="flex items-center gap-2"
                  style={{ marginLeft: `${node.threadLevel * 24}px` }}
                >
                  <ArrowDown className="w-4 h-4 text-muted-foreground" />
                  <div className="p-2 rounded bg-muted/50 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">
                        {node.subject}
                      </span>
                      {node.isReply && (
                        <Reply className="w-3 h-3 text-blue-600" />
                      )}
                      {node.isForward && (
                        <Forward className="w-3 h-3 text-orange-600" />
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      From: {node.from.name} · {node.date}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
