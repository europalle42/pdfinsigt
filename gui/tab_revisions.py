"""Fane 2: Revisioner — tidslinje og detaljevisning."""

import threading

import ttkbootstrap as ttk

from core.revisions import Revision, extract_revisions
from gui.widgets.timeline import TimelineWidget
from i18n.da import t, format_size


class TabRevisions(ttk.Frame):
    """Revisioner fane med visuel tidslinje og detaljer."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.current_filepath: str | None = None
        self.revisions: list[Revision] = []
        self._build()

    def _build(self):
        # Header with info
        header = ttk.Frame(self, padding=10)
        header.pack(fill="x")

        self.info_label = ttk.Label(
            header,
            text=t("load_pdf_first"),
            font=("Segoe UI", 11),
        )
        self.info_label.pack(side="left")

        self.analyze_btn = ttk.Button(
            header,
            text=t("analyze_revisions"),
            bootstyle="primary",
            command=self._analyze,
            state="disabled",
        )
        self.analyze_btn.pack(side="right")

        # Timeline
        self.timeline = TimelineWidget(
            self,
            on_revision_click=self._on_revision_click,
        )
        self.timeline.pack(fill="x", padx=10)

        # Revision count
        self.count_label = ttk.Label(
            self,
            text="",
            font=("Segoe UI", 10),
            padding=(10, 5),
        )
        self.count_label.pack(fill="x")

        # Details panel
        detail_frame = ttk.LabelFrame(self, text=t("revision_detail"))
        detail_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Detail treeview
        self.detail_tree = ttk.Treeview(
            detail_frame,
            columns=("value",),
            show="tree headings",
            height=10,
        )
        self.detail_tree.heading("#0", text="Felt", anchor="w")
        self.detail_tree.heading("value", text="Værdi", anchor="w")
        self.detail_tree.column("#0", width=200, minwidth=120)
        self.detail_tree.column("value", width=400, minwidth=200)

        scroll = ttk.Scrollbar(detail_frame, orient="vertical",
                                command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=scroll.set)
        self.detail_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def set_file(self, filepath: str):
        """Sæt fil fra Enkelt PDF fanen."""
        self.current_filepath = filepath
        self.info_label.config(text=f"Fil: {filepath}")
        self.analyze_btn.config(state="normal")
        self.timeline.clear()
        self.detail_tree.delete(*self.detail_tree.get_children())
        self.count_label.config(text="")

    def _analyze(self):
        """Analysér revisioner i baggrundstråd."""
        if not self.current_filepath:
            return

        self.analyze_btn.config(state="disabled", text=t("analyzing"))
        self.app.set_status(t("status_analyzing"))
        self.app.show_progress()

        def _run():
            try:
                revs = extract_revisions(self.current_filepath)
                self.after(0, lambda: self._display_revisions(revs))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=_run, daemon=True).start()

    def _display_revisions(self, revisions: list[Revision]):
        """Vis revisioner i tidslinje."""
        self.revisions = revisions
        self.timeline.load_revisions(revisions)
        self.count_label.config(text=t("revision_count", len(revisions)))
        self.analyze_btn.config(state="normal", text=t("analyze_revisions"))
        self.app.set_ready()

        if revisions:
            self._show_revision_details(revisions[-1])

    def _on_revision_click(self, revision: Revision):
        """Vis detaljer for valgt revision."""
        self._show_revision_details(revision)

    def _show_revision_details(self, rev: Revision):
        """Vis detaljer for én revision."""
        self.detail_tree.delete(*self.detail_tree.get_children())

        # Basic info
        self.detail_tree.insert("", "end", text=t("rev_number", rev.number), values=("",))
        self.detail_tree.insert("", "end", text=t("rev_size"), values=(format_size(rev.size),))

        if rev.pages is not None:
            self.detail_tree.insert("", "end", text=t("rev_pages"), values=(str(rev.pages),))

        # Type
        type_labels = {
            "created": t("rev_created"),
            "modified": t("rev_modified"),
            "metadata_removed": t("rev_metadata_removed"),
        }
        type_label = type_labels.get(rev.revision_type, rev.revision_type)
        self.detail_tree.insert("", "end", text="Type", values=(type_label,))

        # Metadata
        if rev.metadata:
            meta_parent = self.detail_tree.insert("", "end", text="Metadata",
                                                   values=("",), open=True)
            for key, val in rev.metadata.items():
                display_key = key.lstrip("/")
                self.detail_tree.insert(meta_parent, "end", text=display_key,
                                        values=(str(val),))

    def _on_error(self, msg: str):
        self.analyze_btn.config(state="normal", text=t("analyze_revisions"))
        self.app.set_error(msg)
