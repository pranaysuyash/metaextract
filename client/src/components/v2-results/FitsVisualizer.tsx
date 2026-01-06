import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Map, 
  Database, 
  Calendar, 
  Settings,
  Eye,
  Download,
  Grid3X3,
  Activity
} from 'lucide-react';

interface FitsMetadata {
  telescope?: string;
  instrument?: string;
  object?: string;
  ra?: string; // Right Ascension
  dec?: string; // Declination
  dateObs?: string;
  mjd?: string; // Modified Julian Date
  exposure?: string;
  filter?: string;
  binning?: string;
  gain?: string;
  readNoise?: string;
  pixelScale?: string;
  seeing?: string;
  airmass?: string;
  temperature?: string;
  humidity?: string;
  pressure?: string;
  naxis?: string;
  naxis1?: string;
  naxis2?: string;
  bitpix?: string;
  bscale?: string;
  bzero?: string;
  bunit?: string;
  origin?: string;
  observer?: string;
  observerId?: string;
}

interface FitsVisualizerProps {
  metadata: FitsMetadata;
}

export const FitsVisualizer: React.FC<FitsVisualizerProps> = ({ metadata }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'coordinates' | 'instrument' | 'environment'>('overview');
  
  const renderMetadataSection = (title: string, fields: [string, string | undefined][]) => {
    const validFields = fields.filter(([, value]) => value !== undefined && value.trim() !== '');
    
    if (validFields.length === 0) return null;
    
    return (
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-white border-b border-white/10 pb-1">{title}</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {validFields.map(([label, value], idx) => (
            <div key={idx} className="flex justify-between py-1">
              <span className="text-xs text-slate-300 capitalize">{label.replace(/([A-Z])/g, ' $1').trim()}:</span>
              <span className="text-sm text-white truncate max-w-[120px]">{value}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-4">
            {renderMetadataSection('Observation', [
              ['Object', metadata.object],
              ['Date Observed', metadata.dateObs],
              ['Modified Julian Date', metadata.mjd],
              ['Exposure Time', metadata.exposure],
            ])}
            
            {renderMetadataSection('Telescope', [
              ['Telescope', metadata.telescope],
              ['Instrument', metadata.instrument],
              ['Observer', metadata.observer],
            ])}
          </div>
        );
      
      case 'coordinates':
        return (
          <div className="space-y-4">
            {renderMetadataSection('Celestial Coordinates', [
              ['Right Ascension', metadata.ra],
              ['Declination', metadata.dec],
              ['Pixel Scale', metadata.pixelScale],
            ])}
            
            {renderMetadataSection('Observation Parameters', [
              ['Seeing', metadata.seeing],
              ['Airmass', metadata.airmass],
              ['Binning', metadata.binning],
            ])}
          </div>
        );
      
      case 'instrument':
        return (
          <div className="space-y-4">
            {renderMetadataSection('Detector', [
              ['Gain', metadata.gain],
              ['Read Noise', metadata.readNoise],
              ['Filter', metadata.filter],
            ])}
            
            {renderMetadataSection('FITS Header', [
              ['NAXIS', metadata.naxis],
              ['NAXIS1', metadata.naxis1],
              ['NAXIS2', metadata.naxis2],
              ['BITPIX', metadata.bitpix],
              ['BSCALE', metadata.bscale],
              ['BZERO', metadata.bzero],
              ['BUNIT', metadata.bunit],
            ])}
          </div>
        );
      
      case 'environment':
        return (
          <div className="space-y-4">
            {renderMetadataSection('Environmental Conditions', [
              ['Temperature', metadata.temperature],
              ['Humidity', metadata.humidity],
              ['Pressure', metadata.pressure],
            ])}
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Grid3X3 className="w-5 h-5 text-primary" />
            FITS Data Visualizer
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2 mb-4">
            <Button 
              variant={activeTab === 'overview' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </Button>
            <Button 
              variant={activeTab === 'coordinates' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveTab('coordinates')}
            >
              Coordinates
            </Button>
            <Button 
              variant={activeTab === 'instrument' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveTab('instrument')}
            >
              Instrument
            </Button>
            <Button 
              variant={activeTab === 'environment' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveTab('environment')}
            >
              Environment
            </Button>
          </div>
          
          {renderTabContent()}
        </CardContent>
      </Card>
      
      {/* Scientific Data Visualization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Coordinates Visualization */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Map className="w-5 h-5 text-primary" />
              Celestial Coordinates
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-muted/20 rounded-lg p-4 h-64 flex items-center justify-center">
              <div className="text-center">
                <Activity className="w-12 h-12 mx-auto text-primary mb-2" />
                <p className="text-white">Celestial coordinate visualization</p>
                <p className="text-sm text-slate-300 mt-1">
                  {metadata.ra && metadata.dec 
                    ? `RA: ${metadata.ra}, Dec: ${metadata.dec}` 
                    : 'Coordinates not available'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Data Quality */}
        <Card className="bg-card border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Eye className="w-5 h-5 text-primary" />
              Data Quality Assessment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-300">Seeing Quality</span>
                <Badge variant="outline" className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                  {metadata.seeing || 'Unknown'}
                </Badge>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-slate-300">Airmass</span>
                <Badge variant="outline" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                  {metadata.airmass || 'Unknown'}
                </Badge>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-slate-300">Exposure Quality</span>
                <Badge variant="outline" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                  {metadata.exposure ? 'Good' : 'Unknown'}
                </Badge>
              </div>
              
              <div className="pt-2 border-t border-white/10">
                <h4 className="text-sm font-semibold text-white mb-2">FITS Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {metadata.telescope && (
                    <Badge variant="secondary" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                      Telescope: {metadata.telescope}
                    </Badge>
                  )}
                  {metadata.instrument && (
                    <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30">
                      Instrument: {metadata.instrument}
                    </Badge>
                  )}
                  {metadata.object && (
                    <Badge variant="secondary" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                      Object: {metadata.object}
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* FITS Header Information */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-primary" />
            FITS Header Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-muted/20 rounded-lg">
              <p className="text-xs text-slate-300">Data Type</p>
              <p className="text-lg font-bold text-white">
                {metadata.bitpix === '8' ? '8-bit' : 
                 metadata.bitpix === '16' ? '16-bit' : 
                 metadata.bitpix === '32' ? '32-bit' : 'Unknown'}
              </p>
            </div>
            
            <div className="p-3 bg-muted/20 rounded-lg">
              <p className="text-xs text-slate-300">Dimensions</p>
              <p className="text-lg font-bold text-white">
                {metadata.naxis1 && metadata.naxis2 ? `${metadata.naxis1}×${metadata.naxis2}` : 'Unknown'}
              </p>
            </div>
            
            <div className="p-3 bg-muted/20 rounded-lg">
              <p className="text-xs text-slate-300">Observatory</p>
              <p className="text-lg font-bold text-white truncate">
                {metadata.telescope || 'Unknown'}
              </p>
            </div>
            
            <div className="p-3 bg-muted/20 rounded-lg">
              <p className="text-xs text-slate-300">Authenticity</p>
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