"""Difference highlighting and statistics calculation"""

import difflib
from typing import Tuple, Dict


class DiffHighlighter:
    """Highlights differences between original and generated text"""
    
    @staticmethod
    def highlight_differences(
        original: str,
        generated: str
    ) -> Tuple[str, str, Dict]:
        """
        Create highlighted HTML versions of both texts showing differences
        
        Args:
            original: Original text
            generated: Generated text
            
        Returns:
            Tuple of (highlighted_original, highlighted_generated, statistics)
        """
        # Split into words for comparison
        original_words = original.split()
        generated_words = generated.split()
        
        # Use difflib to find differences
        diff = difflib.SequenceMatcher(None, original_words, generated_words)
        
        highlighted_original = []
        highlighted_generated = []
        
        changes_count = 0
        additions_count = 0
        deletions_count = 0
        unchanged_count = 0
        word_substitutions = []
        
        for tag, i1, i2, j1, j2 in diff.get_opcodes():
            original_chunk = ' '.join(original_words[i1:i2])
            generated_chunk = ' '.join(generated_words[j1:j2])
            
            if tag == 'equal':
                # Unchanged text
                highlighted_original.append(original_chunk)
                highlighted_generated.append(generated_chunk)
                unchanged_count += (i2 - i1)
            
            elif tag == 'replace':
                # Changed text
                highlighted_original.append(
                    f'<span style="color: #ffcccc; padding: 2px 4px; '
                    f'border-radius: 3px; text-decoration: line-through;">'
                    f'{original_chunk}</span>'
                )
                highlighted_generated.append(
                    f'<span style="color: #ccffcc; padding: 2px 4px; '
                    f'border-radius: 3px; font-weight: 500;">{generated_chunk}</span>'
                )
                changes_count += max(i2 - i1, j2 - j1)
                
                # Track word substitutions (limit to single word changes for clarity)
                if i2 - i1 == 1 and j2 - j1 == 1:
                    word_substitutions.append((original_chunk, generated_chunk))
            
            elif tag == 'delete':
                # Text removed in generated
                highlighted_original.append(
                    f'<span style="color: #ffcccc; padding: 2px 4px; '
                    f'border-radius: 3px; text-decoration: line-through;">'
                    f'{original_chunk}</span>'
                )
                deletions_count += (i2 - i1)
            
            elif tag == 'insert':
                # Text added in generated
                highlighted_generated.append(
                    f'<span style="color: #ccffcc; padding: 2px 4px; '
                    f'border-radius: 3px; font-weight: 500;">{generated_chunk}</span>'
                )
                additions_count += (j2 - j1)
        
        # Join with spaces
        final_original = ' '.join(highlighted_original)
        final_generated = ' '.join(highlighted_generated)
        
        # Calculate statistics
        total_original_words = len(original_words)
        total_generated_words = len(generated_words)
        
        percentage_changed = (
            (changes_count + deletions_count + additions_count) /
            max(total_original_words, 1) * 100
        )
        percentage_unchanged = (
            (unchanged_count / max(total_original_words, 1)) * 100
        )
        
        statistics = {
            'total_original': total_original_words,
            'total_generated': total_generated_words,
            'unchanged': unchanged_count,
            'changed': changes_count,
            'added': additions_count,
            'deleted': deletions_count,
            'percentage_changed': percentage_changed,
            'percentage_unchanged': percentage_unchanged,
            'substitutions': word_substitutions[:10]  # Limit to first 10
        }
        
        return final_original, final_generated, statistics


