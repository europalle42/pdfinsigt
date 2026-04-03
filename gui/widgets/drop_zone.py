"""Drag-and-drop zone widget til PDF-filer."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Callable

import ttkbootstrap as ttk

from i18n.da import t


class DropZone(ttk.Frame):
    """Drop-zone: klik for at vælge fil, viser filnavn efter valg."""

    def __init__(self, parent, on_file_selected: Callable[[str], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_file_selected = on_file_selected
        self.current_file: str | None = None

        self._build()

    def _build(self):
        self.config(padding=20)

        # Drop area frame with dashed-border look
        self.drop_frame = ttk.Frame(self, bootstyle="secondary")
        self.drop_frame.pack(fill="both", expand=True)

        # Inner content
        inner = ttk.Frame(self.drop_frame, padding=30)
        inner.pack(fill="both", expand=True)

        # Icon
        self.icon_label = ttk.Label(
            inner,
            text="📄",
            font=("Segoe UI Emoji", 36),
            anchor="center",
        )
        self.icon_label.pack(pady=(10, 5))

        # Main text
        self.text_label = ttk.Label(
            inner,
            text=t("drop_zone_text"),
            font=("Segoe UI", 12),
            anchor="center",
            justify="center",
        )
        self.text_label.pack(pady=5)

        # Hint
        self.hint_label = ttk.Label(
            inner,
            text=t("drop_zone_hint"),
            font=("Segoe UI", 9),
            bootstyle="secondary",
            anchor="center",
        )
        self.hint_label.pack(pady=(0, 10))

        # Browse button
        self.browse_btn = ttk.Button(
            inner,
            text=t("select_file"),
            bootstyle="primary-outline",
            command=self._browse,
        )
        self.browse_btn.pack(pady=5)

        # Make entire frame clickable
        for widget in [self.drop_frame, inner, self.icon_label,
                       self.text_label, self.hint_label]:
            widget.bind("<Button-1>", lambda e: self._browse())

    def _browse(self):
        filepath = filedialog.askopenfilename(
            title=t("select_file"),
            filetypes=[("PDF filer", "*.pdf"), ("Alle filer", "*.*")],
        )
        if filepath:
            self._set_file(filepath)

    def _set_file(self, filepath: str):
        self.current_file = filepath
        name = Path(filepath).name
        self.text_label.config(text=f"✓ {name}")
        self.icon_label.config(text="📑")
        self.hint_label.config(text=filepath)
        self.on_file_selected(filepath)

    def reset(self):
        self.current_file = None
        self.text_label.config(text=t("drop_zone_text"))
        self.icon_label.config(text="📄")
        self.hint_label.config(text=t("drop_zone_hint"))
