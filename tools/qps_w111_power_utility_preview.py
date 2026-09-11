#!/usr/bin/env python3
"""Render a deterministic HTML preview from a sanitized W111 typed receipt."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import sys

FORBIDDEN_KEYS = {"pdf_bytes", "bidder_pdf_bytes", "raw_offer_text", "full_bidder_offer_text", "price_table", "unrestricted_commercial_price_table"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk_keys(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield str(k)
            yield from walk_keys(v)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


def validate(d: dict) -> None:
    for key in ("payload_id", "source_ssot_git_blob_sha", "payload_sha256", "authority_scope", "engineering_promotion_forbidden", "atoms"):
        if key not in d:
            raise ValueError(f"missing required field {key}")
    if d["engineering_promotion_forbidden"] is not True:
        raise ValueError("engineering promotion must be forbidden")
    if len(str(d["source_ssot_git_blob_sha"])) != 40:
        raise ValueError("source SSOT git blob SHA must be 40 hex chars")
    if len(str(d["payload_sha256"])) != 64:
        raise ValueError("payload SHA256 must be 64 hex chars")
    found = FORBIDDEN_KEYS.intersection(set(walk_keys(d)))
    if found:
        raise ValueError(f"forbidden raw source fields present: {sorted(found)}")
    if not isinstance(d["atoms"], list) or not d["atoms"]:
        raise ValueError("atoms must be a non-empty list")
    for atom in d["atoms"]:
        for key in ("name", "value", "unit", "evidence_class", "source_pointer"):
            if key not in atom:
                raise ValueError(f"atom missing {key}")


def render(d: dict) -> str:
    rows = []
    for atom in d["atoms"]:
        value = "UNKNOWN" if atom["value"] is None else str(atom["value"])
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(atom['name']))}</td>"
            f"<td>{html.escape(value)}</td>"
            f"<td>{html.escape(str(atom['unit']))}</td>"
            f"<td>{html.escape(str(atom['evidence_class']))}</td>"
            f"<td><code>{html.escape(str(atom['source_pointer']))}</code></td>"
            "</tr>"
        )
    return """<!doctype html>
<html><head><meta charset="utf-8"><title>QPS W111 Power Utility Workbench</title></head>
<body>
<h1>QPS W111 Power Utility Workbench</h1>
<p><strong>Non-authoritative tooling projection.</strong> Engineering promotion is forbidden.</p>
<p>Payload: <code>{payload}</code><br>Source SSOT blob: <code>{ssot}</code></p>
<table border="1"><thead><tr><th>Atom</th><th>Value</th><th>Unit</th><th>Evidence</th><th>Source pointer</th></tr></thead>
<tbody>{rows}</tbody></table>
</body></html>
""".format(payload=html.escape(str(d["payload_id"])), ssot=html.escape(str(d["source_ssot_git_blob_sha"])), rows="".join(rows))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--html", required=True)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.html)
    rec = Path(args.receipt)
    d = json.loads(inp.read_text(encoding="utf-8"))
    validate(d)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(d), encoding="utf-8")
    receipt = {
        "schema": "codespaces-w111-workbench-receipt/0.1",
        "input_file_sha256": sha256(inp),
        "output_html_sha256": sha256(out),
        "source_ssot_git_blob_sha": d["source_ssot_git_blob_sha"],
        "engineering_promotion_forbidden": True,
        "atoms": len(d["atoms"]),
    }
    rec.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    print("QPS_W111_WORKBENCH=PASS")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"QPS_W111_WORKBENCH=FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
