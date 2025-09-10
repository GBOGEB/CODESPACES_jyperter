
"""
Visio Diagram Parser (.vsdx)
============================

Parser for Microsoft Visio files using the vsdx library.
Extracts shapes, text, connections, and diagram metadata.
"""

from typing import Dict, Any, List
import logging

from .base_parser import BaseParser

logger = logging.getLogger(__name__)

class VisioParser(BaseParser):
    """Parser for Visio .vsdx files"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.vsdx']
        
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse Visio file and extract diagram data
        
        Args:
            file_path: Path to .vsdx file
            
        Returns:
            Dictionary with diagram analysis
        """
        try:
            from vsdx import VisioFile
            
            with VisioFile(file_path) as vis:
                pages_data = []
                total_shapes = 0
                all_text = []
                connections = []
                
                for page_idx, page in enumerate(vis.pages):
                    page_info = {
                        "page_index": page_idx,
                        "page_name": getattr(page, 'name', f'Page_{page_idx}'),
                        "shapes": [],
                        "connections": []
                    }
                    
                    # Extract shapes and text
                    for shape in page.shapes:
                        shape_data = self._extract_shape_data(shape)
                        page_info["shapes"].append(shape_data)
                        
                        if shape_data.get("text"):
                            all_text.append(shape_data["text"])
                    
                    # Extract connections if available
                    if hasattr(page, 'connects'):
                        page_info["connections"] = self._extract_connections(page.connects)
                        connections.extend(page_info["connections"])
                    
                    pages_data.append(page_info)
                    total_shapes += len(page_info["shapes"])
                
                return {
                    "total_pages": len(vis.pages),
                    "total_shapes": total_shapes,
                    "total_connections": len(connections),
                    "pages": pages_data,
                    "all_text": all_text,
                    "diagram_type": self._identify_diagram_type(all_text),
                    "complexity_score": self._calculate_complexity(total_shapes, len(connections))
                }
                
        except ImportError:
            logger.error("vsdx library not installed. Install with: pip install vsdx")
            return {"error": "vsdx library not available"}
        except Exception as e:
            logger.error(f"Error parsing Visio file {file_path}: {e}")
            return {"error": str(e)}
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract all text content from Visio file
        
        Args:
            file_path: Path to .vsdx file
            
        Returns:
            Combined text from all shapes
        """
        try:
            from vsdx import VisioFile
            
            text_content = []
            
            with VisioFile(file_path) as vis:
                for page_idx, page in enumerate(vis.pages):
                    text_content.append(f"=== Page {page_idx + 1} ===")
                    
                    for shape in page.shapes:
                        if hasattr(shape, 'text') and shape.text:
                            text_content.append(shape.text.strip())
            
            return "\n".join(text_content)
            
        except ImportError:
            return "Error: vsdx library not available"
        except Exception as e:
            logger.error(f"Error extracting text from Visio file {file_path}: {e}")
            return f"Error: {e}"
    
    def _extract_shape_data(self, shape) -> Dict[str, Any]:
        """Extract data from a single shape"""
        shape_data = {
            "shape_id": getattr(shape, 'ID', 'unknown'),
            "text": getattr(shape, 'text', '').strip() if hasattr(shape, 'text') else '',
            "shape_type": type(shape).__name__
        }
        
        # Try to get additional properties
        try:
            if hasattr(shape, 'x') and hasattr(shape, 'y'):
                shape_data["position"] = {"x": shape.x, "y": shape.y}
            
            if hasattr(shape, 'width') and hasattr(shape, 'height'):
                shape_data["dimensions"] = {"width": shape.width, "height": shape.height}
                
        except Exception as e:
            logger.debug(f"Could not extract shape properties: {e}")
        
        return shape_data
    
    def _extract_connections(self, connects) -> List[Dict[str, Any]]:
        """Extract connection information"""
        connections = []
        
        try:
            for connect in connects:
                connection_data = {
                    "from_shape": getattr(connect, 'from_shape', 'unknown'),
                    "to_shape": getattr(connect, 'to_shape', 'unknown'),
                    "connection_type": type(connect).__name__
                }
                connections.append(connection_data)
        except Exception as e:
            logger.debug(f"Could not extract connections: {e}")
        
        return connections
    
    def _identify_diagram_type(self, all_text: List[str]) -> str:
        """Identify the type of diagram based on text content"""
        text_lower = " ".join(all_text).lower()
        
        # Common diagram type indicators
        if any(word in text_lower for word in ['process', 'workflow', 'step']):
            return "Process/Workflow"
        elif any(word in text_lower for word in ['network', 'server', 'database']):
            return "Network/Infrastructure"
        elif any(word in text_lower for word in ['organization', 'department', 'manager']):
            return "Organizational Chart"
        elif any(word in text_lower for word in ['floor', 'room', 'office']):
            return "Floor Plan"
        else:
            return "General Diagram"
    
    def _calculate_complexity(self, shape_count: int, connection_count: int) -> int:
        """Calculate diagram complexity score"""
        # Simple complexity scoring
        complexity = shape_count + (connection_count * 2)
        
        if complexity < 10:
            return 1  # Simple
        elif complexity < 50:
            return 2  # Medium
        else:
            return 3  # Complex
