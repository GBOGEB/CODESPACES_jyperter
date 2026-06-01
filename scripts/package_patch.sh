#!/usr/bin/env bash
# Package a self-contained *.patch.md into a handover bundle.
#
# Usage:
#   scripts/package_patch.sh validate <patch.md>
#   scripts/package_patch.sh bundle   <patch.md> [out_dir]
#   scripts/package_patch.sh zip      <patch.md> [out_dir]
#
# The patch markdown file is the canonical source of truth. "bundle" assembles
# a handover directory (patch + extracted manifest + index), and "zip" packs
# that bundle into a zip archive. "validate" checks structural completeness.
set -euo pipefail

REQUIRED_SECTIONS=(
  "## Metadata"
  "## 1. Intent"
  "## 2. Repository Context"
  "## 3. Problem Statement"
  "## 5. Artifact Classification"
  "## 6. Refactor Constraints"
  "## 8. Patch Plan"
  "## 11. Build / Package"
  "## 12. Validation"
  "## 14. Rollback"
  "## 15. Handover / Operational Manifest"
  "### Embedded Manifest"
)

die() { echo "error: $*" >&2; exit 1; }

extract_manifest() {
  # Print the YAML block that immediately follows "### Embedded Manifest".
  local patch="$1"
  awk '
    /^### Embedded Manifest/ { found=1; next }
    found && /^```yaml/ { infence=1; next }
    found && infence && /^```/ { exit }
    found && infence { print }
  ' "$patch"
}

cmd_validate() {
  local patch="$1"
  [ -f "$patch" ] || die "patch file not found: $patch"
  local missing=0
  for section in "${REQUIRED_SECTIONS[@]}"; do
    if ! grep -qF "$section" "$patch"; then
      echo "missing section: $section" >&2
      missing=1
    fi
  done
  local manifest
  manifest="$(extract_manifest "$patch")"
  [ -n "$manifest" ] || die "embedded manifest is empty or missing"
  # Frozen files must not appear as move targets/sources.
  if grep -E '^(rename (from|to)|From:|To:).*\b(README|ADR|CHANGELOG)\b' "$patch" >/dev/null 2>&1; then
    die "frozen file (README/ADR/CHANGELOG) referenced in a move entry"
  fi
  [ "$missing" -eq 0 ] || die "patch package is missing required sections"
  echo "ok: $patch is a valid patch package"
}

cmd_bundle() {
  local patch="$1"
  local out_dir="${2:-handover/bundle}"
  cmd_validate "$patch"
  mkdir -p "$out_dir"
  cp "$patch" "$out_dir/"
  extract_manifest "$patch" > "$out_dir/manifest.yaml"
  local base
  base="$(basename "$patch")"
  cat > "$out_dir/patch-index.json" <<JSON
{
  "patch": "$base",
  "manifest": "manifest.yaml",
  "generated_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON
  echo "bundle assembled in $out_dir"
}

cmd_zip() {
  local patch="$1"
  local out_dir="${2:-handover/bundle}"
  cmd_bundle "$patch" "$out_dir"
  local zip_path="${out_dir%/}.zip"
  (cd "$(dirname "$out_dir")" && zip -qr "$(basename "$zip_path")" "$(basename "$out_dir")")
  echo "zip created at $zip_path"
}

main() {
  local sub="${1:-}"
  [ -n "$sub" ] || die "usage: $0 {validate|bundle|zip} <patch.md> [out_dir]"
  shift
  local patch="${1:-}"
  [ -n "$patch" ] || die "missing <patch.md> argument"
  shift || true
  case "$sub" in
    validate) cmd_validate "$patch" ;;
    bundle)   cmd_bundle "$patch" "$@" ;;
    zip)      cmd_zip "$patch" "$@" ;;
    *)        die "unknown subcommand: $sub" ;;
  esac
}

main "$@"
