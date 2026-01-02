/**
 * Sample File Library System
 * 
 * Manages curated sample files for onboarding and demonstration purposes.
 * Provides metadata explanations, difficulty levels, and use case categorization.
 */

import React, { createContext, useContext, useState, useCallback } from 'react';

// ============================================================================
// Types and Interfaces
// ============================================================================

export type FileType = 'image' | 'video' | 'audio' | 'document' | 'archive';
export type DifficultyLevel = 'basic' | 'intermediate' | 'advanced';
export type UseCase = 'personal' | 'professional' | 'forensic' | 'research' | 'legal';

export interface MetadataHighlight {
  field: string;
  value: string;
  explanation: string;
  importance: 'high' | 'medium' | 'low';
  category: string;
}

export interface SampleFile {
  id: string;
  name: string;
  filename: string;
  description: string;
  fileType: FileType;
  mimeType: string;
  size: number;
  sizeFormatted: string;
  difficulty: DifficultyLevel;
  useCases: UseCase[];
  tierRequired: string;
  
  // Metadata information
  metadataHighlights: MetadataHighlight[];
  expectedFieldCount: number;
  valueProposition: string;
  
  // Learning content
  whatYouWillLearn: string[];
  commonUses: string[];
  
  // Processing info
  estimatedProcessingTime: number; // seconds
  tags: string[];
}

export interface SampleCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  samples: SampleFile[];
}

export interface SampleLibraryState {
  categories: SampleCategory[];
  allSamples: SampleFile[];
  processedSamples: string[]; // IDs of samples user has processed
  favoriteSamples: string[]; // IDs of favorited samples
}

// ============================================================================
// Sample File Definitions
// ============================================================================

const SAMPLE_FILES: SampleFile[] = [
  // Basic Image Samples
  {
    id: 'sample-photo-basic',
    name: 'Vacation Photo',
    filename: 'vacation_beach.jpg',
    description: 'A typical smartphone photo with GPS and camera metadata',
    fileType: 'image',
    mimeType: 'image/jpeg',
    size: 2457600, // 2.4 MB
    sizeFormatted: '2.4 MB',
    difficulty: 'basic',
    useCases: ['personal'],
    tierRequired: 'free',
    metadataHighlights: [
      {
        field: 'GPS Coordinates',
        value: '34.0522° N, 118.2437° W',
        explanation: 'Shows exactly where this photo was taken - useful for organizing travel photos',
        importance: 'high',
        category: 'Location'
      },
      {
        field: 'Camera Model',
        value: 'iPhone 13 Pro',
        explanation: 'Identifies the device used to capture the image',
        importance: 'medium',
        category: 'Device'
      },
      {
        field: 'Date Taken',
        value: '2024-07-15 14:32:18',
        explanation: 'Exact timestamp when the photo was captured',
        importance: 'high',
        category: 'Temporal'
      },
      {
        field: 'Image Dimensions',
        value: '4032 x 3024 pixels',
        explanation: 'Resolution of the image - important for print quality',
        importance: 'medium',
        category: 'Technical'
      }
    ],
    expectedFieldCount: 45,
    valueProposition: 'Discover hidden location data, camera settings, and timestamps in your photos',
    whatYouWillLearn: [
      'How to find GPS coordinates in photos',
      'Understanding EXIF camera data',
      'Reading timestamps and date information',
      'Identifying the device that took the photo'
    ],
    commonUses: [
      'Organizing photo collections by location',
      'Verifying when and where photos were taken',
      'Understanding camera settings for better photography'
    ],
    estimatedProcessingTime: 2,
    tags: ['gps', 'camera', 'exif', 'beginner-friendly']
  },
  
  // Intermediate Image Sample
  {
    id: 'sample-photo-edited',
    name: 'Edited Professional Photo',
    filename: 'professional_edited.jpg',
    description: 'A professionally edited image showing software modification history',
    fileType: 'image',
    mimeType: 'image/jpeg',
    size: 5242880, // 5 MB
    sizeFormatted: '5.0 MB',
    difficulty: 'intermediate',
    useCases: ['professional', 'forensic'],
    tierRequired: 'professional',
    metadataHighlights: [
      {
        field: 'Software Used',
        value: 'Adobe Photoshop 2024',
        explanation: 'Shows which editing software modified this image',
        importance: 'high',
        category: 'Editing'
      },
      {
        field: 'Edit History',
        value: '3 modifications detected',
        explanation: 'Tracks how many times the image was edited',
        importance: 'high',
        category: 'Forensic'
      },
      {
        field: 'Color Profile',
        value: 'Adobe RGB (1998)',
        explanation: 'Professional color space used for high-quality printing',
        importance: 'medium',
        category: 'Technical'
      },
      {
        field: 'Creator',
        value: 'John Smith Photography',
        explanation: 'Copyright and attribution information',
        importance: 'high',
        category: 'Rights'
      }
    ],
    expectedFieldCount: 78,
    valueProposition: 'Uncover editing history, software used, and copyright information in professional images',
    whatYouWillLearn: [
      'Detecting image manipulation and edits',
      'Understanding professional color profiles',
      'Reading copyright and creator metadata',
      'Analyzing software modification history'
    ],
    commonUses: [
      'Verifying image authenticity',
      'Copyright and attribution tracking',
      'Understanding professional workflows'
    ],
    estimatedProcessingTime: 3,
    tags: ['editing', 'photoshop', 'copyright', 'professional']
  },
  
  // Advanced Forensic Sample
  {
    id: 'sample-photo-forensic',
    name: 'Forensic Evidence Photo',
    filename: 'evidence_analysis.jpg',
    description: 'Image with detailed forensic metadata for digital evidence analysis',
    fileType: 'image',
    mimeType: 'image/jpeg',
    size: 3145728, // 3 MB
    sizeFormatted: '3.0 MB',
    difficulty: 'advanced',
    useCases: ['forensic', 'legal', 'research'],
    tierRequired: 'forensic',
    metadataHighlights: [
      {
        field: 'Hash Signature',
        value: 'SHA-256: a3f5...',
        explanation: 'Cryptographic fingerprint proving file integrity',
        importance: 'high',
        category: 'Forensic'
      },
      {
        field: 'Modification Detection',
        value: 'No alterations detected',
        explanation: 'Forensic analysis confirms original file integrity',
        importance: 'high',
        category: 'Forensic'
      },
      {
        field: 'Thumbnail Analysis',
        value: 'Embedded thumbnail matches main image',
        explanation: 'Verifies no thumbnail substitution occurred',
        importance: 'high',
        category: 'Forensic'
      },
      {
        field: 'Device Serial',
        value: 'DMCE123456789',
        explanation: 'Unique identifier linking to specific camera device',
        importance: 'high',
        category: 'Device'
      }
    ],
    expectedFieldCount: 120,
    valueProposition: 'Perform deep forensic analysis to verify authenticity and trace digital evidence',
    whatYouWillLearn: [
      'Forensic hash verification techniques',
      'Detecting image tampering and manipulation',
      'Analyzing embedded thumbnails',
      'Tracing images to specific devices'
    ],
    commonUses: [
      'Legal evidence verification',
      'Digital forensics investigations',
      'Authenticity validation for court cases'
    ],
    estimatedProcessingTime: 5,
    tags: ['forensic', 'evidence', 'hash', 'tampering', 'advanced']
  },
  
  // Video Sample
  {
    id: 'sample-video-basic',
    name: 'Short Video Clip',
    filename: 'family_video.mp4',
    description: 'A short video with codec, duration, and device metadata',
    fileType: 'video',
    mimeType: 'video/mp4',
    size: 15728640, // 15 MB
    sizeFormatted: '15.0 MB',
    difficulty: 'intermediate',
    useCases: ['personal', 'professional'],
    tierRequired: 'professional',
    metadataHighlights: [
      {
        field: 'Video Codec',
        value: 'H.264/AVC',
        explanation: 'Compression format used for the video',
        importance: 'medium',
        category: 'Technical'
      },
      {
        field: 'Duration',
        value: '00:02:34',
        explanation: 'Total length of the video',
        importance: 'high',
        category: 'Content'
      },
      {
        field: 'Frame Rate',
        value: '30 fps',
        explanation: 'Frames per second - affects smoothness',
        importance: 'medium',
        category: 'Technical'
      },
      {
        field: 'Recording Device',
        value: 'GoPro Hero 11',
        explanation: 'Camera used to record the video',
        importance: 'high',
        category: 'Device'
      }
    ],
    expectedFieldCount: 65,
    valueProposition: 'Extract codec information, duration, frame rates, and recording device details',
    whatYouWillLearn: [
      'Understanding video codecs and formats',
      'Reading video duration and frame rates',
      'Identifying recording devices',
      'Analyzing video quality settings'
    ],
    commonUses: [
      'Video library organization',
      'Quality assessment',
      'Device identification'
    ],
    estimatedProcessingTime: 8,
    tags: ['video', 'codec', 'duration', 'gopro']
  },
  
  // Audio Sample
  {
    id: 'sample-audio-basic',
    name: 'Music Track',
    filename: 'song_sample.mp3',
    description: 'Audio file with ID3 tags, artist info, and technical metadata',
    fileType: 'audio',
    mimeType: 'audio/mpeg',
    size: 4194304, // 4 MB
    sizeFormatted: '4.0 MB',
    difficulty: 'basic',
    useCases: ['personal'],
    tierRequired: 'free',
    metadataHighlights: [
      {
        field: 'Artist',
        value: 'Sample Artist',
        explanation: 'Performer or creator of the audio',
        importance: 'high',
        category: 'Content'
      },
      {
        field: 'Album',
        value: 'Greatest Hits 2024',
        explanation: 'Album or collection this track belongs to',
        importance: 'medium',
        category: 'Content'
      },
      {
        field: 'Bitrate',
        value: '320 kbps',
        explanation: 'Audio quality - higher is better',
        importance: 'medium',
        category: 'Technical'
      },
      {
        field: 'Duration',
        value: '00:03:45',
        explanation: 'Length of the audio track',
        importance: 'high',
        category: 'Content'
      }
    ],
    expectedFieldCount: 35,
    valueProposition: 'Discover artist information, album details, and audio quality metrics',
    whatYouWillLearn: [
      'Reading ID3 tags in audio files',
      'Understanding audio bitrates and quality',
      'Extracting artist and album information',
      'Analyzing audio technical specifications'
    ],
    commonUses: [
      'Music library organization',
      'Quality verification',
      'Metadata cleanup and correction'
    ],
    estimatedProcessingTime: 3,
    tags: ['audio', 'music', 'id3', 'mp3']
  },
  
  // Document Sample
  {
    id: 'sample-document-basic',
    name: 'PDF Document',
    filename: 'report_sample.pdf',
    description: 'PDF with author, creation date, and software metadata',
    fileType: 'document',
    mimeType: 'application/pdf',
    size: 1048576, // 1 MB
    sizeFormatted: '1.0 MB',
    difficulty: 'basic',
    useCases: ['professional', 'research'],
    tierRequired: 'free',
    metadataHighlights: [
      {
        field: 'Author',
        value: 'Jane Doe',
        explanation: 'Person who created the document',
        importance: 'high',
        category: 'Content'
      },
      {
        field: 'Creation Date',
        value: '2024-06-20 09:15:00',
        explanation: 'When the document was first created',
        importance: 'high',
        category: 'Temporal'
      },
      {
        field: 'Software',
        value: 'Microsoft Word 2024',
        explanation: 'Application used to create the PDF',
        importance: 'medium',
        category: 'Technical'
      },
      {
        field: 'Page Count',
        value: '12 pages',
        explanation: 'Total number of pages in the document',
        importance: 'medium',
        category: 'Content'
      }
    ],
    expectedFieldCount: 28,
    valueProposition: 'Extract author information, creation dates, and document properties',
    whatYouWillLearn: [
      'Reading PDF metadata and properties',
      'Identifying document authors and creators',
      'Understanding creation and modification dates',
      'Analyzing software used to create documents'
    ],
    commonUses: [
      'Document authenticity verification',
      'Author attribution',
      'Version tracking'
    ],
    estimatedProcessingTime: 2,
    tags: ['pdf', 'document', 'author', 'office']
  }
];

// ============================================================================
// Sample Categories
// ============================================================================

const SAMPLE_CATEGORIES: SampleCategory[] = [
  {
    id: 'getting-started',
    name: 'Getting Started',
    description: 'Perfect for first-time users - simple files with clear, valuable metadata',
    icon: 'Rocket',
    samples: SAMPLE_FILES.filter(s => s.difficulty === 'basic')
  },
  {
    id: 'professional',
    name: 'Professional Use',
    description: 'Advanced samples for professional workflows and detailed analysis',
    icon: 'Briefcase',
    samples: SAMPLE_FILES.filter(s => s.useCases.includes('professional'))
  },
  {
    id: 'forensic',
    name: 'Forensic Analysis',
    description: 'Deep forensic examination samples for evidence and authenticity verification',
    icon: 'Shield',
    samples: SAMPLE_FILES.filter(s => s.useCases.includes('forensic'))
  },
  {
    id: 'by-type',
    name: 'By File Type',
    description: 'Explore samples organized by file format',
    icon: 'FolderOpen',
    samples: SAMPLE_FILES
  }
];

// ============================================================================
// Context
// ============================================================================

export interface SampleComparison {
  samples: SampleFile[];
  commonFields: string[];
  uniqueFields: Map<string, string[]>; // sampleId -> unique field names
  difficultyRange: { min: DifficultyLevel; max: DifficultyLevel };
  sharedUseCases: UseCase[];
  comparisonInsights: string[];
}

interface SampleLibraryContextType {
  state: SampleLibraryState;
  getSampleById: (id: string) => SampleFile | undefined;
  getSamplesByDifficulty: (difficulty: DifficultyLevel) => SampleFile[];
  getSamplesByUseCase: (useCase: UseCase) => SampleFile[];
  getSamplesByFileType: (fileType: FileType) => SampleFile[];
  getRecommendedSamples: (userProfile: { 
    useCase: string; 
    technicalLevel: string;
    primaryFileTypes?: string[];
    goals?: string[];
    industry?: string;
  }) => SampleFile[];
  compareSamples: (sampleIds: string[]) => SampleComparison | null;
  markSampleProcessed: (sampleId: string) => void;
  toggleFavorite: (sampleId: string) => void;
  isSampleProcessed: (sampleId: string) => boolean;
  isSampleFavorited: (sampleId: string) => boolean;
}

const SampleLibraryContext = createContext<SampleLibraryContextType | null>(null);

export function SampleLibraryProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<SampleLibraryState>({
    categories: SAMPLE_CATEGORIES,
    allSamples: SAMPLE_FILES,
    processedSamples: [],
    favoriteSamples: []
  });

  const getSampleById = useCallback((id: string) => {
    return state.allSamples.find(s => s.id === id);
  }, [state.allSamples]);

  const getSamplesByDifficulty = useCallback((difficulty: DifficultyLevel) => {
    return state.allSamples.filter(s => s.difficulty === difficulty);
  }, [state.allSamples]);

  const getSamplesByUseCase = useCallback((useCase: UseCase) => {
    return state.allSamples.filter(s => s.useCases.includes(useCase));
  }, [state.allSamples]);

  const getSamplesByFileType = useCallback((fileType: FileType) => {
    return state.allSamples.filter(s => s.fileType === fileType);
  }, [state.allSamples]);

  const getRecommendedSamples = useCallback((userProfile: { 
    useCase: string; 
    technicalLevel: string;
    primaryFileTypes?: string[];
    goals?: string[];
    industry?: string;
  }) => {
    // Map technical level to difficulty
    const difficultyMap: Record<string, DifficultyLevel> = {
      'beginner': 'basic',
      'intermediate': 'intermediate',
      'advanced': 'advanced'
    };

    const difficulty = difficultyMap[userProfile.technicalLevel] || 'basic';
    const useCase = userProfile.useCase as UseCase;

    // Score each sample based on multiple factors
    const scoredSamples = state.allSamples.map(sample => {
      let score = 0;

      // Primary factor: Use case match (40 points)
      if (sample.useCases.includes(useCase)) {
        score += 40;
      }

      // Secondary factor: Difficulty match (30 points)
      if (sample.difficulty === difficulty) {
        score += 30;
      } else if (
        // Allow one level up or down
        (difficulty === 'basic' && sample.difficulty === 'intermediate') ||
        (difficulty === 'intermediate' && (sample.difficulty === 'basic' || sample.difficulty === 'advanced')) ||
        (difficulty === 'advanced' && sample.difficulty === 'intermediate')
      ) {
        score += 15;
      }

      // Tertiary factor: File type preference (20 points)
      if (userProfile.primaryFileTypes && userProfile.primaryFileTypes.length > 0) {
        const fileTypeMatch = userProfile.primaryFileTypes.some(type => 
          sample.fileType === type || sample.tags.includes(type)
        );
        if (fileTypeMatch) {
          score += 20;
        }
      }

      // Quaternary factor: Goals alignment (10 points)
      if (userProfile.goals && userProfile.goals.length > 0) {
        const goalMatch = userProfile.goals.some(goal =>
          sample.whatYouWillLearn.some(learning => 
            learning.toLowerCase().includes(goal.toLowerCase())
          ) ||
          sample.commonUses.some(use =>
            use.toLowerCase().includes(goal.toLowerCase())
          )
        );
        if (goalMatch) {
          score += 10;
        }
      }

      // Bonus: Industry-specific samples
      if (userProfile.industry) {
        const industryMatch = sample.tags.some(tag =>
          tag.toLowerCase().includes(userProfile.industry!.toLowerCase())
        );
        if (industryMatch) {
          score += 5;
        }
      }

      // Bonus: Unprocessed samples (encourage exploration)
      if (!state.processedSamples.includes(sample.id)) {
        score += 5;
      }

      // Penalty: Already processed samples (but don't exclude completely)
      if (state.processedSamples.includes(sample.id)) {
        score -= 10;
      }

      return { sample, score };
    });

    // Sort by score and return top recommendations
    const recommended = scoredSamples
      .sort((a, b) => b.score - a.score)
      .slice(0, 5) // Top 5 recommendations
      .map(item => item.sample);

    // Ensure we have at least 3 recommendations
    if (recommended.length < 3) {
      // Add more samples from same difficulty
      const additional = state.allSamples
        .filter(s => s.difficulty === difficulty && !recommended.includes(s))
        .slice(0, 3 - recommended.length);
      
      return [...recommended, ...additional];
    }

    return recommended;
  }, [state.allSamples, state.processedSamples]);

  const markSampleProcessed = useCallback((sampleId: string) => {
    setState(prev => ({
      ...prev,
      processedSamples: prev.processedSamples.includes(sampleId)
        ? prev.processedSamples
        : [...prev.processedSamples, sampleId]
    }));
  }, []);

  const toggleFavorite = useCallback((sampleId: string) => {
    setState(prev => ({
      ...prev,
      favoriteSamples: prev.favoriteSamples.includes(sampleId)
        ? prev.favoriteSamples.filter(id => id !== sampleId)
        : [...prev.favoriteSamples, sampleId]
    }));
  }, []);

  const isSampleProcessed = useCallback((sampleId: string) => {
    return state.processedSamples.includes(sampleId);
  }, [state.processedSamples]);

  const isSampleFavorited = useCallback((sampleId: string) => {
    return state.favoriteSamples.includes(sampleId);
  }, [state.favoriteSamples]);

  /**
   * Compare multiple sample files to identify similarities and differences
   */
  const compareSamples = useCallback((sampleIds: string[]): SampleComparison | null => {
    if (sampleIds.length < 2) {
      console.warn('Need at least 2 samples to compare');
      return null;
    }

    // Get all samples
    const samples = sampleIds
      .map(id => state.allSamples.find(s => s.id === id))
      .filter((s): s is SampleFile => s !== undefined);

    if (samples.length < 2) {
      console.warn('Could not find all samples for comparison');
      return null;
    }

    // Find common metadata fields
    const allFields = samples.map(s => 
      s.metadataHighlights.map(h => h.field)
    );
    
    const commonFields = allFields[0].filter(field =>
      allFields.every(fields => fields.includes(field))
    );

    // Find unique fields for each sample
    const uniqueFields = new Map<string, string[]>();
    samples.forEach(sample => {
      const sampleFields = sample.metadataHighlights.map(h => h.field);
      const unique = sampleFields.filter(field => !commonFields.includes(field));
      uniqueFields.set(sample.id, unique);
    });

    // Determine difficulty range
    const difficulties: DifficultyLevel[] = ['basic', 'intermediate', 'advanced'];
    const sampleDifficulties = samples.map(s => s.difficulty);
    const minDifficultyIndex = Math.min(...sampleDifficulties.map(d => difficulties.indexOf(d)));
    const maxDifficultyIndex = Math.max(...sampleDifficulties.map(d => difficulties.indexOf(d)));

    const difficultyRange = {
      min: difficulties[minDifficultyIndex],
      max: difficulties[maxDifficultyIndex]
    };

    // Find shared use cases
    const allUseCases = samples.map(s => s.useCases);
    const sharedUseCases = allUseCases[0].filter(useCase =>
      allUseCases.every(cases => cases.includes(useCase))
    );

    // Generate comparison insights
    const comparisonInsights: string[] = [];

    // File type comparison
    const fileTypes = new Set(samples.map(s => s.fileType));
    if (fileTypes.size === 1) {
      comparisonInsights.push(`All samples are ${Array.from(fileTypes)[0]} files`);
    } else {
      comparisonInsights.push(`Comparing ${fileTypes.size} different file types: ${Array.from(fileTypes).join(', ')}`);
    }

    // Difficulty comparison
    if (difficultyRange.min === difficultyRange.max) {
      comparisonInsights.push(`All samples are at ${difficultyRange.min} difficulty level`);
    } else {
      comparisonInsights.push(`Difficulty ranges from ${difficultyRange.min} to ${difficultyRange.max}`);
    }

    // Field count comparison
    const fieldCounts = samples.map(s => s.expectedFieldCount);
    const minFields = Math.min(...fieldCounts);
    const maxFields = Math.max(...fieldCounts);
    comparisonInsights.push(`Metadata field counts range from ${minFields} to ${maxFields} fields`);

    // Common fields insight
    if (commonFields.length > 0) {
      comparisonInsights.push(`${commonFields.length} metadata fields are common across all samples`);
    } else {
      comparisonInsights.push('No common metadata fields - these files have very different metadata structures');
    }

    // Use case insight
    if (sharedUseCases.length > 0) {
      comparisonInsights.push(`Shared use cases: ${sharedUseCases.join(', ')}`);
    } else {
      comparisonInsights.push('These samples serve different use cases');
    }

    // Processing time comparison
    const processingTimes = samples.map(s => s.estimatedProcessingTime);
    const avgProcessingTime = processingTimes.reduce((sum, t) => sum + t, 0) / processingTimes.length;
    comparisonInsights.push(`Average processing time: ${avgProcessingTime.toFixed(1)} seconds`);

    // Tier requirement comparison
    const tiers = new Set(samples.map(s => s.tierRequired));
    if (tiers.size === 1) {
      comparisonInsights.push(`All samples require ${Array.from(tiers)[0]} tier`);
    } else {
      comparisonInsights.push(`Requires different subscription tiers: ${Array.from(tiers).join(', ')}`);
    }

    return {
      samples,
      commonFields,
      uniqueFields,
      difficultyRange,
      sharedUseCases,
      comparisonInsights
    };
  }, [state.allSamples]);

  return (
    <SampleLibraryContext.Provider
      value={{
        state,
        getSampleById,
        getSamplesByDifficulty,
        getSamplesByUseCase,
        getSamplesByFileType,
        getRecommendedSamples,
        compareSamples,
        markSampleProcessed,
        toggleFavorite,
        isSampleProcessed,
        isSampleFavorited
      }}
    >
      {children}
    </SampleLibraryContext.Provider>
  );
}

export function useSampleLibrary() {
  const context = useContext(SampleLibraryContext);
  if (!context) {
    throw new Error('useSampleLibrary must be used within a SampleLibraryProvider');
  }
  return context;
}
