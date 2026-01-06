/**
 * V2 UI Help Content
 * Simplified help for minimalist V2 UI
 */

export interface V2HelpTopic {
  id: string;
  title: string;
  shortDescription: string;
  expandedContent: string;
}

export const V2_HELP_TOPICS: Record<string, V2HelpTopic> = {
  'quick-findings': {
    id: 'quick-findings',
    title: 'Quick Findings',
    shortDescription: 'Key metadata shown at a glance',
    expandedContent:
      "Quick Findings displays the most important metadata from your file upfront, so you don't have to dig through details. Shows GPS, camera info, file details, and any warnings or issues.",
  },

  'simplified-view': {
    id: 'simplified-view',
    title: 'Simplified View',
    shortDescription: 'Clean, distraction-free interface',
    expandedContent:
      'V2 focuses on what matters most. Less clutter, faster loading, and essential information first. Advanced options are available if you need them.',
  },

  'file-type-support': {
    id: 'file-type-support',
    title: 'Supported File Types',
    shortDescription: 'Extract metadata from any file',
    expandedContent:
      'V2 supports all the same file types as the original: images (JPEG, PNG, HEIC, WebP), documents (PDF, DOCX), videos (MP4, MOV), and more. Just upload and see what metadata is available.',
  },

  'privacy-protection': {
    id: 'privacy-protection',
    title: 'Privacy Features',
    shortDescription: 'Check and clean sensitive data',
    expandedContent:
      'V2 includes privacy-focused features to help you identify and remove sensitive data before sharing. Check GPS location, timestamps, camera info, and clean metadata if needed.',
  },

  'keyboard-shortcuts': {
    id: 'keyboard-shortcuts',
    title: 'Keyboard Shortcuts',
    shortDescription: 'Navigate faster with keyboard',
    expandedContent:
      'Use keyboard shortcuts for common actions: Enter to upload, Esc to close dialogs, Arrow keys to navigate results. Access complete keyboard shortcuts list with ? key.',
  },
};

export function getV2HelpTopic(topicId: string): V2HelpTopic | undefined {
  return V2_HELP_TOPICS[topicId];
}

export function getAllV2HelpTopics(): V2HelpTopic[] {
  return Object.values(V2_HELP_TOPICS);
}
