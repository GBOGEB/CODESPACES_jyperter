#!/usr/bin/env bash
# Example script demonstrating CLI usage of the DMAIC measure-phase pipeline.
set -euo pipefail

python app/run_pipeline.py "$@"
