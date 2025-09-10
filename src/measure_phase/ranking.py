
"""
Artifact Ranking System
=======================

Implements multi-dimensional ranking system:
- Total Rank: Overall importance across all artifacts
- Group Rank: Ranking within artifact type groups
- Self Rank: Individual artifact quality metrics
- Pipeline Role: Importance in processing pipeline
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import math

logger = logging.getLogger(__name__)

class RankingDimension(Enum):
    """Ranking dimensions for artifacts"""
    TOTAL = "total"
    GROUP = "group" 
    SELF = "self"
    PIPELINE = "pipeline"

class ArtifactRanker:
    """
    Multi-dimensional artifact ranking system
    """
    
    def __init__(self):
        self.ranking_weights = {
            'file_size': 0.1,
            'modification_recency': 0.15,
            'content_richness': 0.25,
            'type_priority': 0.2,
            'processing_complexity': 0.15,
            'pipeline_importance': 0.15
        }
        
        # Type-specific priority weights
        self.type_priorities = {
            'ZIP': 100,
            'MARKDOWN': 80,
            'VISIO': 70,
            'WORD': 60,
            'PDF': 50,
            'POWERPOINT': 40,
            'UNKNOWN': 10
        }
    
    def calculate_total_rank(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate total ranking across all artifacts
        
        Args:
            artifacts: List of artifact dictionaries with metadata
            
        Returns:
            Artifacts with total_rank scores added
        """
        if not artifacts:
            return artifacts
        
        # Calculate individual scores
        for artifact in artifacts:
            artifact['total_rank'] = self._calculate_total_score(artifact, artifacts)
        
        # Sort by total rank (descending)
        artifacts.sort(key=lambda x: x.get('total_rank', 0), reverse=True)
        
        # Add rank positions
        for i, artifact in enumerate(artifacts):
            artifact['total_rank_position'] = i + 1
        
        return artifacts
    
    def calculate_group_rank(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate ranking within artifact type groups
        
        Args:
            artifacts: List of artifact dictionaries
            
        Returns:
            Artifacts with group_rank scores added
        """
        # Group by artifact type
        groups = {}
        for artifact in artifacts:
            artifact_type = artifact.get('artifact_type', 'UNKNOWN')
            if artifact_type not in groups:
                groups[artifact_type] = []
            groups[artifact_type].append(artifact)
        
        # Rank within each group
        for artifact_type, group_artifacts in groups.items():
            # Calculate group-specific scores
            for artifact in group_artifacts:
                artifact['group_rank'] = self._calculate_group_score(artifact, group_artifacts, artifact_type)
            
            # Sort by group rank
            group_artifacts.sort(key=lambda x: x.get('group_rank', 0), reverse=True)
            
            # Add group rank positions
            for i, artifact in enumerate(group_artifacts):
                artifact['group_rank_position'] = i + 1
                artifact['group_size'] = len(group_artifacts)
        
        return artifacts
    
    def calculate_self_rank(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate individual artifact quality metrics
        
        Args:
            artifacts: List of artifact dictionaries
            
        Returns:
            Artifacts with self_rank scores added
        """
        for artifact in artifacts:
            artifact['self_rank'] = self._calculate_self_score(artifact)
            artifact['self_rank_category'] = self._categorize_self_rank(artifact['self_rank'])
        
        return artifacts
    
    def calculate_pipeline_rank(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate importance in processing pipeline
        
        Args:
            artifacts: List of artifact dictionaries
            
        Returns:
            Artifacts with pipeline_rank scores added
        """
        for artifact in artifacts:
            artifact['pipeline_rank'] = self._calculate_pipeline_score(artifact)
            artifact['pipeline_role'] = self._determine_pipeline_role(artifact)
        
        return artifacts
    
    def rank_all_dimensions(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate all ranking dimensions
        
        Args:
            artifacts: List of artifact dictionaries
            
        Returns:
            Fully ranked artifacts
        """
        artifacts = self.calculate_self_rank(artifacts)
        artifacts = self.calculate_group_rank(artifacts)
        artifacts = self.calculate_pipeline_rank(artifacts)
        artifacts = self.calculate_total_rank(artifacts)
        
        return artifacts
    
    def get_top_artifacts(self, artifacts: List[Dict[str, Any]], 
                         dimension: RankingDimension = RankingDimension.TOTAL,
                         limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top artifacts by specified ranking dimension
        
        Args:
            artifacts: List of ranked artifacts
            dimension: Ranking dimension to use
            limit: Number of top artifacts to return
            
        Returns:
            Top artifacts by specified dimension
        """
        rank_key = f"{dimension.value}_rank"
        
        # Filter artifacts that have the specified rank
        ranked_artifacts = [a for a in artifacts if rank_key in a]
        
        # Sort by rank (descending)
        ranked_artifacts.sort(key=lambda x: x.get(rank_key, 0), reverse=True)
        
        return ranked_artifacts[:limit]
    
    def _calculate_total_score(self, artifact: Dict[str, Any], all_artifacts: List[Dict[str, Any]]) -> float:
        """Calculate total ranking score"""
        score = 0.0
        
        # File size score (normalized)
        max_size = max((a.get('file_size', 0) for a in all_artifacts), default=1)
        size_score = math.log(artifact.get('file_size', 1)) / math.log(max_size) if max_size > 1 else 0
        score += size_score * self.ranking_weights['file_size']
        
        # Modification recency score
        import time
        current_time = time.time()
        mod_time = artifact.get('modified_time', 0)
        days_old = (current_time - mod_time) / 86400 if mod_time > 0 else 365
        recency_score = max(0, 1 - (days_old / 365))  # Decay over a year
        score += recency_score * self.ranking_weights['modification_recency']
        
        # Content richness score
        content_score = self._calculate_content_richness(artifact)
        score += content_score * self.ranking_weights['content_richness']
        
        # Type priority score
        artifact_type = artifact.get('artifact_type', 'UNKNOWN')
        type_score = self.type_priorities.get(artifact_type, 0) / 100.0
        score += type_score * self.ranking_weights['type_priority']
        
        # Processing complexity score
        complexity_score = self._calculate_processing_complexity(artifact)
        score += complexity_score * self.ranking_weights['processing_complexity']
        
        # Pipeline importance score
        pipeline_score = self._calculate_pipeline_score(artifact)
        score += pipeline_score * self.ranking_weights['pipeline_importance']
        
        return round(score * 100, 2)  # Scale to 0-100
    
    def _calculate_group_score(self, artifact: Dict[str, Any], 
                              group_artifacts: List[Dict[str, Any]], 
                              artifact_type: str) -> float:
        """Calculate group-specific ranking score"""
        score = 0.0
        
        # Type-specific scoring
        if artifact_type == 'ZIP':
            score += self._score_zip_artifact(artifact)
        elif artifact_type == 'MARKDOWN':
            score += self._score_markdown_artifact(artifact)
        elif artifact_type == 'WORD':
            score += self._score_word_artifact(artifact)
        elif artifact_type == 'PDF':
            score += self._score_pdf_artifact(artifact)
        elif artifact_type == 'POWERPOINT':
            score += self._score_powerpoint_artifact(artifact)
        elif artifact_type == 'VISIO':
            score += self._score_visio_artifact(artifact)
        
        # Relative size within group
        group_sizes = [a.get('file_size', 0) for a in group_artifacts]
        max_group_size = max(group_sizes) if group_sizes else 1
        if max_group_size > 0:
            relative_size = artifact.get('file_size', 0) / max_group_size
            score += relative_size * 20
        
        return round(score, 2)
    
    def _calculate_self_score(self, artifact: Dict[str, Any]) -> float:
        """Calculate individual artifact quality score"""
        score = 0.0
        metadata = artifact.get('metadata', {})
        
        # Basic file metrics
        file_size = artifact.get('file_size', 0)
        if file_size > 0:
            score += min(math.log(file_size) / 10, 20)  # Cap at 20 points
        
        # Content quality indicators
        if 'word_count' in metadata:
            word_count = metadata['word_count']
            score += min(word_count / 100, 30)  # Cap at 30 points
        
        if 'structure_score' in metadata:
            score += metadata['structure_score'] * 0.3
        
        if 'complexity_score' in metadata:
            score += metadata['complexity_score'] * 10
        
        # Error penalty
        if 'error' in metadata:
            score *= 0.1  # Heavy penalty for parsing errors
        
        return round(score, 2)
    
    def _calculate_pipeline_score(self, artifact: Dict[str, Any]) -> float:
        """Calculate pipeline importance score"""
        score = 0.0
        artifact_type = artifact.get('artifact_type', 'UNKNOWN')
        metadata = artifact.get('metadata', {})
        
        # Base pipeline importance by type
        pipeline_importance = {
            'ZIP': 90,      # Highest - contains multiple artifacts
            'MARKDOWN': 70, # High - documentation and handover
            'WORD': 60,     # Medium-high - formal documents
            'VISIO': 50,    # Medium - diagrams and processes
            'PDF': 40,      # Medium-low - static documents
            'POWERPOINT': 30, # Low - presentations
            'UNKNOWN': 5    # Very low
        }
        
        score += pipeline_importance.get(artifact_type, 5)
        
        # Special bonuses
        if artifact_type == 'ZIP':
            # Bonus for Python code
            if metadata.get('has_code', False):
                score += 20
            # Bonus for documentation
            if metadata.get('has_docs', False):
                score += 10
        
        if artifact_type == 'MARKDOWN':
            # Bonus for README files
            file_name = artifact.get('file_name', '').lower()
            if 'readme' in file_name:
                score += 15
        
        return round(score, 2)
    
    def _calculate_content_richness(self, artifact: Dict[str, Any]) -> float:
        """Calculate content richness score"""
        metadata = artifact.get('metadata', {})
        richness = 0.0
        
        # Text content indicators
        if 'word_count' in metadata:
            richness += min(metadata['word_count'] / 1000, 0.5)
        
        if 'character_count' in metadata:
            richness += min(metadata['character_count'] / 10000, 0.3)
        
        # Structure indicators
        if 'headings' in metadata:
            richness += min(len(metadata['headings']) / 10, 0.2)
        
        if 'links' in metadata:
            richness += min(len(metadata['links']) / 20, 0.2)
        
        if 'images' in metadata:
            richness += min(len(metadata['images']) / 10, 0.1)
        
        # Special content types
        if 'python_files' in metadata:
            richness += min(len(metadata['python_files']) / 10, 0.3)
        
        if 'tables' in metadata:
            richness += min(len(metadata['tables']) / 5, 0.2)
        
        return min(richness, 1.0)  # Cap at 1.0
    
    def _calculate_processing_complexity(self, artifact: Dict[str, Any]) -> float:
        """Calculate processing complexity score"""
        artifact_type = artifact.get('artifact_type', 'UNKNOWN')
        metadata = artifact.get('metadata', {})
        
        complexity_base = {
            'ZIP': 0.9,      # High complexity - multiple files
            'VISIO': 0.8,    # High complexity - diagram parsing
            'POWERPOINT': 0.7, # Medium-high - slides and media
            'WORD': 0.6,     # Medium - document structure
            'PDF': 0.5,      # Medium-low - text extraction
            'MARKDOWN': 0.3, # Low - simple text parsing
            'UNKNOWN': 0.1   # Very low
        }
        
        base_score = complexity_base.get(artifact_type, 0.1)
        
        # Adjust based on content
        if 'total_files' in metadata:
            # ZIP files - complexity increases with file count
            file_count = metadata['total_files']
            base_score += min(file_count / 100, 0.3)
        
        if 'page_count' in metadata:
            # Multi-page documents
            page_count = metadata['page_count']
            base_score += min(page_count / 50, 0.2)
        
        return min(base_score, 1.0)
    
    def _determine_pipeline_role(self, artifact: Dict[str, Any]) -> str:
        """Determine artifact's role in processing pipeline"""
        artifact_type = artifact.get('artifact_type', 'UNKNOWN')
        metadata = artifact.get('metadata', {})
        file_name = artifact.get('file_name', '').lower()
        
        if artifact_type == 'ZIP':
            if metadata.get('has_code', False):
                return 'Code Archive'
            elif metadata.get('has_docs', False):
                return 'Documentation Archive'
            else:
                return 'Data Archive'
        
        elif artifact_type == 'MARKDOWN':
            if 'readme' in file_name:
                return 'Project Documentation'
            elif any(word in file_name for word in ['api', 'guide', 'tutorial']):
                return 'Technical Documentation'
            else:
                return 'General Documentation'
        
        elif artifact_type == 'WORD':
            doc_type = metadata.get('document_type', 'General Document')
            return f"Formal {doc_type}"
        
        elif artifact_type == 'VISIO':
            diagram_type = metadata.get('diagram_type', 'General Diagram')
            return f"Process {diagram_type}"
        
        elif artifact_type == 'PDF':
            doc_type = metadata.get('document_type', 'General PDF')
            return f"Reference {doc_type}"
        
        elif artifact_type == 'POWERPOINT':
            pres_type = metadata.get('presentation_type', 'General Presentation')
            return f"Visual {pres_type}"
        
        else:
            return 'Unknown Role'
    
    def _categorize_self_rank(self, score: float) -> str:
        """Categorize self rank score"""
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Average'
        elif score >= 20:
            return 'Poor'
        else:
            return 'Very Poor'
    
    # Type-specific scoring methods
    def _score_zip_artifact(self, artifact: Dict[str, Any]) -> float:
        """Score ZIP-specific attributes"""
        metadata = artifact.get('metadata', {})
        score = 0.0
        
        if metadata.get('has_code', False):
            score += 30
        if metadata.get('has_docs', False):
            score += 20
        if metadata.get('compression_ratio', 0) > 50:
            score += 10
        
        return score
    
    def _score_markdown_artifact(self, artifact: Dict[str, Any]) -> float:
        """Score Markdown-specific attributes"""
        metadata = artifact.get('metadata', {})
        score = 0.0
        
        if metadata.get('structure_score', 0) > 50:
            score += 25
        if len(metadata.get('headings', [])) > 3:
            score += 15
        if len(metadata.get('links', [])) > 5:
            score += 10
        
        return score
    
    def _score_word_artifact(self, artifact: Dict[str, Any]) -> float:
        """Score Word-specific attributes"""
        metadata = artifact.get('metadata', {})
        score = 0.0
        
        if metadata.get('word_count', 0) > 1000:
            score += 20
        if len(metadata.get('tables', [])) > 0:
            score += 15
        if metadata.get('properties', {}).get('author'):
            score += 10
        
        return score
    
    def _score_pdf_artifact(self, artifact: Dict[str, Any]) -> float:
        """Score PDF-specific attributes"""
        metadata = artifact.get('metadata', {})
        score = 0.0
        
        if metadata.get('page_count', 0) > 10:
            score += 20
        if metadata.get('images_count', 0) > 0:
            score += 10
        if metadata.get('links_count', 0) > 0:
            score += 10
        
        return score
    
    def _score_powerpoint_artifact(self, artifact: Dict[str, Any]) -> float:
        """Score PowerPoint-specific attributes"""
        metadata = artifact.get('metadata', {})
        score = 0.0
        
        if metadata.get('slide_count', 0) > 10:
            score += 20
        if metadata.get('total_images', 0) > 5:
            score += 15
        if metadata.get('total_text_shapes', 0) > 20:
            score += 10
        
        return score
    
    def _score_visio_artifact(self, artifact: Dict[str, Any]) -> float:
        """Score Visio-specific attributes"""
        metadata = artifact.get('metadata', {})
        score = 0.0
        
        if metadata.get('total_shapes', 0) > 20:
            score += 25
        if metadata.get('total_connections', 0) > 10:
            score += 20
        if metadata.get('complexity_score', 0) > 2:
            score += 15
        
        return score
