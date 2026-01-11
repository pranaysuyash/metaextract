// client/src/components/viz/PremiumTimeline.tsx
import React, {
  useState,
  useRef,
  useEffect,
  useMemo,
  useCallback,
} from 'react';
import {
  Calendar,
  Edit3,
  Eye,
  FileText,
  Camera,
  ZoomIn,
  ZoomOut,
  Clock,
  Search,
  Filter,
  Moon,
  Sun,
  Download,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Layers,
  ArrowUpDown,
  BarChart3,
  FileImage,
  FileType,
  File,
  X,
  Check,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface TimelineEvent {
  id: string;
  type: 'taken' | 'created' | 'modified' | 'accessed';
  date: Date;
  file: FileData;
}

interface FileData {
  id: number;
  filename: string;
  type: 'image' | 'document' | 'text' | 'video' | 'audio';
  icon: React.ComponentType<{ className?: string }>;
  created: Date;
  modified: Date;
  accessed: Date;
  dateTaken?: Date;
  size: string;
  sizeBytes: number;
  dimensions?: string;
  pages?: number;
  location?: string;
  camera?: string;
  author?: string;
  tags?: string[];
}

interface PremiumTimelineProps {
  files?: FileData[];
  onFileSelect?: (file: FileData) => void;
}

const defaultFiles: FileData[] = [
  {
    id: 1,
    filename: 'summer_vacation_2024.jpg',
    type: 'image',
    icon: FileImage,
    created: new Date('2024-07-15T14:30:00'),
    modified: new Date('2024-08-22T09:15:00'),
    accessed: new Date('2025-01-03T16:45:00'),
    dateTaken: new Date('2024-07-15T14:28:30'),
    size: '4.2 MB',
    sizeBytes: 4404019,
    dimensions: '4032x3024',
    location: 'Maldives',
    camera: 'iPhone 15 Pro',
    tags: ['vacation', 'beach', 'summer'],
  },
  {
    id: 2,
    filename: 'project_report.pdf',
    type: 'document',
    icon: FileType,
    created: new Date('2024-09-10T10:00:00'),
    modified: new Date('2024-12-15T14:30:00'),
    accessed: new Date('2025-01-04T11:20:00'),
    size: '1.8 MB',
    sizeBytes: 1887436,
    pages: 24,
    author: 'John Doe',
    tags: ['work', 'report', 'Q4'],
  },
  {
    id: 3,
    filename: 'meeting_notes.txt',
    type: 'text',
    icon: FileText,
    created: new Date('2024-11-20T09:00:00'),
    modified: new Date('2024-11-20T17:45:00'),
    accessed: new Date('2025-01-02T08:30:00'),
    size: '12 KB',
    sizeBytes: 12288,
    tags: ['meeting', 'notes'],
  },
  {
    id: 4,
    filename: 'family_photo.jpg',
    type: 'image',
    icon: FileImage,
    created: new Date('2024-12-25T18:00:00'),
    modified: new Date('2024-12-25T18:00:00'),
    accessed: new Date('2025-01-04T20:15:00'),
    dateTaken: new Date('2024-12-25T17:58:00'),
    size: '3.8 MB',
    sizeBytes: 3984588,
    dimensions: '3840x2160',
    location: 'Home',
    camera: 'Canon EOS R5',
    tags: ['family', 'christmas', 'holiday'],
  },
  {
    id: 5,
    filename: 'presentation.pptx',
    type: 'document',
    icon: FileType,
    created: new Date('2024-10-05T08:00:00'),
    modified: new Date('2024-11-28T16:30:00'),
    accessed: new Date('2025-01-03T09:00:00'),
    size: '5.2 MB',
    sizeBytes: 5452595,
    pages: 32,
    author: 'Jane Smith',
    tags: ['presentation', 'work', 'Q3'],
  },
  {
    id: 6,
    filename: 'budget_2024.xlsx',
    type: 'document',
    icon: File,
    created: new Date('2024-01-15T10:00:00'),
    modified: new Date('2024-12-30T15:45:00'),
    accessed: new Date('2025-01-05T08:00:00'),
    size: '856 KB',
    sizeBytes: 876544,
    author: 'Finance Team',
    tags: ['budget', 'finance', '2024'],
  },
];

const dateTypeInfo: Record<
  string,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    textColor: string;
    bgLight: string;
    border: string;
    ring: string;
  }
> = {
  taken: {
    label: 'Date Taken',
    icon: Camera,
    color: 'bg-purple-500 dark:bg-purple-600',
    textColor: 'text-purple-500',
    bgLight: 'bg-purple-50 dark:bg-purple-900/30',
    border: 'border-purple-200 dark:border-purple-700',
    ring: 'ring-purple-400',
  },
  created: {
    label: 'Created',
    icon: FileText,
    color: 'bg-blue-500 dark:bg-blue-600',
    textColor: 'text-blue-500',
    bgLight: 'bg-blue-50 dark:bg-blue-900/30',
    border: 'border-blue-200 dark:border-blue-700',
    ring: 'ring-blue-400',
  },
  modified: {
    label: 'Modified',
    icon: Edit3,
    color: 'bg-amber-500 dark:bg-amber-600',
    textColor: 'text-amber-500',
    bgLight: 'bg-amber-50 dark:bg-amber-900/30',
    border: 'border-amber-200 dark:border-amber-700',
    ring: 'ring-amber-400',
  },
  accessed: {
    label: 'Last Accessed',
    icon: Eye,
    color: 'bg-green-500 dark:bg-green-600',
    textColor: 'text-green-500',
    bgLight: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-200 dark:border-green-700',
    ring: 'ring-green-400',
  },
};

function formatDate(date: Date, format: 'full' | 'short' = 'full'): string {
  if (format === 'short') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatRelative(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1073741824) return `${(bytes / 1048576).toFixed(1)} MB`;
  return `${(bytes / 1073741824).toFixed(2)} GB`;
}

export function PremiumTimeline({
  files = defaultFiles,
  onFileSelect,
}: PremiumTimelineProps) {
  const [darkMode, setDarkMode] = useState(false);
  const [fileMode, setFileMode] = useState<'single' | 'all'>('single');
  const [selectedFileIdx, setSelectedFileIdx] = useState(0);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, offset: 0 });
  const [hoveredPoint, setHoveredPoint] = useState<string | null>(null);
  const [selectedPoints, setSelectedPoints] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<{
    types: Array<'taken' | 'created' | 'modified' | 'accessed'>;
    fileTypes: Array<'image' | 'document' | 'text'>;
  }>({
    types: ['taken', 'created', 'modified', 'accessed'],
    fileTypes: ['image', 'document', 'text'],
  });
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [currentPlayIndex, setCurrentPlayIndex] = useState(0);
  const [showStats, setShowStats] = useState(false);
  const [groupBy, setGroupBy] = useState<
    'none' | 'day' | 'week' | 'month' | 'year'
  >('none');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [detailModal, setDetailModal] = useState<TimelineEvent | null>(null);
  const [dateRangeStart, setDateRangeStart] = useState('');
  const [dateRangeEnd, setDateRangeEnd] = useState('');
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [compareFiles, setCompareFiles] = useState([0, 1]);

  const timelineRef = useRef<HTMLDivElement>(null);
  const playIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const allTimelinePoints: TimelineEvent[] = useMemo(() => {
    const points: TimelineEvent[] = [];
    const filesToProcess =
      fileMode === 'single' ? [files[selectedFileIdx]] : files;

    filesToProcess.forEach(file => {
      if (
        !filters.fileTypes.includes(file.type as 'image' | 'document' | 'text')
      )
        return;
      if (
        searchQuery &&
        !file.filename.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !file.tags?.some(t =>
          t.toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
        return;

      const addPoint = (
        date: Date,
        type: 'taken' | 'created' | 'modified' | 'accessed'
      ) => {
        if (!filters.types.includes(type)) return;
        if (dateRangeStart && date < new Date(dateRangeStart)) return;
        if (dateRangeEnd && date > new Date(dateRangeEnd + 'T23:59:59')) return;
        points.push({ date, type, file, id: `${file.id}-${type}` });
      };

      if (file.dateTaken) addPoint(file.dateTaken, 'taken');
      addPoint(file.created, 'created');
      addPoint(file.modified, 'modified');
      addPoint(file.accessed, 'accessed');
    });

    points.sort((a, b) =>
      sortOrder === 'asc'
        ? a.date.getTime() - b.date.getTime()
        : b.date.getTime() - a.date.getTime()
    );
    return points;
  }, [
    files,
    fileMode,
    selectedFileIdx,
    filters,
    searchQuery,
    sortOrder,
    dateRangeStart,
    dateRangeEnd,
  ]);

  const { minDate, maxDate, timeRange } = useMemo(() => {
    if (allTimelinePoints.length === 0) {
      const now = new Date();
      return { minDate: now, maxDate: now, timeRange: 1 };
    }
    const dates = allTimelinePoints.map(p => p.date);
    const min = new Date(Math.min(...dates.map(d => d.getTime())));
    const max = new Date(Math.max(...dates.map(d => d.getTime())));
    return {
      minDate: min,
      maxDate: max,
      timeRange: max.getTime() - min.getTime() || 1,
    };
  }, [allTimelinePoints]);

  const stats = useMemo(() => {
    const totalFiles = new Set(allTimelinePoints.map(p => p.file.id)).size;
    const totalEvents = allTimelinePoints.length;
    const byType: Record<string, number> = {};
    let totalSize = 0;

    allTimelinePoints.forEach(p => {
      byType[p.type] = (byType[p.type] || 0) + 1;
      totalSize += p.file.sizeBytes || 0;
    });

    const daysSpan = Math.ceil(timeRange / (1000 * 60 * 60 * 24));
    return { totalFiles, totalEvents, byType, totalSize, daysSpan };
  }, [allTimelinePoints, timeRange]);

  const getPosition = useCallback(
    (date: Date) => {
      const basePos = ((date.getTime() - minDate.getTime()) / timeRange) * 100;
      return basePos * zoomLevel + panOffset;
    },
    [minDate, timeRange, zoomLevel, panOffset]
  );

  const handleZoom = (delta: number) => {
    setZoomLevel(prev => Math.max(0.5, Math.min(5, prev + delta)));
  };

  const handleWheel = (e: React.WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      handleZoom(e.deltaY > 0 ? -0.1 : 0.1);
    } else {
      setPanOffset(prev => prev - e.deltaY * 0.1);
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({ x: e.clientX, offset: panOffset });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      const delta = e.clientX - dragStart.x;
      setPanOffset(dragStart.offset + delta * 0.2);
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const handlePointClick = (point: TimelineEvent, e: React.MouseEvent) => {
    if (e.shiftKey) {
      setSelectedPoints(prev =>
        prev.includes(point.id)
          ? prev.filter(id => id !== point.id)
          : [...prev, point.id]
      );
    } else if (e.ctrlKey || e.metaKey) {
      setDetailModal(point);
    } else {
      setSelectedPoints([point.id]);
    }
  };

  useEffect(() => {
    if (isPlaying && allTimelinePoints.length > 0) {
      playIntervalRef.current = setInterval(() => {
        setCurrentPlayIndex(prev => {
          if (prev >= allTimelinePoints.length - 1) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 1;
        });
      }, 1000 / playbackSpeed);
    } else {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    }
    return () => {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    };
  }, [isPlaying, playbackSpeed, allTimelinePoints.length]);

  useEffect(() => {
    if (isPlaying && allTimelinePoints[currentPlayIndex]) {
      setSelectedPoints([allTimelinePoints[currentPlayIndex].id]);
    }
  }, [currentPlayIndex, isPlaying, allTimelinePoints]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      )
        return;

      switch (e.key) {
        case '+':
        case '=':
          handleZoom(0.2);
          break;
        case '-':
          handleZoom(-0.2);
          break;
        case '0':
          setZoomLevel(1);
          setPanOffset(0);
          break;
        case ' ':
          e.preventDefault();
          setIsPlaying(p => !p);
          break;
        case 'ArrowLeft':
          setPanOffset(p => p + 50);
          break;
        case 'ArrowRight':
          setPanOffset(p => p - 50);
          break;
        case 'd':
          setDarkMode(d => !d);
          break;
        case 'f':
          setShowFilters(f => !f);
          break;
        case 's':
          setShowStats(s => !s);
          break;
        case 'Escape':
          setDetailModal(null);
          setSelectedPoints([]);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const theme = {
    bg: darkMode
      ? 'bg-gray-900'
      : 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50',
    card: darkMode
      ? 'bg-gray-800 border-gray-700'
      : 'bg-white/80 backdrop-blur border-white/50',
    text: darkMode ? 'text-gray-100' : 'text-gray-800',
    textMuted: darkMode ? 'text-gray-400' : 'text-gray-500',
    border: darkMode ? 'border-gray-700' : 'border-gray-200',
    hover: darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-100',
    input: darkMode
      ? 'bg-gray-700 border-gray-600 text-white'
      : 'bg-white border-gray-300',
    accent: 'bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500',
  };

  const exportData = (format: 'json' | 'csv') => {
    const data = allTimelinePoints.map(p => ({
      file: p.file.filename,
      type: p.type,
      date: p.date.toISOString(),
      size: p.file.size,
    }));

    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'timeline-export.json';
      a.click();
    } else {
      const csv = ['File,Type,Date,Size']
        .concat(
          allTimelinePoints.map(
            p =>
              `"${p.file.filename}",${p.type},"${p.date.toISOString()}","${p.file.size}"`
          )
        )
        .join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'timeline-export.csv';
      a.click();
    }
    setShowExportMenu(false);
  };

  const currentFile = files[selectedFileIdx];

  return (
    <div
      className={`w-full min-h-screen ${theme.bg} p-4 md:p-8 transition-colors duration-300`}
    >
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className={`${theme.card} rounded-2xl shadow-xl border p-6`}>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1
                className={`text-3xl font-bold ${theme.text} flex items-center gap-3`}
              >
                <div
                  className={`w-10 h-10 ${theme.accent} rounded-xl flex items-center justify-center`}
                >
                  <Clock className="w-6 h-6 text-white" />
                </div>
                Premium Timeline Explorer
              </h1>
              <p className={`${theme.textMuted} mt-1`}>
                Interactive file metadata visualization •{' '}
                {allTimelinePoints.length} events across {stats.totalFiles}{' '}
                files
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2.5 rounded-xl ${theme.hover} ${theme.text} transition-all`}
              >
                {darkMode ? (
                  <Sun className="w-5 h-5" />
                ) : (
                  <Moon className="w-5 h-5" />
                )}
              </button>
              <button
                type="button"
                onClick={() => setShowStats(!showStats)}
                className={`p-2.5 rounded-xl ${showStats ? 'bg-indigo-500 text-white' : theme.hover + ' ' + theme.text} transition-all`}
              >
                <BarChart3 className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className={`p-2.5 rounded-xl ${showFilters ? 'bg-indigo-500 text-white' : theme.hover + ' ' + theme.text} transition-all`}
              >
                <Filter className="w-5 h-5" />
              </button>
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowExportMenu(!showExportMenu)}
                  className={`p-2.5 rounded-xl ${showExportMenu ? 'bg-indigo-500 text-white' : theme.hover + ' ' + theme.text} transition-all`}
                >
                  <Download className="w-5 h-5" />
                </button>
                {showExportMenu && (
                  <div
                    className={`absolute right-0 top-12 ${theme.card} rounded-xl shadow-2xl border p-2 z-50 min-w-[160px]`}
                  >
                    <button
                      type="button"
                      onClick={() => exportData('json')}
                      className={`w-full text-left px-4 py-2 rounded-lg ${theme.hover} ${theme.text} text-sm block`}
                    >
                      📄 Export as JSON
                    </button>
                    <button
                      type="button"
                      onClick={() => exportData('csv')}
                      className={`w-full text-left px-4 py-2 rounded-lg ${theme.hover} ${theme.text} text-sm block`}
                    >
                      📊 Export as CSV
                    </button>
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={() => setComparisonMode(!comparisonMode)}
                className={`p-2.5 rounded-xl ${comparisonMode ? 'bg-pink-500 text-white' : theme.hover + ' ' + theme.text} transition-all`}
              >
                <Layers className="w-5 h-5" />
              </button>
            </div>
          </div>
          <div className="mt-4 relative">
            <Search
              className={`absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 ${theme.textMuted}`}
            />
            <input
              type="text"
              id="search"
              placeholder="Search files by name or tags..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className={`w-full pl-12 pr-4 py-3 rounded-xl ${theme.input} border focus:ring-2 focus:ring-indigo-500 transition-all`}
            />
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div
            className={`${theme.card} rounded-2xl shadow-xl border p-6 animate-in slide-in-from-top-2`}
          >
            <h3
              className={`font-semibold ${theme.text} mb-4 flex items-center gap-2`}
            >
              <Filter className="w-4 h-4" /> Filters
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <label
                  className={`text-sm font-medium ${theme.textMuted} mb-2 block`}
                >
                  Event Types
                </label>
                <div className="flex flex-wrap gap-2">
                  {(
                    Object.entries(dateTypeInfo) as [
                      string,
                      (typeof dateTypeInfo)[string],
                    ][]
                  ).map(([type, info]) => (
                    <button
                      type="button"
                      key={type}
                      onClick={() =>
                        setFilters(f => ({
                          types: f.types.includes(
                            type as
                              | 'taken'
                              | 'created'
                              | 'modified'
                              | 'accessed'
                          )
                            ? f.types.filter(t => t !== type)
                            : [
                                ...f.types,
                                type as
                                  | 'taken'
                                  | 'created'
                                  | 'modified'
                                  | 'accessed',
                              ],
                          fileTypes: f.fileTypes,
                        }))
                      }
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5 transition-all ${filters.types.includes(type as 'taken' | 'created' | 'modified' | 'accessed') ? info.color + ' text-white' : `${theme.hover} ${theme.text} border ${theme.border}`}`}
                    >
                      <info.icon className="w-3.5 h-3.5" />
                      {info.label}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label
                  className={`text-sm font-medium ${theme.textMuted} mb-2 block`}
                >
                  File Types
                </label>
                <div className="flex flex-wrap gap-2">
                  {(['image', 'document', 'text'] as const).map(type => (
                    <button
                      type="button"
                      key={type}
                      onClick={() =>
                        setFilters(f => ({
                          types: f.types,
                          fileTypes: f.fileTypes.includes(type)
                            ? f.fileTypes.filter(t => t !== type)
                            : [...f.fileTypes, type],
                        }))
                      }
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-all ${filters.fileTypes.includes(type) ? 'bg-indigo-500 text-white' : `${theme.hover} ${theme.text} border ${theme.border}`}`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label
                  className={`text-sm font-medium ${theme.textMuted} mb-2 block`}
                >
                  Group By
                </label>
                <div className="flex flex-wrap gap-2">
                  {(['none', 'day', 'week', 'month', 'year'] as const).map(
                    g => (
                      <button
                        type="button"
                        key={g}
                        onClick={() => setGroupBy(g)}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-all ${groupBy === g ? 'bg-indigo-500 text-white' : `${theme.hover} ${theme.text} border ${theme.border}`}`}
                      >
                        {g === 'none' ? 'None' : g}
                      </button>
                    )
                  )}
                </div>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-dashed border-gray-300">
              <label
                className={`text-sm font-medium ${theme.textMuted} mb-2 block`}
              >
                Date Range
              </label>
              <div className="flex flex-wrap items-center gap-3">
                <input
                  type="date"
                  id="dateStart"
                  value={dateRangeStart}
                  onChange={e => setDateRangeStart(e.target.value)}
                  className={`px-3 py-2 rounded-lg ${theme.input} border text-sm`}
                />
                <span className={theme.textMuted}>to</span>
                <input
                  type="date"
                  id="dateEnd"
                  value={dateRangeEnd}
                  onChange={e => setDateRangeEnd(e.target.value)}
                  className={`px-3 py-2 rounded-lg ${theme.input} border text-sm`}
                />
                {(dateRangeStart || dateRangeEnd) && (
                  <button
                    type="button"
                    onClick={() => {
                      setDateRangeStart('');
                      setDateRangeEnd('');
                    }}
                    className={`px-3 py-2 rounded-lg ${theme.hover} ${theme.text} text-sm`}
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Stats Panel */}
        {showStats && (
          <div
            className={`${theme.card} rounded-2xl shadow-xl border p-6 animate-in slide-in-from-top-2`}
          >
            <h3
              className={`font-semibold ${theme.text} mb-4 flex items-center gap-2`}
            >
              <BarChart3 className="w-4 h-4" /> Statistics
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                {
                  label: 'Files',
                  value: stats.totalFiles,
                  color: 'from-blue-500 to-cyan-500',
                },
                {
                  label: 'Events',
                  value: stats.totalEvents,
                  color: 'from-purple-500 to-pink-500',
                },
                {
                  label: 'Days Span',
                  value: stats.daysSpan,
                  color: 'from-amber-500 to-orange-500',
                },
                {
                  label: 'Total Size',
                  value: formatFileSize(stats.totalSize),
                  color: 'from-green-500 to-emerald-500',
                },
                {
                  label: 'By Type',
                  value: null,
                  color: 'from-indigo-500 to-purple-500',
                  isHtml: true,
                },
              ].map((stat, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-xl ${darkMode ? 'bg-gray-700/50' : 'bg-gray-100'}`}
                >
                  {stat.isHtml ? (
                    <div className="flex gap-2 justify-center">
                      {Object.entries(stats.byType).map(([t, c]) => (
                        <div
                          key={t}
                          className={`w-6 h-6 ${dateTypeInfo[t]?.color} rounded-full flex items-center justify-center text-xs text-white font-bold`}
                        >
                          {c}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div
                      className={`text-2xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent`}
                    >
                      {stat.value}
                    </div>
                  )}
                  <div className={`text-sm ${theme.textMuted} mt-1`}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Controls Bar */}
        <div className={`${theme.card} rounded-2xl shadow-xl border p-4`}>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div
                className={`flex rounded-xl p-1 ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}
              >
                {[
                  { id: 'single', label: 'Single', icon: FileText },
                  { id: 'all', label: 'All Files', icon: Layers },
                ].map(mode => (
                  <button
                    type="button"
                    key={mode.id}
                    onClick={() => {
                      setFileMode(mode.id as 'single' | 'all');
                      setCurrentPlayIndex(0);
                    }}
                    className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${fileMode === mode.id ? 'bg-indigo-500 text-white shadow-md' : `${theme.text} ${theme.hover}`}`}
                  >
                    <mode.icon className="w-4 h-4" />
                    {mode.label}
                  </button>
                ))}
              </div>
              {fileMode === 'single' && (
                <select
                  value={selectedFileIdx}
                  onChange={e => {
                    setSelectedFileIdx(Number(e.target.value));
                    setCurrentPlayIndex(0);
                  }}
                  className={`px-4 py-2 rounded-xl ${theme.input} border text-sm`}
                >
                  {files.map((file, idx) => (
                    <option key={idx} value={idx}>
                      {file.filename}
                    </option>
                  ))}
                </select>
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handleZoom(-0.2)}
                className={`p-2 rounded-lg ${theme.hover} ${theme.text}`}
              >
                <ZoomOut className="w-5 h-5" />
              </button>
              <div
                className={`px-3 py-1 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} ${theme.text} text-sm font-mono min-w-[4rem] text-center`}
              >
                {Math.round(zoomLevel * 100)}%
              </div>
              <button
                type="button"
                onClick={() => handleZoom(0.2)}
                className={`p-2 rounded-lg ${theme.hover} ${theme.text}`}
              >
                <ZoomIn className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={() => {
                  setZoomLevel(1);
                  setPanOffset(0);
                }}
                className={`px-3 py-2 rounded-lg ${theme.hover} ${theme.text} text-sm`}
              >
                Reset
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setCurrentPlayIndex(0)}
                className={`p-2 rounded-lg ${theme.hover} ${theme.text}`}
              >
                <SkipBack className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={() => setIsPlaying(!isPlaying)}
                className={`p-3 rounded-xl ${isPlaying ? 'bg-red-500 text-white' : 'bg-indigo-500 text-white'}`}
              >
                {isPlaying ? (
                  <Pause className="w-5 h-5" />
                ) : (
                  <Play className="w-5 h-5" />
                )}
              </button>
              <button
                type="button"
                onClick={() =>
                  setCurrentPlayIndex(Math.max(0, allTimelinePoints.length - 1))
                }
                className={`p-2 rounded-lg ${theme.hover} ${theme.text}`}
              >
                <SkipForward className="w-5 h-5" />
              </button>
              <select
                value={playbackSpeed}
                onChange={e => setPlaybackSpeed(Number(e.target.value))}
                className={`px-2 py-1 rounded-lg ${theme.input} border text-sm`}
              >
                <option value={0.5}>0.5x</option>
                <option value={1}>1x</option>
                <option value={2}>2x</option>
                <option value={4}>4x</option>
              </select>
            </div>
            <button
              type="button"
              onClick={() => setSortOrder(o => (o === 'asc' ? 'desc' : 'asc'))}
              className={`px-4 py-2 rounded-xl flex items-center gap-2 ${theme.hover} ${theme.text} text-sm`}
            >
              <ArrowUpDown className="w-4 h-4" />
              {sortOrder === 'asc' ? 'Oldest First' : 'Newest First'}
            </button>
          </div>
        </div>

        {/* Main Timeline */}
        <div
          ref={timelineRef}
          onWheel={handleWheel}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className={`${theme.card} rounded-2xl shadow-xl border p-6 overflow-hidden cursor-grab active:cursor-grabbing`}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className={`text-xl font-semibold ${theme.text}`}>
              {fileMode === 'single'
                ? currentFile.filename
                : 'All Files Timeline'}
            </h2>
            <div className={`text-sm ${theme.textMuted}`}>
              {formatDate(minDate, 'short')} → {formatDate(maxDate, 'short')}
            </div>
          </div>

          {/* Minimap */}
          <div
            className={`mb-4 relative h-8 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} overflow-hidden`}
          >
            {allTimelinePoints.map((point, idx) => {
              const pos =
                ((point.date.getTime() - minDate.getTime()) / timeRange) * 100;
              return (
                <div
                  key={idx}
                  className={`absolute w-1 h-full ${dateTypeInfo[point.type]?.color} opacity-60`}
                  style={{ left: `${pos}%` }}
                />
              );
            })}
            <div
              className="absolute h-full bg-indigo-500/30 border-2 border-indigo-500 rounded"
              style={{
                left: `${Math.max(0, -panOffset / zoomLevel)}%`,
                width: `${100 / zoomLevel}%`,
              }}
            />
          </div>

          {/* Timeline Track */}
          <div className="relative pt-16" style={{ minHeight: '300px' }}>
            <div
              className={`absolute top-24 left-0 right-0 h-3 rounded-full ${theme.accent} opacity-20`}
              style={{
                transform: `translateX(${panOffset}px) scaleX(${zoomLevel})`,
                transformOrigin: 'left',
              }}
            />
            <div
              className="absolute top-0 left-0 right-0 flex justify-between text-xs"
              style={{ transform: `translateX(${panOffset}px)` }}
            >
              {[0, 25, 50, 75, 100].map(pct => {
                const date = new Date(
                  minDate.getTime() + (timeRange * pct) / 100
                );
                return (
                  <div
                    key={pct}
                    className={theme.textMuted}
                    style={{
                      left: `${pct * zoomLevel}%`,
                      position: 'absolute',
                    }}
                  >
                    {formatDate(date, 'short')}
                  </div>
                );
              })}
            </div>
            <div className="relative pt-16" style={{ height: '250px' }}>
              {allTimelinePoints.map((point, idx) => {
                const typeInfo = dateTypeInfo[point.type];
                if (!typeInfo) return null;
                const Icon = typeInfo.icon;
                const position = getPosition(point.date);
                const isSelected = selectedPoints.includes(point.id);
                const isHovered = hoveredPoint === point.id;
                const row = fileMode === 'all' ? idx % 3 : 0;
                return (
                  <div
                    key={point.id}
                    className="absolute transform -translate-x-1/2 transition-all duration-200"
                    style={{ left: `${position}%`, top: `${row * 70}px` }}
                    onMouseEnter={() => setHoveredPoint(point.id)}
                    onMouseLeave={() => setHoveredPoint(null)}
                    onClick={e => handlePointClick(point, e)}
                    role="button"
                    tabIndex={0}
                    onKeyUp={e =>
                      e.key === 'Enter' &&
                      handlePointClick(point, e as unknown as React.MouseEvent)
                    }
                  >
                    <div
                      className={`absolute left-1/2 -translate-x-1/2 w-0.5 h-16 ${darkMode ? 'bg-gray-600' : 'bg-gray-300'}`}
                    />
                    <div
                      className={`relative w-14 h-14 ${typeInfo.color} rounded-full flex items-center justify-center cursor-pointer transform transition-all duration-200 shadow-lg ${isHovered || isSelected ? 'scale-125 shadow-2xl z-30' : 'hover:scale-110 z-10'} ${isSelected ? `ring-4 ${typeInfo.ring}` : ''}`}
                    >
                      <Icon className="w-6 h-6 text-white" />
                      {isSelected && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-white rounded-full flex items-center justify-center shadow-md">
                          <Check className="w-3 h-3 text-indigo-600" />
                        </div>
                      )}
                    </div>
                    {(isHovered || isSelected) && (
                      <div className="absolute top-20 left-1/2 -translate-x-1/2 z-40 animate-in fade-in zoom-in-95 duration-150">
                        <div
                          className={`${typeInfo.bgLight} px-5 py-4 rounded-xl shadow-2xl border-2 ${typeInfo.border} whitespace-nowrap`}
                        >
                          <div
                            className={`flex items-center gap-2 mb-2 pb-2 border-b ${theme.border}`}
                          >
                            <point.file.icon
                              className={`w-4 h-4 ${typeInfo.textColor}`}
                            />
                            <span className={`text-sm font-bold ${theme.text}`}>
                              {point.file.filename}
                            </span>
                          </div>
                          <div
                            className={`text-xs font-semibold ${typeInfo.textColor} mb-1`}
                          >
                            {typeInfo.label}
                          </div>
                          <div className={`text-sm font-medium ${theme.text}`}>
                            {formatDate(point.date)}
                          </div>
                          <div className={`text-xs ${theme.textMuted} mt-1`}>
                            {formatRelative(point.date)}
                          </div>
                          <div className="mt-2 pt-2 border-t border-dashed border-gray-300 flex gap-3">
                            <span className={`text-xs ${theme.textMuted}`}>
                              {point.file.size}
                            </span>
                            {point.file.dimensions && (
                              <span className={`text-xs ${theme.textMuted}`}>
                                {point.file.dimensions}
                              </span>
                            )}
                          </div>
                        </div>
                        <div
                          className={`absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 ${typeInfo.bgLight} rotate-45 border-l-2 border-t-2 ${typeInfo.border}`}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Detail Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(fileMode === 'single' ? [currentFile] : files).map(file => {
            const fileDates = [
              file.dateTaken && {
                type: 'taken' as const,
                date: file.dateTaken,
              },
              { type: 'created' as const, date: file.created },
              { type: 'modified' as const, date: file.modified },
              { type: 'accessed' as const, date: file.accessed },
            ].filter(Boolean);
            return (
              <div
                key={file.id}
                className={`${theme.card} rounded-xl border p-5 hover:shadow-lg transition-all cursor-pointer`}
                onClick={() => onFileSelect?.(file)}
                role="button"
                tabIndex={0}
                onKeyUp={e => e.key === 'Enter' && onFileSelect?.(file)}
              >
                <div className="flex items-start gap-3 mb-4">
                  <div
                    className={`w-10 h-10 ${theme.accent} rounded-lg flex items-center justify-center`}
                  >
                    <file.icon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-semibold ${theme.text} truncate`}>
                      {file.filename}
                    </h3>
                    <p className={`text-sm ${theme.textMuted}`}>
                      {file.type} • {file.size}
                      {file.dimensions && ` • ${file.dimensions}`}
                      {file.pages && ` • ${file.pages} pages`}
                    </p>
                  </div>
                </div>
                {file.tags && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {file.tags.map(tag => (
                      <span
                        key={tag}
                        className={`px-2 py-0.5 rounded-full text-xs ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-600'}`}
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
                <div className="grid grid-cols-2 gap-2">
                  {fileDates.map(dateInfo => {
                    if (!dateInfo) return null;
                    const typeInfo = dateTypeInfo[dateInfo.type];
                    if (!typeInfo) return null;
                    const Icon = typeInfo.icon;
                    return (
                      <div
                        key={dateInfo.type}
                        className={`${typeInfo.bgLight} p-3 rounded-lg border ${typeInfo.border}`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <div
                            className={`${typeInfo.color} w-6 h-6 rounded-full flex items-center justify-center`}
                          >
                            <Icon className="w-3 h-3 text-white" />
                          </div>
                          <span
                            className={`text-xs font-medium ${typeInfo.textColor}`}
                          >
                            {typeInfo.label}
                          </span>
                        </div>
                        <div className={`text-xs ${theme.text} font-medium`}>
                          {formatDate(dateInfo.date, 'short')}
                        </div>
                        <div className={`text-xs ${theme.textMuted}`}>
                          {formatRelative(dateInfo.date)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Legend & Shortcuts */}
        <div className={`${theme.card} rounded-2xl shadow-xl border p-6`}>
          <div className="flex flex-wrap justify-between gap-8">
            <div>
              <h3 className={`text-sm font-semibold ${theme.textMuted} mb-3`}>
                Legend
              </h3>
              <div className="flex flex-wrap gap-4">
                {Object.entries(dateTypeInfo).map(([type, info]) => (
                  <div key={type} className="flex items-center gap-2">
                    <div
                      className={`${info.color} w-6 h-6 rounded-full flex items-center justify-center`}
                    >
                      <info.icon className="w-3 h-3 text-white" />
                    </div>
                    <span className={`text-sm ${theme.text}`}>
                      {info.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className={`text-sm font-semibold ${theme.textMuted} mb-3`}>
                Keyboard Shortcuts
              </h3>
              <div className="flex flex-wrap gap-4 text-sm">
                {[
                  { key: '+/-', desc: 'Zoom' },
                  { key: '0', desc: 'Reset' },
                  { key: 'Space', desc: 'Play/Pause' },
                  { key: '←/→', desc: 'Pan' },
                  { key: 'D', desc: 'Dark mode' },
                  { key: 'F', desc: 'Filters' },
                  { key: 'S', desc: 'Stats' },
                ].map(shortcut => (
                  <div key={shortcut.key} className="flex items-center gap-2">
                    <kbd
                      className={`px-2 py-1 rounded ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} ${theme.text} font-mono text-xs`}
                    >
                      {shortcut.key}
                    </kbd>
                    <span className={theme.textMuted}>{shortcut.desc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Detail Modal */}
        {detailModal && (
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setDetailModal(null)}
          >
            <div
              className={`${theme.card} rounded-2xl shadow-2xl border max-w-lg w-full p-6 animate-in zoom-in-95`}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-12 h-12 ${dateTypeInfo[detailModal.type]?.color} rounded-xl flex items-center justify-center`}
                  >
                    {dateTypeInfo[detailModal.type] &&
                      React.createElement(dateTypeInfo[detailModal.type].icon, {
                        className: 'w-6 h-6 text-white',
                      })}
                  </div>
                  <div>
                    <h2 className={`text-xl font-bold ${theme.text}`}>
                      {detailModal.file.filename}
                    </h2>
                    <p
                      className={`${dateTypeInfo[detailModal.type]?.textColor} font-medium`}
                    >
                      {dateTypeInfo[detailModal.type]?.label}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setDetailModal(null)}
                  className={`p-2 rounded-lg ${theme.hover}`}
                >
                  <X className={`w-5 h-5 ${theme.text}`} />
                </button>
              </div>
              <div className="space-y-4">
                <div
                  className={`p-4 rounded-xl ${darkMode ? 'bg-gray-700/50' : 'bg-gray-100'}`}
                >
                  <div className={`text-lg font-semibold ${theme.text}`}>
                    {formatDate(detailModal.date)}
                  </div>
                  <div className={theme.textMuted}>
                    {formatRelative(detailModal.date)}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className={`text-sm ${theme.textMuted}`}>
                      File Type
                    </div>
                    <div className={`font-medium ${theme.text} capitalize`}>
                      {detailModal.file.type}
                    </div>
                  </div>
                  <div>
                    <div className={`text-sm ${theme.textMuted}`}>Size</div>
                    <div className={`font-medium ${theme.text}`}>
                      {detailModal.file.size}
                    </div>
                  </div>
                  {detailModal.file.dimensions && (
                    <div>
                      <div className={`text-sm ${theme.textMuted}`}>
                        Dimensions
                      </div>
                      <div className={`font-medium ${theme.text}`}>
                        {detailModal.file.dimensions}
                      </div>
                    </div>
                  )}
                  {detailModal.file.pages && (
                    <div>
                      <div className={`text-sm ${theme.textMuted}`}>Pages</div>
                      <div className={`font-medium ${theme.text}`}>
                        {detailModal.file.pages}
                      </div>
                    </div>
                  )}
                  {detailModal.file.location && (
                    <div>
                      <div className={`text-sm ${theme.textMuted}`}>
                        Location
                      </div>
                      <div className={`font-medium ${theme.text}`}>
                        {detailModal.file.location}
                      </div>
                    </div>
                  )}
                  {detailModal.file.camera && (
                    <div>
                      <div className={`text-sm ${theme.textMuted}`}>Camera</div>
                      <div className={`font-medium ${theme.text}`}>
                        {detailModal.file.camera}
                      </div>
                    </div>
                  )}
                  {detailModal.file.author && (
                    <div>
                      <div className={`text-sm ${theme.textMuted}`}>Author</div>
                      <div className={`font-medium ${theme.text}`}>
                        {detailModal.file.author}
                      </div>
                    </div>
                  )}
                </div>
                {detailModal.file.tags && (
                  <div>
                    <div className={`text-sm ${theme.textMuted} mb-2`}>
                      Tags
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {detailModal.file.tags.map(tag => (
                        <span
                          key={tag}
                          className={`px-3 py-1 rounded-full text-sm ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-indigo-100 text-indigo-700'}`}
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Comparison Modal */}
        {comparisonMode && (
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setComparisonMode(false)}
          >
            <div
              className={`${theme.card} rounded-2xl shadow-2xl border max-w-5xl w-full max-h-[90vh] overflow-auto p-6`}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className={`text-2xl font-bold ${theme.text}`}>
                  📊 File Comparison
                </h2>
                <button
                  type="button"
                  onClick={() => setComparisonMode(false)}
                  className={`p-2 rounded-lg ${theme.hover}`}
                >
                  <X className={`w-5 h-5 ${theme.text}`} />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <select
                  value={compareFiles[0]}
                  onChange={e =>
                    setCompareFiles([Number(e.target.value), compareFiles[1]])
                  }
                  className={`px-4 py-3 rounded-xl ${theme.input} border text-sm font-medium`}
                >
                  {files.map((file, idx) => (
                    <option key={idx} value={idx}>
                      {file.filename}
                    </option>
                  ))}
                </select>
                <select
                  value={compareFiles[1]}
                  onChange={e =>
                    setCompareFiles([compareFiles[0], Number(e.target.value)])
                  }
                  className={`px-4 py-3 rounded-xl ${theme.input} border text-sm font-medium`}
                >
                  {files.map((file, idx) => (
                    <option key={idx} value={idx}>
                      {file.filename}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-6">
                {compareFiles.map((fileIdx, i) => {
                  const file = files[fileIdx];
                  const fileDates = [
                    file.dateTaken && {
                      type: 'taken' as const,
                      date: file.dateTaken,
                    },
                    { type: 'created' as const, date: file.created },
                    { type: 'modified' as const, date: file.modified },
                    { type: 'accessed' as const, date: file.accessed },
                  ].filter(Boolean);
                  return (
                    <div
                      key={i}
                      className={`p-5 rounded-xl ${darkMode ? 'bg-gray-700/50' : 'bg-gray-50'}`}
                    >
                      <div className="flex items-center gap-3 mb-4">
                        <div
                          className={`w-10 h-10 ${theme.accent} rounded-lg flex items-center justify-center`}
                        >
                          <file.icon className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h3 className={`font-semibold ${theme.text}`}>
                            {file.filename}
                          </h3>
                          <p className={`text-sm ${theme.textMuted}`}>
                            {file.type} • {file.size}
                          </p>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {fileDates.map(dateInfo => {
                          if (!dateInfo) return null;
                          const typeInfo = dateTypeInfo[dateInfo.type];
                          if (!typeInfo) return null;
                          const Icon = typeInfo.icon;
                          return (
                            <div
                              key={dateInfo.type}
                              className={`flex items-center justify-between p-3 rounded-lg ${typeInfo.bgLight} border ${typeInfo.border}`}
                            >
                              <div className="flex items-center gap-2">
                                <div
                                  className={`${typeInfo.color} w-7 h-7 rounded-full flex items-center justify-center`}
                                >
                                  <Icon className="w-3.5 h-3.5 text-white" />
                                </div>
                                <span
                                  className={`text-sm font-medium ${typeInfo.textColor}`}
                                >
                                  {typeInfo.label}
                                </span>
                              </div>
                              <div className="text-right">
                                <div
                                  className={`text-sm font-medium ${theme.text}`}
                                >
                                  {formatDate(dateInfo.date, 'short')}
                                </div>
                                <div className={`text-xs ${theme.textMuted}`}>
                                  {formatRelative(dateInfo.date)}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div
                className={`mt-6 p-4 rounded-xl ${darkMode ? 'bg-gray-700/30' : 'bg-indigo-50'} border ${darkMode ? 'border-gray-600' : 'border-indigo-200'}`}
              >
                <h3 className={`text-sm font-semibold ${theme.text} mb-3`}>
                  📈 Time Difference Analysis
                </h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  {(() => {
                    const f1 = files[compareFiles[0]];
                    const f2 = files[compareFiles[1]];
                    const createdDiff =
                      Math.abs(f1.created.getTime() - f2.created.getTime()) /
                      (1000 * 60 * 60 * 24);
                    const modifiedDiff =
                      Math.abs(f1.modified.getTime() - f2.modified.getTime()) /
                      (1000 * 60 * 60 * 24);
                    const accessedDiff =
                      Math.abs(f1.accessed.getTime() - f2.accessed.getTime()) /
                      (1000 * 60 * 60 * 24);
                    return [
                      {
                        label: 'Created difference',
                        value: `${createdDiff.toFixed(1)} days`,
                      },
                      {
                        label: 'Modified difference',
                        value: `${modifiedDiff.toFixed(1)} days`,
                      },
                      {
                        label: 'Accessed difference',
                        value: `${accessedDiff.toFixed(1)} days`,
                      },
                    ];
                  })().map((stat, i) => (
                    <div key={i}>
                      <div className={`text-lg font-bold ${theme.text}`}>
                        {stat.value}
                      </div>
                      <div className={`text-xs ${theme.textMuted}`}>
                        {stat.label}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default PremiumTimeline;
