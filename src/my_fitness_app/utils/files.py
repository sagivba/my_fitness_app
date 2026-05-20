from pathlib import Path

SAFE_FILENAME_CHARS = {".", "-", "_"}


def sanitize_filename(filename: str) -> str:
    basename = filename.replace("\\", "/").split("/")[-1].replace("\x00", "").strip()
    if not basename:
        return ""

    if "." not in basename:
        return _clean_filename_part(basename).strip("._-") or "upload"

    stem, extension = basename.rsplit(".", 1)
    clean_stem = _clean_filename_part(stem).strip("._-") or "upload"
    clean_extension = _clean_filename_part(extension).strip("._-").lower()
    if not clean_extension:
        return clean_stem

    return f"{clean_stem}.{clean_extension}"


def is_path_relative_to(child_path: str | Path, parent_path: str | Path) -> bool:
    try:
        Path(child_path).resolve().relative_to(Path(parent_path).resolve())
    except ValueError:
        return False

    return True


def _clean_filename_part(value: str) -> str:
    return "".join(
        character if character.isalnum() or character in SAFE_FILENAME_CHARS else "_"
        for character in value
    ).strip("_")
