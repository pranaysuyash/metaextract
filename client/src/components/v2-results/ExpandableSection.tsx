/**
 * Expandable Section Component
 *
 * A collapsible section for progressive disclosure of metadata details.
 * Starts collapsed to reduce cognitive load, expands on demand.
 */

import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ExpandableSectionProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  defaultExpanded?: boolean;
  className?: string;
  children: React.ReactNode;
}

export function ExpandableSection({
  title,
  description,
  icon,
  defaultExpanded = false,
  className,
  children
}: ExpandableSectionProps): React.ReactElement {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className={cn('border rounded-lg overflow-hidden', 'border-gray-200 dark:border-gray-800', className)}>
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={cn(
          'w-full px-4 py-3 flex items-center justify-between',
          'hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors',
          'bg-white dark:bg-gray-800'
        )}
      >
        <div className="flex items-center gap-3 flex-1">
          {icon && <div className="text-gray-600 dark:text-gray-400">{icon}</div>}
          <div className="text-left">
            <h3 className="font-medium text-gray-900 dark:text-white">
              {title}
            </h3>
            {description && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {description}
              </p>
            )}
          </div>
        </div>
        <ChevronDown
          className={cn(
            'w-5 h-5 text-gray-600 dark:text-gray-400 transition-transform',
            isExpanded && 'transform rotate-180'
          )}
        />
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900">
          {children}
        </div>
      )}
    </div>
  );
}

interface ExpandableSectionListProps {
  sections: Array<{
    title: string;
    description?: string;
    icon?: React.ReactNode;
    content: React.ReactNode;
  }>;
  className?: string;
}

export function ExpandableSectionList({
  sections,
  className
}: ExpandableSectionListProps): React.ReactElement {
  return (
    <div className={cn('space-y-2', className)}>
      {sections.map((section, idx) => (
        <ExpandableSection
          key={idx}
          title={section.title}
          description={section.description}
          icon={section.icon}
        >
          {section.content}
        </ExpandableSection>
      ))}
    </div>
  );
}
