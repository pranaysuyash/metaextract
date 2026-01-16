/**
 * Unit tests for SimpleUploadZone extracted hooks
 * Comprehensive test coverage for each hook
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Hooks to test
import { useMobileDetection } from '@/hooks/useMobileDetection';
import { useDragAndDrop } from '@/hooks/useDragAndDrop';
import { useOcrDetection } from '@/hooks/useOcrDetection';

// Utilities to test
import { 
  getFileExtension, 
  probeImageDimensions, 
  isValidImageType, 
  formatFileSize,
  calculateMegapixels,
  exceedsMegapixelLimit 
} from '@/utils/fileProcessing';

// Mock dependencies
vi.mock('@/lib/images-mvp-analytics', () => ({
  trackImagesMvpEvent: vi.fn(),
  getFileSizeBucket: vi.fn(() => '1-5MB'),
}));

describe('useMobileDetection', () => {
  beforeEach(() => {
    // Reset window size
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should detect desktop by default', () => {
    const { result } = renderHook(() => useMobileDetection());
    expect(result.current.isMobile).toBe(false);
  });

  it('should detect mobile when window width is below breakpoint', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 500,
    });

    const { result } = renderHook(() => useMobileDetection());
    expect(result.current.isMobile).toBe(true);
  });

  it('should update when window is resized', () => {
    const { result } = renderHook(() => useMobileDetection());
    
    expect(result.current.isMobile).toBe(false);

    // Simulate window resize
    act(() => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 500,
      });
      window.dispatchEvent(new Event('resize'));
    });

    expect(result.current.isMobile).toBe(true);
  });

  it('should use custom breakpoint', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 700,
    });

    const { result } = renderHook(() => useMobileDetection(800));
    expect(result.current.isMobile).toBe(true);
  });

  it('should cleanup event listener on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');
    
    const { unmount } = renderHook(() => useMobileDetection());
    
    unmount();
    
    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
  });
});

describe('useDragAndDrop', () => {
  const mockOnFileDrop = vi.fn();
  const mockOnDragStart = vi.fn();
  const mockOnDragEnd = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with inactive state', () => {
    const { result } = renderHook(() => 
      useDragAndDrop({ 
        onFileDrop: mockOnFileDrop,
        onDragStart: mockOnDragStart,
        onDragEnd: mockOnDragEnd
      })
    );

    expect(result.current.isDragActive).toBe(false);
  });

  it('should set drag active on drag over', () => {
    const { result } = renderHook(() => 
      useDragAndDrop({ onFileDrop: mockOnFileDrop })
    );

    const mockEvent = {
      preventDefault: vi.fn(),
      stopPropagation: vi.fn(),
    } as unknown as React.DragEvent;

    act(() => {
      result.current.dragHandlers.onDragOver(mockEvent);
    });

    expect(result.current.isDragActive).toBe(true);
    expect(mockEvent.preventDefault).toHaveBeenCalled();
    expect(mockEvent.stopPropagation).toHaveBeenCalled();
  });

  it('should set drag inactive on drag leave', () => {
    const { result } = renderHook(() => 
      useDragAndDrop({ 
        onFileDrop: mockOnFileDrop,
        onDragStart: mockOnDragStart,
        onDragEnd: mockOnDragEnd
      })
    );

    // First activate drag
    const mockOverEvent = {
      preventDefault: vi.fn(),
      stopPropagation: vi.fn(),
    } as unknown as React.DragEvent;

    act(() => {
      result.current.dragHandlers.onDragOver(mockOverEvent);
    });

    expect(result.current.isDragActive).toBe(true);

    // Then deactivate
    const mockLeaveEvent = {
      preventDefault: vi.fn(),
      stopPropagation: vi.fn(),
    } as unknown as React.DragEvent;

    act(() => {
      result.current.dragHandlers.onDragLeave(mockLeaveEvent);
    });

    expect(result.current.isDragActive).toBe(false);
    expect(mockOnDragEnd).toHaveBeenCalled();
  });

  it('should handle file drop', () => {
    const { result } = renderHook(() => 
      useDragAndDrop({ onFileDrop: mockOnFileDrop })
    );

    const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const mockEvent = {
      preventDefault: vi.fn(),
      stopPropagation: vi.fn(),
      dataTransfer: {
        files: [mockFile],
      },
    } as unknown as React.DragEvent;

    act(() => {
      result.current.dragHandlers.onDrop(mockEvent);
    });

    expect(mockOnFileDrop).toHaveBeenCalledWith(mockFile);
    expect(result.current.isDragActive).toBe(false);
  });

  it('should handle keyboard events', () => {
    const { result } = renderHook(() => 
      useDragAndDrop({ onFileDrop: mockOnFileDrop })
    );

    const mockEvent = {
      key: 'Enter',
      preventDefault: vi.fn(),
      stopPropagation: vi.fn(),
    } as unknown as React.KeyboardEvent;

    act(() => {
      result.current.keyboardHandlers.onKeyDown(mockEvent);
    });

    expect(mockEvent.preventDefault).toHaveBeenCalled();
    expect(mockEvent.stopPropagation).toHaveBeenCalled();
  });

  it('should handle space key', () => {
    const { result } = renderHook(() => 
      useDragAndDrop({ onFileDrop: mockOnFileDrop })
    );

    const mockEvent = {
      key: ' ',
      preventDefault: vi.fn(),
      stopPropagation: vi.fn(),
    } as unknown as React.KeyboardEvent;

    act(() => {
      result.current.keyboardHandlers.onKeyDown(mockEvent);
    });

    expect(mockEvent.preventDefault).toHaveBeenCalled();
  });
});

describe('useOcrDetection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useOcrDetection());

    expect(result.current.ocrAutoApplied).toBe(false);
    expect(result.current.ocrUserOverride).toBe(false);
  });

  it('should detect map/GPS patterns in filenames', () => {
    const { result } = renderHook(() => useOcrDetection());

    const testCases = [
      { filename: 'gps_location.jpg', expected: true },
      { filename: 'map_screenshot.png', expected: true },
      { filename: 'my_location.png', expected: true },
      { filename: 'coordinates_123.jpg', expected: true },
      { filename: 'geotag_photo.jpg', expected: true },
      { filename: 'regular_photo.jpg', expected: false },
      { filename: 'IMG_1234.jpg', expected: false },
      { filename: 'screenshot.png', expected: false },
    ];

    testCases.forEach(({ filename, expected }) => {
      expect(result.current.shouldAutoApplyOcr(filename)).toBe(expected);
    });
  });

  it('should handle user override', () => {
    const { result } = renderHook(() => useOcrDetection());

    act(() => {
      result.current.applyOcrOverride();
    });

    expect(result.current.ocrUserOverride).toBe(true);
    expect(result.current.ocrAutoApplied).toBe(false);
  });

  it('should clear user override', () => {
    const { result } = renderHook(() => useOcrDetection());

    // Set override first
    act(() => {
      result.current.applyOcrOverride();
    });

    expect(result.current.ocrUserOverride).toBe(true);

    // Clear override
    act(() => {
      result.current.clearOcrOverride();
    });

    expect(result.current.ocrUserOverride).toBe(false);
    expect(result.current.ocrAutoApplied).toBe(false);
  });

  it('should set auto-applied state', () => {
    const { result } = renderHook(() => useOcrDetection());

    act(() => {
      result.current.setAutoApplied();
    });

    expect(result.current.ocrAutoApplied).toBe(true);
    expect(result.current.ocrUserOverride).toBe(false);
  });

  it('should reset all OCR state', () => {
    const { result } = renderHook(() => useOcrDetection());

    // Set various states
    act(() => {
      result.current.applyOcrOverride();
      result.current.setAutoApplied();
    });

    // Reset
    act(() => {
      result.current.resetOcrState();
    });

    expect(result.current.ocrAutoApplied).toBe(false);
    expect(result.current.ocrUserOverride).toBe(false);
  });

  it('should be case insensitive', () => {
    const { result } = renderHook(() => useOcrDetection());

    expect(result.current.shouldAutoApplyOcr('GPS_LOCATION.jpg')).toBe(true);
    expect(result.current.shouldAutoApplyOcr('Map_Screenshot.PNG')).toBe(true);
    expect(result.current.shouldAutoApplyOcr('MY_COORDINATES.JPG')).toBe(true);
  });
});

describe('File Processing Utilities', () => {
  describe('getFileExtension', () => {
    it('should extract file extension', () => {
      expect(getFileExtension('photo.jpg')).toBe('.jpg');
      expect(getFileExtension('image.png')).toBe('.png');
      expect(getFileExtension('document.pdf')).toBe('.pdf');
    });

    it('should return null for files without extension', () => {
      expect(getFileExtension('README')).toBe(null);
      expect(getFileExtension('')).toBe(null);
    });

    it('should return null for hidden files without extension', () => {
      expect(getFileExtension('.gitignore')).toBe(null);
    });

    it('should convert to lowercase', () => {
      expect(getFileExtension('photo.JPG')).toBe('.jpg');
      expect(getFileExtension('image.PNG')).toBe('.png');
    });

    it('should handle multiple dots', () => {
      expect(getFileExtension('photo.backup.jpg')).toBe('.jpg');
      expect(getFileExtension('archive.tar.gz')).toBe('.gz');
    });

    it('should handle invalid input', () => {
      expect(getFileExtension(null as any)).toBe(null);
      expect(getFileExtension(undefined as any)).toBe(null);
      expect(getFileExtension(123 as any)).toBe(null);
    });
  });

  describe('isValidImageType', () => {
    it('should validate supported image types', () => {
      const validFiles = [
        new File([''], 'test.jpg', { type: 'image/jpeg' }),
        new File([''], 'test.png', { type: 'image/png' }),
        new File([''], 'test.webp', { type: 'image/webp' }),
        new File([''], 'test.heic', { type: 'image/heic' }),
      ];

      validFiles.forEach(file => {
        expect(isValidImageType(file)).toBe(true);
      });
    });

    it('should reject non-image files', () => {
      const invalidFiles = [
        new File([''], 'test.pdf', { type: 'application/pdf' }),
        new File([''], 'test.txt', { type: 'text/plain' }),
        new File([''], 'test.mp4', { type: 'video/mp4' }),
      ];

      invalidFiles.forEach(file => {
        expect(isValidImageType(file)).toBe(false);
      });
    });
  });

  describe('formatFileSize', () => {
    it('should format file sizes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1024 * 1024)).toBe('1 MB');
      expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB');
    });

    it('should handle decimal values', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB');
      expect(formatFileSize(2621440)).toBe('2.5 MB');
    });
  });

  describe('calculateMegapixels', () => {
    it('should calculate megapixels correctly', () => {
      expect(calculateMegapixels(1920, 1080)).toBeCloseTo(2.07, 2);
      expect(calculateMegapixels(4000, 3000)).toBe(12);
      expect(calculateMegapixels(1000, 1000)).toBe(1);
    });
  });

  describe('exceedsMegapixelLimit', () => {
    it('should check megapixel limits correctly', () => {
      expect(exceedsMegapixelLimit(1920, 1080, 2)).toBe(true);
      expect(exceedsMegapixelLimit(1000, 1000, 2)).toBe(false);
      expect(exceedsMegapixelLimit(4000, 3000, 10)).toBe(true);
    });
  });
});

describe('probeImageDimensions', () => {
  // Mock URL and Image for testing
  const mockUrlCreate = vi.fn();
  const mockUrlRevoke = vi.fn();
  let mockImage: any;

  beforeEach(() => {
    // Setup URL mocks
    global.URL.createObjectURL = mockUrlCreate;
    global.URL.revokeObjectURL = mockUrlRevoke;
    mockUrlCreate.mockReturnValue('mock-object-url');

    // Setup Image mock
    mockImage = {
      src: '',
      onload: null,
      onerror: null,
    };
    
    global.Image = vi.fn(() => mockImage) as any;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should probe image dimensions successfully', async () => {
    const mockFile = new File(['image data'], 'test.jpg', { type: 'image/jpeg' });
    
    // Simulate successful image load
    setTimeout(() => {
      mockImage.width = 1920;
      mockImage.height = 1080;
      mockImage.onload();
    }, 0);

    const result = await probeImageDimensions(mockFile);

    expect(result).toEqual({ width: 1920, height: 1080 });
    expect(mockUrlCreate).toHaveBeenCalledWith(mockFile);
    expect(mockUrlRevoke).toHaveBeenCalledWith('mock-object-url');
  });

  it('should handle image load errors', async () => {
    const mockFile = new File(['image data'], 'test.jpg', { type: 'image/jpeg' });
    
    // Simulate image load error
    setTimeout(() => {
      mockImage.onerror();
    }, 0);

    const result = await probeImageDimensions(mockFile);

    expect(result).toBeNull();
    expect(mockUrlRevoke).toHaveBeenCalledWith('mock-object-url');
  });

  it('should return null for non-image files', async () => {
    const mockFile = new File(['text'], 'test.txt', { type: 'text/plain' });
    
    const result = await probeImageDimensions(mockFile);

    expect(result).toBeNull();
    expect(mockUrlCreate).not.toHaveBeenCalled();
  });

  it('should handle exceptions gracefully', async () => {
    const mockFile = new File(['image data'], 'test.jpg', { type: 'image/jpeg' });
    
    // Make URL.createObjectURL throw
    mockUrlCreate.mockImplementation(() => {
      throw new Error('URL creation failed');
    });

    const result = await probeImageDimensions(mockFile);

    expect(result).toBeNull();
  });
});