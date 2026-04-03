"""Danske tekster til PDFIndsigt."""

TEXTS = {
    # App
    "app_title": "PDFIndsigt — PDF Metadata Analyse",
    "app_subtitle": "Analysér metadata og revisionshistorik i PDF-filer",

    # Faner
    "tab_single": "Enkelt PDF",
    "tab_revisions": "Revisioner",
    "tab_batch": "Mappeanalyse",
    "tab_diff": "Sammenlign",

    # Enkelt PDF fane
    "drop_zone_text": "Træk en PDF hertil\neller klik for at vælge",
    "drop_zone_hint": "Understøtter .pdf filer",
    "file_info": "Filinformation",
    "file_name": "Filnavn",
    "file_size": "Størrelse",
    "file_pages": "Sider",
    "file_pdf_version": "PDF-version",
    "file_encrypted": "Krypteret",
    "file_created": "Oprettet",
    "file_modified": "Ændret",
    "metadata_title": "Metadata",
    "doc_info": "Dokument Info",
    "xmp_metadata": "XMP Metadata",
    "pdf_properties": "PDF Egenskaber",
    "export_json": "Eksportér JSON",
    "export_csv": "Eksportér CSV",
    "no_metadata": "Ingen metadata fundet",
    "select_file": "Vælg PDF-fil",

    # Revisioner fane
    "revisions_title": "Revisionshistorik",
    "revision_count": "Antal revisioner: {}",
    "revision_detail": "Revisionsdetaljer",
    "rev_date": "Dato",
    "rev_author": "Forfatter",
    "rev_tool": "Værktøj",
    "rev_size": "Størrelse",
    "rev_pages": "Sider",
    "rev_number": "Revision {}",
    "rev_created": "Oprettet",
    "rev_modified": "Ændret",
    "rev_metadata_removed": "Metadata fjernet",
    "no_revisions": "Ingen revisioner fundet (kun én version)",
    "load_pdf_first": "Indlæs en PDF-fil først i 'Enkelt PDF' fanen",
    "analyze_revisions": "Analysér revisioner",
    "analyzing": "Analyserer...",

    # Tidslinje
    "timeline_created": "Oprettet",
    "timeline_modified": "Ændret",
    "timeline_removed": "Metadata fjernet",

    # Mappeanalyse fane
    "select_folder": "Vælg mappe",
    "batch_analyzing": "Analyserer {} filer...",
    "batch_complete": "Analyse fuldført: {} filer",
    "batch_error": "Fejl ved analyse af {}",
    "col_filename": "Filnavn",
    "col_pages": "Sider",
    "col_author": "Forfatter",
    "col_date": "Dato",
    "col_revisions": "Revisioner",
    "col_size": "Størrelse",
    "col_tool": "Værktøj",
    "stats_title": "Oversigt",
    "stats_total_files": "Filer i alt",
    "stats_total_pages": "Sider i alt",
    "stats_authors": "Unikke forfattere",
    "stats_date_range": "Datointerval",
    "export_batch_csv": "Eksportér alle til CSV",

    # Sammenlign fane
    "compare_files": "Sammenlign to filer",
    "compare_revisions": "Sammenlign to revisioner",
    "file_a": "Fil A",
    "file_b": "Fil B",
    "select_file_a": "Vælg fil A",
    "select_file_b": "Vælg fil B",
    "compare_button": "Sammenlign",
    "diff_identical": "Identisk",
    "diff_changed": "Ændret",
    "diff_removed": "Fjernet",
    "diff_added": "Tilføjet",
    "diff_field": "Felt",
    "diff_value_a": "Værdi A",
    "diff_value_b": "Værdi B",
    "diff_status": "Status",
    "no_files_selected": "Vælg to filer for at sammenligne",

    # Statusbjælke
    "status_ready": "Klar",
    "status_loading": "Indlæser...",
    "status_analyzing": "Analyserer...",
    "status_exporting": "Eksporterer...",
    "status_done": "Færdig",
    "status_error": "Fejl: {}",

    # Generelt
    "yes": "Ja",
    "no": "Nej",
    "unknown": "Ukendt",
    "none": "Ingen",
    "error": "Fejl",
    "cancel": "Annullér",
    "close": "Luk",
    "bytes": "bytes",
    "kb": "KB",
    "mb": "MB",
    "gb": "GB",
}


def t(key: str, *args) -> str:
    """Hent dansk tekst med valgfri formatering."""
    text = TEXTS.get(key, key)
    if args:
        return text.format(*args)
    return text


def format_size(size_bytes: int) -> str:
    """Formatér filstørrelse til læsbar tekst."""
    if size_bytes < 1024:
        return f"{size_bytes} {t('bytes')}"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} {t('kb')}"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} {t('mb')}"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} {t('gb')}"
