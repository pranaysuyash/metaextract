# Vite Setup Refactor Summary

## File: `server/vite.ts`

### Issues Fixed

#### 1. **Hard-coded Path Resolution** ✅
- **Problem**: Long relative path chain repeated, fragile to directory structure changes
  ```typescript
  // Before
  const clientTemplate = path.resolve(
    import.meta.dirname,
    "..",
    "client",
    "index.html",
  );
  ```
- **Solution**: Resolved path once at module level as constant
  ```typescript
  const CLIENT_TEMPLATE_PATH = path.resolve(
    import.meta.dirname,
    '..',
    'client',
    'index.html'
  );
  ```
- **Benefits**: Single source of truth, DRY principle, easier to maintain

#### 2. **Fragile String Replacement** ✅
- **Problem**: Uses exact string matching, fails if HTML formatting changes
  ```typescript
  // Before - breaks with any whitespace or quote variation
  template.replace(`src="/src/main.tsx"`, `src="/src/main.tsx?v=${nanoid()}"`)
  ```
- **Solution**: Used regex pattern for flexible matching
  ```typescript
  const MAIN_SCRIPT_PATTERN = /src=(['"]?)\/src\/main\.tsx\1/;
  function injectVersionToken(template: string): string {
    const versionToken = nanoid();
    return template.replace(
      MAIN_SCRIPT_PATTERN,
      `src="/src/main.tsx?v=${versionToken}"`
    );
  }
  ```
- **Benefits**: Handles single quotes, double quotes, or no quotes; more robust

#### 3. **No Template Caching Strategy** ✅
- **Problem**: Reads entire HTML file from disk on every request
  - I/O overhead on every single request
  - No production optimization path
- **Solution**: Implemented optional in-memory caching with TTL
  ```typescript
  interface ViteSetupOptions {
    cacheTemplate?: boolean;
    cacheMaxAge?: number;
  }
  
  async function getTemplate(): Promise<string> {
    const now = Date.now();
    
    if (shouldCacheTemplate && 
        cachedTemplate && 
        now - cachedTemplate.timestamp < cacheMaxAge) {
      return cachedTemplate.content;
    }
    
    // Read from disk...
  }
  ```
- **Benefits**: Configurable caching, default 1-minute TTL, production-ready

#### 4. **Generic Error Handling** ✅
- **Problem**: Errors logged without context, inconsistent behavior
  ```typescript
  // Before - no error details logged
  catch (e) {
    vite.ssrFixStacktrace(e as Error);
    next(e);
  }
  ```
- **Solution**: Added proper error logging with context
  ```typescript
  catch (error) {
    const err = error as Error;
    viteLogger.error(`Failed to serve index.html: ${err.message}`);
    vite.ssrFixStacktrace(err);
    next(err);
  }
  ```
- **Benefits**: Better observability, aids in debugging, clear error messages

#### 5. **Missing Cache Invalidation** ✅
- **Problem**: Template cache never cleared, no way to bust cache during development
- **Solution**: Added `clearTemplateCache()` export
  ```typescript
  export function clearTemplateCache(): void {
    cachedTemplate = null;
  }
  ```
- **Benefits**: Development flexibility, testing support, explicit cache management

### New Exports

```typescript
export function clearTemplateCache(): void
```
- For cache invalidation during development or hot reloading

### New Function Signatures

```typescript
export async function setupVite(
  server: Server,
  app: Express,
  options?: ViteSetupOptions
)
```

### New Interfaces

```typescript
interface ViteSetupOptions {
  cacheTemplate?: boolean;
  cacheMaxAge?: number;
}

interface CachedTemplate {
  content: string;
  timestamp: number;
}
```

### Code Quality Improvements

| Aspect | Before | After |
|--------|--------|-------|
| Path resolution | Inline chain | Module constant `CLIENT_TEMPLATE_PATH` |
| Script injection | String matching | Regex pattern `MAIN_SCRIPT_PATTERN` |
| Template I/O | Every request | Optional caching with TTL |
| Error logging | Generic error | Contextual error message |
| Cache control | None | `clearTemplateCache()` export |
| Configuration | Hardcoded | `ViteSetupOptions` parameter |
| Code organization | Linear | Sections with clear comments |

### Usage Examples

**Development (no caching):**
```typescript
await setupVite(server, app);
```

**Production (with caching):**
```typescript
await setupVite(server, app, {
  cacheTemplate: true,
  cacheMaxAge: 60000 // 1 minute
});
```

**Force cache clear (hot reload):**
```typescript
clearTemplateCache();
```

### Backward Compatibility

✅ Fully backward compatible. Existing code works without changes:
```typescript
await setupVite(server, app); // Still works
```

New options are optional and default to development-safe behavior (no caching).

### Performance Impact

- **Development**: No change (caching disabled by default)
- **Production**: Potential 95%+ reduction in disk I/O if caching enabled
  - Assuming 1-minute TTL and reasonable request volume
  - Single template read per minute instead of per request

### Testing Recommendations

1. **Cache hits/misses**: Verify cache respects TTL
2. **Template variations**: Test with different quote styles in HTML
3. **Cache clearing**: Verify `clearTemplateCache()` works correctly
4. **Error logging**: Ensure errors are logged with context
5. **Production config**: Test with caching enabled under load
