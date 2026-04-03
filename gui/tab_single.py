"""Fane 1: Enkelt PDF — metadata-visning med drag-and-drop."""

import threading
from pathlib import Path
from tkinter import filedialog

import ttkbootstrap as ttk

from core.metadata import extract_metadata
from core.export import export_metadata_json, export_metadata_csv
from gui.widgets.drop_zone import DropZone
from gui.widgets.metadata_tree import MetadataTree
from i18n.da import t


class TabSingle(ttk.Frame):
    """Enkelt PDF fane med filinformation og metadata-træ."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.current_metadata: dict | None = None
        self.current_filepath: str | None = None
        self._build()

    def _build(self):
        # Top: drop zone
        self.drop_zone = DropZone(self, on_file_selected=self._on_file_selected)
        self.drop_zone.pack(fill="x", padx=10, pady=10)

        # Middle: metadata tree
        self.metadata_tree = MetadataTree(self)
        self.metadata_tree.pack(fill="both", expand=True, padx=10)

        # Bottom: export buttons
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill="x")

        self.btn_json = ttk.Button(
            btn_frame,
            text=t("export_json"),
            bootstyle="info-outline",
            command=self._export_json,
            state="disabled",
        )
        self.btn_json.pack(side="left", padx=(0, 5))

        self.btn_csv = ttk.Button(
            btn_frame,
            text=t("export_csv"),
            bootstyle="info-outline",
            command=self._export_csv,
            state="disabled",
        )
        self.btn_csv.pack(side="left")

    def _on_file_selected(self, filepath: str):
        """Håndtér filvalg — indlæs metadata i baggrundstråd."""
        self.current_filepath = filepath
        self.app.set_status(t("status_loading"))
        self.app.show_progress()

        def _load():
            try:
                meta = extract_metadata(filepath)
                self.after(0, lambda: self._display_metadata(meta))
            except Exception as e:
                self.after(0, lambda: self.app.set_error(str(e)))

        threading.Thread(target=_load, daemon=True).start()

    def _display_metadata(self, metadata: dict):
        """Vis metadata i træet."""
        self.current_metadata = metadata
        self.metadata_tree.load_metadata(metadata)
        self.btn_json.config(state="normal")
        self.btn_csv.config(state="normal")

        # Notify app that file is loaded (for revisions tab)
        self.app.on_file_loaded(self.current_filepath, metadata)
        self.app.set_ready()

    def _export_json(self):
        if not self.current_metadata:
            return
        name = Path(self.current_filepath).stem if self.current_filepath else "metadata"
        filepath = filedialog.asksaveasfilename(
            title=t("export_json"),
            defaultextension=".json",
            initialfile=f"{name}_metadata.json",
            filetypes=[("JSON", "*.json")],
        )
        if filepath:
            self.app.set_status(t("status_exporting"))
            export_metadata_json(self.current_metadata, filepath)
            self.app.set_ready()

    def _export_csv(self):
        if not self.current_metadata:
            return
        name = Path(self.current_filepath).stem if self.current_filepath else "metadata"
        filepath = filedialog.asksaveasfilename(
            title=t("export_csv"),
            defaultextension=".csv",
            initialfile=f"{name}_metadata.csv",
            filetypes=[("CSV", "*.csv")],
        )
        if filepath:
            self.app.set_status(t("status_exporting"))
            export_metadata_csv(self.current_metadata, filepath)
            self.app.set_ready()
