"""Core paraphrasing and expansion logic"""

import logging
import torch
from typing import Tuple, Dict

from ..models.model_manager import ModelManager
from ..models.model_config import PARAPHRASE_MODELS, EXPANSION_MODELS
from .text_utils import chunk_text, estimate_tokens, calculate_max_length
from ..quality.similarity import SimilarityCalculator

logger = logging.getLogger(__name__)


class Paraphraser:
    """Handles text paraphrasing and expansion"""
    
    def __init__(self):
        """Initialize paraphraser with model manager and similarity calculator"""
        self.model_manager = ModelManager()
        self.similarity_calculator = SimilarityCalculator()
    
    def process_text(
        self,
        text: str,
        model_name: str,
        temperature: float,
        top_p: float,
        max_length: int,
        num_beams: int,
        max_sentences: int,
        target_words: int = None,
        mode: str = "Paraphrase"
    ) -> Tuple[str, float]:
        """
        Paraphrase or expand text based on mode
        
        Args:
            text: Input text to process
            model_name: Name of the model to use
            temperature: Generation temperature
            top_p: Top-p sampling parameter
            max_length: Maximum generation length
            num_beams: Number of beams for beam search
            max_sentences: Maximum sentences per chunk
            target_words: Target word count for expansion mode
            mode: Processing mode ("Paraphrase" or "Expand")
            
        Returns:
            Tuple of (processed_text, similarity_score)
        """
        if not text.strip():
            logger.warning("Empty text provided")
            return "Please enter some text to process.", 0.0
        
        try:
            # Select appropriate model based on mode
            if mode == "Paraphrase":
                models_dict = PARAPHRASE_MODELS
                if model_name not in models_dict:
                    model_name = list(models_dict.keys())[0]
                    logger.warning(f"Model not found, using default: {model_name}")
                model_path = models_dict[model_name]
                prefix = "paraphrase: " if "T5" in model_name else ""
            else:  # Expand mode
                models_dict = EXPANSION_MODELS
                if model_name not in models_dict:
                    model_name = list(models_dict.keys())[0]
                    logger.warning(f"Model not found, using default: {model_name}")
                model_path = models_dict[model_name]
                target_words = target_words or 300
                prefix = f"Expand the following text to approximately {target_words} words, adding more details and context: "
            
            # Load model
            model, tokenizer, device = self.model_manager.load_model(model_name, model_path)
            
            # Chunk text based on sentences
            chunks = chunk_text(text, max_sentences=max_sentences)
            
            if not chunks:
                logger.warning("No chunks created from input text")
                return text, 1.0
            
            processed_chunks = []
            
            logger.info(f"Processing {len(chunks)} chunk(s) with {max_sentences} sentences per chunk")
            
            for i, chunk in enumerate(chunks):
                # Calculate dynamic max_length for this chunk
                chunk_max_length = calculate_max_length(chunk, mode, max_length)
                input_tokens = estimate_tokens(chunk)
                
                # Prepare input
                input_text = prefix + chunk + " </s>" if mode == "Paraphrase" else prefix + chunk
                inputs = tokenizer.encode(
                    input_text,
                    return_tensors="pt",
                    max_length=512,
                    truncation=True
                )
                inputs = inputs.to(device)
                
                # Calculate min_length to ensure output isn't too short
                if mode == "Paraphrase":
                    min_length_calc = int(input_tokens * 0.8)
                else:
                    min_length_calc = int(input_tokens * 1.5)
                
                # Generate
                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        max_length=chunk_max_length,
                        min_length=min(min_length_calc, chunk_max_length - 10),
                        num_beams=num_beams,
                        temperature=temperature if temperature > 0 else 1.0,
                        top_p=top_p,
                        top_k=120 if mode == "Paraphrase" else 50,
                        do_sample=temperature > 0,
                        early_stopping=True,
                        no_repeat_ngram_size=3 if mode == "Expand" else 2,
                        length_penalty=1.0 if mode == "Paraphrase" else 1.5,
                        repetition_penalty=1.2,
                    )
                
                # Decode output
                processed_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                processed_chunks.append(processed_text.strip())
                
                output_tokens = estimate_tokens(processed_text)
                logger.debug(
                    f"Chunk {i+1}/{len(chunks)}: "
                    f"Input: {len(chunk.split())} words (~{input_tokens} tokens), "
                    f"Output: {len(processed_text.split())} words (~{output_tokens} tokens), "
                    f"Max length used: {chunk_max_length}"
                )
            
            # Combine chunks with double newline
            final_text = "\n\n".join(processed_chunks)
            
            # Calculate similarity
            similarity_score = self.similarity_calculator.calculate(text, final_text)
            
            logger.info(
                f"Processing complete: {len(text.split())} → {len(final_text.split())} words, "
                f"Similarity: {similarity_score:.4f}"
            )
            
            return final_text, similarity_score
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to process text: {str(e)}") from e


