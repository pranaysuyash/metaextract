/**
 * V2 Results Components - Forensic Analysis Module
 *
 * Comprehensive forensic analysis components for metadata examination,
 * authenticity verification, and manipulation detection.
 */

// Main forensic analysis component
export { ForensicAnalysis } from './ForensicAnalysis';
export type { ForensicAnalysisProps } from './ForensicAnalysis';

// Authenticity and confidence indicators
export {
  AuthenticityBadge,
  AuthenticityAssessment,
  ForensicConfidenceIndicator,
  QuickAuthenticityIndicator,
} from './AuthenticityBadge';
export type { AuthenticityBadgeProps } from './AuthenticityBadge';

// Enhanced key findings with forensic integration
export { KeyFindings, KeyFindingsCompact } from './KeyFindings';
export type { KeyFindingsProps } from './KeyFindings';

// Progressive disclosure with forensic analysis
export {
  ProgressiveDisclosure,
  ProgressiveDisclosureMobile,
} from './ProgressiveDisclosure';
export type {
  ProgressiveDisclosureProps,
  ProgressiveDisclosureData,
} from './ProgressiveDisclosure';

// Demo and utility components
export { ForensicDemo } from './ForensicDemo';
export { default as ForensicDemoDefault } from './ForensicDemo';

// Supporting components
export { QuickDetails } from './QuickDetails';
export { LocationSection } from './LocationSection';
export { ExpandableSectionList } from './ExpandableSection';
export { ActionsToolbar, ActionsToolbarCompact } from './ActionsToolbar';

// Re-export types for convenience
export type {
  SteganographyAnalysis,
  ManipulationAnalysis,
  AIDetection,
  ForensicFindingCardProps,
} from './ForensicAnalysis';

export type {
  ForensicConfidenceIndicatorProps,
  AuthenticityAssessmentProps,
} from './AuthenticityBadge';
