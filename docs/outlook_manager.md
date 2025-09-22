# Outlook Archive Management

This module provides comprehensive functionality for managing Microsoft Outlook email archives, including exporting archives to PST files and maintaining navigation capabilities within Outlook while having offline copies stored locally.

## Features

- **Archive Export**: Export Outlook email archives for specific years and folder structures
- **PST File Creation**: Convert exported data to PST (Personal Storage Table) files
- **Navigation Integration**: Maintain email navigation in Outlook while having offline copies
- **Search Functionality**: Full-text search across archived email data
- **Cross-platform Support**: Works on Windows (with full Outlook integration) and other platforms (simulation mode)

## Quick Start

### 1. Export Outlook Archives

Export all email archives for 2025 including subfolders:

```bash
python -m src.outlook_manager.cli export --year 2025 --include-subfolders
```

Export specific folders only:

```bash
python -m src.outlook_manager.cli export --year 2025 --folders "Inbox" "Sent Items" "Archive"
```

### 2. Create PST Files

Create PST files organized by year and folder:

```bash
python -m src.outlook_manager.cli create-pst --year 2025 --organization by_year_folder
```

Create a single PST file containing all data:

```bash
python -m src.outlook_manager.cli create-pst --year 2025 --organization single_file
```

### 3. Setup Outlook Navigation

Configure hybrid integration (online/offline access):

```bash
python -m src.outlook_manager.cli setup-navigation --year 2025 --integration-mode hybrid
```

### 4. Search Archives

Search by subject:

```bash
python -m src.outlook_manager.cli search "project meeting" --search-type subject
```

Search with date range:

```bash
python -m src.outlook_manager.cli search "important" --start-date 2025-01-01 --end-date 2025-06-30
```

### 5. Check Status

View system status and configuration:

```bash
python -m src.outlook_manager.cli status
```

## Architecture

### Core Components

1. **OutlookArchiveExporter** (`archive_exporter.py`)
   - Connects to Outlook via COM interface (Windows)
   - Exports email data with folder structure preservation
   - Supports simulation mode for non-Windows platforms

2. **PSTFileManager** (`pst_manager.py`)
   - Creates PST-compatible file structures
   - Supports multiple organization strategies
   - Generates Outlook integration scripts

3. **NavigationManager** (`navigation_manager.py`)
   - Sets up folder mappings and navigation shortcuts
   - Creates search indices for offline access
   - Manages Outlook profile integration

### Integration Modes

- **Online**: Full access through Outlook with live data
- **Offline**: Local access only, read-only PST files
- **Hybrid**: Best of both worlds - Outlook navigation with offline copies

## Configuration

### Organization Strategies

When creating PST files, choose from:

- `by_year_folder`: Separate PST file for each folder within a year (recommended)
- `by_folder`: One PST file per folder across all years
- `single_file`: All data in one PST file

### Platform Considerations

#### Windows
- Full Outlook COM interface integration
- Automatic PST file registration with Outlook
- Native Outlook profile configuration

#### Linux/macOS
- Simulation mode with equivalent folder structures
- Manual import instructions for cross-platform use
- Full search and navigation capabilities

## File Structure

After running the complete workflow, you'll have:

```
project_root/
├── outlook_exports/           # Exported email data
│   ├── 2025_Inbox/
│   ├── 2025_Sent_Items/
│   └── export_metadata_2025.json
├── pst_files/                 # PST file structures
│   ├── 2025/
│   │   ├── 2025_Inbox.pst_data/
│   │   ├── 2025_Inbox.index
│   │   └── ...
│   └── pst_metadata_2025.json
└── email_archives/           # Navigation and search data
    ├── navigation_config.json
    ├── folder_mapping.json
    ├── search_index/
    └── setup_outlook_profile.bat  # Windows only
```

## API Usage

### Programmatic Usage

```python
from src.outlook_manager import OutlookArchiveExporter, PSTFileManager, NavigationManager

# Export archives
exporter = OutlookArchiveExporter("./exports")
export_results = exporter.export_archives(year=2025, include_subfolders=True)

# Create PST files
pst_manager = PSTFileManager("./pst_files")
pst_results = pst_manager.create_pst_files(export_results, "by_year_folder")

# Setup navigation
nav_manager = NavigationManager("./navigation")
pst_files = pst_manager.get_pst_files(2025)
nav_results = nav_manager.setup_outlook_integration(pst_files, "hybrid")

# Search archives
search_results = nav_manager.search_archives("meeting", "subject")
```

### Error Handling

The system includes comprehensive error handling:

- Graceful fallback to simulation mode when Outlook is unavailable
- Detailed error reporting with suggestions for resolution
- Safe handling of incomplete or corrupted data

### Logging

Enable verbose logging for troubleshooting:

```bash
python -m src.outlook_manager.cli export --year 2025 --verbose
```

Log files are created in the current directory as `outlook_archive.log`.

## Advanced Features

### Custom Folder Filters

Export only specific folders:

```python
exporter.export_archives(
    year=2025,
    folder_filter=["Important", "Projects", "Client Communications"]
)
```

### Date Range Searches

Search within specific date ranges:

```python
nav_manager.search_archives(
    query="budget",
    search_type="all",
    date_range={"start": "2025-01-01", "end": "2025-03-31"}
)
```

### Batch Operations

Process multiple years:

```bash
for year in 2023 2024 2025; do
    python -m src.outlook_manager.cli export --year $year --include-subfolders
    python -m src.outlook_manager.cli create-pst --year $year
done
```

## Troubleshooting

### Common Issues

1. **"Outlook COM interface not available"**
   - Solution: Install pywin32 on Windows or use simulation mode

2. **"No PST files found"**
   - Solution: Run export and create-pst commands first

3. **"Search index not found"**
   - Solution: Run setup-navigation command to rebuild indices

### Performance Considerations

- Large mailboxes (>1GB) may take several minutes to export
- PST file creation is IO-intensive; use fast storage
- Search indices improve query performance but require additional disk space

### Maintenance

Regular maintenance tasks:

```bash
# Cleanup old PST files (30+ days)
python -c "
from src.outlook_manager import PSTFileManager
pst_manager = PSTFileManager()
pst_manager.cleanup_old_pst_files(days_old=30)
"

# Rebuild search indices
python -m src.outlook_manager.cli setup-navigation --year 2025 --integration-mode hybrid
```

## Contributing

When contributing to this module:

1. Add tests for new functionality in `tests/outlook_manager/`
2. Update documentation for API changes
3. Test on both Windows and non-Windows platforms
4. Follow the existing code style and error handling patterns

## License

This module is part of the DMAIC Measure Phase project and follows the same MIT license terms.