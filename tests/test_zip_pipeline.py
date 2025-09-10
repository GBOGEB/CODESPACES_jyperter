import zipfile
from pathlib import Path

import zip_pipeline


def test_process_zip(tmp_path):
    # create a simple python file inside a temporary directory
    simple_py = tmp_path / "example.py"
    simple_py.write_text("print('hi')\n")

    # create a zip archive containing the python file
    zip_path = tmp_path / "example.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(simple_py, arcname="example.py")

    # process the zip and ensure it is deleted afterwards
    zip_pipeline.process_zip(zip_path)
    assert not zip_path.exists()


def test_discover_zip_files(tmp_path):
    # create nested directories with zip files
    (tmp_path / "a").mkdir()
    zip1 = tmp_path / "a" / "one.zip"
    with zipfile.ZipFile(zip1, "w"):
        pass
    zip2 = tmp_path / "two.zip"
    with zipfile.ZipFile(zip2, "w"):
        pass

    found = zip_pipeline.discover_zip_files([str(tmp_path)])
    assert zip1 in found and zip2 in found
