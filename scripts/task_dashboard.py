"""Minimal Tkinter dashboard for Ariana Trace task runner.

This prototype demonstrates task search/filtering, a Dry-Run toggle,
execution with live console output, and links to artifacts.
"""
from __future__ import annotations

import json
import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config" / "tasks"
ARTIFACT_DIR = Path("artifacts")


def load_tasks():
    tasks = []
    for path in CONFIG_DIR.glob("*.json"):
        with path.open() as f:
            task = json.load(f)
        tasks.append(task)
    return tasks


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ariana Trace Task Dashboard")
        self.geometry("800x500")
        self.tasks = load_tasks()

        self.search_var = tk.StringVar()
        self.dry_run = tk.BooleanVar(value=True)
        self.list_var = tk.StringVar(value=[t["id"] for t in self.tasks])

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Entry(top, textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        ttk.Checkbutton(top, text="Dry-Run", variable=self.dry_run).pack(side="left")
        ttk.Button(top, text="Search", command=self.update_list).pack(side="left")

        middle = ttk.Frame(self)
        middle.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(middle, listvariable=self.list_var, height=10)
        self.listbox.pack(side="left", fill="both", expand=True)
        ttk.Button(middle, text="Run", command=self.run_selected).pack(side="left", padx=5)

        self.console = tk.Text(self, state="disabled", height=15)
        self.console.pack(fill="both", expand=True)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Open Artifacts", command=self.open_artifacts).pack(side="left")

    def update_list(self):
        term = self.search_var.get().lower()
        items = [t["id"] for t in self.tasks if term in t["id"].lower() or any(term in tag for tag in t.get("tags", []))]
        self.list_var.set(items)

    def open_artifacts(self):
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        path = ARTIFACT_DIR.resolve()
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except Exception as exc:
            self.append_console(f"Could not open artifacts: {exc}\n")

    def append_console(self, text: str):
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.configure(state="disabled")
        self.console.see("end")

    def run_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        task_id = self.listbox.get(selection[0])
        task = next(t for t in self.tasks if t["id"] == task_id)
        args = list(task["args"])
        mode = "dry" if self.dry_run.get() else "apply"
        args = [a.replace("{mode}", mode) for a in args]
        thread = threading.Thread(target=self.execute, args=(task["entrypoint"], args, task_id), daemon=True)
        thread.start()

    def execute(self, entrypoint: str, args: list[str], task_id: str):
        self.append_console(f"\nRunning {task_id}...\n")
        proc = subprocess.Popen([entrypoint] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log_dir = ARTIFACT_DIR / task_id
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "run.log").open("w", encoding="utf-8") as log_file:
            for line in proc.stdout:  # type: ignore[assignment]
                self.append_console(line)
                log_file.write(line)
        code = proc.wait()
        self.append_console(f"Task finished with exit code {code}\n")


if __name__ == "__main__":
    Dashboard().mainloop()
