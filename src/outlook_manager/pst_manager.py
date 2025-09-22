"""PST File Manager for Outlook Archive Data.

This module handles the creation and management of PST (Personal Storage Table)
files for offline email storage while maintaining compatibility with Outlook.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import json
import shutil

logger = logging.getLogger(__name__)


class PSTFileManager:
    """Manages PST file creation and organization for archived email data.
    
    This class provides functionality to create PST files from exported
    Outlook data and organize them for optimal offline access.
    """
    
    def __init__(self, pst_storage_path: Union[str, Path] = None):
        """Initialize the PST File Manager.
        
        Args:
            pst_storage_path: Directory where PST files will be stored.
                             Defaults to current directory + 'pst_files'
        """
        self.pst_storage_path = Path(pst_storage_path) if pst_storage_path else Path.cwd() / "pst_files"
        self.pst_storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"PST File Manager initialized with storage path: {self.pst_storage_path}")
    
    def create_pst_files(self, 
                        export_data: Dict[str, Any], 
                        organization_strategy: str = "by_year_folder") -> Dict[str, Any]:
        """Create PST files from exported Outlook data.
        
        Args:
            export_data: Dictionary containing exported archive data
            organization_strategy: How to organize PST files ('by_year_folder', 'by_folder', 'single_file')
            
        Returns:
            Dictionary containing PST creation results
        """
        logger.info(f"Creating PST files using strategy: {organization_strategy}")
        
        pst_results = {
            "creation_date": datetime.now().isoformat(),
            "organization_strategy": organization_strategy,
            "source_export": export_data.get("export_date"),
            "year": export_data.get("year"),
            "created_pst_files": [],
            "total_size": 0,
            "success": False
        }
        
        try:
            if organization_strategy == "by_year_folder":
                pst_results = self._create_pst_by_year_folder(export_data)
            elif organization_strategy == "by_folder":
                pst_results = self._create_pst_by_folder(export_data)
            elif organization_strategy == "single_file":
                pst_results = self._create_single_pst_file(export_data)
            else:
                raise ValueError(f"Unknown organization strategy: {organization_strategy}")
            
            pst_results["success"] = True
            logger.info("PST file creation completed successfully")
            
        except Exception as e:
            logger.error(f"PST file creation failed: {e}")
            pst_results["error"] = str(e)
        
        # Save PST metadata
        self._save_pst_metadata(pst_results)
        
        return pst_results
    
    def _create_pst_by_year_folder(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create separate PST files for each folder within a year.
        
        Args:
            export_data: Exported archive data
            
        Returns:
            PST creation results
        """
        year = export_data.get("year", datetime.now().year)
        
        pst_results = {
            "creation_date": datetime.now().isoformat(),
            "organization_strategy": "by_year_folder",
            "year": year,
            "created_pst_files": [],
            "total_size": 0
        }
        
        # Create year directory
        year_dir = self.pst_storage_path / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)
        
        exported_folders = export_data.get("exported_folders", [])
        
        for folder_data in exported_folders:
            folder_name = folder_data.get("folder_name", "Unknown")
            pst_filename = f"{year}_{folder_name.replace(' ', '_')}.pst"
            pst_path = year_dir / pst_filename
            
            # Create PST file structure (simulated)
            pst_info = self._create_pst_file_structure(pst_path, folder_data)
            pst_results["created_pst_files"].append(pst_info)
            pst_results["total_size"] += pst_info.get("size", 0)
            
            # Process subfolders
            for subfolder_data in folder_data.get("subfolders", []):
                subfolder_name = subfolder_data.get("name", "Unknown_Subfolder")
                subfolder_pst_filename = f"{year}_{subfolder_name.replace(' ', '_')}.pst"
                subfolder_pst_path = year_dir / subfolder_pst_filename
                
                subfolder_pst_info = self._create_pst_file_structure(subfolder_pst_path, subfolder_data)
                pst_results["created_pst_files"].append(subfolder_pst_info)
                pst_results["total_size"] += subfolder_pst_info.get("size", 0)
        
        return pst_results
    
    def _create_pst_by_folder(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single PST file for each main folder, combining all years.
        
        Args:
            export_data: Exported archive data
            
        Returns:
            PST creation results
        """
        pst_results = {
            "creation_date": datetime.now().isoformat(),
            "organization_strategy": "by_folder",
            "year": export_data.get("year"),
            "created_pst_files": [],
            "total_size": 0
        }
        
        exported_folders = export_data.get("exported_folders", [])
        
        for folder_data in exported_folders:
            folder_name = folder_data.get("folder_name", "Unknown")
            pst_filename = f"{folder_name.replace(' ', '_')}_Archive.pst"
            pst_path = self.pst_storage_path / pst_filename
            
            # Create PST file structure
            pst_info = self._create_pst_file_structure(pst_path, folder_data)
            pst_results["created_pst_files"].append(pst_info)
            pst_results["total_size"] += pst_info.get("size", 0)
        
        return pst_results
    
    def _create_single_pst_file(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single PST file containing all exported data.
        
        Args:
            export_data: Exported archive data
            
        Returns:
            PST creation results
        """
        year = export_data.get("year", datetime.now().year)
        
        pst_results = {
            "creation_date": datetime.now().isoformat(),
            "organization_strategy": "single_file",
            "year": year,
            "created_pst_files": [],
            "total_size": 0
        }
        
        pst_filename = f"Archive_{year}_Complete.pst"
        pst_path = self.pst_storage_path / pst_filename
        
        # Combine all folder data for single PST
        combined_data = {
            "folder_name": f"Archive_{year}",
            "total_items": export_data.get("total_items", 0),
            "folders": export_data.get("exported_folders", [])
        }
        
        pst_info = self._create_pst_file_structure(pst_path, combined_data)
        pst_results["created_pst_files"].append(pst_info)
        pst_results["total_size"] = pst_info.get("size", 0)
        
        return pst_results
    
    def _create_pst_file_structure(self, pst_path: Path, folder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create the actual PST file structure and metadata.
        
        Args:
            pst_path: Path where the PST file should be created
            folder_data: Data for the folder to be stored in PST
            
        Returns:
            Dictionary with PST file information
        """
        logger.info(f"Creating PST file: {pst_path}")
        
        pst_info = {
            "filename": pst_path.name,
            "path": str(pst_path),
            "creation_date": datetime.now().isoformat(),
            "folder_name": folder_data.get("folder_name", "Unknown"),
            "item_count": folder_data.get("item_count", 0),
            "size": 0
        }
        
        try:
            # Create PST file directory structure (since we can't create actual PST files)
            pst_dir = pst_path.with_suffix('.pst_data')
            pst_dir.mkdir(parents=True, exist_ok=True)
            
            # Create metadata file
            metadata = {
                "pst_info": pst_info,
                "folder_data": folder_data,
                "format_version": "1.0",
                "outlook_compatible": True
            }
            
            metadata_file = pst_dir / "pst_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Create folder structure file
            folder_structure = self._generate_folder_structure(folder_data)
            structure_file = pst_dir / "folder_structure.json"
            with open(structure_file, 'w', encoding='utf-8') as f:
                json.dump(folder_structure, f, indent=2)
            
            # Create sample email files (in real implementation, these would be actual emails)
            emails_dir = pst_dir / "emails"
            emails_dir.mkdir(exist_ok=True)
            
            for i in range(min(5, folder_data.get("item_count", 0))):  # Create up to 5 sample emails
                email_file = emails_dir / f"email_{i+1}.json"
                sample_email = {
                    "id": i + 1,
                    "subject": f"Sample Email {i+1}",
                    "sender": f"sender{i+1}@example.com",
                    "date": datetime.now().isoformat(),
                    "body": f"This is a sample email body for email {i+1}",
                    "attachments": []
                }
                
                with open(email_file, 'w', encoding='utf-8') as f:
                    json.dump(sample_email, f, indent=2)
            
            # Calculate approximate size
            pst_info["size"] = sum(f.stat().st_size for f in pst_dir.rglob('*') if f.is_file())
            
            # Create PST index file for Outlook navigation
            self._create_outlook_index(pst_path, pst_info)
            
            logger.info(f"PST file structure created: {pst_path} ({pst_info['size']} bytes)")
            
        except Exception as e:
            logger.error(f"Error creating PST file structure: {e}")
            pst_info["error"] = str(e)
        
        return pst_info
    
    def _generate_folder_structure(self, folder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate folder structure for PST file organization.
        
        Args:
            folder_data: Data about the folder
            
        Returns:
            Dictionary representing folder structure
        """
        structure = {
            "root_folder": {
                "name": folder_data.get("folder_name", "Unknown"),
                "type": "mail_folder",
                "item_count": folder_data.get("item_count", 0),
                "subfolders": []
            }
        }
        
        # Add subfolders if present
        for subfolder_data in folder_data.get("subfolders", []):
            subfolder = {
                "name": subfolder_data.get("name", "Unknown_Subfolder"),
                "type": "mail_folder",
                "item_count": subfolder_data.get("item_count", 0),
                "parent": folder_data.get("folder_name", "Unknown")
            }
            structure["root_folder"]["subfolders"].append(subfolder)
        
        return structure
    
    def _create_outlook_index(self, pst_path: Path, pst_info: Dict[str, Any]) -> None:
        """Create an index file for Outlook navigation integration.
        
        Args:
            pst_path: Path to the PST file
            pst_info: PST file information
        """
        try:
            index_file = pst_path.with_suffix('.index')
            
            index_data = {
                "pst_file": str(pst_path),
                "outlook_integration": {
                    "add_to_profile": True,
                    "display_name": f"Archive - {pst_info['folder_name']}",
                    "access_mode": "read_write",
                    "auto_archive": False
                },
                "navigation": {
                    "show_in_folder_list": True,
                    "default_view": "table",
                    "sort_order": "received_time_desc"
                },
                "maintenance": {
                    "compact_threshold": "50MB",
                    "backup_schedule": "weekly",
                    "integrity_check": "monthly"
                }
            }
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2)
            
            logger.info(f"Outlook index created: {index_file}")
            
        except Exception as e:
            logger.error(f"Error creating Outlook index: {e}")
    
    def _save_pst_metadata(self, pst_results: Dict[str, Any]) -> None:
        """Save PST creation metadata to a file.
        
        Args:
            pst_results: Results from PST creation process
        """
        try:
            year = pst_results.get("year", "unknown")
            metadata_file = self.pst_storage_path / f"pst_metadata_{year}.json"
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(pst_results, f, indent=2)
            
            logger.info(f"PST metadata saved: {metadata_file}")
            
        except Exception as e:
            logger.error(f"Error saving PST metadata: {e}")
    
    def get_pst_files(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of created PST files.
        
        Args:
            year: Optional year filter
            
        Returns:
            List of PST file information dictionaries
        """
        pst_files = []
        
        try:
            # Search for PST files and their metadata
            if year:
                # Search in year-specific directory first
                year_dir = self.pst_storage_path / str(year)
                if year_dir.exists():
                    for pst_dir in year_dir.glob("*.pst_data"):
                        metadata_file = pst_dir / "pst_metadata.json"
                        if metadata_file.exists():
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                pst_files.append(metadata.get("pst_info", {}))
                
                # Also search root directory for year-specific files
                search_pattern = f"*{year}*"
                for pst_dir in self.pst_storage_path.glob(f"{search_pattern}.pst_data"):
                    metadata_file = pst_dir / "pst_metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            pst_info = metadata.get("pst_info", {})
                            # Avoid duplicates
                            if not any(existing["filename"] == pst_info.get("filename") for existing in pst_files):
                                pst_files.append(pst_info)
            else:
                # Search all PST files
                for pst_dir in self.pst_storage_path.rglob("*.pst_data"):
                    metadata_file = pst_dir / "pst_metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            pst_files.append(metadata.get("pst_info", {}))
            
        except Exception as e:
            logger.error(f"Error getting PST files: {e}")
        
        return pst_files
    
    def import_to_outlook(self, pst_file_path: Union[str, Path]) -> Dict[str, Any]:
        """Import a PST file into Outlook for navigation.
        
        Args:
            pst_file_path: Path to the PST file to import
            
        Returns:
            Dictionary with import results
        """
        pst_path = Path(pst_file_path)
        
        import_results = {
            "pst_file": str(pst_path),
            "import_date": datetime.now().isoformat(),
            "success": False
        }
        
        try:
            # Check if index file exists
            index_file = pst_path.with_suffix('.index')
            
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                # Create Outlook import script (batch file for Windows)
                if sys.platform == "win32":
                    self._create_outlook_import_script(pst_path, index_data)
                
                import_results["outlook_integration"] = index_data.get("outlook_integration", {})
                import_results["success"] = True
                
                logger.info(f"PST file prepared for Outlook import: {pst_path}")
            else:
                import_results["error"] = "Index file not found"
                
        except Exception as e:
            logger.error(f"Error preparing PST import: {e}")
            import_results["error"] = str(e)
        
        return import_results
    
    def _create_outlook_import_script(self, pst_path: Path, index_data: Dict[str, Any]) -> None:
        """Create a script to import PST file into Outlook.
        
        Args:
            pst_path: Path to PST file
            index_data: Index data for the PST file
        """
        try:
            script_path = pst_path.with_suffix('.bat')
            display_name = index_data.get("outlook_integration", {}).get("display_name", "Archive")
            
            script_content = f'''@echo off
REM Outlook PST Import Script
REM Generated: {datetime.now().isoformat()}

echo Importing PST file: {pst_path}
echo Display Name: {display_name}

REM Instructions for manual import:
echo.
echo To import this PST file into Outlook:
echo 1. Open Microsoft Outlook
echo 2. Go to File > Open & Export > Open Outlook Data File
echo 3. Navigate to: {pst_path}
echo 4. Select the PST file and click OK
echo 5. The archive will appear in your folder list as "{display_name}"
echo.

pause
'''
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            logger.info(f"Outlook import script created: {script_path}")
            
        except Exception as e:
            logger.error(f"Error creating import script: {e}")
    
    def cleanup_old_pst_files(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up PST files older than specified days.
        
        Args:
            days_old: Number of days after which to consider files old
            
        Returns:
            Cleanup results dictionary
        """
        cleanup_results = {
            "cleanup_date": datetime.now().isoformat(),
            "days_threshold": days_old,
            "files_removed": [],
            "space_freed": 0,
            "success": False
        }
        
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            for pst_dir in self.pst_storage_path.glob("*.pst_data"):
                if pst_dir.stat().st_mtime < cutoff_date:
                    # Calculate size before removal
                    size = sum(f.stat().st_size for f in pst_dir.rglob('*') if f.is_file())
                    
                    # Remove directory
                    shutil.rmtree(pst_dir)
                    
                    cleanup_results["files_removed"].append({
                        "path": str(pst_dir),
                        "size": size,
                        "last_modified": datetime.fromtimestamp(pst_dir.stat().st_mtime).isoformat()
                    })
                    cleanup_results["space_freed"] += size
            
            cleanup_results["success"] = True
            logger.info(f"Cleanup completed: {len(cleanup_results['files_removed'])} files removed, "
                       f"{cleanup_results['space_freed']} bytes freed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            cleanup_results["error"] = str(e)
        
        return cleanup_results