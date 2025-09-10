# GitHub Codespaces ♥️ Jupyter Notebooks

Welcome to your shiny new codespace! We've got everything fired up and running for you to explore Python and Jupyter notebooks.

You've got a blank canvas to work on from a git perspective as well. There's a single initial commit with what you're seeing right now - where you go from here is up to you!

Everything you do here is contained within this one codespace. There is no repository on GitHub yet. If and when you’re ready you can click "Publish Branch" and we’ll create your repository and push up your project. If you were just exploring then and have no further need for this code then you can simply delete your codespace and it's gone forever.

## ZIP Processing Pipeline

The project includes `src/zip_pipeline.py`, a small utility for sequentially
processing ZIP archives. For each archive it performs bytecode compilation
(smoke test), an optional dry run, and integration tests via `pytest`. The
original ZIP is deleted when processing succeeds.

Run the pipeline by supplying the directories to scan:

```bash
python -m src.zip_pipeline <dir1> <dir2> ...
```
