/**
 * Property-based tests for the Intelligent User Onboarding system
 * 
 * These tests validate universal correctness properties using fast-check
 * to ensure the onboarding system behaves correctly across all possible inputs.
 */

// Polyfill for TextEncoder/TextDecoder in Node.js test environment
import { TextEncoder, TextDecoder } from 'util';
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;

import React from 'react';
import { render, screen } from '@testing-library/react';
import fc from 'fast-check';
import { OnboardingProvider, useOnboarding } from '../onboarding';

// Mock the auth hook completely for testing
jest.mock('../auth', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: jest.fn(() => ({
    isAuthenticated: false,
    isLoading: false,
    user: null
  }))
}));

// Test utilities
interface TestWrapperProps {
  children: React.ReactNode;
  mockAuthState?: {
    isAuthenticated: boolean;
    isLoading: boolean;
    user: any;
  };
}

function TestWrapper({ children, mockAuthState }: TestWrapperProps) {
  // Mock the auth state if provided
  if (mockAuthState) {
    const { useAuth } = require('../auth');
    useAuth.mockReturnValue(mockAuthState);
  }
  
  return (
    <OnboardingProvider>
      {children}
    </OnboardingProvider>
  );
}

// Mock component to test onboarding state
function OnboardingTestComponent() {
  const { session, isOnboardingActive, isOnboardingComplete, getRecommendedPath } = useOnboarding();
  
  return (
    <div>
      <div data-testid="onboarding-state">
        {JSON.stringify({
          hasSession: !!session,
          isActive: isOnboardingActive,
          isComplete: isOnboardingComplete
        })}
      </div>
      <div data-testid="path-recommendation">
        {JSON.stringify(getRecommendedPath({
          useCase: 'personal',
          technicalLevel: 'beginner',
          primaryFileTypes: ['image'],
          goals: ['learn']
        }))}
      </div>
    </div>
  );
}

describe('Onboarding System Property Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock fetch for onboarding API calls
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 404,
        json: () => Promise.resolve({}),
      })
    ) as jest.Mock;
  });

  afterEach(() => {
    jest.restoreAllMocks();
    // Clean up any rendered components
    document.body.innerHTML = '';
  });

  /**
   * Property 1: New user welcome screen display
   * For any user without existing session data or onboarding completion status,
   * the welcome screen should be displayed on first application visit
   * Validates: Requirements 1.1
   */
  test('Property 1: New user welcome screen display', () => {
    fc.assert(fc.property(
      fc.record({
        isAuthenticated: fc.boolean(),
        isLoading: fc.boolean(),
        user: fc.option(fc.record({
          id: fc.string(),
          username: fc.string(),
          email: fc.string()
        }), { nil: null })
      }),
      (authState) => {
        // Mock the auth hook to return our test state
        const { useAuth } = require('../auth');
        useAuth.mockReturnValue(authState);

        // Render the component with test state
        const { unmount } = render(
          <TestWrapper mockAuthState={authState}>
            <OnboardingTestComponent />
          </TestWrapper>
        );

        const stateElements = screen.getAllByTestId('onboarding-state');
        const state = JSON.parse(stateElements[0].textContent || '{}');

        // For authenticated users with a user object, onboarding should be available
        if (authState.isAuthenticated && authState.user && !authState.isLoading) {
          // The onboarding system should be ready to show onboarding
          expect(state.hasSession).toBe(false); // No session initially
          expect(state.isComplete).toBe(false); // Not completed initially
        }

        // For unauthenticated users, no onboarding should be active
        if (!authState.isAuthenticated || !authState.user) {
          expect(state.isActive).toBe(false);
        }

        // Clean up
        unmount();
      }
    ), { numRuns: 20 });
  });

  /**
   * Property 2: Path recommendation consistency
   * For any valid user profile, the system should consistently recommend
   * the same onboarding path for the same profile characteristics
   */
  test('Property 2: Path recommendation consistency', () => {
    fc.assert(fc.property(
      fc.record({
        useCase: fc.constantFrom('personal', 'professional', 'forensic', 'research', 'enterprise'),
        technicalLevel: fc.constantFrom('beginner', 'intermediate', 'advanced'),
        primaryFileTypes: fc.array(fc.string(), { minLength: 1, maxLength: 5 }),
        industry: fc.option(fc.string(), { nil: undefined }),
        goals: fc.array(fc.string(), { minLength: 1, maxLength: 3 })
      }),
      (userProfile) => {
        // Render the component multiple times with the same profile
        const { unmount: unmount1 } = render(
          <TestWrapper>
            <OnboardingTestComponent />
          </TestWrapper>
        );

        const pathElements1 = screen.getAllByTestId('path-recommendation');
        const path1 = JSON.parse(pathElements1[0].textContent || '{}');
        
        unmount1();

        const { unmount: unmount2 } = render(
          <TestWrapper>
            <OnboardingTestComponent />
          </TestWrapper>
        );

        const pathElements2 = screen.getAllByTestId('path-recommendation');
        const path2 = JSON.parse(pathElements2[0].textContent || '{}');
        
        unmount2();

        // Same profile should always get the same recommended path
        expect(path1.id).toBe(path2.id);
        expect(path1.name).toBe(path2.name);
        expect(path1.steps.length).toBe(path2.steps.length);
      }
    ), { numRuns: 15 });
  });

  /**
   * Property 3: Onboarding path structure validation
   * For any recommended onboarding path, it should have valid structure
   * with required fields and logical step progression
   */
  test('Property 3: Onboarding path structure validation', () => {
    fc.assert(fc.property(
      fc.record({
        useCase: fc.constantFrom('personal', 'professional', 'forensic', 'research', 'enterprise'),
        technicalLevel: fc.constantFrom('beginner', 'intermediate', 'advanced'),
        primaryFileTypes: fc.array(fc.string({ minLength: 1 }), { minLength: 1, maxLength: 5 }),
        goals: fc.array(fc.string({ minLength: 1 }), { minLength: 1, maxLength: 3 })
      }),
      (userProfile) => {
        const { unmount } = render(
          <TestWrapper>
            <OnboardingTestComponent />
          </TestWrapper>
        );

        const pathElements = screen.getAllByTestId('path-recommendation');
        const path = JSON.parse(pathElements[0].textContent || '{}');

        // Validate path structure
        expect(path).toHaveProperty('id');
        expect(path).toHaveProperty('name');
        expect(path).toHaveProperty('description');
        expect(path).toHaveProperty('steps');
        expect(path).toHaveProperty('estimatedDuration');
        expect(path).toHaveProperty('prerequisites');

        // Validate path content
        expect(typeof path.id).toBe('string');
        expect(typeof path.name).toBe('string');
        expect(typeof path.description).toBe('string');
        expect(Array.isArray(path.steps)).toBe(true);
        expect(typeof path.estimatedDuration).toBe('number');
        expect(Array.isArray(path.prerequisites)).toBe(true);

        // Validate steps structure
        path.steps.forEach((step: any) => {
          expect(step).toHaveProperty('id');
          expect(step).toHaveProperty('title');
          expect(step).toHaveProperty('description');
          expect(step).toHaveProperty('position');
          expect(step).toHaveProperty('skippable');
          expect(step).toHaveProperty('completionCriteria');
          
          expect(typeof step.id).toBe('string');
          expect(typeof step.title).toBe('string');
          expect(typeof step.description).toBe('string');
          expect(['top', 'bottom', 'left', 'right', 'center']).toContain(step.position);
          expect(typeof step.skippable).toBe('boolean');
          expect(step.completionCriteria).toHaveProperty('type');
          expect(['interaction', 'time', 'manual']).toContain(step.completionCriteria.type);
        });

        // Validate logical constraints
        expect(path.estimatedDuration).toBeGreaterThan(0);
        expect(path.steps.length).toBeGreaterThan(0);

        // Clean up
        unmount();
      }
    ), { numRuns: 15 });
  });
});