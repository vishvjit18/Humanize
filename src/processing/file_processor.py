"""File processing utilities for handling markdown file uploads"""

import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Maximum file size in bytes (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


class FileProcessor:
    """Handle file reading and validation for markdown uploads"""
    
    @staticmethod
    def read_markdown_file(file_path: str) -> Tuple[str, Optional[str]]:
        """
        Read and validate a markdown file
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Tuple of (content, error_message)
            - If successful: (file_content, None)
            - If error: (empty_string, error_message)
        """
        try:
            path = Path(file_path)
            
            # Validate file exists
            if not path.exists():
                return "", f"File not found: {file_path}"
            
            # Validate file extension
            if path.suffix.lower() != '.md':
                return "", f"Invalid file type. Expected .md file, got {path.suffix}"
            
            # Validate file size
            file_size = path.stat().st_size
            if file_size > MAX_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                max_mb = MAX_FILE_SIZE / (1024 * 1024)
                return "", f"File too large: {size_mb:.2f}MB (max: {max_mb}MB)"
            
            if file_size == 0:
                return "", "File is empty"
            
            # Read file content
            content = path.read_text(encoding='utf-8')
            
            logger.info(f"Successfully read markdown file: {path.name} ({file_size} bytes)")
            return content, None
            
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading file: {str(e)}")
            return "", "File encoding error. Please ensure the file is UTF-8 encoded."
        
        except PermissionError:
            logger.error(f"Permission denied reading file: {file_path}")
            return "", "Permission denied. Cannot read the file."
        
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}", exc_info=True)
            return "", f"Error reading file: {str(e)}"

    @staticmethod
    def save_markdown_file(content: str, original_filename: str, directory: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Save markdown content to a file with timestamp
        
        Args:
            content: Markdown content to save
            original_filename: Original name of the file
            directory: Directory to save the file in
            
        Returns:
            Tuple of (saved_file_path, error_message)
        """
        import time
        import re
        try:
            # Create timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Sanitize filename
            filename = Path(original_filename).stem
            filename = re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')
            save_name = f"{timestamp}_{filename}.md"
            
            save_path = Path(directory) / save_name
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            save_path.write_text(content, encoding='utf-8')
            
            logger.info(f"Successfully saved file: {save_path}")
            return str(save_path), None
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}", exc_info=True)
            return None, str(e)
    
    @staticmethod
    def get_file_info(file_path: str) -> str:
        """
        Get formatted file information
        
        Args:
            file_path: Path to the file
            
        Returns:
            Formatted string with file name and size
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return "File not found"
            
            size = path.stat().st_size
            size_kb = size / 1024
            
            if size_kb < 1:
                size_str = f"{size} bytes"
            elif size_kb < 1024:
                size_str = f"{size_kb:.2f} KB"
            else:
                size_mb = size_kb / 1024
                size_str = f"{size_mb:.2f} MB"
            
            return f"📄 **{path.name}** ({size_str})"
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return "Unknown file"
