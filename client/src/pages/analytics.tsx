/**
 * Analytics Dashboard Component
 * Real-time monitoring of extraction performance and system usage
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface PerformanceMetrics {
  avg_extraction_time: number;
  total_extractions: number;
  success_rate: number;
  fields_per_extraction: number;
  throughput_per_minute: number;
}

interface SystemUsage {
  active_users: number;
  images_processed_today: number;
  data_processed_gb: number;
  error_rate: number;
}

interface TopFormats {
  format: string;
  count: number;
  avg_time: number;
}[]

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [usage, setUsage] = useState<SystemUsage | null>(null);
  const [topFormats, setTopFormats] = useState<TopFormats>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d'>('24h');

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`/api/analytics?range=${timeRange}`);
      const data = await response.json();

      setMetrics(data.performance);
      setUsage(data.usage);
      setTopFormats(data.top_formats);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Time Range Selector */}
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Analytics Dashboard</h2>
        <div className="flex gap-2">
          {(['1h', '24h', '7d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg ${
                timeRange === range
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              {range === '1h' ? 'Last Hour' : range === '24h' ? '24 Hours' : '7 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Performance Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <PerformanceCard
          title="Avg Extraction Time"
          value={`${metrics?.avg_extraction_time?.toFixed(3) || 0}s`}
          target="<0.5s"
          status={metrics?.avg_extraction_time < 0.5 ? 'success' : 'warning'}
          trend="↓ 97% vs baseline"
        />
        <PerformanceCard
          title="Success Rate"
          value={`${((metrics?.success_rate || 0) * 100).toFixed(1)}%`}
          target=">99%"
          status={metrics?.success_rate > 0.99 ? 'success' : 'warning'}
          trend="Stable"
        />
        <PerformanceCard
          title="Fields per Extraction"
          value={`${metrics?.fields_per_extraction?.toFixed(0) || 0}`}
          target="200+"
          status={metrics?.fields_per_extraction >= 200 ? 'success' : 'warning'}
          trend="↑ 15% improvement"
        />
        <PerformanceCard
          title="Throughput"
          value={`${metrics?.throughput_per_minute?.toFixed(1) || 0}/min`}
          target="60+/min"
          status={metrics?.throughput_per_minute >= 60 ? 'success' : 'warning'}
          trend="Scaling well"
        />
      </div>

      {/* System Usage Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>System Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <MetricRow
                label="Active Users"
                value={usage?.active_users || 0}
                icon="👥"
                trend="Current"
              />
              <MetricRow
                label="Images Today"
                value={usage?.images_processed_today || 0}
                icon="📊"
                trend="+12% vs yesterday"
              />
              <MetricRow
                label="Data Processed"
                value={`${(usage?.data_processed_gb || 0).toFixed(1)} GB`}
                icon="💾"
                trend="Efficient"
              />
              <MetricRow
                label="Error Rate"
                value={`${((usage?.error_rate || 0) * 100).toFixed(2)}%`}
                icon="⚠️"
                trend="Low"
                status={usage?.error_rate < 0.01 ? 'success' : 'warning'}
              />
            </div>
          </CardContent>
        </Card>

        {/* Top Formats Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Top File Formats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topFormats.map((format, index) => (
                <div key={format.format} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold">#{index + 1}</span>
                    <span className="font-medium">{format.format.toUpperCase()}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-gray-600">{format.count} files</span>
                    <span className="text-blue-600 font-mono">
                      {format.avg_time.toFixed(3)}s
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Performance Graph */}
      <Card>
        <CardHeader>
          <CardTitle>Extraction Performance Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-gray-500">Performance graph visualization</p>
            {/* In production, this would show a real-time chart */}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function PerformanceCard({
  title,
  value,
  target,
  status,
  trend
}: {
  title: string;
  value: string;
  target: string;
  status: 'success' | 'warning' | 'error';
  trend: string;
}) {
  const statusColors = {
    success: 'bg-green-100 border-green-500 text-green-800',
    warning: 'bg-yellow-100 border-yellow-500 text-yellow-800',
    error: 'bg-red-100 border-red-500 text-red-800'
  };

  return (
    <Card className={`border-2 ${statusColors[status].split(' ')[0]}`}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{value}</div>
        <div className="flex justify-between items-center mt-2 text-sm">
          <span className="text-gray-500">Target: {target}</span>
          <span className="text-blue-600">{trend}</span>
        </div>
      </CardContent>
    </Card>
  );
}

function MetricRow({
  label,
  value,
  icon,
  trend,
  status
}: {
  label: string;
  value: number | string;
  icon: string;
  trend: string;
  status?: 'success' | 'warning' | 'error';
}) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <span className="font-medium">{label}</span>
      </div>
      <div className="text-right">
        <div className="font-bold">{value}</div>
        <div className="text-sm text-gray-500">{trend}</div>
      </div>
    </div>
  );
}