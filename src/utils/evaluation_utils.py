"""Evaluation utilities for measuring cognitive friendliness, cultural competency, and performance.

This module provides comprehensive evaluation frameworks for:
- Cognitive friendliness assessment (readability, clarity, accessibility)
- Cultural competency evaluation (community expert review, pilot testing)
- Performance monitoring (response time, accuracy, user satisfaction)
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re
import statistics

# Evaluation Dependencies
try:
    import textstat
    from textstat import textstat
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False
    print("⚠️ textstat not available. Install with: pip install textstat")

try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️ NLTK not available. Install with: pip install nltk")

class CognitiveFriendlinessEvaluator:
    """Evaluates cognitive friendliness of AI responses"""
    
    def __init__(self):
        self.readability_metrics = {}
        self.clarity_indicators = {}
        self.accessibility_scores = {}
        
        # Initialize NLTK if available
        if NLTK_AVAILABLE:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            except:
                pass
    
    def evaluate_response(self, response_text: str) -> Dict[str, Any]:
        """Comprehensive evaluation of cognitive friendliness"""
        
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "response_length": len(response_text),
            "readability_scores": {},
            "clarity_indicators": {},
            "accessibility_features": {},
            "overall_score": 0.0,
            "recommendations": []
        }
        
        # Readability analysis
        if READABILITY_AVAILABLE:
            evaluation["readability_scores"] = self._calculate_readability_scores(response_text)
        
        # Clarity indicators
        evaluation["clarity_indicators"] = self._analyze_clarity_indicators(response_text)
        
        # Accessibility features
        evaluation["accessibility_features"] = self._analyze_accessibility_features(response_text)
        
        # Overall score calculation
        evaluation["overall_score"] = self._calculate_overall_score(evaluation)
        
        # Generate recommendations
        evaluation["recommendations"] = self._generate_recommendations(evaluation)
        
        return evaluation
    
    def _calculate_readability_scores(self, text: str) -> Dict[str, float]:
        """Calculate various readability scores"""
        try:
            return {
                "flesch_reading_ease": textstat.flesch_reading_ease(text),
                "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
                "gunning_fog": textstat.gunning_fog(text),
                "smog_index": textstat.smog_index(text),
                "automated_readability_index": textstat.automated_readability_index(text),
                "coleman_liau_index": textstat.coleman_liau_index(text),
                "linsear_write_formula": textstat.linsear_write_formula(text),
                "dale_chall_readability_score": textstat.dale_chall_readability_score(text),
                "difficult_words": textstat.difficult_words(text),
                "lexicon_count": textstat.lexicon_count(text),
                "sentence_count": textstat.sentence_count(text)
            }
        except Exception as e:
            print(f"Error calculating readability scores: {e}")
            return {}
    
    def _analyze_clarity_indicators(self, text: str) -> Dict[str, Any]:
        """Analyze clarity indicators in the text"""
        
        indicators = {
            "sentence_length": {},
            "paragraph_structure": {},
            "bullet_points": 0,
            "numbered_lists": 0,
            "headings": 0,
            "concrete_examples": 0,
            "jargon_count": 0,
            "positive_language_ratio": 0.0
        }
        
        # Analyze sentence structure
        sentences = text.split('.')
        sentence_lengths = [len(s.strip().split()) for s in sentences if s.strip()]
        
        if sentence_lengths:
            indicators["sentence_length"] = {
                "average": statistics.mean(sentence_lengths),
                "median": statistics.median(sentence_lengths),
                "short_sentences": len([l for l in sentence_lengths if l <= 15]),
                "long_sentences": len([l for l in sentence_lengths if l > 25])
            }
        
        # Count structural elements
        indicators["bullet_points"] = text.count('•') + text.count('-') + text.count('*')
        indicators["numbered_lists"] = len(re.findall(r'\d+\.', text))
        indicators["headings"] = len(re.findall(r'\*\*.*?\*\*', text))
        
        # Count concrete examples
        example_patterns = [
            r'for example', r'such as', r'including', r'specifically',
            r'concrete', r'specific', r'detailed'
        ]
        indicators["concrete_examples"] = sum(
            len(re.findall(pattern, text.lower())) for pattern in example_patterns
        )
        
        # Analyze jargon
        jargon_words = [
            'stakeholder', 'leverage', 'synergy', 'paradigm', 'methodology',
            'infrastructure', 'optimization', 'implementation', 'facilitation'
        ]
        indicators["jargon_count"] = sum(
            text.lower().count(word) for word in jargon_words
        )
        
        # Positive language ratio
        positive_words = [
            'help', 'support', 'improve', 'enhance', 'strengthen', 'build',
            'create', 'develop', 'success', 'positive', 'benefit', 'opportunity'
        ]
        total_words = len(text.split())
        positive_count = sum(text.lower().count(word) for word in positive_words)
        indicators["positive_language_ratio"] = positive_count / total_words if total_words > 0 else 0
        
        return indicators
    
    def _analyze_accessibility_features(self, text: str) -> Dict[str, Any]:
        """Analyze accessibility features in the text"""
        
        features = {
            "has_clear_structure": False,
            "has_bullet_points": False,
            "has_headings": False,
            "has_examples": False,
            "has_positive_tone": False,
            "has_simple_language": False,
            "has_concrete_actions": False
        }
        
        # Check for clear structure
        features["has_clear_structure"] = bool(
            re.search(r'\*\*.*?\*\*', text) or 
            re.search(r'\d+\.', text) or 
            text.count('•') > 0
        )
        
        # Check for bullet points
        features["has_bullet_points"] = text.count('•') > 0 or text.count('-') > 0
        
        # Check for headings
        features["has_headings"] = bool(re.search(r'\*\*.*?\*\*', text))
        
        # Check for examples
        features["has_examples"] = bool(
            re.search(r'for example|such as|including|specifically', text.lower())
        )
        
        # Check for positive tone
        positive_indicators = ['help', 'support', 'improve', 'enhance', 'success']
        features["has_positive_tone"] = any(
            indicator in text.lower() for indicator in positive_indicators
        )
        
        # Check for simple language (readability score)
        if READABILITY_AVAILABLE:
            try:
                flesch_score = textstat.flesch_reading_ease(text)
                features["has_simple_language"] = flesch_score >= 60  # Good readability
            except:
                features["has_simple_language"] = len(text.split()) < 200  # Fallback
        
        # Check for concrete actions
        action_words = ['will', 'can', 'should', 'must', 'need to', 'plan to']
        features["has_concrete_actions"] = any(
            action in text.lower() for action in action_words
        )
        
        return features
    
    def _calculate_overall_score(self, evaluation: Dict[str, Any]) -> float:
        """Calculate overall cognitive friendliness score"""
        
        score = 0.0
        max_score = 100.0
        
        # Readability score (30 points)
        if evaluation["readability_scores"]:
            flesch_score = evaluation["readability_scores"].get("flesch_reading_ease", 0)
            if flesch_score >= 80:
                score += 30
            elif flesch_score >= 60:
                score += 20
            elif flesch_score >= 40:
                score += 10
        
        # Clarity indicators (25 points)
        clarity = evaluation["clarity_indicators"]
        if clarity.get("sentence_length", {}).get("average", 0) <= 20:
            score += 10
        if clarity.get("bullet_points", 0) > 0:
            score += 5
        if clarity.get("concrete_examples", 0) > 0:
            score += 5
        if clarity.get("positive_language_ratio", 0) > 0.1:
            score += 5
        
        # Accessibility features (25 points)
        accessibility = evaluation["accessibility_features"]
        feature_count = sum(accessibility.values())
        score += (feature_count / 7) * 25
        
        # Response length (20 points)
        length = evaluation["response_length"]
        if 100 <= length <= 500:
            score += 20
        elif 50 <= length <= 1000:
            score += 15
        elif length > 0:
            score += 10
        
        return min(score, max_score)
    
    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improvement"""
        
        recommendations = []
        
        # Readability recommendations
        if evaluation["readability_scores"]:
            flesch_score = evaluation["readability_scores"].get("flesch_reading_ease", 0)
            if flesch_score < 60:
                recommendations.append("Consider using shorter sentences and simpler vocabulary")
        
        # Clarity recommendations
        clarity = evaluation["clarity_indicators"]
        if clarity.get("sentence_length", {}).get("average", 0) > 20:
            recommendations.append("Break down long sentences into shorter, clearer ones")
        if clarity.get("bullet_points", 0) == 0:
            recommendations.append("Add bullet points or numbered lists for better organization")
        if clarity.get("concrete_examples", 0) == 0:
            recommendations.append("Include specific examples to make concepts clearer")
        
        # Accessibility recommendations
        accessibility = evaluation["accessibility_features"]
        if not accessibility.get("has_clear_structure"):
            recommendations.append("Add clear headings and structure to improve readability")
        if not accessibility.get("has_positive_tone"):
            recommendations.append("Use more positive, encouraging language")
        
        return recommendations

class CulturalCompetencyEvaluator:
    """Evaluates cultural competency of AI responses"""
    
    def __init__(self):
        self.cultural_indicators = self._load_cultural_indicators()
        self.community_expert_feedback = {}
        self.pilot_test_results = {}
    
    def _load_cultural_indicators(self) -> Dict[str, List[str]]:
        """Load cultural competency indicators"""
        return {
            "inclusive_language": [
                "diverse", "inclusive", "respectful", "honor", "celebrate",
                "community", "cultural", "traditional", "heritage", "multicultural"
            ],
            "strength_based": [
                "strength", "resilience", "capability", "expertise", "knowledge",
                "wisdom", "experience", "leadership", "innovation", "creativity"
            ],
            "community_focused": [
                "community", "local", "partnership", "collaboration", "engagement",
                "participation", "voice", "perspective", "input", "consultation"
            ],
            "avoid_stereotypes": [
                "avoid", "respect", "understand", "acknowledge", "recognize",
                "consider", "sensitive", "appropriate", "contextual", "nuanced"
            ],
            "cultural_sensitivity": [
                "cultural", "traditional", "ceremony", "protocol", "custom",
                "practice", "belief", "value", "heritage", "ancestral"
            ]
        }
    
    def evaluate_response(self, response_text: str, community_context: str = None) -> Dict[str, Any]:
        """Evaluate cultural competency of AI response"""
        
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "community_context": community_context,
            "cultural_indicators": {},
            "inclusive_language_score": 0.0,
            "strength_based_score": 0.0,
            "community_focused_score": 0.0,
            "stereotype_avoidance_score": 0.0,
            "cultural_sensitivity_score": 0.0,
            "overall_cultural_score": 0.0,
            "recommendations": []
        }
        
        # Analyze cultural indicators
        for category, indicators in self.cultural_indicators.items():
            count = sum(response_text.lower().count(indicator) for indicator in indicators)
            evaluation["cultural_indicators"][category] = count
        
        # Calculate category scores
        text_length = len(response_text.split())
        if text_length > 0:
            evaluation["inclusive_language_score"] = (
                evaluation["cultural_indicators"]["inclusive_language"] / text_length * 100
            )
            evaluation["strength_based_score"] = (
                evaluation["cultural_indicators"]["strength_based"] / text_length * 100
            )
            evaluation["community_focused_score"] = (
                evaluation["cultural_indicators"]["community_focused"] / text_length * 100
            )
            evaluation["stereotype_avoidance_score"] = (
                evaluation["cultural_indicators"]["avoid_stereotypes"] / text_length * 100
            )
            evaluation["cultural_sensitivity_score"] = (
                evaluation["cultural_indicators"]["cultural_sensitivity"] / text_length * 100
            )
        
        # Calculate overall score
        scores = [
            evaluation["inclusive_language_score"],
            evaluation["strength_based_score"],
            evaluation["community_focused_score"],
            evaluation["stereotype_avoidance_score"],
            evaluation["cultural_sensitivity_score"]
        ]
        evaluation["overall_cultural_score"] = statistics.mean(scores)
        
        # Generate recommendations
        evaluation["recommendations"] = self._generate_cultural_recommendations(evaluation)
        
        return evaluation
    
    def _generate_cultural_recommendations(self, evaluation: Dict[str, Any]) -> List[str]:
        """Generate cultural competency recommendations"""
        
        recommendations = []
        
        if evaluation["inclusive_language_score"] < 0.5:
            recommendations.append("Use more inclusive language that honors diverse communities")
        
        if evaluation["strength_based_score"] < 0.5:
            recommendations.append("Emphasize community strengths and resilience rather than deficits")
        
        if evaluation["community_focused_score"] < 0.5:
            recommendations.append("Include more community voice and local expertise")
        
        if evaluation["stereotype_avoidance_score"] < 0.5:
            recommendations.append("Avoid assumptions and stereotypes about cultural groups")
        
        if evaluation["cultural_sensitivity_score"] < 0.5:
            recommendations.append("Show more respect for traditional knowledge and cultural practices")
        
        return recommendations
    
    def add_expert_feedback(self, response_id: str, expert_feedback: Dict[str, Any]):
        """Add community expert feedback"""
        self.community_expert_feedback[response_id] = {
            "feedback": expert_feedback,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_pilot_test_result(self, response_id: str, test_result: Dict[str, Any]):
        """Add pilot testing results"""
        self.pilot_test_results[response_id] = {
            "test_result": test_result,
            "timestamp": datetime.now().isoformat()
        }

class PerformanceMonitor:
    """Monitors performance metrics for database retrieval and LLM generation"""
    
    def __init__(self):
        self.performance_targets = {
            "database_retrieval_time": 0.5,  # seconds
            "llm_generation_time": 3.0,      # seconds
            "overall_response_time": 4.0,     # seconds
            "accuracy_threshold": 0.8,        # 80%
            "user_satisfaction_target": 4.0   # out of 5
        }
        
        self.performance_history = []
        self.response_times = []
        self.accuracy_scores = []
        self.satisfaction_scores = []
    
    def start_timer(self) -> float:
        """Start performance timer"""
        return time.time()
    
    def end_timer(self, start_time: float) -> float:
        """End performance timer and return duration"""
        return time.time() - start_time
    
    def record_performance(self, operation: str, duration: float, 
                          accuracy: float = None, satisfaction: float = None):
        """Record performance metrics"""
        
        record = {
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "meets_target": False
        }
        
        # Check if meets target
        target = self.performance_targets.get(f"{operation}_time", 5.0)
        record["meets_target"] = duration <= target
        
        # Add accuracy and satisfaction if provided
        if accuracy is not None:
            record["accuracy"] = accuracy
            self.accuracy_scores.append(accuracy)
        
        if satisfaction is not None:
            record["satisfaction"] = satisfaction
            self.satisfaction_scores.append(satisfaction)
        
        self.performance_history.append(record)
        self.response_times.append(duration)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        
        if not self.response_times:
            return {"error": "No performance data available"}
        
        summary = {
            "total_operations": len(self.performance_history),
            "average_response_time": statistics.mean(self.response_times),
            "median_response_time": statistics.median(self.response_times),
            "target_meeting_rate": sum(1 for r in self.performance_history if r["meets_target"]) / len(self.performance_history),
            "performance_targets": self.performance_targets,
            "recent_performance": self.performance_history[-10:] if self.performance_history else []
        }
        
        if self.accuracy_scores:
            summary["average_accuracy"] = statistics.mean(self.accuracy_scores)
        
        if self.satisfaction_scores:
            summary["average_satisfaction"] = statistics.mean(self.satisfaction_scores)
        
        return summary
    
    def get_recommendations(self) -> List[str]:
        """Get performance improvement recommendations"""
        
        recommendations = []
        summary = self.get_performance_summary()
        
        if "average_response_time" in summary:
            avg_time = summary["average_response_time"]
            target = self.performance_targets["overall_response_time"]
            
            if avg_time > target:
                recommendations.append(f"Response time ({avg_time:.2f}s) exceeds target ({target}s)")
                recommendations.append("Consider optimizing database queries and LLM calls")
        
        if "target_meeting_rate" in summary:
            meeting_rate = summary["target_meeting_rate"]
            if meeting_rate < 0.8:
                recommendations.append(f"Only {meeting_rate:.1%} of operations meet performance targets")
                recommendations.append("Review system architecture and resource allocation")
        
        if "average_satisfaction" in summary:
            avg_satisfaction = summary["average_satisfaction"]
            target = self.performance_targets["user_satisfaction_target"]
            
            if avg_satisfaction < target:
                recommendations.append(f"User satisfaction ({avg_satisfaction:.1f}) below target ({target})")
                recommendations.append("Focus on improving response quality and cultural competency")
        
        return recommendations

# Initialize evaluators
cognitive_evaluator = CognitiveFriendlinessEvaluator()
cultural_evaluator = CulturalCompetencyEvaluator()
performance_monitor = PerformanceMonitor() 