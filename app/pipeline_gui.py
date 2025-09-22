import json
import os
import pathlib
import threading
import time
import tkinter as tk

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG_ROOT = ROOT / ".gui_runs"


def load_pipelines():
    cfg_json = ROOT / "configs/pipelines.json"
    cfg_toml = ROOT / "configs/pipelines.toml"
    if cfg_json.exists():
        return [p["name"] for p in json.loads(cfg_json.read_text())["pipelines"]]
    if cfg_toml.exists():
        import tomllib
        return [p["name"] for p in tomllib.loads(cfg_toml.read_text())["pipelines"]]
    return []


class Tailer:
    def __init__(self, path: pathlib.Path, callback):
        self.path = path
        self.callback = callback
        self.stop = False
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as f:
            f.seek(0, os.SEEK_END)
            while not self.stop:
                line = f.readline()
                if line:
                    self.callback(line)
                else:
                    time.sleep(0.5)


def main():
    root = tk.Tk()
    root.title("Pipeline Health Monitor")
    pipelines = load_pipelines()
    var = tk.StringVar(value=pipelines)
    listbox = tk.Listbox(root, listvariable=var, height=6)
    listbox.pack(fill="both", expand=False)
    log_text = tk.Text(root, height=25)
    log_text.pack(fill="both", expand=True)
    status = tk.Label(root, text="Select pipeline to tail", anchor="w")
    status.pack(fill="x")
    tailer = None

    def on_select(evt):
        nonlocal tailer
        w = evt.widget
        if not w.curselection():
            return
        name = w.get(w.curselection()[0])
        logs = sorted((LOG_ROOT / name).glob("*.log"))
        if not logs:
            status.config(text=f"No logs for {name}")
            return
        latest = logs[-1]
        status.config(text=f"Tailing {latest}")
        log_text.delete("1.0", "end")
        if tailer:
            tailer.stop = True
        def cb(line):
            log_text.insert("end", line)
            log_text.see("end")
        tailer = Tailer(latest, cb)

    listbox.bind("<<ListboxSelect>>", on_select)
    root.mainloop()


if __name__ == "__main__":
    main()
