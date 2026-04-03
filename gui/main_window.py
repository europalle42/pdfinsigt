"""Hovedvindue med fanebaseret layout."""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from gui.tab_single import TabSingle
from gui.tab_revisions import TabRevisions
from gui.tab_batch import TabBatch
from gui.tab_diff import TabDiff
from gui.widgets.status_bar import StatusBar
from i18n.da import t


class MainWindow:
    """PDFIndsigt hovedvindue."""

    def __init__(self):
        self.root = ttk.Window(
            title=t("app_title"),
            themename="cosmo",
            size=(1000, 720),
            minsize=(800, 600),
        )
        self.root.place_window_center()

        self._build()

    def _build(self):
        # Header
        header = ttk.Frame(self.root, padding=(15, 10))
        header.pack(fill="x")

        ttk.Label(
            header,
            text=t("app_title"),
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left")

        ttk.Label(
            header,
            text=t("app_subtitle"),
            font=("Segoe UI", 10),
            bootstyle="secondary",
        ).pack(side="left", padx=(15, 0))

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root, bootstyle="primary")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # Create tabs
        self.tab_single = TabSingle(self.notebook, app=self)
        self.tab_revisions = TabRevisions(self.notebook, app=self)
        self.tab_batch = TabBatch(self.notebook, app=self)
        self.tab_diff = TabDiff(self.notebook, app=self)

        self.notebook.add(self.tab_single, text=f"  {t('tab_single')}  ")
        self.notebook.add(self.tab_revisions, text=f"  {t('tab_revisions')}  ")
        self.notebook.add(self.tab_batch, text=f"  {t('tab_batch')}  ")
        self.notebook.add(self.tab_diff, text=f"  {t('tab_diff')}  ")

        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill="x", side="bottom")

    # --- App-level methods called by tabs ---

    def on_file_loaded(self, filepath: str, metadata: dict):
        """Kaldt når en fil er indlæst i Enkelt PDF fanen."""
        self.tab_revisions.set_file(filepath)

    def set_status(self, text: str):
        self.status_bar.set_status(text)

    def show_progress(self):
        self.status_bar.show_progress()

    def set_ready(self):
        self.status_bar.set_ready()

    def set_error(self, msg: str):
        self.status_bar.set_error(msg)

    def run(self):
        self.root.mainloop()
