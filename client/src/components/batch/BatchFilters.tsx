import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Filter, Calendar as CalendarIcon, FileText, Image, FileSpreadsheet, Database } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import type { DateRange } from 'react-day-picker';

interface BatchResult {
  id: string;
  filename: string;
  status: 'success' | 'error' | 'processing' | 'pending';
  extractionDate: string;
  fieldsExtracted: number;
  fileSize: number;
  fileType: string;
  authenticityScore?: number;
  metadata: Record<string, any>;
}

interface BatchFilters {
  status?: string;
  fileType?: string;
  dateRange?: { start: Date; end: Date };
  minFields?: number;
  maxFields?: number;
}

interface BatchFiltersProps {
  filters: BatchFilters;
  onFiltersChange: (filters: BatchFilters) => void;
  results: BatchResult[];
}

export const BatchFilters: React.FC<BatchFiltersProps> = ({ filters, onFiltersChange, results }) => {
  const [dateRange, setDateRange] = React.useState<DateRange | undefined>();

  // Get unique file types from results
  const fileTypes = React.useMemo(() => {
    const types = new Set<string>();
    results.forEach(result => {
      const mainType = result.fileType.split('/')[0];
      types.add(mainType);
    });
    return Array.from(types).sort();
  }, [results]);

  // Get field count range
  const fieldCountRange = React.useMemo(() => {
    if (results.length === 0) return { min: 0, max: 0 };
    const counts = results.map(r => r.fieldsExtracted);
    return {
      min: Math.min(...counts),
      max: Math.max(...counts),
    };
  }, [results]);

  const handleStatusChange = (status: string) => {
    onFiltersChange({ ...filters, status: status === 'all' ? undefined : status });
  };

  const handleFileTypeChange = (fileType: string) => {
    onFiltersChange({ ...filters, fileType: fileType === 'all' ? undefined : fileType });
  };

  const handleDateRangeSelect = (range: DateRange | undefined) => {
    setDateRange(range);
    if (range?.from && range?.to) {
      onFiltersChange({
        ...filters,
        dateRange: { start: range.from, end: range.to },
      });
    } else {
      onFiltersChange({ ...filters, dateRange: undefined });
    }
  };

  const handleMinFieldsChange = (value: string) => {
    const minFields = value === 'all' ? undefined : parseInt(value);
    onFiltersChange({ ...filters, minFields });
  };

  const handleMaxFieldsChange = (value: string) => {
    const maxFields = value === 'all' ? undefined : parseInt(value);
    onFiltersChange({ ...filters, maxFields });
  };

  const getFileTypeIcon = (type: string) => {
    switch (type) {
      case 'image': return <Image className="w-4 h-4" />;
      case 'application': return <FileSpreadsheet className="w-4 h-4" />;
      case 'text': return <FileText className="w-4 h-4" />;
      case 'video': return <Database className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getFileTypeLabel = (type: string) => {
    switch (type) {
      case 'image': return 'Images';
      case 'application': return 'Documents';
      case 'text': return 'Text Files';
      case 'video': return 'Videos';
      default: return type.charAt(0).toUpperCase() + type.slice(1);
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {/* Status Filter */}
      <Select value={filters.status || 'all'} onValueChange={handleStatusChange}>
        <SelectTrigger className="w-32">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Status</SelectItem>
          <SelectItem value="success">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
              Success
            </div>
          </SelectItem>
          <SelectItem value="error">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-red-500"></div>
              Error
            </div>
          </SelectItem>
          <SelectItem value="processing">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
              Processing
            </div>
          </SelectItem>
          <SelectItem value="pending">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              Pending
            </div>
          </SelectItem>
        </SelectContent>
      </Select>

      {/* File Type Filter */}
      <Select value={filters.fileType || 'all'} onValueChange={handleFileTypeChange}>
        <SelectTrigger className="w-40">
          <SelectValue placeholder="File Type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Types</SelectItem>
          {fileTypes.map(type => (
            <SelectItem key={type} value={type}>
              <div className="flex items-center gap-2">
                {getFileTypeIcon(type)}
                {getFileTypeLabel(type)}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Fields Range Filter */}
      <div className="flex items-center gap-2">
        <Select 
          value={filters.minFields?.toString() || 'all'} 
          onValueChange={handleMinFieldsChange}
        >
          <SelectTrigger className="w-28">
            <SelectValue placeholder="Min Fields" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Min: Any</SelectItem>
            <SelectItem value="0">0+</SelectItem>
            <SelectItem value="50">50+</SelectItem>
            <SelectItem value="100">100+</SelectItem>
            <SelectItem value="200">200+</SelectItem>
          </SelectContent>
        </Select>
        
        <span className="text-slate-400">to</span>
        
        <Select 
          value={filters.maxFields?.toString() || 'all'} 
          onValueChange={handleMaxFieldsChange}
        >
          <SelectTrigger className="w-28">
            <SelectValue placeholder="Max Fields" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Max: Any</SelectItem>
            <SelectItem value="50">50</SelectItem>
            <SelectItem value="100">100</SelectItem>
            <SelectItem value="200">200</SelectItem>
            <SelectItem value="500">500+</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Date Range Filter */}
      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline" className={cn(
            "w-48 justify-start text-left font-normal",
            !dateRange?.from && "text-muted-foreground"
          )}>
            <CalendarIcon className="mr-2 h-4 w-4" />
            {dateRange?.from ? (
              dateRange?.to ? (
                <>
                  {format(dateRange.from, "LLL dd, y")} -{" "}
                  {format(dateRange.to, "LLL dd, y")}
                </>
              ) : (
                format(dateRange.from, "LLL dd, y")
              )
            ) : (
              <span>Pick a date range</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={dateRange?.from}
            selected={dateRange}
            onSelect={handleDateRangeSelect}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>

      {/* Active Filters Display */}
      {(filters.status || filters.fileType || filters.dateRange || filters.minFields !== undefined || filters.maxFields !== undefined) && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400">Active:</span>
          {filters.status && (
            <Badge variant="secondary" className="gap-1">
              Status: {filters.status}
              <button
                onClick={() => handleStatusChange('all')}
                className="ml-1 hover:text-destructive"
              >
                ×
              </button>
            </Badge>
          )}
          {filters.fileType && (
            <Badge variant="secondary" className="gap-1">
              {getFileTypeLabel(filters.fileType)}
              <button
                onClick={() => handleFileTypeChange('all')}
                className="ml-1 hover:text-destructive"
              >
                ×
              </button>
            </Badge>
          )}
          {(filters.minFields !== undefined || filters.maxFields !== undefined) && (
            <Badge variant="secondary" className="gap-1">
              Fields: {filters.minFields || 0}-{filters.maxFields || '∞'}
              <button
                onClick={() => {
                  onFiltersChange({
                    ...filters,
                    minFields: undefined,
                    maxFields: undefined,
                  });
                }}
                className="ml-1 hover:text-destructive"
              >
                ×
              </button>
            </Badge>
          )}
          {filters.dateRange && (
            <Badge variant="secondary" className="gap-1">
              {format(filters.dateRange.start, "MMM dd")} - {format(filters.dateRange.end, "MMM dd")}
              <button
                onClick={() => {
                  setDateRange(undefined);
                  onFiltersChange({ ...filters, dateRange: undefined });
                }}
                className="ml-1 hover:text-destructive"
              >
                ×
              </button>
            </Badge>
          )}
        </div>
      )}
    </div>
  );
};
