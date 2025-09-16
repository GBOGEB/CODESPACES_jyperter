from flask import Flask, render_template_string, send_file
import subprocess, sys, os, json, requests

app = Flask(__name__)

ARTEFACTS = {
    "CI Workflow": ".github/workflows/mcp_runner.yml",
    "Parser": "Processing_Engine/doc_parser.py",
    "Manifest": "handover_manifest.json",
    "ASCII Diagram": "ASCII_descriptive.md",
    "DMAIC Iteration": "dmaic.yml"
}

STATUS_COLOR = {"success": "green", "fail": "red", "pending": "lightgray", "cancelled": "orange"}

def load_manifest_status():
    manifest = "handover_manifest.json"
    if not os.path.exists(manifest):
        return {}
    try:
        with open(manifest, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("step_status", {})
    except Exception:
        return {}

def fetch_github_status():
    """Optional: query GitHub Actions API (requires token in GITHUB_TOKEN env)."""
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPO", "GBOGEB/MCP")
    if not token:
        return {}
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=1"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        return {}
    run = r.json().get("workflow_runs", [{}])[0]
    return {"S2": run.get("conclusion", "pending")}

HTML = """
<!doctype html>
<html>
<head>
<title>MCP Handover Dashboard</title>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({ startOnLoad: true });
</script>
</head>
<body>
<h1>MCP Recursive Handover</h1>

<h2>Artefacts</h2>
<ul>
{% for name, path in artefacts.items() %}
  <li><a href="/open/{{path}}">{{name}}</a></li>
{% endfor %}
</ul>

<h2>Run Parser</h2>
<a href="/run_parser">Run DOCX Parser</a>

<h2>Workflow Diagram</h2>
<div class="mermaid">
graph TD
{% for step in steps %}
  {{step.id}}["{{loop.index}}. {{step.name}}"]; style {{step.id}} fill:{{colors[step.status]}},stroke:#333,stroke-width:2px
{% endfor %}
S1-->S2-->S3-->S4-->S5
</div>

</body>
</html>
"""

@app.route("/")
def home():
    steps = [
        {"id": "S1", "name": "Codex IDE", "status": "pending"},
        {"id": "S2", "name": "GitHub CI", "status": "pending"},
        {"id": "S3", "name": "RedHat VM", "status": "pending"},
        {"id": "S4", "name": "Master.doc Parser", "status": "pending"},
        {"id": "S5", "name": "Outputs Dashboard", "status": "pending"},
    ]
    manifest_status = load_manifest_status()
    for s in steps:
        if s["id"] in manifest_status:
            s["status"] = manifest_status[s["id"]]
    gh_status = fetch_github_status()
    for s in steps:
        if s["id"] in gh_status:
            s["status"] = gh_status[s["id"]]
    return render_template_string(HTML, artefacts=ARTEFACTS, steps=steps, colors=STATUS_COLOR)

@app.route("/run_parser")
def run_parser():
    try:
        subprocess.run([sys.executable, "Processing_Engine/doc_parser.py"], check=True)
        manifest_status = load_manifest_status()
        manifest_status["S4"] = "success"
        with open("handover_manifest.json", "w", encoding="utf-8") as f:
            json.dump({"step_status": manifest_status}, f, indent=2)
        return "Parser executed successfully."
    except Exception as e:
        manifest_status = load_manifest_status()
        manifest_status["S4"] = "fail"
        with open("handover_manifest.json", "w", encoding="utf-8") as f:
            json.dump({"step_status": manifest_status}, f, indent=2)
        return str(e), 500
