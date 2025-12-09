"""Quality metrics calculation (grammar, readability, flow)"""

import logging
import numpy as np
import language_tool_python
import textstat
from typing import Dict

from ..config.settings import Settings
from .similarity import SimilarityCalculator
from .repetition import RepetitionDetector
from sentence_transformers import util

logger = logging.getLogger(__name__)


class QualityMetrics:
    """Calculates quality metrics for text"""
    
    _instance: 'QualityMetrics' = None
    _grammar_tool: language_tool_python.LanguageTool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize quality metrics calculator"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.similarity_calculator = SimilarityCalculator()
            self.repetition_detector = RepetitionDetector()
            
            if QualityMetrics._grammar_tool is None:
                try:
                    logger.info(f"Initializing LanguageTool: {Settings.LANGUAGE_TOOL_LANG}")
                    QualityMetrics._grammar_tool = language_tool_python.LanguageTool(
                        Settings.LANGUAGE_TOOL_LANG,
                        remote_server=None if not Settings.LANGUAGE_TOOL_REMOTE else Settings.LANGUAGE_TOOL_REMOTE
                    )
                    logger.info("LanguageTool initialized successfully")
                except Exception as e:
                    logger.warning(f"Error initializing LanguageTool: {str(e)}")
                    QualityMetrics._grammar_tool = None
    
    def calculate(self, text: str) -> Dict:
        """
        Analyze text for grammar, punctuation, logical flow, and readability
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with quality metrics
        """
        if not text.strip():
            return {
                "grammar_issues": 0,
                "punctuation_issues": 0,
                "logical_flow": 0.0,
                "readability_score": 0.0,
                "logical_flow": 0.0,
                "readability_score": 0.0,
                "readability_label": "N/A",
                "repetition": {}
            }
        
        try:
            # 1. Grammar & Punctuation (using LanguageTool)
            grammar_errors = 0
            punct_errors = 0
            
            if QualityMetrics._grammar_tool is not None:
                try:
                    matches = QualityMetrics._grammar_tool.check(text)
                    punct_errors = len([
                        m for m in matches
                        if 'PUNCTUATION' in m.rule_issue_type
                    ])
                    grammar_errors = len(matches) - punct_errors
                except Exception as e:
                    logger.warning(f"Grammar check warning: {e}")
            else:
                logger.debug("LanguageTool not available, skipping grammar check")
            
            # 2. Logical Flow (Coherence Score)
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if len(sentences) > 1:
                try:
                    embeddings = self.similarity_calculator.encode(sentences)
                    flows = []
                    for i in range(len(embeddings) - 1):
                        sim = util.cos_sim(embeddings[i], embeddings[i+1]).item()
                        flows.append(sim)
                    flow_score = float(np.mean(flows))
                except Exception as e:
                    logger.warning(f"Error calculating logical flow: {e}")
                    flow_score = 1.0
            else:
                flow_score = 1.0
            
            # 3. Readability (Flesch Reading Ease)
            try:
                readability = textstat.flesch_reading_ease(text)
            except Exception as e:
                logger.warning(f"Error calculating readability: {e}")
                readability = 0.0
            
            # Determine Readability Label
            if readability >= 90:
                label = "Very Easy"
            elif readability >= 80:
                label = "Easy"
            elif readability >= 70:
                label = "Fairly Easy"
            elif readability >= 60:
                label = "Standard"
            elif readability >= 50:
                label = "Fairly Difficult"
            elif readability >= 30:
                label = "Difficult"
            else:
                label = "Very Difficult"
            
            # 4. Repetition Analysis
            repetition_metrics = self.repetition_detector.detect(text)
            
            return {
                "grammar_issues": grammar_errors,
                "punctuation_issues": punct_errors,
                "logical_flow": flow_score,
                "readability_score": readability,
                "readability_label": label,
                "repetition": repetition_metrics
            }
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}", exc_info=True)
            return {
                "grammar_issues": 0,
                "punctuation_issues": 0,
                "logical_flow": 0.0,
                "readability_score": 0.0,
                "logical_flow": 0.0,
                "readability_score": 0.0,
                "readability_label": "Error",
                "repetition": {}
            }


