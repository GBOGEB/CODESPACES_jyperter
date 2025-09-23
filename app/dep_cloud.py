import ast
import pathlib
import subprocess
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOT = ROOT / "reports/import_graph.dot"
PNG = ROOT / "reports/import_graph.png"


def parse_imports(py: pathlib.Path):
    g = set()
    mod = py.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except Exception:
        return g
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                g.add((mod, a.name.split(".")[0]))
        elif isinstance(n, ast.ImportFrom) and n.module:
            g.add((mod, n.module.split(".")[0]))
    return g

def build_graph():
    edges = set()
    for p in ROOT.rglob("*.py"):
        edges |= parse_imports(p)
    DOT.parent.mkdir(exist_ok=True, parents=True)
    with DOT.open("w", encoding="utf-8") as f:
        f.write("digraph imports {\nrankdir=LR;\n")
        for a, b in sorted(edges):
            f.write(f"  \"{a}\" -> \"{b}\";\n")
        f.write("}\n")
    if shutil.which("dot"):
        subprocess.run(["dot", "-Tpng", str(DOT), "-o", str(PNG)], check=False)
    print(f"Wrote {DOT} and {PNG if PNG.exists() else '(PNG skipped)'}")

if __name__ == "__main__":
    build_graph()
