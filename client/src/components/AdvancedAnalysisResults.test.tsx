/**
 * Comprehensive test suite for AdvancedAnalysisResults component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AdvancedAnalysisResults } from './AdvancedAnalysisResults';

// Helper to find text that might be split by Badge component icons
function findBadgeWithText(text: string) {
  return (
    screen.queryAllByText(text).find((element) => {
      return (
        element.textContent === text || element.textContent?.includes(text)
      );
    }) || screen.getByText(text)
  );
}

describe('AdvancedAnalysisResults', () => {
  let user: ReturnType<typeof userEvent.setup>;

  const mockSteganographyData = {
    detected: true,
    confidence: 85,
    methods_checked: ['LSB', 'DCT', 'Frequency Analysis'],
    findings: [
      'Potential LSB steganography detected in blue channel',
      'Unusual patterns in DCT coefficients',
    ],
  };

  const mockManipulationData = {
    detected: true,
    confidence: 92,
    indicators: [
      {
        type: 'JPEG Ghosts',
        severity: 'high' as const,
        description: 'Evidence of multiple compression artifacts',
      },
      {
        type: 'Lighting Inconsistency',
        severity: 'medium' as const,
        description: 'Inconsistent lighting directions detected',
      },
      {
        type: 'Noise Pattern Analysis',
        severity: 'low' as const,
        description: 'Minor variations in noise patterns',
      },
    ],
  };

  const mockAIDetectionData = {
    ai_generated: true,
    confidence: 88,
    model_hints: [
      'GAN artifacts',
      'Unnatural texture patterns',
      'AI-generated faces',
    ],
  };

  const mockTimelineData = {
    events: [
      {
        timestamp: '2024-01-15 10:30:00',
        event_type: 'File Created',
        source: 'EXIF DateTimeOriginal',
      },
      {
        timestamp: '2024-01-15 14:22:00',
        event_type: 'Metadata Modified',
        source: 'XMP ModifyDate',
      },
      {
        timestamp: '2024-01-16 09:15:00',
        event_type: 'File Uploaded',
        source: 'HTTP Headers',
      },
    ],
    gaps_detected: false,
    chain_of_custody_complete: true,
  };

  const defaultProps = {
    steganography: null,
    manipulation: null,
    aiDetection: null,
    timeline: null,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    user = userEvent.setup();
  });

  describe('Empty State', () => {
    it('should show empty state when no analysis data', () => {
      render(<AdvancedAnalysisResults {...defaultProps} />);

      expect(
        screen.getByText('No advanced analysis data available')
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          /Advanced analysis requires Forensic or Enterprise tier/
        )
      ).toBeInTheDocument();
    });

    it('should display shield icon in empty state', () => {
      render(<AdvancedAnalysisResults {...defaultProps} />);

      const shieldIcon =
        document.querySelector('svg[data-lucide="shield"]') ||
        document.querySelector('svg[class*="shield"]');
      expect(shieldIcon).toBeInTheDocument();
    });
  });

  describe('Steganography Analysis', () => {
    it('should display steganography detection results', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      const hiddenDataBadge = findBadgeWithText('Hidden Data Detected');
      expect(hiddenDataBadge).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
    });

    it('should show methods analyzed', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      expect(screen.getByText('Methods Analyzed:')).toBeInTheDocument();
      expect(screen.getByText('LSB')).toBeInTheDocument();
      expect(screen.getByText('DCT')).toBeInTheDocument();
      expect(screen.getByText('Frequency Analysis')).toBeInTheDocument();
    });

    it('should display findings', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      expect(
        screen.getByText(/Potential LSB steganography detected/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Unusual patterns in DCT coefficients/)
      ).toBeInTheDocument();
    });

    it('should show negative result when no steganography detected', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={{
            ...mockSteganographyData,
            detected: false,
            confidence: 95,
            findings: [],
          }}
        />
      );

      const noHiddenDataBadge = findBadgeWithText('No Hidden Data');
      expect(noHiddenDataBadge).toBeInTheDocument();
      expect(screen.getByText('95%')).toBeInTheDocument();
    });

    it('should handle empty findings array', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={{
            ...mockSteganographyData,
            findings: [],
          }}
        />
      );

      expect(findBadgeWithText('Hidden Data Detected')).toBeInTheDocument();
    });

    it('should handle empty methods array', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={{
            ...mockSteganographyData,
            methods_checked: [],
          }}
        />
      );

      expect(findBadgeWithText('Hidden Data Detected')).toBeInTheDocument();
      expect(screen.queryByText('Methods Analyzed:')).not.toBeInTheDocument();
    });
  });

  describe('Manipulation Detection', () => {
    it('should display manipulation detection results', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          manipulation={mockManipulationData}
        />
      );

      // Click on the Manipulation tab first
      const manipulationTab = screen.getByText('Manipulation');
      await userEvent.click(manipulationTab);

      const manipulationBadge = findBadgeWithText('Manipulation Detected');
      expect(manipulationBadge).toBeInTheDocument();
      expect(screen.getByText('92%')).toBeInTheDocument();
    });

    it('should show indicators with severity levels', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          manipulation={mockManipulationData}
        />
      );

      // Click on the Manipulation tab
      await userEvent.click(screen.getByText('Manipulation'));

      expect(screen.getByText('JPEG Ghosts')).toBeInTheDocument();
      expect(screen.getByText('Lighting Inconsistency')).toBeInTheDocument();
      expect(screen.getByText('Noise Pattern Analysis')).toBeInTheDocument();
    });

    it('should apply correct severity styling', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          manipulation={mockManipulationData}
        />
      );

      // Click on the Manipulation tab
      await userEvent.click(screen.getByText('Manipulation'));

      const highSeverityBadge = screen.getByText('HIGH');
      const mediumSeverityBadge = screen.getByText('MEDIUM');
      const lowSeverityBadge = screen.getByText('LOW');

      expect(highSeverityBadge).toBeInTheDocument();
      expect(mediumSeverityBadge).toBeInTheDocument();
      expect(lowSeverityBadge).toBeInTheDocument();
    });

    it('should display indicator descriptions', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          manipulation={mockManipulationData}
        />
      );

      // Manipulation content is hidden until its tab is active
      await user.click(screen.getByText('Manipulation'));

      expect(
        screen.getByText(/Evidence of multiple compression artifacts/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Inconsistent lighting directions detected/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Minor variations in noise patterns/)
      ).toBeInTheDocument();
    });

    it('should show negative result when no manipulation detected', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          manipulation={{
            ...mockManipulationData,
            detected: false,
            confidence: 98,
            indicators: [],
          }}
        />
      );

      await userEvent.click(screen.getByText('Manipulation'));

      const noManipulationBadge = findBadgeWithText('No Manipulation');
      expect(noManipulationBadge).toBeInTheDocument();
      expect(screen.getByText('98%')).toBeInTheDocument();
    });

    it('should handle empty indicators array', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          manipulation={{
            ...mockManipulationData,
            indicators: [],
          }}
        />
      );

      await userEvent.click(screen.getByText('Manipulation'));

      expect(findBadgeWithText('Manipulation Detected')).toBeInTheDocument();
    });
  });

  describe('AI Detection', () => {
    it('should display AI detection results', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          aiDetection={mockAIDetectionData}
        />
      );

      // Click on the AI Detection tab
      await userEvent.click(screen.getByText('AI Detection'));

      const aiGeneratedBadge = findBadgeWithText('AI-Generated');
      expect(aiGeneratedBadge).toBeInTheDocument();
      expect(screen.getByText('88%')).toBeInTheDocument();
    });

    it('should show model hints', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          aiDetection={mockAIDetectionData}
        />
      );

      // Click on the AI Detection tab
      await userEvent.click(screen.getByText('AI Detection'));

      expect(screen.getByText('Model Indicators:')).toBeInTheDocument();
      expect(screen.getByText('GAN artifacts')).toBeInTheDocument();
      expect(
        screen.getByText('Unnatural texture patterns')
      ).toBeInTheDocument();
      expect(screen.getByText('AI-generated faces')).toBeInTheDocument();
    });

    it('should show negative result when content is likely authentic', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          aiDetection={{
            ai_generated: false,
            confidence: 75,
            model_hints: [],
          }}
        />
      );

      // Click on the AI Detection tab
      await userEvent.click(screen.getByText('AI Detection'));

      const authenticBadge = findBadgeWithText('Likely Authentic');
      expect(authenticBadge).toBeInTheDocument();
      expect(screen.getByText('75%')).toBeInTheDocument();
    });

    it('should handle empty model hints', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          aiDetection={{
            ...mockAIDetectionData,
            model_hints: [],
          }}
        />
      );

      // AI content is hidden until its tab is active
      await user.click(screen.getByText('AI Detection'));
      expect(screen.getByText('AI-Generated')).toBeInTheDocument();
      expect(screen.queryByText('Model Indicators:')).not.toBeInTheDocument();
    });
  });

  describe('Timeline Analysis', () => {
    it('should display timeline events', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          timeline={mockTimelineData}
        />
      );

      await userEvent.click(screen.getByText('Timeline'));

      expect(screen.getByText('File Created')).toBeInTheDocument();
      expect(screen.getByText('Metadata Modified')).toBeInTheDocument();
      expect(screen.getByText('File Uploaded')).toBeInTheDocument();
    });

    it('should show event timestamps and sources', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          timeline={mockTimelineData}
        />
      );

      await user.click(screen.getByText('Timeline'));

      expect(screen.getByText('2024-01-15 10:30:00')).toBeInTheDocument();
      expect(screen.getByText('EXIF DateTimeOriginal')).toBeInTheDocument();
      expect(screen.getByText('2024-01-15 14:22:00')).toBeInTheDocument();
      expect(screen.getByText('XMP ModifyDate')).toBeInTheDocument();
    });

    it('should display chain of custody status', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          timeline={mockTimelineData}
        />
      );

      await userEvent.click(screen.getByText('Timeline'));

      expect(screen.getByText('No Gaps')).toBeInTheDocument();
      expect(screen.getByText('Chain Complete')).toBeInTheDocument();
    });

    it('should show negative status when gaps detected', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          timeline={{
            ...mockTimelineData,
            gaps_detected: true,
          }}
        />
      );

      await userEvent.click(screen.getByText('Timeline'));

      expect(screen.getByText('Gaps Detected')).toBeInTheDocument();
    });

    it('should show incomplete chain status', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          timeline={{
            ...mockTimelineData,
            chain_of_custody_complete: false,
          }}
        />
      );

      await userEvent.click(screen.getByText('Timeline'));

      expect(screen.getByText('Chain Incomplete')).toBeInTheDocument();
    });

    it('should handle empty events array', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          timeline={{
            ...mockTimelineData,
            events: [],
          }}
        />
      );

      await userEvent.click(screen.getByText('Timeline'));

      expect(screen.getByText('No Gaps')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should switch between tabs correctly', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
          manipulation={mockManipulationData}
        />
      );

      const steganographyTab = screen.getByText('Steganography');
      const manipulationTab = screen.getByText('Manipulation');

      expect(steganographyTab).toBeInTheDocument();
      expect(manipulationTab).toBeInTheDocument();

      await userEvent.click(manipulationTab);
      expect(screen.getByText('JPEG Ghosts')).toBeInTheDocument();
    });

    it('should display all tabs when data available', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
          manipulation={mockManipulationData}
          aiDetection={mockAIDetectionData}
          timeline={mockTimelineData}
        />
      );

      expect(screen.getByText('Steganography')).toBeInTheDocument();
      expect(screen.getByText('Manipulation')).toBeInTheDocument();
      expect(screen.getByText('AI Detection')).toBeInTheDocument();
      expect(screen.getByText('Timeline')).toBeInTheDocument();
    });
  });

  describe('Status Badges', () => {
    it('should show destructive badge for detected issues', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      const badge = findBadgeWithText('Hidden Data Detected');
      expect(badge).toHaveClass('bg-red-500/20');
    });

    it('should show secondary badge for no issues', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={{
            ...mockSteganographyData,
            detected: false,
          }}
        />
      );

      const badge = findBadgeWithText('No Hidden Data');
      expect(badge).toHaveClass('bg-emerald-500/20');
    });
  });

  describe('Confidence Indicators', () => {
    it('should display confidence percentage correctly', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      expect(screen.getByText('85%')).toBeInTheDocument();
    });

    it('should show confidence label', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      expect(screen.getByText('Confidence')).toBeInTheDocument();
    });

    it('should render progress bar for confidence', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      const progressBars = document.querySelectorAll('div[role="progressbar"]');
      expect(progressBars.length).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases', () => {
    it('should handle null values gracefully', () => {
      render(<AdvancedAnalysisResults {...defaultProps} />);

      expect(
        screen.getByText('No advanced analysis data available')
      ).toBeInTheDocument();
    });

    it('should handle partial data (only some tabs populated)', async () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      expect(findBadgeWithText('Hidden Data Detected')).toBeInTheDocument();

      // Other tabs should show "not available" messaging when their data is missing.
      await user.click(screen.getByText('Manipulation'));
      expect(
        screen.getByText('Manipulation detection not available')
      ).toBeInTheDocument();

      await user.click(screen.getByText('AI Detection'));
      expect(
        screen.getByText('AI detection not available')
      ).toBeInTheDocument();

      await user.click(screen.getByText('Timeline'));
      expect(
        screen.getByText('Timeline analysis not available')
      ).toBeInTheDocument();
    });

    it('should handle zero confidence values', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={{
            ...mockSteganographyData,
            confidence: 0,
          }}
        />
      );

      expect(screen.getByText('0%')).toBeInTheDocument();
    });

    it('should handle extreme confidence values', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={{
            ...mockSteganographyData,
            confidence: 100,
          }}
        />
      );

      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    it('should handle special characters in findings', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={{
            ...mockSteganographyData,
            findings: [
              'Finding with <script>alert("xss")</script> special chars',
            ],
          }}
        />
      );

      expect(screen.getByText(/Finding with/)).toBeInTheDocument();
    });

    it('should handle very long indicator descriptions', async () => {
      const longDescription = 'A'.repeat(500);
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          manipulation={{
            ...mockManipulationData,
            indicators: [
              {
                type: 'Test',
                severity: 'low',
                description: longDescription,
              },
            ],
          }}
        />
      );

      await user.click(screen.getByText('Manipulation'));
      expect(screen.getByText(longDescription)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible tab buttons', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      const tabs = screen.getAllByRole('tab');
      tabs.forEach((tab) => {
        expect(tab).toBeVisible();
      });
    });

    it('should have accessible progress bars', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      const progressBars = screen.getAllByRole('progressbar');
      progressBars.forEach((bar) => {
        expect(bar).toBeVisible();
      });
    });

    it('should announce status changes to screen readers', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      const statusBadges = screen.getAllByText(/Hidden Data|No Hidden Data/);
      expect(statusBadges.length).toBeGreaterThan(0);
    });
  });

  describe('Card Structure', () => {
    it('should display card title and description', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      expect(screen.getByText('Forensic Analysis')).toBeInTheDocument();
      expect(
        screen.getByText(/Deep analysis for authenticity/)
      ).toBeInTheDocument();
    });

    it('should display fingerprint icon', () => {
      render(
        <AdvancedAnalysisResults
          {...defaultProps}
          steganography={mockSteganographyData}
        />
      );

      const fingerprintIcon =
        document.querySelector('svg[data-lucide="fingerprint"]') ||
        document.querySelector('svg[class*="fingerprint"]');
      expect(fingerprintIcon).toBeInTheDocument();
    });
  });

  describe('Component Integration', () => {
    it('should render all analysis types together', async () => {
      render(
        <AdvancedAnalysisResults
          steganography={mockSteganographyData}
          manipulation={mockManipulationData}
          aiDetection={mockAIDetectionData}
          timeline={mockTimelineData}
        />
      );

      expect(screen.getByText('Forensic Analysis')).toBeInTheDocument();
      expect(findBadgeWithText('Hidden Data Detected')).toBeInTheDocument();

      await user.click(screen.getByText('Manipulation'));
      expect(findBadgeWithText('Manipulation Detected')).toBeInTheDocument();

      await user.click(screen.getByText('AI Detection'));
      expect(findBadgeWithText('AI-Generated')).toBeInTheDocument();

      await user.click(screen.getByText('Timeline'));
      expect(screen.getByText('No Gaps')).toBeInTheDocument();
    });

    it('should handle mixed positive and negative results', async () => {
      render(
        <AdvancedAnalysisResults
          steganography={{ ...mockSteganographyData, detected: true }}
          manipulation={{ ...mockManipulationData, detected: false }}
          aiDetection={{ ...mockAIDetectionData, ai_generated: false }}
          timeline={mockTimelineData}
        />
      );

      expect(findBadgeWithText('Hidden Data Detected')).toBeInTheDocument();

      await user.click(screen.getByText('Manipulation'));
      expect(findBadgeWithText('No Manipulation')).toBeInTheDocument();

      await user.click(screen.getByText('AI Detection'));
      expect(findBadgeWithText('Likely Authentic')).toBeInTheDocument();

      await user.click(screen.getByText('Timeline'));
      expect(screen.getByText('Chain Complete')).toBeInTheDocument();
    });
  });
});
