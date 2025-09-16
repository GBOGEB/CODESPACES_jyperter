# GitHub Codespaces ♥️ Jupyter Notebooks

Welcome to your shiny new codespace! We've got everything fired up and running for you to explore Python and Jupyter notebooks.

You've got a blank canvas to work on from a git perspective as well. There's a single initial commit with what you're seeing right now - where you go from here is up to you!

Everything you do here is contained within this one codespace. There is no repository on GitHub yet. If and when you’re ready you can click "Publish Branch" and we’ll create your repository and push up your project. If you were just exploring then and have no further need for this code then you can simply delete your codespace and it's gone forever.

## ZIP Processing Pipeline

The project includes `src/zip_pipeline.py`, a small utility for sequentially processing ZIP archives. For each archive it performs bytecode compilation (smoke test), an optional dry run, and integration tests via `pytest`. The original ZIP is deleted when processing succeeds.

Run the pipeline by supplying the directories to scan:

```bash
python -m src.zip_pipeline <dir1> <dir2> ...
```

## Slide Preview Generator

Use `tools/extract_slide_previews.py` to create quick HTML previews of a PowerPoint deck. It writes three files to the chosen output directory:

- `slide_texts.json` – full text content for each slide
- `slide_digital_twins.json` – compact summary and styling hints
- `slide_preview.html` – simple visual cards with inline CSS

Run the script like this:

```bash
python tools/extract_slide_previews.py --pptx path/to/deck.pptx --outdir output --limit 10
```

The generated HTML uses basic cards per slide:

```html
<div class='card' style='background:#f0f8ff'>
  <div class='meta'><span class='num'>#1</span> • shapes:5 • bullets:2</div>
  <h3 class='title'>SLIDE TITLE</h3>
  <div class='para'>First bullet item…</div>
</div>
```
