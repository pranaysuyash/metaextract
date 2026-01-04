/**
 * Performance-Optimized Metadata Display Component
 * Uses React.memo, virtualization, and lazy loading for large datasets
 */

import React, { useState, useCallback, useMemo } from 'react';
import { FixedSizeList } from 'react-window';

interface MetadataItem {
  key: string;
  value: any;
  category: string;
  confidence: number;
}

interface OptimizedMetadataDisplayProps {
  metadata: Record<string, any>;
  onFilterChange?: (filters: any) => void;
}

// Memoized individual metadata item
const MemoizedMetadataItem = React.memo<{
  item: MetadataItem;
  onCategoryClick: (category: string) => void;
}>(({ item, onCategoryClick }) => {
  const valueDisplay = useMemo(() => {
    if (typeof item.value === 'object' && item.value !== null) {
      return JSON.stringify(item.value, null, 2);
    }
    return String(item.value);
  }, [item.value]);

  return (
    <div className="p-3 border-b border-gray-100 hover:bg-gray-50 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm truncate">{item.key}</span>
            <button
              onClick={() => onCategoryClick(item.category)}
              className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
            >
              {item.category}
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-1 break-all">{valueDisplay}</p>
        </div>
        <div className="flex-shrink-0">
          <div className={`w-2 h-2 rounded-full ${
            item.confidence > 0.8 ? 'bg-green-500' :
            item.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
          }`} />
        </div>
      </div>
    </div>
  );
});

MemoizedMetadataItem.displayName = 'MemoizedMetadataItem';

export const OptimizedMetadataDisplay: React.FC<OptimizedMetadataDisplayProps> = ({
  metadata,
  onFilterChange
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'key' | 'confidence'>('key');

  // Memoized metadata processing
  const processedMetadata = useMemo(() => {
    const items: MetadataItem[] = [];
    const categories = new Set<string>();

    Object.entries(metadata).forEach(([key, value]) => {
      if (value === null || value === undefined || value === {}) return;

      // Determine category based on key
      let category = 'other';
      if (key.includes('exif')) category = 'exif';
      else if (key.includes('gps')) category = 'gps';
      else if (key.includes('iptc')) category = 'iptc';
      else if (key.includes('xmp')) category = 'xmp';
      else if (key.includes('ai_')) category = 'ai';
      else if (key.includes('quality')) category = 'quality';

      categories.add(category);

      // Calculate confidence based on data quality
      let confidence = 1.0;
      if (value === '') confidence = 0.3;
      else if (typeof value === 'object') {
        const entries = Object.entries(value).length;
        confidence = Math.min(1.0, entries / 10);
      }

      items.push({
        key,
        value,
        category,
        confidence
      });
    });

    // Filter and sort
    let filtered = items.filter(item =>
      item.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(item.value).toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (selectedCategory) {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    filtered.sort((a, b) => {
      if (sortBy === 'confidence') {
        return b.confidence - a.confidence;
      }
      return a.key.localeCompare(b.key);
    });

    return {
      items: filtered,
      categories: Array.from(categories).sort()
    };
  }, [metadata, searchTerm, selectedCategory, sortBy]);

  // Callback memoization
  const handleCategoryClick = useCallback((category: string) => {
    setSelectedCategory(prev => prev === category ? null : category);
  }, []);

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  }, []);

  // Virtualized list item renderer
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <MemoizedMetadataItem
        item={processedMetadata.items[index]}
        onCategoryClick={handleCategoryClick}
      />
    </div>
  );

  return (
    <div className="space-y-4">
      {/* Search and Filter Controls */}
      <div className="flex gap-4 items-center">
        <input
          type="text"
          placeholder="Search metadata..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />

        <select
          value={selectedCategory || 'all'}
          onChange={(e) => setSelectedCategory(e.target.value === 'all' ? null : e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="all">All Categories</option>
          {processedMetadata.categories.map(cat => (
            <option key={cat} value={cat}>{cat.toUpperCase()}</option>
          ))}
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'key' | 'confidence')}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="key">Sort by Name</option>
          <option value="confidence">Sort by Confidence</option>
        </select>
      </div>

      {/* Results Summary */}
      <div className="text-sm text-gray-600">
        Showing {processedMetadata.items.length} metadata items
        {searchTerm && ` matching "${searchTerm}"`}
        {selectedCategory && ` in ${selectedCategory.toUpperCase()}`}
      </div>

      {/* Virtualized List for Performance */}
      {processedMetadata.items.length > 0 ? (
        <FixedSizeList
          height={600}
          itemCount={processedMetadata.items.length}
          itemSize={80}
          width="100%"
        >
          {Row}
        </FixedSizeList>
      ) : (
        <div className="text-center py-12 text-gray-500">
          No metadata found matching your criteria
        </div>
      )}
    </div>
  );
};

// Lazy-loaded heavy components
export const LazyMetadataCharts = React.lazy(() =>
  import('./metadata-charts').then(module => ({
    default: module.MetadataCharts
  }))
);

export const LazyMetadataExport = React.lazy(() =>
  import('./metadata-export').then(module => ({
    default: module.MetadataExport
  }))
);

// Performance monitoring hook
export function usePerformanceMonitor(componentName: string) {
  const [renderTime, setRenderTime] = useState<number>(0);

  React.useEffect(() => {
    const start = performance.now();

    return () => {
      const end = performance.now();
      setRenderTime(end - start);

      if (end - start > 100) {
        console.warn(`${componentName} slow render: ${(end - start).toFixed(2)}ms`);
      }
    };
  });

  return { renderTime, isSlow: renderTime > 100 };
}