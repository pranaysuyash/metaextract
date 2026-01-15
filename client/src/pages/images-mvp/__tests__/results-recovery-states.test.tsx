import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { render, screen } from '@testing-library/react';

import ImagesMvpResults from '@/pages/images-mvp/results';
import { AuthProvider } from '@/lib/auth';
import { TooltipProvider } from '@/components/ui/tooltip';

function renderResults() {
  if (!globalThis.crypto) {
    // @ts-ignore - test polyfill
    globalThis.crypto = { randomUUID: () => 'test-uuid' } as any;
  } else if (!globalThis.crypto.randomUUID) {
    // @ts-ignore
    globalThis.crypto.randomUUID = () => 'test-uuid';
  }

  return render(
    <AuthProvider>
      <TooltipProvider>
        <MemoryRouter initialEntries={['/images_mvp/results']}>
          <ImagesMvpResults />
        </MemoryRouter>
      </TooltipProvider>
    </AuthProvider>
  );
}

describe('ImagesMvpResults recovery states', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  test('shows processing state when last run is processing and metadata is missing', () => {
    sessionStorage.setItem('images_mvp_status', 'processing');
    renderResults();
    expect(screen.getByText('Still processing')).toBeInTheDocument();
  });

  test('shows failure state when last run failed and metadata is missing', () => {
    sessionStorage.setItem('images_mvp_status', 'fail');
    sessionStorage.setItem(
      'images_mvp_error',
      JSON.stringify({ status: 500, message: 'Upload failed' })
    );
    renderResults();
    expect(screen.getByText('Analysis failed')).toBeInTheDocument();
    expect(screen.getByText(/Upload failed/)).toBeInTheDocument();
  });
});
