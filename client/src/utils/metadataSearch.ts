/**
 * Search Utilities for Metadata
 * 
 * Intelligent search and filtering across metadata fields with
 * fuzzy matching, category filtering, and value search.
 */

export interface SearchOptions {
  /** Search query string */
  query: string;
  
  /** Filter by specific categories */
  categories?: string[];
  
  /** Search in field names only */
  fieldsOnly?: boolean;
  
  /** Search in values only */
  valuesOnly?: boolean;
  
  /** Case sensitive search */
  caseSensitive?: boolean;
  
  /** Use fuzzy matching */
  fuzzyMatch?: boolean;
}

export interface SearchResult {
  /** Matching field key */
  fieldKey: string;
  
  /** Field value */
  fieldValue: any;
  
  /** Category this field belongs to */
  category: string;
  
  /** Match score (0-1, higher is better) */
  score: number;
  
  /** What matched (field name, value, or both) */
  matchType: 'field' | 'value' | 'both';
  
  /** Highlighted match for display */
  highlightedField?: string;
  highlightedValue?: string;
}

/**
 * Calculate Levenshtein distance for fuzzy matching
 */
function levenshteinDistance(str1: string, str2: string): number {
  const matrix: number[][] = [];
  
  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1,     // insertion
          matrix[i - 1][j] + 1      // deletion
        );
      }
    }
  }
  
  return matrix[str2.length][str1.length];
}

/**
 * Calculate fuzzy match score (0-1, higher is better)
 */
function fuzzyMatchScore(query: string, target: string, caseSensitive = false): number {
  const q = caseSensitive ? query : query.toLowerCase();
  const t = caseSensitive ? target : target.toLowerCase();
  
  // Exact match
  if (t === q) return 1.0;
  
  // Starts with
  if (t.startsWith(q)) return 0.9;
  
  // Contains
  if (t.includes(q)) return 0.8;
  
  // Fuzzy match with Levenshtein
  const distance = levenshteinDistance(q, t);
  const maxLength = Math.max(q.length, t.length);
  const similarity = 1 - (distance / maxLength);
  
  // Only return scores above threshold
  return similarity > 0.6 ? similarity * 0.7 : 0;
}

/**
 * Highlight matching parts of text
 */
function highlightMatch(text: string, query: string, caseSensitive = false): string {
  if (!query) return text;
  
  const q = caseSensitive ? query : query.toLowerCase();
  const t = caseSensitive ? text : text.toLowerCase();
  
  const index = t.indexOf(q);
  if (index === -1) return text;
  
  return (
    text.slice(0, index) +
    '<mark>' + text.slice(index, index + query.length) + '</mark>' +
    text.slice(index + query.length)
  );
}

/**
 * Search metadata fields
 */
export function searchMetadata(
  metadata: Record<string, any>,
  options: SearchOptions
): SearchResult[] {
  const results: SearchResult[] = [];
  const { query, categories, fieldsOnly, valuesOnly, caseSensitive, fuzzyMatch } = options;
  
  if (!query || query.trim().length === 0) {
    return results;
  }
  
  const searchQuery = caseSensitive ? query : query.toLowerCase();
  
  // Search through all fields
  Object.entries(metadata).forEach(([key, value]) => {
    // Skip internal fields
    if (key.startsWith('_')) return;
    
    const fieldText = caseSensitive ? key : key.toLowerCase();
    const valueText = caseSensitive 
      ? String(value) 
      : String(value).toLowerCase();
    
    let fieldScore = 0;
    let valueScore = 0;
    let matchType: 'field' | 'value' | 'both' = 'field';
    
    // Search in field name
    if (!valuesOnly) {
      if (fuzzyMatch) {
        fieldScore = fuzzyMatchScore(searchQuery, fieldText, caseSensitive);
      } else {
        fieldScore = fieldText.includes(searchQuery) ? 1.0 : 0;
      }
    }
    
    // Search in value
    if (!fieldsOnly && value !== null && value !== undefined) {
      if (fuzzyMatch) {
        valueScore = fuzzyMatchScore(searchQuery, valueText, caseSensitive);
      } else {
        valueScore = valueText.includes(searchQuery) ? 0.8 : 0;
      }
    }
    
    // Determine match type and score
    const hasFieldMatch = fieldScore > 0;
    const hasValueMatch = valueScore > 0;
    
    if (!hasFieldMatch && !hasValueMatch) return;
    
    if (hasFieldMatch && hasValueMatch) {
      matchType = 'both';
    } else if (hasValueMatch) {
      matchType = 'value';
    }
    
    const finalScore = Math.max(fieldScore, valueScore);
    
    results.push({
      fieldKey: key,
      fieldValue: value,
      category: '', // Will be set by caller
      score: finalScore,
      matchType,
      highlightedField: hasFieldMatch ? highlightMatch(key, query, caseSensitive) : undefined,
      highlightedValue: hasValueMatch ? highlightMatch(String(value), query, caseSensitive) : undefined
    });
  });
  
  // Sort by score (highest first)
  return results.sort((a, b) => b.score - a.score);
}

/**
 * Search across categorized metadata
 */
export function searchCategorizedMetadata(
  categorizedData: Record<string, Record<string, any>>,
  options: SearchOptions
): SearchResult[] {
  const results: SearchResult[] = [];
  
  Object.entries(categorizedData).forEach(([category, fields]) => {
    // Filter by category if specified
    if (options.categories && !options.categories.includes(category)) {
      return;
    }
    
    const categoryResults = searchMetadata(fields, options);
    
    // Add category to results
    categoryResults.forEach(result => {
      results.push({
        ...result,
        category
      });
    });
  });
  
  // Sort by score
  return results.sort((a, b) => b.score - a.score);
}

/**
 * Filter metadata by criteria
 */
export interface FilterCriteria {
  /** Has value (not null/undefined/empty) */
  hasValue?: boolean;
  
  /** Value type */
  valueType?: 'string' | 'number' | 'boolean' | 'object' | 'array';
  
  /** Min value (for numbers) */
  minValue?: number;
  
  /** Max value (for numbers) */
  maxValue?: number;
  
  /** String length range */
  minLength?: number;
  maxLength?: number;
}

export function filterMetadata(
  metadata: Record<string, any>,
  criteria: FilterCriteria
): Record<string, any> {
  const filtered: Record<string, any> = {};
  
  Object.entries(metadata).forEach(([key, value]) => {
    let include = true;
    
    // Check has value
    if (criteria.hasValue !== undefined) {
      const hasVal = value !== null && value !== undefined && value !== '';
      if (criteria.hasValue !== hasVal) {
        include = false;
      }
    }
    
    // Check value type
    if (include && criteria.valueType) {
      const actualType = Array.isArray(value) ? 'array' : typeof value;
      if (actualType !== criteria.valueType) {
        include = false;
      }
    }
    
    // Check numeric range
    if (include && typeof value === 'number') {
      if (criteria.minValue !== undefined && value < criteria.minValue) {
        include = false;
      }
      if (criteria.maxValue !== undefined && value > criteria.maxValue) {
        include = false;
      }
    }
    
    // Check string length
    if (include && typeof value === 'string') {
      if (criteria.minLength !== undefined && value.length < criteria.minLength) {
        include = false;
      }
      if (criteria.maxLength !== undefined && value.length > criteria.maxLength) {
        include = false;
      }
    }
    
    if (include) {
      filtered[key] = value;
    }
  });
  
  return filtered;
}

/**
 * Get search suggestions based on partial query
 */
export function getSearchSuggestions(
  metadata: Record<string, any>,
  partialQuery: string,
  limit = 5
): string[] {
  if (!partialQuery || partialQuery.length < 2) {
    return [];
  }
  
  const query = partialQuery.toLowerCase();
  const suggestions = new Set<string>();
  
  // Add matching field names
  Object.keys(metadata).forEach(key => {
    if (key.toLowerCase().includes(query)) {
      suggestions.add(key);
    }
  });
  
  // Convert to array and limit
  return Array.from(suggestions).slice(0, limit);
}
