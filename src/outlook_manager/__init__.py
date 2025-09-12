"""Outlook Archive Management Module.

This module provides functionality for managing Outlook email archives,
including exporting archives to PST files while maintaining navigation
capabilities within Outlook.

Key Features:
- Export Outlook archives for specific years (e.g., 2025)
- Create PST files for offline storage
- Maintain folder structure and navigation
- Support for subfolder hierarchy
"""

from .archive_exporter import OutlookArchiveExporter
from .pst_manager import PSTFileManager
from .navigation_manager import NavigationManager

__all__ = [
    "OutlookArchiveExporter",
    "PSTFileManager", 
    "NavigationManager",
]

__version__ = "1.0.0"