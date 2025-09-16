
"""
Artifact Type Classifier for Heterogeneous Environments
=======================================================

Classifies and prioritizes artifacts: VISIO, WORD, ZIP, MARKDOWN, PDF, POWERPOINT
Implements priority-based processing with ZIP files receiving highest priority.
"""

import os
import mimetypes
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ArtifactType(Enum):
    """Supported artifact types with processing priorities"""
    ZIP = ("application/zip", 1, [".zip", ".zipx"])
    MARKDOWN = ("text/markdown", 2, [".md", ".markdown", ".mdown"])
    VISIO = ("application/vnd.visio", 3, [".vsdx", ".vsd"])
    WORD = ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", 4, [".docx", ".doc"])
    PDF = ("application/pdf", 5, [".pdf"])
    POWERPOINT = ("application/vnd.openxmlformats-officedocument.presentationml.presentation", 6, [".pptx", ".ppt"])
    UNKNOWN = ("application/octet-stream", 99, [])

    def __init__(self, mime_type: str, priority: int, extensions: List[str]):
        self.mime_type = mime_type
        self.priority = priority
        self.extensions = extensions

class ArtifactClassifier:
    """
    Enhanced artifact classifier with priority-based processing
    and heterogeneous environment support.
    """
    
    def __init__(self):
        self.supported_types = {ext: artifact_type 
                              for artifact_type in ArtifactType 
                              for ext in artifact_type.extensions}
        self._init_mimetypes()
    
    def _init_mimetypes(self):
        """Initialize custom MIME type mappings"""
        mimetypes.add_type('application/vnd.visio', '.vsdx')
        mimetypes.add_type('text/markdown', '.md')
        mimetypes.add_type('text/markdown', '.markdown')
    
    def classify_file(self, file_path: str) -> Tuple[ArtifactType, Dict]:
        """
        Classify a single file and extract metadata
        
        Args:
            file_path: Path to the file to classify
            
        Returns:
            Tuple of (ArtifactType, metadata_dict)
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return ArtifactType.UNKNOWN, {"error": "File not found"}
        
        # Get file extension
        extension = path.suffix.lower()
        
        # Classify by extension first
        artifact_type = self.supported_types.get(extension, ArtifactType.UNKNOWN)
        
        # Extract basic metadata
        metadata = {
            "file_path": str(path.absolute()),
            "file_name": path.name,
            "file_size": path.stat().st_size,
            "extension": extension,
            "mime_type": artifact_type.mime_type,
            "priority": artifact_type.priority,
            "modified_time": path.stat().st_mtime
        }
        
        # Add type-specific metadata
        if artifact_type == ArtifactType.ZIP:
            metadata.update(self._analyze_zip(file_path))
        
        return artifact_type, metadata
    
    def _analyze_zip(self, zip_path: str) -> Dict:
        """Analyze ZIP file contents and create manifest"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Categorize contents
                python_files = [f for f in file_list if f.endswith('.py')]
                markdown_files = [f for f in file_list if f.endswith(('.md', '.markdown'))]
                config_files = [f for f in file_list if f.endswith(('.json', '.yaml', '.yml', '.toml', '.ini'))]
                
                return {
                    "total_files": len(file_list),
                    "python_files": len(python_files),
                    "markdown_files": len(markdown_files),
                    "config_files": len(config_files),
                    "file_manifest": file_list[:50],  # Limit for performance
                    "python_file_list": python_files,
                    "markdown_file_list": markdown_files,
                    "has_code": len(python_files) > 0,
                    "has_docs": len(markdown_files) > 0
                }
        except Exception as e:
            logger.error(f"Error analyzing ZIP file {zip_path}: {e}")
            return {"error": str(e)}
    
    def classify_directory(self, directory_path: str, recursive: bool = True) -> List[Tuple[ArtifactType, Dict]]:
        """
        Classify all supported files in a directory
        
        Args:
            directory_path: Path to directory to scan
            recursive: Whether to scan subdirectories
            
        Returns:
            List of (ArtifactType, metadata) tuples sorted by priority
        """
        results = []
        path = Path(directory_path)
        
        if not path.exists() or not path.is_dir():
            logger.error(f"Directory not found or not a directory: {directory_path}")
            return results
        
        # Get all files
        if recursive:
            files = path.rglob('*')
        else:
            files = path.glob('*')
        
        # Classify each file
        for file_path in files:
            if file_path.is_file():
                artifact_type, metadata = self.classify_file(str(file_path))
                if artifact_type != ArtifactType.UNKNOWN:
                    results.append((artifact_type, metadata))
        
        # Sort by priority (ZIP files first)
        results.sort(key=lambda x: x[0].priority)
        
        return results
    
    def get_processing_order(self, artifacts: List[Tuple[ArtifactType, Dict]]) -> List[Tuple[ArtifactType, Dict]]:
        """
        Return artifacts in processing order (ZIP first, then by priority)
        """
        return sorted(artifacts, key=lambda x: (x[0].priority, x[1].get('file_size', 0)))
    
    def filter_by_type(self, artifacts: List[Tuple[ArtifactType, Dict]], 
                      artifact_types: List[ArtifactType]) -> List[Tuple[ArtifactType, Dict]]:
        """Filter artifacts by specific types"""
        return [(atype, metadata) for atype, metadata in artifacts 
                if atype in artifact_types]
    
    def get_statistics(self, artifacts: List[Tuple[ArtifactType, Dict]]) -> Dict:
        """Generate statistics for classified artifacts"""
        stats = {
            "total_artifacts": len(artifacts),
            "by_type": {},
            "total_size": 0,
            "priority_distribution": {}
        }
        
        for artifact_type, metadata in artifacts:
            type_name = artifact_type.name
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1
            stats["total_size"] += metadata.get("file_size", 0)
            
            priority = artifact_type.priority
            stats["priority_distribution"][priority] = stats["priority_distribution"].get(priority, 0) + 1
        
        return stats
