
"""
Markdown Parser (.md)
====================

Parser for Markdown files with structure analysis and metadata extraction.
"""

from typing import Dict, Any, List
import re
import logging

from .base_parser import BaseParser

logger = logging.getLogger(__name__)

class MarkdownParser(BaseParser):
    """Parser for Markdown files"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.md', '.markdown', '.mdown']
        
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse Markdown file and extract structure
        
        Args:
            file_path: Path to .md file
            
        Returns:
            Dictionary with markdown analysis
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter if present
            frontmatter = self._extract_frontmatter(content)
            
            # Remove frontmatter from content for analysis
            if frontmatter:
                content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
            
            # Analyze structure
            headings = self._extract_headings(content)
            links = self._extract_links(content)
            images = self._extract_images(content)
            code_blocks = self._extract_code_blocks(content)
            
            # Count elements
            word_count = len(content.split())
            line_count = len(content.split('\n'))
            
            return {
                "frontmatter": frontmatter,
                "headings": headings,
                "links": links,
                "images": images,
                "code_blocks": code_blocks,
                "word_count": word_count,
                "line_count": line_count,
                "character_count": len(content),
                "document_type": self._identify_document_type(content, headings),
                "structure_score": self._calculate_structure_score(headings, links, images)
            }
            
        except Exception as e:
            logger.error(f"Error parsing Markdown file {file_path}: {e}")
            return {"error": str(e)}
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract plain text from Markdown file
        
        Args:
            file_path: Path to .md file
            
        Returns:
            Plain text content (markdown syntax removed)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove frontmatter
            content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
            
            # Remove markdown syntax
            content = re.sub(r'#{1,6}\s+', '', content)  # Headers
            content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
            content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
            content = re.sub(r'`(.*?)`', r'\1', content)  # Inline code
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)  # Code blocks
            content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # Links
            content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', content)  # Images
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from Markdown file {file_path}: {e}")
            return f"Error: {e}"
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter if present"""
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        
        if frontmatter_match:
            try:
                import yaml
                return yaml.safe_load(frontmatter_match.group(1))
            except ImportError:
                logger.debug("PyYAML not available for frontmatter parsing")
                return {"raw": frontmatter_match.group(1)}
            except Exception as e:
                logger.debug(f"Could not parse frontmatter: {e}")
                return {"raw": frontmatter_match.group(1)}
        
        return {}
    
    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """Extract all headings with levels"""
        headings = []
        
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append({
                "level": level,
                "text": text,
                "anchor": self._create_anchor(text)
            })
        
        return headings
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract all links"""
        links = []
        
        # Markdown links [text](url)
        for match in re.finditer(r'\[([^\]]+)\]\(([^\)]+)\)', content):
            links.append({
                "text": match.group(1),
                "url": match.group(2),
                "type": "markdown"
            })
        
        # Reference links [text][ref]
        for match in re.finditer(r'\[([^\]]+)\]\[([^\]]+)\]', content):
            links.append({
                "text": match.group(1),
                "reference": match.group(2),
                "type": "reference"
            })
        
        return links
    
    def _extract_images(self, content: str) -> List[Dict[str, str]]:
        """Extract all images"""
        images = []
        
        for match in re.finditer(r'!\[([^\]]*)\]\(([^\)]+)\)', content):
            images.append({
                "alt_text": match.group(1),
                "url": match.group(2)
            })
        
        return images
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks"""
        code_blocks = []
        
        # Fenced code blocks
        for match in re.finditer(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL):
            code_blocks.append({
                "language": match.group(1) or "text",
                "code": match.group(2),
                "type": "fenced"
            })
        
        # Indented code blocks
        indented_pattern = r'^(    .+)$'
        indented_blocks = []
        current_block = []
        
        for line in content.split('\n'):
            if re.match(indented_pattern, line):
                current_block.append(line[4:])  # Remove 4-space indent
            else:
                if current_block:
                    indented_blocks.append('\n'.join(current_block))
                    current_block = []
        
        if current_block:
            indented_blocks.append('\n'.join(current_block))
        
        for block in indented_blocks:
            code_blocks.append({
                "language": "text",
                "code": block,
                "type": "indented"
            })
        
        return code_blocks
    
    def _create_anchor(self, text: str) -> str:
        """Create URL anchor from heading text"""
        anchor = text.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def _identify_document_type(self, content: str, headings: List[Dict]) -> str:
        """Identify document type"""
        content_lower = content.lower()
        heading_text = " ".join([h["text"] for h in headings]).lower()
        
        if "readme" in content_lower or any("readme" in h["text"].lower() for h in headings):
            return "README"
        elif any(word in content_lower for word in ["api", "endpoint", "request", "response"]):
            return "API Documentation"
        elif any(word in content_lower for word in ["tutorial", "guide", "how to", "getting started"]):
            return "Tutorial/Guide"
        elif any(word in content_lower for word in ["changelog", "release", "version"]):
            return "Changelog"
        elif "table of contents" in content_lower or "toc" in content_lower:
            return "Table of Contents"
        else:
            return "General Documentation"
    
    def _calculate_structure_score(self, headings: List[Dict], 
                                 links: List[Dict], images: List[Dict]) -> int:
        """Calculate document structure quality score"""
        score = 0
        
        # Points for headings
        if headings:
            score += 20
            # Bonus for hierarchical structure
            levels = [h["level"] for h in headings]
            if len(set(levels)) > 1:
                score += 10
        
        # Points for links
        if links:
            score += min(len(links) * 5, 30)
        
        # Points for images
        if images:
            score += min(len(images) * 3, 15)
        
        return min(score, 100)
