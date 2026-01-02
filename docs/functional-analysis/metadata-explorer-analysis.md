# metadata-explorer.tsx - Functional Issue Analysis

**File Path:** `client/src/components/metadata-explorer.tsx`
**Lines of Code:** 1,076
**Component Type:** React Component (Three-Pane Metadata Explorer)
**Analysis Date:** 2026-01-02

---

## 🔴 Critical Issues (3)

### 1. XSS Vulnerability via `dangerouslySetInnerHTML`
**Location:** Lines 256-263, 583-590, 662-669
**Severity:** CRITICAL
**Type:** Security Vulnerability

```tsx
const HighlightedText = ({ text, className }: { text: string; className?: string }) => {
  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: text }}  // ❌ UNSAFE
    />
  );
};
```

**Issue:** Using `dangerouslySetInnerHTML` without sanitization allows XSS attacks. Malicious scripts can be injected through search queries or metadata values.

**Attack Vector:**
```tsx
// Malicious metadata value
const maliciousField = {
  key: 'description',
  value: '<script>alert("xss")</script>',
  category: 'Test'
};

// After search highlighting, becomes:
const highlightedText = '<mark><script>alert("xss")</script></mark>';
```

**Impact:**
- Remote code execution in user context
- Session hijacking
- Data theft

**Recommended Fix:**
```tsx
import DOMPurify from 'dompurify';

const HighlightedText = ({ text, className }: { text: string; className?: string }) => {
  const sanitizedHtml = DOMPurify.sanitize(text, {
    ALLOWED_TAGS: ['mark'],
    ALLOWED_ATTR: []
  });

  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
    />
  );
};
```

---

### 2. Unsafe Type Casting in Metadata Search
**Location:** Lines 460-476
**Severity:** HIGH
**Type:** Type Safety

```tsx
const matchedFields = results.map(result => {
  const originalField = fieldMap.get(result.fieldKey);  // ❌ No null check
  if (!originalField) return null;

  return {
    ...originalField,
    highlightedKey: result.highlightedField,
    highlightedValue: result.highlightedValue
  };
}).filter(isMetadataField);  // ❌ May still pass invalid objects
```

**Issue:** Direct type casting without proper validation can lead to runtime errors when `result.fieldKey` doesn't match expected format.

**Impact:**
- Runtime crashes on invalid search results
- Type safety violations
- Unpredictable UI behavior

**Recommended Fix:**
```tsx
const matchedFields = results
  .map(result => {
    const originalField = fieldMap.get(result.fieldKey);
    if (!originalField) return null;

    // Validate structure before spreading
    if (!isMetadataField(originalField)) return null;

    return {
      ...originalField,
      highlightedKey: result.highlightedField,
      highlightedValue: result.highlightedValue
    };
  })
  .filter((field): field is MetadataField => field !== null && isMetadataField(field));
```

---

### 3. Missing Error Handling for User Preferences
**Location:** Lines 374-425
**Severity:** HIGH
**Type:** Error Handling

```tsx
const [expandedCategories, setExpandedCategories] = useState<string[]>(() => {
  const prefs = loadPreferences();  // ❌ No try-catch
  const expanded = prefs.expandedCategories;
  // ... processing logic
});
```

**Issue:** No error handling for corrupted preferences or localStorage unavailability.

**Impact:**
- Application crashes on corrupted data
- Poor user experience in restricted environments
- No graceful degradation

**Recommended Fix:**
```tsx
const [expandedCategories, setExpandedCategories] = useState<string[]>(() => {
  try {
    const prefs = loadPreferences();
    if (!prefs || typeof prefs !== 'object') return [];

    const expanded = prefs.expandedCategories;
    // ... rest of logic
  } catch (error) {
    logger.warn('Failed to load user preferences:', error);
    return [];
  }
});
```

---

## ⚡ Performance Issues (4)

### 4. Memory Leak Potential in Search Effect
**Location:** Lines 489-493
**Severity:** MEDIUM
**Type:** Memory Management

```tsx
useEffect(() => {
  if (searchQuery.trim() && visibleCategories.length > 0) {
    setExpandedCategories(visibleCategories.map(c => c.name));  // ❌ No cleanup
  }
}, [searchQuery, visibleCategories.length]);
```

**Issue:** Expensive operations on every keystroke without debouncing or cleanup.

**Impact:**
- Performance degradation on large datasets
- Unnecessary re-renders
- Memory accumulation

**Recommended Fix:**
```tsx
import { useMemo } from 'react';
import { debounce } from 'lodash';

const debouncedSetExpanded = useMemo(
  () => debounce((categories: string[]) => {
    setExpandedCategories(categories);
  }, 300),
  []
);

useEffect(() => {
  if (searchQuery.trim() && visibleCategories.length > 0) {
    debouncedSetExpanded(visibleCategories.map(c => c.name));
  }

  return () => {
    debouncedSetExpanded.cancel();
  };
}, [searchQuery, visibleCategories.length, debouncedSetExpanded]);
```

---

### 5. Missing Virtualization for Large Lists
**Location:** Lines 283-291, 428-486
**Severity:** MEDIUM
**Type:** Performance

```tsx
{filteredFiles.map((file) => (  // ❌ No virtualization
  <button key={file.id} onClick={() => onFileSelect(file.id)}>
    {/* file content */}
  </button>
))}
```

**Issue:** Renders all files/fields without virtualization, causing performance issues with large datasets.

**Impact:**
- Slow rendering with 1000+ items
- Memory issues
- Poor scrolling performance

**Recommended Fix:**
```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

const fileVirtualizer = useVirtualizer({
  count: filteredFiles.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 80,
  overscan: 5
});
```

---

### 6. Inefficient Search Without Debouncing
**Location:** Lines 449-483
**Severity:** MEDIUM
**Type:** Performance

```tsx
const visibleCategories = useMemo(() => {
  if (!file) return [];

  // Apply active search
  if (searchQuery.trim()) {  // ❌ Runs on every keystroke
    return categories.map(category => {
      const results = searchMetadata(categoryData, {
        query: searchQuery,
        fuzzyMatch: true,
        caseSensitive: false
      });
      // ... expensive operations
    });
  }
}, [file, viewMode, searchQuery]);  // ❌ searchQuery triggers recompute
```

**Issue:** Search runs on every keystroke without debouncing.

**Impact:**
- UI freezes during typing
- Excessive computations
- Poor user experience

---

### 7. Unnecessary Re-renders Due to Complex Dependencies
**Location:** Lines 856-903
**Severity:** LOW
**Type:** Performance

```tsx
const [internalViewMode, setInternalViewMode] = useState<
  'simple' | 'advanced' | 'raw'
>(viewMode ?? 'advanced');  // ❌ Complex dual-state management
```

**Issue:** Complex controlled/uncontrolled pattern causing unnecessary re-renders.

**Impact:**
- Performance overhead
- State synchronization issues
- Difficult to maintain

---

## 🛠️ Error Handling Issues (3)

### 8. Clipboard API Error Handling Missing
**Location:** Line 250
**Severity:** MEDIUM
**Type:** Error Handling

```tsx
function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text);  // ❌ No error handling
}
```

**Issue:** No error handling for clipboard operations that may fail in non-secure contexts.

**Impact:**
- Unhandled exceptions
- Poor UX in restricted environments
- No user feedback

**Recommended Fix:**
```tsx
async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    logger.warn('Failed to copy to clipboard:', error);
    // Fallback for older browsers
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      return true;
    } catch (fallbackError) {
      logger.error('Clipboard copy failed:', fallbackError);
      return false;
    }
  }
}
```

---

### 9. Missing Null Checks in GPS Display
**Location:** Lines 766-795
**Severity:** MEDIUM
**Type:** Error Handling

```tsx
{isGPS && file?.rawMetadata?.gps && (
  <Card>
    <CardContent>
      <div className='space-y-2'>
        {file.rawMetadata.gps.google_maps_url && (  // ❌ No validation
          <a href={file.rawMetadata.gps.google_maps_url}>  // ❌ Potential XSS
            Open in Google Maps
          </a>
        )}
```

**Issue:** Incomplete validation of GPS data structure and potential XSS in URL rendering.

**Impact:**
- Runtime crashes on malformed GPS data
- XSS through malicious URLs
- Broken location features

---

### 10. Unsafe HTML Rendering in Tooltips
**Location:** Lines 592-658
**Severity:** MEDIUM
**Type:** Security

```tsx
<TooltipContent className='max-w-sm'>
  {(() => {
    const explanation = getFieldExplanation(field.key);  // ❌ No validation
    if (explanation) {
      return (
        <div className='space-y-2'>
          <p className='font-semibold'>{explanation.title}</p>  // ❌ Unsafe text
          <p className='text-sm mt-1'>{explanation.description}</p>  // ❌ Unsafe text
```

**Issue:** No sanitization of tooltip content, potential XSS through field explanations.

---

## 🧪 Code Quality Issues (2)

### 11. Complex State Management Pattern
**Location:** Lines 856-903
**Severity:** LOW
**Type:** Code Quality

```tsx
const activeViewMode = isViewModeControlled ? viewMode : internalViewMode;
const lastEmittedViewModeRef = useRef<'simple' | 'advanced' | 'raw'>(
  activeViewMode
);
```

**Issue:** Overly complex controlled/uncontrolled component pattern.

**Impact:**
- Difficult to maintain
- Potential state desynchronization
- Hard to test

---

### 12. Missing Accessibility Features
**Location:** Throughout component
**Severity:** LOW
**Type:** Accessibility

**Issues:**
- Missing ARIA labels on interactive elements
- No keyboard navigation for resizable panels
- Incomplete focus management
- Missing screen reader announcements

**Impact:**
- Poor accessibility for keyboard users
- Screen reader compatibility issues
- Non-compliant with WCAG guidelines

---

## 📊 Summary

| Severity | Count | Type |
|----------|-------|------|
| Critical | 1 | Security |
| High | 2 | Security, Type Safety |
| Medium | 6 | Performance, Error Handling |
| Low | 3 | Code Quality, Accessibility |

### Priority Actions

1. **Immediate (Critical/High)**
   - Fix XSS vulnerability in `HighlightedText` component
   - Add proper input sanitization
   - Fix unsafe type casting

2. **Short-term (Medium)**
   - Add error handling for user preferences
   - Implement search debouncing
   - Add clipboard error handling

3. **Long-term (Low)**
   - Refactor state management
   - Improve accessibility
   - Add virtualization for large datasets