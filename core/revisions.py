"""Revisionshistorik fra PDF-filer via %%EOF-detektion og binær slicing."""

import io
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pikepdf


@dataclass
class Revision:
    """Én revision af en PDF-fil."""
    number: int
    offset: int  # byte offset for %%EOF
    size: int  # bytes for denne revision
    pages: int | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    revision_type: str = "modified"  # created, modified, metadata_removed


def find_eof_offsets(data: bytes) -> list[int]:
    """Find alle %%EOF markører i PDF-data.

    Returnerer liste af byte-offsets (inkl. %%EOF + newline).
    """
    offsets = []
    # %%EOF can be followed by \r\n, \n, \r, or be at end of file
    for match in re.finditer(rb'%%EOF[\r\n]*', data):
        offsets.append(match.end())
    return offsets


def extract_revisions(filepath: str | Path) -> list[Revision]:
    """Udtræk alle revisioner fra en PDF-fil.

    Bruger binær slicing: skær PDF-bytes ved hver %%EOF markør
    for at få tidligere versioner af filen.
    """
    filepath = Path(filepath)
    data = filepath.read_bytes()
    eof_offsets = find_eof_offsets(data)

    if not eof_offsets:
        return []

    revisions = []
    for i, offset in enumerate(eof_offsets):
        slice_data = data[:offset]
        rev = Revision(
            number=i + 1,
            offset=offset,
            size=len(slice_data),
        )

        # Try to extract metadata from this revision slice
        try:
            pdf = pikepdf.open(io.BytesIO(slice_data))
            rev.pages = len(pdf.pages)
            rev.metadata = _extract_revision_metadata(pdf)
            rev.revision_type = _classify_revision(rev, revisions)
            pdf.close()
        except Exception:
            rev.revision_type = "modified"

        revisions.append(rev)

    return revisions


def _extract_revision_metadata(pdf: pikepdf.Pdf) -> dict[str, str]:
    """Udtræk metadata fra en åben pikepdf instans."""
    meta = {}

    # Document Info dict
    try:
        info = pdf.docinfo
        if info:
            for key in info:
                try:
                    val = str(info[key])
                    meta[str(key)] = val
                except Exception:
                    pass
    except Exception:
        pass

    # XMP metadata
    try:
        with pdf.open_metadata() as xmp:
            for key in ["xmp:CreateDate", "xmp:ModifyDate", "xmp:CreatorTool",
                         "dc:creator", "dc:title", "pdf:Producer"]:
                try:
                    val = xmp.get(key)
                    if val:
                        meta[key] = str(val)
                except Exception:
                    pass
    except Exception:
        pass

    return meta


def _classify_revision(current: Revision, previous: list[Revision]) -> str:
    """Klassificér revision baseret på metadata-ændringer."""
    if not previous:
        return "created"

    prev = previous[-1]
    # If current has no metadata but previous did, it's metadata removal
    if not current.metadata and prev.metadata:
        return "metadata_removed"

    return "modified"


def compare_revisions(rev_a: Revision, rev_b: Revision) -> dict[str, Any]:
    """Sammenlign to revisioner og returnér forskelle."""
    all_keys = set(rev_a.metadata.keys()) | set(rev_b.metadata.keys())
    diffs = {}

    for key in sorted(all_keys):
        val_a = rev_a.metadata.get(key)
        val_b = rev_b.metadata.get(key)

        if val_a == val_b:
            diffs[key] = {"status": "identical", "a": val_a, "b": val_b}
        elif val_a is None:
            diffs[key] = {"status": "added", "a": None, "b": val_b}
        elif val_b is None:
            diffs[key] = {"status": "removed", "a": val_a, "b": None}
        else:
            diffs[key] = {"status": "changed", "a": val_a, "b": val_b}

    # Also compare pages and size
    diffs["_pages"] = {
        "status": "identical" if rev_a.pages == rev_b.pages else "changed",
        "a": rev_a.pages,
        "b": rev_b.pages,
    }
    diffs["_size"] = {
        "status": "identical" if rev_a.size == rev_b.size else "changed",
        "a": rev_a.size,
        "b": rev_b.size,
    }

    return diffs
