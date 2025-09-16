# Dependency Management

This document explains the dependency management approach for the DMAIC Measure Phase project.

## Overview

The project uses pinned dependencies to ensure reproducible builds across all environments (development, CI, production).

## Files

- `requirements.txt` - Production dependencies with pinned versions
- `requirements-dev.txt` - Development dependencies 
- `pyproject.toml` - Package metadata and dependency specification
- `scripts/validate_dependencies.py` - Dependency validation tool

## Key Principles

### 1. Pinned Versions
All production dependencies use exact version pinning (`==`) instead of range constraints (`>=`).

**Example:**
```
# Good - pinned version
pandas==2.3.2

# Avoid - range constraint  
pandas>=2.1.0
```

### 2. Reproducible Builds
Pinned versions ensure the same packages are installed across:
- Developer machines
- CI/CD pipelines  
- Production deployments

### 3. Version Consistency
The same versions are specified in both `requirements.txt` and `pyproject.toml` to avoid conflicts.

## Updating Dependencies

### Adding New Dependencies
1. Install the package: `pip install package-name`
2. Pin the version in `requirements.txt`: `package-name==x.y.z`
3. Add to `pyproject.toml` dependencies list
4. Run validation: `python scripts/validate_dependencies.py`
5. Test the installation: `pip install -r requirements.txt`

### Upgrading Dependencies
1. Update the pinned version in `requirements.txt`
2. Update the version in `pyproject.toml`
3. Test compatibility with existing code
4. Run the full test suite
5. Validate: `python scripts/validate_dependencies.py`

## CI/CD Integration

The GitHub Actions workflow includes:
- Dependency caching based on requirements file hashes
- Automatic validation of dependency format
- Installation testing in clean environment

## Troubleshooting

### Cache Issues
If you encounter dependency conflicts in CI:
1. Check if `requirements.txt` has been updated
2. Clear GitHub Actions cache (workflows will rebuild)
3. Ensure all versions are properly pinned

### Version Conflicts
If packages have conflicting dependencies:
1. Use `pip check` to identify conflicts
2. Update to compatible versions
3. Consider using `pip-tools` for dependency resolution

### Installation Failures
1. Verify all packages exist on PyPI with specified versions
2. Check for platform-specific dependencies
3. Ensure Python version compatibility

## Tools

### Validation Script
```bash
python scripts/validate_dependencies.py
```

This script checks:
- Proper version pinning format
- Valid package names and versions
- Basic consistency between files

### Manual Validation
```bash
# Install in clean environment
pip install -r requirements.txt

# Check for conflicts
pip check

# List installed versions
pip freeze
```

## Best Practices

1. **Always pin versions** in requirements.txt
2. **Test installations** in clean environments
3. **Update regularly** but methodically
4. **Document changes** in commit messages
5. **Run validation** before committing changes