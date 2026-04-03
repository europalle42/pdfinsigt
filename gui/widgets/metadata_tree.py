"""Trævisning af metadata med udfoldelige sektioner."""

import tkinter as tk
from typing import Any

import ttkbootstrap as ttk

from i18n.da import t, format_size


class MetadataTree(ttk.Frame):
    """Trævisning af PDF-metadata med udfoldelige kategorier."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        # Treeview with scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("value",),
            show="tree headings",
            selectmode="browse",
            height=18,
        )
        self.tree.heading("#0", text="Felt", anchor="w")
        self.tree.heading("value", text="Værdi", anchor="w")
        self.tree.column("#0", width=250, minwidth=150)
        self.tree.column("value", width=400, minwidth=200)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_metadata(self, metadata: dict[str, Any]):
        """Indlæs metadata i træet."""
        self.tree.delete(*self.tree.get_children())

        section_labels = {
            "file_info": t("file_info"),
            "doc_info": t("doc_info"),
            "xmp": t("xmp_metadata"),
            "pdf_properties": t("pdf_properties"),
        }

        for section_key, section_data in metadata.items():
            if not isinstance(section_data, dict) or not section_data:
                continue

            label = section_labels.get(section_key, section_key)
            parent_id = self.tree.insert("", "end", text=label, open=True)

            for key, value in section_data.items():
                if key.startswith("_"):
                    continue
                display_val = self._format_value(key, value)
                display_key = self._translate_key(key)
                self.tree.insert(parent_id, "end", text=display_key,
                                 values=(display_val,))

    def clear(self):
        """Ryd træet."""
        self.tree.delete(*self.tree.get_children())

    def _format_value(self, key: str, value: Any) -> str:
        """Formatér værdi til visning."""
        if isinstance(value, bool):
            return t("yes") if value else t("no")
        if key == "size_bytes" and isinstance(value, (int, float)):
            return format_size(int(value))
        if isinstance(value, list):
            return ", ".join(str(v) for v in value[:10])
        return str(value) if value else t("none")

    def _translate_key(self, key: str) -> str:
        """Oversæt metadata-nøgler til dansk."""
        translations = {
            "filename": t("file_name"),
            "path": "Sti",
            "size_bytes": t("file_size"),
            "pages": t("file_pages"),
            "pdf_version": t("file_pdf_version"),
            "encrypted": t("file_encrypted"),
            "file_modified": "Fil ændret",
            "Title": "Titel",
            "Author": "Forfatter",
            "Subject": "Emne",
            "Keywords": "Nøgleord",
            "Creator": "Opretter",
            "Producer": "Producent",
            "CreationDate": "Oprettelsesdato",
            "ModDate": "Ændringsdato",
            "page_size_pt": "Sidestørrelse (pt)",
            "page_size_mm": "Sidestørrelse (mm)",
            "page_format": "Papirformat",
            "form_fields": "Formularfelter",
            "form_field_names": "Feltnavne",
            "has_attachments": "Vedhæftninger",
        }
        return translations.get(key, key)
