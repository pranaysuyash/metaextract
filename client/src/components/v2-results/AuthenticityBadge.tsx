import React from 'react';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, AlertTriangle, XCircle, Eye, Shield } from 'lucide-react';

interface AuthenticityBadgeProps {
  score: number;
  label?: string;
  showIcon?: boolean;
  variant?: 'default' | 'outline';
}

export const AuthenticityBadge: React.FC<AuthenticityBadgeProps> = ({ 
  score, 
  label, 
  showIcon = true,
  variant = 'default'
}) => {
  // Determine authenticity level based on score
  let authenticityLevel: 'authentic' | 'questionable' | 'suspicious' | 'unknown';
  let badgeVariant: 'default' | 'destructive' | 'secondary' | 'outline';
  let icon: React.ReactNode;
  let displayLabel: string;

  if (score >= 80) {
    authenticityLevel = 'authentic';
    badgeVariant = 'secondary';
    icon = <CheckCircle className="w-3 h-3 text-emerald-500" />;
    displayLabel = label || `Authentic (${score}%)`;
  } else if (score >= 50) {
    authenticityLevel = 'questionable';
    badgeVariant = 'outline';
    icon = <AlertTriangle className="w-3 h-3 text-yellow-500" />;
    displayLabel = label || `Questionable (${score}%)`;
  } else if (score >= 0) {
    authenticityLevel = 'suspicious';
    badgeVariant = 'destructive';
    icon = <XCircle className="w-3 h-3 text-red-500" />;
    displayLabel = label || `Suspicious (${score}%)`;
  } else {
    authenticityLevel = 'unknown';
    badgeVariant = 'outline';
    icon = <Eye className="w-3 h-3 text-slate-500" />;
    displayLabel = label || 'Authenticity Unknown';
  }

  // Adjust badge variant based on props
  const finalVariant = variant === 'outline' ? 'outline' : badgeVariant;

  return (
    <Badge 
      variant={finalVariant}
      className={`
        ${authenticityLevel === 'authentic' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : ''}
        ${authenticityLevel === 'questionable' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' : ''}
        ${authenticityLevel === 'suspicious' ? 'bg-red-500/20 text-red-400 border-red-500/30' : ''}
        ${authenticityLevel === 'unknown' ? 'bg-slate-500/20 text-slate-300 border-slate-500/30' : ''}
        ${showIcon ? 'flex items-center gap-1' : ''}
      `}
    >
      {showIcon && icon}
      <span>{displayLabel}</span>
    </Badge>
  );
};

interface AuthenticityAssessmentProps {
  score: number;
  details?: string;
  showConfidence?: boolean;
}

export const AuthenticityAssessment: React.FC<AuthenticityAssessmentProps> = ({ 
  score, 
  details,
  showConfidence = true
}) => {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <AuthenticityBadge score={score} />
        {showConfidence && (
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <Shield className="w-3 h-3" />
            <span>Confidence: {score}%</span>
          </div>
        )}
      </div>
      
      {details && (
        <p className="text-xs text-slate-300 mt-1">{details}</p>
      )}
    </div>
  );
};