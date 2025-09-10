
"""
ZIP Archive Parser with Priority Processing
===========================================

Specialized parser for ZIP files with manifest generation,
Python code extraction, and handover document linking.
"""

import zipfile
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import logging

from .base_parser import BaseParser

logger = logging.getLogger(__name__)

class ZipParser(BaseParser):
    """
    Enhanced ZIP parser with priority processing and code analysis
    """
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.zip', '.zipx']
        
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse ZIP file and extract comprehensive metadata
        
        Args:
            file_path: Path to ZIP file
            
        Returns:
            Dictionary with ZIP contents analysis
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Get file list and info
                file_list = zip_file.namelist()
                file_info = zip_file.infolist()
                
                # Analyze contents
                analysis = self._analyze_contents(file_list, file_info)
                
                # Generate manifest
                manifest = self._generate_manifest(zip_file, file_list, file_info)
                
                # Extract Python code if present
                python_analysis = self._analyze_python_code(zip_file, analysis['python_files'])
                
                # Find handover documents
                handover_docs = self._find_handover_documents(file_list)
                
                return {
                    "total_files": len(file_list),
                    "compressed_size": sum(info.compress_size for info in file_info),
                    "uncompressed_size": sum(info.file_size for info in file_info),
                    "compression_ratio": self._calculate_compression_ratio(file_info),
                    "file_analysis": analysis,
                    "manifest": manifest,
                    "python_analysis": python_analysis,
                    "handover_documents": handover_docs,
                    "priority_score": self._calculate_priority_score(analysis)
                }
                
        except Exception as e:
            logger.error(f"Error parsing ZIP file {file_path}: {e}")
            return {"error": str(e)}
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from text files within the ZIP
        
        Args:
            file_path: Path to ZIP file
            
        Returns:
            Combined text content from readable files
        """
        text_content = []
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                for file_name in zip_file.namelist():
                    if self._is_text_file(file_name):
                        try:
                            with zip_file.open(file_name) as f:
                                content = f.read().decode('utf-8', errors='ignore')
                                text_content.append(f"=== {file_name} ===\n{content}\n")
                        except Exception as e:
                            logger.warning(f"Could not read {file_name}: {e}")
                            
        except Exception as e:
            logger.error(f"Error extracting text from ZIP {file_path}: {e}")
            return f"Error: {e}"
        
        return "\n".join(text_content)
    
    def _analyze_contents(self, file_list: List[str], file_info: List) -> Dict[str, Any]:
        """Analyze ZIP contents by file type"""
        analysis = {
            "python_files": [],
            "markdown_files": [],
            "config_files": [],
            "image_files": [],
            "document_files": [],
            "other_files": [],
            "directories": []
        }
        
        for file_name in file_list:
            if file_name.endswith('/'):
                analysis["directories"].append(file_name)
            elif file_name.endswith('.py'):
                analysis["python_files"].append(file_name)
            elif file_name.endswith(('.md', '.markdown', '.rst')):
                analysis["markdown_files"].append(file_name)
            elif file_name.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg')):
                analysis["config_files"].append(file_name)
            elif file_name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                analysis["image_files"].append(file_name)
            elif file_name.endswith(('.docx', '.pdf', '.pptx')):
                analysis["document_files"].append(file_name)
            else:
                analysis["other_files"].append(file_name)
        
        return analysis
    
    def _generate_manifest(self, zip_file: zipfile.ZipFile, 
                          file_list: List[str], file_info: List) -> Dict[str, Any]:
        """Generate comprehensive manifest for ZIP contents"""
        manifest = {
            "version": "1.0",
            "generated_by": "DMAIC_ZIP_Parser",
            "files": []
        }
        
        for info in file_info:
            file_entry = {
                "filename": info.filename,
                "file_size": info.file_size,
                "compress_size": info.compress_size,
                "date_time": list(info.date_time),
                "crc": info.CRC,
                "is_directory": info.filename.endswith('/'),
                "compression_type": info.compress_type
            }
            manifest["files"].append(file_entry)
        
        return manifest
    
    def _analyze_python_code(self, zip_file: zipfile.ZipFile, 
                           python_files: List[str]) -> Dict[str, Any]:
        """Analyze Python code within the ZIP"""
        if not python_files:
            return {"has_python": False}
        
        analysis = {
            "has_python": True,
            "python_file_count": len(python_files),
            "files": [],
            "imports": set(),
            "functions": [],
            "classes": []
        }
        
        for py_file in python_files[:10]:  # Limit analysis for performance
            try:
                with zip_file.open(py_file) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    file_analysis = self._analyze_python_file_content(content)
                    file_analysis["filename"] = py_file
                    analysis["files"].append(file_analysis)
                    analysis["imports"].update(file_analysis.get("imports", []))
                    
            except Exception as e:
                logger.warning(f"Could not analyze Python file {py_file}: {e}")
        
        analysis["imports"] = list(analysis["imports"])
        return analysis
    
    def _analyze_python_file_content(self, content: str) -> Dict[str, Any]:
        """Basic Python code analysis"""
        lines = content.split('\n')
        analysis = {
            "line_count": len(lines),
            "imports": [],
            "functions": [],
            "classes": []
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                analysis["imports"].append(line)
            elif line.startswith('def '):
                func_name = line.split('(')[0].replace('def ', '')
                analysis["functions"].append(func_name)
            elif line.startswith('class '):
                class_name = line.split('(')[0].split(':')[0].replace('class ', '')
                analysis["classes"].append(class_name)
        
        return analysis
    
    def _find_handover_documents(self, file_list: List[str]) -> List[str]:
        """Find potential handover/documentation files"""
        handover_patterns = [
            'readme', 'handover', 'documentation', 'guide', 'manual',
            'setup', 'install', 'getting_started', 'quickstart'
        ]
        
        handover_docs = []
        for file_name in file_list:
            file_lower = file_name.lower()
            if any(pattern in file_lower for pattern in handover_patterns):
                if file_name.endswith(('.md', '.txt', '.rst', '.docx')):
                    handover_docs.append(file_name)
        
        return handover_docs
    
    def _calculate_compression_ratio(self, file_info: List) -> float:
        """Calculate overall compression ratio"""
        total_uncompressed = sum(info.file_size for info in file_info)
        total_compressed = sum(info.compress_size for info in file_info)
        
        if total_uncompressed == 0:
            return 0.0
        
        return round((1 - total_compressed / total_uncompressed) * 100, 2)
    
    def _calculate_priority_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate priority score based on content analysis"""
        score = 100  # Base priority for ZIP files
        
        # Boost for Python code
        if analysis["python_files"]:
            score += len(analysis["python_files"]) * 10
        
        # Boost for documentation
        if analysis["markdown_files"]:
            score += len(analysis["markdown_files"]) * 5
        
        # Boost for configuration files
        if analysis["config_files"]:
            score += len(analysis["config_files"]) * 3
        
        return min(score, 200)  # Cap at 200
    
    def _is_text_file(self, filename: str) -> bool:
        """Check if file is likely to contain readable text"""
        text_extensions = [
            '.txt', '.md', '.rst', '.py', '.js', '.html', '.css', '.json',
            '.yaml', '.yml', '.toml', '.ini', '.cfg', '.xml', '.csv'
        ]
        return any(filename.lower().endswith(ext) for ext in text_extensions)
    
    def extract_to_temp(self, file_path: str, target_files: Optional[List[str]] = None) -> str:
        """
        Extract ZIP contents to temporary directory
        
        Args:
            file_path: Path to ZIP file
            target_files: Specific files to extract (None for all)
            
        Returns:
            Path to temporary directory with extracted files
        """
        temp_dir = tempfile.mkdtemp(prefix="dmaic_zip_")
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                if target_files:
                    for file_name in target_files:
                        if file_name in zip_file.namelist():
                            zip_file.extract(file_name, temp_dir)
                else:
                    zip_file.extractall(temp_dir)
            
            return temp_dir
            
        except Exception as e:
            logger.error(f"Error extracting ZIP to temp directory: {e}")
            return ""
