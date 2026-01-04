import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  Server,
  BarChart3
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface AnalyticsData {
  timestamp: string;
  failure_analysis: {
    error_counts: Record<string, number>;
    error_by_tier: Record<string, Record<string, number>>;
    error_by_filetype: Record<string, Record<string, number>>;
    failure_rates_by_tier: Record<string, {
      total: number;
      failed: number;
      failure_rate: number;
    }>;
    failure_rates_by_filetype: Record<string, {
      total: number;
      failed: number;
      failure_rate: number;
    }>;
  };
  performance_analysis: {
    overall_performance: {
      count: number;
      avg: number;
      median: number;
      min: number;
      max: number;
      std_dev: number;
    };
    performance_by_tier: Record<string, {
      count: number;
      avg: number;
      median: number;
      min: number;
      max: number;
      std_dev: number;
    }>;
    performance_by_filetype: Record<string, {
      count: number;
      avg: number;
      median: number;
      min: number;
      max: number;
      std_dev: number;
    }>;
    outliers_count: number;
    outlier_percentage: number;
  };
  bottleneck_analysis: Array<{
    type: string;
    severity: string;
    description: string;
    recommendation: string;
  }>;
  trend_analysis: {
    hourly_metrics: Array<{
      hour: number;
      timestamp: number;
      total_extractions: number;
      successful_extractions: number;
      failed_extractions: number;
      success_rate: number;
      avg_processing_time: number;
    }>;
    success_rate_trend: number;
    processing_time_trend: number;
    trend_period_hours: number;
  };
  recommendations: string[];
}

const AnalyticsDashboard: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        const response = await fetch('/api/analytics/report');
        if (!response.ok) {
          throw new Error('Failed to fetch analytics data');
        }
        const data = await response.json();
        setAnalyticsData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchAnalyticsData, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
        <h3 className="mt-2 text-lg font-medium">Error Loading Data</h3>
        <p className="mt-1 text-sm text-gray-500">{error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="p-6 text-center">
        <Server className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-lg font-medium">No Data Available</h3>
        <p className="mt-1 text-sm text-gray-500">Analytics data is not available</p>
      </div>
    );
  }

  // Prepare data for charts
  const tierPerformanceData = Object.entries(analyticsData.performance_analysis.performance_by_tier).map(([tier, perf]) => ({
    name: tier,
    avg: perf.avg,
    median: perf.median,
    min: perf.min,
    max: perf.max
  }));

  const filetypePerformanceData = Object.entries(analyticsData.performance_analysis.performance_by_filetype).map(([type, perf]) => ({
    name: type,
    avg: perf.avg,
    median: perf.median,
    min: perf.min,
    max: perf.max
  }));

  const errorData = Object.entries(analyticsData.failure_analysis.error_counts).map(([error, count]) => ({
    name: error,
    count
  }));

  const tierFailureData = Object.entries(analyticsData.failure_analysis.failure_rates_by_tier).map(([tier, data]) => ({
    name: tier,
    failure_rate: data.failure_rate * 100, // Convert to percentage
    success_rate: (1 - data.failure_rate) * 100
  }));

  // Color palette for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <BarChart3 className="mr-2 h-8 w-8" />
          Analytics Dashboard
        </h1>
        <Badge variant="default">
          Updated: {new Date(analyticsData.timestamp).toLocaleTimeString()}
        </Badge>
      </div>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-5 space-y-2">
            {analyticsData.recommendations.map((rec, index) => (
              <li key={index} className="text-sm">{rec}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance by Tier */}
        <Card>
          <CardHeader>
            <CardTitle>Performance by Tier</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tierPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg" name="Avg Processing Time (ms)" fill="#8884d8" />
                <Bar dataKey="max" name="Max Processing Time (ms)" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Performance by File Type */}
        <Card>
          <CardHeader>
            <CardTitle>Performance by File Type</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={filetypePerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg" name="Avg Processing Time (ms)" fill="#8884d8" />
                <Bar dataKey="max" name="Max Processing Time (ms)" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Failure Rates by Tier */}
        <Card>
          <CardHeader>
            <CardTitle>Failure Rates by Tier</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tierFailureData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis unit="%" />
                <Tooltip />
                <Legend />
                <Bar dataKey="failure_rate" name="Failure Rate (%)" fill="#ff4d4d" />
                <Bar dataKey="success_rate" name="Success Rate (%)" fill="#4caf50" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Error Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Error Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={errorData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {errorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Bottleneck Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Bottleneck Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          {analyticsData.bottleneck_analysis.length > 0 ? (
            <div className="space-y-4">
              {analyticsData.bottleneck_analysis.map((bottleneck, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium">{bottleneck.description}</h4>
                      <p className="text-sm text-gray-600 mt-1">{bottleneck.recommendation}</p>
                    </div>
                    <Badge 
                      variant={bottleneck.severity === 'high' ? 'destructive' : 
                               bottleneck.severity === 'medium' ? 'secondary' : 'default'}
                    >
                      {bottleneck.severity}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No bottlenecks detected
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trend Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Trend Analysis (Last {analyticsData.trend_analysis.trend_period_hours} Hours)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={analyticsData.trend_analysis.hourly_metrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="hour" 
                tickFormatter={(value) => new Date(value * 3600 * 1000).toLocaleTimeString([], {hour: '2-digit'})}
              />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="success_rate" 
                name="Success Rate (%)" 
                stroke="#4caf50" 
                strokeWidth={2} 
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line 
                type="monotone" 
                dataKey="avg_processing_time" 
                name="Avg Processing Time (ms)" 
                stroke="#2196f3" 
                strokeWidth={2} 
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-800">Success Rate Trend</h4>
              <p className="text-2xl font-bold text-blue-600">
                {analyticsData.trend_analysis.success_rate_trend >= 0 ? '↗️' : '↘️'} 
                {analyticsData.trend_analysis.success_rate_trend.toFixed(4)}/hr
              </p>
              <p className="text-sm text-blue-600">
                {analyticsData.trend_analysis.success_rate_trend >= 0 ? 'Improving' : 'Declining'}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-medium text-purple-800">Processing Time Trend</h4>
              <p className="text-2xl font-bold text-purple-600">
                {analyticsData.trend_analysis.processing_time_trend >= 0 ? '↗️' : '↘️'} 
                {analyticsData.trend_analysis.processing_time_trend.toFixed(2)}ms/hr
              </p>
              <p className="text-sm text-purple-600">
                {analyticsData.trend_analysis.processing_time_trend >= 0 ? 'Slowing' : 'Improving'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsDashboard;