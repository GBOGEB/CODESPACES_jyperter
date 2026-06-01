.PHONY: lint test patch-validate patch-bundle handover-zip

# Default patch package (override with: make patch-validate PATCH=...)
PATCH ?= patches/2026-06-01_artifact-federation-refactor.patch.md

lint:
	flake8 src tests

test: lint
	pytest --cov=src --cov-report=term-missing

# Validate that a *.patch.md is a structurally complete patch package.
patch-validate:
	bash scripts/package_patch.sh validate $(PATCH)

# Assemble a handover bundle directory from a *.patch.md.
patch-bundle:
	bash scripts/package_patch.sh bundle $(PATCH)

# Produce a zip handover bundle from a *.patch.md.
handover-zip:
	bash scripts/package_patch.sh zip $(PATCH)
