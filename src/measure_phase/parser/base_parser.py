
"""
Base Parser Interface for Artifact Processing
=============================================

Defines the common interface and functionality for all artifact parsers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class BaseParser(ABC):
    """Abstract base class for all artifact parsers"""
    
    def __init__(self):
        self.supported_extensions = []
        self.parser_name = self.__class__.__name__
    
    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse the artifact and extract structured data
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary containing parsed data and metadata
        """
        pass
    
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract plain text content from the artifact
        
        Args:
            file_path: Path to the file
            
        Returns:
            Plain text content
        """
        pass
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file can be processed by this parser
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is valid for this parser
        """
        try:
            from pathlib import Path
            path = Path(file_path)
            return path.exists() and path.suffix.lower() in self.supported_extensions
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {e}")
            return False
    
    def get_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract basic metadata from the file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata
        """
        try:
            from pathlib import Path
            path = Path(file_path)
            
            return {
                "file_path": str(path.absolute()),
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "extension": path.suffix.lower(),
                "modified_time": path.stat().st_mtime,
                "parser_used": self.parser_name
            }
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return {"error": str(e)}
    
    def safe_parse(self, file_path: str) -> Dict[str, Any]:
        """
        Safely parse a file with error handling
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parsed data or error information
        """
        try:
            if not self.validate_file(file_path):
                return {"error": f"File not valid for {self.parser_name}"}
            
            result = self.parse(file_path)
            result.update(self.get_metadata(file_path))
            return result
            
        except Exception as e:
            logger.error(f"Error parsing {file_path} with {self.parser_name}: {e}")
            return {
                "error": str(e),
                "parser": self.parser_name,
                **self.get_metadata(file_path)
            }
