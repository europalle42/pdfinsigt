"""Fane 3: Mappeanalyse — parallel batch-analyse af PDF-filer."""

import threading
from tkinter import filedialog

import ttkbootstrap as ttk

from core.batch import analyze_folder, BatchResult, BatchStats
from core.export import export_batch_csv
from i18n.da import t, format_size


class TabBatch(ttk.Frame):
    """Mappeanalyse fane med sorterbar tabel og statistik."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.results: list[BatchResult] = []
        self.sort_column: str = "filename"
        self.sort_reverse: bool = False
        self._build()

    def _build(self):
        # Top bar
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        self.folder_btn = ttk.Button(
            top,
            text=t("select_folder"),
            bootstyle="primary",
            command=self._select_folder,
        )
        self.folder_btn.pack(side="left")

        self.folder_label = ttk.Label(top, text="", font=("Segoe UI", 9))
        self.folder_label.pack(side="left", padx=10)

        self.export_btn = ttk.Button(
            top,
            text=t("export_batch_csv"),
            bootstyle="info-outline",
            command=self._export_csv,
            state="disabled",
        )
        self.export_btn.pack(side="right")

        # Stats panel
        stats_frame = ttk.LabelFrame(self, text=t("stats_title"))
        stats_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.stats_labels = {}
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill="x")

        stat_keys = [
            ("stats_total_files", 0, 0),
            ("stats_total_pages", 0, 1),
            ("stats_authors", 1, 0),
            ("stats_date_range", 1, 1),
        ]
        for key, row, col in stat_keys:
            f = ttk.Frame(stats_grid)
            f.grid(row=row, column=col, sticky="w", padx=(0, 30), pady=2)
            ttk.Label(f, text=f"{t(key)}:", font=("Segoe UI", 9, "bold")).pack(side="left")
            lbl = ttk.Label(f, text="—", font=("Segoe UI", 9))
            lbl.pack(side="left", padx=(5, 0))
            self.stats_labels[key] = lbl

        # Table
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("pages", "author", "date", "tool", "revisions", "size")
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15,
        )

        col_config = {
            "pages": (t("col_pages"), 60),
            "author": (t("col_author"), 150),
            "date": (t("col_date"), 140),
            "tool": (t("col_tool"), 150),
            "revisions": (t("col_revisions"), 80),
            "size": (t("col_size"), 90),
        }

        # Add filename as #0 tree column
        self.table.heading("#0", text=t("col_filename"),
                           command=lambda: self._sort("filename"))
        self.table.column("#0", width=200, minwidth=120)

        for col_id, (heading, width) in col_config.items():
            self.table.heading(col_id, text=heading,
                               command=lambda c=col_id: self._sort(c))
            self.table.column(col_id, width=width, minwidth=50)

        scroll = ttk.Scrollbar(table_frame, orient="vertical",
                                command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Progress bar
        self.progress_var = ttk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            bootstyle="primary",
        )

    def _select_folder(self):
        folder = filedialog.askdirectory(title=t("select_folder"))
        if not folder:
            return

        self.folder_label.config(text=folder)
        self.folder_btn.config(state="disabled")
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5))
        self.app.set_status(t("status_analyzing"))

        def _run():
            try:
                results, stats = analyze_folder(
                    folder,
                    progress_callback=self._on_progress,
                )
                self.after(0, lambda: self._display_results(results, stats))
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=_run, daemon=True).start()

    def _on_progress(self, current: int, total: int, filename: str):
        pct = int(current / total * 100) if total > 0 else 0
        self.after(0, lambda: self.progress_var.set(pct))
        self.after(0, lambda: self.app.set_status(
            t("batch_analyzing", f"{current}/{total}")))

    def _display_results(self, results: list[BatchResult], stats: BatchStats):
        self.results = results
        self.table.delete(*self.table.get_children())

        for r in results:
            values = (
                r.pages or "",
                r.author,
                r.date,
                r.tool,
                r.revision_count,
                format_size(r.size_bytes),
            )
            self.table.insert("", "end", text=r.filename, values=values)

        # Update stats
        self.stats_labels["stats_total_files"].config(text=str(stats.total_files))
        self.stats_labels["stats_total_pages"].config(text=str(stats.total_pages))
        authors_text = str(len(stats.unique_authors)) if stats.unique_authors else "0"
        self.stats_labels["stats_authors"].config(text=authors_text)
        date_text = f"{stats.date_min} — {stats.date_max}" if stats.date_min else "—"
        self.stats_labels["stats_date_range"].config(text=date_text)

        self.folder_btn.config(state="normal")
        self.export_btn.config(state="normal")
        self.progress_bar.pack_forget()
        self.app.set_status(t("batch_complete", len(results)))

    def _sort(self, column: str):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        if not self.results:
            return

        key_map = {
            "filename": lambda r: r.filename.lower(),
            "pages": lambda r: r.pages or 0,
            "author": lambda r: r.author.lower(),
            "date": lambda r: r.date,
            "tool": lambda r: r.tool.lower(),
            "revisions": lambda r: r.revision_count,
            "size": lambda r: r.size_bytes,
        }

        key_fn = key_map.get(column, key_map["filename"])
        self.results.sort(key=key_fn, reverse=self.sort_reverse)

        # Re-display
        self.table.delete(*self.table.get_children())
        for r in self.results:
            values = (
                r.pages or "",
                r.author,
                r.date,
                r.tool,
                r.revision_count,
                format_size(r.size_bytes),
            )
            self.table.insert("", "end", text=r.filename, values=values)

    def _export_csv(self):
        if not self.results:
            return
        filepath = filedialog.asksaveasfilename(
            title=t("export_batch_csv"),
            defaultextension=".csv",
            initialfile="mappeanalyse.csv",
            filetypes=[("CSV", "*.csv")],
        )
        if filepath:
            self.app.set_status(t("status_exporting"))
            export_batch_csv(self.results, filepath)
            self.app.set_ready()

    def _on_error(self, msg: str):
        self.folder_btn.config(state="normal")
        self.progress_bar.pack_forget()
        self.app.set_error(msg)
