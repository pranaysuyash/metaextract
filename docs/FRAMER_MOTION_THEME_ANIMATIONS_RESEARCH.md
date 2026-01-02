# Framer Motion for Advanced Theme Animations

## Overview

This document outlines how Framer Motion can be leveraged for more sophisticated theme animations in the MetaExtract application.

## What Could Be Implemented

Framer Motion could be used to create more advanced theme transition animations beyond simple CSS transitions, including:

1. **Page-level theme transitions** - Animate the entire page when theme changes
2. **Component-level animations** - Individual components could have more complex animations during theme changes
3. **Staggered animations** - Elements could animate in sequence during theme transitions
4. **Custom easing functions** - More sophisticated easing than CSS can provide

## Why This Would Be Beneficial

- **Enhanced UX**: More engaging and polished theme transitions
- **Leverage existing dependency**: Framer Motion is already in the project but not used for theme transitions
- **Differentiation**: More sophisticated animations than typical theme switches
- **Consistency**: Use the same animation library as other components in the project

## How It Could Be Implemented

### Option 1: Enhanced Theme Provider
Create a wrapper around the existing ThemeProvider that uses AnimatePresence to animate theme changes:

```tsx
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from '@/lib/theme-provider';

const AnimatedThemeWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { resolvedTheme } = useTheme();
  
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={resolvedTheme}
        initial={{ opacity: 0.8, filter: 'blur(4px)' }}
        animate={{ opacity: 1, filter: 'blur(0px)' }}
        exit={{ opacity: 0.8, filter: 'blur(4px)' }}
        transition={{ 
          duration: 0.5, 
          ease: "easeInOut" 
        }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};
```

### Option 2: Theme Transition Hook
Create a custom hook that provides animated theme transitions:

```tsx
import { useTheme } from '@/lib/theme-provider';
import { motion } from 'framer-motion';

const useAnimatedTheme = () => {
  const { mode, setMode, resolvedTheme } = useTheme();
  
  const setAnimatedMode = (newMode: ThemeMode) => {
    // Trigger animation before changing theme
    // This would require more complex state management
    setMode(newMode);
  };
  
  return {
    ...useTheme(),
    setAnimatedMode,
    ThemeTransition: ({ children }: { children: React.ReactNode }) => (
      <motion.div
        initial={{ opacity: 0.8 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        {children}
      </motion.div>
    )
  };
};
```

### Option 3: Component-Specific Animations
Individual components could animate their appearance based on theme changes using Framer Motion.

## Considerations

### Performance
- Complex animations could impact performance
- Need to ensure animations are smooth on all devices
- Consider user "prefers-reduced-motion" settings

### Complexity
- Would add complexity to the theming system
- May not be necessary for simple theme transitions
- CSS transitions may be sufficient for most use cases

## Current State

The project already uses Framer Motion in multiple components but not for theme transitions. The current CSS-based transitions provide a good baseline experience, and more complex animations might be overkill for theme switching.

## Recommendation

The current CSS-based transitions are likely sufficient for theme changes. Framer Motion is better utilized for more complex UI animations and interactions rather than basic theme transitions, which work well with CSS transitions.

## Related Files

- `client/src/lib/theme-provider.tsx` - Current theme provider implementation
- `client/src/components/theme-toggle.tsx` - Theme toggle component
- Components using Framer Motion:
  - `client/src/pages/home.tsx`
  - `client/src/pages/results.tsx`
  - `client/src/components/pricing-calculator.tsx`
  - And several other components
