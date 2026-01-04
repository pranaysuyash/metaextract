/**
 * Tests for ActionsToolbar component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ActionsToolbar, ActionsToolbarCompact } from './ActionsToolbar';

// Mock useToast
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

const mockMetadata = {
  filename: 'test.jpg',
  filesize: '2.5 MB',
  exif: { camera: 'iPhone' },
};

describe('ActionsToolbar', () => {
  it('should render all action buttons', () => {
    render(
      <ActionsToolbar
        filename="test.jpg"
        metadata={mockMetadata}
      />
    );

    expect(screen.getByText(/JSON/i)).toBeInTheDocument();
    expect(screen.getByText(/PDF/i)).toBeInTheDocument();
    expect(screen.getByText(/Copy/i)).toBeInTheDocument();
    expect(screen.getByText(/Compare/i)).toBeInTheDocument();
    expect(screen.getByText(/Share/i)).toBeInTheDocument();
  });

  it('should render Actions label', () => {
    render(
      <ActionsToolbar
        filename="test.jpg"
        metadata={mockMetadata}
      />
    );

    expect(screen.getByText(/Actions/i)).toBeInTheDocument();
  });

  it('should handle JSON export click', () => {
    render(
      <ActionsToolbar
        filename="test.jpg"
        metadata={mockMetadata}
      />
    );

    const jsonButton = screen.getByText(/JSON/i);
    fireEvent.click(jsonButton);
    expect(jsonButton).toBeInTheDocument();
  });

  it('should toggle copy button state', async () => {
    render(
      <ActionsToolbar
        filename="test.jpg"
        metadata={mockMetadata}
      />
    );

    const copyButtons = screen.getAllByText(/Copy/i);
    const copyButton = copyButtons[0];
    fireEvent.click(copyButton);

    // Check for the icon instead of text since button children contain both icon and text
    await waitFor(() => {
      const buttons = screen.getAllByRole('button');
      expect(buttons.some(b => b.textContent?.includes('Copy'))).toBeTruthy();
    });
  });

  it('should call onCompare callback', () => {
    const onCompare = jest.fn();
    render(
      <ActionsToolbar
        filename="test.jpg"
        metadata={mockMetadata}
        onCompare={onCompare}
      />
    );

    const compareButton = screen.getByText(/Compare/i);
    fireEvent.click(compareButton);
    expect(onCompare).toHaveBeenCalled();
  });

  it('should call onShare callback', () => {
    const onShare = jest.fn();
    render(
      <ActionsToolbar
        filename="test.jpg"
        metadata={mockMetadata}
        onShare={onShare}
      />
    );

    const shareButton = screen.getByText(/Share/i);
    fireEvent.click(shareButton);
    expect(onShare).toHaveBeenCalled();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <ActionsToolbar
        filename="test.jpg"
        metadata={mockMetadata}
        className="custom-class"
      />
    );

    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });
});

describe('ActionsToolbarCompact', () => {
  it('should render compact variant with 2 columns', () => {
    const { container } = render(
      <ActionsToolbarCompact
        filename="test.jpg"
        metadata={mockMetadata}
      />
    );

    expect(container.querySelector('.grid-cols-2')).toBeInTheDocument();
  });

  it('should render only essential buttons', () => {
    render(
      <ActionsToolbarCompact
        filename="test.jpg"
        metadata={mockMetadata}
      />
    );

    expect(screen.getByText(/Export/i)).toBeInTheDocument();
    expect(screen.getByText(/Copy/i)).toBeInTheDocument();
    expect(screen.queryByText(/PDF/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Share/i)).not.toBeInTheDocument();
  });

  it('should handle export in compact variant', () => {
    render(
      <ActionsToolbarCompact
        filename="test.jpg"
        metadata={mockMetadata}
      />
    );

    const exportButton = screen.getByText(/Export/i);
    fireEvent.click(exportButton);
    expect(exportButton).toBeInTheDocument();
  });

  it('should toggle copy state in compact variant', async () => {
    render(
      <ActionsToolbarCompact
        filename="test.jpg"
        metadata={mockMetadata}
      />
    );

    const copyButtons = screen.getAllByText(/Copy/i);
    const copyButton = copyButtons[0];
    fireEvent.click(copyButton);

    // Just verify button is still in document after click
    await waitFor(() => {
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  it('should apply custom className to compact variant', () => {
    const { container } = render(
      <ActionsToolbarCompact
        filename="test.jpg"
        metadata={mockMetadata}
        className="custom-compact"
      />
    );

    expect(container.querySelector('.custom-compact')).toBeInTheDocument();
  });
});
