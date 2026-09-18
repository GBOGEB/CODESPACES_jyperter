from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

try:
    from .status_model import (
        STATUS_META,
        build_steps,
        load_manifest,
        write_step_status,
    )
except ImportError:
    from status_model import (
        STATUS_META,
        build_steps,
        load_manifest,
        write_step_status,
    )

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(
    os.environ.get(
        "MCP_MANIFEST",
        str(REPO_ROOT / "handover_manifest.json"),
    )
).expanduser().resolve()
PARSER = REPO_ROOT / "Processing_Engine" / "doc_parser.py"

ARTEFACTS = {
    "Repository CI": REPO_ROOT / ".github/workflows/ci.yml",
    "GUI candidate CI": REPO_ROOT / ".github/workflows/mcp-gui-candidate.yml",
    "Manifest": REPO_ROOT / "handover_manifest.json",
    "ASCII / Mermaid cross-check":
        REPO_ROOT / "gui_candidate_bundle/ASCII_descriptive.md",
    "GUI handover": REPO_ROOT / "gui_candidate_bundle/HANDOVER.md",
}


def open_file(path: Path) -> None:
    if not path.exists():
        messagebox.showwarning(
            "Not present",
            "Repository artefact is not present:\n"
            f"{path.relative_to(REPO_ROOT)}",
        )
        return
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except OSError as exc:
        messagebox.showerror("Open failed", str(exc))


def run_parser() -> None:
    if not PARSER.exists():
        write_step_status(
            MANIFEST,
            "S4",
            "blocked",
            "Processing_Engine/doc_parser.py is not present",
        )
        messagebox.showwarning(
            "BLOCK 4 blocked",
            "Parser is not present in this repository. "
            "Status recorded as BLOCKED.",
        )
        return

    completed = subprocess.run(
        [sys.executable, str(PARSER)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    status = "success" if completed.returncode == 0 else "fail"
    detail = (
        completed.stdout
        or completed.stderr
        or "Parser completed"
    ).strip()[-800:]
    write_step_status(MANIFEST, "S4", status, detail)
    messagebox.showinfo(
        "BLOCK 4",
        f"Parser status: {STATUS_META[status]['label']}",
    )


def main() -> None:
    root = tk.Tk()
    root.title("MCP Human Execution Console")
    root.geometry("820x560")

    tk.Label(
        root,
        text="MCP Recursive Handover",
        font=("Segoe UI", 18, "bold"),
    ).pack(anchor="w", padx=18, pady=(16, 2))
    tk.Label(
        root,
        text=(
            "Numbered execution blocks with evidence status. "
            "Colour is supplemented by text labels."
        ),
        font=("Segoe UI", 10),
    ).pack(anchor="w", padx=18, pady=(0, 12))

    frame = tk.Frame(root)
    frame.pack(fill="x", padx=18)
    for index, step in enumerate(
        build_steps(load_manifest(MANIFEST)),
        start=1,
    ):
        meta = step["visual"]
        row = tk.Frame(
            frame,
            bd=1,
            relief="solid",
            padx=8,
            pady=8,
        )
        row.pack(fill="x", pady=3)
        tk.Label(
            row,
            text=f"BLOCK {index} · {step['id']}",
            width=14,
            anchor="w",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        tk.Label(
            row,
            text=step["name"],
            width=34,
            anchor="w",
        ).pack(side="left")
        tk.Label(
            row,
            text=meta["label"],
            fg=meta["color"],
            bg=meta["background"],
            width=12,
        ).pack(side="left", padx=6)
        tk.Label(
            row,
            text=f"source: {step['source']}",
            anchor="w",
        ).pack(side="left")

    actions = tk.Frame(root)
    actions.pack(fill="x", padx=18, pady=14)
    tk.Button(
        actions,
        text="Run BLOCK 4 parser",
        command=run_parser,
    ).pack(side="left", padx=(0, 8))
    tk.Button(
        actions,
        text="Open Flask dashboard",
        command=lambda: subprocess.Popen(
            [
                sys.executable,
                str(REPO_ROOT / "gui_candidate_bundle/gui_flask.py"),
            ],
            cwd=REPO_ROOT,
        ),
    ).pack(side="left")

    files = tk.LabelFrame(
        root,
        text="Artefacts",
        padx=8,
        pady=8,
    )
    files.pack(
        fill="both",
        expand=True,
        padx=18,
        pady=(0, 16),
    )
    for label, path in ARTEFACTS.items():
        state = "present" if path.exists() else "not present"
        tk.Button(
            files,
            text=f"{label} — {state}",
            anchor="w",
            command=lambda p=path: open_file(p),
        ).pack(fill="x", pady=2)

    root.mainloop()


if __name__ == "__main__":
    main()
