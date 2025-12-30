#!/usr/bin/env python3
"""
Metadata Comparison Module for MetaExtract

Provides side-by-side comparison of metadata from multiple files:
- Field-by-field comparison
- Difference highlighting
- Similarity scoring
- Batch comparison
- Export capabilities
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import difflib

logger = logging.getLogger("metaextract.comparison")

class MetadataComparator:
    """Advanced metadata comparison and analysis."""
    
    def __init__(self):
        self.comparison_categories = [
            "file_info",
            "exif_data", 
            "image_properties",
            "gps_data",
            "timestamps",
            "camera_settings",
            "software_info",
            "hashes",
            "forensic_data"
        ]
    
    def compare_files(
        self,
        file_metadata_list: List[Dict[str, Any]],
        comparison_mode: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Compare metadata from multiple files.
        
        Args:
            file_metadata_list: List of metadata dictionaries
            comparison_mode: "detailed", "summary", or "differences_only"
            
        Returns:
            Comprehensive comparison results
        """
        if len(file_metadata_list) < 2:
            return {"error": "At least 2 files required for comparison"}
        
        try:
            results = {
                "comparison_info": {
                    "timestamp": datetime.now().isoformat(),
                    "files_compared": len(file_metadata_list),
                    "comparison_mode": comparison_mode,
                    "categories_analyzed": len(self.comparison_categories)
                },
                "file_summaries": [],
                "field_comparisons": {},
                "similarity_analysis": {},
                "differences_summary": {},
                "recommendations": []
            }
            
            # Extract file summaries
            for i, metadata in enumerate(file_metadata_list):
                file_summary = self._extract_file_summary(metadata, i)
                results["file_summaries"].append(file_summary)
            
            # Perform category-wise comparisons
            for category in self.comparison_categories:
                category_comparison = self._compare_category(
                    file_metadata_list, category, comparison_mode
                )
                if category_comparison:
                    results["field_comparisons"][category] = category_comparison
            
            # Calculate overall similarity
            results["similarity_analysis"] = self._calculate_similarity(file_metadata_list)
            
            # Generate differences summary
            results["differences_summary"] = self._generate_differences_summary(
                results["field_comparisons"]
            )
            
            # Generate recommendations
            results["recommendations"] = self._generate_comparison_recommendations(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return {"error": f"Comparison failed: {str(e)}"}
    
    def compare_two_files(
        self,
        metadata1: Dict[str, Any],
        metadata2: Dict[str, Any],
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        Detailed comparison between exactly two files.
        
        Args:
            metadata1: First file metadata
            metadata2: Second file metadata  
            focus_areas: Specific areas to focus on (optional)
            
        Returns:
            Detailed two-file comparison
        """
        try:
            results = {
                "comparison_type": "two_file_detailed",
                "timestamp": datetime.now().isoformat(),
                "file1_summary": self._extract_file_summary(metadata1, 0),
                "file2_summary": self._extract_file_summary(metadata2, 1),
                "detailed_differences": {},
                "similarity_score": 0.0,
                "match_analysis": {},
                "recommendations": []
            }
            
            # Focus on specific areas if provided
            categories_to_compare = focus_areas if focus_areas else self.comparison_categories
            
            # Detailed field-by-field comparison
            for category in categories_to_compare:
                category_diff = self._detailed_category_comparison(
                    metadata1, metadata2, category
                )
                if category_diff:
                    results["detailed_differences"][category] = category_diff
            
            # Calculate similarity score
            results["similarity_score"] = self._calculate_two_file_similarity(
                metadata1, metadata2
            )
            
            # Analyze matches and differences
            results["match_analysis"] = self._analyze_matches_and_differences(
                results["detailed_differences"]
            )
            
            # Generate specific recommendations
            results["recommendations"] = self._generate_two_file_recommendations(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Two-file comparison failed: {e}")
            return {"error": f"Two-file comparison failed: {str(e)}"}
    
    def batch_compare(
        self,
        file_metadata_list: List[Dict[str, Any]],
        group_by: str = "camera_model"
    ) -> Dict[str, Any]:
        """
        Batch comparison with grouping and analysis.
        
        Args:
            file_metadata_list: List of metadata dictionaries
            group_by: Field to group by ("camera_model", "software", "date", etc.)
            
        Returns:
            Batch comparison results with grouping
        """
        try:
            results = {
                "batch_info": {
                    "timestamp": datetime.now().isoformat(),
                    "total_files": len(file_metadata_list),
                    "group_by": group_by
                },
                "groups": {},
                "cross_group_analysis": {},
                "outliers": [],
                "patterns": {},
                "summary": {}
            }
            
            # Group files by specified criteria
            groups = self._group_files(file_metadata_list, group_by)
            
            # Analyze each group
            for group_name, group_files in groups.items():
                if len(group_files) > 1:
                    group_comparison = self.compare_files(group_files, "summary")
                    results["groups"][group_name] = {
                        "file_count": len(group_files),
                        "comparison": group_comparison
                    }
            
            # Cross-group analysis
            results["cross_group_analysis"] = self._analyze_cross_groups(groups)
            
            # Identify outliers
            results["outliers"] = self._identify_outliers(file_metadata_list)
            
            # Pattern detection
            results["patterns"] = self._detect_patterns(file_metadata_list)
            
            # Generate summary
            results["summary"] = self._generate_batch_summary(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch comparison failed: {e}")
            return {"error": f"Batch comparison failed: {str(e)}"}
    
    def _extract_file_summary(self, metadata: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Extract key information for file summary."""
        try:
            summary = {
                "file_index": index,
                "filename": "Unknown",
                "file_type": "Unknown",
                "file_size": "Unknown",
                "camera_make": None,
                "camera_model": None,
                "software": None,
                "timestamp": None,
                "gps_available": False,
                "total_fields": 0
            }
            
            # Extract basic file info
            if "file" in metadata:
                file_info = metadata["file"]
                summary["filename"] = file_info.get("name", "Unknown")
                summary["file_type"] = file_info.get("extension", "Unknown")
            
            if "filesystem" in metadata:
                fs_info = metadata["filesystem"]
                summary["file_size"] = fs_info.get("size_human", "Unknown")
            
            # Extract camera info
            if "exif" in metadata and metadata["exif"]:
                exif = metadata["exif"]
                summary["camera_make"] = exif.get("Make")
                summary["camera_model"] = exif.get("Model")
                summary["software"] = exif.get("Software")
                summary["timestamp"] = exif.get("DateTime") or exif.get("DateTimeOriginal")
            
            # Check GPS availability
            if "gps" in metadata and metadata["gps"]:
                summary["gps_available"] = True
            
            # Count total fields
            summary["total_fields"] = self._count_metadata_fields(metadata)
            
            return summary
            
        except Exception as e:
            logger.warning(f"Failed to extract file summary: {e}")
            return {"file_index": index, "error": str(e)}
    
    def _compare_category(
        self,
        file_metadata_list: List[Dict[str, Any]],
        category: str,
        mode: str
    ) -> Dict[str, Any]:
        """Compare a specific category across all files."""
        try:
            category_data = []
            
            # Extract category data from each file
            for metadata in file_metadata_list:
                cat_data = self._extract_category_data(metadata, category)
                category_data.append(cat_data)
            
            if not any(category_data):  # No data in this category
                return None
            
            comparison = {
                "category": category,
                "files_with_data": sum(1 for data in category_data if data),
                "common_fields": [],
                "unique_fields": {},
                "field_differences": {},
                "consistency_score": 0.0
            }
            
            # Find common and unique fields
            all_fields = set()
            field_presence = {}
            
            for i, data in enumerate(category_data):
                if data:
                    fields = set(data.keys())
                    all_fields.update(fields)
                    
                    for field in fields:
                        if field not in field_presence:
                            field_presence[field] = []
                        field_presence[field].append(i)
            
            # Categorize fields
            total_files = len(file_metadata_list)
            for field, present_in_files in field_presence.items():
                if len(present_in_files) == total_files:
                    comparison["common_fields"].append(field)
                else:
                    comparison["unique_fields"][field] = present_in_files
            
            # Compare field values for common fields
            for field in comparison["common_fields"]:
                field_values = []
                for data in category_data:
                    if data and field in data:
                        field_values.append(data[field])
                    else:
                        field_values.append(None)
                
                field_comparison = self._compare_field_values(field, field_values)
                comparison["field_differences"][field] = field_comparison
            
            # Calculate consistency score
            comparison["consistency_score"] = self._calculate_category_consistency(comparison)
            
            return comparison
            
        except Exception as e:
            logger.warning(f"Category comparison failed for {category}: {e}")
            return None
    
    def _extract_category_data(self, metadata: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Extract data for a specific category from metadata."""
        category_mapping = {
            "file_info": ["file", "filesystem"],
            "exif_data": ["exif"],
            "image_properties": ["image"],
            "gps_data": ["gps"],
            "timestamps": ["exif", "filesystem"],  # Special handling
            "camera_settings": ["exif"],  # Filtered EXIF
            "software_info": ["exif"],  # Software-related fields
            "hashes": ["hashes"],
            "forensic_data": ["forensic"]
        }
        
        try:
            if category == "timestamps":
                return self._extract_timestamp_data(metadata)
            elif category == "camera_settings":
                return self._extract_camera_settings(metadata)
            elif category == "software_info":
                return self._extract_software_info(metadata)
            else:
                # Standard category extraction
                sections = category_mapping.get(category, [])
                extracted_data = {}
                
                for section in sections:
                    if section in metadata and metadata[section]:
                        if isinstance(metadata[section], dict):
                            extracted_data.update(metadata[section])
                        else:
                            extracted_data[section] = metadata[section]
                
                return extracted_data
                
        except Exception as e:
            logger.warning(f"Failed to extract {category} data: {e}")
            return {}
    
    def _extract_timestamp_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all timestamp-related data."""
        timestamps = {}
        
        # EXIF timestamps
        if "exif" in metadata and metadata["exif"]:
            exif = metadata["exif"]
            timestamp_fields = [
                "DateTime", "DateTimeOriginal", "DateTimeDigitized",
                "CreateDate", "ModifyDate"
            ]
            for field in timestamp_fields:
                if field in exif:
                    timestamps[f"exif_{field}"] = exif[field]
        
        # Filesystem timestamps
        if "filesystem" in metadata and metadata["filesystem"]:
            fs = metadata["filesystem"]
            fs_timestamp_fields = ["created", "modified", "accessed"]
            for field in fs_timestamp_fields:
                if field in fs:
                    timestamps[f"fs_{field}"] = fs[field]
        
        return timestamps
    
    def _extract_camera_settings(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract camera-specific settings from EXIF."""
        settings = {}
        
        if "exif" in metadata and metadata["exif"]:
            exif = metadata["exif"]
            camera_fields = [
                "Make", "Model", "LensModel", "FocalLength", "FNumber",
                "ExposureTime", "ISO", "Flash", "WhiteBalance", "ExposureMode",
                "MeteringMode", "SceneCaptureType", "Saturation", "Sharpness",
                "Contrast"
            ]
            
            for field in camera_fields:
                if field in exif:
                    settings[field] = exif[field]
        
        return settings
    
    def _extract_software_info(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract software-related information."""
        software_info = {}
        
        if "exif" in metadata and metadata["exif"]:
            exif = metadata["exif"]
            software_fields = [
                "Software", "ProcessingSoftware", "HostComputer",
                "ExifVersion", "FlashPixVersion", "ColorSpace"
            ]
            
            for field in software_fields:
                if field in exif:
                    software_info[field] = exif[field]
        
        return software_info
    
    def _compare_field_values(self, field_name: str, values: List[Any]) -> Dict[str, Any]:
        """Compare values of a specific field across files."""
        try:
            comparison = {
                "field_name": field_name,
                "total_files": len(values),
                "non_null_values": sum(1 for v in values if v is not None),
                "unique_values": [],
                "all_same": False,
                "differences": [],
                "similarity_score": 0.0
            }
            
            # Filter out None values for analysis
            non_null_values = [v for v in values if v is not None]
            
            if not non_null_values:
                comparison["note"] = "No non-null values found"
                return comparison
            
            # Get unique values
            unique_values = list(set(str(v) for v in non_null_values))
            comparison["unique_values"] = unique_values
            
            # Check if all values are the same
            comparison["all_same"] = len(unique_values) == 1
            
            if not comparison["all_same"]:
                # Generate differences
                for i, value in enumerate(values):
                    if value is not None:
                        comparison["differences"].append({
                            "file_index": i,
                            "value": value
                        })
                
                # Calculate similarity score for string values
                if all(isinstance(v, str) for v in non_null_values):
                    comparison["similarity_score"] = self._calculate_string_similarity(non_null_values)
                else:
                    # For non-string values, similarity is based on uniqueness
                    comparison["similarity_score"] = 1.0 / len(unique_values)
            else:
                comparison["similarity_score"] = 1.0
            
            return comparison
            
        except Exception as e:
            logger.warning(f"Field comparison failed for {field_name}: {e}")
            return {"field_name": field_name, "error": str(e)}
    
    def _calculate_string_similarity(self, strings: List[str]) -> float:
        """Calculate average similarity between strings."""
        if len(strings) < 2:
            return 1.0
        
        try:
            similarities = []
            
            for i in range(len(strings)):
                for j in range(i + 1, len(strings)):
                    # Use difflib for string similarity
                    similarity = difflib.SequenceMatcher(None, strings[i], strings[j]).ratio()
                    similarities.append(similarity)
            
            return sum(similarities) / len(similarities) if similarities else 0.0
            
        except Exception as e:
            return 0.0
    
    def _calculate_category_consistency(self, comparison: Dict[str, Any]) -> float:
        """Calculate consistency score for a category."""
        try:
            if not comparison["field_differences"]:
                return 1.0
            
            field_scores = []
            for field_data in comparison["field_differences"].values():
                if "similarity_score" in field_data:
                    field_scores.append(field_data["similarity_score"])
            
            return sum(field_scores) / len(field_scores) if field_scores else 0.0
            
        except Exception as e:
            return 0.0
    
    def _calculate_similarity(self, file_metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall similarity between files."""
        try:
            similarity_analysis = {
                "overall_similarity": 0.0,
                "category_similarities": {},
                "pairwise_similarities": [],
                "most_similar_pair": None,
                "least_similar_pair": None
            }
            
            # Calculate pairwise similarities
            similarities = []
            
            for i in range(len(file_metadata_list)):
                for j in range(i + 1, len(file_metadata_list)):
                    pair_similarity = self._calculate_two_file_similarity(
                        file_metadata_list[i], file_metadata_list[j]
                    )
                    
                    similarity_data = {
                        "file1_index": i,
                        "file2_index": j,
                        "similarity_score": pair_similarity
                    }
                    
                    similarities.append(similarity_data)
            
            similarity_analysis["pairwise_similarities"] = similarities
            
            if similarities:
                # Overall similarity is average of all pairs
                similarity_analysis["overall_similarity"] = sum(
                    s["similarity_score"] for s in similarities
                ) / len(similarities)
                
                # Find most and least similar pairs
                similarities_sorted = sorted(similarities, key=lambda x: x["similarity_score"])
                similarity_analysis["least_similar_pair"] = similarities_sorted[0]
                similarity_analysis["most_similar_pair"] = similarities_sorted[-1]
            
            return similarity_analysis
            
        except Exception as e:
            logger.warning(f"Similarity calculation failed: {e}")
            return {"error": str(e)}
    
    def _calculate_two_file_similarity(
        self,
        metadata1: Dict[str, Any],
        metadata2: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between two files."""
        try:
            category_scores = []
            
            for category in self.comparison_categories:
                data1 = self._extract_category_data(metadata1, category)
                data2 = self._extract_category_data(metadata2, category)
                
                if not data1 and not data2:
                    continue  # Skip empty categories
                
                if not data1 or not data2:
                    category_scores.append(0.0)  # One file missing data
                    continue
                
                # Compare fields in this category
                all_fields = set(data1.keys()) | set(data2.keys())
                field_matches = 0
                field_similarities = []
                
                for field in all_fields:
                    val1 = data1.get(field)
                    val2 = data2.get(field)
                    
                    if val1 is None and val2 is None:
                        field_similarities.append(1.0)
                    elif val1 is None or val2 is None:
                        field_similarities.append(0.0)
                    elif val1 == val2:
                        field_similarities.append(1.0)
                    elif isinstance(val1, str) and isinstance(val2, str):
                        # String similarity
                        similarity = difflib.SequenceMatcher(None, val1, val2).ratio()
                        field_similarities.append(similarity)
                    else:
                        field_similarities.append(0.0)
                
                if field_similarities:
                    category_score = sum(field_similarities) / len(field_similarities)
                    category_scores.append(category_score)
            
            return sum(category_scores) / len(category_scores) if category_scores else 0.0
            
        except Exception as e:
            logger.warning(f"Two-file similarity calculation failed: {e}")
            return 0.0
    
    def _detailed_category_comparison(
        self,
        metadata1: Dict[str, Any],
        metadata2: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Detailed comparison of a category between two files."""
        try:
            data1 = self._extract_category_data(metadata1, category)
            data2 = self._extract_category_data(metadata2, category)
            
            comparison = {
                "category": category,
                "file1_fields": len(data1),
                "file2_fields": len(data2),
                "common_fields": [],
                "file1_only": [],
                "file2_only": [],
                "different_values": [],
                "identical_values": [],
                "similarity_score": 0.0
            }
            
            all_fields = set(data1.keys()) | set(data2.keys())
            
            for field in all_fields:
                val1 = data1.get(field)
                val2 = data2.get(field)
                
                if val1 is not None and val2 is not None:
                    comparison["common_fields"].append(field)
                    
                    if val1 == val2:
                        comparison["identical_values"].append({
                            "field": field,
                            "value": val1
                        })
                    else:
                        comparison["different_values"].append({
                            "field": field,
                            "file1_value": val1,
                            "file2_value": val2,
                            "similarity": self._calculate_value_similarity(val1, val2)
                        })
                elif val1 is not None:
                    comparison["file1_only"].append({
                        "field": field,
                        "value": val1
                    })
                elif val2 is not None:
                    comparison["file2_only"].append({
                        "field": field,
                        "value": val2
                    })
            
            # Calculate category similarity
            if comparison["common_fields"]:
                identical_count = len(comparison["identical_values"])
                total_common = len(comparison["common_fields"])
                
                # Base similarity on identical fields
                base_similarity = identical_count / total_common
                
                # Adjust for different values with partial similarity
                if comparison["different_values"]:
                    partial_similarities = [
                        diff["similarity"] for diff in comparison["different_values"]
                        if "similarity" in diff
                    ]
                    if partial_similarities:
                        avg_partial = sum(partial_similarities) / len(partial_similarities)
                        different_count = len(comparison["different_values"])
                        weighted_partial = (different_count / total_common) * avg_partial
                        base_similarity += weighted_partial
                
                comparison["similarity_score"] = min(base_similarity, 1.0)
            else:
                comparison["similarity_score"] = 0.0
            
            return comparison
            
        except Exception as e:
            logger.warning(f"Detailed category comparison failed for {category}: {e}")
            return {"category": category, "error": str(e)}
    
    def _calculate_value_similarity(self, val1: Any, val2: Any) -> float:
        """Calculate similarity between two values."""
        try:
            if val1 == val2:
                return 1.0
            
            if isinstance(val1, str) and isinstance(val2, str):
                return difflib.SequenceMatcher(None, val1, val2).ratio()
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric similarity based on relative difference
                max_val = max(abs(val1), abs(val2))
                if max_val == 0:
                    return 1.0
                diff = abs(val1 - val2)
                return max(0.0, 1.0 - (diff / max_val))
            
            return 0.0
            
        except Exception as e:
            return 0.0
    
    def _count_metadata_fields(self, metadata: Dict[str, Any]) -> int:
        """Count total number of metadata fields."""
        try:
            count = 0
            
            def count_recursive(obj):
                nonlocal count
                if isinstance(obj, dict):
                    count += len(obj)
                    for value in obj.values():
                        if isinstance(value, dict):
                            count_recursive(value)
                
            count_recursive(metadata)
            return count
            
        except Exception as e:
            return 0
    
    def _generate_differences_summary(self, field_comparisons: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of differences found."""
        try:
            summary = {
                "total_categories": len(field_comparisons),
                "categories_with_differences": 0,
                "most_different_category": None,
                "most_consistent_category": None,
                "key_differences": [],
                "consistency_scores": {}
            }
            
            category_scores = {}
            
            for category, comparison in field_comparisons.items():
                consistency_score = comparison.get("consistency_score", 0.0)
                category_scores[category] = consistency_score
                
                if consistency_score < 1.0:
                    summary["categories_with_differences"] += 1
                
                # Collect key differences
                if "field_differences" in comparison:
                    for field, field_data in comparison["field_differences"].items():
                        if not field_data.get("all_same", True):
                            summary["key_differences"].append({
                                "category": category,
                                "field": field,
                                "unique_values": field_data.get("unique_values", []),
                                "similarity": field_data.get("similarity_score", 0.0)
                            })
            
            summary["consistency_scores"] = category_scores
            
            if category_scores:
                # Find most and least consistent categories
                sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])
                summary["most_different_category"] = sorted_categories[0][0]
                summary["most_consistent_category"] = sorted_categories[-1][0]
            
            return summary
            
        except Exception as e:
            logger.warning(f"Differences summary generation failed: {e}")
            return {"error": str(e)}
    
    def _analyze_matches_and_differences(self, detailed_differences: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze matches and differences for two-file comparison."""
        try:
            analysis = {
                "total_categories": len(detailed_differences),
                "perfect_matches": [],
                "partial_matches": [],
                "significant_differences": [],
                "unique_to_file1": [],
                "unique_to_file2": [],
                "overall_match_score": 0.0
            }
            
            category_scores = []
            
            for category, diff_data in detailed_differences.items():
                similarity = diff_data.get("similarity_score", 0.0)
                category_scores.append(similarity)
                
                if similarity >= 0.95:
                    analysis["perfect_matches"].append(category)
                elif similarity >= 0.7:
                    analysis["partial_matches"].append(category)
                else:
                    analysis["significant_differences"].append(category)
                
                # Collect unique fields
                file1_only = diff_data.get("file1_only", [])
                file2_only = diff_data.get("file2_only", [])
                
                for item in file1_only:
                    analysis["unique_to_file1"].append({
                        "category": category,
                        "field": item["field"],
                        "value": item["value"]
                    })
                
                for item in file2_only:
                    analysis["unique_to_file2"].append({
                        "category": category,
                        "field": item["field"],
                        "value": item["value"]
                    })
            
            # Calculate overall match score
            if category_scores:
                analysis["overall_match_score"] = sum(category_scores) / len(category_scores)
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Match analysis failed: {e}")
            return {"error": str(e)}
    
    def _group_files(self, file_metadata_list: List[Dict[str, Any]], group_by: str) -> Dict[str, List[Dict[str, Any]]]:
        """Group files by specified criteria."""
        try:
            groups = {}
            
            for metadata in file_metadata_list:
                group_key = self._extract_grouping_key(metadata, group_by)
                
                if group_key not in groups:
                    groups[group_key] = []
                groups[group_key].append(metadata)
            
            return groups
            
        except Exception as e:
            logger.warning(f"File grouping failed: {e}")
            return {"ungrouped": file_metadata_list}
    
    def _extract_grouping_key(self, metadata: Dict[str, Any], group_by: str) -> str:
        """Extract grouping key from metadata."""
        try:
            if group_by == "camera_model":
                if "exif" in metadata and metadata["exif"]:
                    make = metadata["exif"].get("Make", "Unknown")
                    model = metadata["exif"].get("Model", "Unknown")
                    return f"{make} {model}".strip()
                return "Unknown Camera"
            
            elif group_by == "software":
                if "exif" in metadata and metadata["exif"]:
                    software = metadata["exif"].get("Software", "Unknown")
                    return software
                return "Unknown Software"
            
            elif group_by == "date":
                if "exif" in metadata and metadata["exif"]:
                    date_time = metadata["exif"].get("DateTime") or metadata["exif"].get("DateTimeOriginal")
                    if date_time:
                        # Extract date part (YYYY:MM:DD)
                        return date_time.split(" ")[0] if " " in date_time else date_time[:10]
                return "Unknown Date"
            
            elif group_by == "file_type":
                if "file" in metadata:
                    return metadata["file"].get("extension", "Unknown").upper()
                return "Unknown Type"
            
            else:
                return "Default Group"
                
        except Exception as e:
            return "Error Group"
    
    def _analyze_cross_groups(self, groups: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze relationships between different groups."""
        try:
            analysis = {
                "total_groups": len(groups),
                "group_sizes": {},
                "cross_similarities": {},
                "group_characteristics": {}
            }
            
            # Analyze group sizes
            for group_name, group_files in groups.items():
                analysis["group_sizes"][group_name] = len(group_files)
            
            # Calculate cross-group similarities
            group_names = list(groups.keys())
            for i in range(len(group_names)):
                for j in range(i + 1, len(group_names)):
                    group1_name = group_names[i]
                    group2_name = group_names[j]
                    
                    # Sample files from each group for comparison
                    sample1 = groups[group1_name][:3]  # Max 3 files per group
                    sample2 = groups[group2_name][:3]
                    
                    similarities = []
                    for file1 in sample1:
                        for file2 in sample2:
                            sim = self._calculate_two_file_similarity(file1, file2)
                            similarities.append(sim)
                    
                    if similarities:
                        avg_similarity = sum(similarities) / len(similarities)
                        analysis["cross_similarities"][f"{group1_name} vs {group2_name}"] = avg_similarity
            
            # Analyze group characteristics
            for group_name, group_files in groups.items():
                if len(group_files) > 1:
                    group_comparison = self.compare_files(group_files, "summary")
                    analysis["group_characteristics"][group_name] = {
                        "internal_consistency": group_comparison.get("similarity_analysis", {}).get("overall_similarity", 0.0),
                        "common_features": self._extract_group_features(group_files)
                    }
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Cross-group analysis failed: {e}")
            return {"error": str(e)}
    
    def _extract_group_features(self, group_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract common features within a group."""
        try:
            features = {
                "common_camera": None,
                "common_software": None,
                "date_range": None,
                "common_settings": []
            }
            
            # Find common camera
            cameras = set()
            for metadata in group_files:
                if "exif" in metadata and metadata["exif"]:
                    make = metadata["exif"].get("Make", "")
                    model = metadata["exif"].get("Model", "")
                    if make or model:
                        cameras.add(f"{make} {model}".strip())
            
            if len(cameras) == 1:
                features["common_camera"] = list(cameras)[0]
            
            # Find common software
            software_set = set()
            for metadata in group_files:
                if "exif" in metadata and metadata["exif"]:
                    software = metadata["exif"].get("Software")
                    if software:
                        software_set.add(software)
            
            if len(software_set) == 1:
                features["common_software"] = list(software_set)[0]
            
            # Find date range
            dates = []
            for metadata in group_files:
                if "exif" in metadata and metadata["exif"]:
                    date_time = metadata["exif"].get("DateTime") or metadata["exif"].get("DateTimeOriginal")
                    if date_time:
                        dates.append(date_time)
            
            if dates:
                dates.sort()
                if len(dates) == 1:
                    features["date_range"] = dates[0]
                else:
                    features["date_range"] = f"{dates[0]} to {dates[-1]}"
            
            return features
            
        except Exception as e:
            return {}
    
    def _identify_outliers(self, file_metadata_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify files that are significantly different from others."""
        try:
            outliers = []
            
            if len(file_metadata_list) < 3:
                return outliers  # Need at least 3 files to identify outliers
            
            # Calculate each file's average similarity to all others
            file_similarities = []
            
            for i, metadata in enumerate(file_metadata_list):
                similarities = []
                
                for j, other_metadata in enumerate(file_metadata_list):
                    if i != j:
                        sim = self._calculate_two_file_similarity(metadata, other_metadata)
                        similarities.append(sim)
                
                avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
                file_similarities.append({
                    "file_index": i,
                    "filename": self._extract_file_summary(metadata, i).get("filename", "Unknown"),
                    "avg_similarity": avg_similarity
                })
            
            # Identify outliers (files with significantly lower similarity)
            if file_similarities:
                similarities_values = [fs["avg_similarity"] for fs in file_similarities]
                mean_similarity = sum(similarities_values) / len(similarities_values)
                
                # Files with similarity more than 1 standard deviation below mean are outliers
                import statistics
                if len(similarities_values) > 1:
                    std_dev = statistics.stdev(similarities_values)
                    threshold = mean_similarity - std_dev
                    
                    for file_sim in file_similarities:
                        if file_sim["avg_similarity"] < threshold:
                            outliers.append({
                                "file_index": file_sim["file_index"],
                                "filename": file_sim["filename"],
                                "avg_similarity": file_sim["avg_similarity"],
                                "deviation_from_mean": mean_similarity - file_sim["avg_similarity"],
                                "reason": "Significantly different from group average"
                            })
            
            return outliers
            
        except Exception as e:
            logger.warning(f"Outlier identification failed: {e}")
            return []
    
    def _detect_patterns(self, file_metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns across the file collection."""
        try:
            patterns = {
                "camera_patterns": {},
                "software_patterns": {},
                "temporal_patterns": {},
                "technical_patterns": {}
            }
            
            # Camera patterns
            camera_counts = {}
            for metadata in file_metadata_list:
                if "exif" in metadata and metadata["exif"]:
                    make = metadata["exif"].get("Make", "Unknown")
                    model = metadata["exif"].get("Model", "Unknown")
                    camera = f"{make} {model}".strip()
                    camera_counts[camera] = camera_counts.get(camera, 0) + 1
            
            patterns["camera_patterns"] = {
                "most_common": max(camera_counts.items(), key=lambda x: x[1]) if camera_counts else None,
                "distribution": camera_counts,
                "unique_cameras": len(camera_counts)
            }
            
            # Software patterns
            software_counts = {}
            for metadata in file_metadata_list:
                if "exif" in metadata and metadata["exif"]:
                    software = metadata["exif"].get("Software", "Unknown")
                    software_counts[software] = software_counts.get(software, 0) + 1
            
            patterns["software_patterns"] = {
                "most_common": max(software_counts.items(), key=lambda x: x[1]) if software_counts else None,
                "distribution": software_counts,
                "unique_software": len(software_counts)
            }
            
            # Temporal patterns
            dates = []
            for metadata in file_metadata_list:
                if "exif" in metadata and metadata["exif"]:
                    date_time = metadata["exif"].get("DateTime") or metadata["exif"].get("DateTimeOriginal")
                    if date_time:
                        dates.append(date_time)
            
            if dates:
                dates.sort()
                patterns["temporal_patterns"] = {
                    "date_range": f"{dates[0]} to {dates[-1]}" if len(dates) > 1 else dates[0],
                    "total_dates": len(dates),
                    "earliest": dates[0],
                    "latest": dates[-1]
                }
            
            return patterns
            
        except Exception as e:
            logger.warning(f"Pattern detection failed: {e}")
            return {}
    
    def _generate_batch_summary(self, batch_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for batch comparison."""
        try:
            summary = {
                "total_files": batch_results["batch_info"]["total_files"],
                "groups_found": len(batch_results["groups"]),
                "outliers_detected": len(batch_results["outliers"]),
                "key_findings": [],
                "recommendations": []
            }
            
            # Key findings
            if batch_results["groups"]:
                largest_group = max(
                    batch_results["groups"].items(),
                    key=lambda x: x[1]["file_count"]
                )
                summary["key_findings"].append(
                    f"Largest group: {largest_group[0]} ({largest_group[1]['file_count']} files)"
                )
            
            if batch_results["outliers"]:
                summary["key_findings"].append(
                    f"Found {len(batch_results['outliers'])} outlier files"
                )
            
            # Recommendations
            if len(batch_results["groups"]) > 1:
                summary["recommendations"].append("Multiple distinct groups detected - consider separate analysis")
            
            if batch_results["outliers"]:
                summary["recommendations"].append("Investigate outlier files for potential issues")
            
            return summary
            
        except Exception as e:
            logger.warning(f"Batch summary generation failed: {e}")
            return {"error": str(e)}
    
    def _generate_comparison_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on comparison results."""
        recommendations = []
        
        try:
            similarity = results.get("similarity_analysis", {}).get("overall_similarity", 0.0)
            
            if similarity > 0.9:
                recommendations.append("Files are highly similar - likely from same source/camera")
                recommendations.append("Consider checking for duplicate or near-duplicate content")
            elif similarity > 0.7:
                recommendations.append("Files show good similarity - possibly related sources")
                recommendations.append("Review differences for potential editing or processing variations")
            elif similarity < 0.3:
                recommendations.append("Files are significantly different - likely from different sources")
                recommendations.append("Investigate for potential authenticity or chain of custody issues")
            
            # Category-specific recommendations
            differences = results.get("differences_summary", {})
            
            if differences.get("most_different_category") == "timestamps":
                recommendations.append("Timestamp inconsistencies detected - verify file creation dates")
            
            if differences.get("most_different_category") == "camera_settings":
                recommendations.append("Camera settings vary significantly - check for different devices")
            
            if differences.get("most_different_category") == "software_info":
                recommendations.append("Software differences found - files may have been processed differently")
            
            return recommendations
            
        except Exception as e:
            logger.warning(f"Recommendation generation failed: {e}")
            return ["Error generating recommendations"]
    
    def _generate_two_file_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations for two-file comparison."""
        recommendations = []
        
        try:
            match_score = results.get("match_analysis", {}).get("overall_match_score", 0.0)
            
            if match_score > 0.95:
                recommendations.append("Files are nearly identical - possible duplicates")
                recommendations.append("Check for exact binary match or minor processing differences")
            elif match_score > 0.8:
                recommendations.append("Files are very similar - likely same source with minor variations")
                recommendations.append("Review specific differences for editing or processing history")
            elif match_score < 0.5:
                recommendations.append("Files are significantly different - different sources likely")
                recommendations.append("Investigate authenticity and provenance separately")
            
            # Specific difference recommendations
            match_analysis = results.get("match_analysis", {})
            
            if match_analysis.get("unique_to_file1"):
                recommendations.append("File 1 contains unique metadata fields - may be more complete")
            
            if match_analysis.get("unique_to_file2"):
                recommendations.append("File 2 contains unique metadata fields - may be more complete")
            
            if "timestamps" in match_analysis.get("significant_differences", []):
                recommendations.append("Timestamp differences require investigation")
            
            return recommendations
            
        except Exception as e:
            logger.warning(f"Two-file recommendation generation failed: {e}")
            return ["Error generating recommendations"]

# Global comparator instance
_comparator = None

def get_metadata_comparator() -> MetadataComparator:
    """Get or create the global metadata comparator instance."""
    global _comparator
    if _comparator is None:
        _comparator = MetadataComparator()
    return _comparator

def compare_metadata_files(
    file_metadata_list: List[Dict[str, Any]],
    comparison_mode: str = "detailed"
) -> Dict[str, Any]:
    """
    Compare metadata from multiple files.
    
    Args:
        file_metadata_list: List of metadata dictionaries
        comparison_mode: "detailed", "summary", or "differences_only"
        
    Returns:
        Comprehensive comparison results
    """
    comparator = get_metadata_comparator()
    return comparator.compare_files(file_metadata_list, comparison_mode)

def compare_two_metadata_files(
    metadata1: Dict[str, Any],
    metadata2: Dict[str, Any],
    focus_areas: List[str] = None
) -> Dict[str, Any]:
    """
    Detailed comparison between exactly two files.
    
    Args:
        metadata1: First file metadata
        metadata2: Second file metadata
        focus_areas: Specific areas to focus on (optional)
        
    Returns:
        Detailed two-file comparison
    """
    comparator = get_metadata_comparator()
    return comparator.compare_two_files(metadata1, metadata2, focus_areas)

def batch_compare_metadata(
    file_metadata_list: List[Dict[str, Any]],
    group_by: str = "camera_model"
) -> Dict[str, Any]:
    """
    Batch comparison with grouping and analysis.
    
    Args:
        file_metadata_list: List of metadata dictionaries
        group_by: Field to group by ("camera_model", "software", "date", etc.)
        
    Returns:
        Batch comparison results with grouping
    """
    comparator = get_metadata_comparator()
    return comparator.batch_compare(file_metadata_list, group_by)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python comparison.py <metadata_file1> <metadata_file2> [metadata_file3] ...")
        sys.exit(1)
    
    # Load metadata files
    metadata_list = []
    for filepath in sys.argv[1:]:
        try:
            with open(filepath, 'r') as f:
                metadata = json.load(f)
                metadata_list.append(metadata)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            sys.exit(1)
    
    print(f"Comparing {len(metadata_list)} metadata files...")
    
    if len(metadata_list) == 2:
        # Two-file detailed comparison
        result = compare_two_metadata_files(metadata_list[0], metadata_list[1])
    else:
        # Multi-file comparison
        result = compare_metadata_files(metadata_list, "detailed")
    
    print(json.dumps(result, indent=2, default=str))