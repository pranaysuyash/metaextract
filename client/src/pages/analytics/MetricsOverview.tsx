/**
 * Metrics Overview - KPI cards for analytics dashboard
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  FileText, 
  Users, 
  DollarSign, 
  TrendingUp, 
  Eye,
  Calendar,
  Activity,
  BarChart3
} from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change: string;
  icon: React.ReactNode;
  color: string;
  trend?: 'up' | 'down';
  description?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  change, 
  icon, 
  color, 
  trend,
  description 
}) => {
  return (
    <Card className="bg-card border-white/10">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-slate-300">{title}</p>
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
            <div className="flex items-center gap-1 mt-1">
              {trend === 'up' ? (
                <TrendingUp className="w-3 h-3 text-emerald-400" />
              ) : trend === 'down' ? (
                <TrendingUp className="w-3 h-3 text-red-400 rotate-180" />
              ) : null}
              <span className={`text-xs ${change.startsWith('+') ? 'text-emerald-400' : 'text-red-400'}`}>
                {change}
              </span>
            </div>
            {description && (
              <p className="text-xs text-slate-500 mt-2">{description}</p>
            )}
          </div>
          <div className={`p-3 rounded-lg ${color}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

interface MetricsOverviewProps {
  dateRange?: string;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({ 
  dateRange = 'Last 30 days' 
}) => {
  // Mock data for metrics
  const metrics = [
    { 
      title: 'Total Uploads', 
      value: '12,458', 
      change: '+12.5%', 
      icon: <Upload className="w-5 h-5 text-white" />, 
      color: 'bg-blue-500/20',
      trend: 'up',
      description: 'Files processed in period'
    },
    { 
      title: 'Conversions', 
      value: '3,241', 
      change: '+8.2%', 
      icon: <FileText className="w-5 h-5 text-white" />, 
      color: 'bg-emerald-500/20',
      trend: 'up',
      description: 'Successful extractions'
    },
    { 
      title: 'Active Users', 
      value: '842', 
      change: '+5.7%', 
      icon: <Users className="w-5 h-5 text-white" />, 
      color: 'bg-purple-500/20',
      trend: 'up',
      description: 'Unique users this period'
    },
    { 
      title: 'Revenue', 
      value: '$24,568', 
      change: '+15.3%', 
      icon: <DollarSign className="w-5 h-5 text-white" />, 
      color: 'bg-amber-500/20',
      trend: 'up',
      description: 'Monthly recurring revenue'
    },
    { 
      title: 'Avg. Processing Time', 
      value: '2.4s', 
      change: '-3.2%', 
      icon: <Activity className="w-5 h-5 text-white" />, 
      color: 'bg-cyan-500/20',
      trend: 'down',
      description: 'Faster than last period'
    },
    { 
      title: 'User Satisfaction', 
      value: '4.7/5', 
      change: '+0.2', 
      icon: <Eye className="w-5 h-5 text-white" />, 
      color: 'bg-pink-500/20',
      trend: 'up',
      description: 'Based on user feedback'
    },
    { 
      title: 'API Requests', 
      value: '45,231', 
      change: '+22.1%', 
      icon: <BarChart3 className="w-5 h-5 text-white" />, 
      color: 'bg-indigo-500/20',
      trend: 'up',
      description: 'Enterprise API usage'
    },
    { 
      title: 'Error Rate', 
      value: '0.3%', 
      change: '-0.1%', 
      icon: <Activity className="w-5 h-5 text-white" />, 
      color: 'bg-rose-500/20',
      trend: 'down',
      description: 'System reliability metric'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Key Metrics</h2>
          <p className="text-slate-300 text-sm">Performance overview for {dateRange}</p>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-slate-300" />
          <span className="text-sm text-slate-300">{dateRange}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <MetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            change={metric.change}
            icon={metric.icon}
            color={metric.color}
            trend={metric.trend}
            description={metric.description}
          />
        ))}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2 text-sm">
              <TrendingUp className="w-4 h-4 text-primary" />
              Growth Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-400">+12.5%</div>
            <p className="text-slate-300 text-sm mt-1">MoM growth in usage</p>
            <div className="mt-3 w-full bg-muted rounded-full h-2">
              <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '75%' }}></div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2 text-sm">
              <Activity className="w-4 h-4 text-primary" />
              Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">99.7%</div>
            <p className="text-slate-300 text-sm mt-1">Uptime this month</p>
            <div className="mt-3 w-full bg-muted rounded-full h-2">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '99.7%' }}></div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2 text-sm">
              <Users className="w-4 h-4 text-primary" />
              Retention
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-400">84.3%</div>
            <p className="text-slate-300 text-sm mt-1">Monthly active users returning</p>
            <div className="mt-3 w-full bg-muted rounded-full h-2">
              <div className="bg-purple-500 h-2 rounded-full" style={{ width: '84.3%' }}></div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MetricsOverview;