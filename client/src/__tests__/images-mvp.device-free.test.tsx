import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '@/lib/auth';
import Results from '@/pages/images-mvp/results';

jest.mock('@/lib/images-mvp-analytics', () => ({ trackImagesMvpEvent: jest.fn() }));

describe('Images MVP Results - device_free banner and unlock behavior', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it('shows device_free banner and does not show locked fields preview', async () => {
    const metadata = {
      filename: 'gps-map-photo.jpg',
      filesize: '9.12 MB',
      mime_type: 'image/jpeg',
      access: { mode: 'device_free', free_used: 1 },
      exif: { Model: 'X' },
      calculated: { aspect_ratio: '3:4' },
      metadata_comparison: { summary: {} },
      file_integrity: { md5: 'a' },
      burned_metadata: { has_burned_metadata: true, extracted_text: null, confidence: 0.9 },
      gps: null,
    };
    sessionStorage.setItem('currentMetadata', JSON.stringify(metadata));
    sessionStorage.setItem('images_mvp_status', 'success');

    render(
      <MemoryRouter>
        <AuthProvider>
          <Results />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(await screen.findByText(/Free check used/)).toBeInTheDocument();
    // Limited report banner should not be present
    expect(screen.queryByText(/Limited report/)).toBeNull();
  });
});
