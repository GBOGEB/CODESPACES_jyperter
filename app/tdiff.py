import difflib
import pathlib
import sys

def tdiff(a: str, b: str, out: str):
    A = pathlib.Path(a).read_text(encoding="utf-8").splitlines()
    B = pathlib.Path(b).read_text(encoding="utf-8").splitlines()
    patch = difflib.unified_diff(A, B, fromfile=a, tofile=b, lineterm="")
    pathlib.Path(out).write_text("\n".join(patch), encoding="utf-8")
    print(f"Wrote {out}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: python app/tdiff.py <logA> <logB> <out.patch>")
        sys.exit(2)
    tdiff(sys.argv[1], sys.argv[2], sys.argv[3])
