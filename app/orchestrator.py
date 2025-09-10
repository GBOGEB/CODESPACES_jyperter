import os
import sys
import json
import tomllib
import time
import socket
import subprocess
import shlex
import pathlib
import datetime
from argparse import ArgumentParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG_DIR = ROOT / "configs"
RUN_DIR = ROOT / ".gui_runs"
RUN_DIR.mkdir(exist_ok=True)
NDJ_DIR = ROOT / ".ndjson"
NDJ_DIR.mkdir(exist_ok=True)


def _load_cfg():
    pj = CFG_DIR / "pipelines.json"
    pt = CFG_DIR / "pipelines.toml"
    if pj.exists():
        return json.loads(pj.read_text(encoding="utf-8"))
    elif pt.exists():
        return tomllib.loads(pt.read_text(encoding="utf-8"))
    raise SystemExit("No pipelines.(json|toml) found in configs/")


def _next_port(host, start):
    port = start
    while True:
        with socket.socket() as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                port += 1


def run_pipeline(name: str, debug: bool = False):
    cfg = _load_cfg()
    defaults = cfg.get("defaults", {})
    host = defaults.get("debug_host", "127.0.0.1")
    port = defaults.get("debug_port_start", 5678)
    spec = next(p for p in cfg["pipelines"] if p["name"] == name)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = RUN_DIR / name
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{name}_{ts}.log"
    ndjson_path = NDJ_DIR / f"{name}_{ts}.ndjson"

    cmd = spec["command"]
    args = shlex.split(cmd, posix=os.name != "nt")
    if debug and "python" in args[0].lower():
        listen = _next_port(host, port)
        dbg = [
            sys.executable,
            "-m",
            "debugpy",
            "--listen",
            f"{host}:{listen}",
            "--wait-for-client",
        ] + args[1:]
        os.environ["PIPELINE_GUI_DEBUG_PORT"] = str(listen)
        popen_args = dbg
        print(f"[DEBUG] Attach on {host}:{listen}")
    else:
        popen_args = args

    with open(log_path, "w", encoding="utf-8") as lf, open(
        ndjson_path, "w", encoding="utf-8"
    ) as nf:
        proc = subprocess.Popen(
            popen_args,
            cwd=spec.get("workdir", "."),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for line in proc.stdout:
            line = line.rstrip("\n")
            stamp = datetime.datetime.utcnow().isoformat() + "Z"
            rec = f"{stamp} {line}"
            print(rec)
            lf.write(rec + "\n")
            nf.write(json.dumps({"ts": stamp, "msg": line}) + "\n")
        rc = proc.wait()
    print(f"[EXIT] {name} rc={rc} log={log_path}")


if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument("--run", help="pipeline name to run")
    ap.add_argument(
        "--debug", nargs="?", const=True, default=False, help="debug mode for named pipeline"
    )
    args = ap.parse_args()
    if args.run:
        run_pipeline(args.run, debug=bool(args.debug))
