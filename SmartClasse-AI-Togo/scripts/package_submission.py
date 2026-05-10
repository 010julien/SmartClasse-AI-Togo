from __future__ import annotations

import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT_DIR / "dist"
INCLUDE_ITEMS = [
    "README.md",
    "LICENSE",
    "NOTICE.txt",
    "requirements.txt",
    "src",
    "flutter_client",
    "scripts",
]


def run_tests() -> None:
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT_DIR, check=True)


def check_required_files() -> None:
    missing = [name for name in ["LICENSE", "NOTICE.txt"] if not (ROOT_DIR / name).is_file()]
    if missing:
        raise SystemExit(
            "Missing required file(s): " + ", ".join(missing) + ". Create them before packaging."
        )


def add_path_to_zip(archive: zipfile.ZipFile, path: Path) -> None:
    if path.is_file():
        archive.write(path, path.relative_to(ROOT_DIR))
        return

    if not path.is_dir():
        return

    for file_path in path.rglob("*"):
        if file_path.is_file() and "dist" not in file_path.parts:
            archive.write(file_path, file_path.relative_to(ROOT_DIR))


def create_archive() -> Path:
    DIST_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = DIST_DIR / f"smartclasse_submission_{timestamp}.zip"

    print("Creating submission archive...")
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in INCLUDE_ITEMS:
            add_path_to_zip(archive, ROOT_DIR / item)

    return archive_path


def main() -> int:
    run_tests()
    check_required_files()
    archive_path = create_archive()
    print(f"Package created: {archive_path}")
    print("Please review dist/ and ensure sensitive/private data not included.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())