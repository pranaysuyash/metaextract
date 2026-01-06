import React from 'react';
import { render, screen } from '@testing-library/react';
import { ForensicAnalysis } from './ForensicAnalysis';
import {
  AuthenticityBadge,
  ForensicConfidenceIndicator,
} from './AuthenticityBadge';
import { KeyFindings } from './KeyFindings';
import { ProgressiveDisclosure } from './ProgressiveDisclosure';

describe.skip('Forensic Analysis Components Integration', () => {
  const mockForensicData = {
    steganography: {
      detected: false,
      confidence: 95,
      methodsChecked: ['LSB', 'DCT', 'Echo'],
      findings: ['No hidden data detected'],
      details: 'Comprehensive steganography analysis completed',
    },
    manipulation: {
      detected: false,
      confidence: 88,
      indicators: [],
      originalityScore: 92,
    },
    aiDetection: {
      aiGenerated: false,
      confidence: 91,
      modelHints: [],
      detectionMethods: ['Frequency Analysis', 'Artifact Detection'],
    },
    authenticityScore: 89,
  };

  const mockKeyFindings = {
    when: 'January 3, 2025 at 3:45 PM',
    where: 'San Francisco, California',
    device: 'iPhone 15 Pro',
    edited: false,
    authenticity: 'Appears authentic',
    confidence: 'high' as const,
  };

  const mockQuickDetails = {
    resolution: '12.2 megapixels',
    fileSize: '3.2 MB',
    cameraSettings: 'f/1.6, 1/120s, ISO 64',
    colorSpace: 'sRGB',
    dimensions: '4032 x 3024',
  };

  describe('ForensicAnalysis Component', () => {
    it('renders with forensic data', () => {
      render(
        <ForensicAnalysis
          steganography={mockForensicData.steganography}
          manipulation={mockForensicData.manipulation}
          aiDetection={mockForensicData.aiDetection}
          authenticityScore={mockForensicData.authenticityScore}
        />
      );

      expect(screen.getByText('Forensic Analysis')).toBeInTheDocument();
      expect(screen.getByText('89%')).toBeInTheDocument();
      expect(screen.getByText('Authentic')).toBeInTheDocument();
    });

    it('shows no data message when forensic data is missing', () => {
      render(<ForensicAnalysis />);

      expect(
        screen.getByText('No forensic analysis data available')
      ).toBeInTheDocument();
    });

    it('displays correct number of analysis tabs', () => {
      render(
        <ForensicAnalysis
          steganography={mockForensicData.steganography}
          manipulation={mockForensicData.manipulation}
          aiDetection={mockForensicData.aiDetection}
          authenticityScore={mockForensicData.authenticityScore}
        />
      );

      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Steganography')).toBeInTheDocument();
      expect(screen.getByText('Manipulation')).toBeInTheDocument();
      expect(screen.getByText('AI Detection')).toBeInTheDocument();
    });
  });

  describe('AuthenticityBadge Component', () => {
    it('displays authentic badge for high scores', () => {
      render(<AuthenticityBadge score={85} />);

      expect(screen.getByText('Authentic (85%)')).toBeInTheDocument();
    });

    it('displays questionable badge for medium scores', () => {
      render(<AuthenticityBadge score={65} />);

      expect(screen.getByText('Questionable (65%)')).toBeInTheDocument();
    });

    it('displays suspicious badge for low scores', () => {
      render(<AuthenticityBadge score={35} />);

      expect(screen.getByText('Suspicious (35%)')).toBeInTheDocument();
    });

    it('supports compact variant', () => {
      render(<AuthenticityBadge score={85} variant="compact" />);

      expect(screen.getByText('85%')).toBeInTheDocument();
    });

    it('supports detailed variant', () => {
      render(<AuthenticityBadge score={85} variant="detailed" />);

      expect(screen.getByText('Authentic (85%)')).toBeInTheDocument();
      expect(screen.getByText('Confidence: 85%')).toBeInTheDocument();
    });
  });

  describe('ForensicConfidenceIndicator Component', () => {
    it('displays authenticity indicators correctly', () => {
      const { rerender } = render(
        <ForensicConfidenceIndicator confidence={85} type="authenticity" />
      );

      expect(screen.getByText('Authentic (85%)')).toBeInTheDocument();

      rerender(
        <ForensicConfidenceIndicator confidence={45} type="authenticity" />
      );

      expect(screen.getByText('Suspicious (45%)')).toBeInTheDocument();
    });

    it('displays manipulation indicators correctly', () => {
      const { rerender } = render(
        <ForensicConfidenceIndicator confidence={85} type="manipulation" />
      );

      expect(screen.getByText('High Risk (85%)')).toBeInTheDocument();

      rerender(
        <ForensicConfidenceIndicator confidence={25} type="manipulation" />
      );

      expect(screen.getByText('Low Risk (25%)')).toBeInTheDocument();
    });

    it('supports different sizes', () => {
      const { rerender } = render(
        <ForensicConfidenceIndicator confidence={85} size="sm" />
      );

      expect(screen.getByText('Authentic (85%)')).toBeInTheDocument();

      rerender(<ForensicConfidenceIndicator confidence={85} size="lg" />);

      expect(screen.getByText('Authentic (85%)')).toBeInTheDocument();
    });
  });

  describe('KeyFindings Component', () => {
    it('renders basic findings', () => {
      render(<KeyFindings findings={mockKeyFindings} />);

      expect(screen.getByText('When')).toBeInTheDocument();
      expect(
        screen.getByText('January 3, 2025 at 3:45 PM')
      ).toBeInTheDocument();
      expect(screen.getByText('Where')).toBeInTheDocument();
      expect(screen.getByText('San Francisco, California')).toBeInTheDocument();
    });

    it('integrates forensic analysis when provided', () => {
      render(
        <KeyFindings
          findings={mockKeyFindings}
          forensicScore={mockForensicData.authenticityScore}
          forensicAnalysis={mockForensicData}
          showForensicIndicators={true}
        />
      );

      expect(screen.getByText('Forensic Analysis')).toBeInTheDocument();
      expect(screen.getByText('Forensic: 89%')).toBeInTheDocument();
    });

    it('supports compact mode', () => {
      render(
        <KeyFindings
          findings={mockKeyFindings}
          forensicScore={mockForensicData.authenticityScore}
          forensicAnalysis={mockForensicData}
          compact={true}
        />
      );

      expect(screen.getByText('Forensic: 89%')).toBeInTheDocument();
    });
  });

  describe('ProgressiveDisclosure Component', () => {
    it('renders with forensic analysis tab when data is available', () => {
      const mockData = {
        keyFindings: mockKeyFindings,
        quickDetails: mockQuickDetails,
        forensicAnalysis: mockForensicData,
      };

      render(<ProgressiveDisclosure data={mockData} />);

      expect(screen.getByText('Forensic')).toBeInTheDocument();
      expect(screen.getByText('Key Findings')).toBeInTheDocument();
    });

    it('does not show forensic tab when no forensic data', () => {
      const mockDataWithoutForensic = {
        keyFindings: mockKeyFindings,
        quickDetails: mockQuickDetails,
      };

      render(<ProgressiveDisclosure data={mockDataWithoutForensic} />);

      expect(screen.queryByText('Forensic')).not.toBeInTheDocument();
    });

    it('supports default tab selection', () => {
      const mockData = {
        keyFindings: mockKeyFindings,
        quickDetails: mockQuickDetails,
        forensicAnalysis: mockForensicData,
      };

      render(<ProgressiveDisclosure data={mockData} defaultTab="forensic" />);

      // The forensic tab content should be visible
      expect(screen.getByText('Forensic Analysis Results')).toBeInTheDocument();
    });
  });

  describe('Integration Scenarios', () => {
    it('handles suspicious forensic results correctly', () => {
      const suspiciousForensicData = {
        ...mockForensicData,
        manipulation: {
          detected: true,
          confidence: 85,
          indicators: [
            {
              type: 'Clone Detection',
              severity: 'high' as const,
              description: 'Evidence of cloning tool usage',
              confidence: 82,
            },
          ],
          originalityScore: 25,
        },
        authenticityScore: 35,
      };

      render(
        <KeyFindings
          findings={mockKeyFindings}
          forensicScore={suspiciousForensicData.authenticityScore}
          forensicAnalysis={suspiciousForensicData}
          showForensicIndicators={true}
        />
      );

      expect(screen.getByText('Suspicious (35%)')).toBeInTheDocument();
    });

    it('displays forensic findings in detailed view', () => {
      render(
        <ForensicAnalysis
          steganography={mockForensicData.steganography}
          manipulation={mockForensicData.manipulation}
          aiDetection={mockForensicData.aiDetection}
          authenticityScore={mockForensicData.authenticityScore}
        />
      );

      // Navigate to steganography tab
      const stegoTab = screen.getByText('Steganography');
      stegoTab.click();

      expect(screen.getByText('No Hidden Data')).toBeInTheDocument();
      expect(screen.getByText('95% confidence')).toBeInTheDocument();
    });
  });
});
