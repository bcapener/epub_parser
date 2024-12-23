from pathlib import Path
import zipfile
import tempfile
import os
import contextlib
from typing import Generator


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

    compress_info: dict[str, zipfile.ZipInfo] = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            compress_info = zip_ref.NameToInfo
            zip_ref.extractall(temp_dir)

        yield temp_dir

        full_file_paths = {}
        for file_path in walk(temp_dir):
            rel_path = str(file_path.relative_to(temp_dir))
            assert rel_path in compress_info
            full_file_paths[rel_path] = file_path

        with zipfile.ZipFile(new_path, 'w') as zip_ref:
            for rel_path, zip_info in compress_info.items():
                full_path = full_file_paths[rel_path]
                zip_ref.write(full_path, rel_path, compress_type=zip_info.compress_type)

def main():
    with explode_epub(CURR_DIR / "Mercy of Gods, The - James S. A. Corey.epub") as epub_dir:
        for file_path in walk(epub_dir):
            if file_path.suffix.endswith("html"):
                content = file_path.read_text()
                if "fuck" in content:
                    open(file_path, "w").write(content.replace("fuck", "BEEP"))
        # for root, dirs, files in os.walk(epub_dir):
        #     root = Path(root)
        #     for file in files:
        #         file_path = root / file
        #         if file_path.suffix.endswith("html"):
        #             content = file_path.read_text()
        #             if "fuck" in content:
        #                 open(file_path, "w").write(content.replace("fuck", "BEEP"))
        #             # if "fuck" in file_path.read_text().lower().count("fuck"):
        #             # if count:
        #             #     print(file_path, count)
        #         # print(os.path.relpath(file_path, epub_dir))


if __name__ == "__main__":
    main()
