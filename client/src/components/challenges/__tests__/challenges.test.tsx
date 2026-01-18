/**
 * Challenge Components Tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChallengeUI } from '../ChallengeUI';
import { DelayChallenge } from '../DelayChallenge';
import { CaptchaChallenge } from '../CaptchaChallenge';
import { BehavioralChallenge } from '../BehavioralChallenge';
import { ChallengeData } from '../types';

const mockChallenge: ChallengeData = {
  type: 'delay',
  difficulty: 'easy',
  data: {
    sessionId: 'test-session-123',
  },
  reasons: ['High risk score'],
  incidentId: 'incident-123',
  instructions: 'Please wait while we verify your request',
};

describe('Challenge Components', () => {
  describe('ChallengeUI', () => {
    const defaultProps = {
      challenge: mockChallenge,
      retryAfter: 30,
      onComplete: jest.fn(),
      onCancel: jest.fn(),
    };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('renders challenge UI with correct title', () => {
      render(<ChallengeUI {...defaultProps} />);

      expect(screen.getByText('Security Verification')).toBeInTheDocument();
      expect(
        screen.getByText('Security verification required')
      ).toBeInTheDocument();
    });

    it('displays challenge reasons', () => {
      render(<ChallengeUI {...defaultProps} />);

      expect(screen.getByText('High risk score')).toBeInTheDocument();
    });

    it('shows incident ID', () => {
      render(<ChallengeUI {...defaultProps} />);

      expect(screen.getByText(/Incident ID:/i)).toBeInTheDocument();
    });

    it('calls onCancel when cancel button is clicked', () => {
      render(<ChallengeUI {...defaultProps} />);

      const cancelButton = screen.getAllByRole('button', {
        name: /cancel/i,
      })[0];
      fireEvent.click(cancelButton);

      expect(defaultProps.onCancel).toHaveBeenCalledTimes(1);
    });

    it('renders correct icon for delay challenge', () => {
      render(<ChallengeUI {...defaultProps} />);

      expect(screen.getByTestId('clock-icon')).toBeInTheDocument();
    });

    it('renders correct title for CAPTCHA challenge', () => {
      const captchaChallenge = {
        ...mockChallenge,
        type: 'captcha' as const,
      };

      render(<ChallengeUI {...defaultProps} challenge={captchaChallenge} />);

      expect(screen.getByText('CAPTCHA Verification')).toBeInTheDocument();
    });

    it('renders correct title for behavioral challenge', () => {
      const behavioralChallenge = {
        ...mockChallenge,
        type: 'behavioral' as const,
      };

      render(<ChallengeUI {...defaultProps} challenge={behavioralChallenge} />);

      expect(screen.getByText('Behavioral Verification')).toBeInTheDocument();
    });
  });

  describe('DelayChallenge', () => {
    const defaultProps = {
      challenge: mockChallenge,
      retryAfter: 5,
      onComplete: jest.fn(),
      onCancel: jest.fn(),
    };

    beforeEach(() => {
      jest.clearAllMocks();
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('renders countdown timer', () => {
      render(<DelayChallenge {...defaultProps} />);

      expect(screen.getByText(/0:05/i)).toBeInTheDocument();
    });

    it('shows continue button when timer expires', async () => {
      render(<DelayChallenge {...defaultProps} />);

      expect(screen.queryByText('Continue to Upload')).not.toBeInTheDocument();

      jest.advanceTimersByTime(5000);

      await waitFor(() => {
        expect(screen.getByText('Continue to Upload')).toBeInTheDocument();
      });
    });

    it('calls onComplete when continue is clicked after timer', async () => {
      render(<DelayChallenge {...defaultProps} />);

      jest.advanceTimersByTime(5000);

      await waitFor(() => {
        expect(screen.getByText('Continue to Upload')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Continue to Upload'));

      expect(defaultProps.onComplete).toHaveBeenCalledWith({
        success: true,
        completed: true,
        type: 'delay',
      });
    });

    it('calls onCancel when cancel button is clicked', () => {
      render(<DelayChallenge {...defaultProps} />);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelButton);

      expect(defaultProps.onCancel).toHaveBeenCalledTimes(1);
    });
  });

  describe('CaptchaChallenge', () => {
    const defaultProps = {
      challenge: mockChallenge,
      onComplete: jest.fn(),
      onCancel: jest.fn(),
    };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('renders CAPTCHA verification UI', () => {
      render(<CaptchaChallenge {...defaultProps} />);

      expect(
        screen.getByText('Click to confirm you are not a robot')
      ).toBeInTheDocument();
    });

    it('shows verification button initially', () => {
      render(<CaptchaChallenge {...defaultProps} />);

      expect(
        screen.getByRole('button', { name: /i'm not a robot/i })
      ).toBeInTheDocument();
    });

    it('shows verified state after clicking verify', async () => {
      render(<CaptchaChallenge {...defaultProps} />);

      const verifyButton = screen.getByRole('button', {
        name: /i'm not a robot/i,
      });
      fireEvent.click(verifyButton);

      await new Promise(resolve => setTimeout(resolve, 2000));

      expect(
        screen.getByText('CAPTCHA verified successfully')
      ).toBeInTheDocument();
    });

    it('shows privacy note', () => {
      render(<CaptchaChallenge {...defaultProps} />);

      expect(
        screen.getByText(/helps protect our platform/i)
      ).toBeInTheDocument();
    });
  });

  describe('BehavioralChallenge', () => {
    const defaultProps = {
      challenge: mockChallenge,
      onComplete: jest.fn(),
      onCancel: jest.fn(),
    };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('renders behavioral analysis UI', () => {
      render(<BehavioralChallenge {...defaultProps} />);

      expect(
        screen.getByText('Analyzing your browsing behavior')
      ).toBeInTheDocument();
    });

    it('shows collection progress indicator', () => {
      render(<BehavioralChallenge {...defaultProps} />);

      expect(
        screen.getByText(/collecting behavioral patterns/i)
      ).toBeInTheDocument();
    });

    it('shows movement and typing indicators', () => {
      render(<BehavioralChallenge {...defaultProps} />);

      expect(screen.getByText('Movement')).toBeInTheDocument();
      expect(screen.getByText('Typing')).toBeInTheDocument();
    });

    it('shows completion state after collection finishes', async () => {
      render(<BehavioralChallenge {...defaultProps} />);

      await new Promise(resolve => setTimeout(resolve, 3500));

      expect(
        screen.getByText('Behavioral analysis complete')
      ).toBeInTheDocument();
    });

    it('calls onComplete with behavioral data after completion', async () => {
      render(<BehavioralChallenge {...defaultProps} />);

      await new Promise(resolve => setTimeout(resolve, 3500));

      const continueButton = screen.getByRole('button', { name: /continue/i });
      fireEvent.click(continueButton);

      expect(defaultProps.onComplete).toHaveBeenCalled();
      const callArg = defaultProps.onComplete.mock.calls[0][0];
      expect(callArg.success).toBe(true);
      expect(callArg.completed).toBe(true);
      expect(callArg.type).toBe('behavioral');
      expect(callArg.behavioralData).toBeDefined();
      expect(callArg.behavioralData.isHuman).toBe(true);
    });

    it('includes data points in the response', async () => {
      render(<BehavioralChallenge {...defaultProps} />);

      await new Promise(resolve => setTimeout(resolve, 3500));

      const continueButton = screen.getByRole('button', { name: /continue/i });
      fireEvent.click(continueButton);

      const callArg = defaultProps.onComplete.mock.calls[0][0];
      expect(callArg.behavioralData.dataPoints).toBeDefined();
      expect(callArg.behavioralData.dataPoints.mouseMovements).toBeDefined();
    });
  });
});
