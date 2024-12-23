from pathlib import Path
import zipfile
import tempfile
import os
import contextlib
from typing import Generator
import argparse


CURR_DIR = Path(__file__).resolve().parent


def walk(path: Path) -> Generator[Path, None, None]:
    for root, _dirs, files in os.walk(path):
        root = Path(root)
        for file in files:
            yield root / file


@contextlib.contextmanager
def explode_epub(path: Path):
    assert path.exists()
    assert path.suffix.lower() == ".epub"
    new_path = path.parent / f"{path.stem}_edit{path.suffix}"

    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            rel_path_to_zip_info = zip_ref.NameToInfo
            zip_ref.extractall(temp_dir)

        yield temp_dir

        rel_path_to_full_path = {}
        for file_path in walk(temp_dir):
            rel_path = str(file_path.relative_to(temp_dir))
            assert rel_path in rel_path_to_zip_info
            rel_path_to_full_path[rel_path] = file_path

        # verify no files were added or removed.
        orig_files = sorted(rel_path_to_zip_info.keys())
        curr_files = sorted(rel_path_to_full_path.keys())
        if orig_files != curr_files:
            raise RuntimeError("No files can be added or deleted from the epub.")

        with zipfile.ZipFile(new_path, 'w') as zip_ref:
            for rel_path, zip_info in rel_path_to_zip_info.items():
                full_path = rel_path_to_full_path[rel_path]
                zip_ref.write(full_path, rel_path, compress_type=zip_info.compress_type)


def valid_epub_file(path_str) -> Path:
    path = Path(path_str).resolve()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Invalid path: {path_str}")
    if path.suffix.lower() != ".epub":
        raise argparse.ArgumentTypeError(f"File must have an 'epub' extension. '{path_str}'")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=valid_epub_file, help="path to an epub")
    args = parser.parse_args()

    with explode_epub(args.path) as epub_dir:
        html_files = (f for f in walk(epub_dir) if "html" in f.suffix)
        for file_path in html_files:
            content = file_path.read_text()
            if "fuck" in content:
                open(file_path, "w").write(content.replace("fuck", "BEEP"))


if __name__ == "__main__":
    main()
