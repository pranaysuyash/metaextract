/**
 * Professional Visualization Components - Advanced data visualization
 */

import React from 'react';
import { 
  BarChart3, 
  PieChart as PieChartIcon, 
  LineChart, 
  AreaChart,
  TrendingUp,
  Calendar,
  MapPin,
  Camera,
  Eye,
  FileText,
  Database,
  Activity,
  Layers,
  Filter,
  Download,
  Settings
} from 'lucide-react';
import { 
  Bar,
  BarChart,
  Pie,
  PieChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';

export interface ChartData {
  name: string;
  value: number;
  fill?: string;
  [key: string]: any;
}

export interface TimeSeriesData {
  date: string;
  value: number;
  [key: string]: any;
}

export interface MetadataFieldDistribution {
  fieldName: string;
  count: number;
  percentage: number;
  avgConfidence: number;
}

export interface ExtractionTrend {
  date: string;
  extractions: number;
  successRate: number;
  avgProcessingTime: number;
}

export interface UserEngagementData {
  date: string;
  activeUsers: number;
  newUsers: number;
  retentionRate: number;
}

export interface FileFormatDistribution {
  format: string;
  count: number;
  percentage: number;
  avgSize: number;
}

export interface GeographicDistribution {
  country: string;
  count: number;
  percentage: number;
}

export interface CameraMakeDistribution {
  make: string;
  count: number;
  percentage: number;
}

export interface ProfessionalVisualizationProps {
  data: ChartData[] | TimeSeriesData[] | MetadataFieldDistribution[] | ExtractionTrend[] | UserEngagementData[] | FileFormatDistribution[] | GeographicDistribution[] | CameraMakeDistribution[];
  type: 'bar' | 'line' | 'area' | 'pie' | 'scatter' | 'heatmap' | 'radar';
  title?: string;
  subtitle?: string;
  xAxisKey?: string;
  yAxisKey?: string;
  colorScheme?: string[];
  height?: number;
  width?: number;
  className?: string;
  showLegend?: boolean;
  showTooltip?: boolean;
  showGrid?: boolean;
  stacked?: boolean;
  formatValue?: (value: number) => string;
}

export const ProfessionalBarChart: React.FC<ProfessionalVisualizationProps> = ({
  data,
  title,
  subtitle,
  xAxisKey = 'name',
  yAxisKey = 'value',
  colorScheme = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'],
  height = 400,
  width = '100%',
  className = '',
  showLegend = true,
  showTooltip = true,
  showGrid = true,
  stacked = false,
  formatValue
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <p className="font-medium text-foreground">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatValue ? formatValue(entry.value) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`bg-card border border-border rounded-xl p-6 ${className}`}>
      <div className="mb-4">
        {title && <h3 className="text-lg font-semibold text-foreground mb-1">{title}</h3>}
        {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      
      <div style={{ height, width }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout={stacked ? 'vertical' : 'horizontal'}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />}
            <XAxis 
              dataKey={xAxisKey} 
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              tickFormatter={formatValue}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            
            {stacked ? (
              <>
                {Object.keys(data[0]).filter(key => key !== xAxisKey).map((key, index) => (
                  <Bar 
                    key={key}
                    dataKey={key} 
                    stackId="a"
                    fill={colorScheme[index % colorScheme.length]}
                  />
                ))}
              </>
            ) : (
              <Bar 
                dataKey={yAxisKey} 
                fill={colorScheme[0]}
                radius={[4, 4, 0, 0]}
              />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const ProfessionalLineChart: React.FC<ProfessionalVisualizationProps> = ({
  data,
  title,
  subtitle,
  xAxisKey = 'date',
  yAxisKey = 'value',
  colorScheme = ['#3b82f6'],
  height = 400,
  width = '100%',
  className = '',
  showLegend = true,
  showTooltip = true,
  showGrid = true,
  formatValue
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <p className="font-medium text-foreground">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatValue ? formatValue(entry.value) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`bg-card border border-border rounded-xl p-6 ${className}`}>
      <div className="mb-4">
        {title && <h3 className="text-lg font-semibold text-foreground mb-1">{title}</h3>}
        {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      
      <div style={{ height, width }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />}
            <XAxis 
              dataKey={xAxisKey} 
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              tickFormatter={formatValue}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            
            <Line 
              type="monotone" 
              dataKey={yAxisKey} 
              stroke={colorScheme[0]} 
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const ProfessionalAreaChart: React.FC<ProfessionalVisualizationProps> = ({
  data,
  title,
  subtitle,
  xAxisKey = 'date',
  yAxisKey = 'value',
  colorScheme = ['#3b82f6'],
  height = 400,
  width = '100%',
  className = '',
  showLegend = true,
  showTooltip = true,
  showGrid = true,
  formatValue
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <p className="font-medium text-foreground">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {formatValue ? formatValue(entry.value) : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`bg-card border border-border rounded-xl p-6 ${className}`}>
      <div className="mb-4">
        {title && <h3 className="text-lg font-semibold text-foreground mb-1">{title}</h3>}
        {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      
      <div style={{ height, width }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />}
            <XAxis 
              dataKey={xAxisKey} 
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              tickFormatter={formatValue}
            />
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            
            <Area 
              type="monotone" 
              dataKey={yAxisKey} 
              fill={colorScheme[0]} 
              stroke={colorScheme[0]}
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const ProfessionalPieChart: React.FC<ProfessionalVisualizationProps> = ({
  data,
  title,
  subtitle,
  xAxisKey = 'name',
  yAxisKey = 'value',
  colorScheme = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1'],
  height = 400,
  width = '100%',
  className = '',
  showLegend = true,
  showTooltip = true,
  formatValue
}) => {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
          <p className="font-medium text-foreground">{payload[0].name}</p>
          <p className="text-sm text-foreground">
            {formatValue ? formatValue(payload[0].value) : payload[0].value}
          </p>
          <p className="text-xs text-muted-foreground">
            {(payload[0].percentage || 0).toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={`bg-card border border-border rounded-xl p-6 ${className}`}>
      <div className="mb-4">
        {title && <h3 className="text-lg font-semibold text-foreground mb-1">{title}</h3>}
        {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      
      <div style={{ height, width }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            {showTooltip && <Tooltip content={<CustomTooltip />} />}
            {showLegend && <Legend />}
            
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey={yAxisKey}
              nameKey={xAxisKey}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colorScheme[index % colorScheme.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export interface DashboardWidgetProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  value: string | number;
  change?: number; // Positive for increase, negative for decrease
  changeLabel?: string;
  trend?: 'up' | 'down';
  footer?: React.ReactNode;
  className?: string;
}

export const DashboardWidget: React.FC<DashboardWidgetProps> = ({
  title,
  subtitle,
  icon,
  value,
  change,
  changeLabel,
  trend,
  footer,
  className = ''
}) => {
  return (
    <div className={`bg-card border border-border rounded-xl p-6 ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            {icon}
            <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
          </div>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        {change !== undefined && (
          <div className={`flex items-center gap-1 text-sm ${
            trend === 'up' ? 'text-emerald-500' : 'text-red-500'
          }`}>
            {trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingUp className="w-4 h-4 rotate-180" />}
            <span>{change > 0 ? '+' : ''}{change}%</span>
          </div>
        )}
      </div>
      
      <div className="mt-4">
        <p className="text-3xl font-bold text-foreground">{value}</p>
        {changeLabel && <p className="text-xs text-muted-foreground mt-1">{changeLabel}</p>}
      </div>
      
      {footer && <div className="mt-4 pt-4 border-t border-border">{footer}</div>}
    </div>
  );
};

export interface DataExplorerProps {
  data: any[];
  columns: Array<{
    key: string;
    label: string;
    type?: 'text' | 'number' | 'date' | 'boolean';
    sortable?: boolean;
    searchable?: boolean;
  }>;
  title?: string;
  description?: string;
  onRowClick?: (row: any) => void;
  className?: string;
}

export const DataExplorer: React.FC<DataExplorerProps> = ({
  data,
  columns,
  title,
  description,
  onRowClick,
  className = ''
}) => {
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const sortedData = useMemo(() => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [data, sortConfig]);

  const filteredData = useMemo(() => {
    if (!searchTerm) return sortedData;

    return sortedData.filter(row => {
      return Object.values(row).some(value =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      );
    });
  }, [sortedData, searchTerm]);

  const handleSort = (key: string) => {
    let direction: 'asc' | 'desc' = 'asc';
    if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  return (
    <div className={`bg-card border border-border rounded-xl ${className}`}>
      <div className="p-6 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          {title && <h2 className="text-xl font-bold text-foreground">{title}</h2>}
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              {columns.map(column => (
                <th 
                  key={column.key}
                  className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider"
                >
                  {column.sortable ? (
                    <button
                      onClick={() => handleSort(column.key)}
                      className="flex items-center gap-1 hover:text-foreground transition-colors"
                    >
                      {column.label}
                      {sortConfig?.key === column.key && (
                        <ChevronDown className={`w-4 h-4 ${sortConfig.direction === 'desc' ? 'rotate-180' : ''}`} />
                      )}
                    </button>
                  ) : (
                    column.label
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filteredData.map((row, rowIndex) => (
              <tr 
                key={rowIndex} 
                className={`hover:bg-muted/50 transition-colors ${
                  onRowClick ? 'cursor-pointer' : ''
                }`}
                onClick={() => onRowClick && onRowClick(row)}
              >
                {columns.map(column => (
                  <td key={column.key} className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                    {column.type === 'date' 
                      ? new Date(row[column.key]).toLocaleDateString() 
                      : String(row[column.key])
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {filteredData.length === 0 && (
        <div className="py-12 text-center text-muted-foreground">
          <Database className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No data found</p>
          <p className="text-sm mt-1">Try adjusting your search or filter criteria</p>
        </div>
      )}
    </div>
  );
};

// Export all visualization components
export {
  ProfessionalBarChart,
  ProfessionalLineChart,
  ProfessionalAreaChart,
  ProfessionalPieChart,
  DashboardWidget,
  DataExplorer
};

// Default export
export default {
  ProfessionalBarChart,
  ProfessionalLineChart,
  ProfessionalAreaChart,
  ProfessionalPieChart,
  DashboardWidget,
  DataExplorer
};