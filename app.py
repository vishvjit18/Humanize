"""Main application entry point"""

import logging
import sys
from pathlib import Path
import gradio as gr

from src.config.settings import Settings
from src.ui.gradio_interface import create_gradio_interface

# Configure logging
logging.basicConfig(
    level=getattr(logging, Settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        *([logging.FileHandler(Settings.LOG_FILE)] if Settings.LOG_FILE else [])
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    try:
        logger.info("Starting Text Paraphraser & Expander application")
        logger.info(f"Log level: {Settings.LOG_LEVEL}")
        logger.info(f"Device: {'CUDA' if Settings.MODEL_CACHE_DIR else 'CPU (default)'}")
        
        # Create Gradio interface
        demo = create_gradio_interface()
        
        # Launch interface
        logger.info(
            f"Launching Gradio interface on {Settings.GRADIO_SERVER_NAME}:"
            f"{Settings.GRADIO_SERVER_PORT}"
        )
        
        demo.launch(
            server_name=Settings.GRADIO_SERVER_NAME,
            server_port=Settings.GRADIO_SERVER_PORT,
            share=Settings.GRADIO_SHARE,
            theme=gr.themes.Soft()  # Fix deprecation warning
        )
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

