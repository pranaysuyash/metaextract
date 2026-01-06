/**
 * User Segmentation - User type breakdown for analytics dashboard
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Users, 
  User, 
  UserPlus, 
  Calendar, 
  TrendingUp, 
  BarChart3,
  PieChart,
  Activity,
  FileText,
  DollarSign
} from 'lucide-react';
import { 
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';

interface UserSegment {
  name: string;
  value: number;
  percentage: number;
  color: string;
  users: number;
  activity: number;
  conversion: number;
}

interface UserSegmentationProps {
  dateRange?: string;
}

export const UserSegmentation: React.FC<UserSegmentationProps> = ({ 
  dateRange = 'Last 30 days' 
}) => {
  // Mock data for user segments
  const userSegments: UserSegment[] = [
    { 
      name: 'Free Tier', 
      value: 45, 
      percentage: 45, 
      color: '#6b7280', 
      users: 4500,
      activity: 12000,
      conversion: 2
    },
    { 
      name: 'Starter', 
      value: 25, 
      percentage: 25, 
      color: '#3b82f6', 
      users: 2500,
      activity: 8000,
      conversion: 15
    },
    { 
      name: 'Pro', 
      value: 20, 
      percentage: 20, 
      color: '#10b981', 
      users: 2000,
      activity: 15000,
      conversion: 35
    },
    { 
      name: 'Enterprise', 
      value: 10, 
      percentage: 10, 
      color: '#8b5cf6', 
      users: 1000,
      activity: 8000,
      conversion: 65
    }
  ];

  // Mock data for user activity over time
  const activityData = [
    { date: 'Jan 1', free: 120, starter: 80, pro: 60, enterprise: 30 },
    { date: 'Jan 2', free: 130, starter: 85, pro: 65, enterprise: 32 },
    { date: 'Jan 3', free: 125, starter: 82, pro: 62, enterprise: 31 },
    { date: 'Jan 4', free: 140, starter: 90, pro: 70, enterprise: 35 },
    { date: 'Jan 5', free: 135, starter: 88, pro: 68, enterprise: 34 },
    { date: 'Jan 6', free: 150, starter: 95, pro: 75, enterprise: 38 },
    { date: 'Jan 7', free: 145, starter: 92, pro: 72, enterprise: 36 },
  ];

  // Mock data for conversion rates
  const conversionData = [
    { tier: 'Free', rate: 2.1 },
    { tier: 'Starter', rate: 15.3 },
    { tier: 'Pro', rate: 35.7 },
    { tier: 'Enterprise', rate: 65.2 },
  ];

  const COLORS = userSegments.map(segment => segment.color);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">User Segmentation</h2>
          <p className="text-slate-300 text-sm">User distribution by tier for {dateRange}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart - User Distribution */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <PieChart className="w-5 h-5 text-primary" />
              User Distribution by Tier
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                  <Pie
                    data={userSegments}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    nameKey="name"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {userSegments.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Legend />
                </RechartsPieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Segment Details */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Users className="w-5 h-5 text-primary" />
              Segment Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {userSegments.map((segment, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-4 h-4 rounded-full" 
                      style={{ backgroundColor: segment.color }}
                    ></div>
                    <div>
                      <h3 className="font-medium text-white">{segment.name}</h3>
                      <p className="text-sm text-slate-300">{segment.users.toLocaleString()} users</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-white">{segment.percentage}%</p>
                    <p className="text-sm text-slate-300">{segment.conversion}% conversion</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Over Time */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Activity by Tier Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={activityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                  <Bar dataKey="free" fill="#6b7280" name="Free Tier" />
                  <Bar dataKey="starter" fill="#3b82f6" name="Starter" />
                  <Bar dataKey="pro" fill="#10b981" name="Pro" />
                  <Bar dataKey="enterprise" fill="#8b5cf6" name="Enterprise" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Conversion Rates */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              Conversion Rates by Tier
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={{}} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={conversionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="tier" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" domain={[0, 100]} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line 
                    type="monotone" 
                    dataKey="rate" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Segment Performance Summary */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            Segment Performance Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Tier</th>
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Users</th>
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Activity</th>
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Conversion</th>
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Revenue</th>
                  <th className="text-left py-3 px-4 text-slate-300 font-medium">Growth</th>
                </tr>
              </thead>
              <tbody>
                {userSegments.map((segment, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-muted/10' : ''}>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: segment.color }}
                        ></div>
                        <span className="text-white font-medium">{segment.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-white">{segment.users.toLocaleString()}</td>
                    <td className="py-3 px-4 text-white">{segment.activity.toLocaleString()}</td>
                    <td className="py-3 px-4">
                      <span className="text-white font-medium">{segment.conversion}%</span>
                    </td>
                    <td className="py-3 px-4 text-white">
                      {segment.name === 'Free' ? '$0' : 
                       segment.name === 'Starter' ? '$2,400' : 
                       segment.name === 'Pro' ? '$10,500' : '$15,600'}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-sm ${segment.conversion > 20 ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {segment.conversion > 20 ? '+12.5%' : '+5.2%'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserSegmentation;