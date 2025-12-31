import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Activity, 
  AlertTriangle, 
  Clock, 
  Database, 
  TrendingUp, 
  Server,
  CheckCircle,
  XCircle
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

interface MonitoringData {
  health_status: string;
  timestamp: string;
  metrics: {
    total_extractions: number;
    successful_extractions: number;
    failed_extractions: number;
    success_rate: number;
    avg_processing_time_ms: number;
    min_processing_time_ms: number;
    max_processing_time_ms: number;
    extractions_per_minute: number;
    total_runtime_seconds: number;
    tier_usage: Record<string, number>;
    file_type_usage: Record<string, number>;
    recent_errors: Record<string, number>;
  };
}

const MonitoringDashboard: React.FC = () => {
  const [monitoringData, setMonitoringData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMonitoringData = async () => {
      try {
        const response = await fetch('/api/monitoring/status');
        if (!response.ok) {
          throw new Error('Failed to fetch monitoring data');
        }
        const data = await response.json();
        setMonitoringData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchMonitoringData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchMonitoringData, 5000);
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

  if (!monitoringData) {
    return (
      <div className="p-6 text-center">
        <Server className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-lg font-medium">No Data Available</h3>
        <p className="mt-1 text-sm text-gray-500">Monitoring data is not available</p>
      </div>
    );
  }

  // Prepare data for charts
  const tierUsageData = Object.entries(monitoringData.metrics.tier_usage).map(([tier, count]) => ({
    name: tier,
    count
  }));

  const fileTypeData = Object.entries(monitoringData.metrics.file_type_usage).map(([type, count]) => ({
    name: type,
    count
  }));

  const errorData = Object.entries(monitoringData.metrics.recent_errors).map(([error, count]) => ({
    name: error,
    count
  }));

  // Color palette for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <Activity className="mr-2 h-8 w-8" />
          System Monitoring Dashboard
        </h1>
        <Badge variant={monitoringData.health_status === 'operational' ? 'default' : 
                      monitoringData.health_status === 'degraded' ? 'secondary' : 'destructive'}>
          {monitoringData.health_status.toUpperCase()}
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Success Rate Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(monitoringData.metrics.success_rate * 100).toFixed(2)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {monitoringData.metrics.successful_extractions} successful / {monitoringData.metrics.total_extractions} total
            </p>
          </CardContent>
        </Card>

        {/* Avg Processing Time Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Processing Time</CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {monitoringData.metrics.avg_processing_time_ms.toFixed(2)}ms
            </div>
            <p className="text-xs text-muted-foreground">
              Min: {monitoringData.metrics.min_processing_time_ms.toFixed(2)}ms | Max: {monitoringData.metrics.max_processing_time_ms.toFixed(2)}ms
            </p>
          </CardContent>
        </Card>

        {/* Extractions Per Minute Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Extractions/Minute</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {monitoringData.metrics.extractions_per_minute.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              Current throughput
            </p>
          </CardContent>
        </Card>

        {/* Error Rate Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {((1 - monitoringData.metrics.success_rate) * 100).toFixed(2)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {monitoringData.metrics.failed_extractions} failed
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tier Usage Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Tier Usage Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={tierUsageData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {tierUsageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* File Type Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>File Type Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={fileTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Errors */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Errors</CardTitle>
          </CardHeader>
          <CardContent>
            {errorData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={errorData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#ff4d4d" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No recent errors detected
              </div>
            )}
          </CardContent>
        </Card>

        {/* System Health */}
        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span>Health Status</span>
                <Badge variant={monitoringData.health_status === 'operational' ? 'default' : 
                              monitoringData.health_status === 'degraded' ? 'secondary' : 'destructive'}>
                  {monitoringData.health_status}
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <span>Total Runtime</span>
                <span>{(monitoringData.metrics.total_runtime_seconds / 3600).toFixed(2)} hours</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span>Total Extractions</span>
                <span>{monitoringData.metrics.total_extractions}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span>Successful Extractions</span>
                <span>{monitoringData.metrics.successful_extractions}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span>Failed Extractions</span>
                <span>{monitoringData.metrics.failed_extractions}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MonitoringDashboard;