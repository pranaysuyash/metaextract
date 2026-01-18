export interface ChallengeData {
  type: 'behavioral' | 'captcha' | 'device_verification' | 'standard' | 'delay';
  difficulty: 'easy' | 'medium' | 'hard';
  data: {
    sessionId?: string;
    instructions?: string;
    [key: string]: unknown;
  };
  reasons: string[];
  incidentId: string;
  instructions: string;
}

export interface ChallengeResponse {
  success: boolean;
  message?: string;
  incidentId?: string;
  completed?: boolean;
  type?: string;
  acknowledged?: boolean;
  behavioralData?: {
    behavioralScore: number;
    isHuman: boolean;
    confidence: number;
    dataPoints: Record<string, unknown>;
  };
  [key: string]: unknown;
}

export interface ChallengeProps {
  challenge: ChallengeData;
  retryAfter: number;
  onComplete: (response: ChallengeResponse) => void;
  onCancel: () => void;
}

export type ChallengeType = ChallengeData['type'];
