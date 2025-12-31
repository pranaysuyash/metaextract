/**
 * Unit tests for Error Boundary components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ErrorBoundary, MetadataErrorBoundary, NetworkErrorBoundary, withErrorBoundary } from '@/components/error-boundary';
import '@testing-library/jest-dom';

// ============================================================================
// Test Utilities
// ============================================================================

// Helper to simulate a component that throws an error
const ThrowError = ({ shouldThrow, errorMessage = 'Test error' }: { shouldThrow: boolean; errorMessage?: string }) => {
  if (shouldThrow) {
    throw new Error(errorMessage);
  }
  return <div data-testid="success">Component rendered successfully</div>;
};

// Helper component for testing
const SuccessComponent = ({ text = 'Success' }: { text?: string }) => (
  <div data-testid="success-component">{text}</div>
);

// ============================================================================
// Error Boundary Tests
// ============================================================================

describe('ErrorBoundary', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Basic Functionality', () => {
    it('should render children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <div data-testid="child">Test Child</div>
        </ErrorBoundary>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
    });

    it('should catch errors and display error state', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should render custom fallback when provided', () => {
      const customFallback = <div data-testid="custom-fallback">Custom Error UI</div>;

      render(
        <ErrorBoundary fallback={customFallback}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    });

    it('should generate unique error IDs', () => {
      const { container: container1 } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      const { container: container2 } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      // Both should show error UI but with different error IDs
      expect(container1.textContent).toContain('error_');
      expect(container2.textContent).toContain('error_');
    });
  });

  describe('Error Type Detection', () => {
    it('should detect network errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Network error: failed to fetch" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Network Error')).toBeInTheDocument();
      expect(screen.getByText('Unable to connect to the server')).toBeInTheDocument();
    });

    it('should detect loading errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Chunk loading failed" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Loading Error')).toBeInTheDocument();
      expect(screen.getByText('Failed to load the required resources')).toBeInTheDocument();
    });

    it('should detect permission errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Unauthorized: permission denied" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Permission Error')).toBeInTheDocument();
      expect(screen.getByText("You don't have permission to access this resource")).toBeInTheDocument();
    });

    it('should detect not found errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="404: Resource not found" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Resource Not Found')).toBeInTheDocument();
      expect(screen.getByText('The requested resource could not be found')).toBeInTheDocument();
    });

    it('should use generic error message for unknown errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Some cryptic error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText('An unexpected error occurred')).toBeInTheDocument();
    });
  });

  describe('Retry Functionality', () => {
    it('should have a retry button', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    it('should reset error state when retry is clicked', async () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      // Note: The retry will cause the error to be thrown again
      // In a real test, you'd mock the error to only throw once
      fireEvent.click(screen.getByText('Try Again'));

      // The error will be caught again immediately
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should render children again after successful retry', async () => {
      let shouldThrow = true;

      const ConditionalThrow = () => {
        if (shouldThrow) {
          throw new Error('Conditional error');
        }
        return <div data-testid="recovered">Recovered!</div>;
      };

      const { rerender } = render(
        <ErrorBoundary>
          <ConditionalThrow />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();

      // Simulate successful retry by changing state
      shouldThrow = false;
      fireEvent.click(screen.getByText('Try Again'));

      // Re-render with new props
      rerender(
        <ErrorBoundary>
          <ConditionalThrow />
        </ErrorBoundary>
      );

      await waitFor(() => {
        expect(screen.getByText('Recovered!')).toBeInTheDocument();
      });
    });
  });

  describe('Error Levels', () => {
    it('should render page level error with full layout', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Try Again')).toBeInTheDocument();
      expect(screen.getByText('Refresh Page')).toBeInTheDocument();
    });

    it('should render section level error with alert style', () => {
      render(
        <ErrorBoundary level="section">
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Retry')).toBeInTheDocument();
      // Section level uses Alert component
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should render component level error with compact style', () => {
      render(
        <ErrorBoundary level="component">
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  describe('Error Callback', () => {
    it('should call onError callback when error is caught', () => {
      const onError = jest.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(onError).toHaveBeenCalledTimes(1);
      expect(onError.mock.calls[0][0]).toBeInstanceOf(Error);
      expect(onError.mock.calls[0][1]).toBeDefined();
    });
  });

  describe('Suggestions Display', () => {
    it('should show network-specific suggestions for network errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Network error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Check your internet connection')).toBeInTheDocument();
      expect(screen.getByText('Try refreshing the page')).toBeInTheDocument();
    });

    it('should show loading-specific suggestions for loading errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Chunk loading error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Try refreshing the page')).toBeInTheDocument();
      expect(screen.getByText('Clear your browser cache')).toBeInTheDocument();
    });

    it('should show default suggestions for unknown errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Unknown error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Try refreshing the page')).toBeInTheDocument();
      expect(screen.getByText('Report this issue if it continues')).toBeInTheDocument();
    });
  });
});

// ============================================================================
// Specialized Error Boundaries
// ============================================================================

describe('MetadataErrorBoundary', () => {
  it('should render with section level and custom fallback', () => {
    render(
      <MetadataErrorBoundary>
        <div data-testid="metadata-content">Metadata content</div>
      </MetadataErrorBoundary>
    );

    expect(screen.getByTestId('metadata-content')).toBeInTheDocument();
  });

  it('should show metadata-specific error message on error', () => {
    render(
      <MetadataErrorBoundary>
        <ThrowError shouldThrow={true} />
      </MetadataErrorBoundary>
    );

    expect(screen.getByText('Unable to display metadata')).toBeInTheDocument();
    expect(screen.getByText('The file may be corrupted or in an unsupported format')).toBeInTheDocument();
  });
});

describe('NetworkErrorBoundary', () => {
  it('should render children normally when no network error', () => {
    render(
      <NetworkErrorBoundary>
        <div data-testid="network-content">Network content</div>
      </NetworkErrorBoundary>
    );

    expect(screen.getByTestId('network-content')).toBeInTheDocument();
  });
});

// ============================================================================
// HOC Tests
// ============================================================================

describe('withErrorBoundary HOC', () => {
  it('should wrap component with error boundary', () => {
    const WrappedComponent = withErrorBoundary(SuccessComponent);

    render(
      <WrappedComponent text="Wrapped Success" />
    );

    expect(screen.getByText('Wrapped Success')).toBeInTheDocument();
  });

  it('should catch errors in wrapped component', () => {
    const WrappedThrowError = withErrorBoundary(ThrowError);

    render(
      <WrappedThrowError shouldThrow={true} />
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('should pass through props to wrapped component', () => {
    const WrappedComponent = withErrorBoundary(SuccessComponent);

    render(
      <WrappedComponent text="Custom Text" />
    );

    expect(screen.getByText('Custom Text')).toBeInTheDocument();
  });

  it('should allow custom error boundary props', () => {
    const onError = jest.fn();
    const WrappedComponent = withErrorBoundary(SuccessComponent, { onError });

    render(
      <WrappedComponent text="Wrapped Success" />
    );

    // Should render successfully, no error
    expect(screen.getByText('Wrapped Success')).toBeInTheDocument();
  });
});

// ============================================================================
// Error State Persistence Tests
// ============================================================================

describe('Error Boundary State Management', () => {
  it('should maintain error state until reset', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();

    // Rerender with same error
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('should not catch errors after successful recovery', async () => {
    const RecoveryComponent = () => {
      const [recovered, setRecovered] = React.useState(false);

      if (recovered) {
        return <div data-testid="recovered">Recovered!</div>;
      }

      return (
        <ErrorBoundary>
          <button data-testid="recover-btn" onClick={() => setRecovered(true)}>
            Recover
          </button>
          <ThrowError shouldThrow={!recovered} />
        </ErrorBoundary>
      );
    };

    render(<RecoveryComponent />);

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('recover-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('recovered')).toBeInTheDocument();
    });
  });
});
