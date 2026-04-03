"""Eksport af metadata til JSON og CSV."""

import csv
import io
import json
from pathlib import Path
from typing import Any

from core.batch import BatchResult


def export_metadata_json(metadata: dict[str, Any], filepath: str | Path) -> None:
    """Eksportér metadata til JSON-fil."""
    filepath = Path(filepath)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)


def export_metadata_csv(metadata: dict[str, Any], filepath: str | Path) -> None:
    """Eksportér metadata til CSV-fil med BOM for Excel."""
    filepath = Path(filepath)
    rows = _flatten_metadata(metadata)

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Kategori", "Felt", "Værdi"])
        for category, field, value in rows:
            writer.writerow([category, field, value])


def export_batch_csv(results: list[BatchResult], filepath: str | Path) -> None:
    """Eksportér batch-resultater til CSV med BOM for Excel."""
    filepath = Path(filepath)

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "Filnavn", "Sider", "Forfatter", "Dato",
            "Værktøj", "Revisioner", "Størrelse (bytes)", "Fejl"
        ])
        for r in results:
            writer.writerow([
                r.filename,
                r.pages or "",
                r.author,
                r.date,
                r.tool,
                r.revision_count,
                r.size_bytes,
                r.error or "",
            ])


def metadata_to_json_string(metadata: dict[str, Any]) -> str:
    """Konvertér metadata til JSON-streng."""
    return json.dumps(metadata, ensure_ascii=False, indent=2, default=str)


def _flatten_metadata(metadata: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Flad metadata ud til (kategori, felt, værdi) tupler."""
    rows = []
    category_names = {
        "file_info": "Filinformation",
        "doc_info": "Dokument Info",
        "xmp": "XMP Metadata",
        "pdf_properties": "PDF Egenskaber",
    }

    for section_key, section_data in metadata.items():
        category = category_names.get(section_key, section_key)
        if isinstance(section_data, dict):
            for key, val in section_data.items():
                if key.startswith("_"):
                    continue
                rows.append((category, key, _format_value(val)))
        else:
            rows.append((category, "", _format_value(section_data)))

    return rows


def _format_value(val: Any) -> str:
    """Formatér en værdi til streng for CSV."""
    if val is None:
        return ""
    if isinstance(val, bool):
        return "Ja" if val else "Nej"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)
