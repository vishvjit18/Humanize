"""Similarity calculation using sentence transformers"""

import logging
from sentence_transformers import SentenceTransformer, util

from ..config.settings import Settings

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """Calculates cosine similarity between texts"""
    
    _instance: 'SimilarityCalculator' = None
    _model: SentenceTransformer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize similarity calculator with sentence transformer model"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            if SimilarityCalculator._model is None:
                try:
                    logger.info(f"Loading similarity model: {Settings.SIMILARITY_MODEL}")
                    SimilarityCalculator._model = SentenceTransformer(
                        Settings.SIMILARITY_MODEL,
                        cache_folder=Settings.get_model_cache_dir()
                    )
                    logger.info("Similarity model loaded successfully")
                except Exception as e:
                    logger.error(f"Error loading similarity model: {str(e)}")
                    raise RuntimeError(f"Failed to load similarity model: {str(e)}") from e
    
    def calculate(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            embeddings = SimilarityCalculator._model.encode(
                [text1, text2],
                convert_to_tensor=True
            )
            similarity = util.cos_sim(embeddings[0], embeddings[1])
            return similarity.item()
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def encode(self, texts: list) -> list:
        """
        Encode texts to embeddings
        
        Args:
            texts: List of texts to encode
            
        Returns:
            List of embeddings
        """
        try:
            embeddings = SimilarityCalculator._model.encode(
                texts,
                convert_to_tensor=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding texts: {str(e)}")
            raise RuntimeError(f"Failed to encode texts: {str(e)}") from e


