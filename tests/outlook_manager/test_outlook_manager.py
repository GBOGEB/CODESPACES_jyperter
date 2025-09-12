"""Tests for Outlook Archive Management functionality."""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from src.outlook_manager.archive_exporter import OutlookArchiveExporter
from src.outlook_manager.pst_manager import PSTFileManager
from src.outlook_manager.navigation_manager import NavigationManager


class TestOutlookArchiveExporter:
    """Test cases for OutlookArchiveExporter."""
    
    def test_initialization(self):
        """Test exporter initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = OutlookArchiveExporter(temp_dir)
            assert exporter.output_path == Path(temp_dir)
            assert exporter.output_path.exists()
    
    def test_export_archives_simulation_mode(self):
        """Test archive export in simulation mode (non-Windows or no Outlook)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = OutlookArchiveExporter(temp_dir)
            
            results = exporter.export_archives(
                year=2025,
                include_subfolders=True,
                folder_filter=["Inbox", "Sent Items"]
            )
            
            assert results["success"] is True
            assert results["year"] == 2025
            assert results["method"] == "simulation"
            assert len(results["exported_folders"]) == 2
            assert results["total_items"] > 0
            
            # Check that output files were created
            assert (Path(temp_dir) / "2025_Inbox").exists()
            assert (Path(temp_dir) / "2025_Sent_Items").exists()
            
            # Check metadata file
            metadata_file = Path(temp_dir) / "export_metadata_2025.json"
            assert metadata_file.exists()
    
    def test_get_available_years(self):
        """Test getting available years."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = OutlookArchiveExporter(temp_dir)
            years = exporter.get_available_years()
            
            assert isinstance(years, list)
            assert 2025 in years
            assert all(isinstance(year, int) for year in years)
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = OutlookArchiveExporter(temp_dir)
            # Should not raise an exception
            exporter.cleanup()


class TestPSTFileManager:
    """Test cases for PSTFileManager."""
    
    def test_initialization(self):
        """Test PST manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pst_manager = PSTFileManager(temp_dir)
            assert pst_manager.pst_storage_path == Path(temp_dir)
            assert pst_manager.pst_storage_path.exists()
    
    def test_create_pst_files_by_year_folder(self):
        """Test PST file creation with by_year_folder organization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pst_manager = PSTFileManager(temp_dir)
            
            # Sample export data
            export_data = {
                "year": 2025,
                "export_date": datetime.now().isoformat(),
                "exported_folders": [
                    {
                        "folder_name": "Inbox",
                        "item_count": 100,
                        "subfolders": [
                            {"name": "Inbox_Archive", "item_count": 25}
                        ]
                    },
                    {
                        "folder_name": "Sent Items",
                        "item_count": 50,
                        "subfolders": []
                    }
                ],
                "total_items": 175
            }
            
            results = pst_manager.create_pst_files(export_data, "by_year_folder")
            
            assert results["success"] is True
            assert results["organization_strategy"] == "by_year_folder"
            assert len(results["created_pst_files"]) == 3  # 2 main folders + 1 subfolder
            
            # Check that PST data directories were created
            year_dir = Path(temp_dir) / "2025"
            assert year_dir.exists()
            assert (year_dir / "2025_Inbox.pst_data").exists()
            assert (year_dir / "2025_Sent_Items.pst_data").exists()
    
    def test_create_pst_files_single_file(self):
        """Test PST file creation with single_file organization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pst_manager = PSTFileManager(temp_dir)
            
            export_data = {
                "year": 2025,
                "exported_folders": [
                    {"folder_name": "Inbox", "item_count": 100}
                ],
                "total_items": 100
            }
            
            results = pst_manager.create_pst_files(export_data, "single_file")
            
            assert results["success"] is True
            assert results["organization_strategy"] == "single_file"
            assert len(results["created_pst_files"]) == 1
            
            # Check that PST data directory was created
            assert (Path(temp_dir) / "Archive_2025_Complete.pst_data").exists()
    
    def test_get_pst_files(self):
        """Test getting PST files list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pst_manager = PSTFileManager(temp_dir)
            
            # Create sample PST data
            pst_data_dir = Path(temp_dir) / "test.pst_data"
            pst_data_dir.mkdir()
            
            metadata = {
                "pst_info": {
                    "filename": "test.pst",
                    "folder_name": "Test",
                    "item_count": 10
                }
            }
            
            with open(pst_data_dir / "pst_metadata.json", 'w') as f:
                json.dump(metadata, f)
            
            pst_files = pst_manager.get_pst_files()
            assert len(pst_files) == 1
            assert pst_files[0]["filename"] == "test.pst"
    
    def test_import_to_outlook(self):
        """Test preparing PST file for Outlook import."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pst_manager = PSTFileManager(temp_dir)
            
            # Create sample PST with index
            pst_path = Path(temp_dir) / "test.pst"
            index_path = pst_path.with_suffix('.index')
            
            index_data = {
                "outlook_integration": {
                    "display_name": "Test Archive"
                }
            }
            
            with open(index_path, 'w') as f:
                json.dump(index_data, f)
            
            results = pst_manager.import_to_outlook(pst_path)
            
            assert results["success"] is True
            assert "outlook_integration" in results


class TestNavigationManager:
    """Test cases for NavigationManager."""
    
    def test_initialization(self):
        """Test navigation manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nav_manager = NavigationManager(temp_dir)
            assert nav_manager.archive_root == Path(temp_dir)
            assert nav_manager.archive_root.exists()
            
            # Check that config file was created
            assert nav_manager.navigation_config_file.exists()
    
    def test_setup_outlook_integration(self):
        """Test setting up Outlook integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nav_manager = NavigationManager(temp_dir)
            
            pst_files = [
                {
                    "filename": "test.pst",
                    "folder_name": "Inbox",
                    "item_count": 100,
                    "path": "/path/to/test.pst"
                }
            ]
            
            results = nav_manager.setup_outlook_integration(pst_files, "hybrid")
            
            assert results["success"] is True
            assert results["integration_mode"] == "hybrid"
            assert len(results["navigation_shortcuts"]) > 0
            assert "folder_mappings" in results
            
            # Check that mapping file was created
            assert nav_manager.folder_mapping_file.exists()
    
    def test_search_archives(self):
        """Test searching archived emails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nav_manager = NavigationManager(temp_dir)
            
            # Set up search index first
            pst_files = [
                {
                    "filename": "test.pst",
                    "folder_name": "Inbox", 
                    "item_count": 10,
                    "path": "/path/to/test.pst"
                }
            ]
            
            nav_manager.setup_outlook_integration(pst_files, "hybrid")
            
            # Perform search
            results = nav_manager.search_archives("Sample", "subject")
            
            assert "query" in results
            assert "results" in results
            assert "total_found" in results
            assert "search_time_ms" in results
    
    def test_get_navigation_status(self):
        """Test getting navigation status."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nav_manager = NavigationManager(temp_dir)
            
            status = nav_manager.get_navigation_status()
            
            assert "check_date" in status
            assert "navigation_config" in status
            assert "archive_root" in status
            assert "integration_ready" in status
    
    def test_rebuild_navigation(self):
        """Test rebuilding navigation indices."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nav_manager = NavigationManager(temp_dir)
            
            pst_files = [
                {
                    "filename": "test.pst",
                    "folder_name": "Inbox",
                    "item_count": 100,
                    "path": "/path/to/test.pst"
                }
            ]
            
            results = nav_manager.rebuild_navigation(pst_files)
            
            assert results["success"] is True
            assert "folder_mappings" in results
            assert "search_index" in results


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_complete_workflow(self):
        """Test the complete archive, PST creation, and navigation setup workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            
            # Step 1: Export archives
            exporter = OutlookArchiveExporter(base_path / "exports")
            export_results = exporter.export_archives(
                year=2025,
                include_subfolders=True,
                folder_filter=["Inbox", "Sent Items"]
            )
            
            assert export_results["success"] is True
            
            # Step 2: Create PST files
            pst_manager = PSTFileManager(base_path / "pst_files")
            pst_results = pst_manager.create_pst_files(export_results, "by_year_folder")
            
            assert pst_results["success"] is True
            
            # Step 3: Setup navigation
            nav_manager = NavigationManager(base_path / "navigation")
            pst_files = pst_manager.get_pst_files(2025)
            nav_results = nav_manager.setup_outlook_integration(pst_files, "hybrid")
            
            assert nav_results["success"] is True
            
            # Step 4: Test search
            search_results = nav_manager.search_archives("Sample", "all")
            assert "results" in search_results
            
            # Cleanup
            exporter.cleanup()
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test PST creation with invalid export data
            pst_manager = PSTFileManager(temp_dir)
            
            invalid_export_data = {}  # Empty/invalid data
            results = pst_manager.create_pst_files(invalid_export_data, "by_year_folder")
            
            # Should handle gracefully
            assert "success" in results
            
            # Test navigation setup with empty PST files
            nav_manager = NavigationManager(temp_dir)
            nav_results = nav_manager.setup_outlook_integration([], "hybrid")
            
            assert "success" in nav_results


if __name__ == "__main__":
    pytest.main([__file__])