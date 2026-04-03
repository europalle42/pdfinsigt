"""Test core modules med syntetiske PDFer."""

import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pikepdf


def create_test_pdf(path: str, title: str = "Test", author: str = "Tester",
                    pages: int = 3) -> None:
    """Opret en test-PDF med metadata."""
    pdf = pikepdf.Pdf.new()
    for i in range(pages):
        pdf.add_blank_page(page_size=(595, 842))  # A4

    with pdf.open_metadata() as meta:
        meta["dc:title"] = title
        meta["dc:creator"] = [author]
        meta["xmp:CreatorTool"] = "PDFIndsigt Test"
        meta["xmp:CreateDate"] = datetime.now().isoformat()

    pdf.save(path)


def create_multi_revision_pdf(path: str) -> None:
    """Opret en PDF med flere revisioner (inkrementelle opdateringer)."""
    # Version 1
    pdf = pikepdf.Pdf.new()
    pdf.add_blank_page(page_size=(595, 842))

    with pdf.open_metadata() as meta:
        meta["dc:title"] = "Original titel"
        meta["dc:creator"] = ["Forfatter A"]
        meta["xmp:CreateDate"] = "2024-01-15T10:00:00"

    pdf.save(path)

    # Version 2 — incremental save
    pdf2 = pikepdf.open(path, allow_overwriting_input=True)
    with pdf2.open_metadata() as meta:
        meta["dc:title"] = "Ændret titel"
        meta["xmp:ModifyDate"] = "2024-03-20T14:30:00"

    pdf2.save(path, linearize=False)
    pdf2.close()

    # Version 3 — another incremental save
    pdf3 = pikepdf.open(path, allow_overwriting_input=True)
    pdf3.add_blank_page(page_size=(595, 842))

    with pdf3.open_metadata() as meta:
        meta["dc:title"] = "Endelig version"
        meta["dc:creator"] = ["Forfatter B"]
        meta["xmp:ModifyDate"] = "2024-06-10T09:15:00"

    pdf3.save(path, linearize=False)
    pdf3.close()


def test_metadata():
    """Test metadata-udtræk."""
    from core.metadata import extract_metadata

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name

    try:
        create_test_pdf(path, title="Kommunal rapport", author="København Kommune", pages=5)
        meta = extract_metadata(path)

        print("=== Metadata Test ===")
        print(f"Filnavn: {meta['file_info']['filename']}")
        print(f"Sider: {meta['file_info']['pages']}")
        print(f"PDF-version: {meta['file_info']['pdf_version']}")
        print(f"Krypteret: {meta['file_info']['encrypted']}")
        print(f"Doc Info: {meta['doc_info']}")
        print(f"XMP nøgler: {list(meta['xmp'].keys())}")
        print(f"Egenskaber: {meta['pdf_properties']}")

        assert meta['file_info']['pages'] == 5, f"Forventede 5 sider, fik {meta['file_info']['pages']}"
        assert meta['file_info']['encrypted'] == False
        print("OK: Metadata test bestået\n")
    finally:
        os.unlink(path)


def test_revisions():
    """Test revisionshistorik."""
    from core.revisions import extract_revisions

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name

    try:
        create_multi_revision_pdf(path)
        revisions = extract_revisions(path)

        print("=== Revisions Test ===")
        print(f"Antal revisioner: {len(revisions)}")
        for rev in revisions:
            print(f"  Rev {rev.number}: type={rev.revision_type}, "
                  f"size={rev.size}, pages={rev.pages}")
            if rev.metadata:
                for k, v in rev.metadata.items():
                    print(f"    {k}: {v}")

        assert len(revisions) >= 1, "Forventede mindst 1 revision"
        print("OK: Revisions test bestået\n")
    finally:
        os.unlink(path)


def test_batch():
    """Test mappeanalyse."""
    from core.batch import analyze_folder

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 5 test PDFs
        for i in range(5):
            path = os.path.join(tmpdir, f"test_{i+1}.pdf")
            create_test_pdf(path, title=f"Dokument {i+1}",
                            author=f"Forfatter {chr(65+i)}", pages=i+1)

        results, stats = analyze_folder(tmpdir)

        print("=== Batch Test ===")
        print(f"Filer: {stats.total_files}")
        print(f"Sider i alt: {stats.total_pages}")
        print(f"Unikke forfattere: {stats.unique_authors}")
        for r in results:
            print(f"  {r.filename}: {r.pages} sider, forfatter={r.author}")

        assert stats.total_files == 5, f"Forventede 5 filer, fik {stats.total_files}"
        assert stats.total_pages == 15, f"Forventede 15 sider, fik {stats.total_pages}"
        print("OK: Batch test bestået\n")


def test_diff():
    """Test sammenligning."""
    from core.diff import compare_files

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f1:
        path_a = f1.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f2:
        path_b = f2.name

    try:
        create_test_pdf(path_a, title="Version A", author="Forfatter A", pages=3)
        create_test_pdf(path_b, title="Version B", author="Forfatter B", pages=5)

        diffs = compare_files(path_a, path_b)

        print("=== Diff Test ===")
        for d in diffs:
            print(f"  {d.field}: {d.status} ({d.value_a} → {d.value_b})")

        changed = [d for d in diffs if d.status != "identical"]
        assert len(changed) > 0, "Forventede mindst én forskel"
        print("OK: Diff test bestået\n")
    finally:
        os.unlink(path_a)
        os.unlink(path_b)


def test_export():
    """Test eksport."""
    from core.metadata import extract_metadata
    from core.export import export_metadata_json, export_metadata_csv

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name

    try:
        create_test_pdf(path, title="Eksport test", author="Testbruger")
        meta = extract_metadata(path)

        # JSON
        json_path = path + ".json"
        export_metadata_json(meta, json_path)
        import json
        with open(json_path, encoding="utf-8") as jf:
            data = json.load(jf)
        assert "file_info" in data
        print("=== Export Test ===")
        print(f"JSON eksport OK ({os.path.getsize(json_path)} bytes)")
        os.unlink(json_path)

        # CSV
        csv_path = path + ".csv"
        export_metadata_csv(meta, csv_path)
        with open(csv_path, encoding="utf-8-sig") as cf:
            lines = cf.readlines()
        assert len(lines) > 1
        print(f"CSV eksport OK ({len(lines)} rækker)")
        os.unlink(csv_path)

        print("OK: Export test bestået\n")
    finally:
        os.unlink(path)


if __name__ == "__main__":
    print("PDFIndsigt — Kerne-tests\n")
    test_metadata()
    test_revisions()
    test_batch()
    test_diff()
    test_export()
    print("=== Alle tests bestået! ===")
