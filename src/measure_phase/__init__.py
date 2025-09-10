
"""
DMAIC Measure Phase - Enhanced Heterogeneous Artifact Support
============================================================

This module provides comprehensive artifact analysis, indexing, ranking, and 
integration capabilities for heterogeneous environments including VISIO, WORD, 
ZIP, MARKDOWN, PDF, and POWERPOINT files.

Key Components:
- Artifact Type Classifier
- Priority-based Processing (ZIP first)
- SQL-like Querying with FTS
- [KEB] Pipeline Integration
- Caching and Performance Optimization
- DEEP Agent → GitHub → User Git Workflow
"""

__version__ = "1.0.0"
__author__ = "DMAIC Enhanced System"

from .classifier import ArtifactClassifier
from .index import ArtifactIndexer
from .ranking import ArtifactRanker
from .cache import PriorityCache
from .keb_interface import KEBAdapter
from .workflow import WorkflowSync

__all__ = [
    'ArtifactClassifier',
    'ArtifactIndexer', 
    'ArtifactRanker',
    'PriorityCache',
    'KEBAdapter',
    'WorkflowSync'
]
