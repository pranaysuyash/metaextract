// client/src/components/viz/VizDemo.tsx
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DateTimeTimeline } from './DateTimeTimeline';
import { CameraSettingsRadar } from './CameraSettingsRadar';
import { EmailThreadViz } from './EmailThreadViz';
import { ColorHistogram } from './ColorHistogram';
import { LocationMiniMap } from './LocationMiniMap';
import { AudioWaveformViz } from './AudioWaveformViz';
import { VideoKeyframesViz } from './VideoKeyframesViz';
import { ForensicTimeline } from './ForensicTimeline';
import { ManipulationDashboard } from './ManipulationDashboard';
import {
  Calendar,
  Camera,
  Mail,
  Play,
  RotateCcw,
  FileImage,
  FileAudio,
  FileVideo,
  AlertTriangle,
  Activity,
  Film,
  History,
  Shield,
} from 'lucide-react';

// Sample data for demos
const sampleImageMetadata = {
  DateTimeOriginal: '2024:03:15 14:32:45',
  CreateDate: '2024:03:15 14:32:50',
  ModifyDate: '2024:03:15 14:35:12',
  FileCreateDate: '2024-03-15T10:32:50-04:00',
  FileModifyDate: '2024-03-15T10:35:12-04:00',
  FileAccessDate: '2024-03-15T11:00:00-04:00',
};

const sampleExif = {
  ISO: 400,
  FNumber: 2.8,
  ExposureTime: '1/250',
  FocalLength: 50,
  WhiteBalance: 6500,
  ColorTemperature: 6500,
  Flash: 1,
  ExposureCompensation: 0,
  DigitalZoomRatio: 1,
};

const sampleImage = {
  width: 6000,
  height: 4000,
  bit_depth: 14,
  color_mode: 'RGB',
};

const sampleGps = {
  latitude: 37.7749,
  longitude: -122.4194,
  latitude_decimal: 37.7749,
  longitude_decimal: -122.4194,
  altitude_meters: 15,
  gps_timestamp: '2024-03-15T14:32:45Z',
  gps_speed: 0,
  gps_direction: 180,
  coordinates_formatted: '37.7749° N, 122.4194° W',
  google_maps_url: 'https://www.google.com/maps?q=37.7749,-122.4194',
  openstreetmap_url:
    'https://www.openstreetmap.org/?mlat=37.7749&mlon=-122.4194#map=15/37.7749/-122.4194',
};

const sampleEmail = {
  email_from: 'John Doe <john.doe@example.com>',
  email_from_name: 'John Doe',
  email_from_address: 'john.doe@example.com',
  email_to: 'Jane Smith <jane@company.org>',
  email_to_addresses: ['jane@company.org'],
  email_cc: 'Team Lead <lead@company.org>',
  email_cc_addresses: ['lead@company.org'],
  email_subject: 'Re: Project Update - Q2 Planning',
  email_date: 'Mon, 15 Mar 2024 14:30:00 +0000',
  email_datetime_parsed: '2024-03-15T14:30:00+00:00',
  email_timestamp: 1710513000,
  email_message_id: '<ABC123@example.com>',
  email_in_reply_to: '<XYZ789@example.com>',
  email_is_reply: true,
  email_is_direct_reply: true,
  email_is_forward: false,
  email_thread_level: 2,
  email_priority: 'high',
  email_dkim_present: true,
  email_spf_result: 'pass',
  email_authentication_results: 'example.com; spf=pass; dkim=pass',
  email_spam_status: 'No, score=0.0',
  email_attachment_count: 2,
  email_attachments: [
    {
      filename: 'Q2_Planning_Document.pdf',
      content_type: 'application/pdf',
      size: 245760,
    },
    {
      filename: 'Budget_Summary.xlsx',
      content_type:
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      size: 51200,
    },
  ],
};

const sampleAudio = {
  duration: 245,
  bitrate: 320000,
  sample_rate: 44100,
  channels: 2,
  bit_depth: 16,
  codec: 'MP3',
  artist: 'Sample Artist',
  album: 'Demo Album',
  title: 'Sample Track',
  genre: 'Rock',
  year: 2024,
};

const sampleVideo = {
  duration: 120,
  width: 1920,
  height: 1080,
  frame_rate: 30,
  bitrate: 8000000,
  codec: 'H.264',
  audio_codec: 'AAC',
  container: 'MP4',
};

const sampleIntegrity = {
  md5: 'd41d8cd98f00b204e9800998ecf8427e',
  sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
  sha1: 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
  crc32: '00000000',
};

const sampleForensic = {
  forensic_filesystem: {
    file_created: '2024-03-15T10:32:50-04:00',
    file_modified: '2024-03-15T14:35:12-04:00',
    file_accessed: '2024-03-15T18:00:00-04:00',
    file_size: 2457600,
    file_permissions: '644',
    file_owner: 1000,
    file_inode: 12345678,
  },
  forensic_device_hardware: {
    device_id: 'device-abc123',
    volume_id: 'volume-xyz789',
    drive_type: 'SSD',
    filesystem_type: 'APFS',
  },
};

const sampleManipulation = {
  manipulation_probability: 15,
  indicators: ['Minor metadata adjustment', 'Color correction'],
  jpeg_analysis: {
    compression_artifacts: false,
    recompression_detected: true,
  },
  noise_analysis: {
    inconsistent_regions: 0,
    confidence: 85,
  },
};

const sampleSteganography = {
  suspicious_score: 5,
  methods_detected: [],
  entropy_analysis: {
    score: 3.2,
    suspicious_regions: 0,
  },
  lsb_analysis: {
    suspicious_channels: [],
    confidence: 92,
  },
};

const sampleAIDetection = {
  ai_probability: 8,
  detection_methods: ['Noise analysis', 'Frequency domain'],
  confidence: 78,
  suspicious_patterns: [],
};

// Anomaly example
const anomalyMetadata = {
  DateTimeOriginal: '2024:01:15 08:30:00',
  CreateDate: '2024:01:15 08:30:05',
  ModifyDate: '2024:01:20 18:45:30',
  FileCreateDate: '2024-03-15T10:00:00-04:00',
  FileModifyDate: '2024-03-15T18:45:30-04:00',
  FileAccessDate: '2024-03-15T18:45:30-04:00',
};

export function VizDemo() {
  const [activeTab, setActiveTab] = useState('timeline');
  const [showAnomaly, setShowAnomaly] = useState(false);
  const [currentImageData, setCurrentImageData] = useState(sampleImageMetadata);
  const [currentExif, setCurrentExif] = useState(sampleExif);
  const [currentEmail, setCurrentEmail] = useState(sampleEmail);

  const resetDemo = () => {
    setShowAnomaly(false);
    setCurrentImageData(sampleImageMetadata);
    setCurrentExif(sampleExif);
    setCurrentEmail(sampleEmail);
  };

  const loadAnomalyDemo = () => {
    setShowAnomaly(true);
    setCurrentImageData(anomalyMetadata);
  };

  const randomizeExif = () => {
    setCurrentExif({
      ...currentExif,
      ISO: Math.floor(Math.random() * 6400) + 50,
      FNumber: [1.4, 1.8, 2.8, 4, 5.6, 8, 11, 16][
        Math.floor(Math.random() * 8)
      ],
      ExposureTime: [
        '1/4000',
        '1/2000',
        '1/1000',
        '1/500',
        '1/250',
        '1/125',
        '1/60',
        '1/30',
      ][Math.floor(Math.random() * 8)],
      FocalLength: [24, 35, 50, 85, 135, 200][Math.floor(Math.random() * 6)],
      Flash: Math.random() > 0.5 ? 1 : 0,
    });
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Metadata Visualization Demo</h1>
        <p className="text-muted-foreground">
          Explore interactive visualizations for different metadata types
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5 mb-6">
          <TabsTrigger value="timeline" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Timeline
          </TabsTrigger>
          <TabsTrigger value="camera" className="flex items-center gap-2">
            <Camera className="w-4 h-4" />
            Camera
          </TabsTrigger>
          <TabsTrigger value="email" className="flex items-center gap-2">
            <Mail className="w-4 h-4" />
            Email
          </TabsTrigger>
          <TabsTrigger value="media" className="flex items-center gap-2">
            <Film className="w-4 h-4" />
            Audio/Video
          </TabsTrigger>
          <TabsTrigger value="forensic" className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Forensic
          </TabsTrigger>
        </TabsList>

        {/* Timeline Demo */}
        <TabsContent value="timeline">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DateTimeTimeline metadata={currentImageData} fileType="image" />
            <Card>
              <CardHeader>
                <CardTitle>Date/Time Timeline</CardTitle>
                <CardDescription>
                  Multi-source date visualization with anomaly detection
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <Button onClick={resetDemo} variant="outline" size="sm">
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Normal Data
                  </Button>
                  <Button
                    onClick={loadAnomalyDemo}
                    variant="destructive"
                    size="sm"
                  >
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    Show Anomaly
                  </Button>
                </div>
                {showAnomaly && (
                  <Badge
                    variant="secondary"
                    className="bg-amber-100 text-amber-800"
                  >
                    ⚠️ Large gap detected between dates
                  </Badge>
                )}
                <p className="text-sm text-muted-foreground">
                  Shows all date/time sources: EXIF (capture, create, modify),
                  filesystem, and email. Automatically highlights anomalies like
                  large gaps between dates.
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Camera Demo */}
        <TabsContent value="camera">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CameraSettingsRadar exif={currentExif} image={sampleImage} />
            <div className="space-y-4">
              <ColorHistogram image={sampleImage} exif={sampleExif} />
              <LocationMiniMap gps={sampleGps} />
            </div>
          </div>
          <div className="mt-4">
            <Button onClick={randomizeExif} className="w-full">
              <Play className="w-4 h-4 mr-2" />
              Randomize Camera Settings
            </Button>
          </div>
        </TabsContent>

        {/* Email Demo */}
        <TabsContent value="email">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <EmailThreadViz email={currentEmail} />
            <Card>
              <CardHeader>
                <CardTitle>Email Thread Visualization</CardTitle>
                <CardDescription>
                  Email metadata with security status and thread structure
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                  Visualizes email headers, participant cards, security
                  verification (DKIM/SPF), attachments, and thread
                  relationships.
                </p>
                <ul className="text-sm space-y-2">
                  <li>• Color-coded participant avatars</li>
                  <li>• DKIM/SPF verification badges</li>
                  <li>• Attachment list with sizes</li>
                  <li>• Thread level visualization</li>
                  <li>• Priority indicators</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Audio/Video Demo */}
        <TabsContent value="media">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AudioWaveformViz audio={sampleAudio} />
            <VideoKeyframesViz video={sampleVideo} />
          </div>
        </TabsContent>

        {/* Forensic Demo */}
        <TabsContent value="forensic">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ForensicTimeline
              integrity={sampleIntegrity}
              forensic={sampleForensic}
              filename="sample.jpg"
            />
            <ManipulationDashboard
              manipulation={sampleManipulation}
              steganography={sampleSteganography}
              ai_detection={sampleAIDetection}
            />
          </div>
        </TabsContent>
      </Tabs>

      <div className="mt-12 border-t pt-8">
        <h2 className="text-2xl font-bold mb-4">
          All Visualization Components
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                DateTimeTimeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                Multi-source date timeline with anomaly detection
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  EXIF
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Filesystem
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Email
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="w-5 h-5" />
                CameraSettingsRadar
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                Radar chart for camera settings
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  ISO
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Aperture
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Shutter
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="w-5 h-5" />
                EmailThreadViz
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                Email thread with security status
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  DKIM
                </Badge>
                <Badge variant="outline" className="text-xs">
                  SPF
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Attachments
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                ColorHistogram
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                RGB/luminance histogram
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Red
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Green
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Blue
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="w-5 h-5" />
                LocationMiniMap
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                GPS location with map links
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Coordinates
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Altitude
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                ForensicTimeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                Chain of custody visualization
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Hashes
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Device
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Film className="w-5 h-5" />
                VideoKeyframesViz
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                Video overview with keyframes
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Codec
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Resolution
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="w-5 h-5" />
                AudioWaveformViz
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                Audio waveform visualization
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Format
                </Badge>
                <Badge variant="outline" className="text-xs">
                  Bitrate
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                ManipulationDashboard
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                AI/manipulation detection
              </p>
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs">
                  Steganography
                </Badge>
                <Badge variant="outline" className="text-xs">
                  AI Detection
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default VizDemo;
