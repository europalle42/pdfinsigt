"""Metadata-udtræk fra PDF-filer med pikepdf og pypdf."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pikepdf
from pypdf import PdfReader


def extract_metadata(filepath: str | Path) -> dict[str, Any]:
    """Udtræk al metadata fra en PDF-fil.

    Returnerer dict med:
        file_info: filnavn, størrelse, sider, version, kryptering
        doc_info: Document Info dictionary (Title, Author, etc.)
        xmp: XMP metadata (dc:title, dc:creator, xmp:CreateDate, etc.)
        pdf_properties: sidestørrelser, formularfelter, etc.
    """
    filepath = Path(filepath)
    result = {
        "file_info": _extract_file_info(filepath),
        "doc_info": _extract_doc_info(filepath),
        "xmp": _extract_xmp(filepath),
        "pdf_properties": _extract_properties(filepath),
    }
    return result


def _extract_file_info(filepath: Path) -> dict[str, Any]:
    """Grundlæggende filinformation."""
    stat = filepath.stat()
    info = {
        "filename": filepath.name,
        "path": str(filepath),
        "size_bytes": stat.st_size,
        "file_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }

    try:
        with pikepdf.open(filepath) as pdf:
            info["pages"] = len(pdf.pages)
            info["pdf_version"] = str(pdf.pdf_version)
            info["encrypted"] = False
    except pikepdf.PasswordError:
        info["encrypted"] = True
        info["pages"] = None
        info["pdf_version"] = None
        # Try pypdf for basic info on encrypted files
        try:
            reader = PdfReader(str(filepath))
            info["pages"] = len(reader.pages)
        except Exception:
            pass

    return info


def _extract_doc_info(filepath: Path) -> dict[str, str]:
    """Document Info dictionary via pypdf."""
    result = {}
    try:
        reader = PdfReader(str(filepath))
        meta = reader.metadata
        if meta is None:
            return result

        field_map = {
            "/Title": "Title",
            "/Author": "Author",
            "/Subject": "Subject",
            "/Keywords": "Keywords",
            "/Creator": "Creator",
            "/Producer": "Producer",
            "/CreationDate": "CreationDate",
            "/ModDate": "ModDate",
        }
        for pdf_key, label in field_map.items():
            val = meta.get(pdf_key)
            if val:
                result[label] = _clean_value(str(val))

        # Extra fields beyond standard
        for key in meta:
            if key not in field_map and key.startswith("/"):
                label = key.lstrip("/")
                val = meta.get(key)
                if val:
                    result[label] = _clean_value(str(val))

    except Exception:
        pass
    return result


def _extract_xmp(filepath: Path) -> dict[str, Any]:
    """XMP metadata via pikepdf."""
    result = {}
    try:
        with pikepdf.open(filepath) as pdf:
            with pdf.open_metadata() as xmp:
                # Standard XMP namespaces
                ns_map = {
                    "dc:title": "dc:title",
                    "dc:creator": "dc:creator",
                    "dc:description": "dc:description",
                    "dc:subject": "dc:subject",
                    "dc:format": "dc:format",
                    "xmp:CreateDate": "xmp:CreateDate",
                    "xmp:ModifyDate": "xmp:ModifyDate",
                    "xmp:MetadataDate": "xmp:MetadataDate",
                    "xmp:CreatorTool": "xmp:CreatorTool",
                    "pdf:Producer": "pdf:Producer",
                    "pdf:PDFVersion": "pdf:PDFVersion",
                    "pdf:Keywords": "pdf:Keywords",
                    "xmpMM:DocumentID": "xmpMM:DocumentID",
                    "xmpMM:InstanceID": "xmpMM:InstanceID",
                }
                for key, label in ns_map.items():
                    try:
                        val = xmp.get(key)
                        if val:
                            result[label] = _clean_value(str(val))
                    except Exception:
                        pass

                # Get all other XMP keys (skip raw namespace URIs)
                try:
                    known_prefixes = set(ns_map.keys())
                    for key in xmp:
                        if key not in known_prefixes and not key.startswith("{"):
                            try:
                                val = xmp.get(key)
                                if val:
                                    result[key] = _clean_value(str(val))
                            except Exception:
                                pass
                except Exception:
                    pass

    except pikepdf.PasswordError:
        result["_error"] = "Filen er krypteret"
    except Exception:
        pass
    return result


def _extract_properties(filepath: Path) -> dict[str, Any]:
    """PDF-specifikke egenskaber."""
    result = {}
    try:
        reader = PdfReader(str(filepath))

        # Page sizes
        if reader.pages:
            page = reader.pages[0]
            box = page.mediabox
            width_pt = float(box.width)
            height_pt = float(box.height)
            width_mm = width_pt * 25.4 / 72
            height_mm = height_pt * 25.4 / 72
            result["page_size_pt"] = f"{width_pt:.0f} x {height_pt:.0f} pt"
            result["page_size_mm"] = f"{width_mm:.0f} x {height_mm:.0f} mm"

            # Detect standard sizes
            size_name = _detect_page_size(width_mm, height_mm)
            if size_name:
                result["page_format"] = size_name

        # Form fields
        if reader.get_fields():
            fields = reader.get_fields()
            result["form_fields"] = len(fields)
            result["form_field_names"] = list(fields.keys())[:20]  # max 20
        else:
            result["form_fields"] = 0

        # Attachments
        try:
            if "/Names" in reader.trailer["/Root"]:
                names = reader.trailer["/Root"]["/Names"]
                if "/EmbeddedFiles" in names:
                    result["has_attachments"] = True
        except Exception:
            pass

    except Exception:
        pass
    return result


def _detect_page_size(width_mm: float, height_mm: float) -> str | None:
    """Genkend standard papirstørrelser."""
    sizes = {
        "A4": (210, 297),
        "A3": (297, 420),
        "A5": (148, 210),
        "Letter": (216, 279),
        "Legal": (216, 356),
    }
    tolerance = 3  # mm
    for name, (w, h) in sizes.items():
        if (abs(width_mm - w) < tolerance and abs(height_mm - h) < tolerance) or \
           (abs(width_mm - h) < tolerance and abs(height_mm - w) < tolerance):
            return name
    return None


def _clean_value(val: str) -> str:
    """Rens metadata-værdi for uønskede tegn."""
    if not val:
        return ""
    # Remove PDF date prefix
    val = val.strip()
    if val.startswith("D:"):
        val = _parse_pdf_date(val)
    return val


def _parse_pdf_date(date_str: str) -> str:
    """Konvertér PDF-datoformat (D:YYYYMMDDHHmmSS) til læsbar dato."""
    try:
        s = date_str.replace("D:", "").replace("'", "")
        # Handle timezone offset
        if "+" in s:
            s = s[:s.index("+")]
        elif "Z" in s:
            s = s[:s.index("Z")]
        # Pad if short
        s = s.ljust(14, "0")
        dt = datetime.strptime(s[:14], "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_str
