import pathlib

def count_lines(root: pathlib.Path) -> int:
    total = 0
    for p in root.rglob("*.py"):
        try:
            total += len(p.read_text(encoding="utf-8").splitlines())
        except Exception:
            continue
    return total

def main():
    root = pathlib.Path(__file__).resolve().parents[1]
    files = list(root.rglob("*.py"))
    pkgs = {p.parent for p in files if (p.parent / "__init__.py").exists()}
    print(f"Python files: {len(files)}")
    print(f"Packages: {len(pkgs)}")
    print(f"Total lines: {count_lines(root)}")

if __name__ == "__main__":
    main()
