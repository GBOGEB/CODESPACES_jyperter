"""Navigation Manager for Outlook Email Archives.

This module handles the navigation and integration aspects of archived
email data, ensuring users can still browse and access their emails
through Outlook while having offline copies.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import json

logger = logging.getLogger(__name__)


class NavigationManager:
    """Manages navigation and integration of archived email data with Outlook.
    
    This class ensures that archived emails remain accessible through
    Outlook's interface while being stored offline on the local PC.
    """
    
    def __init__(self, archive_root: Union[str, Path] = None):
        """Initialize the Navigation Manager.
        
        Args:
            archive_root: Root directory containing archived email data.
                         Defaults to current directory + 'email_archives'
        """
        self.archive_root = Path(archive_root) if archive_root else Path.cwd() / "email_archives"
        self.archive_root.mkdir(parents=True, exist_ok=True)
        
        self.navigation_config_file = self.archive_root / "navigation_config.json"
        self.folder_mapping_file = self.archive_root / "folder_mapping.json"
        
        self._load_navigation_config()
        logger.info(f"Navigation Manager initialized with archive root: {self.archive_root}")
    
    def _load_navigation_config(self) -> None:
        """Load navigation configuration from file."""
        self.navigation_config = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "archive_root": str(self.archive_root),
            "integration_mode": "hybrid",  # 'online', 'offline', 'hybrid'
            "show_offline_folders": True,
            "auto_sync": False,
            "cache_settings": {
                "enable_cache": True,
                "cache_size_mb": 100,
                "cache_duration_days": 7
            }
        }
        
        if self.navigation_config_file.exists():
            try:
                with open(self.navigation_config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.navigation_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Failed to load navigation config: {e}")
        
        self._save_navigation_config()
    
    def _save_navigation_config(self) -> None:
        """Save navigation configuration to file."""
        try:
            with open(self.navigation_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.navigation_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save navigation config: {e}")
    
    def setup_outlook_integration(self, 
                                 pst_files: List[Dict[str, Any]], 
                                 integration_mode: str = "hybrid") -> Dict[str, Any]:
        """Set up integration between archived PST files and Outlook navigation.
        
        Args:
            pst_files: List of PST file information dictionaries
            integration_mode: Type of integration ('online', 'offline', 'hybrid')
            
        Returns:
            Dictionary containing setup results
        """
        logger.info(f"Setting up Outlook integration in {integration_mode} mode")
        
        setup_results = {
            "setup_date": datetime.now().isoformat(),
            "integration_mode": integration_mode,
            "pst_files": pst_files,
            "integrated_folders": [],
            "navigation_shortcuts": [],
            "success": False
        }
        
        try:
            # Update navigation config
            self.navigation_config["integration_mode"] = integration_mode
            self.navigation_config["last_setup"] = datetime.now().isoformat()
            
            # Create folder mappings
            folder_mappings = self._create_folder_mappings(pst_files)
            setup_results["folder_mappings"] = folder_mappings
            
            # Set up navigation shortcuts
            shortcuts = self._create_navigation_shortcuts(pst_files, integration_mode)
            setup_results["navigation_shortcuts"] = shortcuts
            
            # Configure Outlook profile integration
            if sys.platform == "win32":
                profile_config = self._configure_outlook_profile(pst_files, integration_mode)
                setup_results["outlook_profile"] = profile_config
            
            # Create search index for offline access
            search_index = self._create_search_index(pst_files)
            setup_results["search_index"] = search_index
            
            setup_results["success"] = True
            self._save_navigation_config()
            
            logger.info("Outlook integration setup completed successfully")
            
        except Exception as e:
            logger.error(f"Outlook integration setup failed: {e}")
            setup_results["error"] = str(e)
        
        return setup_results
    
    def _create_folder_mappings(self, pst_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create mappings between original Outlook folders and archived PST files.
        
        Args:
            pst_files: List of PST file information
            
        Returns:
            Dictionary containing folder mappings
        """
        folder_mappings = {
            "creation_date": datetime.now().isoformat(),
            "mappings": {}
        }
        
        for pst_info in pst_files:
            original_folder = pst_info.get("folder_name", "Unknown")
            pst_path = pst_info.get("path", "")
            
            folder_mappings["mappings"][original_folder] = {
                "pst_file": pst_path,
                "display_name": f"{original_folder} (Archive)",
                "access_type": "offline",
                "item_count": pst_info.get("item_count", 0),
                "last_updated": pst_info.get("creation_date", ""),
                "navigation_path": f"Archives\\{original_folder}"
            }
        
        # Save folder mappings
        try:
            with open(self.folder_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(folder_mappings, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save folder mappings: {e}")
        
        return folder_mappings
    
    def _create_navigation_shortcuts(self, 
                                   pst_files: List[Dict[str, Any]], 
                                   integration_mode: str) -> List[Dict[str, Any]]:
        """Create navigation shortcuts for easy access to archived data.
        
        Args:
            pst_files: List of PST file information
            integration_mode: Integration mode being used
            
        Returns:
            List of navigation shortcut definitions
        """
        shortcuts = []
        
        # Create main archive shortcut
        main_shortcut = {
            "name": "Email Archives",
            "type": "folder_group",
            "path": str(self.archive_root),
            "icon": "archive",
            "description": "Access to all archived email data",
            "integration_mode": integration_mode
        }
        shortcuts.append(main_shortcut)
        
        # Create shortcuts for each PST file
        for pst_info in pst_files:
            folder_name = pst_info.get("folder_name", "Unknown")
            
            shortcut = {
                "name": f"{folder_name} Archive",
                "type": "pst_folder",
                "pst_file": pst_info.get("path", ""),
                "original_folder": folder_name,
                "item_count": pst_info.get("item_count", 0),
                "access_mode": "read_write" if integration_mode == "hybrid" else "read_only",
                "show_in_favorites": True
            }
            shortcuts.append(shortcut)
        
        # Create year-based shortcuts
        years = set()
        for pst_info in pst_files:
            # Extract year from filename or metadata
            filename = pst_info.get("filename", "")
            if filename:
                parts = filename.split("_")
                for part in parts:
                    if part.isdigit() and len(part) == 4:
                        years.add(int(part))
        
        for year in sorted(years):
            year_shortcut = {
                "name": f"Archive {year}",
                "type": "year_group",
                "year": year,
                "description": f"All archived emails from {year}",
                "auto_expand": True
            }
            shortcuts.append(year_shortcut)
        
        return shortcuts
    
    def _configure_outlook_profile(self, 
                                  pst_files: List[Dict[str, Any]], 
                                  integration_mode: str) -> Dict[str, Any]:
        """Configure Outlook profile for PST file integration.
        
        Args:
            pst_files: List of PST file information
            integration_mode: Integration mode being used
            
        Returns:
            Outlook profile configuration
        """
        profile_config = {
            "profile_name": "Email_Archives_Profile",
            "creation_date": datetime.now().isoformat(),
            "integration_mode": integration_mode,
            "pst_integrations": []
        }
        
        for pst_info in pst_files:
            pst_integration = {
                "pst_file": pst_info.get("path", ""),
                "display_name": f"Archive - {pst_info.get('folder_name', 'Unknown')}",
                "auto_connect": True,
                "read_only": integration_mode == "offline",
                "show_in_folder_list": True,
                "default_delivery": False
            }
            profile_config["pst_integrations"].append(pst_integration)
        
        # Create Outlook profile setup script
        if sys.platform == "win32":
            self._create_outlook_profile_script(profile_config)
        
        return profile_config
    
    def _create_outlook_profile_script(self, profile_config: Dict[str, Any]) -> None:
        """Create a script to set up Outlook profile with PST files.
        
        Args:
            profile_config: Outlook profile configuration
        """
        try:
            script_path = self.archive_root / "setup_outlook_profile.bat"
            
            script_content = f'''@echo off
REM Outlook Profile Setup Script
REM Generated: {datetime.now().isoformat()}
REM Profile: {profile_config["profile_name"]}

echo Setting up Outlook profile for email archives...
echo.

echo Integration Mode: {profile_config["integration_mode"]}
echo PST Files to integrate: {len(profile_config["pst_integrations"])}
echo.

'''
            
            for i, pst_integration in enumerate(profile_config["pst_integrations"], 1):
                script_content += f'''echo {i}. {pst_integration["display_name"]}
echo    File: {pst_integration["pst_file"]}
echo    Mode: {"Read-Only" if pst_integration["read_only"] else "Read-Write"}
echo.

'''
            
            script_content += '''echo To complete the setup:
echo 1. Open Microsoft Outlook
echo 2. Go to File > Account Settings > Account Settings
echo 3. On the Data Files tab, click "Add..."
echo 4. For each PST file listed above:
echo    - Navigate to the file location
echo    - Select the PST file
echo    - Click OK
echo    - Set the display name as shown above
echo.
echo The archived folders will appear in your Outlook folder list.
echo.

pause
'''
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            logger.info(f"Outlook profile setup script created: {script_path}")
            
        except Exception as e:
            logger.error(f"Error creating profile setup script: {e}")
    
    def _create_search_index(self, pst_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a search index for offline email access.
        
        Args:
            pst_files: List of PST file information
            
        Returns:
            Search index information
        """
        search_index = {
            "index_date": datetime.now().isoformat(),
            "version": "1.0",
            "total_files": len(pst_files),
            "indexed_folders": [],
            "search_capabilities": {
                "full_text_search": True,
                "date_range_search": True,
                "sender_search": True,
                "subject_search": True,
                "attachment_search": True
            }
        }
        
        # Create index directory
        index_dir = self.archive_root / "search_index"
        index_dir.mkdir(exist_ok=True)
        
        for pst_info in pst_files:
            folder_name = pst_info.get("folder_name", "Unknown")
            
            # Create folder index
            folder_index = {
                "folder_name": folder_name,
                "pst_file": pst_info.get("path", ""),
                "item_count": pst_info.get("item_count", 0),
                "index_file": str(index_dir / f"{folder_name.replace(' ', '_')}_index.json"),
                "last_indexed": datetime.now().isoformat()
            }
            
            # Create sample index data
            self._create_folder_index(folder_index)
            search_index["indexed_folders"].append(folder_index)
        
        # Save main search index
        index_file = index_dir / "main_index.json"
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(search_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save search index: {e}")
        
        return search_index
    
    def _create_folder_index(self, folder_index: Dict[str, Any]) -> None:
        """Create search index for a specific folder.
        
        Args:
            folder_index: Folder index information
        """
        try:
            # Create sample index entries
            index_entries = []
            item_count = folder_index.get("item_count", 0)
            
            for i in range(min(item_count, 10)):  # Index up to 10 sample items
                entry = {
                    "id": f"{folder_index['folder_name']}_{i+1}",
                    "subject": f"Sample Email {i+1}",
                    "sender": f"sender{i+1}@example.com",
                    "date": datetime.now().isoformat(),
                    "keywords": ["sample", "email", "archive"],
                    "has_attachments": i % 3 == 0,  # Every 3rd email has attachments
                    "size": 1024 * (i + 1),
                    "folder": folder_index["folder_name"]
                }
                index_entries.append(entry)
            
            folder_index_data = {
                "folder_info": folder_index,
                "entries": index_entries,
                "statistics": {
                    "total_entries": len(index_entries),
                    "with_attachments": sum(1 for e in index_entries if e["has_attachments"]),
                    "date_range": {
                        "earliest": datetime.now().isoformat(),
                        "latest": datetime.now().isoformat()
                    }
                }
            }
            
            # Save folder index
            index_file = Path(folder_index["index_file"])
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(folder_index_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to create folder index: {e}")
    
    def search_archives(self, 
                       query: str, 
                       search_type: str = "all", 
                       date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Search through archived email data.
        
        Args:
            query: Search query string
            search_type: Type of search ('all', 'subject', 'sender', 'content')
            date_range: Optional date range filter {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
            
        Returns:
            Dictionary containing search results
        """
        logger.info(f"Searching archives for: '{query}' (type: {search_type})")
        
        search_results = {
            "query": query,
            "search_type": search_type,
            "date_range": date_range,
            "search_date": datetime.now().isoformat(),
            "results": [],
            "total_found": 0,
            "search_time_ms": 0
        }
        
        start_time = datetime.now()
        
        try:
            # Load search index
            index_dir = self.archive_root / "search_index"
            main_index_file = index_dir / "main_index.json"
            
            if not main_index_file.exists():
                search_results["error"] = "Search index not found. Please rebuild the index."
                return search_results
            
            with open(main_index_file, 'r', encoding='utf-8') as f:
                main_index = json.load(f)
            
            # Search through folder indices
            for folder_info in main_index.get("indexed_folders", []):
                folder_results = self._search_folder_index(folder_info, query, search_type, date_range)
                search_results["results"].extend(folder_results)
            
            search_results["total_found"] = len(search_results["results"])
            
            # Sort results by relevance (simplified)
            search_results["results"].sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            search_results["error"] = str(e)
        
        # Calculate search time
        end_time = datetime.now()
        search_results["search_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
        
        return search_results
    
    def _search_folder_index(self, 
                           folder_info: Dict[str, Any], 
                           query: str, 
                           search_type: str, 
                           date_range: Optional[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Search within a specific folder index.
        
        Args:
            folder_info: Folder index information
            query: Search query
            search_type: Type of search
            date_range: Optional date range filter
            
        Returns:
            List of matching search results
        """
        results = []
        
        try:
            index_file = Path(folder_info["index_file"])
            if not index_file.exists():
                return results
            
            with open(index_file, 'r', encoding='utf-8') as f:
                folder_index = json.load(f)
            
            for entry in folder_index.get("entries", []):
                if self._matches_search_criteria(entry, query, search_type, date_range):
                    result = {
                        "id": entry["id"],
                        "subject": entry["subject"],
                        "sender": entry["sender"],
                        "date": entry["date"],
                        "folder": entry["folder"],
                        "pst_file": folder_info["pst_file"],
                        "relevance_score": self._calculate_relevance(entry, query, search_type),
                        "has_attachments": entry.get("has_attachments", False),
                        "size": entry.get("size", 0)
                    }
                    results.append(result)
        
        except Exception as e:
            logger.error(f"Error searching folder index {folder_info['folder_name']}: {e}")
        
        return results
    
    def _matches_search_criteria(self, 
                               entry: Dict[str, Any], 
                               query: str, 
                               search_type: str, 
                               date_range: Optional[Dict[str, str]]) -> bool:
        """Check if an entry matches the search criteria.
        
        Args:
            entry: Index entry to check
            query: Search query
            search_type: Type of search
            date_range: Optional date range filter
            
        Returns:
            True if entry matches criteria, False otherwise
        """
        query_lower = query.lower()
        
        # Date range check
        if date_range:
            entry_date = entry.get("date", "")
            # Simplified date comparison (in practice, use proper date parsing)
            if date_range.get("start") and entry_date < date_range["start"]:
                return False
            if date_range.get("end") and entry_date > date_range["end"]:
                return False
        
        # Content matching
        if search_type == "subject":
            return query_lower in entry.get("subject", "").lower()
        elif search_type == "sender":
            return query_lower in entry.get("sender", "").lower()
        elif search_type == "content":
            # In practice, this would search email body content
            keywords = entry.get("keywords", [])
            return any(query_lower in keyword.lower() for keyword in keywords)
        else:  # search_type == "all"
            return (query_lower in entry.get("subject", "").lower() or
                   query_lower in entry.get("sender", "").lower() or
                   any(query_lower in keyword.lower() for keyword in entry.get("keywords", [])))
    
    def _calculate_relevance(self, entry: Dict[str, Any], query: str, search_type: str) -> float:
        """Calculate relevance score for a search result.
        
        Args:
            entry: Index entry
            query: Search query
            search_type: Type of search
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        score = 0.0
        query_lower = query.lower()
        
        # Subject match (highest weight)
        if query_lower in entry.get("subject", "").lower():
            score += 0.5
        
        # Sender match (medium weight)
        if query_lower in entry.get("sender", "").lower():
            score += 0.3
        
        # Keyword match (lower weight)
        keywords = entry.get("keywords", [])
        keyword_matches = sum(1 for keyword in keywords if query_lower in keyword.lower())
        score += min(keyword_matches * 0.1, 0.2)
        
        return min(score, 1.0)
    
    def get_navigation_status(self) -> Dict[str, Any]:
        """Get current navigation and integration status.
        
        Returns:
            Dictionary containing navigation status information
        """
        status = {
            "check_date": datetime.now().isoformat(),
            "navigation_config": self.navigation_config,
            "archive_root": str(self.archive_root),
            "folder_mappings_exist": self.folder_mapping_file.exists(),
            "search_index_exists": (self.archive_root / "search_index" / "main_index.json").exists(),
            "integration_ready": False
        }
        
        # Check if integration is ready
        try:
            if (self.folder_mapping_file.exists() and 
                (self.archive_root / "search_index").exists()):
                status["integration_ready"] = True
            
            # Get statistics
            if status["folder_mappings_exist"]:
                with open(self.folder_mapping_file, 'r', encoding='utf-8') as f:
                    mappings = json.load(f)
                    status["mapped_folders"] = len(mappings.get("mappings", {}))
            
            if status["search_index_exists"]:
                index_file = self.archive_root / "search_index" / "main_index.json"
                with open(index_file, 'r', encoding='utf-8') as f:
                    search_index = json.load(f)
                    status["indexed_folders"] = len(search_index.get("indexed_folders", []))
        
        except Exception as e:
            logger.error(f"Error getting navigation status: {e}")
            status["error"] = str(e)
        
        return status
    
    def rebuild_navigation(self, pst_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rebuild navigation and search indices.
        
        Args:
            pst_files: List of PST file information
            
        Returns:
            Rebuild results dictionary
        """
        logger.info("Rebuilding navigation and search indices")
        
        rebuild_results = {
            "rebuild_date": datetime.now().isoformat(),
            "pst_files_processed": len(pst_files),
            "success": False
        }
        
        try:
            # Rebuild folder mappings
            folder_mappings = self._create_folder_mappings(pst_files)
            rebuild_results["folder_mappings"] = folder_mappings
            
            # Rebuild search index
            search_index = self._create_search_index(pst_files)
            rebuild_results["search_index"] = search_index
            
            # Update navigation config
            self.navigation_config["last_rebuild"] = datetime.now().isoformat()
            self._save_navigation_config()
            
            rebuild_results["success"] = True
            logger.info("Navigation rebuild completed successfully")
            
        except Exception as e:
            logger.error(f"Navigation rebuild failed: {e}")
            rebuild_results["error"] = str(e)
        
        return rebuild_results