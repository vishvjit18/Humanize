"""Text processing utilities"""

import re
from typing import List


def chunk_text(text: str, max_sentences: int = 4) -> List[str]:
    """
    Split text into chunks based on number of sentences
    
    Args:
        text: Input text to chunk
        max_sentences: Maximum number of sentences per chunk
        
    Returns:
        List of text chunks
    """
    if not text.strip():
        return []
    
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    chunks = [
        ' '.join(sentences[i:i+max_sentences])
        for i in range(0, len(sentences), max_sentences)
    ]
    return [chunk for chunk in chunks if chunk.strip()]


def estimate_tokens(text: str) -> int:
    """
    Estimate number of tokens in text (approximate: 1 token ≈ 0.75 words)
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    word_count = len(text.split())
    return int(word_count / 0.75)


def calculate_max_length(input_text: str, mode: str, base_max_length: int) -> int:
    """
    Calculate appropriate max_length based on input tokens
    
    Args:
        input_text: Input text
        mode: Processing mode ("Paraphrase" or "Expand")
        base_max_length: Base maximum length from user settings
        
    Returns:
        Calculated max length (capped at 1024)
    """
    input_tokens = estimate_tokens(input_text)
    
    if mode == "Paraphrase":
        # For paraphrasing: output should be 1.2-1.5x input tokens
        calculated_max = int(input_tokens * 1.5) + 50
    else:
        # For expansion: output should be 2-3x input tokens
        calculated_max = int(input_tokens * 3) + 100
    
    # Use the larger of calculated or user-specified max_length
    final_max_length = max(calculated_max, base_max_length)
    
    # Cap at reasonable maximum to avoid memory issues
    return min(final_max_length, 1024)


