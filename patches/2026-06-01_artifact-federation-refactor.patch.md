# Patch Package: Artifact Federation Refactor

> Single, self-contained Markdown patch package. This file is the **canonical
> source of truth**. It doubles as a patch description, architecture decision
> note, migration manifest, handover artifact, packaging recipe, and local
> integration guide. Supporting files (`manifest/`, `scripts/`, `Makefile`
> targets) are generated from or validated against this document.

## Metadata
- Repository: GBOGEB/anthropic
- Repository ID: 1255640890
- Patch Version: v0.1.0
- Patch Date: 2026-06-01
- Patch Type: architecture / artifact-governance / handover
- Baseline Ref: `<branch-or-commit>`
- Output Mode: single-file self-contained patch manifest

## 1. Intent
- **Scope**: Establish a repository output contract for `GBOGEB/anthropic` so
  that architectural refactors are delivered as one fully-contained
  `*.patch.md` package with optional local packaging.
- **Reason**: The repository should act as a **governance / custodian layer**,
  not a runtime or primitive library. Refactors must be reviewable,
  versionable, diffable, archivable, and convertible into a handover bundle.
- **Non-goals**:
  - No implementation-heavy runtime code in this package.
  - No automatic cross-repo semantic moves.
  - No conceptual reassignment of artifacts without human review.

## 2. Repository Context
- Repo name: `GBOGEB/anthropic`
- Repo id: `1255640890`
- Branch / baseline: `<branch-or-commit>`
- Artifact lineage / version: `artifact-federation@v0.1.0`

## 3. Problem Statement
- **Architectural concern**: Artifact ownership and movement are currently
  ambiguous; there is no single contract describing how artifacts are
  classified, where they live, and who owns them.
- **Current ambiguity**: Schema, parser, runtime, policy, taxonomy, federation
  contract, and governance artifacts are not consistently separated, so moves
  risk drifting concepts across repositories.
- **Ownership assumptions**: `anthropic` owns governance, taxonomy, and
  federation contracts; downstream repos own runtime and primitives.

## 4. Architectural Position
ABACUS / CODEX / ARTSTYLE / governance interpretation: `anthropic` is the
**custodian layer**. The patch therefore emphasizes policy, taxonomy,
artifact-routing, review checkpoints, and constraints on movement rather than
runtime logic.

## 5. Artifact Classification
| Class | Description | Owning Concern |
| ----- | ----------- | -------------- |
| schema | Structural definitions of artifacts | governance |
| parser | Readers/transformers for artifacts | runtime (downstream) |
| runtime | Executable behavior | runtime (downstream) |
| policy | Rules constraining behavior/movement | governance |
| taxonomy | Classification vocabulary | governance |
| federation contract | Cross-repo interoperability rules | governance |
| governance | Custodianship, review, ownership | governance |

## 6. Refactor Constraints (Move Rules)
- **Allowed**:
  - Move artifacts deeper in the tree (depth movement only).
  - Add manifests.
  - Add setup / make packaging.
- **Not allowed**:
  - Automatic semantic cross-repo moves.
  - Conceptual reassignment without review.
  - Splicing / rewriting repo-level history files
    (`README`, `ADR`, `CHANGELOG` are **frozen**).
- **Principle**: Move artifacts, not concepts. The only automatic refactoring is
  depth movement within the same repository.

## 7. Artifact Ownership Rules
- Each artifact has exactly one owning concern (see §5).
- Repo-level `README`, `ADR`, and `CHANGELOG` are frozen and never moved.
- Cross-repo moves require an explicit, human-reviewed decision recorded in the
  Handover Notes (§15).

## 8. Patch Plan
> Replace the placeholder moves below with concrete entries per refactor.

### Move 001
- From: `<source/path>`
- To: `<target/path>`
- Reason: `<why this move>`
- Artifact Type: `<schema|parser|runtime|policy|taxonomy|federation|governance>`
- Owning Concern: `<concern>`
- Move Type: depth

### Move 002
- From: `<source/path>`
- To: `<target/path>`
- Reason: `<why this move>`
- Artifact Type: `<...>`
- Owning Concern: `<concern>`
- Move Type: depth

## 9. Proposed File Operations (Diff-like)
```diff
# Representative patch-style entries. File moves, creations, manifest
# additions, and compatibility shims are listed here for review.

# File moves (depth movement only)
rename from <source/path>
rename to   <target/path>

# File creations
new file manifest/artifact-map.yaml
new file handover/patch-index.json

# Compatibility shims (if any)
# new file <old/path>  # re-export pointing at <new/path>
```

## 10. Files to Create
- `manifest/artifact-map.yaml` — artifact-to-owner map.
- `handover/patch-index.json` — index of applied patches.
- `Makefile` additions — packaging targets.
- Setup instructions — only if new tooling is required.

## 11. Build / Package
```bash
# Assemble a handover bundle from this patch file
make patch-bundle PATCH=patches/2026-06-01_artifact-federation-refactor.patch.md

# Produce a zip handover bundle
make handover-zip PATCH=patches/2026-06-01_artifact-federation-refactor.patch.md
```

## 12. Validation
```bash
# Validate that the patch package is structurally complete
make patch-validate PATCH=patches/2026-06-01_artifact-federation-refactor.patch.md
```

Validation checks:
1. All required sections (§1–§15) are present.
2. The embedded manifest (§15) parses as YAML.
3. Frozen files (`README`, `ADR`, `CHANGELOG`) are absent from move entries.

## 13. Integration Instructions
- **Local application**:
  1. Review the Patch Plan (§8) and Proposed File Operations (§9).
  2. Apply each move/creation manually or via your refactoring tool.
  3. Update `manifest/artifact-map.yaml` to reflect new ownership.
- **Validation**: run `make patch-validate` (§12).
- **Rollback**: see §14 Rollback.

## 14. Rollback
1. Revert moved files to their `From:` paths listed in §8.
2. Remove any newly created manifests/shims listed in §10.
3. Restore `manifest/artifact-map.yaml` from version control.
4. Confirm with `make patch-validate`.

## 15. Handover / Operational Manifest
- **Affected artifacts**: see §5 and §8.
- **Decisions**: `anthropic` is governance/custodian; only depth moves are
  automatic.
- **Assumptions**: ownership concerns in §5 are authoritative.
- **Follow-up review items**:
  - Confirm cross-repo boundaries before any semantic move.
  - Verify frozen files were untouched.

### Embedded Manifest
```yaml
version: 1
repository: GBOGEB/anthropic
repository_id: 1255640890
patch_version: v0.1.0
patch_date: 2026-06-01
patch_type: architecture/artifact-governance/handover
output_mode: single-file
constraints:
  allowed:
    - depth-movement
    - add-manifests
    - add-packaging
  not_allowed:
    - cross-repo-semantic-move
    - conceptual-reassignment-without-review
    - splice-repo-history
frozen_files:
  - README
  - ADR
  - CHANGELOG
artifact_classes:
  - schema
  - parser
  - runtime
  - policy
  - taxonomy
  - federation-contract
  - governance
moves: []
```
