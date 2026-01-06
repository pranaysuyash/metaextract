/**
 * Trend Charts - Time-series graphs for analytics dashboard
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
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
  Area,
  ComposedChart,
  Scatter,
  Cell
} from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { 
  Calendar,
  TrendingUp,
  TrendingDown,
  Activity,
  Users,
  FileText,
  DollarSign
} from 'lucide-react';

interface TimeSeriesData {
  date: string;
  value: number;
  [key: string]: number | string;
}

interface TrendChartProps {
  title: string;
  data: TimeSeriesData[];
  dataKey: string;
  color: string;
  icon: React.ReactNode;
  description?: string;
  chartType?: 'line' | 'bar' | 'area';
}

export const TrendChart: React.FC<TrendChartProps> = ({ 
  title, 
  data, 
  dataKey, 
  color, 
  icon, 
  description,
  chartType = 'line'
}) => {
  const renderChart = () => {
    const chartProps = {
      data,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    switch (chartType) {
      case 'bar':
        return (
          <BarChart {...chartProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey={dataKey} fill={color} />
          </BarChart>
        );
      
      case 'area':
        return (
          <AreaChart {...chartProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Area type="monotone" dataKey={dataKey} fill={color} stroke={color} />
          </AreaChart>
        );
      
      case 'line':
      default:
        return (
          <LineChart {...chartProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Line 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        );
    }
  };

  return (
    <Card className="bg-card border-white/10">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={{}} className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </ChartContainer>
        {description && (
          <p className="text-sm text-slate-300 mt-4">{description}</p>
        )}
      </CardContent>
    </Card>
  );
};

interface TrendChartsProps {
  dateRange?: string;
}

export const TrendCharts: React.FC<TrendChartsProps> = ({ 
  dateRange = 'Last 30 days' 
}) => {
  // Mock data for different metrics
  const uploadData: TimeSeriesData[] = [
    { date: 'Jan 1', uploads: 45, conversions: 12 },
    { date: 'Jan 2', uploads: 52, conversions: 15 },
    { date: 'Jan 3', uploads: 48, conversions: 14 },
    { date: 'Jan 4', uploads: 61, conversions: 18 },
    { date: 'Jan 5', uploads: 55, conversions: 16 },
    { date: 'Jan 6', uploads: 67, conversions: 20 },
    { date: 'Jan 7', uploads: 72, conversions: 22 },
    { date: 'Jan 8', uploads: 68, conversions: 19 },
    { date: 'Jan 9', uploads: 75, conversions: 24 },
    { date: 'Jan 10', uploads: 82, conversions: 26 },
    { date: 'Jan 11', uploads: 78, conversions: 23 },
    { date: 'Jan 12', uploads: 85, conversions: 28 },
    { date: 'Jan 13', uploads: 92, conversions: 30 },
    { date: 'Jan 14', uploads: 88, conversions: 27 },
    { date: 'Jan 15', uploads: 95, conversions: 32 },
  ];

  const revenueData: TimeSeriesData[] = [
    { date: 'Week 1', revenue: 1200, profit: 800 },
    { date: 'Week 2', revenue: 1500, profit: 1000 },
    { date: 'Week 3', revenue: 1800, profit: 1200 },
    { date: 'Week 4', revenue: 2200, profit: 1500 },
  ];

  const userData: TimeSeriesData[] = [
    { date: 'Mon', newUsers: 12, returning: 45 },
    { date: 'Tue', newUsers: 18, returning: 52 },
    { date: 'Wed', newUsers: 15, returning: 48 },
    { date: 'Thu', newUsers: 22, returning: 61 },
    { date: 'Fri', newUsers: 28, returning: 72 },
    { date: 'Sat', newUsers: 19, returning: 58 },
    { date: 'Sun', newUsers: 14, returning: 42 },
  ];

  const performanceData: TimeSeriesData[] = [
    { date: 'Jan 1', responseTime: 2.4, errorRate: 0.3 },
    { date: 'Jan 2', responseTime: 2.3, errorRate: 0.2 },
    { date: 'Jan 3', responseTime: 2.2, errorRate: 0.2 },
    { date: 'Jan 4', responseTime: 2.1, errorRate: 0.1 },
    { date: 'Jan 5', responseTime: 2.0, errorRate: 0.1 },
    { date: 'Jan 6', responseTime: 1.9, errorRate: 0.1 },
    { date: 'Jan 7', responseTime: 1.8, errorRate: 0.0 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Trend Analysis</h2>
          <p className="text-slate-300 text-sm">Performance trends for {dateRange}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TrendChart
          title="Uploads & Conversions"
          data={uploadData}
          dataKey="uploads"
          color="#3b82f6"
          icon={<Activity className="w-5 h-5 text-primary" />}
          description="Daily uploads and successful conversions"
          chartType="line"
        />

        <TrendChart
          title="User Growth"
          data={userData}
          dataKey="newUsers"
          color="#10b981"
          icon={<Users className="w-5 h-5 text-primary" />}
          description="New vs returning users by day of week"
          chartType="bar"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TrendChart
          title="Revenue Growth"
          data={revenueData}
          dataKey="revenue"
          color="#f59e0b"
          icon={<DollarSign className="w-5 h-5 text-primary" />}
          description="Weekly revenue and profit trends"
          chartType="area"
        />

        <TrendChart
          title="Performance Metrics"
          data={performanceData}
          dataKey="responseTime"
          color="#8b5cf6"
          icon={<TrendingUp className="w-5 h-5 text-primary" />}
          description="Response time and error rate trends"
          chartType="line"
        />
      </div>

      {/* Combined chart */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            Combined Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer config={{}} className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={uploadData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis yAxisId="left" stroke="#9CA3AF" />
                <YAxis yAxisId="right" orientation="right" stroke="#9CA3AF" />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Legend />
                <Bar yAxisId="left" dataKey="uploads" fill="#3b82f6" name="Uploads" />
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="conversions" 
                  stroke="#10b981" 
                  name="Conversions" 
                  strokeWidth={2}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrendCharts;