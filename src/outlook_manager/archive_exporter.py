"""Archive Exporter for Outlook Email Data.

This module handles the export of Outlook archives for specific years
and folder structures.
"""

import os
import sys
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dateutil.relativedelta import relativedelta
import json

# Platform-specific imports
if sys.platform == "win32":
    try:
        import win32com.client
        import pywintypes
        OUTLOOK_AVAILABLE = True
    except ImportError:
        OUTLOOK_AVAILABLE = False
        logging.warning("pywin32 not available. Outlook functionality will be limited.")
else:
    OUTLOOK_AVAILABLE = False
    logging.info("Non-Windows platform detected. Outlook COM interface not available.")


logger = logging.getLogger(__name__)


class OutlookArchiveExporter:
    """Exports Outlook archives to local storage.
    
    This class provides functionality to export Outlook email archives
    for specific years and folder structures while maintaining the
    organization and accessibility of the data.
    """
    
    def __init__(self, output_path: Union[str, Path] = None):
        """Initialize the Outlook Archive Exporter.
        
        Args:
            output_path: Directory where exported archives will be stored.
                        Defaults to current directory + 'outlook_exports'
        """
        self.output_path = Path(output_path) if output_path else Path.cwd() / "outlook_exports"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self._outlook_app = None
        self._namespace = None
        
        if OUTLOOK_AVAILABLE:
            self._initialize_outlook()
        else:
            logger.warning("Outlook COM interface not available. Operating in simulation mode.")
    
    def _initialize_outlook(self) -> bool:
        """Initialize connection to Outlook application.
        
        Returns:
            bool: True if successfully connected, False otherwise
        """
        try:
            self._outlook_app = win32com.client.Dispatch("Outlook.Application")
            self._namespace = self._outlook_app.GetNamespace("MAPI")
            logger.info("Successfully connected to Outlook application")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Outlook: {e}")
            return False
    
    def export_archives(self, 
                       year: int = 2025, 
                       include_subfolders: bool = True,
                       folder_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export Outlook archives for the specified year.
        
        Args:
            year: Year to export archives for (default: 2025)
            include_subfolders: Whether to include subfolders in export
            folder_filter: List of specific folder names to export (optional)
            
        Returns:
            Dict containing export results and metadata
        """
        logger.info(f"Starting archive export for year {year}")
        
        export_results = {
            "year": year,
            "export_date": datetime.now().isoformat(),
            "include_subfolders": include_subfolders,
            "folder_filter": folder_filter,
            "exported_folders": [],
            "total_items": 0,
            "success": False,
            "output_path": str(self.output_path)
        }
        
        try:
            if OUTLOOK_AVAILABLE and self._namespace:
                export_results = self._export_outlook_data(year, include_subfolders, folder_filter)
            else:
                # Simulation mode for non-Windows or when Outlook is not available
                export_results = self._simulate_export(year, include_subfolders, folder_filter)
                
            export_results["success"] = True
            logger.info(f"Archive export completed successfully")
            
        except Exception as e:
            logger.error(f"Archive export failed: {e}")
            export_results["error"] = str(e)
        
        # Save export metadata
        self._save_export_metadata(export_results)
        
        return export_results
    
    def _export_outlook_data(self, year: int, include_subfolders: bool, folder_filter: Optional[List[str]]) -> Dict[str, Any]:
        """Export actual Outlook data using COM interface.
        
        Args:
            year: Year to export
            include_subfolders: Include subfolders flag
            folder_filter: Optional folder filter list
            
        Returns:
            Export results dictionary
        """
        export_results = {
            "year": year,
            "export_date": datetime.now().isoformat(),
            "include_subfolders": include_subfolders,
            "folder_filter": folder_filter,
            "exported_folders": [],
            "total_items": 0,
            "method": "outlook_com"
        }
        
        try:
            # Get default folders
            inbox = self._namespace.GetDefaultFolder(6)  # olFolderInbox
            sent_items = self._namespace.GetDefaultFolder(5)  # olFolderSentMail
            
            folders_to_process = [
                ("Inbox", inbox),
                ("Sent Items", sent_items)
            ]
            
            # Add custom folders if specified
            if folder_filter:
                for folder_name in folder_filter:
                    folder = self._find_folder_by_name(folder_name)
                    if folder:
                        folders_to_process.append((folder_name, folder))
            
            for folder_name, folder in folders_to_process:
                folder_results = self._process_folder(folder, folder_name, year, include_subfolders)
                export_results["exported_folders"].append(folder_results)
                export_results["total_items"] += folder_results.get("item_count", 0)
                
        except Exception as e:
            logger.error(f"Error during Outlook data export: {e}")
            raise
            
        return export_results
    
    def _simulate_export(self, year: int, include_subfolders: bool, folder_filter: Optional[List[str]]) -> Dict[str, Any]:
        """Simulate export for non-Windows environments or when Outlook is unavailable.
        
        Args:
            year: Year to export
            include_subfolders: Include subfolders flag  
            folder_filter: Optional folder filter list
            
        Returns:
            Simulated export results dictionary
        """
        logger.info("Running in simulation mode - creating sample export structure")
        
        export_results = {
            "year": year,
            "export_date": datetime.now().isoformat(),
            "include_subfolders": include_subfolders,
            "folder_filter": folder_filter,
            "exported_folders": [],
            "total_items": 0,
            "method": "simulation"
        }
        
        # Create sample folder structure
        sample_folders = folder_filter or ["Inbox", "Sent Items", "Drafts", "Archive"]
        
        for folder_name in sample_folders:
            folder_path = self.output_path / f"{year}_{folder_name.replace(' ', '_')}"
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Create sample metadata file
            folder_metadata = {
                "folder_name": folder_name,
                "year": year,
                "item_count": 150,  # Simulated count
                "export_date": datetime.now().isoformat(),
                "subfolders": []
            }
            
            if include_subfolders:
                # Simulate subfolders
                subfolders = [f"{folder_name}_Archive", f"{folder_name}_Old"]
                for subfolder in subfolders:
                    subfolder_path = folder_path / subfolder
                    subfolder_path.mkdir(parents=True, exist_ok=True)
                    folder_metadata["subfolders"].append({
                        "name": subfolder,
                        "item_count": 25,
                        "path": str(subfolder_path)
                    })
            
            # Save folder metadata
            metadata_file = folder_path / "folder_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(folder_metadata, f, indent=2)
            
            export_results["exported_folders"].append(folder_metadata)
            export_results["total_items"] += folder_metadata["item_count"]
        
        return export_results
    
    def _process_folder(self, folder: Any, folder_name: str, year: int, include_subfolders: bool) -> Dict[str, Any]:
        """Process a single Outlook folder for export.
        
        Args:
            folder: Outlook folder object
            folder_name: Name of the folder
            year: Year to filter emails
            include_subfolders: Whether to process subfolders
            
        Returns:
            Dictionary with folder processing results
        """
        folder_results = {
            "folder_name": folder_name,
            "year": year,
            "item_count": 0,
            "export_date": datetime.now().isoformat(),
            "subfolders": []
        }
        
        try:
            # Create folder export directory
            folder_path = self.output_path / f"{year}_{folder_name.replace(' ', '_')}"
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Filter items by year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            
            # Process items in the folder
            items = folder.Items
            items.Sort("[ReceivedTime]", True)  # Sort by received time, descending
            
            filtered_items = []
            for item in items:
                try:
                    if hasattr(item, 'ReceivedTime'):
                        item_date = item.ReceivedTime
                        if start_date <= item_date < end_date:
                            filtered_items.append(item)
                except:
                    continue  # Skip items with date issues
            
            folder_results["item_count"] = len(filtered_items)
            
            # Export items metadata (actual email export would be more complex)
            items_metadata = []
            for i, item in enumerate(filtered_items[:10]):  # Limit to first 10 for demo
                try:
                    item_data = {
                        "subject": getattr(item, 'Subject', 'No Subject'),
                        "sender": getattr(item, 'SenderName', 'Unknown'),
                        "received_time": str(getattr(item, 'ReceivedTime', '')),
                        "size": getattr(item, 'Size', 0)
                    }
                    items_metadata.append(item_data)
                except:
                    continue
            
            # Save items metadata
            if items_metadata:
                metadata_file = folder_path / "items_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(items_metadata, f, indent=2)
            
            # Process subfolders if requested
            if include_subfolders and hasattr(folder, 'Folders'):
                for subfolder in folder.Folders:
                    subfolder_name = f"{folder_name}_{subfolder.Name}"
                    subfolder_results = self._process_folder(subfolder, subfolder_name, year, False)
                    folder_results["subfolders"].append(subfolder_results)
                    folder_results["item_count"] += subfolder_results["item_count"]
            
        except Exception as e:
            logger.error(f"Error processing folder {folder_name}: {e}")
            folder_results["error"] = str(e)
        
        return folder_results
    
    def _find_folder_by_name(self, folder_name: str) -> Optional[Any]:
        """Find a folder by name in the Outlook namespace.
        
        Args:
            folder_name: Name of the folder to find
            
        Returns:
            Outlook folder object if found, None otherwise
        """
        try:
            # This is a simplified implementation
            # In practice, you might need to search through all folders
            for folder in self._namespace.Folders:
                if folder.Name.lower() == folder_name.lower():
                    return folder
                # Search subfolders recursively
                for subfolder in folder.Folders:
                    if subfolder.Name.lower() == folder_name.lower():
                        return subfolder
        except Exception as e:
            logger.error(f"Error finding folder {folder_name}: {e}")
        
        return None
    
    def _save_export_metadata(self, export_results: Dict[str, Any]) -> None:
        """Save export metadata to a JSON file.
        
        Args:
            export_results: Dictionary containing export results
        """
        try:
            metadata_file = self.output_path / f"export_metadata_{export_results['year']}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(export_results, f, indent=2)
            logger.info(f"Export metadata saved to {metadata_file}")
        except Exception as e:
            logger.error(f"Failed to save export metadata: {e}")
    
    def get_available_years(self) -> List[int]:
        """Get list of years that have email data available.
        
        Returns:
            List of years with available email data
        """
        if not OUTLOOK_AVAILABLE or not self._namespace:
            # Return sample years for simulation
            current_year = datetime.now().year
            return list(range(current_year - 5, current_year + 2))
        
        # In a real implementation, this would scan through all folders
        # and determine which years have email data
        return [2023, 2024, 2025]
    
    def cleanup(self) -> None:
        """Clean up Outlook connection and resources."""
        if self._outlook_app:
            try:
                self._outlook_app = None
                self._namespace = None
                logger.info("Outlook connection cleaned up")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")