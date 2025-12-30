/**
 * Error Boundary Components
 * 
 * Provides graceful error handling and recovery for React components.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  AlertTriangle, 
  RefreshCw, 
  Bug, 
  FileX, 
  Wifi,
  Server,
  Code
} from 'lucide-react';

// ============================================================================
// Types
// ============================================================================

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  level?: 'page' | 'section' | 'component';
}

// ============================================================================
// Main Error Boundary
// ============================================================================

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Call custom error handler
    this.props.onError?.(error, errorInfo);

    // In production, you might want to send this to an error reporting service
    // reportError(error, errorInfo, this.state.errorId);
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <ErrorDisplay
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          errorId={this.state.errorId}
          level={this.props.level || 'component'}
          onRetry={this.handleRetry}
        />
      );
    }

    return this.props.children;
  }
}

// ============================================================================
// Error Display Component
// ============================================================================

interface ErrorDisplayProps {
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
  level: 'page' | 'section' | 'component';
  onRetry: () => void;
}

function ErrorDisplay({ error, errorInfo, errorId, level, onRetry }: ErrorDisplayProps) {
  const getErrorType = (error: Error | null) => {
    if (!error) return 'unknown';
    
    const message = error.message.toLowerCase();
    if (message.includes('network') || message.includes('fetch')) return 'network';
    if (message.includes('chunk') || message.includes('loading')) return 'loading';
    if (message.includes('permission') || message.includes('unauthorized')) return 'permission';
    if (message.includes('not found') || message.includes('404')) return 'notfound';
    return 'runtime';
  };

  const errorType = getErrorType(error);

  const getErrorIcon = () => {
    switch (errorType) {
      case 'network':
        return <Wifi className="h-6 w-6" />;
      case 'loading':
        return <Server className="h-6 w-6" />;
      case 'permission':
        return <FileX className="h-6 w-6" />;
      case 'notfound':
        return <FileX className="h-6 w-6" />;
      default:
        return <Bug className="h-6 w-6" />;
    }
  };

  const getErrorTitle = () => {
    switch (errorType) {
      case 'network':
        return 'Network Error';
      case 'loading':
        return 'Loading Error';
      case 'permission':
        return 'Permission Error';
      case 'notfound':
        return 'Resource Not Found';
      default:
        return 'Something went wrong';
    }
  };

  const getErrorMessage = () => {
    switch (errorType) {
      case 'network':
        return 'Unable to connect to the server. Please check your internet connection and try again.';
      case 'loading':
        return 'Failed to load the required resources. This might be a temporary issue.';
      case 'permission':
        return 'You don\'t have permission to access this resource.';
      case 'notfound':
        return 'The requested resource could not be found.';
      default:
        return 'An unexpected error occurred while processing your request.';
    }
  };

  const getSuggestions = () => {
    switch (errorType) {
      case 'network':
        return [
          'Check your internet connection',
          'Try refreshing the page',
          'Contact support if the problem persists'
        ];
      case 'loading':
        return [
          'Try refreshing the page',
          'Clear your browser cache',
          'Try again in a few minutes'
        ];
      case 'permission':
        return [
          'Make sure you\'re logged in',
          'Contact an administrator for access',
          'Try logging out and back in'
        ];
      default:
        return [
          'Try refreshing the page',
          'Report this issue if it continues',
          'Try using a different browser'
        ];
    }
  };

  if (level === 'page') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4 text-destructive">
              {getErrorIcon()}
            </div>
            <CardTitle className="text-xl">{getErrorTitle()}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground text-center">
              {getErrorMessage()}
            </p>
            
            <div className="space-y-2">
              <h4 className="font-medium text-sm">Try these steps:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                {getSuggestions().map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-primary">•</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="flex gap-2">
              <Button onClick={onRetry} className="flex-1">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
              <Button 
                variant="outline" 
                onClick={() => window.location.reload()}
                className="flex-1"
              >
                Refresh Page
              </Button>
            </div>
            
            {process.env.NODE_ENV === 'development' && error && (
              <details className="mt-4">
                <summary className="cursor-pointer text-sm font-medium">
                  Technical Details
                </summary>
                <div className="mt-2 p-3 bg-muted rounded text-xs font-mono">
                  <div className="mb-2">
                    <strong>Error ID:</strong> {errorId}
                  </div>
                  <div className="mb-2">
                    <strong>Error:</strong> {error.message}
                  </div>
                  {error.stack && (
                    <div>
                      <strong>Stack:</strong>
                      <pre className="mt-1 whitespace-pre-wrap">{error.stack}</pre>
                    </div>
                  )}
                </div>
              </details>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (level === 'section') {
    return (
      <Alert className="my-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          <div className="space-y-2">
            <div className="font-medium">{getErrorTitle()}</div>
            <div className="text-sm">{getErrorMessage()}</div>
            <Button size="sm" onClick={onRetry} className="mt-2">
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  // Component level
  return (
    <div className="p-4 border border-destructive/20 rounded-lg bg-destructive/5">
      <div className="flex items-start gap-3">
        <div className="text-destructive mt-0.5">
          <AlertTriangle className="h-4 w-4" />
        </div>
        <div className="flex-1 space-y-2">
          <div className="font-medium text-sm">{getErrorTitle()}</div>
          <div className="text-xs text-muted-foreground">{getErrorMessage()}</div>
          <Button size="sm" variant="outline" onClick={onRetry}>
            <RefreshCw className="h-3 w-3 mr-1" />
            Retry
          </Button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Specialized Error Boundaries
// ============================================================================

export function MetadataErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      level="section"
      onError={(error, errorInfo) => {
        console.error('Metadata processing error:', error);
      }}
      fallback={
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Unable to display metadata. The file may be corrupted or in an unsupported format.
          </AlertDescription>
        </Alert>
      }
    >
      {children}
    </ErrorBoundary>
  );
}

export function AdvancedAnalysisErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      level="section"
      onError={(error, errorInfo) => {
        console.error('Advanced analysis error:', error);
      }}
      fallback={
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Advanced analysis features are temporarily unavailable. Basic metadata is still accessible.
          </AlertDescription>
        </Alert>
      }
    >
      {children}
    </ErrorBoundary>
  );
}

export function NetworkErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      level="component"
      onError={(error, errorInfo) => {
        if (error.message.includes('fetch') || error.message.includes('network')) {
          console.error('Network error:', error);
        }
      }}
    >
      {children}
    </ErrorBoundary>
  );
}

// ============================================================================
// Error Reporting Utilities
// ============================================================================

export function reportError(error: Error, errorInfo: ErrorInfo, errorId: string) {
  // In a real application, you would send this to your error reporting service
  // Example: Sentry, LogRocket, Bugsnag, etc.
  
  const errorReport = {
    errorId,
    message: error.message,
    stack: error.stack,
    componentStack: errorInfo.componentStack,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href,
  };
  
  if (process.env.NODE_ENV === 'development') {
    console.log('Error report:', errorReport);
  } else {
    // Send to error reporting service
    // fetch('/api/errors', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(errorReport)
    // });
  }
}

// ============================================================================
// HOC for Error Boundaries
// ============================================================================

export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Partial<ErrorBoundaryProps>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`;
  
  return WrappedComponent;
}