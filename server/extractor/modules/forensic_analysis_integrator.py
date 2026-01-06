#!/usr/bin/env python3
"""
Forensic Analysis Integration Module

Automatically integrates forensic analysis results into the main extraction pipeline.
Provides confidence scoring and visualization data structures for forensic analysis.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ForensicAnalysisIntegrator:
    """Integrates forensic analysis results with confidence scoring and visualization."""
    
    def __init__(self):
        self.confidence_weights = {
            'steganography': 0.30,
            'manipulation': 0.40,
            'ai_detection': 0.20,
            'forensic_analysis': 0.10
        }
        
    def integrate_forensic_results(self, 
                                 base_result: Dict[str, Any], 
                                 filepath: str,
                                 tier_config: Any) -> Dict[str, Any]:
        """
        Integrate forensic analysis results into the base extraction result.
        
        Args:
            base_result: The base metadata extraction result
            filepath: Path to the file being analyzed
            tier_config: Tier configuration object
            
        Returns:
            Updated result with integrated forensic analysis
        """
        start_time = time.time()
        
        # Initialize forensic integration section
        forensic_integration = {
            'enabled': True,
            'processing_time_ms': 0,
            'modules_analyzed': [],
            'confidence_scores': {},
            'forensic_score': 100,
            'authenticity_assessment': 'authentic',
            'risk_indicators': [],
            'visualization_data': {}
        }
        
        try:
            # Extract existing forensic results
            existing_forensic = self._extract_existing_forensic_results(base_result)
            
            # Calculate confidence scores for each module
            confidence_scores = self._calculate_confidence_scores(existing_forensic)
            forensic_integration['confidence_scores'] = confidence_scores
            
            # Calculate overall forensic score
            forensic_score = self._calculate_forensic_score(confidence_scores)
            forensic_integration['forensic_score'] = forensic_score
            
            # Determine authenticity assessment
            authenticity = self._determine_authenticity_assessment(forensic_score, confidence_scores)
            forensic_integration['authenticity_assessment'] = authenticity
            
            # Generate risk indicators
            risk_indicators = self._generate_risk_indicators(confidence_scores, existing_forensic)
            forensic_integration['risk_indicators'] = risk_indicators
            
            # Generate visualization data
            visualization_data = self._generate_visualization_data(confidence_scores, forensic_score)
            forensic_integration['visualization_data'] = visualization_data
            
            # Update modules analyzed
            forensic_integration['modules_analyzed'] = list(existing_forensic.keys())
            
            # Add processing time
            processing_time = (time.time() - start_time) * 1000
            forensic_integration['processing_time_ms'] = processing_time
            
            # Integrate results back into base result
            base_result['forensic_analysis_integration'] = forensic_integration
            
            # Update existing forensic sections with confidence scores
            self._update_existing_forensic_sections(base_result, confidence_scores)
            
            logger.info(f"Forensic analysis integration completed for {filepath} - Score: {forensic_score}, Assessment: {authenticity}")
            
        except Exception as e:
            logger.error(f"Error during forensic analysis integration for {filepath}: {e}")
            forensic_integration['error'] = str(e)
            forensic_integration['enabled'] = False
            base_result['forensic_analysis_integration'] = forensic_integration
        
        return base_result
    
    def _extract_existing_forensic_results(self, base_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract existing forensic analysis results from the base result."""
        forensic_results = {}
        
        # Check for existing forensic modules
        forensic_modules = [
            'steganography_analysis',
            'manipulation_detection', 
            'ai_detection',
            'forensic_security',
            'image_forensics',
            'ai_generation'
        ]
        
        for module in forensic_modules:
            if module in base_result and base_result[module]:
                forensic_results[module] = base_result[module]
        
        return forensic_results
    
    def _calculate_confidence_scores(self, forensic_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for each forensic analysis module."""
        confidence_scores = {}
        
        # Steganography analysis confidence
        if 'steganography_analysis' in forensic_results:
            stego_result = forensic_results['steganography_analysis']
            confidence_scores['steganography'] = self._calculate_steganography_confidence(stego_result)
        
        # Manipulation detection confidence
        if 'manipulation_detection' in forensic_results:
            manip_result = forensic_results['manipulation_detection']
            confidence_scores['manipulation'] = self._calculate_manipulation_confidence(manip_result)
        
        # AI detection confidence
        if 'ai_detection' in forensic_results:
            ai_result = forensic_results['ai_detection']
            confidence_scores['ai_detection'] = self._calculate_ai_detection_confidence(ai_result)
        
        # Forensic security confidence
        if 'forensic_security' in forensic_results:
            forensic_result = forensic_results['forensic_security']
            confidence_scores['forensic_analysis'] = self._calculate_forensic_security_confidence(forensic_result)
        
        # Image forensics confidence
        if 'image_forensics' in forensic_results:
            img_forensic_result = forensic_results['image_forensics']
            confidence_scores['image_forensics'] = self._calculate_image_forensics_confidence(img_forensic_result)
        
        # AI generation confidence
        if 'ai_generation' in forensic_results:
            ai_gen_result = forensic_results['ai_generation']
            confidence_scores['ai_generation'] = self._calculate_ai_generation_confidence(ai_gen_result)
        
        return confidence_scores
    
    def _calculate_steganography_confidence(self, stego_result: Dict[str, Any]) -> float:
        """Calculate confidence score for steganography analysis."""
        confidence = 0.0
        
        # Check for suspicious statistical indicators
        if 'statistical_analysis' in stego_result:
            stats = stego_result['statistical_analysis']
            if 'chi_square' in stats:
                # Lower chi-square values indicate less randomness (potential steganography)
                chi_square = stats['chi_square']
                if chi_square < 200:
                    confidence += 0.7
                elif chi_square < 293:
                    confidence += 0.4
                else:
                    confidence += 0.1
            
            if 'lsb_avg_run_length' in stats:
                # Higher LSB run lengths can indicate LSB steganography
                lsb_run_length = stats['lsb_avg_run_length']
                if lsb_run_length > 2.5:
                    confidence += 0.6
                elif lsb_run_length > 2.0:
                    confidence += 0.3
        
        # Check for known steganography tool signatures
        if 'steganography_detection' in stego_result:
            detection = stego_result['steganography_detection']
            if detection.get('has_known_signatures', False):
                confidence += 0.8
            if detection.get('potential_tools'):
                confidence += 0.3 * len(detection['potential_tools'])
        
        # Check recommendations
        if 'recommendations' in stego_result and stego_result['recommendations']:
            for rec in stego_result['recommendations']:
                if 'steganography' in rec.lower():
                    confidence += 0.5
        
        return min(confidence, 1.0)
    
    def _calculate_manipulation_confidence(self, manip_result: Dict[str, Any]) -> float:
        """Calculate confidence score for manipulation detection."""
        confidence = 0.0
        
        # Check for manipulation probability
        if 'manipulation_probability' in manip_result:
            confidence = manip_result['manipulation_probability']
        elif 'manipulation_score' in manip_result:
            confidence = manip_result['manipulation_score']
        
        # Check for specific manipulation indicators
        if 'manipulation_indicators' in manip_result:
            indicators = manip_result['manipulation_indicators']
            if isinstance(indicators, dict):
                # Count positive indicators
                positive_indicators = sum(1 for v in indicators.values() if v is True or v > 0.5)
                confidence += (positive_indicators / max(len(indicators), 1)) * 0.3
        
        return min(confidence, 1.0)
    
    def _calculate_ai_detection_confidence(self, ai_result: Dict[str, Any]) -> float:
        """Calculate confidence score for AI detection."""
        confidence = 0.0
        
        # Check for AI probability
        if 'ai_probability' in ai_result:
            confidence = ai_result['ai_probability']
        elif 'ai_score' in ai_result:
            confidence = ai_result['ai_score']
        elif 'confidence' in ai_result:
            confidence = ai_result['confidence']
        
        return min(confidence, 1.0)
    
    def _calculate_forensic_security_confidence(self, forensic_result: Dict[str, Any]) -> float:
        """Calculate confidence score for forensic security analysis."""
        confidence = 0.0
        
        # Check for suspicious patterns
        if 'security_indicators' in forensic_result:
            security = forensic_result['security_indicators']
            if 'threat_assessment' in security:
                threat = security['threat_assessment']
                if threat.get('risk_level') == 'high':
                    confidence += 0.8
                elif threat.get('risk_level') == 'medium':
                    confidence += 0.4
                elif threat.get('risk_level') == 'low':
                    confidence += 0.1
        
        # Check for file integrity issues
        if 'file_integrity' in forensic_result:
            integrity = forensic_result['file_integrity']
            if 'file_consistency' in integrity:
                consistency = integrity['file_consistency']
                if not consistency.get('size_match', True):
                    confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _calculate_image_forensics_confidence(self, img_forensic_result: Dict[str, Any]) -> float:
        """Calculate confidence score for image forensics analysis."""
        confidence = 0.0
        
        # Check for error level analysis results
        if 'ela_analysis' in img_forensic_result:
            ela = img_forensic_result['ela_analysis']
            if 'compression_inconsistencies' in ela and ela['compression_inconsistencies']:
                confidence += 0.6
            if 'potential_manipulation' in ela and ela['potential_manipulation']:
                confidence += 0.7
        
        # Check for noise analysis
        if 'noise_analysis' in img_forensic_result:
            noise = img_forensic_result['noise_analysis']
            if 'anomalies_detected' in noise and noise['anomalies_detected']:
                confidence += 0.5
        
        return min(confidence, 1.0)
    
    def _calculate_ai_generation_confidence(self, ai_gen_result: Dict[str, Any]) -> float:
        """Calculate confidence score for AI generation detection."""
        confidence = 0.0
        
        # Check for AI generation probability
        if 'ai_generated_probability' in ai_gen_result:
            confidence = ai_gen_result['ai_generated_probability']
        elif 'confidence' in ai_gen_result:
            confidence = ai_gen_result['confidence']
        
        # Check for specific AI tool detection
        if 'detected_tools' in ai_gen_result:
            tools = ai_gen_result['detected_tools']
            if isinstance(tools, list) and len(tools) > 0:
                confidence += 0.2 * len(tools)
        
        return min(confidence, 1.0)
    
    def _calculate_forensic_score(self, confidence_scores: Dict[str, float]) -> float:
        """Calculate overall forensic score based on confidence scores."""
        if not confidence_scores:
            return 100.0
        
        # Weighted average of confidence scores
        total_weight = 0.0
        weighted_sum = 0.0
        
        for module, confidence in confidence_scores.items():
            # Map module names to weights
            if 'steganography' in module:
                weight = self.confidence_weights['steganography']
            elif 'manipulation' in module or 'image_forensics' in module:
                weight = self.confidence_weights['manipulation']
            elif 'ai' in module:
                weight = self.confidence_weights['ai_detection']
            elif 'forensic' in module:
                weight = self.confidence_weights['forensic_analysis']
            else:
                weight = 0.1  # Default weight for unknown modules
            
            total_weight += weight
            weighted_sum += confidence * weight
        
        if total_weight == 0:
            return 100.0
        
        # Convert confidence (suspicion) to forensic score (authenticity)
        average_confidence = weighted_sum / total_weight
        forensic_score = 100.0 - (average_confidence * 100.0)
        
        return max(0.0, min(100.0, forensic_score))
    
    def _determine_authenticity_assessment(self, forensic_score: float, confidence_scores: Dict[str, float]) -> str:
        """Determine authenticity assessment based on forensic score."""
        if forensic_score >= 90:
            return 'authentic'
        elif forensic_score >= 70:
            return 'likely_authentic'
        elif forensic_score >= 50:
            return 'questionable'
        elif forensic_score >= 30:
            return 'likely_manipulated'
        else:
            return 'suspicious'
    
    def _generate_risk_indicators(self, confidence_scores: Dict[str, float], forensic_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate risk indicators based on forensic analysis."""
        risk_indicators = []
        
        for module, confidence in confidence_scores.items():
            if confidence > 0.5:  # Only report significant risks
                risk_level = 'high' if confidence > 0.8 else 'medium' if confidence > 0.6 else 'low'
                
                indicator = {
                    'module': module,
                    'risk_level': risk_level,
                    'confidence': confidence,
                    'description': self._get_risk_description(module, confidence, forensic_results.get(module, {}))
                }
                risk_indicators.append(indicator)
        
        return risk_indicators
    
    def _get_risk_description(self, module: str, confidence: float, result: Dict[str, Any]) -> str:
        """Get a human-readable risk description."""
        if 'steganography' in module:
            if confidence > 0.8:
                return f"High probability of steganography detected ({confidence:.1%} confidence)"
            elif confidence > 0.6:
                return f"Moderate probability of steganography detected ({confidence:.1%} confidence)"
            else:
                return f"Low probability of steganography detected ({confidence:.1%} confidence)"
        
        elif 'manipulation' in module:
            if confidence > 0.8:
                return f"High probability of image manipulation detected ({confidence:.1%} confidence)"
            elif confidence > 0.6:
                return f"Moderate probability of image manipulation detected ({confidence:.1%} confidence)"
            else:
                return f"Low probability of image manipulation detected ({confidence:.1%} confidence)"
        
        elif 'ai' in module:
            if confidence > 0.8:
                return f"High probability of AI-generated content detected ({confidence:.1%} confidence)"
            elif confidence > 0.6:
                return f"Moderate probability of AI-generated content detected ({confidence:.1%} confidence)"
            else:
                return f"Low probability of AI-generated content detected ({confidence:.1%} confidence)"
        
        else:
            return f"Potential issues detected in {module} analysis ({confidence:.1%} confidence)"
    
    def _generate_visualization_data(self, confidence_scores: Dict[str, float], forensic_score: float) -> Dict[str, Any]:
        """Generate data for forensic analysis visualization."""
        visualization_data = {
            'forensic_score_gauge': {
                'score': forensic_score,
                'color': self._get_score_color(forensic_score),
                'label': self._get_score_label(forensic_score)
            },
            'module_breakdown': {},
            'risk_chart': {
                'labels': [],
                'data': [],
                'colors': []
            }
        }
        
        # Module breakdown
        for module, confidence in confidence_scores.items():
            visualization_data['module_breakdown'][module] = {
                'confidence': confidence,
                'color': self._get_score_color(100 - (confidence * 100)),  # Invert for risk
                'label': module.replace('_', ' ').title()
            }
        
        # Risk chart data
        for module, confidence in confidence_scores.items():
            risk_level = confidence * 100  # Convert to percentage
            visualization_data['risk_chart']['labels'].append(module.replace('_', ' ').title())
            visualization_data['risk_chart']['data'].append(risk_level)
            visualization_data['risk_chart']['colors'].append(self._get_score_color(100 - risk_level))
        
        return visualization_data
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on forensic score."""
        if score >= 90:
            return '#28a745'  # Green
        elif score >= 70:
            return '#ffc107'  # Yellow
        elif score >= 50:
            return '#fd7e14'  # Orange
        else:
            return '#dc3545'  # Red
    
    def _get_score_label(self, score: float) -> str:
        """Get label based on forensic score."""
        if score >= 90:
            return 'Authentic'
        elif score >= 70:
            return 'Likely Authentic'
        elif score >= 50:
            return 'Questionable'
        elif score >= 30:
            return 'Likely Manipulated'
        else:
            return 'Suspicious'
    
    def _update_existing_forensic_sections(self, base_result: Dict[str, Any], confidence_scores: Dict[str, float]) -> None:
        """Update existing forensic sections with confidence scores."""
        for module, confidence in confidence_scores.items():
            if module in base_result and isinstance(base_result[module], dict):
                base_result[module]['confidence_score'] = confidence
                base_result[module]['confidence_level'] = self._get_confidence_level(confidence)
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level string."""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.6:
            return 'medium'
        elif confidence >= 0.4:
            return 'low'
        else:
            return 'very_low'


# Global instance
_forensic_integrator = None

def get_forensic_integrator() -> ForensicAnalysisIntegrator:
    """Get the global forensic analysis integrator instance."""
    global _forensic_integrator
    if _forensic_integrator is None:
        _forensic_integrator = ForensicAnalysisIntegrator()
    return _forensic_integrator

def integrate_forensic_analysis(base_result: Dict[str, Any], filepath: str, tier_config: Any) -> Dict[str, Any]:
    """
    Convenience function to integrate forensic analysis results.
    
    Args:
        base_result: The base metadata extraction result
        filepath: Path to the file being analyzed
        tier_config: Tier configuration object
        
    Returns:
        Updated result with integrated forensic analysis
    """
    integrator = get_forensic_integrator()
    return integrator.integrate_forensic_results(base_result, filepath, tier_config)