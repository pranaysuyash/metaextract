import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  FileText,
  Activity,
  Server
} from 'lucide-react';

interface SecurityCheckResult {
  check_name: string;
  is_safe: boolean;
  details: string;
  severity: string;
}

interface SecurityReport {
  filepath: string;
  security_level: string;
  timestamp: string;
  checks_performed: number;
  safe: boolean;
  results: SecurityCheckResult[];
  summary: {
    safe_checks: number;
    unsafe_checks: number;
    overall_risk: string;
  };
}

const SecurityPage: React.FC = () => {
  const [securityReports, setSecurityReports] = useState<SecurityReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSecurityData = async () => {
      try {
        const response = await fetch('/api/security/reports');
        if (!response.ok) {
          throw new Error('Failed to fetch security reports');
        }
        const data = await response.json();
        setSecurityReports(data.reports || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchSecurityData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchSecurityData, 30000); // Every 30 seconds
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

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
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

  const getCheckStatusIcon = (isSafe: boolean) => {
    return isSafe ? 
      <CheckCircle className="h-4 w-4 text-green-500" /> : 
      <AlertTriangle className="h-4 w-4 text-red-500" />;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold flex items-center">
          <Shield className="mr-2 h-8 w-8" />
          Security Dashboard
        </h1>
        <Badge variant="default">
          Real-time Monitoring
        </Badge>
      </div>

      {/* Security Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Scans</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{securityReports.length}</div>
            <p className="text-xs text-muted-foreground">Files scanned</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Safe Files</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {securityReports.filter(report => report.safe).length}
            </div>
            <p className="text-xs text-muted-foreground">Successfully validated</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Risk</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {securityReports.filter(report => !report.safe).length}
            </div>
            <p className="text-xs text-muted-foreground">Flagged for review</p>
          </CardContent>
        </Card>
      </div>

      {/* Security Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Security Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium mb-3">Security Levels</h3>
              <div className="space-y-3">
                {['Basic', 'Standard', 'Strict', 'Paranoid'].map((level, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <span>{level}</span>
                    <Badge variant={index === 1 ? "default" : "secondary"}>
                      {index === 1 ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-3">Active Security Checks</h3>
              <div className="space-y-2">
                {[
                  'File Extension Check',
                  'File Size Check', 
                  'MIME Type Check',
                  'File Signature Check',
                  'Malicious Content Scan'
                ].map((check, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>{check}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Security Reports */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Security Reports</CardTitle>
        </CardHeader>
        <CardContent>
          {securityReports.length > 0 ? (
            <div className="space-y-4">
              {securityReports.slice(0, 10).map((report, index) => (
                <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        {getCheckStatusIcon(report.safe)}
                        <h4 className="font-medium truncate">{report.filepath}</h4>
                        <Badge variant={getRiskColor(report.summary.overall_risk)}>
                          {report.summary.overall_risk}
                        </Badge>
                        <Badge variant="secondary">
                          {report.security_level}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-sm mt-2">
                        <div>
                          <span className="text-gray-600">Checks: </span>
                          <span className="font-medium">{report.checks_performed}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Safe: </span>
                          <span className="font-medium">{report.summary.safe_checks}</span>
                          <span className="text-gray-500">/{report.checks_performed}</span>
                        </div>
                      </div>
                      
                      <div className="mt-3">
                        <h5 className="font-medium text-sm mb-2">Security Checks:</h5>
                        <div className="space-y-2">
                          {report.results.slice(0, 3).map((result, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-xs">
                              {getCheckStatusIcon(result.is_safe)}
                              <span className="truncate">{result.check_name}</span>
                              <Badge 
                                variant={getSeverityColor(result.severity)} 
                                className="text-xs"
                              >
                                {result.severity}
                              </Badge>
                            </div>
                          ))}
                          {report.results.length > 3 && (
                            <div className="text-xs text-gray-500">
                              +{report.results.length - 3} more checks...
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right text-xs text-gray-500 ml-4">
                      <div>{new Date(report.timestamp).toLocaleDateString()}</div>
                      <div>{new Date(report.timestamp).toLocaleTimeString()}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No security reports available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Security Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Security Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-blue-500 mt-0.5" />
              <div>
                <h4 className="font-medium">Enable Strict Security Level</h4>
                <p className="text-sm text-gray-600">Consider upgrading to strict security level for production environments</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
              <div>
                <h4 className="font-medium">File Type Validation</h4>
                <p className="text-sm text-gray-600">Current file type validation is properly configured</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
              <div>
                <h4 className="font-medium">Review Dangerous Extensions</h4>
                <p className="text-sm text-gray-600">Consider blocking additional executable file extensions</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SecurityPage;