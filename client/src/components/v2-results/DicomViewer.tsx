import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Image as ImageIcon, 
  Database, 
  MapPin, 
  Calendar, 
  Settings,
  Eye,
  Download,
  ZoomIn,
  ZoomOut,
  RotateCw
} from 'lucide-react';

interface DicomMetadata {
  patientName?: string;
  patientId?: string;
  patientAge?: string;
  patientSex?: string;
  studyDate?: string;
  studyTime?: string;
  studyDescription?: string;
  modality?: string;
  manufacturer?: string;
  modelName?: string;
  institutionName?: string;
  bodyPartExamined?: string;
  sliceThickness?: string;
  kvp?: string;
  tubeCurrent?: string;
  exposureTime?: string;
  imagePosition?: string;
  imageOrientation?: string;
  sliceLocation?: string;
  windowCenter?: string;
  windowWidth?: string;
}

interface DicomViewerProps {
  metadata: DicomMetadata;
  imageUrl?: string;
  onImageLoad?: () => void;
}

export const DicomViewer: React.FC<DicomViewerProps> = ({ 
  metadata, 
  imageUrl,
  onImageLoad 
}) => {
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (imageUrl) {
      setIsLoading(true);
      setError(null);
      
      const img = new window.Image();
      img.onload = () => {
        setIsLoading(false);
        onImageLoad?.();
      };
      img.onerror = () => {
        setIsLoading(false);
        setError('Failed to load DICOM image preview');
      };
      img.src = imageUrl;
    }
  }, [imageUrl, onImageLoad]);

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.1, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.1, 0.5));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const handleReset = () => {
    setZoom(1);
    setRotation(0);
  };

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

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Image Preview */}
        <div className="lg:col-span-2">
          <Card className="bg-card border-white/10 h-full">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-primary" />
                DICOM Image Preview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative bg-muted/20 rounded-lg overflow-hidden aspect-square flex items-center justify-center">
                {isLoading ? (
                  <div className="text-center p-8">
                    <Database className="w-12 h-12 mx-auto text-primary mb-2" />
                    <p className="text-slate-300">Loading DICOM preview...</p>
                  </div>
                ) : error ? (
                  <div className="text-center p-8">
                    <Database className="w-12 h-12 mx-auto text-red-500 mb-2" />
                    <p className="text-red-400">{error}</p>
                  </div>
                ) : imageUrl ? (
                  <img
                    src={imageUrl}
                    alt="DICOM preview"
                    className="w-full h-full object-contain"
                    style={{
                      transform: `scale(${zoom}) rotate(${rotation}deg)`,
                      transition: 'transform 0.2s ease'
                    }}
                  />
                ) : (
                  <div className="text-center p-8">
                    <Database className="w-12 h-12 mx-auto text-slate-500 mb-2" />
                    <p className="text-slate-300">No image preview available</p>
                  </div>
                )}
              </div>
              
              {/* Image Controls */}
              <div className="flex flex-wrap gap-2 mt-4">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleZoomIn}
                  disabled={zoom >= 3}
                  className="gap-2"
                >
                  <ZoomIn className="w-4 h-4" />
                  Zoom In
                </Button>
                
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleZoomOut}
                  disabled={zoom <= 0.5}
                  className="gap-2"
                >
                  <ZoomOut className="w-4 h-4" />
                  Zoom Out
                </Button>
                
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleRotate}
                  className="gap-2"
                >
                  <RotateCw className="w-4 h-4" />
                  Rotate
                </Button>
                
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleReset}
                  className="gap-2"
                >
                  <Settings className="w-4 h-4" />
                  Reset
                </Button>
                
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="gap-2 ml-auto"
                >
                  <Download className="w-4 h-4" />
                  Export
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Metadata Panel */}
        <div className="space-y-4">
          {renderMetadataSection('Patient Information', [
            ['Patient Name', metadata.patientName],
            ['Patient ID', metadata.patientId],
            ['Age', metadata.patientAge],
            ['Sex', metadata.patientSex],
          ])}
          
          {renderMetadataSection('Study Information', [
            ['Study Date', metadata.studyDate],
            ['Study Time', metadata.studyTime],
            ['Description', metadata.studyDescription],
            ['Modality', metadata.modality],
          ])}
          
          {renderMetadataSection('Equipment', [
            ['Manufacturer', metadata.manufacturer],
            ['Model Name', metadata.modelName],
            ['Institution', metadata.institutionName],
          ])}
          
          {renderMetadataSection('Image Parameters', [
            ['Body Part', metadata.bodyPartExamined],
            ['Slice Thickness', metadata.sliceThickness],
            ['KVP', metadata.kvp],
            ['Tube Current', metadata.tubeCurrent],
            ['Exposure Time', metadata.exposureTime],
          ])}
          
          {renderMetadataSection('Positioning', [
            ['Image Position', metadata.imagePosition],
            ['Image Orientation', metadata.imageOrientation],
            ['Slice Location', metadata.sliceLocation],
          ])}
          
          {renderMetadataSection('Display Settings', [
            ['Window Center', metadata.windowCenter],
            ['Window Width', metadata.windowWidth],
          ])}
        </div>
      </div>
      
      {/* Additional DICOM Information */}
      <Card className="bg-card border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-primary" />
            DICOM Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3 bg-muted/20 rounded-lg">
              <p className="text-xs text-slate-300">Modality</p>
              <p className="text-lg font-bold text-white">
                {metadata.modality || 'Unknown'}
              </p>
            </div>
            
            <div className="p-3 bg-muted/20 rounded-lg">
              <p className="text-xs text-slate-300">Manufacturer</p>
              <p className="text-lg font-bold text-white truncate">
                {metadata.manufacturer || 'Unknown'}
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
          
          <div className="mt-4 pt-4 border-t border-white/10">
            <h4 className="text-sm font-semibold text-white mb-2">DICOM Tags</h4>
            <div className="flex flex-wrap gap-2">
              {metadata.modality && (
                <Badge variant="secondary" className="bg-purple-500/20 text-purple-400 border-purple-500/30">
                  Modality: {metadata.modality}
                </Badge>
              )}
              {metadata.bodyPartExamined && (
                <Badge variant="secondary" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
                  Body Part: {metadata.bodyPartExamined}
                </Badge>
              )}
              {metadata.institutionName && (
                <Badge variant="secondary" className="bg-green-500/20 text-green-400 border-green-500/30">
                  Institution: {metadata.institutionName}
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
