from pathlib import Path

from pptx import Presentation

from tools.extract_slide_previews import extract_slides, write_html_preview


def test_extract_and_preview(tmp_path):
    prs = Presentation()
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "TITLE"
    slide.placeholders[1].text = "- bullet1\nbullet2"
    pptx_path = tmp_path / "sample.pptx"
    prs.save(pptx_path)

    slides = extract_slides(pptx_path)
    assert slides[0]["texts"][0] == "TITLE"
    html_path = tmp_path / "preview.html"
    write_html_preview(slides, html_path)
    assert html_path.exists()
    content = html_path.read_text()
    assert "Slide Preview" in content
