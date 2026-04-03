"""Statusbjælke widget."""

import ttkbootstrap as ttk

from i18n.da import t


class StatusBar(ttk.Frame):
    """Statusbjælke i bunden af vinduet."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        self.config(padding=(10, 5))

        self.label = ttk.Label(
            self,
            text=t("status_ready"),
            font=("Segoe UI", 9),
            bootstyle="secondary",
        )
        self.label.pack(side="left")

        self.progress = ttk.Progressbar(
            self,
            length=150,
            mode="indeterminate",
            bootstyle="primary",
        )

    def set_status(self, text: str):
        """Sæt statustekst."""
        self.label.config(text=text)

    def show_progress(self):
        """Vis fremdriftsindikator."""
        self.progress.pack(side="right", padx=(10, 0))
        self.progress.start(10)

    def hide_progress(self):
        """Skjul fremdriftsindikator."""
        self.progress.stop()
        self.progress.pack_forget()

    def set_ready(self):
        """Sæt status til klar."""
        self.set_status(t("status_ready"))
        self.hide_progress()

    def set_error(self, msg: str):
        """Vis fejlbesked."""
        self.set_status(t("status_error", msg))
        self.hide_progress()
