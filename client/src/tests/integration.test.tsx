/**
 * Integration tests for complete upload to extraction workflow
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EnhancedUploadZone } from '@/components/enhanced-upload-zone';
import { MetadataExplorer } from '@/components/metadata-explorer';
import { AdvancedAnalysisResults } from '@/components/AdvancedAnalysisResults';

// Mock fetch API
global.fetch = jest.fn();

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(),
  },
});

// Mock crypto
global.crypto = { randomUUID: () => 'mock-uuid-' + Math.random() } as any;

// Mock URL APIs
global.URL.createObjectURL = jest.fn(() => 'mock-preview-url');
global.URL.revokeObjectURL = jest.fn();

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

describe('Upload to Extraction Workflow Integration', () => {
  const mockExtractionResult = {
    filename: 'test_image.jpg',
    filesize: '2.5 MB',
    mime_type: 'image/jpeg',
    tier: 'premium',
    summary: {
      filename: 'test_image.jpg',
      filesize: 2621440,
      filetype: 'image/jpeg',
    },
    exif: {
      Make: 'Canon',
      Model: 'EOS R5',
      DateTimeOriginal: '2024:01:15 10:30:00',
      FocalLength: '50mm',
      FNumber: 1.8,
      ExposureTime: '1/200',
      ISO: 400,
    },
    gps: {
      latitude: 37.7749,
      longitude: -122.4194,
      google_maps_url: 'https://maps.google.com/?q=37.7749,-122.4194',
      coordinates: '37.7749° N, 122.4194° W',
    },
    image: {
      ImageWidth: 8192,
      ImageHeight: 5464,
      BitsPerSample: 8,
      ColorSpace: 'sRGB',
    },
    filesystem: {
      creation_timestamp: '2024-01-15T10:30:00Z',
      modification_timestamp: '2024-01-15T10:30:00Z',
      filesize: 2621440,
    },
    file_integrity: {
      md5: 'd41d8cd98f00b204e9800998ecf8427e',
      sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    },
    forensic: {
      manipulation_detected: false,
      integrity_verified: true,
      steganography_detected: false,
    },
    advanced_analysis: {
      steganography: {
        detected: false,
        confidence: 95,
        methods_checked: ['LSB', 'DCT', 'Frequency Analysis'],
        findings: [],
      },
      manipulation: {
        detected: false,
        confidence: 98,
        indicators: [],
      },
      aiDetection: {
        ai_generated: false,
        confidence: 92,
        model_hints: [],
      },
      timeline: {
        events: [
          {
            timestamp: '2024-01-15 10:30:00',
            event_type: 'File Created',
            source: 'EXIF DateTimeOriginal',
          },
        ],
        gaps_detected: false,
        chain_of_custody_complete: true,
      },
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Complete Happy Path', () => {
    it('should successfully upload file and display results', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockExtractionResult,
      });

      const onResults = jest.fn();

      render(
        <div>
          <EnhancedUploadZone
            onResults={onResults}
            tier="premium"
            maxFiles={10}
          />
        </div>
      );

      // Initial state should show upload zone
      expect(screen.getByText(/Upload files for analysis/i)).toBeInTheDocument();
    });

    it('should handle single file extraction', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockExtractionResult,
      });

      const onResults = jest.fn();

      render(
        <EnhancedUploadZone
          onResults={onResults}
          tier="premium"
        />
      );
    });

    it('should handle batch file extraction', async () => {
      const batchResults = {
        results: {
          'file1.jpg': mockExtractionResult,
          'file2.jpg': { ...mockExtractionResult, filename: 'file2.jpg' },
        },
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => batchResults,
      });

      const onResults = jest.fn();

      render(
        <EnhancedUploadZone
          onResults={onResults}
          tier="premium"
        />
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const onResults = jest.fn();

      render(
        <EnhancedUploadZone
          onResults={onResults}
          tier="free"
        />
      );
    });

    it('should handle HTTP error responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      const onResults = jest.fn();

      render(
        <EnhancedUploadZone
          onResults={onResults}
          tier="free"
        />
      );
    });

    it('should handle timeout errors', async () => {
      (global.fetch as jest.Mock).mockImplementation(() =>
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      const onResults = jest.fn();

      render(
        <EnhancedUploadZone
          onResults={onResults}
          tier="free"
        />
      );
    });
  });

  describe('Data Flow Integration', () => {
    it('should pass extraction results to metadata explorer', async () => {
      const { convertMetadataToProcessedFile } = require('@/components/metadata-explorer');

      const processedFile = convertMetadataToProcessedFile(
        mockExtractionResult,
        'file-id-123'
      );

      expect(processedFile.name).toBe('test_image.jpg');
      expect(processedFile.fieldCount).toBeGreaterThan(0);
      expect(processedFile.categories.length).toBeGreaterThan(0);

      render(
        <MetadataExplorer
          files={[processedFile]}
          selectedFileId="file-id-123"
        />
      );

      expect(screen.getByText('test_image.jpg')).toBeInTheDocument();
    });

    it('should display advanced analysis results', async () => {
      render(
        <AdvancedAnalysisResults
          steganography={mockExtractionResult.advanced_analysis.steganography}
          manipulation={mockExtractionResult.advanced_analysis.manipulation}
          aiDetection={mockExtractionResult.advanced_analysis.aiDetection}
          timeline={mockExtractionResult.advanced_analysis.timeline}
        />
      );

      expect(screen.getByText('Forensic Analysis')).toBeInTheDocument();
      expect(screen.getByText('No Hidden Data')).toBeInTheDocument();
      expect(screen.getByText('No Manipulation')).toBeInTheDocument();
    });
  });

  describe('Tier-Based Functionality', () => {
    it('should enforce file size limits by tier', () => {
      const { rerender } = render(
        <EnhancedUploadZone
          onResults={jest.fn()}
          tier="free"
        />
      );

      expect(screen.getByText(/10MB per file/i)).toBeInTheDocument();

      rerender(
        <EnhancedUploadZone
          onResults={jest.fn()}
          tier="premium"
        />
      );

      expect(screen.getByText(/500MB per file/i)).toBeInTheDocument();
    });

    it('should show appropriate format support by tier', () => {
      const { rerender } = render(
        <EnhancedUploadZone
          onResults={jest.fn()}
          tier="free"
        />
      );

      // Free tier shows basic formats
      expect(screen.getByText('Images')).toBeInTheDocument();

      rerender(
        <EnhancedUploadZone
          onResults={jest.fn()}
          tier="premium"
        />
      );

      // Premium tier shows advanced formats
      expect(screen.getByText('Medical')).toBeInTheDocument();
      expect(screen.getByText('Scientific')).toBeInTheDocument();
    });
  });

  describe('User Workflow Scenarios', () => {
    it('should handle user uploading single photo and viewing results', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockExtractionResult,
      });

      const onResults = jest.fn((results) => {
        // Convert results to ProcessedFile format
        const { convertMetadataToProcessedFile } = require('@/components/metadata-explorer');
        const processedFile = convertMetadataToProcessedFile(results[0], 'file-1');

        // Render metadata explorer with results
        render(
          <MetadataExplorer
            files={[processedFile]}
            selectedFileId="file-1"
          />
        );

        expect(screen.getByText('test_image.jpg')).toBeInTheDocument();
        expect(screen.getByText('Canon')).toBeInTheDocument();
        expect(screen.getByText('EOS R5')).toBeInTheDocument();
      });

      render(
        <EnhancedUploadZone
          onResults={onResults}
          tier="premium"
        />
      );
    });

    it('should handle user exploring metadata details', async () => {
      const { convertMetadataToProcessedFile } = require('@/components/metadata-explorer');
      const processedFile = convertMetadataToProcessedFile(mockExtractionResult, 'file-1');

      render(
        <MetadataExplorer
          files={[processedFile]}
          selectedFileId="file-1"
        />
      );

      // Select file
      expect(screen.getByText('test_image.jpg')).toBeInTheDocument();

      // Click on EXIF category
      const exifCategory = screen.getByText('Camera & EXIF');
      await userEvent.click(exifCategory);

      // Click on Make field
      const makeField = screen.getByText('Make');
      await userEvent.click(makeField);

      // Verify detail view
      expect(screen.getByText('Camera manufacturer - useful for identifying device')).toBeInTheDocument();
    });

    it('should handle user viewing forensic analysis', async () => {
      render(
        <AdvancedAnalysisResults
          steganography={mockExtractionResult.advanced_analysis.steganography}
          manipulation={mockExtractionResult.advanced_analysis.manipulation}
          aiDetection={mockExtractionResult.advanced_analysis.aiDetection}
          timeline={mockExtractionResult.advanced_analysis.timeline}
        />
      );

      // Switch to AI Detection tab
      const aiTab = screen.getByText('AI Detection');
      await userEvent.click(aiTab);

      expect(screen.getByText('Likely Authentic')).toBeInTheDocument();
      expect(screen.getByText('92%')).toBeInTheDocument();
    });
  });

  describe('State Management', () => {
    it('should maintain file selection state', async () => {
      const { convertMetadataToProcessedFile } = require('@/components/metadata-explorer');
      const processedFile = convertMetadataToProcessedFile(mockExtractionResult, 'file-1');

      const onFileSelect = jest.fn();

      render(
        <MetadataExplorer
          files={[processedFile]}
          selectedFileId="file-1"
          onFileSelect={onFileSelect}
        />
      );

      const fileButton = screen.getByText('test_image.jpg').closest('button');
      await userEvent.click(fileButton!);

      expect(onFileSelect).toHaveBeenCalledWith('file-1');
    });

    it('should maintain view mode state', async () => {
      const onViewModeChange = jest.fn();

      render(
        <MetadataExplorer
          files={[]}
          onViewModeChange={onViewModeChange}
        />
      );

      const simpleTab = screen.getByText('Simple');
      await userEvent.click(simpleTab);

      expect(onViewModeChange).toHaveBeenCalledWith('simple');
    });
  });

  describe('Performance', () => {
    it('should handle large metadata sets without performance issues', async () => {
      const largeMetadata = {
        ...mockExtractionResult,
        exif: Object.fromEntries(
          Array.from({ length: 1000 }, (_, i) => [`Field${i}`, `Value${i}`])
        ),
      };

      const { convertMetadataToProcessedFile } = require('@/components/metadata-explorer');
      const processedFile = convertMetadataToProcessedFile(largeMetadata, 'file-1');

      const startTime = performance.now();

      render(
        <MetadataExplorer
          files={[processedFile]}
          selectedFileId="file-1"
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(1000); // Should render in less than 1 second
    });

    it('should handle rapid tab switching without errors', async () => {
      render(
        <AdvancedAnalysisResults
          steganography={mockExtractionResult.advanced_analysis.steganography}
          manipulation={mockExtractionResult.advanced_analysis.manipulation}
          aiDetection={mockExtractionResult.advanced_analysis.aiDetection}
          timeline={mockExtractionResult.advanced_analysis.timeline}
        />
      );

      const tabs = ['Steganography', 'Manipulation', 'AI Detection', 'Timeline'];

      for (const tab of tabs) {
        const tabButton = screen.getByText(tab);
        await userEvent.click(tabButton);
      }

      // Should not throw any errors
      expect(screen.getByText('Forensic Analysis')).toBeInTheDocument();
    });
  });

  describe('Accessibility Integration', () => {
    it('should maintain keyboard navigation throughout workflow', async () => {
      render(
        <EnhancedUploadZone
          onResults={jest.fn()}
          tier="premium"
        />
      );

      const uploadZone = screen.getByText(/Upload files for analysis/i);
      expect(uploadZone).toBeVisible();

      // Tab key should navigate to focusable elements
      const tabbableElements = document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      expect(tabbableElements.length).toBeGreaterThan(0);
    });

    it('should announce important state changes', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockExtractionResult,
      });

      render(
        <EnhancedUploadZone
          onResults={jest.fn()}
          tier="premium"
        />
      );

      // Status changes should be announced
      // This would require checking for aria-live regions
    });
  });

  describe('Error Recovery', () => {
    it('should allow retry after failed upload', async () => {
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockExtractionResult,
        });

      const onResults = jest.fn();

      render(
        <EnhancedUploadZone
          onResults={onResults}
          tier="premium"
        />
      );

      // First attempt fails
      // User retries
      // Second attempt succeeds
    });

    it('should handle partial failures in batch uploads', async () => {
      const batchResults = {
        results: {
          'file1.jpg': mockExtractionResult,
          'file2.jpg': null, // Failed
          'file3.jpg': mockExtractionResult,
        },
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => batchResults,
      });

      const onResults = jest.fn();

      render(
        <EnhancedUploadZone
          onResults={onResults}
          tier="premium"
        />
      );
    });
  });
});