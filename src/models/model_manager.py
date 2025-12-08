"""Model loading and caching management"""

import logging
import torch
from typing import Dict, Tuple, Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from ..config.settings import Settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages model loading and caching with singleton pattern"""
    
    _instance: Optional['ModelManager'] = None
    _cache: Dict[str, Tuple[AutoModelForSeq2SeqLM, AutoTokenizer, str]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize model manager"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"ModelManager initialized. Device: {self.device}")
    
    def load_model(
        self,
        model_name: str,
        model_path: str
    ) -> Tuple[AutoModelForSeq2SeqLM, AutoTokenizer, str]:
        """
        Load model and tokenizer with caching
        
        Args:
            model_name: Name identifier for the model
            model_path: HuggingFace model path or local path
            
        Returns:
            Tuple of (model, tokenizer, device)
        """
        if model_name in self._cache:
            logger.debug(f"Using cached model: {model_name}")
            return self._cache[model_name]
        
        try:
            logger.info(f"Loading model: {model_name} from {model_path}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                cache_dir=Settings.get_model_cache_dir()
            )
            
            # Load model
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_path,
                cache_dir=Settings.get_model_cache_dir()
            )
            
            # Move to device
            model = model.to(self.device)
            model.eval()  # Set to evaluation mode
            
            # Cache the model
            self._cache[model_name] = (model, tokenizer, self.device)
            
            logger.info(f"Successfully loaded and cached model: {model_name}")
            return model, tokenizer, self.device
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            raise RuntimeError(f"Failed to load model {model_name}: {str(e)}") from e
    
    def clear_cache(self) -> None:
        """Clear the model cache"""
        self._cache.clear()
        logger.info("Model cache cleared")
    
    def get_cached_models(self) -> list:
        """Get list of cached model names"""
        return list(self._cache.keys())


