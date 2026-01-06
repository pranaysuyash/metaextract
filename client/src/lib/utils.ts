/**
 * Utility functions for the MetaExtract application
 */

import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Compose class names using clsx and resolve Tailwind class conflicts with twMerge.
 * Accepts strings, arrays, objects, and conditional values similar to clsx.
 */
export function cn(...inputs: any[]) {
  return twMerge(clsx(...inputs));
}

/**
 * Format file size in human-readable format
 * @param bytes File size in bytes
 * @returns Formatted file size string
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Get appropriate icon for file type
 * @param fileType MIME type of the file
 * @returns Icon component name as string
 */
export function getFileIcon(fileType: string): string {
  if (fileType.includes('image')) return 'FileImage';
  if (fileType.includes('pdf')) return 'FileText';
  if (fileType.includes('dicom') || fileType.includes('medical'))
    return 'Database';
  if (fileType.includes('audio')) return 'Music';
  if (fileType.includes('video')) return 'Video';
  return 'File';
}

/**
 * Get file extension from filename
 * @param filename Name of the file
 * @returns File extension without the dot
 */
export function getFileExtension(filename: string): string {
  const parts = filename.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
}

/**
 * Validate if a file type is supported
 * @param fileType MIME type of the file
 * @returns True if the file type is supported
 */
export function isFileTypeSupported(fileType: string): boolean {
  const supportedTypes = [
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/gif',
    'image/bmp',
    'image/webp',
    'application/pdf',
    'application/dicom',
    'image/dicom',
    'audio/mp3',
    'audio/wav',
    'audio/flac',
    'video/mp4',
    'video/avi',
    'video/mov',
  ];

  return supportedTypes.includes(fileType.toLowerCase());
}

/**
 * Get a color based on authenticity score
 * @param score Authenticity score (0-100)
 * @returns Tailwind CSS color class
 */
export function getAuthenticityColor(score: number): string {
  if (score >= 80) return 'text-emerald-400';
  if (score >= 60) return 'text-yellow-400';
  return 'text-red-400';
}

/**
 * Format a date string to a more readable format
 * @param dateStr Date string to format
 * @returns Formatted date string
 */
export function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleString();
  } catch {
    return dateStr;
  }
}

/**
 * Sanitize a filename to remove potentially problematic characters
 * @param filename Original filename
 * @returns Sanitized filename
 */
export function sanitizeFilename(filename: string): string {
  return filename.replace(/[<>:"/\\|?*]/g, '_');
}

/**
 * Generate a human-readable label for a metadata key
 * @param key Metadata key
 * @returns Human-readable label
 */
export function getMetadataLabel(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Get a color based on the severity of a finding
 * @param severity Severity level ('info', 'warning', 'critical')
 * @returns Tailwind CSS color class
 */
export function getSeverityColor(
  severity: 'info' | 'warning' | 'critical'
): string {
  switch (severity) {
    case 'critical':
      return 'text-red-400';
    case 'warning':
      return 'text-yellow-400';
    case 'info':
      return 'text-blue-400';
    default:
      return 'text-slate-400';
  }
}

/**
 * Calculate the percentage of a value relative to a total
 * @param value The value to calculate percentage for
 * @param total The total value
 * @returns Percentage as a number
 */
export function calculatePercentage(value: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
}
