"""CSV logging functionality"""

import csv
import os
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict

from ..config.settings import Settings

logger = logging.getLogger(__name__)


class CSVLogger:
    """Thread-safe CSV logger for paraphraser results"""
    
    _instance: 'CSVLogger' = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize CSV logger"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.file_path = Path(Settings.CSV_LOG_PATH)
            self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure CSV file exists with headers"""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            headers = [
                'Timestamp', 'Mode', 'Model',
                'Input Words', 'Output Words',
                'Similarity', 'Change %',
                'Grammar Issues', 'Punctuation Issues',
                'Logical Flow Score', 'Readability Score'
            ]
            try:
                with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                logger.info(f"Created CSV log file: {self.file_path}")
            except Exception as e:
                logger.error(f"Error creating CSV log file: {str(e)}")
    
    def log_result(
        self,
        input_text: str,
        output_text: str,
        similarity: float,
        stats: Dict,
        quality_metrics: Dict,
        model_name: str,
        mode: str
    ) -> None:
        """
        Append generation statistics and quality metrics to CSV file
        
        Args:
            input_text: Original input text
            output_text: Generated output text
            similarity: Similarity score
            stats: Statistics dictionary from DiffHighlighter
            quality_metrics: Quality metrics dictionary
            model_name: Name of the model used
            mode: Processing mode ("Paraphrase" or "Expand")
        """
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            mode,
            model_name,
            stats.get('total_original', 0),
            stats.get('total_generated', 0),
            round(similarity, 4),
            round(stats.get('percentage_changed', 0), 2),
            quality_metrics.get('grammar_issues', 0),
            quality_metrics.get('punctuation_issues', 0),
            round(quality_metrics.get('logical_flow', 0), 4),
            round(quality_metrics.get('readability_score', 0), 2)
        ]
        
        try:
            with self._lock:
                file_exists = self.file_path.exists()
                with open(
                    self.file_path,
                    'a',
                    newline='',
                    encoding='utf-8'
                ) as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        # Write headers if file doesn't exist
                        headers = [
                            'Timestamp', 'Mode', 'Model',
                            'Input Words', 'Output Words',
                            'Similarity', 'Change %',
                            'Grammar Issues', 'Punctuation Issues',
                            'Logical Flow Score', 'Readability Score'
                        ]
                        writer.writerow(headers)
                    writer.writerow(row)
            logger.debug(f"Logged result to CSV: {self.file_path}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}", exc_info=True)


