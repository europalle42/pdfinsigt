"""Visuel tidslinje-widget til revisionshistorik."""

import tkinter as tk
from typing import Callable

import ttkbootstrap as ttk

from core.revisions import Revision
from i18n.da import t, format_size


# Colors for revision types
COLORS = {
    "created": "#2196F3",       # Blue
    "modified": "#FF9800",      # Orange
    "metadata_removed": "#F44336",  # Red
}


class TimelineWidget(ttk.Frame):
    """Visuel tidslinje med farvede cirkler per revision."""

    def __init__(self, parent, on_revision_click: Callable[[Revision], None] | None = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.on_revision_click = on_revision_click
        self.revisions: list[Revision] = []
        self.selected_index: int | None = None
        self._circles: list[int] = []  # canvas item IDs

        self._build()

    def _build(self):
        # Legend
        legend_frame = ttk.Frame(self)
        legend_frame.pack(fill="x", padx=10, pady=(10, 5))

        for rev_type, color in COLORS.items():
            label_key = f"timeline_{rev_type}"
            f = ttk.Frame(legend_frame)
            f.pack(side="left", padx=(0, 15))
            canvas = tk.Canvas(f, width=12, height=12, highlightthickness=0,
                               bg=self.winfo_toplevel().cget("bg"))
            canvas.pack(side="left", padx=(0, 4))
            canvas.create_oval(1, 1, 11, 11, fill=color, outline="")
            ttk.Label(f, text=t(label_key), font=("Segoe UI", 9)).pack(side="left")

        # Canvas for timeline
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill="x", padx=10, pady=10)

        self.canvas = tk.Canvas(
            canvas_frame,
            height=80,
            highlightthickness=0,
            bg="#ffffff",
        )
        self.canvas.pack(fill="x", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        self.canvas.bind("<Button-1>", self._on_click)

        # Scrollable for many revisions
        self.h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal",
                                      command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set)

    def load_revisions(self, revisions: list[Revision]):
        """Indlæs revisioner og tegn tidslinje."""
        self.revisions = revisions
        self.selected_index = None
        self._draw()

    def _draw(self):
        """Tegn tidslinjen på canvas."""
        self.canvas.delete("all")
        self._circles = []

        if not self.revisions:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2, 40,
                text=t("no_revisions"),
                font=("Segoe UI", 10),
                fill="#888",
            )
            self.h_scroll.pack_forget()
            return

        n = len(self.revisions)
        canvas_width = self.canvas.winfo_width()

        # Calculate spacing
        circle_r = 16
        spacing = max(60, min(100, canvas_width // max(n, 1)))
        total_width = spacing * n + 40

        if total_width > canvas_width:
            self.canvas.configure(scrollregion=(0, 0, total_width, 80))
            self.h_scroll.pack(fill="x")
        else:
            self.canvas.configure(scrollregion=(0, 0, canvas_width, 80))
            self.h_scroll.pack_forget()
            # Center
            spacing = canvas_width // max(n + 1, 2)

        y_center = 40

        for i, rev in enumerate(self.revisions):
            x = spacing * (i + 1) if total_width <= canvas_width else 30 + spacing * i
            color = COLORS.get(rev.revision_type, COLORS["modified"])

            # Line between circles
            if i > 0:
                prev_x = spacing * i if total_width <= canvas_width else 30 + spacing * (i - 1)
                self.canvas.create_line(prev_x + circle_r, y_center,
                                        x - circle_r, y_center,
                                        fill="#ccc", width=2)

            # Selection highlight
            if i == self.selected_index:
                self.canvas.create_oval(
                    x - circle_r - 4, y_center - circle_r - 4,
                    x + circle_r + 4, y_center + circle_r + 4,
                    fill="", outline=color, width=2,
                )

            # Circle
            circle_id = self.canvas.create_oval(
                x - circle_r, y_center - circle_r,
                x + circle_r, y_center + circle_r,
                fill=color, outline="white", width=2,
            )
            self._circles.append(circle_id)

            # Revision number inside circle
            self.canvas.create_text(
                x, y_center,
                text=str(rev.number),
                font=("Segoe UI", 10, "bold"),
                fill="white",
            )

            # Date label below
            date_str = self._get_date(rev)
            if date_str:
                self.canvas.create_text(
                    x, y_center + circle_r + 12,
                    text=date_str,
                    font=("Segoe UI", 7),
                    fill="#666",
                )

    def _on_click(self, event):
        """Håndtér klik på tidslinje."""
        item = self.canvas.find_closest(event.x, event.y)
        if item and item[0] in self._circles:
            idx = self._circles.index(item[0])
            self.selected_index = idx
            self._draw()
            if self.on_revision_click and idx < len(self.revisions):
                self.on_revision_click(self.revisions[idx])

    def _get_date(self, rev: Revision) -> str:
        """Hent dato fra revision metadata."""
        for key in ["xmp:ModifyDate", "xmp:CreateDate", "/ModDate", "/CreationDate"]:
            if key in rev.metadata:
                val = rev.metadata[key]
                # Shorten for display
                if len(val) > 10:
                    return val[:10]
                return val
        return ""

    def clear(self):
        """Ryd tidslinjen."""
        self.revisions = []
        self.selected_index = None
        self.canvas.delete("all")
