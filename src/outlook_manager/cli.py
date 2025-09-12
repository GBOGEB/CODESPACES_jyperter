"""Outlook Archive Management CLI.

Command-line interface for managing Outlook email archives, creating PST files,
and setting up navigation integration.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .archive_exporter import OutlookArchiveExporter
from .pst_manager import PSTFileManager
from .navigation_manager import NavigationManager


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.
    
    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('outlook_archive.log')
        ]
    )


def export_archives_command(args: argparse.Namespace) -> None:
    """Handle the export archives command.
    
    Args:
        args: Parsed command line arguments
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Exporting archives for year {args.year}")
    
    exporter = OutlookArchiveExporter(args.output_path)
    
    try:
        results = exporter.export_archives(
            year=args.year,
            include_subfolders=args.include_subfolders,
            folder_filter=args.folders
        )
        
        if results.get("success"):
            print(f"✓ Archive export completed successfully")
            print(f"  Year: {results['year']}")
            print(f"  Folders exported: {len(results['exported_folders'])}")
            print(f"  Total items: {results['total_items']}")
            if 'output_path' in results:
                print(f"  Output path: {results['output_path']}")
            else:
                print(f"  Output path: {exporter.output_path}")
        else:
            print(f"✗ Archive export failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Export failed: {e}")
        print(f"✗ Export failed: {e}")
        sys.exit(1)
    finally:
        exporter.cleanup()


def create_pst_command(args: argparse.Namespace) -> None:
    """Handle the create PST files command.
    
    Args:
        args: Parsed command line arguments
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Creating PST files from export data")
    
    # Load export data
    export_metadata_file = Path(args.export_path) / f"export_metadata_{args.year}.json"
    
    if not export_metadata_file.exists():
        print(f"✗ Export metadata not found: {export_metadata_file}")
        print("  Please run the export command first.")
        sys.exit(1)
    
    try:
        import json
        with open(export_metadata_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
    except Exception as e:
        print(f"✗ Failed to load export data: {e}")
        sys.exit(1)
    
    pst_manager = PSTFileManager(args.pst_path)
    
    try:
        results = pst_manager.create_pst_files(
            export_data,
            args.organization
        )
        
        if results.get("success"):
            print(f"✓ PST files created successfully")
            print(f"  Organization: {results['organization_strategy']}")
            print(f"  Files created: {len(results['created_pst_files'])}")
            print(f"  Total size: {results['total_size']} bytes")
            
            for pst_file in results['created_pst_files']:
                print(f"    - {pst_file['filename']} ({pst_file['item_count']} items)")
        else:
            print(f"✗ PST creation failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"PST creation failed: {e}")
        print(f"✗ PST creation failed: {e}")
        sys.exit(1)


def setup_navigation_command(args: argparse.Namespace) -> None:
    """Handle the setup navigation command.
    
    Args:
        args: Parsed command line arguments
    """
    logger = logging.getLogger(__name__)
    logger.info("Setting up Outlook navigation integration")
    
    # Get PST files
    pst_manager = PSTFileManager(args.pst_path)
    pst_files = pst_manager.get_pst_files(args.year)
    
    if not pst_files:
        print(f"✗ No PST files found for year {args.year}")
        print("  Please create PST files first using the create-pst command.")
        sys.exit(1)
    
    nav_manager = NavigationManager(args.archive_path)
    
    try:
        results = nav_manager.setup_outlook_integration(
            pst_files,
            args.integration_mode
        )
        
        if results.get("success"):
            print(f"✓ Navigation setup completed successfully")
            print(f"  Integration mode: {results['integration_mode']}")
            print(f"  Navigation shortcuts: {len(results['navigation_shortcuts'])}")
            print(f"  Search index created: {'search_index' in results}")
            
            if sys.platform == "win32":
                print(f"  Outlook profile configuration: Available")
                print("  Run the generated setup script to complete Outlook integration.")
            else:
                print("  Note: Full Outlook integration requires Windows platform.")
        else:
            print(f"✗ Navigation setup failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Navigation setup failed: {e}")
        print(f"✗ Navigation setup failed: {e}")
        sys.exit(1)


def search_command(args: argparse.Namespace) -> None:
    """Handle the search archives command.
    
    Args:
        args: Parsed command line arguments
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Searching archives for: {args.query}")
    
    nav_manager = NavigationManager(args.archive_path)
    
    date_range = None
    if args.start_date or args.end_date:
        date_range = {}
        if args.start_date:
            date_range["start"] = args.start_date
        if args.end_date:
            date_range["end"] = args.end_date
    
    try:
        results = nav_manager.search_archives(
            args.query,
            args.search_type,
            date_range
        )
        
        if "error" in results:
            print(f"✗ Search failed: {results['error']}")
            sys.exit(1)
        
        print(f"✓ Search completed in {results['search_time_ms']}ms")
        print(f"  Query: '{results['query']}' (type: {results['search_type']})")
        print(f"  Results found: {results['total_found']}")
        
        if results['total_found'] > 0:
            print("\nTop results:")
            for i, result in enumerate(results['results'][:10], 1):
                print(f"  {i}. {result['subject']}")
                print(f"     From: {result['sender']}")
                print(f"     Date: {result['date']}")
                print(f"     Folder: {result['folder']}")
                if result.get('has_attachments'):
                    print(f"     📎 Has attachments")
                print()
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        print(f"✗ Search failed: {e}")
        sys.exit(1)


def status_command(args: argparse.Namespace) -> None:
    """Handle the status command.
    
    Args:
        args: Parsed command line arguments
    """
    print("Outlook Archive Management Status")
    print("=" * 40)
    
    try:
        # Check export status
        export_path = Path(args.export_path or "outlook_exports")
        if export_path.exists():
            export_files = list(export_path.glob("export_metadata_*.json"))
            print(f"✓ Export data: {len(export_files)} years available")
            for export_file in sorted(export_files):
                year = export_file.stem.split("_")[-1]
                print(f"    - Year {year}")
        else:
            print("✗ No export data found")
        
        # Check PST files
        pst_path = Path(args.pst_path or "pst_files")
        if pst_path.exists():
            pst_files = list(pst_path.glob("*.pst_data"))
            print(f"✓ PST files: {len(pst_files)} files created")
        else:
            print("✗ No PST files found")
        
        # Check navigation setup
        nav_manager = NavigationManager(args.archive_path)
        nav_status = nav_manager.get_navigation_status()
        
        if nav_status.get("integration_ready"):
            print("✓ Navigation: Integration ready")
            print(f"    - Mapped folders: {nav_status.get('mapped_folders', 0)}")
            print(f"    - Indexed folders: {nav_status.get('indexed_folders', 0)}")
        else:
            print("✗ Navigation: Not configured")
        
        print(f"✓ Platform: {sys.platform}")
        if sys.platform == "win32":
            print("✓ Outlook integration: Available")
        else:
            print("⚠ Outlook integration: Limited (non-Windows platform)")
    
    except Exception as e:
        print(f"✗ Status check failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Outlook Archive Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export 2025 archives with subfolders
  python -m outlook_manager export --year 2025 --include-subfolders
  
  # Create PST files organized by year and folder
  python -m outlook_manager create-pst --year 2025 --organization by_year_folder
  
  # Setup Outlook navigation integration
  python -m outlook_manager setup-navigation --year 2025 --integration-mode hybrid
  
  # Search archived emails
  python -m outlook_manager search "project meeting" --search-type subject
  
  # Check system status
  python -m outlook_manager status
        """
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export Outlook archives")
    export_parser.add_argument(
        "--year", type=int, default=2025,
        help="Year to export (default: 2025)"
    )
    export_parser.add_argument(
        "--output-path", type=str,
        help="Output directory for exported data"
    )
    export_parser.add_argument(
        "--include-subfolders", action="store_true",
        help="Include subfolders in export"
    )
    export_parser.add_argument(
        "--folders", nargs="*",
        help="Specific folders to export (default: all)"
    )
    
    # Create PST command
    pst_parser = subparsers.add_parser("create-pst", help="Create PST files from exported data")
    pst_parser.add_argument(
        "--year", type=int, default=2025,
        help="Year of export data to process (default: 2025)"
    )
    pst_parser.add_argument(
        "--export-path", type=str, default="outlook_exports",
        help="Path to exported data"
    )
    pst_parser.add_argument(
        "--pst-path", type=str,
        help="Output directory for PST files"
    )
    pst_parser.add_argument(
        "--organization", choices=["by_year_folder", "by_folder", "single_file"],
        default="by_year_folder",
        help="How to organize PST files"
    )
    
    # Setup navigation command
    nav_parser = subparsers.add_parser("setup-navigation", help="Setup Outlook navigation integration")
    nav_parser.add_argument(
        "--year", type=int, default=2025,
        help="Year of PST files to integrate (default: 2025)"
    )
    nav_parser.add_argument(
        "--pst-path", type=str, default="pst_files",
        help="Path to PST files"
    )
    nav_parser.add_argument(
        "--archive-path", type=str,
        help="Path for archive navigation data"
    )
    nav_parser.add_argument(
        "--integration-mode", choices=["online", "offline", "hybrid"],
        default="hybrid",
        help="Integration mode with Outlook"
    )
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search archived emails")
    search_parser.add_argument(
        "query",
        help="Search query"
    )
    search_parser.add_argument(
        "--archive-path", type=str, default="email_archives",
        help="Path to archive navigation data"
    )
    search_parser.add_argument(
        "--search-type", choices=["all", "subject", "sender", "content"],
        default="all",
        help="Type of search to perform"
    )
    search_parser.add_argument(
        "--start-date", type=str,
        help="Start date filter (YYYY-MM-DD)"
    )
    search_parser.add_argument(
        "--end-date", type=str,
        help="End date filter (YYYY-MM-DD)"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument(
        "--export-path", type=str, default="outlook_exports",
        help="Path to check for export data"
    )
    status_parser.add_argument(
        "--pst-path", type=str, default="pst_files",
        help="Path to check for PST files"
    )
    status_parser.add_argument(
        "--archive-path", type=str, default="email_archives",
        help="Path to check for navigation data"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    setup_logging(args.verbose)
    
    # Route to appropriate command handler
    if args.command == "export":
        export_archives_command(args)
    elif args.command == "create-pst":
        create_pst_command(args)
    elif args.command == "setup-navigation":
        setup_navigation_command(args)
    elif args.command == "search":
        search_command(args)
    elif args.command == "status":
        status_command(args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()