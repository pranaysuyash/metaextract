/**
 * UI Adaptation Controller
 * 
 * Dynamically adapts the UI based on file context and user preferences.
 * Provides intelligent layout switching and contextual suggestions.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { detectFileContext, getUIAdaptations, type FileContext } from '@/lib/context-detection';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Lightbulb, 
  Eye, 
  Settings, 
  Zap, 
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';

// ============================================================================
// Context and Types
// ============================================================================

interface UIAdaptationState {
  context: FileContext | null;
  adaptations: ReturnType<typeof getUIAdaptations> | null;
  userPreferences: {
    autoAdapt: boolean;
    preferredLayout: 'auto' | 'standard' | 'forensic' | 'scientific' | 'compact';
    showSuggestions: boolean;
    hideEmptySections: boolean;
  };
  overrides: {
    layout?: string;
    emphasizedSections?: string[];
    hiddenSections?: string[];
  };
}

interface UIAdaptationContextType extends UIAdaptationState {
  updateContext: (metadata: Record<string, any>) => void;
  updatePreferences: (prefs: Partial<UIAdaptationState['userPreferences']>) => void;
  applyOverride: (overrides: Partial<UIAdaptationState['overrides']>) => void;
  resetOverrides: () => void;
  getSectionVisibility: (section: string) => boolean;
  getSectionEmphasis: (section: string) => boolean;
  getLayout: () => string;
}

const UIAdaptationContext = createContext<UIAdaptationContextType | null>(null);

// ============================================================================
// Provider Component
// ============================================================================

interface UIAdaptationProviderProps {
  children: ReactNode;
  initialMetadata?: Record<string, any>;
}

export function UIAdaptationProvider({ children, initialMetadata }: UIAdaptationProviderProps) {
  const [state, setState] = useState<UIAdaptationState>({
    context: null,
    adaptations: null,
    userPreferences: {
      autoAdapt: true,
      preferredLayout: 'auto',
      showSuggestions: true,
      hideEmptySections: true,
    },
    overrides: {},
  });

  const updateContext = (metadata: Record<string, any>) => {
    const context = detectFileContext(metadata);
    const adaptations = getUIAdaptations(context);
    
    setState(prev => ({
      ...prev,
      context,
      adaptations: prev.userPreferences.autoAdapt ? adaptations : prev.adaptations,
    }));
  };

  const updatePreferences = (prefs: Partial<UIAdaptationState['userPreferences']>) => {
    setState(prev => ({
      ...prev,
      userPreferences: { ...prev.userPreferences, ...prefs },
    }));
  };

  const applyOverride = (overrides: Partial<UIAdaptationState['overrides']>) => {
    setState(prev => ({
      ...prev,
      overrides: { ...prev.overrides, ...overrides },
    }));
  };

  const resetOverrides = () => {
    setState(prev => ({
      ...prev,
      overrides: {},
    }));
  };

  const getSectionVisibility = (section: string): boolean => {
    if (state.overrides.hiddenSections?.includes(section)) return false;
    if (!state.adaptations) return true;
    return !state.adaptations.hiddenSections.includes(section);
  };

  const getSectionEmphasis = (section: string): boolean => {
    if (state.overrides.emphasizedSections?.includes(section)) return true;
    if (!state.adaptations) return false;
    return state.adaptations.emphasizedSections.includes(section);
  };

  const getLayout = (): string => {
    if (state.overrides.layout) return state.overrides.layout;
    if (state.userPreferences.preferredLayout !== 'auto') {
      return state.userPreferences.preferredLayout;
    }
    return state.adaptations?.layout || 'standard';
  };

  // Initialize with metadata if provided
  useEffect(() => {
    if (initialMetadata) {
      updateContext(initialMetadata);
    }
  }, [initialMetadata]);

  const contextValue: UIAdaptationContextType = {
    ...state,
    updateContext,
    updatePreferences,
    applyOverride,
    resetOverrides,
    getSectionVisibility,
    getSectionEmphasis,
    getLayout,
  };

  return (
    <UIAdaptationContext.Provider value={contextValue}>
      {children}
    </UIAdaptationContext.Provider>
  );
}

// ============================================================================
// Hook
// ============================================================================

export function useUIAdaptation() {
  const context = useContext(UIAdaptationContext);
  if (!context) {
    throw new Error('useUIAdaptation must be used within UIAdaptationProvider');
  }
  return context;
}

// ============================================================================
// Context Banner Component
// ============================================================================

export function ContextBanner() {
  const { context, adaptations, userPreferences } = useUIAdaptation();
  const [dismissed, setDismissed] = useState(false);

  if (!context || !userPreferences.showSuggestions || dismissed) {
    return null;
  }

  const getContextIcon = () => {
    switch (context.type) {
      case 'forensic':
        return <AlertTriangle className="h-4 w-4" />;
      case 'scientific':
        return <Zap className="h-4 w-4" />;
      case 'photography':
        return <Eye className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getContextColor = () => {
    switch (context.type) {
      case 'forensic':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'scientific':
        return 'border-blue-200 bg-blue-50 text-blue-800';
      case 'photography':
        return 'border-green-200 bg-green-50 text-green-800';
      default:
        return 'border-gray-200 bg-gray-50 text-gray-800';
    }
  };

  return (
    <Alert className={`mb-4 ${getContextColor()}`}>
      <div className="flex items-start gap-3">
        {getContextIcon()}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium">
              {context.type.charAt(0).toUpperCase() + context.type.slice(1)} Context Detected
            </span>
            <Badge variant="secondary" className="text-xs">
              {Math.round(context.confidence * 100)}% confidence
            </Badge>
          </div>
          <AlertDescription className="text-sm">
            This file appears to be from a {context.type} workflow. 
            {adaptations && (
              <span>
                {' '}The interface has been optimized to highlight {adaptations.emphasizedSections.slice(0, 3).join(', ')} sections.
              </span>
            )}
          </AlertDescription>
          
          {context.warnings && context.warnings.length > 0 && (
            <div className="mt-2 space-y-1">
              {context.warnings.map((warning, index) => (
                <div key={index} className="flex items-center gap-2 text-sm font-medium">
                  <AlertTriangle className="h-3 w-3" />
                  {warning}
                </div>
              ))}
            </div>
          )}
          
          {adaptations && adaptations.suggestedActions.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {adaptations.suggestedActions.slice(0, 3).map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                >
                  {action.label}
                </Button>
              ))}
            </div>
          )}
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setDismissed(true)}
          className="h-6 w-6 p-0"
        >
          ×
        </Button>
      </div>
    </Alert>
  );
}

// ============================================================================
// Smart Section Component
// ============================================================================

interface SmartSectionProps {
  section: string;
  title: string;
  children: ReactNode;
  className?: string;
  defaultVisible?: boolean;
}

export function SmartSection({ 
  section, 
  title, 
  children, 
  className = '',
  defaultVisible = true 
}: SmartSectionProps) {
  const { getSectionVisibility, getSectionEmphasis } = useUIAdaptation();
  
  const isVisible = getSectionVisibility(section);
  const isEmphasized = getSectionEmphasis(section);
  
  if (!isVisible && !defaultVisible) {
    return null;
  }
  
  const sectionClassName = `
    ${className}
    ${isEmphasized ? 'ring-2 ring-primary/20 bg-primary/5' : ''}
    ${!isVisible ? 'opacity-50' : ''}
  `.trim();
  
  return (
    <section className={sectionClassName}>
      <div className="flex items-center gap-2 mb-3">
        <h4 className={`text-sm font-medium ${isEmphasized ? 'text-primary' : 'text-muted-foreground'}`}>
          {title}
        </h4>
        {isEmphasized && (
          <Badge variant="secondary" className="text-xs">
            <Lightbulb className="h-3 w-3 mr-1" />
            Relevant
          </Badge>
        )}
      </div>
      {children}
    </section>
  );
}

// ============================================================================
// Layout Adapter Component
// ============================================================================

interface LayoutAdapterProps {
  children: (layout: string) => ReactNode;
}

export function LayoutAdapter({ children }: LayoutAdapterProps) {
  const { getLayout } = useUIAdaptation();
  const layout = getLayout();
  
  return <>{children(layout)}</>;
}

// ============================================================================
// Context Indicator Component
// ============================================================================

export function ContextIndicator() {
  const { context } = useUIAdaptation();
  
  if (!context) return null;
  
  const getIndicatorColor = () => {
    switch (context.type) {
      case 'forensic':
        return 'bg-red-500';
      case 'scientific':
        return 'bg-blue-500';
      case 'photography':
        return 'bg-green-500';
      case 'web':
        return 'bg-purple-500';
      case 'mobile':
        return 'bg-orange-500';
      case 'professional':
        return 'bg-indigo-500';
      default:
        return 'bg-gray-500';
    }
  };
  
  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <div className={`w-2 h-2 rounded-full ${getIndicatorColor()}`} />
      <span className="capitalize">{context.type}</span>
      <span>({Math.round(context.confidence * 100)}%)</span>
    </div>
  );
}

// ============================================================================
// Preferences Panel Component
// ============================================================================

export function AdaptationPreferences() {
  const { userPreferences, updatePreferences, resetOverrides } = useUIAdaptation();
  
  return (
    <div className="space-y-4 p-4 border rounded-lg">
      <h3 className="font-medium flex items-center gap-2">
        <Settings className="h-4 w-4" />
        UI Adaptation Settings
      </h3>
      
      <div className="space-y-3">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={userPreferences.autoAdapt}
            onChange={(e) => updatePreferences({ autoAdapt: e.target.checked })}
            className="rounded"
          />
          <span className="text-sm">Auto-adapt interface based on file type</span>
        </label>
        
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={userPreferences.showSuggestions}
            onChange={(e) => updatePreferences({ showSuggestions: e.target.checked })}
            className="rounded"
          />
          <span className="text-sm">Show contextual suggestions</span>
        </label>
        
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={userPreferences.hideEmptySections}
            onChange={(e) => updatePreferences({ hideEmptySections: e.target.checked })}
            className="rounded"
          />
          <span className="text-sm">Hide empty sections</span>
        </label>
        
        <div className="flex items-center gap-2">
          <label className="text-sm">Preferred layout:</label>
          <select
            value={userPreferences.preferredLayout}
            onChange={(e) => updatePreferences({ preferredLayout: e.target.value as any })}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="auto">Auto</option>
            <option value="standard">Standard</option>
            <option value="forensic">Forensic</option>
            <option value="scientific">Scientific</option>
            <option value="compact">Compact</option>
          </select>
        </div>
        
        <Button
          variant="outline"
          size="sm"
          onClick={resetOverrides}
          className="w-full"
        >
          Reset Customizations
        </Button>
      </div>
    </div>
  );
}