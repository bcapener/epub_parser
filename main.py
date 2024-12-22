from pathlib import Path
import zipfile
import tempfile
import os
import contextlib


CURR_DIR = Path(__file__).resolve().parent

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
        for root, _dirs, files in os.walk(temp_dir):
            root = Path(root)
            for file in files:
                file_path = root / file
                rel_path = str(file_path.relative_to(temp_dir))
                assert rel_path in compress_info
                full_file_paths[rel_path] = file_path

        with zipfile.ZipFile(new_path, 'w') as zip_ref:
            for rel_path, zip_info in compress_info.items():
                full_path = full_file_paths[rel_path]
                zip_ref.write(full_path, rel_path, compress_type=zip_info.compress_type)

def main():
    with explode_epub(CURR_DIR / "Mercy of Gods, The - James S. A. Corey.epub") as epub_dir:
        for root, dirs, files in os.walk(epub_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print(os.path.relpath(file_path, epub_dir))


if __name__ == "__main__":
    main()
