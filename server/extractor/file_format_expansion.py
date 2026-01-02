"""
MetaExtract File Format Expansion System

This module analyzes usage patterns from monitoring data to identify and prioritize
new file format support based on actual usage.
"""

import json
import time
import statistics
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re
import mimetypes
from pathlib import Path


class FileFormatAnalyzer:
    """Analyzes monitoring data to identify file format usage patterns."""
    
    def __init__(self):
        self.usage_patterns = defaultdict(int)
        self.error_patterns = defaultdict(int)
        self.performance_by_format = defaultdict(list)
        self.trend_data = defaultdict(list)
        self.last_analysis_time = time.time()
    
    def analyze_monitoring_data(self, monitoring_data: Dict) -> Dict[str, Any]:
        """Analyze monitoring data to identify file format usage patterns."""
        # Extract file type usage from monitoring data
        metrics = monitoring_data.get('metrics', {})
        file_type_usage = metrics.get('file_type_usage', {})
        
        # Update usage patterns
        for file_type, count in file_type_usage.items():
            self.usage_patterns[file_type] += count
            
        # Analyze error patterns by file type
        recent_errors = metrics.get('recent_errors', {})
        
        # Get performance data by file type
        performance_data = self._extract_performance_by_format(monitoring_data)
        
        # Calculate usage statistics
        total_requests = sum(self.usage_patterns.values())
        
        # Calculate statistics for each format
        format_stats = {}
        for file_type, count in self.usage_patterns.items():
            format_stats[file_type] = {
                'usage_count': count,
                'usage_percentage': (count / total_requests * 100) if total_requests > 0 else 0,
                'error_count': self.error_patterns.get(file_type, 0),
                'avg_processing_time': statistics.mean(self.performance_by_format[file_type]) 
                                    if self.performance_by_format[file_type] else 0,
                'performance_samples': len(self.performance_by_format[file_type])
            }
        
        # Identify formats that might need better support
        recommendations = self._generate_recommendations(format_stats, recent_errors)
        
        self.last_analysis_time = time.time()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'format_statistics': format_stats,
            'recommendations': recommendations,
            'total_requests': total_requests,
            'analyzed_formats': list(format_stats.keys())
        }
    
    def _extract_performance_by_format(self, monitoring_data: Dict) -> Dict[str, List[float]]:
        """Extract performance data by file format from monitoring data."""
        # This would typically come from the analytics module
        # For now, we'll simulate it based on available data
        return {}
    
    def _generate_recommendations(self, format_stats: Dict, recent_errors: Dict) -> List[Dict[str, Any]]:
        """Generate recommendations for file format support based on usage patterns."""
        recommendations = []
        
        # Sort formats by usage count
        sorted_formats = sorted(
            format_stats.items(), 
            key=lambda x: x[1]['usage_count'], 
            reverse=True
        )
        
        # Identify high-usage formats with performance issues
        for file_type, stats in sorted_formats[:10]:  # Top 10 formats
            if stats['usage_count'] > 10:  # Only consider formats with significant usage
                recommendation = {
                    'file_type': file_type,
                    'usage_count': stats['usage_count'],
                    'usage_percentage': stats['usage_percentage'],
                    'priority': 'high' if stats['usage_percentage'] > 5 else 'medium' if stats['usage_percentage'] > 1 else 'low',
                    'reason': 'High usage frequency'
                }
                
                # Check if there are performance issues
                if stats['avg_processing_time'] > 5.0:  # More than 5 seconds average
                    recommendation['performance_concern'] = f"Slow processing: {stats['avg_processing_time']:.2f}s avg"
                    recommendation['priority'] = 'high'
                
                # Check error rate
                error_rate = stats['error_count'] / stats['usage_count'] if stats['usage_count'] > 0 else 0
                if error_rate > 0.1:  # More than 10% error rate
                    recommendation['error_concern'] = f"High error rate: {error_rate:.2%}"
                    recommendation['priority'] = 'high'
                
                recommendations.append(recommendation)
        
        # Also identify formats that are requested but not well supported
        for error_type, count in recent_errors.items():
            if 'format' in error_type.lower() or 'unsupported' in error_type.lower():
                recommendations.append({
                    'file_type': 'unknown_or_unsupported',
                    'usage_count': count,
                    'priority': 'high',
                    'reason': 'Unsupported format errors',
                    'error_type': error_type
                })
        
        return recommendations
    
    def get_format_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get trends for file format usage over time."""
        # This would typically analyze historical data
        # For now, we'll return a placeholder
        return {
            'period_days': days,
            'trends': dict(list(self.trend_data.items())[:10])  # Top 10 trends
        }


class FileFormatExpander:
    """Manages the expansion of supported file formats based on usage patterns."""
    
    def __init__(self):
        self.analyzer = FileFormatAnalyzer()
        self.supported_formats = self._get_currently_supported_formats()
        self.proposed_formats = []
        self.implementation_status = {}
    
    def _get_currently_supported_formats(self) -> set:
        """Get currently supported file formats."""
        # This would typically come from the actual extractor modules
        # For now, we'll return a comprehensive list
        return {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.heic', '.heif', '.svg', '.ico',
            '.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.wmv',
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.odt', '.ods', '.odp',
            '.dcm', '.dicom',  # Medical imaging
            '.fits', '.fit', '.fts',  # Astronomical data
            '.h5', '.hdf5', '.he5',  # Scientific data
            '.nc', '.netcdf', '.nc4',  # NetCDF
            '.cr2', '.cr3', '.nef', '.arw', '.dng',  # RAW formats
            '.psd', '.ai', '.indd',  # Design formats
        }
    
    def analyze_usage_and_recommend_formats(self, monitoring_data: Dict) -> Dict[str, Any]:
        """Analyze usage patterns and recommend new formats to support."""
        analysis = self.analyzer.analyze_monitoring_data(monitoring_data)
        
        # Filter out already supported formats
        recommendations = []
        for rec in analysis['recommendations']:
            file_type = rec.get('file_type', '').lower()
            
            # Try to extract extension from file type
            ext = self._extract_extension_from_type(file_type)
            
            if ext and ext not in self.supported_formats:
                rec['extension'] = ext
                recommendations.append(rec)
        
        analysis['new_format_recommendations'] = recommendations
        return analysis
    
    def _extract_extension_from_type(self, file_type: str) -> Optional[str]:
        """Extract file extension from MIME type or other format identifier."""
        if not file_type:
            return None
        
        # Handle MIME types
        if '/' in file_type:
            # Try to guess extension from MIME type
            ext = mimetypes.guess_extension(file_type)
            if ext:
                return ext.lower()
        
        # Handle direct extensions
        if file_type.startswith('.'):
            return file_type.lower()
        
        # Handle common format names
        format_to_ext = {
            'jpeg': '.jpeg',
            'tiff': '.tiff',
            'mpeg': '.mpg',
            'quicktime': '.mov',
            'wave': '.wav',
            'adobe': '.pdf',
            'msword': '.doc',
            'vnd.ms-excel': '.xls',
            'vnd.ms-powerpoint': '.ppt',
        }
        
        return format_to_ext.get(file_type.lower())
    
    def generate_implementation_plan(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Generate an implementation plan for new file formats."""
        # Sort recommendations by priority
        sorted_recs = sorted(
            recommendations, 
            key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x.get('priority', 'low'), 1), 
            reverse=True
        )
        
        plan = {
            'timestamp': datetime.now().isoformat(),
            'recommended_formats': sorted_recs,
            'implementation_phases': {
                'phase_1': [],  # High priority
                'phase_2': [],  # Medium priority
                'phase_3': []   # Low priority
            },
            'estimated_effort': {}
        }
        
        for rec in sorted_recs:
            priority = rec.get('priority', 'low')
            if priority == 'high':
                plan['implementation_phases']['phase_1'].append(rec)
            elif priority == 'medium':
                plan['implementation_phases']['phase_2'].append(rec)
            else:
                plan['implementation_phases']['phase_3'].append(rec)
        
        # Estimate implementation effort
        for rec in sorted_recs:
            ext = rec.get('extension', 'unknown')
            effort = self._estimate_implementation_effort(ext)
            plan['estimated_effort'][ext] = effort
        
        return plan
    
    def _estimate_implementation_effort(self, extension: str) -> Dict[str, Any]:
        """Estimate the effort required to implement support for a format."""
        # Base effort categories
        well_documented_formats = {
            '.epub', '.mobi', '.azw', '.azw3',  # E-book formats
            '.dwg', '.dxf',  # CAD formats
            '.stl', '.obj', '.fbx',  # 3D formats
            '.dwf',  # Design format
            '.xcf',  # GIMP format
        }
        
        complex_formats = {
            '.psd', '.ai', '.indd',  # Adobe formats
            '.doc', '.xls', '.ppt',  # Legacy MS formats
        }
        
        standard_formats = {
            '.xml', '.json', '.yaml', '.yml',  # Text-based
            '.zip', '.rar', '.7z', '.tar', '.gz',  # Archives
        }
        
        effort = {
            'complexity': 'medium',
            'estimated_time_hours': 8,
            'dependencies': [],
            'risk_level': 'low'
        }
        
        if extension in well_documented_formats:
            effort.update({
                'complexity': 'low',
                'estimated_time_hours': 4,
                'risk_level': 'low'
            })
        elif extension in complex_formats:
            effort.update({
                'complexity': 'high',
                'estimated_time_hours': 16,
                'risk_level': 'medium'
            })
        elif extension in standard_formats:
            effort.update({
                'complexity': 'low',
                'estimated_time_hours': 2,
                'risk_level': 'low'
            })
        
        return effort
    
    def get_popular_unsupported_formats(self, monitoring_data: Dict, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most popular unsupported file formats from monitoring data."""
        analysis = self.analyze_usage_and_recommend_formats(monitoring_data)
        recommendations = analysis.get('new_format_recommendations', [])
        
        # Sort by usage count
        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: x.get('usage_count', 0),
            reverse=True
        )
        
        return sorted_recommendations[:limit]


# Global file format expander instance
_format_expander = None


def get_format_expander():
    """Get the global format expander instance."""
    global _format_expander
    if _format_expander is None:
        _format_expander = FileFormatExpander()
    return _format_expander


def analyze_format_usage(monitoring_data: Dict) -> Dict[str, Any]:
    """Analyze format usage patterns and get recommendations."""
    expander = get_format_expander()
    return expander.analyze_usage_and_recommend_formats(monitoring_data)


def get_implementation_plan(monitoring_data: Dict) -> Dict[str, Any]:
    """Get an implementation plan for new file formats based on usage."""
    expander = get_format_expander()
    analysis = expander.analyze_usage_and_recommend_formats(monitoring_data)
    recommendations = analysis.get('new_format_recommendations', [])
    return expander.generate_implementation_plan(recommendations)


def get_popular_unsupported_formats(monitoring_data: Dict, limit: int = 10) -> List[Dict[str, Any]]:
    """Get the most popular unsupported file formats."""
    expander = get_format_expander()
    return expander.get_popular_unsupported_formats(monitoring_data, limit)


# Example usage and testing
if __name__ == "__main__":
    import statistics
    
    print("Testing file format expansion system...")
    
    # Create mock monitoring data
    mock_monitoring_data = {
        'metrics': {
            'file_type_usage': {
                'image/jpeg': 1500,
                'image/png': 1200,
                'image/gif': 800,
                'application/pdf': 600,
                'video/mp4': 400,
                'audio/mp3': 300,
                'application/msword': 200,
                'application/vnd.ms-excel': 150,
                'image/tiff': 100,
                'application/x-dosexec': 50,  # This would be an unsupported format
                'application/epub+zip': 75,    # This would be a supported format
                'application/x-unknown': 25,
            },
            'recent_errors': {
                'UnsupportedFormatError': 15,
                'UnknownMimeTypeError': 8,
                'FileFormatNotSupported': 12,
            }
        }
    }
    
    print("\n--- Analyzing Format Usage ---")
    analysis = analyze_format_usage(mock_monitoring_data)
    
    print(f"Total requests analyzed: {analysis['total_requests']}")
    print(f"Analyzed formats: {len(analysis['analyzed_formats'])}")
    
    print(f"\n--- Format Statistics (Top 5) ---")
    top_formats = sorted(
        analysis['format_statistics'].items(),
        key=lambda x: x[1]['usage_count'],
        reverse=True
    )[:5]
    
    for fmt, stats in top_formats:
        print(f"  {fmt}: {stats['usage_count']} uses ({stats['usage_percentage']:.1f}%)")
    
    print(f"\n--- New Format Recommendations ---")
    new_recommendations = analysis.get('new_format_recommendations', [])
    if new_recommendations:
        for rec in new_recommendations[:5]:  # Show top 5
            print(f"  {rec.get('file_type', 'unknown')}: {rec.get('usage_count', 0)} uses, "
                  f"Priority: {rec.get('priority', 'unknown')}")
            if 'performance_concern' in rec:
                print(f"    Performance: {rec['performance_concern']}")
            if 'error_concern' in rec:
                print(f"    Error: {rec['error_concern']}")
    else:
        print("  No new format recommendations found.")
    
    print(f"\n--- Implementation Plan ---")
    plan = get_implementation_plan(mock_monitoring_data)
    
    for phase, formats in plan['implementation_phases'].items():
        if formats:
            print(f"  {phase.upper()}: {len(formats)} formats")
            for fmt in formats[:3]:  # Show first 3 of each phase
                print(f"    - {fmt.get('file_type', 'unknown')} "
                      f"(Priority: {fmt.get('priority', 'unknown')})")
    
    print(f"\n--- Popular Unsupported Formats ---")
    unsupported = get_popular_unsupported_formats(mock_monitoring_data)
    if unsupported:
        for fmt in unsupported[:5]:
            print(f"  {fmt.get('file_type', 'unknown')}: {fmt.get('usage_count', 0)} uses")
    else:
        print("  No popular unsupported formats found.")