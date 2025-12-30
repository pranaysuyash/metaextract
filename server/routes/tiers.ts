/**
 * Tier Routes Module
 *
 * Handles tier configuration and information endpoints:
 * - Tier configurations
 * - Field information
 * - Sample files
 */

import type { Express, Response } from 'express';
import fs from 'fs/promises';
import path from 'path';
import { getTierConfig, TIER_CONFIGS } from '@shared/tierConfig';

// ============================================================================
// Route Registration
// ============================================================================

export function registerTierRoutes(app: Express): void {
  // All tier configurations
  app.get('/api/tiers', (req, res) => {
    res.json(TIER_CONFIGS);
  });

  // Specific tier configuration
  app.get('/api/tiers/:tier', (req, res) => {
    const tierConfig = getTierConfig(req.params.tier);
    res.json(tierConfig);
  });

  // Field information endpoint
  app.get('/api/fields', (req, res) => {
    res.json({
      total_possible_fields: '45,000+',
      comprehensive_engine_version: '4.0.0',
      tiers: {
        free: {
          fields: '~200',
          categories: [
            'summary',
            'basic_exif',
            'basic_image',
            'gps',
            'hashes',
            'calculated',
          ],
          file_types: ['Images (JPEG, PNG, GIF, WebP)'],
          max_size_mb: 10,
          locked: [
            'makernote',
            'iptc',
            'xmp',
            'extended_attributes',
            'serial_numbers',
            'video',
            'audio',
            'pdf',
            'advanced_analysis',
          ],
        },
        professional: {
          fields: '~1000',
          categories: [
            'summary',
            'exif',
            'image',
            'gps',
            'filesystem',
            'hashes',
            'calculated',
            'forensic',
            'audio',
            'pdf',
          ],
          file_types: ['Images + RAW + HEIC'],
          max_size_mb: 100,
          locked: [
            'video',
            'audio',
            'pdf',
            'advanced_analysis',
            'timeline_analysis',
          ],
        },
        forensic: {
          fields: '~15000',
          categories: ['all_fields'],
          file_types: ['Images + RAW + Video + Audio + PDF + SVG'],
          max_size_mb: 500,
          locked: [
            'medical_imaging',
            'astronomical_data',
            'scientific_data',
            'blockchain_provenance',
          ],
        },
        enterprise: {
          fields: '45,000+',
          categories: ['all_fields', 'batch_processing', 'api_access'],
          file_types: ['All file types'],
          max_size_mb: 2000,
          locked: [],
        },
      },
      categories: {
        summary: 'Basic file information (name, size, type)',
        exif: 'Camera settings, dates, software',
        image: 'Resolution, color mode, format details',
        gps: 'GPS coordinates with Google Maps links',
        filesystem: 'Permissions, ownership, timestamps',
        hashes: 'MD5, SHA256, SHA1, CRC32 checksums',
        calculated: 'Aspect ratio, megapixels, file age',
        forensic: 'Device identification, modification detection',
        makernote:
          'Vendor-specific camera data (Canon, Nikon, Sony, etc.)',
        iptc: 'News/photo agency metadata (copyright, keywords, captions)',
        xmp: 'Adobe metadata (editing history, keywords)',
        video: 'Codec, streams, chapters, HDR metadata',
        audio: 'Tags, album art, bitrate, format details',
        pdf: 'Pages, author, encryption, forms',
        svg: 'Elements, viewBox, scripts detection',
        extended_attributes: 'macOS Finder tags, Spotlight metadata',
        normalized: 'Normalized/searchable fields (camera/lens/exposure)',
        web_metadata: 'Open Graph, schema.org, and web metadata',
        social_media: 'Platform-specific social metadata',
        mobile_metadata: 'Smartphone computational photography fields',
        forensic_security: 'C2PA, signatures, provenance indicators',
        action_camera: 'GoPro/Action cam specific tags',
        print_publishing: 'Print/publishing workflow metadata',
        workflow_dam: 'DAM/workflow metadata',
        audio_advanced: 'ReplayGain and advanced audio analysis',
        video_advanced: 'HDR and professional video analysis',
        steganography_analysis: 'Hidden data detection signals',
        manipulation_detection: 'Tampering detection indicators',
        ai_detection: 'AI-generated content indicators',
        timeline_analysis: 'Forensic timeline reconstruction',
      },
      domains: {
        image_metadata: {
          total_fields: '15,000+',
          standards: [
            'EXIF (1,200+ fields)',
            'MakerNotes (7,000+ vendor-specific fields)',
            'IPTC (150+ fields)',
            'XMP (500+ fields)',
            'ICC Profiles (200+ fields)',
            'Computational Photography (300+ fields)',
          ],
        },
        video_metadata: {
          total_fields: '8,000+',
          standards: [
            'Container formats (2,000+ fields)',
            'Codec-specific (3,000+ fields)',
            'Professional video (3,000+ fields)',
          ],
        },
        audio_metadata: {
          total_fields: '3,500+',
          standards: [
            'ID3 (1,200+ fields)',
            'Vorbis/FLAC (300+ fields)',
            'Professional audio (2,000+ fields)',
          ],
        },
        document_metadata: {
          total_fields: '4,000+',
          standards: [
            'PDF (2,000+ fields)',
            'Office documents (1,000+ fields)',
            'HTML/Web (1,000+ fields)',
          ],
        },
        scientific_metadata: {
          total_fields: '15,000+',
          standards: [
            'DICOM medical imaging (8,000+ fields)',
            'FITS astronomy (3,000+ fields)',
            'Geospatial GIS (2,000+ fields)',
            'Scientific data formats (2,000+ fields)',
          ],
        },
        forensic_metadata: {
          total_fields: '2,500+',
          standards: [
            'Filesystem (500+ fields)',
            'Digital signatures (800+ fields)',
            'Security metadata (700+ fields)',
            'Device/Hardware (500+ fields)',
          ],
        },
      },
    });
  });

  // Sample files endpoint
  app.get('/api/samples', (req, res) => {
    const samples = [
      {
        id: 'sample_photo',
        name: 'Standard Photo',
        filename: 'sample_photo.jpg',
        description: 'JPEG with basic EXIF data - perfect for beginners',
        size: '2.3 MB',
        type: 'image/jpeg',
        highlights: ['Camera settings', 'Timestamp', 'Resolution'],
        tier_required: 'free',
      },
      {
        id: 'sample_gps',
        name: 'GPS Photo',
        filename: 'sample_gps.jpg',
        description: 'Photo with embedded GPS coordinates',
        size: '3.1 MB',
        type: 'image/jpeg',
        highlights: ['GPS coordinates', 'Google Maps link', 'Location data'],
        tier_required: 'professional',
      },
      {
        id: 'sample_raw',
        name: 'Canon RAW',
        filename: 'sample_raw.cr2',
        description: 'Canon RAW file with extensive MakerNotes',
        size: '24.5 MB',
        type: 'image/x-canon-cr2',
        highlights: ['Canon MakerNotes', 'Lens data', 'Camera serial'],
        tier_required: 'professional',
      },
      {
        id: 'sample_video',
        name: 'Video Sample',
        filename: 'sample_video.mp4',
        description: 'MP4 video with codec and stream information',
        size: '15.2 MB',
        type: 'video/mp4',
        highlights: ['Video codecs', 'Stream data', 'Duration'],
        tier_required: 'forensic',
      },
      {
        id: 'sample_audio',
        name: 'Audio File',
        filename: 'sample_audio.mp3',
        description: 'MP3 with ID3 tags and album art',
        size: '4.8 MB',
        type: 'audio/mpeg',
        highlights: ['ID3 tags', 'Album art', 'Audio quality'],
        tier_required: 'forensic',
      },
      {
        id: 'sample_pdf',
        name: 'PDF Document',
        filename: 'sample_document.pdf',
        description: 'PDF with document metadata and form fields',
        size: '1.2 MB',
        type: 'application/pdf',
        highlights: ['Document info', 'Page count', 'Creation software'],
        tier_required: 'forensic',
      },
    ];

    res.json({
      samples,
      total_count: samples.length,
      description: 'Sample files for demonstrating MetaExtract capabilities',
    });
  });

  // Sample file download endpoint
  app.get('/api/samples/:sampleId/download', async (req, res) => {
    try {
      const sampleId = req.params.sampleId;
      const samplePath = path.join(
        __dirname,
        '..',
        'sample-files',
        `${sampleId}.bin`
      );

      // Check if sample file exists
      try {
        await fs.access(samplePath);
      } catch {
        return res.status(404).json({ error: 'Sample file not found' });
      }

      // Get sample info
      const samples = [
        {
          id: 'sample_photo',
          filename: 'sample_photo.jpg',
          type: 'image/jpeg',
        },
        { id: 'sample_gps', filename: 'sample_gps.jpg', type: 'image/jpeg' },
        {
          id: 'sample_raw',
          filename: 'sample_raw.cr2',
          type: 'image/x-canon-cr2',
        },
        {
          id: 'sample_video',
          filename: 'sample_video.mp4',
          type: 'video/mp4',
        },
        {
          id: 'sample_audio',
          filename: 'sample_audio.mp3',
          type: 'audio/mpeg',
        },
        {
          id: 'sample_pdf',
          filename: 'sample_document.pdf',
          type: 'application/pdf',
        },
      ];

      const sample = samples.find((s) => s.id === sampleId);
      if (!sample) {
        return res.status(404).json({ error: 'Sample not found' });
      }

      res.setHeader('Content-Type', sample.type);
      res.setHeader(
        'Content-Disposition',
        `attachment; filename="${sample.filename}"`
      );

      const fileStream = require('fs').createReadStream(samplePath);
      fileStream.pipe(res);
    } catch (error) {
      console.error('Sample download error:', error);
      res.status(500).json({ error: 'Failed to download sample file' });
    }
  });
}
