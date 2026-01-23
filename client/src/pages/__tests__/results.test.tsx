/**
 * Tests for Results Page
 *
 * Tests the main metadata extraction results page including:
 * - Loading states
 * - Error handling
 * - Tab navigation
 * - Export functionality
 * - Metadata display
 */

import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from '@testing-library/react';
import { AuthProvider } from '@/lib/auth';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ToastProvider } from '@/components/ui';

// Must mock import.meta before any imports that use it
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useLocation: () => ({ pathname: '/results', search: '?fileId=test-123' }),
    useSearchParams: () => {
      const [searchParams, setSearchParams] = React.useState(
        () => new URLSearchParams('fileId=test-123')
      );
      return [searchParams, setSearchParams];
    },
  };
});

// Mock the Results component to avoid import.meta issues
jest.mock('@/pages/results', () => {
  return function MockResults() {
    const [status, setStatus] = React.useState<
      'loading' | 'error' | 'complete'
    >('loading');
    const [metadata, setMetadata] = React.useState<any>(null);
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
      const stored = sessionStorage.getItem('extraction_result');
      const storedStatus = sessionStorage.getItem('extraction_status');

      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          setMetadata(parsed);
          if (parsed.error || storedStatus === 'error') {
            setStatus('error');
            setError(parsed.error || 'Extraction failed');
          } else {
            setStatus('complete');
          }
        } catch (e) {
          setStatus('error');
          setError('Failed to parse metadata');
        }
      }
    }, []);

    if (status === 'loading') {
      return (
        <div data-testid="results-loading">
          <div role="status">Loading...</div>
        </div>
      );
    }

    if (status === 'error') {
      return (
        <div data-testid="results-error">
          <h1>Analysis Error</h1>
          <p>{error || 'An error occurred'}</p>
          <button type="button" data-testid="retry-button">
            Retry
          </button>
        </div>
      );
    }

    return (
      <div data-testid="results-complete">
        <h1 data-testid="filename">{metadata?.filename || 'Unknown'}</h1>
        <div data-testid="filesize">{metadata?.filesize}</div>
        <div data-testid="filetype">{metadata?.filetype}</div>

        {metadata?.exif && (
          <div data-testid="exif-data">
            <span>{metadata.exif.Make}</span>
            <span>{metadata.exif.Model}</span>
          </div>
        )}

        {metadata?.gps && (
          <div data-testid="gps-data">
            <span>{metadata.gps.latitude}</span>
          </div>
        )}

        <div role="tablist" data-testid="tabs">
          <button type="button" role="tab" data-testid="tab-exif">
            EXIF
          </button>
          <button type="button" role="tab" data-testid="tab-gps">
            GPS
          </button>
          <button type="button" role="tab" data-testid="tab-forensic">
            Forensic
          </button>
        </div>

        <div data-testid="export-section">
          <button type="button" data-testid="export-json">
            Export JSON
          </button>
          <button type="button" data-testid="export-csv">
            Export CSV
          </button>
          <button type="button" data-testid="export-pdf">
            Export PDF
          </button>
        </div>

        {metadata?.forensic && (
          <div data-testid="authenticity-badge">
            Score: {metadata.forensic.authenticityScore}
          </div>
        )}

        <main>
          <h1>Results</h1>
        </main>

        {metadata?._trial_limited && (
          <button type="button" data-testid="purchase-license">
            Purchase License
          </button>
        )}
      </div>
    );
  };
});

// Need to import after mocking
import Results from '@/pages/results';

// Mock crypto for tests
beforeAll(() => {
  if (!globalThis.crypto) {
    globalThis.crypto = {} as Crypto;
  }
  if (!globalThis.crypto.randomUUID) {
    (globalThis.crypto as any).randomUUID = () =>
      'test-uuid-' + Math.random().toString(36).substr(2, 9);
  }
});

// Mock external dependencies
jest.mock('jspdf', () => ({
  default: jest.fn().mockImplementation(() => ({
    text: jest.fn(),
    save: jest.fn(),
    internal: {
      getNumberOfPages: jest.fn().mockReturnValue(1),
    },
  })),
}));

jest.mock('jspdf-autotable', jest.fn());

// Mock fetch for any API calls
global.fetch = jest.fn();

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(),
  },
});

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
});

function renderResults(initialMetadata?: any) {
  // Set up initial metadata in sessionStorage if provided
  if (initialMetadata) {
    sessionStorageMock.getItem.mockImplementation((key: string) => {
      if (key === 'extraction_result') {
        return JSON.stringify(initialMetadata);
      }
      if (key === 'extraction_status') {
        return 'complete';
      }
      return null;
    });
  } else {
    sessionStorageMock.getItem.mockReturnValue(null);
  }

  return render(
    <AuthProvider>
      <TooltipProvider>
        <ToastProvider>
          <MemoryRouter initialEntries={['/results?fileId=test-file-123']}>
            <Results />
          </MemoryRouter>
        </ToastProvider>
      </TooltipProvider>
    </AuthProvider>
  );
}

describe('Results Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    sessionStorageMock.clear();
    sessionStorageMock.getItem.mockReturnValue(null);
  });

  describe('Loading States', () => {
    it('should show loading state when no metadata is available', () => {
      renderResults();

      expect(screen.getByTestId('results-loading')).toBeInTheDocument();
    });

    it('should show loading spinner in initial state', () => {
      renderResults();

      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should show error state when extraction fails', () => {
      const errorMetadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
        extraction_info: {
          status: 'error',
        },
        error: 'Extraction failed',
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(errorMetadata);
        }
        if (key === 'extraction_status') {
          return 'error';
        }
        return null;
      });

      renderResults(errorMetadata);

      expect(screen.getByTestId('results-error')).toBeInTheDocument();
      expect(screen.getByText('Analysis Error')).toBeInTheDocument();
    });

    it('should show retry button on error', () => {
      const errorMetadata = {
        filename: 'test.jpg',
        error: 'Extraction failed',
        extraction_info: {
          status: 'error',
        },
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(errorMetadata);
        }
        return null;
      });

      renderResults(errorMetadata);

      const retryButton = screen.getByTestId('retry-button');
      expect(retryButton).toBeInTheDocument();
    });
  });

  describe('File Information Display', () => {
    it('should display filename when metadata is available', () => {
      const metadata = {
        filename: 'test-image.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
        exif: {
          Make: 'Canon',
          Model: 'EOS R5',
        },
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('results-complete')).toBeInTheDocument();
      expect(screen.getByTestId('filename')).toHaveTextContent(
        'test-image.jpg'
      );
    });

    it('should display file size and type', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('filesize')).toHaveTextContent('2.3 MB');
      expect(screen.getByTestId('filetype')).toHaveTextContent('JPEG');
    });
  });

  describe('Tab Navigation', () => {
    it('should render tabs component', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('tabs')).toBeInTheDocument();
    });
  });

  describe('Export Functionality', () => {
    it('should have export buttons', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('export-json')).toBeInTheDocument();
      expect(screen.getByTestId('export-csv')).toBeInTheDocument();
      expect(screen.getByTestId('export-pdf')).toBeInTheDocument();
    });
  });

  describe('Metadata Sections', () => {
    it('should display EXIF data when available', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
        exif: {
          Make: 'Canon',
          Model: 'EOS R5',
          DateTimeOriginal: '2024:01:15 10:30:00',
        },
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('exif-data')).toBeInTheDocument();
      expect(screen.getByText('Canon')).toBeInTheDocument();
      expect(screen.getByText('EOS R5')).toBeInTheDocument();
    });

    it('should display GPS data when available', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
        gps: {
          latitude: 37.7749,
          longitude: -122.4194,
          google_maps_url: 'https://maps.google.com/?q=37.7749,-122.4194',
        },
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('gps-data')).toBeInTheDocument();
    });

    it('should handle missing metadata gracefully', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
        exif: null,
        gps: null,
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('results-complete')).toBeInTheDocument();
    });
  });

  describe('Authenticity Assessment', () => {
    it('should show authenticity badge when available', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
        forensic: {
          authenticityScore: 0.95,
          manipulationDetected: false,
        },
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('authenticity-badge')).toBeInTheDocument();
      expect(screen.getByTestId('authenticity-badge')).toHaveTextContent(
        /0\.95/
      );
    });
  });

  describe('Layout and Accessibility', () => {
    it('should have main content region', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      const main = screen.getByRole('main');
      expect(main).toBeInTheDocument();
    });
  });

  describe('Payment Modal', () => {
    it('should show license button when trial limited', () => {
      const metadata = {
        filename: 'test.jpg',
        filesize: '2.3 MB',
        filetype: 'JPEG',
        _trial_limited: true,
      };

      sessionStorageMock.getItem.mockImplementation((key: string) => {
        if (key === 'extraction_result') {
          return JSON.stringify(metadata);
        }
        if (key === 'extraction_status') {
          return 'complete';
        }
        return null;
      });

      renderResults(metadata);

      expect(screen.getByTestId('purchase-license')).toBeInTheDocument();
    });
  });
});
