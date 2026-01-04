/**
 * Tests for QuickDetails component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { QuickDetails, type QuickDetailsData } from './QuickDetails';

describe('QuickDetails', () => {
  it('should render image properties section', () => {
    const data: QuickDetailsData = {
      resolution: '4000x3000',
      dimensions: '4000 x 3000 pixels',
      colorSpace: 'RGB'
    };

    render(<QuickDetails data={data} />);
    
    expect(screen.getByText('Image')).toBeInTheDocument();
    expect(screen.getByText('4000x3000')).toBeInTheDocument();
    expect(screen.getByText('4000 x 3000 pixels')).toBeInTheDocument();
    expect(screen.getByText('RGB')).toBeInTheDocument();
  });

  it('should render file properties section', () => {
    const data: QuickDetailsData = {
      fileSize: '2.5 MB'
    };

    render(<QuickDetails data={data} />);
    
    expect(screen.getByText('File')).toBeInTheDocument();
    expect(screen.getByText('2.5 MB')).toBeInTheDocument();
  });

  it('should render camera settings section', () => {
    const data: QuickDetailsData = {
      iso: 400,
      focalLength: '50mm',
      exposure: '1/125',
      aperture: 'f/2.8'
    };

    render(<QuickDetails data={data} />);
    
    expect(screen.getByText('Camera Settings')).toBeInTheDocument();
    expect(screen.getByText('400')).toBeInTheDocument();
    expect(screen.getByText('50mm')).toBeInTheDocument();
    expect(screen.getByText('1/125')).toBeInTheDocument();
    expect(screen.getByText('f/2.8')).toBeInTheDocument();
  });

  it('should display partial camera settings', () => {
    const data: QuickDetailsData = {
      iso: 800,
      focalLength: '85mm'
    };

    render(<QuickDetails data={data} />);
    
    expect(screen.getByText('Camera Settings')).toBeInTheDocument();
    expect(screen.getByText('800')).toBeInTheDocument();
    expect(screen.getByText('85mm')).toBeInTheDocument();
  });

  it('should show message when no data provided', () => {
    render(<QuickDetails data={{}} />);
    
    expect(screen.getByText('No quick details available')).toBeInTheDocument();
  });

  it('should ignore undefined properties', () => {
    const data: QuickDetailsData = {
      resolution: '2000x1500',
      iso: undefined,
      aperture: undefined
    };

    render(<QuickDetails data={data} />);
    
    expect(screen.getByText('Image')).toBeInTheDocument();
    expect(screen.queryByText('Camera Settings')).not.toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const data: QuickDetailsData = {
      fileSize: '1.5 MB'
    };

    const { container } = render(
      <QuickDetails data={data} className="custom-class" />
    );
    
    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });

  it('should display all sections together', () => {
    const data: QuickDetailsData = {
      resolution: '3840x2160',
      dimensions: '3840 x 2160 pixels',
      colorSpace: 'sRGB',
      fileSize: '5.2 MB',
      iso: 200,
      focalLength: '35mm',
      exposure: '1/500',
      aperture: 'f/4'
    };

    render(<QuickDetails data={data} />);
    
    expect(screen.getByText('Image')).toBeInTheDocument();
    expect(screen.getByText('File')).toBeInTheDocument();
    expect(screen.getByText('Camera Settings')).toBeInTheDocument();
  });

  it('should handle empty string values', () => {
    const data: QuickDetailsData = {
      fileSize: ''
    };

    render(<QuickDetails data={data} />);
    
    expect(screen.getByText('No quick details available')).toBeInTheDocument();
  });
});
