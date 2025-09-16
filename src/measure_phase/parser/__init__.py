
"""
Universal Artifact Parsers for Heterogeneous Environments
=========================================================

Provides specialized parsers for each supported artifact type:
- VISIO (.vsdx) - Shape and diagram parsing
- WORD (.docx) - Document content extraction  
- ZIP - Archive analysis and content extraction
- MARKDOWN (.md) - Structured text parsing
- PDF - Text and metadata extraction
- POWERPOINT (.pptx) - Slide content parsing
"""

from .visio_parser import VisioParser
from .word_parser import WordParser
from .zip_parser import ZipParser
from .markdown_parser import MarkdownParser
from .pdf_parser import PDFParser
from .powerpoint_parser import PowerPointParser
from .base_parser import BaseParser

__all__ = [
    'BaseParser',
    'VisioParser',
    'WordParser', 
    'ZipParser',
    'MarkdownParser',
    'PDFParser',
    'PowerPointParser'
]
