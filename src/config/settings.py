"""Configuration management using environment variables"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Paths
    CSV_LOG_PATH: str = os.getenv(
        "CSV_LOG_PATH",
        str(Path(__file__).parent.parent.parent / "logs" / "paraphraser_results.csv")
    )
    
    MODEL_CACHE_DIR: Optional[str] = os.getenv("MODEL_CACHE_DIR", None)
    
    UPLOADS_DIR: str = os.getenv(
        "UPLOADS_DIR",
        str(Path(__file__).parent.parent.parent / "data" / "uploads")
    )
    
    RESULTS_DIR: str = os.getenv(
        "RESULTS_DIR",
        str(Path(__file__).parent.parent.parent / "data" / "results")
    )
    
    # Language Tool settings
    LANGUAGE_TOOL_LANG: str = os.getenv("LANGUAGE_TOOL_LANG", "en-US")
    LANGUAGE_TOOL_REMOTE: bool = os.getenv("LANGUAGE_TOOL_REMOTE", "false").lower() == "true"
    
    # Similarity model
    SIMILARITY_MODEL: str = os.getenv(
        "SIMILARITY_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Gradio settings
    GRADIO_SERVER_NAME: str = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    GRADIO_SERVER_PORT: int = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist"""
        # Log directory
        log_path = Path(cls.CSV_LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Uploads directory
        Path(cls.UPLOADS_DIR).mkdir(parents=True, exist_ok=True)
        
        # Results directory
        Path(cls.RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_model_cache_dir(cls) -> Optional[str]:
        """Get model cache directory, creating it if needed"""
        if cls.MODEL_CACHE_DIR:
            cache_path = Path(cls.MODEL_CACHE_DIR)
            cache_path.mkdir(parents=True, exist_ok=True)
            return str(cache_path)
        return None


# Ensure directories exist on import
Settings.ensure_directories()


