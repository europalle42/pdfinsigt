"""Mappeanalyse — parallel batch-analyse af PDF-filer."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from core.metadata import extract_metadata
from core.revisions import find_eof_offsets


@dataclass
class BatchResult:
    """Resultat for én fil i batch-analyse."""
    filepath: str
    filename: str
    size_bytes: int
    pages: int | None
    author: str
    date: str
    tool: str
    revision_count: int
    error: str | None = None


@dataclass
class BatchStats:
    """Samlet statistik for batch-analyse."""
    total_files: int = 0
    total_pages: int = 0
    unique_authors: list[str] | None = None
    date_min: str = ""
    date_max: str = ""
    errors: int = 0


def analyze_folder(
    folder: str | Path,
    progress_callback: Callable[[int, int, str], None] | None = None,
    max_workers: int = 4,
) -> tuple[list[BatchResult], BatchStats]:
    """Analysér alle PDF-filer i en mappe parallelt.

    Args:
        folder: Sti til mappen
        progress_callback: Funktion(current, total, filename) for fremdrift
        max_workers: Antal parallelle tråde

    Returns:
        (liste af BatchResult, BatchStats)
    """
    folder = Path(folder)
    pdf_files = sorted(folder.glob("*.pdf"))

    if not pdf_files:
        return [], BatchStats()

    results: list[BatchResult] = []
    total = len(pdf_files)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_analyze_single, fp): fp
            for fp in pdf_files
        }

        for i, future in enumerate(as_completed(futures)):
            fp = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(BatchResult(
                    filepath=str(fp),
                    filename=fp.name,
                    size_bytes=fp.stat().st_size,
                    pages=None,
                    author="",
                    date="",
                    tool="",
                    revision_count=0,
                    error=str(e),
                ))

            if progress_callback:
                progress_callback(i + 1, total, fp.name)

    # Sort by filename
    results.sort(key=lambda r: r.filename.lower())

    stats = _compute_stats(results)
    return results, stats


def _analyze_single(filepath: Path) -> BatchResult:
    """Analysér en enkelt PDF-fil."""
    meta = extract_metadata(filepath)
    file_info = meta["file_info"]
    doc_info = meta["doc_info"]
    xmp = meta["xmp"]

    # Count revisions via EOF markers
    data = filepath.read_bytes()
    eof_offsets = find_eof_offsets(data)
    rev_count = len(eof_offsets)

    # Get author from doc_info or xmp
    author = doc_info.get("Author", "")
    if not author:
        author = xmp.get("dc:creator", "")

    # Get date
    date = doc_info.get("CreationDate", "")
    if not date:
        date = xmp.get("xmp:CreateDate", "")

    # Get tool
    tool = doc_info.get("Creator", "")
    if not tool:
        tool = xmp.get("xmp:CreatorTool", "")

    return BatchResult(
        filepath=str(filepath),
        filename=file_info["filename"],
        size_bytes=file_info["size_bytes"],
        pages=file_info.get("pages"),
        author=author,
        date=date,
        tool=tool,
        revision_count=rev_count,
    )


def _compute_stats(results: list[BatchResult]) -> BatchStats:
    """Beregn samlet statistik."""
    stats = BatchStats()
    stats.total_files = len(results)
    stats.errors = sum(1 for r in results if r.error)

    pages = [r.pages for r in results if r.pages is not None]
    stats.total_pages = sum(pages)

    authors = set(r.author for r in results if r.author)
    stats.unique_authors = sorted(authors)

    dates = [r.date for r in results if r.date]
    if dates:
        stats.date_min = min(dates)
        stats.date_max = max(dates)

    return stats
