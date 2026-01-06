# Onboarding Engine

Core state management and orchestration for intelligent user onboarding system.

## Features

- **Session-based progress tracking**: Tracks user's onboarding state across sessions
- **Per-UI-version configuration**: Tailored onboarding for Original, V2, and Images MVP
- **Event-driven architecture**: Decoupled components communicate via events
- **Cross-UI synchronization**: State syncs between different UI versions
- **Adaptive learning**: Adjusts based on user behavior and expertise

## Architecture

```
OnboardingEngine (Core)
  ├── OnboardingStorage (Persistence)
  ├── OnboardingEvents (Event Bus)
  ├── OnboardingConfig (Configuration)
  └── TutorialState (Active Tutorial State)
```

## Usage

```typescript
import { OnboardingEngine } from '@/lib/onboarding/onboarding-engine';

// Initialize for specific UI version
const engine = new OnboardingEngine('original');

// Start tutorial
await engine.startTutorial('basic-tour');

// Track step completion
await engine.completeStep('basic-tour', 'upload-file');

// Get next step
const nextStep = await engine.getNextStep('basic-tour');
```

## Events

Events are emitted for:

- `tutorial:started` - Tutorial begins
- `step:completed` - Step finished
- `step:skipped` - Step skipped
- `tutorial:completed` - Tutorial finished
- `tutorial:dismissed` - Tutorial dismissed
- `feature:unlocked` - New feature available
- `help:viewed` - Help content accessed
