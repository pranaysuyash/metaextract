# Forensic Analysis Components Guide

This guide documents the forensic analysis components for the V2 results system, providing advanced authenticity verification, manipulation detection, and AI generation analysis.

## Overview

The forensic analysis module provides a comprehensive suite of components for displaying advanced metadata analysis results, including:

- **Authenticity scoring** with visual indicators
- **Steganography detection** (hidden data analysis)
- **Manipulation detection** (image editing identification)
- **AI generation detection** (synthetic content identification)
- **Confidence visualization** with progress bars and gauges
- **Interactive exploration** with tabbed interfaces

## Components

### 1. ForensicAnalysis

Main component that displays comprehensive forensic analysis results with interactive tabs.

```tsx
import { ForensicAnalysis } from '@/components/v2-results';

<ForensicAnalysis
  steganography={steganographyData}
  manipulation={manipulationData}
  aiDetection={aiDetectionData}
  authenticityScore={85}
  onReanalyze={handleReanalyze}
  className="custom-class"
/>
```

**Props:**
- `steganography`: SteganographyAnalysis data
- `manipulation`: ManipulationAnalysis data  
- `aiDetection`: AIDetection data
- `authenticityScore`: Overall authenticity score (0-100)
- `onReanalyze`: Callback for re-analysis
- `className`: Optional CSS classes

**Features:**
- Forensic score gauge visualization
- Tabbed interface (Overview, Steganography, Manipulation, AI Detection)
- Risk assessment dashboard
- Detailed findings breakdown
- Interactive confidence bars
- Export/report functionality

### 2. AuthenticityBadge

Flexible badge component for displaying authenticity scores with multiple variants.

```tsx
import { AuthenticityBadge } from '@/components/v2-results';

// Default badge
<AuthenticityBadge score={85} />

// Compact variant
<AuthenticityBadge score={85} variant="compact" />

// Detailed variant with confidence
<AuthenticityBadge score={85} variant="detailed" showConfidence={true} />

// Custom label
<AuthenticityBadge score={85} label="Verified" />
```

**Props:**
- `score`: Authenticity score (0-100)
- `label`: Custom label text
- `showIcon`: Show/hide icon (default: true)
- `variant`: 'default' | 'outline' | 'minimal' | 'compact' | 'detailed'
- `size`: 'sm' | 'md' | 'lg'
- `showConfidence`: Show confidence percentage
- `animated`: Enable animations
- `className`: Optional CSS classes

**Color Coding:**
- 80-100%: Green (Authentic)
- 60-79%: Yellow (Questionable)
- 0-59%: Red (Suspicious)

### 3. ForensicConfidenceIndicator

Specialized indicator for different types of forensic confidence.

```tsx
import { ForensicConfidenceIndicator } from '@/components/v2-results';

// Authenticity indicator
<ForensicConfidenceIndicator confidence={85} type="authenticity" />

// Manipulation risk indicator
<ForensicConfidenceIndicator confidence={75} type="manipulation" />

// AI detection indicator
<ForensicConfidenceIndicator confidence={60} type="ai-detection" />
```

**Props:**
- `confidence`: Confidence score (0-100)
- `type`: 'authenticity' | 'manipulation' | 'ai-detection'
- `size`: 'sm' | 'md' | 'lg'
- `showLabel`: Show/hide label text

### 4. KeyFindings (Enhanced)

Enhanced key findings component with forensic integration.

```tsx
import { KeyFindings } from '@/components/v2-results';

<KeyFindings
  findings={keyFindingsData}
  forensicScore={85}
  forensicAnalysis={forensicData}
  showForensicIndicators={true}
  compact={false}
  className="custom-class"
/>
```

**Props:**
- `findings`: KeyFindings data
- `forensicScore`: Overall forensic score
- `forensicAnalysis`: Forensic analysis data
- `showForensicIndicators`: Show forensic badges
- `compact`: Compact layout mode
- `className`: Optional CSS classes

### 5. ProgressiveDisclosure (Enhanced)

Enhanced progressive disclosure with forensic analysis tab.

```tsx
import { ProgressiveDisclosure } from '@/components/v2-results';

<ProgressiveDisclosure
  data={{
    keyFindings: keyFindings,
    quickDetails: quickDetails,
    location: locationData,
    advancedMetadata: metadata,
    forensicAnalysis: forensicData
  }}
  showForensicAnalysis={true}
  defaultTab="overview"
  className="custom-class"
/>
```

**Props:**
- `data`: ProgressiveDisclosureData with forensicAnalysis
- `showForensicAnalysis`: Show forensic tab
- `defaultTab`: Initial active tab
- `className`: Optional CSS classes

### 6. ForensicDemo

Interactive demo component showcasing forensic analysis capabilities.

```tsx
import { ForensicDemo } from '@/components/v2-results';

<ForensicDemo
  defaultScenario="authentic"
  showControls={true}
  showComparison={true}
  className="custom-class"
/>
```

**Props:**
- `defaultScenario`: 'authentic' | 'suspicious' | 'questionable'
- `showControls`: Show scenario controls
- `showComparison`: Show comparison view
- `className`: Optional CSS classes

## Data Types

### SteganographyAnalysis
```typescript
interface SteganographyAnalysis {
  detected: boolean;
  confidence: number;
  methodsChecked: string[];
  findings: string[];
  details?: string;
}
```

### ManipulationAnalysis
```typescript
interface ManipulationAnalysis {
  detected: boolean;
  confidence: number;
  indicators: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high';
    description: string;
    confidence: number;
  }>;
  originalityScore?: number;
}
```

### AIDetection
```typescript
interface AIDetection {
  aiGenerated: boolean;
  confidence: number;
  modelHints: string[];
  detectionMethods: string[];
}
```

## Integration Examples

### Basic Integration
```tsx
import { ForensicAnalysis, AuthenticityBadge } from '@/components/v2-results';

function ResultsPage({ metadata }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2>Forensic Analysis</h2>
        <AuthenticityBadge score={metadata.forensicScore} />
      </div>
      
      <ForensicAnalysis
        steganography={metadata.forensic?.steganography}
        manipulation={metadata.forensic?.manipulation}
        aiDetection={metadata.forensic?.aiDetection}
        authenticityScore={metadata.forensicScore}
      />
    </div>
  );
}
```

### Full Integration with Progressive Disclosure
```tsx
import { ProgressiveDisclosure } from '@/components/v2-results';

function ResultsV2Page({ metadata }) {
  const data = {
    keyFindings: extractKeyFindings(metadata),
    quickDetails: extractQuickDetails(metadata),
    location: extractLocation(metadata),
    advancedMetadata: metadata,
    forensicAnalysis: metadata.forensic
  };

  return (
    <ProgressiveDisclosure
      data={data}
      showForensicAnalysis={true}
      defaultTab="overview"
    />
  );
}
```

### Mobile Integration
```tsx
import { ProgressiveDisclosureMobile } from '@/components/v2-results';

function MobileResultsPage({ metadata }) {
  const data = {
    keyFindings: extractKeyFindings(metadata),
    quickDetails: extractQuickDetails(metadata),
    location: extractLocation(metadata),
    forensicAnalysis: metadata.forensic
  };

  return (
    <ProgressiveDisclosureMobile
      data={data}
      showForensicAnalysis={true}
    />
  );
}
```

## Styling and Theming

### Dark Mode Support
All components support dark mode through Tailwind CSS classes:
- `dark:bg-slate-900` for dark backgrounds
- `dark:text-white` for dark text
- `dark:border-slate-700` for dark borders

### Responsive Design
Components are fully responsive with:
- Mobile-first approach
- Breakpoint-specific layouts
- Touch-friendly interactions
- Collapsible sections for mobile

### Custom Styling
Components accept `className` props for custom styling:
```tsx
<ForensicAnalysis 
  className="custom-forensic-class"
  // ... props
/>
```

## Performance Considerations

### Lazy Loading
Forensic analysis components are designed for lazy loading:
- Heavy computations are deferred
- Progressive disclosure reduces initial load
- Tabs load content on demand

### Memoization
Components use React.memo for performance:
- Prevents unnecessary re-renders
- Optimizes for frequent updates
- Maintains smooth animations

### Virtual Scrolling
For large datasets, consider virtual scrolling:
- Implement windowing for long lists
- Use pagination for extensive findings
- Consider infinite scroll for historical data

## Accessibility

### ARIA Labels
All interactive elements include ARIA labels:
- Buttons have descriptive labels
- Progress bars include value text
- Tabs are keyboard navigable

### Keyboard Navigation
Full keyboard support:
- Tab navigation through components
- Enter/Space for activation
- Arrow keys for tab navigation

### Screen Reader Support
Comprehensive screen reader support:
- Semantic HTML structure
- Descriptive text alternatives
- Live regions for updates

## Testing

### Component Testing
```tsx
import { render, screen } from '@testing-library/react';
import { ForensicAnalysis } from '@/components/v2-results';

test('renders forensic analysis', () => {
  render(<ForensicAnalysis authenticityScore={85} />);
  expect(screen.getByText('Forensic Analysis')).toBeInTheDocument();
});
```

### Integration Testing
```tsx
import { ProgressiveDisclosure } from '@/components/v2-results';

test('integrates with key findings', () => {
  const data = {
    keyFindings: mockKeyFindings,
    quickDetails: mockQuickDetails,
    forensicAnalysis: mockForensicData
  };
  
  render(<ProgressiveDisclosure data={data} />);
  expect(screen.getByText('Forensic')).toBeInTheDocument();
});
```

## Best Practices

### Data Validation
Always validate forensic data before rendering:
```typescript
const hasForensicData = !!(forensic?.steganography || forensic?.manipulation || forensic?.aiDetection);
```

### Error Handling
Handle missing or invalid data gracefully:
```tsx
{forensicData ? (
  <ForensicAnalysis {...forensicData} />
) : (
  <div>No forensic analysis available</div>
)}
```

### Performance Optimization
Use appropriate variants for different contexts:
- `compact` for lists and tables
- `detailed` for main displays
- `minimal` for subtle indicators

### User Experience
Provide clear feedback and controls:
- Show analysis confidence levels
- Include re-analysis options
- Offer export capabilities
- Provide educational content

## Troubleshooting

### Common Issues

1. **Components not rendering**: Check data structure matches expected interfaces
2. **Styling issues**: Ensure Tailwind CSS is properly configured
3. **Type errors**: Verify TypeScript interfaces are correctly imported
4. **Performance issues**: Consider memoization and lazy loading

### Debug Mode
Enable debug logging:
```tsx
<ForensicAnalysis 
  debug={true}
  // ... props
/>
```

## Future Enhancements

### Planned Features
- Batch analysis support
- Historical trend analysis
- Custom detection algorithms
- Export to forensic formats
- Integration with external tools

### API Extensions
- Webhook notifications
- Real-time analysis updates
- Custom confidence thresholds
- Advanced filtering options

---

For additional support and examples, refer to the component test files and demo implementations.