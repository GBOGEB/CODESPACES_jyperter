
"""
PDF Parser
==========

Parser for PDF files using PyMuPDF (fitz).
Extracts text, metadata, and document structure.
"""

from typing import Dict, Any, List
import logging

from .base_parser import BaseParser

logger = logging.getLogger(__name__)

class PDFParser(BaseParser):
    """Parser for PDF files"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.pdf']
        
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse PDF file and extract content
        
        Args:
            file_path: Path to .pdf file
            
        Returns:
            Dictionary with PDF analysis
        """
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(file_path)
            
            # Extract metadata
            metadata = doc.metadata
            
            # Extract text from all pages
            pages_text = []
            total_chars = 0
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                pages_text.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text)
                })
                total_chars += len(text)
            
            # Extract images info
            images_info = self._extract_images_info(doc)
            
            # Extract links
            links = self._extract_links(doc)
            
            # Analyze document structure
            structure = self._analyze_structure(pages_text)
            
            doc.close()
            
            return {
                "page_count": len(doc),
                "total_characters": total_chars,
                "word_count": len(" ".join([p["text"] for p in pages_text]).split()),
                "metadata": metadata,
                "pages": pages_text,
                "images_count": len(images_info),
                "images_info": images_info,
                "links_count": len(links),
                "links": links,
                "structure": structure,
                "document_type": self._identify_document_type(metadata, pages_text)
            }
            
        except ImportError:
            logger.error("PyMuPDF library not installed. Install with: pip install PyMuPDF")
            return {"error": "PyMuPDF library not available"}
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {e}")
            return {"error": str(e)}
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract plain text from PDF file
        
        Args:
            file_path: Path to .pdf file
            
        Returns:
            Plain text content from all pages
        """
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(file_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_content.append(f"=== Page {page_num + 1} ===")
                    text_content.append(text)
            
            doc.close()
            return "\n".join(text_content)
            
        except ImportError:
            return "Error: PyMuPDF library not available"
        except Exception as e:
            logger.error(f"Error extracting text from PDF file {file_path}: {e}")
            return f"Error: {e}"
    
    def _extract_images_info(self, doc) -> List[Dict[str, Any]]:
        """Extract information about images in the PDF"""
        images_info = []
        
        try:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    images_info.append({
                        "page": page_num + 1,
                        "image_index": img_index,
                        "xref": img[0],
                        "smask": img[1],
                        "width": img[2],
                        "height": img[3],
                        "bpc": img[4],
                        "colorspace": img[5],
                        "alt": img[6],
                        "name": img[7],
                        "filter": img[8]
                    })
        except Exception as e:
            logger.debug(f"Could not extract image info: {e}")
        
        return images_info
    
    def _extract_links(self, doc) -> List[Dict[str, Any]]:
        """Extract links from the PDF"""
        links = []
        
        try:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                link_list = page.get_links()
                
                for link in link_list:
                    links.append({
                        "page": page_num + 1,
                        "from": link.get("from"),
                        "to": link.get("to"),
                        "uri": link.get("uri"),
                        "kind": link.get("kind")
                    })
        except Exception as e:
            logger.debug(f"Could not extract links: {e}")
        
        return links
    
    def _analyze_structure(self, pages_text: List[Dict]) -> Dict[str, Any]:
        """Analyze document structure"""
        structure = {
            "has_toc": False,
            "avg_page_length": 0,
            "empty_pages": 0,
            "text_distribution": []
        }
        
        if pages_text:
            total_chars = sum(p["char_count"] for p in pages_text)
            structure["avg_page_length"] = total_chars / len(pages_text)
            
            for page in pages_text:
                if page["char_count"] < 50:  # Likely empty or mostly empty
                    structure["empty_pages"] += 1
                
                structure["text_distribution"].append({
                    "page": page["page_number"],
                    "char_count": page["char_count"],
                    "relative_size": page["char_count"] / total_chars if total_chars > 0 else 0
                })
            
            # Check for table of contents
            first_page_text = pages_text[0]["text"].lower() if pages_text else ""
            if any(phrase in first_page_text for phrase in ["table of contents", "contents", "index"]):
                structure["has_toc"] = True
        
        return structure
    
    def _identify_document_type(self, metadata: Dict, pages_text: List[Dict]) -> str:
        """Identify document type based on metadata and content"""
        # Check metadata first
        title = metadata.get("title", "").lower()
        subject = metadata.get("subject", "").lower()
        
        if any(word in title for word in ["manual", "guide", "handbook"]):
            return "Manual/Guide"
        elif any(word in title for word in ["report", "analysis"]):
            return "Report"
        elif any(word in title for word in ["specification", "spec"]):
            return "Specification"
        
        # Check content
        if pages_text:
            first_page = pages_text[0]["text"].lower()
            
            if any(phrase in first_page for phrase in ["table of contents", "abstract", "executive summary"]):
                return "Formal Document"
            elif "invoice" in first_page or "bill" in first_page:
                return "Invoice/Bill"
            elif any(word in first_page for word in ["contract", "agreement"]):
                return "Legal Document"
        
        return "General PDF"
