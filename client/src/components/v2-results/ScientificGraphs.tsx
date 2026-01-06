import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  BarChart3, 
  Activity, 
  Eye, 
  Database,
  TrendingUp,
  Thermometer,
  Gauge
} from 'lucide-react';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';

interface ScientificDataPoint {
  name: string;
  value: number;
  unit?: string;
  confidence?: number;
}

interface ScientificGraphsProps {
  data: ScientificDataPoint[];
  title?: string;
  chartType?: 'bar' | 'line' | 'area';
  yAxisLabel?: string;
}

export const ScientificGraphs: React.FC<ScientificGraphsProps> = ({ 
  data, 
  title = 'Scientific Data Visualization',
  chartType = 'bar',
  yAxisLabel = 'Value'
}) => {
  const renderChart = () => {
    const chartProps = {
      data,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    switch (chartType) {
      case 'line':
        return (
          <LineChart {...chartProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="#3b82f6" 
              activeDot={{ r: 8 }} 
              name={yAxisLabel}
            />
          </LineChart>
        );
      
      case 'area':
        return (
          <AreaChart {...chartProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="#8b5cf6" 
              fill="#8b5cf6" 
              fillOpacity={0.3} 
              name={yAxisLabel}
            />
          </AreaChart>
        );
      
      case 'bar':
      default:
        return (
          <BarChart {...chartProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Legend />
            <Bar 
              dataKey="value" 
              fill="#3b82f6" 
              name={yAxisLabel}
            />
          </BarChart>
        );
    }
  };

  // Calculate statistics
  const values = data.map(d => d.value);
  const average = values.reduce((sum, val) => sum + val, 0) / values.length;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const total = values.reduce((sum, val) => sum + val, 0);

  return (
    <div className="space-y-6">
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={{}} className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              {renderChart()}
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Statistics Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Gauge className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Average</p>
                <p className="text-lg font-bold text-white">{average.toFixed(2)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-500/10 rounded-lg">
                <TrendingUp className="w-5 h-5 text-emerald-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Maximum</p>
                <p className="text-lg font-bold text-white">{max}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Activity className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Minimum</p>
                <p className="text-lg font-bold text-white">{min}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <Database className="w-5 h-5 text-purple-500" />
              </div>
              <div>
                <p className="text-xs text-slate-300">Total</p>
                <p className="text-lg font-bold text-white">{total}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Table */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-primary" />
            Raw Data
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Name</th>
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Value</th>
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Unit</th>
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-muted/10' : ''}>
                    <td className="py-3 px-4 text-white">{item.name}</td>
                    <td className="py-3 px-4 text-white font-medium">{item.value}</td>
                    <td className="py-3 px-4 text-slate-300">{item.unit || 'N/A'}</td>
                    <td className="py-3 px-4">
                      {item.confidence !== undefined ? (
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-muted rounded-full h-2">
                            <div 
                              className="bg-primary h-2 rounded-full" 
                              style={{ width: `${item.confidence}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-slate-300">{item.confidence}%</span>
                        </div>
                      ) : (
                        <span className="text-slate-300">N/A</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Data Quality Assessment */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Eye className="w-5 h-5 text-primary" />
            Data Quality Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">Data Completeness</span>
                <span className="text-white font-medium">
                  {data.filter(d => d.value !== undefined).length}/{data.length} values
                </span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-emerald-500 h-2 rounded-full" 
                  style={{ 
                    width: `${(data.filter(d => d.value !== undefined).length / data.length) * 100}%` 
                  }}
                ></div>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-300">Average Confidence</span>
                <span className="text-white font-medium">
                  {data.length > 0 
                    ? Math.round(data.reduce((sum, d) => sum + (d.confidence || 0), 0) / data.length) + '%' 
                    : '0%'}
                </span>
              </div>
              <div className="w-full bg-muted rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full" 
                  style={{ 
                    width: data.length > 0 
                      ? `${Math.round(data.reduce((sum, d) => sum + (d.confidence || 0), 0) / data.length)}%` 
                      : '0%' 
                  }}
                ></div>
              </div>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-white/10">
            <h4 className="text-sm font-semibold text-white mb-2">Quality Indicators</h4>
            <div className="flex flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                <span className="text-xs text-slate-300">High Completeness</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span className="text-xs text-slate-300">Good Confidence</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                <span className="text-xs text-slate-300">Valid Format</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};