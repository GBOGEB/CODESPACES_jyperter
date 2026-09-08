# TRIAGE offline repository index

This directory is generated from the exact tracked repository state by `scripts/repo_artifact_index.py`.

## Outputs

- `ARTIFACT_INDEX.yaml` — complete tracked-artifact census grouped by artifact type and alphabetically ordered by path within each type.
- `FILE_INDEX.tsv` — flat, grep-friendly inventory containing type, path, kind, size, SHA256, Git object and text-searchable flag.

The two generated files exclude themselves from the census to avoid recursive hash churn. `indexed_source_sha` records the exact commit that was inventoried.

## Offline use

```bash
python scripts/repo_artifact_index.py
python scripts/repo_artifact_index.py --grep QPLANT
python scripts/repo_artifact_index.py --grep ALAT
python scripts/repo_artifact_index.py --grep 'ALAT|compliance|negotiation' --regex
python scripts/repo_artifact_index.py --grep RTM --case-sensitive
```

Normal local tools remain useful:

```bash
grep -i 'QPLANT' triage/repo_index/FILE_INDEX.tsv
rg -n -i 'ALAT|compliance|negotiation' .
```

Binary files remain fully indexed by path/type/size/hash but are deliberately skipped by content grep.

## TRIAGE use

The index is discovery and modernization evidence. It does not promote a file to QPS/ABACUS/CODEX authority. Candidate promotion still requires an exact-source SHA, smoke/reproduction evidence, a unique-delta statement, target owner and explicit disposition.
