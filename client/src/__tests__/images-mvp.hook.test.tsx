import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '@/lib/auth';
import Results from '@/pages/images-mvp/results';
import { TooltipProvider } from '@/components/ui/tooltip';

describe('ImagesMvpResults hook-order safety', () => {
  test('renders with basic metadata from sessionStorage without throwing hook-order errors', () => {
    const minimalMetadata = {
      filename: 'test.jpg',
      filesize: '1 MB',
      filetype: 'JPEG',
      mime_type: 'image/jpeg',
      exif: {},
      access: { trial_granted: false, trial_email_present: false },
    };
    sessionStorage.setItem('currentMetadata', JSON.stringify(minimalMetadata));
    sessionStorage.setItem('images_mvp_status', 'success');

    // Ensure crypto.randomUUID exists in this test environment
    if (!globalThis.crypto) {
      // @ts-ignore - test polyfill
      globalThis.crypto = { randomUUID: () => 'test-uuid' } as any;
    } else if (!globalThis.crypto.randomUUID) {
      // @ts-ignore
      globalThis.crypto.randomUUID = () => 'test-uuid';
    }

    // Render inside a Router + AuthProvider because Results uses useNavigate and auth context
    expect(() =>
      render(
        <AuthProvider>
          <TooltipProvider>
            <MemoryRouter>
              <Results />
            </MemoryRouter>
          </TooltipProvider>
        </AuthProvider>
      )
    ).not.toThrow();

    // Basic smoke: key pieces should be present
    expect(screen.getByText('test.jpg')).toBeInTheDocument();
    expect(screen.getByTestId('key-field-mime-type')).toHaveTextContent(
      'image/jpeg'
    );
  });
});
