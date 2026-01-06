import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ProgressTracker } from '@/components/images-mvp/progress-tracker';
import { ExtractionProgressTracker } from '@/components/extraction-progress-tracker';

// Minimal WebSocket mock to prevent actual socket connections during tests
class MockWebSocket {
  url: string;
  onopen: (() => void) | null = null;
  onmessage: ((e: any) => void) | null = null;
  onerror: ((e: any) => void) | null = null;
  onclose: (() => void) | null = null;
  constructor(url: string) {
    this.url = url;
    // Simulate async open
    setTimeout(() => this.onopen && this.onopen(), 0);
  }
  close() {
    this.onclose && this.onclose();
  }
  send() {}
}

// @ts-ignore - set global for jest jsdom
global.WebSocket = MockWebSocket as any;

test('only images-mvp ProgressTracker renders and generic tracker is disabled', () => {
  render(
    <>
      <ProgressTracker sessionId="session-test" />
      <ExtractionProgressTracker
        extractionId="ex-1"
        onComplete={() => {}}
        onError={() => {}}
      />
    </>
  );

  // The images-mvp tracker shows 'Extracting Metadata...'
  expect(screen.getAllByText(/Extracting Metadata/).length).toBe(1);

  // There should be exactly one status region (images-mvp tracker)
  expect(screen.getAllByRole('status').length).toBe(1);

  // Progress bar fill should exist
  expect(screen.getByTestId('progress-bar-fill')).toBeInTheDocument();

  // Rendering the generic tracker alone returns nothing (clean previous DOM first)
  // cleanup ensures we are inspecting a fresh render
  const { cleanup } = require('@testing-library/react');
  cleanup();
  render(
    <ExtractionProgressTracker
      extractionId="ex-2"
      onComplete={() => {}}
      onError={() => {}}
    />
  );
  expect(screen.queryByRole('status')).toBeNull();
});
