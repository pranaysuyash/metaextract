/**
 * Advanced Analytics Dashboard - Main dashboard component
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  FileText, 
  DollarSign, 
  Calendar,
  Download,
  Filter,
  Activity,
  Eye,
  Upload,
  UserPlus
} from 'lucide-react';
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
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';

interface MetricCardProps {
  title: string;
  value: string | number;
  change: string;
  icon: React.ReactNode;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, icon, color }) => {
  return (
    <Card className="bg-card border-white/10">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-300">{title}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className={`text-xs mt-1 ${change.startsWith('+') ? 'text-emerald-400' : 'text-red-400'}`}>
              {change}
            </p>
          </div>
          <div className={`p-3 rounded-lg ${color}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

interface DateRangeFilterProps {
  onDateChange: (start: Date, end: Date) => void;
}

const DateRangeFilter: React.FC<DateRangeFilterProps> = ({ onDateChange }) => {
  const [startDate, setStartDate] = useState<string>('2025-01-01');
  const [endDate, setEndDate] = useState<string>('2025-01-31');

  const handleApply = () => {
    onDateChange(new Date(startDate), new Date(endDate));
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2">
        <Calendar className="w-4 h-4 text-slate-300" />
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="px-3 py-1 bg-muted border border-white/10 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary"
        />
        <span className="text-slate-300">to</span>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="px-3 py-1 bg-muted border border-white/10 rounded text-white text-sm focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>
      <Button variant="outline" size="sm" onClick={handleApply}>
        Apply
      </Button>
    </div>
  );
};

const AnalyticsDashboard: React.FC = () => {
  const [dateRange, setDateRange] = useState<[Date, Date]>([
    new Date(2025, 0, 1), // Jan 1, 2025
    new Date(2025, 0, 31)  // Jan 31, 2025
  ]);

  // Mock data for metrics
  const metrics = [
    { title: 'Total Uploads', value: '12,458', change: '+12.5%', icon: <Upload className="w-5 h-5 text-white" />, color: 'bg-blue-500/20' },
    { title: 'Conversions', value: '3,241', change: '+8.2%', icon: <FileText className="w-5 h-5 text-white" />, color: 'bg-emerald-500/20' },
    { title: 'Active Users', value: '842', change: '+5.7%', icon: <Users className="w-5 h-5 text-white" />, color: 'bg-purple-500/20' },
    { title: 'Revenue', value: '$24,568', change: '+15.3%', icon: <DollarSign className="w-5 h-5 text-white" />, color: 'bg-amber-500/20' },
  ];

  // Mock data for charts
  const uploadData = [
    { date: 'Jan 1', uploads: 45, conversions: 12 },
    { date: 'Jan 2', uploads: 52, conversions: 15 },
    { date: 'Jan 3', uploads: 48, conversions: 14 },
    { date: 'Jan 4', uploads: 61, conversions: 18 },
    { date: 'Jan 5', uploads: 55, conversions: 16 },
    { date: 'Jan 6', uploads: 67, conversions: 20 },
    { date: 'Jan 7', uploads: 72, conversions: 22 },
  ];

  const userData = [
    { name: 'New Users', value: 400 },
    { name: 'Returning', value: 300 },
    { name: 'Inactive', value: 300 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

  const tierData = [
    { name: 'Free', value: 400 },
    { name: 'Starter', value: 300 },
    { name: 'Pro', value: 300 },
    { name: 'Enterprise', value: 200 },
  ];

  const tierColors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const handleDateChange = (start: Date, end: Date) => {
    setDateRange([start, end]);
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Analytics Dashboard</h1>
            <p className="text-slate-300">Monitor platform performance and user engagement</p>
          </div>
          <Button variant="outline" className="gap-2">
            <Download className="w-4 h-4" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Date Range Filter */}
      <div className="mb-6">
        <DateRangeFilter onDateChange={handleDateChange} />
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {metrics.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            change={metric.change}
            icon={metric.icon}
            color={metric.color}
          />
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Uploads vs Conversions Chart */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Uploads vs Conversions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={uploadData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Bar dataKey="uploads" fill="#3b82f6" name="Uploads" />
                  <Bar dataKey="conversions" fill="#10b981" name="Conversions" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* User Distribution */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Users className="w-5 h-5 text-primary" />
              User Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                  <Pie
                    data={userData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {userData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Additional Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tier Distribution */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              Tier Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={uploadData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Bar dataKey="uploads" fill="#8b5cf6" name="Free Tier" />
                  <Bar dataKey="conversions" fill="#ec4899" name="Paid Tier" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Revenue by Tier */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-primary" />
              Revenue by Tier
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                  <Pie
                    data={tierData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {tierData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={tierColors[index % tierColors.length]} />
                    ))}
                  </Pie>
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="mt-6">
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-muted/20 rounded">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-500/20 rounded">
                    <Upload className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <p className="font-medium text-white">New file uploaded</p>
                    <p className="text-sm text-slate-300">by John Doe • 5 minutes ago</p>
                  </div>
                </div>
                <Badge variant="outline">Free Tier</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-muted/20 rounded">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500/20 rounded">
                    <UserPlus className="w-4 h-4 text-blue-400" />
                  </div>
                  <div>
                    <p className="font-medium text-white">New user registered</p>
                    <p className="text-sm text-slate-300">Sarah Johnson • 12 minutes ago</p>
                  </div>
                </div>
                <Badge variant="outline">Trial</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-muted/20 rounded">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-500/20 rounded">
                    <FileText className="w-4 h-4 text-purple-400" />
                  </div>
                  <div>
                    <p className="font-medium text-white">Report generated</p>
                    <p className="text-sm text-slate-300">by Alex Smith • 1 hour ago</p>
                  </div>
                </div>
                <Badge variant="outline">Pro Tier</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;