from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests
from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template_string,
    send_file,
    url_for,
)

try:
    from .status_model import (
        STATUS_META,
        build_steps,
        load_manifest,
        normalize_status,
        utc_now,
        write_step_status,
    )
except ImportError:
    from status_model import (
        STATUS_META,
        build_steps,
        load_manifest,
        normalize_status,
        utc_now,
        write_step_status,
    )

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "handover_manifest.json"
MANIFEST_PATH = Path(
    os.environ.get("MCP_MANIFEST", str(DEFAULT_MANIFEST))
).expanduser().resolve()
PARSER_PATH = REPO_ROOT / "Processing_Engine" / "doc_parser.py"

ARTEFACTS = {
    "Repository CI": ".github/workflows/ci.yml",
    "GUI candidate CI": ".github/workflows/mcp-gui-candidate.yml",
    "Parser": "Processing_Engine/doc_parser.py",
    "Manifest": "handover_manifest.json",
    "ASCII / Mermaid cross-check": "gui_candidate_bundle/ASCII_descriptive.md",
    "GUI handover": "gui_candidate_bundle/HANDOVER.md",
}

app = Flask(__name__)


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_github_status() -> dict[str, dict[str, Any]]:
    """Return live CI evidence for S2; degrade safely if GitHub is unavailable."""
    repo = os.environ.get("GITHUB_REPO", "GBOGEB/CODESPACES_jyperter")
    workflow = os.environ.get(
        "MCP_GITHUB_WORKFLOW",
        "mcp-gui-candidate.yml",
    )
    branch = os.environ.get("MCP_GITHUB_BRANCH", "main")
    url = (
        f"https://api.github.com/repos/{repo}/actions/"
        f"workflows/{workflow}/runs"
    )
    try:
        response = requests.get(
            url,
            headers=_github_headers(),
            params={"branch": branch, "per_page": 1},
            timeout=4,
        )
        response.raise_for_status()
        runs = response.json().get("workflow_runs", [])
        if not runs:
            return {}
        run = runs[0]
        raw = run.get("conclusion") or run.get("status") or "pending"
        return {
            "S2": {
                "status": normalize_status(raw),
                "detail": (
                    "GitHub Actions: "
                    f"{run.get('name', workflow)} "
                    f"#{run.get('run_number', '?')} ({raw})"
                ),
                "updated_at": run.get("updated_at"),
                "url": run.get("html_url"),
            }
        }
    except (requests.RequestException, ValueError, TypeError):
        return {}


def current_steps() -> list[dict[str, Any]]:
    return build_steps(
        load_manifest(MANIFEST_PATH),
        fetch_github_status(),
    )


HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MCP Human Execution Console</title>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({
  startOnLoad: true,
  securityLevel: 'strict',
  theme: 'base'
});
</script>
<style>
:root {
  font-family: Inter, "Segoe UI", Arial, sans-serif;
  color: #172033;
  background: #f6f7f9;
}
body { margin: 0; }
.shell { max-width: 1180px; margin: auto; padding: 28px; }
.hero, .panel {
  background: #fff;
  border: 1px solid #d9dee7;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 18px #14213d12;
}
.panel { margin-top: 14px; }
h1 { margin: 0 0 8px; font-size: 30px; }
.sub, .note, .detail, .source { color: #5d677a; }
.sub { margin: 0; }
.legend, .actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.legend { margin: 18px 0; }
.pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #cfd5df;
}
.dot { width: 9px; height: 9px; border-radius: 50%; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));
  gap: 12px;
  margin: 18px 0;
}
.card {
  background: #fff;
  border: 1px solid #d9dee7;
  border-radius: 14px;
  padding: 16px;
  min-height: 150px;
}
.stepid {
  font-size: 12px;
  color: #667085;
  font-weight: 800;
  letter-spacing: .06em;
}
.name { font-weight: 800; margin: 6px 0; }
.status {
  display: inline-block;
  border-radius: 8px;
  padding: 5px 8px;
  font-size: 12px;
  font-weight: 900;
}
.detail { font-size: 13px; margin-top: 10px; line-height: 1.35; }
.source { font-size: 11px; margin-top: 8px; }
.btn {
  background: #172033;
  color: #fff;
  border: 0;
  border-radius: 9px;
  padding: 10px 14px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
}
.btn.secondary { background: #eef1f4; color: #172033; }
.btn[disabled] { opacity: .45; cursor: not-allowed; }
table { width: 100%; border-collapse: collapse; }
td, th {
  text-align: left;
  border-bottom: 1px solid #e7eaf0;
  padding: 9px;
  font-size: 13px;
}
code { font-size: 12px; }
.mermaid { overflow: auto; }
.note { font-size: 12px; }
</style>
</head>
<body>
<main class="shell">
<section class="hero">
<h1>MCP Recursive Handover — Human Execution Console</h1>
<p class="sub">
  Evidence-first view: numbered blocks, status text + colour,
  source provenance, and bounded actions. Colour is never the only signal.
</p>

<div class="legend" aria-label="Status legend">
{% for key, meta in status_meta.items() %}
<span class="pill">
  <span class="dot" style="background:{{meta.color}}"></span>{{meta.label}}
</span>
{% endfor %}
</div>

<div class="grid">
{% for step in steps %}
<article class="card"
         aria-label="{{step.id}} {{step.name}} {{step.visual.label}}">
<div class="stepid">
  BLOCK {{loop.index}} · {{step.id}} · {{step.role|upper}}
</div>
<div class="name">{{step.name}}</div>
<span class="status"
      style="color:{{step.visual.color}};background:{{step.visual.background}}">
  {{step.visual.label}}
</span>
<div class="detail">{{step.detail}}</div>
<div class="source">
  source: {{step.source}}
  {% if step.updated_at %} · {{step.updated_at}}{% endif %}
</div>
</article>
{% endfor %}
</div>

<div class="actions">
<form action="{{url_for('run_parser')}}" method="post">
  <button class="btn" type="submit"
    {% if not parser_exists %}
    disabled aria-disabled="true"
    title="Parser is not present in this repository"
    {% endif %}>
    Run BLOCK 4 parser
  </button>
</form>
<a class="btn secondary" href="{{url_for('home')}}">Refresh evidence</a>
<a class="btn secondary" href="{{url_for('status_api')}}">Status JSON</a>
</div>

{% if not parser_exists %}
<p class="note">
  BLOCK 4 launch is disabled because
  <code>Processing_Engine/doc_parser.py</code> is not present.
  The dashboard reports this as a repository integration gap rather than
  pretending to execute it.
</p>
{% endif %}
</section>

<section class="panel">
<h2>Workflow rendering</h2>
<div class="mermaid">
flowchart LR
{% for step in steps %}
  {{step.id}}["{{loop.index}}. {{step.name}}\n{{step.visual.label}}"]
  style {{step.id}} fill:{{step.visual.background}},stroke:{{step.visual.color}},stroke-width:3px,color:#172033
{% endfor %}
S1 --> S2 --> S3 --> S4 --> S5
</div>
<p class="note">
  Mermaid mirrors the same status model used by the cards and JSON API;
  it is a rendering, not a second source of truth.
</p>
</section>

<section class="panel">
<h2>Artefacts</h2>
<table>
<thead><tr><th>Purpose</th><th>Repository path</th><th>State</th></tr></thead>
<tbody>
{% for label, path, state in artefacts %}
<tr>
  <td>{{label}}</td>
  <td>
    <a href="{{url_for('open_artifact', filename=path)}}">
      <code>{{path}}</code>
    </a>
  </td>
  <td>{{state}}</td>
</tr>
{% endfor %}
</tbody>
</table>
</section>
</main>
</body>
</html>
"""


@app.get("/")
def home():
    artefacts = []
    for label, relative in ARTEFACTS.items():
        state = "present" if (REPO_ROOT / relative).exists() else "not present"
        artefacts.append((label, relative, state))
    return render_template_string(
        HTML,
        steps=current_steps(),
        status_meta=STATUS_META,
        artefacts=artefacts,
        parser_exists=PARSER_PATH.exists(),
    )


@app.get("/api/status")
def status_api():
    return jsonify(
        {
            "generated_at": utc_now(),
            "manifest": str(MANIFEST_PATH),
            "steps": current_steps(),
        }
    )


@app.post("/run_parser")
def run_parser():
    if not PARSER_PATH.exists():
        write_step_status(
            MANIFEST_PATH,
            "S4",
            "blocked",
            f"Parser missing: {PARSER_PATH.relative_to(REPO_ROOT)}",
        )
        return redirect(url_for("home"), code=303)

    try:
        completed = subprocess.run(
            [sys.executable, str(PARSER_PATH)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        write_step_status(
            MANIFEST_PATH,
            "S4",
            "fail",
            f"Parser launch failed: {exc}",
        )
        return redirect(url_for("home"), code=303)

    detail = (
        completed.stdout
        or completed.stderr
        or "Parser completed"
    ).strip()[-800:]
    write_step_status(
        MANIFEST_PATH,
        "S4",
        "success" if completed.returncode == 0 else "fail",
        detail,
    )
    return redirect(url_for("home"), code=303)


@app.get("/open/<path:filename>")
def open_artifact(filename: str):
    candidate = (REPO_ROOT / filename).resolve()
    try:
        candidate.relative_to(REPO_ROOT)
    except ValueError:
        abort(404)
    if not candidate.is_file():
        abort(404)
    return send_file(candidate, as_attachment=False)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
    )
