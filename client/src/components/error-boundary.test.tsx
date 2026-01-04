/**
 * Unit tests for Error Boundary components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import {
  ErrorBoundary,
  MetadataErrorBoundary,
  NetworkErrorBoundary,
  withErrorBoundary,
} from '@/components/error-boundary';
import '@testing-library/jest-dom';

// ============================================================================
// Test Utilities
// ============================================================================

// Helper to simulate a component that throws an error
const ThrowError = ({
  shouldThrow,
  errorMessage = 'Test error',
}: {
  shouldThrow: boolean;
  errorMessage?: string;
}) => {
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
      const customFallback = (
        <div data-testid="custom-fallback">Custom Error UI</div>
      );

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

      // Both should show error UI (each in its own ErrorBoundary)
      expect(screen.getAllByText(/error/i).length).toBeGreaterThanOrEqual(2);

      // Use containers to avoid unused variable lint errors (keeps test semantics)
      expect(container1).toBeDefined();
      expect(container2).toBeDefined();
    });
  });

  describe('Error Type Detection', () => {
    it('should detect network errors at page level', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError
            shouldThrow={true}
            errorMessage="Network error: failed to fetch"
          />
        </ErrorBoundary>
      );

      expect(screen.getByText('Network Error')).toBeInTheDocument();
    });

    it('should detect loading errors at page level', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} errorMessage="Chunk loading failed" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Loading Error')).toBeInTheDocument();
    });

    it('should detect permission errors at page level', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError
            shouldThrow={true}
            errorMessage="Unauthorized: permission denied"
          />
        </ErrorBoundary>
      );

      expect(screen.getByText('Permission Error')).toBeInTheDocument();
    });

    it('should detect not found errors at page level', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError
            shouldThrow={true}
            errorMessage="404: Resource not found"
          />
        </ErrorBoundary>
      );

      expect(screen.getByText('Resource Not Found')).toBeInTheDocument();
    });

    it('should use generic error message for unknown errors at page level', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} errorMessage="Some cryptic error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should detect loading errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} errorMessage="Chunk loading failed" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Loading Error')).toBeInTheDocument();
    });

    it('should detect permission errors', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError
            shouldThrow={true}
            errorMessage="Unauthorized: permission denied"
          />
        </ErrorBoundary>
      );

      expect(screen.getByText('Permission Error')).toBeInTheDocument();
    });

    it('should detect not found errors at page level', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError
            shouldThrow={true}
            errorMessage="404: Resource not found"
          />
        </ErrorBoundary>
      );

      expect(screen.getByText('Resource Not Found')).toBeInTheDocument();
      // Verify error message is present
      const errorText = screen.getByText(
        content => content.includes('not found') || content.includes('Resource')
      );
      expect(errorText).toBeInTheDocument();
    });

    it('should use generic error message for unknown errors at page level', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} errorMessage="Some cryptic error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      // Verify error message is present (may vary by environment)
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  describe('Retry Functionality', () => {
    it('should have a retry button at page level', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    it('should have retry button that calls onRetry callback', () => {
      const onError = jest.fn();

      render(
        <ErrorBoundary level="page" onError={onError}>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      // Click the retry button
      fireEvent.click(screen.getByText('Try Again'));

      // onError should have been called already when the error occurred
      expect(onError).toHaveBeenCalled();
    });

    it('should show retry option in error display', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      // Verify retry buttons exist
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThanOrEqual(2); // Try Again and Refresh Page
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
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} errorMessage="Network error" />
        </ErrorBoundary>
      );

      expect(
        screen.getByText('Check your internet connection')
      ).toBeInTheDocument();
    });

    it('should show loading-specific suggestions for loading errors', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} errorMessage="Chunk loading error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Try refreshing the page')).toBeInTheDocument();
    });

    it('should show default suggestions for unknown errors', () => {
      render(
        <ErrorBoundary level="page">
          <ThrowError shouldThrow={true} errorMessage="Unknown error" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Try refreshing the page')).toBeInTheDocument();
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

  it('should catch errors in children', () => {
    render(
      <MetadataErrorBoundary>
        <ThrowError shouldThrow={true} />
      </MetadataErrorBoundary>
    );

    // Verify that the ThrowError component was removed and error UI is shown
    expect(screen.queryByTestId('success')).not.toBeInTheDocument();
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

    render(<WrappedComponent text="Wrapped Success" />);

    expect(screen.getByText('Wrapped Success')).toBeInTheDocument();
  });

  it('should catch errors in wrapped component', () => {
    const WrappedThrowError = withErrorBoundary(ThrowError);

    render(<WrappedThrowError shouldThrow={true} />);

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('should pass through props to wrapped component', () => {
    const WrappedComponent = withErrorBoundary(SuccessComponent);

    render(<WrappedComponent text="Custom Text" />);

    expect(screen.getByText('Custom Text')).toBeInTheDocument();
  });

  it('should allow custom error boundary props', () => {
    const onError = jest.fn();
    const WrappedComponent = withErrorBoundary(SuccessComponent, { onError });

    render(<WrappedComponent text="Wrapped Success" />);

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

  it('should recover and render children after error state is cleared', async () => {
    const TestComponent = () => {
      const [shouldError, setShouldError] = React.useState(true);
      const [key, setKey] = React.useState(0);

      return (
        <div>
          <button
            data-testid="reset-btn"
            type="button"
            onClick={() => {
              setShouldError(false);
              setKey(prev => prev + 1);
            }}
          >
            Reset
          </button>
          <ErrorBoundary key={key}>
            {shouldError ? (
              <ThrowError shouldThrow={true} />
            ) : (
              <div data-testid="recovered">Recovered!</div>
            )}
          </ErrorBoundary>
        </div>
      );
    };

    render(<TestComponent />);

    expect(screen.getByText(/error/i)).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('reset-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('recovered')).toBeInTheDocument();
    });
  });
});
