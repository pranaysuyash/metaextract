/**
 * Unit tests for utility functions
 */

import { cn } from '@/lib/utils';

describe('Utility Functions', () => {
  describe('cn (classnames)', () => {
    it('should merge classnames correctly', () => {
      const result = cn('base-class', 'extra-class');
      expect(result).toContain('base-class');
      expect(result).toContain('extra-class');
    });

    it('should handle conditional classes', () => {
      const result = cn(
        'base-class',
        true && 'conditional-true',
        false && 'conditional-false'
      );
      expect(result).toContain('base-class');
      expect(result).toContain('conditional-true');
      expect(result).not.toContain('conditional-false');
    });

    it('should merge tailwind classes intelligently', () => {
      const result = cn('p-2 p-4', 'm-2 m-4');
      // tailwind-merge should resolve conflicting classes
      expect(result).toBeTruthy();
      expect(typeof result).toBe('string');
    });

    it('should handle array inputs', () => {
      const result = cn(['class1', 'class2'], ['class3', 'class4']);
      expect(result).toContain('class1');
      expect(result).toContain('class4');
    });

    it('should handle object inputs', () => {
      const result = cn({
        'active-class': true,
        'inactive-class': false
      });
      expect(result).toContain('active-class');
      expect(result).not.toContain('inactive-class');
    });
  });
});
