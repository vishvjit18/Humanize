"""
Repetition detection module for identifying repetitive words and phrases.
"""

import logging
import re
from collections import Counter
from typing import Dict, List, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)


class RepetitionDetector:
    """Detects repetitive words and phrases in text"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize repetition detector"""
        if not self._initialized:
            self._initialized = True
            self.stemmer = PorterStemmer()
            self._download_nltk_data()
            
            try:
                self.stop_words = set(stopwords.words('english'))
                # Add common conversational fillers/structural words that are okay to repeat
                self.stop_words.update({
                    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                    'is', 'are', 'was', 'were', 'be', 'been', 'being',
                    'it', 'this', 'that', 'these', 'those',
                    'i', 'you', 'he', 'she', 'they', 'we',
                    'will', 'would', 'can', 'could', 'should', 'may', 'might',
                    'have', 'has', 'had', 'do', 'does', 'did',
                    'not', 'no', 'yes'
                })
            except Exception as e:
                logger.warning(f"Error loading stopwords: {e}")
                self.stop_words = set()

    def _download_nltk_data(self):
        """Download necessary NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            logger.warning(f"Error downloading NLTK data: {e}")

    def detect(self, text: str, window_size: int = 50) -> Dict:
        """
        Detect repetitions in text
        
        Args:
            text: Input text
            window_size: Window size for detecting local repetitions
            
        Returns:
            Dictionary containing repetition metrics
        """
        if not text.strip():
            return {
                "top_global_repetitions": [],
                "local_repetition_score": 0.0,
                "total_repetitions_found": 0
            }

        try:
            # Tokenize
            words = word_tokenize(text.lower())
            
            # Filter distinct words for analysis (remove punctuation, numbers)
            content_words = [
                w for w in words 
                if w.isalnum() and not w.isdigit() and w not in self.stop_words
            ]
            
            if not content_words:
                return {
                    "top_global_repetitions": [],
                    "local_repetition_score": 0.0,
                    "total_repetitions_found": 0
                }

            # 1. Global Repetitions (Frequency analysis)
            # Use stems to catch "use", "using", "used" as the same word
            stemmed_words = [self.stemmer.stem(w) for w in content_words]
            counts = Counter(stemmed_words)
            
            # Map stems back to most common original word for display
            stem_to_word = {}
            for w, stem in zip(content_words, stemmed_words):
                if stem not in stem_to_word:
                    stem_to_word[stem] = w
            
            # Filter for words appearing more than expected (e.g., > 2 times in short text)
            # Dynamic threshold: max(3, len(content_words) * 0.05)
            threshold = max(3, int(len(content_words) * 0.05))
            
            global_reps = []
            for stem, count in counts.most_common(5):
                if count >= threshold:
                    global_reps.append({
                        "word": stem_to_word.get(stem, stem),
                        "count": count,
                        "ratio": count / len(content_words)
                    })

            # 2. Local Repetitions (Proximity)
            # Check for same stem appearance within 'window_size' words
            local_rep_count = 0
            
            for i in range(len(stemmed_words)):
                current_word = stemmed_words[i]
                # Look ahead in window
                window_end = min(i + 1 + int(window_size/5), len(stemmed_words)) # Smaller window for adjacent check
                
                for j in range(i + 1, window_end):
                    if stemmed_words[j] == current_word:
                        local_rep_count += 1
            
            # Normalize local repetition score (0.0 to 1.0)
            # Heuristic: > 5 local reps per 100 words is "bad"
            local_rep_score = min(1.0, (local_rep_count * 10) / max(1, len(content_words)))

            return {
                "top_global_repetitions": global_reps,
                "local_repetition_score": local_rep_score,
                "total_repetitions_found": local_rep_count + sum(r['count'] for r in global_reps)
            }

        except Exception as e:
            logger.error(f"Error in repetition detection: {e}", exc_info=True)
            return {
                "top_global_repetitions": [],
                "local_repetition_score": 0.0,
                "total_repetitions_found": 0
            }
