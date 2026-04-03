"""Fane 4: Sammenlign — side-om-side metadata-sammenligning."""

import threading
from tkinter import filedialog

import ttkbootstrap as ttk

from core.diff import compare_files, DiffEntry
from i18n.da import t


# Colors for diff status
DIFF_TAGS = {
    "identical": ("identical", "#2E7D32"),  # Green
    "changed": ("changed", "#F57F17"),      # Yellow/amber
    "removed": ("removed", "#C62828"),      # Red
    "added": ("added", "#1565C0"),          # Blue
}


class TabDiff(ttk.Frame):
    """Sammenlign fane med filvalg og farvekodede forskelle."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.file_a: str | None = None
        self.file_b: str | None = None
        self._build()

    def _build(self):
        # File selection
        sel_frame = ttk.Frame(self, padding=10)
        sel_frame.pack(fill="x")

        # File A
        fa = ttk.LabelFrame(sel_frame, text=t("file_a"))
        fa.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.label_a = ttk.Label(fa, text=t("no_files_selected"),
                                  font=("Segoe UI", 9))
        self.label_a.pack(side="left", fill="x", expand=True)

        ttk.Button(
            fa,
            text=t("select_file_a"),
            bootstyle="outline",
            command=lambda: self._select_file("a"),
        ).pack(side="right")

        # File B
        fb = ttk.LabelFrame(sel_frame, text=t("file_b"))
        fb.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.label_b = ttk.Label(fb, text=t("no_files_selected"),
                                  font=("Segoe UI", 9))
        self.label_b.pack(side="left", fill="x", expand=True)

        ttk.Button(
            fb,
            text=t("select_file_b"),
            bootstyle="outline",
            command=lambda: self._select_file("b"),
        ).pack(side="right")

        # Compare button
        btn_frame = ttk.Frame(self, padding=(10, 5))
        btn_frame.pack(fill="x")

        self.compare_btn = ttk.Button(
            btn_frame,
            text=t("compare_button"),
            bootstyle="primary",
            command=self._compare,
            state="disabled",
        )
        self.compare_btn.pack(side="left")

        # Legend
        legend = ttk.Frame(btn_frame)
        legend.pack(side="right")

        for status, (tag, color) in DIFF_TAGS.items():
            lf = ttk.Frame(legend)
            lf.pack(side="left", padx=(10, 0))
            # Color swatch
            import tkinter as tk
            c = tk.Canvas(lf, width=12, height=12, highlightthickness=0)
            c.pack(side="left", padx=(0, 3))
            c.create_rectangle(0, 0, 12, 12, fill=color, outline="")
            label_key = f"diff_{status}"
            ttk.Label(lf, text=t(label_key), font=("Segoe UI", 8)).pack(side="left")

        # Results table
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("field", "value_a", "value_b", "status")
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=18,
        )

        self.table.heading("field", text=t("diff_field"))
        self.table.heading("value_a", text=t("diff_value_a"))
        self.table.heading("value_b", text=t("diff_value_b"))
        self.table.heading("status", text=t("diff_status"))

        self.table.column("field", width=180, minwidth=100)
        self.table.column("value_a", width=220, minwidth=100)
        self.table.column("value_b", width=220, minwidth=100)
        self.table.column("status", width=100, minwidth=60)

        # Configure tags for coloring
        for status, (tag, color) in DIFF_TAGS.items():
            self.table.tag_configure(tag, foreground=color)

        scroll = ttk.Scrollbar(table_frame, orient="vertical",
                                command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _select_file(self, which: str):
        filepath = filedialog.askopenfilename(
            title=t("select_file"),
            filetypes=[("PDF filer", "*.pdf"), ("Alle filer", "*.*")],
        )
        if not filepath:
            return

        from pathlib import Path
        name = Path(filepath).name

        if which == "a":
            self.file_a = filepath
            self.label_a.config(text=name)
        else:
            self.file_b = filepath
            self.label_b.config(text=name)

        if self.file_a and self.file_b:
            self.compare_btn.config(state="normal")

    def _compare(self):
        if not self.file_a or not self.file_b:
            return

        self.compare_btn.config(state="disabled")
        self.app.set_status(t("status_analyzing"))
        self.app.show_progress()

        def _run():
            try:
                diffs = compare_files(self.file_a, self.file_b)
                self.after(0, lambda: self._display_diffs(diffs))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=_run, daemon=True).start()

    def _display_diffs(self, diffs: list[DiffEntry]):
        self.table.delete(*self.table.get_children())

        for diff in diffs:
            tag = DIFF_TAGS.get(diff.status, ("identical", "#000"))[0]
            status_label = t(f"diff_{diff.status}")
            self.table.insert(
                "", "end",
                values=(
                    diff.field,
                    diff.value_a or "—",
                    diff.value_b or "—",
                    status_label,
                ),
                tags=(tag,),
            )

        self.compare_btn.config(state="normal")
        self.app.set_ready()

    def _on_error(self, msg: str):
        self.compare_btn.config(state="normal")
        self.app.set_error(msg)
