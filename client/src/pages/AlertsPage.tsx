import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Activity,
  Server,
  TrendingUp
} from 'lucide-react';

interface Alert {
  name: string;
  message: string;
  severity: string;
  timestamp: string;
  metrics: any;
}

interface AlertStatus {
  active_rules: string[];
  recent_alerts: Alert[];
  severity_counts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  total_alerts: number;
}

const AlertsPage: React.FC = () => {
  const [alertStatus, setAlertStatus] = useState<AlertStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAlertStatus = async () => {
      try {
        const response = await fetch('/api/monitoring/alerts');
        if (!response.ok) {
          throw new Error('Failed to fetch alert status');
        }
        const data = await response.json();
        setAlertStatus(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchAlertStatus();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchAlertStatus, 15000); // Every 15 seconds
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

  if (!alertStatus) {
    return (
      <div className="p-6 text-center">
        <Server className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-lg font-medium">No Alert Data Available</h3>
        <p className="mt-1 text-sm text-gray-500">Alert monitoring data is not available</p>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'destructive';
      case 'high':
        return 'destructive';
      case 'medium':
        return 'secondary';
      case 'low':
        return 'default';
      default:
        return 'default';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'low':
        return <AlertTriangle className="h-4 w-4 text-blue-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <AlertTriangle className="mr-2 h-8 w-8" />
          Alert Management
        </h1>
        <Badge variant="default">
          Active Rules: {alertStatus.active_rules.length}
        </Badge>
      </div>

      {/* Alert Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical</CardTitle>
            {getSeverityIcon('critical')}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{alertStatus.severity_counts.critical}</div>
            <p className="text-xs text-muted-foreground">Critical alerts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High</CardTitle>
            {getSeverityIcon('high')}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">{alertStatus.severity_counts.high}</div>
            <p className="text-xs text-muted-foreground">High severity alerts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Medium</CardTitle>
            {getSeverityIcon('medium')}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-500">{alertStatus.severity_counts.medium}</div>
            <p className="text-xs text-muted-foreground">Medium severity alerts</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low</CardTitle>
            {getSeverityIcon('low')}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">{alertStatus.severity_counts.low}</div>
            <p className="text-xs text-muted-foreground">Low severity alerts</p>
          </CardContent>
        </Card>
      </div>

      {/* Active Rules */}
      <Card>
        <CardHeader>
          <CardTitle>Active Alert Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {alertStatus.active_rules.map((rule, index) => (
              <div key={index} className="border rounded-lg p-3 bg-gray-50">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-blue-500" />
                  <span className="font-medium">{rule}</span>
                </div>
              </div>
            ))}
          </div>
          {alertStatus.active_rules.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No active alert rules configured
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          {alertStatus.recent_alerts.length > 0 ? (
            <div className="space-y-4">
              {alertStatus.recent_alerts.map((alert, index) => (
                <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        {getSeverityIcon(alert.severity)}
                        <h4 className="font-medium truncate">{alert.name}</h4>
                        <Badge variant={getSeverityColor(alert.severity)}>
                          {alert.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          <span>{new Date(alert.timestamp).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No recent alerts
            </div>
          )}
        </CardContent>
      </Card>

      {/* Alert Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">High Error Rate Detection</h4>
                <p className="text-sm text-gray-600">Triggers when success rate drops below 80%</p>
              </div>
              <Badge variant="default">Enabled</Badge>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">Slow Processing Detection</h4>
                <p className="text-sm text-gray-600">Triggers when average processing time exceeds 5 seconds</p>
              </div>
              <Badge variant="default">Enabled</Badge>
            </div>
            
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">High Error Count Detection</h4>
                <p className="text-sm text-gray-600">Triggers when error rate exceeds 30%</p>
              </div>
              <Badge variant="default">Enabled</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AlertsPage;