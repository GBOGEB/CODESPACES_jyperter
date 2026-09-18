# MCP GUI workflow cross-check

The human-facing GUI enumerates the same five blocks everywhere: cards, Mermaid, JSON API, and Tkinter.

```text
+----------------------+     +----------------------+     +----------------------+
| BLOCK 1 / S1         | --> | BLOCK 2 / S2         | --> | BLOCK 3 / S3         |
| Codex IDE / Orch     |     | GitHub CI            |     | RedHat / Container   |
| source: manifest     |     | source: GitHub/manifest|    | source: manifest     |
+----------------------+     +----------------------+     +----------------------+
                                                                    |
                                                                    v
+----------------------+     +----------------------+
| BLOCK 5 / S5         | <-- | BLOCK 4 / S4         |
| Human Dashboard      |     | MASTER.doc Parser    |
| source: manifest     |     | source: execution    |
+----------------------+     +----------------------+
```

```mermaid
flowchart LR
  S1["1. Codex IDE / Orchestrator"] --> S2["2. GitHub CI"] --> S3["3. RedHat / Container Executor"] --> S4["4. MASTER.doc Parser / RTM"] --> S5["5. Human Outputs Dashboard"]
```

Status semantics are explicit: `PASS`, `FAIL`, `RUNNING`, `PENDING`, `CANCELLED`, `BLOCKED`, `UNKNOWN`. Colour is supplementary only.
