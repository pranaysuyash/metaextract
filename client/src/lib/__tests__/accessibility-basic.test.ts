/**
 * Basic Accessibility Tests
 * 
 * Tests the accessibility utilities and infrastructure.
 * 
 * @module accessibility-basic.test
 * @validates Requirements 1.1, 1.5 - Universal ARIA compliance
 */

import '@testing-library/jest-dom';
import {
  generateAriaId,
  createAriaAttributes,
  setAriaAttributes,
  createAccessibleInput,
  getFocusableElements,
  announceToScreenReader,
  calculateContrastRatio,
  meetsContrastRequirement,
} from '../accessibility-utils';

describe('Accessibility Foundation Tests', () => {
  beforeEach(() => {
    // Clear any existing live regions
    const existingRegions = document.querySelectorAll('[aria-live]');
    existingRegions.forEach(region => region.remove());
    
    // Reset document focus
    if (document.activeElement && 'blur' in document.activeElement) {
      (document.activeElement as HTMLElement).blur();
    }
  });

  afterEach(() => {
    // Clean up any created elements
    const testElements = document.querySelectorAll('[data-testid]');
    testElements.forEach(element => element.remove());
  });

  test('generates unique ARIA IDs', () => {
    const ids = new Set();
    for (let i = 0; i < 10; i++) {
      const id = generateAriaId('test');
      expect(id).toMatch(/^test-[a-z0-9]+$/);
      expect(ids.has(id)).toBe(false);
      ids.add(id);
    }
  });

  test('creates valid ARIA attributes', () => {
    const element = document.createElement('div');
    element.setAttribute('data-testid', 'aria-element');
    
    const attributes = createAriaAttributes({
      role: 'button',
      'aria-expanded': true,
      'aria-selected': false,
      'aria-disabled': false,
      'aria-required': true,
      'aria-hidden': false,
    });
    
    setAriaAttributes(element, attributes);
    document.body.appendChild(element);
    
    try {
      expect(element.getAttribute('role')).toBe('button');
      expect(element.getAttribute('aria-expanded')).toBe('true');
      expect(element.getAttribute('aria-selected')).toBe('false');
      expect(element.getAttribute('aria-disabled')).toBe('false');
      expect(element.getAttribute('aria-required')).toBe('true');
      expect(element.getAttribute('aria-hidden')).toBe('false');
    } finally {
      element.remove();
    }
  });

  test('creates accessible form inputs with labels', () => {
    const container = document.createElement('div');
    container.setAttribute('data-testid', 'form-container');
    
    const { input, label } = createAccessibleInput('text', 'Test Label', {
      required: true,
      id: 'test-input-123',
    });
    
    container.appendChild(label);
    container.appendChild(input);
    document.body.appendChild(container);
    
    try {
      // Validate that input has proper labeling
      const hasLabel = 
        input.getAttribute('aria-label') ||
        input.getAttribute('aria-labelledby') ||
        document.querySelector(`label[for="${input.id}"]`);
      
      expect(hasLabel).toBeTruthy();
      expect(input.hasAttribute('required')).toBe(true);
      expect(input.getAttribute('aria-required')).toBe('true');
    } finally {
      container.remove();
    }
  });

  test('calculates color contrast ratios correctly', () => {
    // Test known color combinations
    const whiteBlackRatio = calculateContrastRatio('#ffffff', '#000000');
    expect(whiteBlackRatio).toBeCloseTo(21, 1);
    
    const sameColorRatio = calculateContrastRatio('#ff0000', '#ff0000');
    expect(sameColorRatio).toBeCloseTo(1, 1);
    
    // Test WCAG compliance
    expect(meetsContrastRequirement('#ffffff', '#000000', 'AA', false)).toBe(true);
    expect(meetsContrastRequirement('#ffffff', '#000000', 'AA', true)).toBe(true);
    expect(meetsContrastRequirement('#ffffff', '#ffffff', 'AA', false)).toBe(false);
  });

  test('creates live regions for screen reader announcements', () => {
    const regionId = 'test-region-123';
    const message = 'Test announcement';
    const priority = 'polite';
    
    announceToScreenReader(message, priority, regionId);
    
    // Check that live region was created
    const liveRegion = document.getElementById(regionId);
    expect(liveRegion).toBeTruthy();
    expect(liveRegion?.getAttribute('aria-live')).toBe(priority);
    expect(liveRegion?.getAttribute('aria-atomic')).toBe('true');
    
    // Clean up
    liveRegion?.remove();
  });

  test('identifies focusable elements correctly', () => {
    const container = document.createElement('div');
    container.setAttribute('data-testid', 'focus-container');
    
    // Create various elements
    const button = document.createElement('button');
    button.textContent = 'Test Button';
    
    const input = document.createElement('input');
    input.type = 'text';
    
    const link = document.createElement('a');
    link.href = '#';
    link.textContent = 'Test Link';
    
    const div = document.createElement('div');
    div.textContent = 'Not focusable';
    
    const focusableDiv = document.createElement('div');
    focusableDiv.tabIndex = 0;
    focusableDiv.textContent = 'Focusable div';
    
    container.appendChild(button);
    container.appendChild(input);
    container.appendChild(link);
    container.appendChild(div);
    container.appendChild(focusableDiv);
    document.body.appendChild(container);
    
    try {
      const focusableElements = getFocusableElements(container);
      const elementTypes = focusableElements.map(item => item.element.tagName.toLowerCase());
      
      expect(elementTypes).toContain('button');
      expect(elementTypes).toContain('input');
      expect(elementTypes).toContain('a');
      expect(elementTypes).toContain('div'); // The focusable div
      expect(focusableElements.length).toBe(4); // Should not include the non-focusable div
    } finally {
      container.remove();
    }
  });
});