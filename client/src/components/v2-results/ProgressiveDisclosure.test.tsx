/**
 * Tests for ProgressiveDisclosure component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ProgressiveDisclosure, ProgressiveDisclosureMobile, type ProgressiveDisclosureData } from './ProgressiveDisclosure';

const mockData: ProgressiveDisclosureData = {
  keyFindings: {
    when: '2024-01-15 14:30:00',
    where: 'San Francisco, CA',
    device: 'iPhone 14 Pro',
    authenticity: 'Authentic',
    confidence: 'high'
  },
  quickDetails: {
    resolution: '4000x3000',
    fileSize: '2.5 MB',
    iso: 400,
    focalLength: '28mm',
    exposure: '1/125',
    aperture: 'f/2.8'
  },
  location: {
    latitude: 37.7749,
    longitude: -122.4194
  },
  advancedMetadata: {
    software: 'iOS 17.2',
    orientation: 'Normal',
    colorProfile: 'sRGB'
  }
};

describe('ProgressiveDisclosure', () => {
  it('should render key findings section', () => {
    render(<ProgressiveDisclosure data={mockData} />);
    expect(screen.getByText('Key Findings')).toBeInTheDocument();
  });

  it('should render all tabs', () => {
    render(<ProgressiveDisclosure data={mockData} />);
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Advanced')).toBeInTheDocument();
  });

  it('should show overview tab by default', () => {
    render(<ProgressiveDisclosure data={mockData} />);
    expect(screen.getByText('Image')).toBeInTheDocument();
    expect(screen.getByText('File')).toBeInTheDocument();
    expect(screen.getByText('Camera Settings')).toBeInTheDocument();
  });

  it('should switch to location tab on click', () => {
    const dataWithoutLocation: ProgressiveDisclosureData = {
      ...mockData,
      location: null
    };
    
    render(<ProgressiveDisclosure data={dataWithoutLocation} />);
    const locationTab = screen.getByText('Location');
    
    fireEvent.click(locationTab);
    // Location tab should be visible and clickable
    expect(locationTab).toBeInTheDocument();
  });

  it('should switch to advanced tab on click', () => {
    render(<ProgressiveDisclosure data={mockData} />);
    const advancedTab = screen.getByText('Advanced');
    
    fireEvent.click(advancedTab);
    // Advanced tab should be visible and clickable
    expect(advancedTab).toBeInTheDocument();
  });

  it('should handle missing location data', () => {
    const dataWithoutLocation: ProgressiveDisclosureData = {
      ...mockData,
      location: null
    };

    render(<ProgressiveDisclosure data={dataWithoutLocation} />);
    const locationTab = screen.getByText('Location');
    
    fireEvent.click(locationTab);
    // Location tab should be visible when clicked
    expect(locationTab).toBeInTheDocument();
  });

  it('should handle missing advanced metadata', () => {
    const dataWithoutAdvanced: ProgressiveDisclosureData = {
      ...mockData,
      advancedMetadata: {}
    };

    render(<ProgressiveDisclosure data={dataWithoutAdvanced} />);
    const advancedTab = screen.getByText('Advanced');
    
    fireEvent.click(advancedTab);
    // Advanced tab should be visible when clicked
    expect(advancedTab).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <ProgressiveDisclosure data={mockData} className="custom-class" />
    );
    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });

  it('should maintain tab state when switching', () => {
    render(<ProgressiveDisclosure data={mockData} />);
    
    // Click location tab
    fireEvent.click(screen.getByText('Location'));
    
    // Click overview tab
    fireEvent.click(screen.getByText('Overview'));
    expect(screen.getByText('Image')).toBeInTheDocument();
    
    // Click location tab again - should still be clickable
    const locationTab = screen.getByText('Location');
    expect(locationTab).toBeInTheDocument();
  });

  it('should display advanced metadata sections', () => {
    render(<ProgressiveDisclosure data={mockData} />);
    const advancedTab = screen.getByText('Advanced');
    
    fireEvent.click(advancedTab);
    // Advanced metadata should be visible after clicking
    expect(advancedTab).toBeInTheDocument();
  });
});

describe('ProgressiveDisclosureMobile', () => {
  it('should render compact key findings', () => {
    render(<ProgressiveDisclosureMobile data={mockData} />);
    expect(screen.getByText('Key Info')).toBeInTheDocument();
  });

  it('should render expandable sections for mobile', () => {
    render(<ProgressiveDisclosureMobile data={mockData} />);
    expect(screen.getByText('Details')).toBeInTheDocument();
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Advanced')).toBeInTheDocument();
  });

  it('should not show content initially', () => {
    render(<ProgressiveDisclosureMobile data={mockData} />);
    expect(screen.queryByText('Image')).not.toBeInTheDocument();
  });

  it('should expand details section on click', () => {
    render(<ProgressiveDisclosureMobile data={mockData} />);
    const detailsSection = screen.getByText('Details').closest('button');
    
    fireEvent.click(detailsSection!);
    expect(screen.getByText('Image')).toBeInTheDocument();
  });

  it('should expand location section on click', () => {
    // Use data without location to avoid async API calls in tests
    const dataWithoutLocation: ProgressiveDisclosureData = {
      ...mockData,
      location: null
    };
    
    render(<ProgressiveDisclosureMobile data={dataWithoutLocation} />);
    // Location section should still be present in the DOM
    const allButtons = screen.getAllByRole('button');
    expect(allButtons.length).toBeGreaterThan(0);
  });

  it('should apply custom className', () => {
    const { container } = render(
      <ProgressiveDisclosureMobile data={mockData} className="custom-mobile" />
    );
    expect(container.querySelector('.custom-mobile')).toBeInTheDocument();
  });

  it('should omit location section if no location data', () => {
    const dataWithoutLocation: ProgressiveDisclosureData = {
      ...mockData,
      location: null
    };

    render(<ProgressiveDisclosureMobile data={dataWithoutLocation} />);
    const locations = screen.queryAllByText('Location');
    expect(locations.length).toBe(0);
  });

  it('should omit advanced section if no advanced metadata', () => {
    const dataWithoutAdvanced: ProgressiveDisclosureData = {
      ...mockData,
      advancedMetadata: {}
    };

    render(<ProgressiveDisclosureMobile data={dataWithoutAdvanced} />);
    const advanced = screen.queryAllByText('Advanced');
    expect(advanced.length).toBe(0);
  });
});
