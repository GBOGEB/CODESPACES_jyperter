# SEC-07: USER REQUEST / TRACEABILITY PLAN

The traceability plan captures user-driven requirements and links them to
code, configuration, and automation artifacts.

```json
{
  "requirements": [
    {
      "id": "REQ-01",
      "title": "Artifact indexing system",
      "section": "SEC-07",
      "dependencies": [],
      "dependents": ["REQ-02"],
      "artifacts": [
        "src/measure_phase/index.py",
        "Makefile"
      ]
    },
    {
      "id": "REQ-02",
      "title": "Requirement dashboard and changelog",
      "section": "SEC-07",
      "dependencies": ["REQ-01"],
      "dependents": [],
      "artifacts": [
        "docs/dashboard.html",
        "scripts/update_changelog.py",
        ".github/workflows/req-changelog.yml"
      ]
    }
  ]
}
```

Each requirement lists its forward and backward dependencies along with
links to the artifacts that implement or support it.
