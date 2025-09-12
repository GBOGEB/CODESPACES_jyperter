# Outlook Manager Tests

This directory contains test files for the Outlook archive management functionality.

## Test Structure

- `test_outlook_manager.py` - Main test suite covering all modules
  - OutlookArchiveExporter tests
  - PSTFileManager tests  
  - NavigationManager tests
  - Integration tests
  - Error handling tests

## Running Tests

Run all outlook manager tests:
```bash
python -m pytest tests/outlook_manager/ -v
```

Run specific test class:
```bash
python -m pytest tests/outlook_manager/test_outlook_manager.py::TestOutlookArchiveExporter -v
```

Run with coverage:
```bash
python -m pytest tests/outlook_manager/ --cov=src.outlook_manager --cov-report=html
```