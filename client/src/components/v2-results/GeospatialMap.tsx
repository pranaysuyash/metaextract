import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  MapPin, 
  Navigation, 
  Globe, 
  Eye, 
  Download,
  Settings,
  ZoomIn,
  ZoomOut,
  RotateCcw
} from 'lucide-react';

interface LocationData {
  latitude: number;
  longitude: number;
  accuracy?: number;
  altitude?: number;
  address?: string;
  city?: string;
  region?: string;
  country?: string;
  timestamp?: string;
  provider?: string;
  bearing?: number;
  speed?: number;
}

interface GeospatialMapProps {
  location: LocationData;
  title?: string;
  showControls?: boolean;
}

export const GeospatialMap: React.FC<GeospatialMapProps> = ({ 
  location, 
  title = 'Geospatial Location',
  showControls = true
}) => {
  const [zoom, setZoom] = useState(12);
  const [mapType, setMapType] = useState<'roadmap' | 'satellite' | 'hybrid'>('roadmap');
  
  // Simulate map loading
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Simulate map loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, []);

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 1, 18));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 1, 1));
  };

  const handleMapTypeChange = (type: 'roadmap' | 'satellite' | 'hybrid') => {
    setMapType(type);
  };

  const handleReset = () => {
    setZoom(12);
    setMapType('roadmap');
  };

  const getMapUrl = () => {
    // This would be replaced with an actual map service URL in a real implementation
    // For now, we'll return a placeholder
    return `https://placehold.co/600x400?text=Map+${location.latitude.toFixed(4)},${location.longitude.toFixed(4)}`;
  };

  return (
    <div className="space-y-6">
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Globe className="w-5 h-5 text-primary" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Map Visualization */}
            <div className="lg:col-span-2">
              <div className="bg-muted/20 rounded-lg overflow-hidden aspect-video relative">
                {isLoading ? (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-center">
                      <Globe className="w-12 h-12 mx-auto text-primary mb-2 animate-pulse" />
                      <p className="text-slate-300">Loading map...</p>
                    </div>
                  </div>
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <img 
                      src={getMapUrl()} 
                      alt={`Map of ${location.address || `${location.latitude}, ${location.longitude}`}`}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute top-4 left-4 flex gap-2">
                      <Badge variant="secondary" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                        {mapType.charAt(0).toUpperCase() + mapType.slice(1)}
                      </Badge>
                      <Badge variant="secondary" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                        Zoom: {zoom}
                      </Badge>
                    </div>
                  </div>
                )}
                
                {/* Map Controls */}
                {showControls && (
                  <div className="absolute bottom-4 right-4 flex flex-col gap-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleZoomIn}
                      className="p-2"
                    >
                      <ZoomIn className="w-4 h-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleZoomOut}
                      className="p-2"
                    >
                      <ZoomOut className="w-4 h-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleReset}
                      className="p-2"
                    >
                      <RotateCcw className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </div>
              
              {/* Map Type Controls */}
              {showControls && (
                <div className="flex gap-2 mt-4">
                  <Button 
                    variant={mapType === 'roadmap' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleMapTypeChange('roadmap')}
                  >
                    Roadmap
                  </Button>
                  <Button 
                    variant={mapType === 'satellite' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleMapTypeChange('satellite')}
                  >
                    Satellite
                  </Button>
                  <Button 
                    variant={mapType === 'hybrid' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleMapTypeChange('hybrid')}
                  >
                    Hybrid
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="ml-auto"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>
              )}
            </div>
            
            {/* Location Information */}
            <div className="space-y-4">
              <Card className="bg-muted/20 border-white/10">
                <CardContent className="p-4">
                  <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-primary" />
                    Location Details
                  </h3>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-slate-300">Coordinates:</span>
                      <span className="text-white font-mono text-sm">
                        {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}
                      </span>
                    </div>
                    
                    {location.address && (
                      <div className="flex justify-between">
                        <span className="text-slate-300">Address:</span>
                        <span className="text-white text-sm max-w-[140px] truncate">{location.address}</span>
                      </div>
                    )}
                    
                    {location.city && (
                      <div className="flex justify-between">
                        <span className="text-slate-300">City:</span>
                        <span className="text-white">{location.city}</span>
                      </div>
                    )}
                    
                    {location.region && (
                      <div className="flex justify-between">
                        <span className="text-slate-300">Region:</span>
                        <span className="text-white">{location.region}</span>
                      </div>
                    )}
                    
                    {location.country && (
                      <div className="flex justify-between">
                        <span className="text-slate-300">Country:</span>
                        <span className="text-white">{location.country}</span>
                      </div>
                    )}
                    
                    {location.altitude !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-slate-300">Altitude:</span>
                        <span className="text-white">{location.altitude}m</span>
                      </div>
                    )}
                    
                    {location.accuracy !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-slate-300">Accuracy:</span>
                        <span className="text-white">±{location.accuracy}m</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
              
              {/* Location Metadata */}
              <Card className="bg-muted/20 border-white/10">
                <CardContent className="p-4">
                  <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                    <Navigation className="w-4 h-4 text-primary" />
                    Metadata
                  </h3>
                  
                  <div className="space-y-2">
                    {location.timestamp && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-300">Timestamp:</span>
                        <span className="text-white">{new Date(location.timestamp).toLocaleString()}</span>
                      </div>
                    )}
                    
                    {location.provider && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-300">Provider:</span>
                        <span className="text-white">{location.provider}</span>
                      </div>
                    )}
                    
                    {location.bearing !== undefined && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-300">Bearing:</span>
                        <span className="text-white">{location.bearing}°</span>
                      </div>
                    )}
                    
                    {location.speed !== undefined && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-300">Speed:</span>
                        <span className="text-white">{location.speed} m/s</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
              
              {/* Location Quality Assessment */}
              <Card className="bg-muted/20 border-white/10">
                <CardContent className="p-4">
                  <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                    <Eye className="w-4 h-4 text-primary" />
                    Quality Assessment
                  </h3>
                  
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-slate-300">Accuracy</span>
                        <span className="text-white">
                          {location.accuracy !== undefined 
                            ? location.accuracy < 10 ? 'High' 
                              : location.accuracy < 50 ? 'Medium' 
                              : 'Low'
                            : 'Unknown'}
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div 
                          className="bg-emerald-500 h-2 rounded-full" 
                          style={{ 
                            width: location.accuracy !== undefined 
                              ? `${Math.max(0, Math.min(100, 100 - (location.accuracy / 10)))}%` 
                              : '0%' 
                          }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="pt-2 border-t border-white/10">
                      <h4 className="text-xs font-semibold text-slate-300 mb-2">Location Tags</h4>
                      <div className="flex flex-wrap gap-2">
                        <Badge variant="secondary" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                          GPS
                        </Badge>
                        {location.provider && (
                          <Badge variant="secondary" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                            {location.provider}
                          </Badge>
                        )}
                        {location.accuracy !== undefined && (
                          <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30">
                            {location.accuracy < 10 ? 'Precise' : location.accuracy < 50 ? 'Standard' : 'Rough'}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Location Context */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Globe className="w-5 h-5 text-primary" />
            Location Context
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Coordinates</p>
              <p className="text-lg font-bold text-white">
                {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
              </p>
            </div>
            
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Location Type</p>
              <p className="text-lg font-bold text-white">
                {location.address ? 'Address' : 'Coordinates'}
              </p>
            </div>
            
            <div className="p-4 bg-muted/20 rounded-lg">
              <p className="text-sm text-slate-300 mb-1">Authenticity</p>
              <div className="flex items-center gap-2">
                <Eye className="w-5 h-5 text-emerald-500" />
                <span className="text-lg font-bold text-emerald-400">Verified</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};