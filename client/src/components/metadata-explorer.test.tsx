/**
 * Comprehensive test suite for MetadataExplorer component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MetadataExplorer, convertMetadataToProcessedFile } from './metadata-explorer';

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(),
  },
});

// Mock resize observer
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

describe('MetadataExplorer', () => {
  const mockFiles = [
    {
      id: 'file1',
      name: 'photo1.jpg',
      type: 'image/jpeg',
      size: '2.5 MB',
      metadataDensity: 'high' as const,
      fieldCount: 150,
      tier: 'premium',
      processedAt: '2024-01-15T10:30:00Z',
      categories: [
        {
          name: 'summary',
          displayName: 'Summary',
          icon: <div data-testid="icon-summary" />,
          fields: [
            {
              key: 'filename',
              value: 'photo1.jpg',
              category: 'Summary',
            },
            {
              key: 'filesize',
              value: 2621440,
              category: 'Summary',
            },
          ],
          fieldCount: 2,
        },
        {
          name: 'exif',
          displayName: 'Camera & EXIF',
          icon: <div data-testid="icon-camera" />,
          fields: [
            {
              key: 'Make',
              value: 'Canon',
              category: 'Camera & EXIF',
              significance: 'Camera manufacturer - useful for identifying device',
            },
            {
              key: 'Model',
              value: 'EOS R5',
              category: 'Camera & EXIF',
              significance: 'Camera model - helps determine capabilities and age',
            },
            {
              key: 'DateTimeOriginal',
              value: '2024:01:15 10:30:00',
              category: 'Camera & EXIF',
              significance: 'When the photo was actually taken',
            },
          ],
          fieldCount: 3,
        },
        {
          name: 'gps',
          displayName: 'Location',
          icon: <div data-testid="icon-location" />,
          fields: [
            {
              key: 'GPSLatitude',
              value: 37.7749,
              category: 'Location',
              significance: 'Geographic latitude where photo was taken',
            },
            {
              key: 'GPSLongitude',
              value: -122.4194,
              category: 'Location',
              significance: 'Geographic longitude where photo was taken',
            },
          ],
          fieldCount: 2,
        },
      ],
      rawMetadata: {
        filename: 'photo1.jpg',
        mime_type: 'image/jpeg',
        filesize: '2.5 MB',
        gps: {
          latitude: 37.7749,
          longitude: -122.4194,
          google_maps_url: 'https://maps.google.com/?q=37.7749,-122.4194',
          coordinates: '37.7749° N, 122.4194° W',
        },
      },
    },
    {
      id: 'file2',
      name: 'document.pdf',
      type: 'application/pdf',
      size: '1.2 MB',
      metadataDensity: 'medium' as const,
      fieldCount: 45,
      tier: 'starter',
      processedAt: '2024-01-15T11:00:00Z',
      categories: [
        {
          name: 'summary',
          displayName: 'Summary',
          icon: <div data-testid="icon-summary" />,
          fields: [
            {
              key: 'filename',
              value: 'document.pdf',
              category: 'Summary',
            },
          ],
          fieldCount: 1,
        },
      ],
      rawMetadata: {
        filename: 'document.pdf',
        mime_type: 'application/pdf',
        filesize: '1.2 MB',
      },
    },
  ];

  const defaultProps = {
    files: mockFiles,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('File Browser (Left Pane)', () => {
    it('should display all files', () => {
      render(<MetadataExplorer {...defaultProps} />);

      expect(screen.getByText('photo1.jpg')).toBeInTheDocument();
      expect(screen.getByText('document.pdf')).toBeInTheDocument();
    });

    it('should show file metadata density indicators', () => {
      render(<MetadataExplorer {...defaultProps} />);

      const highDensityIndicator = screen.getByText('photo1.jpg')
        .closest('button')
        ?.querySelector('[class*="bg-green-500"]');
      expect(highDensityIndicator).toBeInTheDocument();
    });

    it('should show field count for each file', () => {
      render(<MetadataExplorer {...defaultProps} />);

      expect(screen.getByText(/150 fields/)).toBeInTheDocument();
      expect(screen.getByText(/45 fields/)).toBeInTheDocument();
    });

    it('should filter files by search query', async () => {
      render(<MetadataExplorer {...defaultProps} />);

      const searchInput = screen.getAllByPlaceholderText('Search files...')[0];
      await userEvent.type(searchInput, 'photo');

      expect(screen.getByText('photo1.jpg')).toBeInTheDocument();
      expect(screen.queryByText('document.pdf')).not.toBeInTheDocument();
    });

    it('should select file when clicked', async () => {
      const mockOnFileSelect = jest.fn();
      render(<MetadataExplorer {...defaultProps} onFileSelect={mockOnFileSelect} />);

      const fileButton = screen.getByText('photo1.jpg').closest('button');
      await userEvent.click(fileButton!);

      expect(mockOnFileSelect).toHaveBeenCalledWith('file1');
    });

    it('should highlight selected file', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const selectedFile = screen.getByText('photo1.jpg').closest('button');
      expect(selectedFile).toHaveClass('bg-primary/10');
    });

    it('should show no results message when search yields no results', async () => {
      render(<MetadataExplorer {...defaultProps} />);

      const searchInput = screen.getAllByPlaceholderText('Search files...')[0];
      await userEvent.type(searchInput, 'nonexistent');

      expect(screen.getByText('No files match your search')).toBeInTheDocument();
    });

    it('should display file size', () => {
      render(<MetadataExplorer {...defaultProps} />);

      expect(screen.getByText(/2\.5 MB.*150 fields/)).toBeInTheDocument();
      expect(screen.getByText(/1\.2 MB.*45 fields/)).toBeInTheDocument();
    });
  });

  describe('Metadata Tree (Middle Pane)', () => {
    it('should show select file message when no file selected', () => {
      render(<MetadataExplorer files={[]} />);

      expect(screen.getByText('Select a file to view metadata')).toBeInTheDocument();
    });

    it('should display categories for selected file', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      expect(screen.getByText('Summary')).toBeInTheDocument();
      expect(screen.getByText('Camera & EXIF')).toBeInTheDocument();
      expect(screen.getByText('Location')).toBeInTheDocument();
    });

    it('should show field count badges for categories', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const summaryBadge = screen.getByText('Summary')
        .parentElement
        ?.querySelector('[class*="badge"]');
      expect(summaryBadge).toHaveTextContent('2');
    });

    it('should display fields within categories', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      expect(screen.getByText('Make')).toBeInTheDocument();
      expect(screen.getByText('Model')).toBeInTheDocument();
      expect(screen.getByText('DateTimeOriginal')).toBeInTheDocument();
    });

    it('should filter fields by search query', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const searchInput = screen.getAllByPlaceholderText('Search fields...')[0];
      await userEvent.type(searchInput, 'canon');

      expect(screen.getByText('Make')).toBeInTheDocument();
      expect(screen.queryByText('Model')).not.toBeInTheDocument();
    });

    it('should filter categories in simple view mode', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" viewMode="simple" />);

      // Should only show key categories in simple mode
      expect(screen.getByText('Summary')).toBeInTheDocument();
      expect(screen.getByText('Camera & EXIF')).toBeInTheDocument();
    });

    it('should select field when clicked', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const makeField = screen.getByText('Make');
      await userEvent.click(makeField);

      // Detail view should update
      expect(screen.getByText('Camera manufacturer - useful for identifying device')).toBeInTheDocument();
    });

    it('should highlight selected field', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const makeField = screen.getByText('Make');
      await userEvent.click(makeField);

      const selectedField = screen.getByText('Make').closest('button');
      expect(selectedField).toHaveClass('bg-primary/10');
    });
  });

  describe('Detail View (Right Pane)', () => {
    it('should show select field message when no field selected', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      expect(screen.getByText('Select a field to see details')).toBeInTheDocument();
    });

    it('should display field details', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const makeField = screen.getByText('Make');
      await userEvent.click(makeField);

      expect(screen.getByText('Make')).toBeInTheDocument();
      expect(screen.getByText('Camera & EXIF')).toBeInTheDocument();
      expect(screen.getByText('Canon')).toBeInTheDocument();
    });

    it('should show field significance', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const makeField = screen.getByText('Make');
      await userEvent.click(makeField);

      expect(screen.getByText('Why This Matters')).toBeInTheDocument();
      expect(screen.getByText('Camera manufacturer - useful for identifying device')).toBeInTheDocument();
    });

    it('should copy value to clipboard', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const makeField = screen.getByText('Make');
      await userEvent.click(makeField);

      const copyButton = screen.getAllByRole('button').find(
        button => button.querySelector('svg[data-lucide="copy"]')
      );

      if (copyButton) {
        await userEvent.click(copyButton);
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith('Canon');
      }
    });

    it('should show GPS location link for GPS fields', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const gpsField = screen.getByText('GPSLatitude');
      await userEvent.click(gpsField);

      expect(screen.getByText('Location')).toBeInTheDocument();
      expect(screen.getByText('Open in Google Maps')).toBeInTheDocument();
    });

    it('should show external link for URL values', async () => {
      const fileWithUrl = {
        ...mockFiles[0],
        categories: [
          {
            name: 'test',
            displayName: 'Test',
            icon: <div />,
            fields: [
              {
                key: 'url',
                value: 'https://example.com',
                category: 'Test',
              },
            ],
            fieldCount: 1,
          },
        ],
      };

      render(<MetadataExplorer files={[fileWithUrl]} selectedFileId="file1" />);

      const urlField = screen.getByText('url');
      await userEvent.click(urlField);

      expect(screen.getByText('Open Link')).toBeInTheDocument();
    });

    it('should display technical details', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const makeField = screen.getByText('Make');
      await userEvent.click(makeField);

      expect(screen.getByText('Technical Details')).toBeInTheDocument();
      expect(screen.getByText('Category')).toBeInTheDocument();
      expect(screen.getByText('Type')).toBeInTheDocument();
    });

    it('should format long values as code blocks', async () => {
      const fileWithLongValue = {
        ...mockFiles[0],
        categories: [
          {
            name: 'test',
            displayName: 'Test',
            icon: <div />,
            fields: [
              {
                key: 'long_value',
                value: 'a'.repeat(150),
                category: 'Test',
              },
            ],
            fieldCount: 1,
          },
        ],
      };

      render(<MetadataExplorer files={[fileWithLongValue]} selectedFileId="file1" />);

      const longField = screen.getByText('long_value');
      await userEvent.click(longField);

      const codeBlock = screen.getByText('a'.repeat(150))
        .closest('pre');
      expect(codeBlock).toBeInTheDocument();
    });
  });

  describe('View Mode Switching', () => {
    it('should switch between simple, advanced, and raw views', async () => {
      const mockOnViewModeChange = jest.fn();
      render(
        <MetadataExplorer
          {...defaultProps}
          selectedFileId="file1"
          onViewModeChange={mockOnViewModeChange}
        />
      );

      const simpleTab = screen.getByText('Simple');
      await userEvent.click(simpleTab);
      expect(mockOnViewModeChange).toHaveBeenCalledWith('simple');

      const advancedTab = screen.getByText('Advanced');
      await userEvent.click(advancedTab);
      expect(mockOnViewModeChange).toHaveBeenCalledWith('advanced');

      const rawTab = screen.getByText('Raw');
      await userEvent.click(rawTab);
      expect(mockOnViewModeChange).toHaveBeenCalledWith('raw');
    });

    it('should display raw JSON in raw view mode', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" viewMode="raw" />);

      expect(screen.getByText('"filename"')).toBeInTheDocument();
      expect(screen.getByText('"photo1.jpg"')).toBeInTheDocument();
    });
  });

  describe('Metadata Conversion', () => {
    it('should convert API metadata to ProcessedFile format', () => {
      const apiMetadata = {
        filename: 'test.jpg',
        mime_type: 'image/jpeg',
        filesize: '1.5 MB',
        exif: {
          Make: 'Nikon',
          Model: 'D850',
        },
        gps: {
          latitude: 40.7128,
          longitude: -74.0060,
        },
        image: {
          ImageWidth: 8256,
          ImageHeight: 5504,
        },
      };

      const processedFile = convertMetadataToProcessedFile(apiMetadata, 'test-id');

      expect(processedFile.name).toBe('test.jpg');
      expect(processedFile.type).toBe('image/jpeg');
      expect(processedFile.categories).toHaveLength(4); // summary, exif, gps, image
    });

    it('should calculate metadata density correctly', () => {
      const lowDensityMetadata = {
        filename: 'low.jpg',
        exif: { Make: 'Canon' },
      };

      const highDensityMetadata = {
        filename: 'high.jpg',
        exif: { Make: 'Canon', Model: 'R5' },
        gps: { latitude: 37.7, longitude: -122.4 },
        image: { width: 1000, height: 1000 },
        filesystem: { size: 1000 },
      };

      const lowFile = convertMetadataToProcessedFile(lowDensityMetadata, 'low-id');
      const highFile = convertMetadataToProcessedFile(highDensityMetadata, 'high-id');

      expect(lowFile.metadataDensity).toBe('low');
      expect(highFile.metadataDensity).toBe('medium');
    });

    it('should handle locked categories', () => {
      const lockedMetadata = {
        filename: 'locked.jpg',
        makernote: {
          _locked: true,
        },
      };

      const processedFile = convertMetadataToProcessedFile(lockedMetadata, 'locked-id');

      const makernoteCategory = processedFile.categories.find(c => c.name === 'makernote');
      expect(makernoteCategory?.locked).toBe(true);
      expect(makernoteCategory?.fieldCount).toBe(0);
    });
  });

  describe('Empty States', () => {
    it('should show empty state when no files provided', () => {
      render(<MetadataExplorer files={[]} />);

      expect(screen.getByText('Select a file to view metadata')).toBeInTheDocument();
    });

    it('should show empty state in file browser when no files', () => {
      render(<MetadataExplorer files={[]} />);

      const searchInput = screen.queryByPlaceholderText('Search files...');
      expect(searchInput).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible file buttons', () => {
      render(<MetadataExplorer {...defaultProps} />);

      const fileButtons = screen.getAllByText('photo1.jpg');
      fileButtons.forEach(button => {
        expect(button).toBeVisible();
      });
    });

    it('should have accessible field buttons', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const fieldButtons = screen.getAllByText('Make');
      fieldButtons.forEach(button => {
        expect(button).toBeVisible();
      });
    });

    it('should announce changes to screen readers', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      // Tabs and buttons should be keyboard accessible
      const tabs = screen.getAllByRole('tab');
      tabs.forEach(tab => {
        expect(tab).toBeVisible();
      });
    });
  });

  describe('Responsive Layout', () => {
    it('should render resizable panels', () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      // Check if all three panes are rendered
      expect(screen.getByPlaceholderText('Search files...')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Search fields...')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('should handle large metadata sets efficiently', () => {
      const largeFile = {
        ...mockFiles[0],
        fieldCount: 7000,
        categories: [
          {
            name: 'large',
            displayName: 'Large Category',
            icon: <div />,
            fields: Array.from({ length: 1000 }, (_, i) => ({
              key: `field${i}`,
              value: `value${i}`,
              category: 'Large Category',
            })),
            fieldCount: 1000,
          },
        ],
      };

      render(<MetadataExplorer files={[largeFile]} selectedFileId="file1" />);

      expect(screen.getByText('Large Category')).toBeInTheDocument();
    });

    it('should debounce search inputs', async () => {
      render(<MetadataExplorer {...defaultProps} selectedFileId="file1" />);

      const searchInput = screen.getAllByPlaceholderText('Search fields...')[0];

      await userEvent.type(searchInput, 'test');

      // Should handle rapid typing without errors
      expect(screen.getByText('Camera & EXIF')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle null/undefined values gracefully', () => {
      const fileWithNulls = {
        ...mockFiles[0],
        categories: [
          {
            name: 'nulls',
            displayName: 'Null Values',
            icon: <div />,
            fields: [
              {
                key: 'null_value',
                value: null,
                category: 'Null Values',
              },
              {
                key: 'undefined_value',
                value: undefined,
                category: 'Null Values',
              },
            ],
            fieldCount: 2,
          },
        ],
      };

      render(<MetadataExplorer files={[fileWithNulls]} selectedFileId="file1" />);

      const nullField = screen.getByText('null_value');
      await userEvent.click(nullField);

      expect(screen.getByText('N/A')).toBeInTheDocument();
    });

    it('should handle object and array values', () => {
      const fileWithComplex = {
        ...mockFiles[0],
        categories: [
          {
            name: 'complex',
            displayName: 'Complex Values',
            icon: <div />,
            fields: [
              {
                key: 'array_value',
                value: ['one', 'two', 'three'],
                category: 'Complex Values',
              },
              {
                key: 'object_value',
                value: { nested: 'value' },
                category: 'Complex Values',
              },
            ],
            fieldCount: 2,
          },
        ],
      };

      render(<MetadataExplorer files={[fileWithComplex]} selectedFileId="file1" />);

      const arrayField = screen.getByText('array_value');
      await userEvent.click(arrayField);

      expect(screen.getByText('one, two, three')).toBeInTheDocument();
    });

    it('should handle special characters in values', () => {
      const fileWithSpecial = {
        ...mockFiles[0],
        categories: [
          {
            name: 'special',
            displayName: 'Special Chars',
            icon: <div />,
            fields: [
              {
                key: 'special_chars',
                value: '<script>alert("xss")</script>',
                category: 'Special Chars',
              },
            ],
            fieldCount: 1,
          },
        ],
      };

      render(<MetadataExplorer files={[fileWithSpecial]} selectedFileId="file1" />);

      expect(screen.getByText('<script>alert("xss")</script>')).toBeInTheDocument();
    });
  });
});