"""Markdown structure parsing and preservation utilities"""

import logging
import re
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MarkdownElement:
    """Represents a single element in markdown document"""
    type: str  # 'heading', 'paragraph', 'code', 'list', 'link', 'blockquote', 'hr'
    content: str
    line_number: int
    metadata: Dict = None  # For storing additional info like heading level, list type, etc.
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MarkdownProcessor:
    """Parse and preserve markdown structure during text processing"""
    
    # Regex patterns for markdown elements
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'^```[\s\S]*?^```', re.MULTILINE)
    INLINE_CODE_PATTERN = re.compile(r'`[^`]+`')
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    REFERENCE_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\[([^\]]*)\]')
    LINK_DEFINITION_PATTERN = re.compile(r'^\[([^\]]+)\]:\s*(.+)$', re.MULTILINE)
    ORDERED_LIST_PATTERN = re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
    UNORDERED_LIST_PATTERN = re.compile(r'^[\*\-\+]\s+(.+)$', re.MULTILINE)
    BLOCKQUOTE_PATTERN = re.compile(r'^>\s+(.+)$', re.MULTILINE)
    HR_PATTERN = re.compile(r'^(\*{3,}|-{3,}|_{3,})$', re.MULTILINE)
    
    def __init__(self):
        self.elements: List[MarkdownElement] = []
    
    def parse(self, markdown_text: str) -> List[MarkdownElement]:
        """
        Parse markdown text into structural elements
        
        Args:
            markdown_text: The markdown content to parse
            
        Returns:
            List of MarkdownElement objects
        """
        self.elements = []
        lines = markdown_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for code blocks (multi-line)
            if line.strip().startswith('```'):
                code_block, lines_consumed = self._extract_code_block(lines[i:])
                if code_block:
                    self.elements.append(MarkdownElement(
                        type='code_block',
                        content=code_block,
                        line_number=i
                    ))
                    i += lines_consumed
                    continue
            
            # Check for headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2)
                self.elements.append(MarkdownElement(
                    type='heading',
                    content=line,
                    line_number=i,
                    metadata={'level': level, 'text': content}
                ))
                i += 1
                continue
            
            # Check for horizontal rule
            if re.match(r'^(\*{3,}|-{3,}|_{3,})$', line.strip()):
                self.elements.append(MarkdownElement(
                    type='hr',
                    content=line,
                    line_number=i
                ))
                i += 1
                continue
            
            # Check for link definitions
            link_def_match = re.match(r'^\[([^\]]+)\]:\s*(.+)$', line)
            if link_def_match:
                self.elements.append(MarkdownElement(
                    type='link_definition',
                    content=line,
                    line_number=i
                ))
                i += 1
                continue
            
            # Check for blockquote
            blockquote_match = re.match(r'^>\s+(.+)$', line)
            if blockquote_match:
                self.elements.append(MarkdownElement(
                    type='blockquote',
                    content=line,
                    line_number=i,
                    metadata={'processable': True}  # Can process blockquote content
                ))
                i += 1
                continue
            
            # Check for lists
            ordered_match = re.match(r'^(\d+\.)\s+(.+)$', line)
            unordered_match = re.match(r'^([\*\-\+])\s+(.+)$', line)
            
            if ordered_match:
                self.elements.append(MarkdownElement(
                    type='ordered_list',
                    content=line,
                    line_number=i,
                    metadata={'marker': ordered_match.group(1), 'text': ordered_match.group(2), 'processable': True}
                ))
                i += 1
                continue
            
            if unordered_match:
                self.elements.append(MarkdownElement(
                    type='unordered_list',
                    content=line,
                    line_number=i,
                    metadata={'marker': unordered_match.group(1), 'text': unordered_match.group(2), 'processable': True}
                ))
                i += 1
                continue
            
            # Check for empty lines
            if not line.strip():
                self.elements.append(MarkdownElement(
                    type='empty',
                    content=line,
                    line_number=i
                ))
                i += 1
                continue
            
            # Everything else is a paragraph (processable content)
            self.elements.append(MarkdownElement(
                type='paragraph',
                content=line,
                line_number=i,
                metadata={'processable': True}
            ))
            i += 1
        
        logger.info(f"Parsed {len(self.elements)} markdown elements")
        return self.elements
    
    def _extract_code_block(self, lines: List[str]) -> Tuple[str, int]:
        """Extract a code block starting from current position"""
        code_lines = [lines[0]]
        i = 1
        
        while i < len(lines):
            code_lines.append(lines[i])
            if lines[i].strip().startswith('```'):
                return '\n'.join(code_lines), i + 1
            i += 1
        
        # Unclosed code block, return as is
        return '\n'.join(code_lines), i
    
    def extract_processable_text(self) -> List[Tuple[int, str]]:
        """
        Extract text that should be processed (paragraphs, list content, blockquotes)
        
        Returns:
            List of tuples: (element_index, text_content)
        """
        processable = []
        
        for idx, element in enumerate(self.elements):
            if element.type == 'paragraph':
                # Extract text while preserving inline markdown
                processable.append((idx, element.content))
            
            elif element.type in ['ordered_list', 'unordered_list', 'blockquote']:
                # Extract the text portion of lists and blockquotes
                if element.metadata.get('processable'):
                    text = element.metadata.get('text', element.content)
                    processable.append((idx, text))
        
        logger.info(f"Extracted {len(processable)} processable text elements")
        return processable
    
    def preserve_inline_markdown(self, text: str) -> Tuple[str, List[Tuple[str, str, str]]]:
        """
        Extract and preserve inline markdown elements (links, code)
        
        Strategy: Keep link text but remove URLs, preserve inline code completely
        
        Args:
            text: Text with inline markdown
            
        Returns:
            Tuple of (text_with_preserved_elements, list_of_(original_full, link_text, url))
        """
        preserved = []
        modified_text = text
        
        # First, preserve inline code completely with placeholders
        inline_codes = self.INLINE_CODE_PATTERN.findall(text)
        for i, code in enumerate(inline_codes):
            placeholder = f"INLINECODE{i}PLACEHOLDER"
            preserved.append((code, placeholder, "CODE"))
            modified_text = modified_text.replace(code, placeholder, 1)
        
        # For links: extract URL but keep link text in place
        # This way the AI sees natural text like "Medium to large firms" instead of a placeholder
        links = []
        for match in self.LINK_PATTERN.finditer(modified_text):
            link_text = match.group(1)
            url = match.group(2)
            full_link = match.group(0)
            links.append((full_link, link_text, url))
        
        # Replace [text](url) with just text - the AI will preserve the natural language
        for full_link, link_text, url in links:
            preserved.append((full_link, link_text, url))
            modified_text = modified_text.replace(full_link, link_text, 1)
        
        return modified_text, preserved
    
    def restore_inline_markdown(self, text: str, preserved: List[Tuple[str, str, str]]) -> str:
        """
        Restore preserved inline markdown elements
        
        Args:
            text: Text after AI processing
            preserved: List of (original_full, link_text_or_placeholder, url_or_type) tuples
            
        Returns:
            Text with markdown restored
        """
        restored_text = text
        
        # Process in reverse to avoid position shifts
        for original_full, link_text_or_placeholder, url_or_type in reversed(preserved):
            if url_or_type == "CODE":
                # Restore inline code by replacing placeholder
                restored_text = restored_text.replace(link_text_or_placeholder, original_full)
            else:
                # Restore link by finding the link text and wrapping it
                # The AI might have modified the link text slightly, so we use fuzzy matching
                if link_text_or_placeholder in restored_text:
                    # Exact match - restore the link
                    restored_link = f"[{link_text_or_placeholder}]({url_or_type})"
                    restored_text = restored_text.replace(link_text_or_placeholder, restored_link, 1)
                else:
                    # Link text was modified by AI, log warning but continue
                    logger.warning(f"Link text '{link_text_or_placeholder}' not found in processed text, link may be lost")
        
        return restored_text
    
    def reconstruct(self, processed_texts: Dict[int, str]) -> str:
        """
        Reconstruct markdown with processed text
        
        Args:
            processed_texts: Dictionary mapping element indices to processed text
            
        Returns:
            Reconstructed markdown string
        """
        output_lines = []
        
        for idx, element in enumerate(self.elements):
            if idx in processed_texts:
                # This element was processed
                processed = processed_texts[idx]
                
                if element.type == 'paragraph':
                    output_lines.append(processed)
                
                elif element.type == 'ordered_list':
                    marker = element.metadata.get('marker', '1.')
                    output_lines.append(f"{marker} {processed}")
                
                elif element.type == 'unordered_list':
                    marker = element.metadata.get('marker', '-')
                    output_lines.append(f"{marker} {processed}")
                
                elif element.type == 'blockquote':
                    output_lines.append(f"> {processed}")
            else:
                # Keep original element as is
                output_lines.append(element.content)
        
        result = '\n'.join(output_lines)
        logger.info("Reconstructed markdown document")
        return result
