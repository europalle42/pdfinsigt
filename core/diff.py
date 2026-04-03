"""Sammenligning af metadata mellem to PDF-filer."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.metadata import extract_metadata


@dataclass
class DiffEntry:
    """Én forskel mellem to filer."""
    field: str
    value_a: str | None
    value_b: str | None
    status: str  # identical, changed, removed, added


def compare_files(path_a: str | Path, path_b: str | Path) -> list[DiffEntry]:
    """Sammenlign metadata fra to PDF-filer.

    Returns:
        Liste af DiffEntry med alle felter og deres status.
    """
    meta_a = extract_metadata(path_a)
    meta_b = extract_metadata(path_b)

    diffs = []

    # Compare file info (skip path)
    _compare_section(diffs, "Fil", meta_a["file_info"], meta_b["file_info"],
                     skip_keys={"path", "filename"})

    # Compare doc info
    _compare_section(diffs, "Dokument", meta_a["doc_info"], meta_b["doc_info"])

    # Compare XMP
    _compare_section(diffs, "XMP", meta_a["xmp"], meta_b["xmp"])

    # Compare properties
    _compare_section(diffs, "Egenskaber", meta_a["pdf_properties"], meta_b["pdf_properties"])

    return diffs


def _compare_section(
    diffs: list[DiffEntry],
    prefix: str,
    dict_a: dict[str, Any],
    dict_b: dict[str, Any],
    skip_keys: set[str] | None = None,
) -> None:
    """Sammenlign to dicts og tilføj forskelle til diffs-listen."""
    skip = skip_keys or set()
    all_keys = sorted(set(dict_a.keys()) | set(dict_b.keys()))

    for key in all_keys:
        if key in skip or key.startswith("_"):
            continue

        val_a = dict_a.get(key)
        val_b = dict_b.get(key)

        str_a = _to_str(val_a)
        str_b = _to_str(val_b)

        if val_a is None and val_b is not None:
            status = "added"
        elif val_a is not None and val_b is None:
            status = "removed"
        elif str_a == str_b:
            status = "identical"
        else:
            status = "changed"

        diffs.append(DiffEntry(
            field=f"{prefix}: {key}",
            value_a=str_a,
            value_b=str_b,
            status=status,
        ))


def _to_str(val: Any) -> str | None:
    """Konvertér værdi til streng."""
    if val is None:
        return None
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)
