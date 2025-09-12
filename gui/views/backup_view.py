# gui/views/backup_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht für Backup- und Wiederherstellungsoperationen.
"""
import customtkinter as ctk
from tkinter import filedialog
import logging

from ..widgets.custom_dialogs import CustomMessagebox
from ..widgets.accessible_widgets import AccessibleCTkButton

logger = logging.getLogger(__name__)

class BackupView(ctk.CTkFrame):
    """
    Eine Ansicht, die dem Benutzer ermöglicht, alle Anwendungsdaten
    in eine ZIP-Datei zu exportieren oder aus einer zu importieren.
    """
    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.controller = app_logic.controller
        
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Export-Bereich ---
        export_frame = ctk.CTkFrame(self)
        export_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        export_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(export_frame, text="Datenexport", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(export_frame, text="Sichert alle Konfigurationen, Berichte und Vorlagen\nin einer einzigen ZIP-Datei.", justify="center").pack(pady=5, padx=10)
        
        AccessibleCTkButton(
            export_frame, 
            text="Daten exportieren...", 
            command=self._export_data,
            accessible_text="Öffnet einen Dialog, um alle Anwendungsdaten in einer ZIP-Datei zu speichern.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        ).pack(pady=15)

        # --- Import-Bereich ---
        import_frame = ctk.CTkFrame(self)
        import_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        import_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(import_frame, text="Datenwiederherstellung", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        ctk.CTkLabel(import_frame, text="Stellt alle Daten aus einer zuvor erstellten\nBackup-ZIP-Datei wieder her.", justify="center").pack(pady=5, padx=10)
        
        AccessibleCTkButton(
            import_frame, 
            text="Daten importieren...", 
            fg_color="#D32F2F", 
            hover_color="#B71C1C", 
            command=self._show_import_warning,
            accessible_text="Warnung: Startet den Import aus einer Backup-Datei. Aktuelle Daten werden überschrieben.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        ).pack(pady=15)

    def _export_data(self) -> None:
        """Öffnet einen Dialog zum Speichern der ZIP-Datei und startet den Export."""
        zip_path = filedialog.asksaveasfilename(
            title="Backup-Datei speichern",
            defaultextension=".zip",
            filetypes=[("ZIP-Archive", "*.zip")],
            initialfile="berichtsheft_backup.zip"
        )
        if not zip_path:
            return

        success, message = self.controller.export_all_data(zip_path)

        # Verwende den benutzerdefinierten Dialog für die Erfolgs-/Fehlermeldung
        dialog_title = "Export erfolgreich" if success else "Exportfehler"
        CustomMessagebox(title=dialog_title, message=message).get_choice()

    
    def _show_import_warning(self):
        """Zeigt eine Warnung vor dem Import an."""
        dialog = CustomMessagebox(
            title="Warnung",
            message="Beim Importieren werden alle aktuellen Daten überschrieben.\nFortfahren?",
            buttons=["Ja, importieren", "Abbrechen"]
        )
        choice = dialog.get_choice()
        if choice == "Ja, importieren":
            self._import_data()

    def _import_data(self) -> None:
        """Öffnet einen Dialog zum Auswählen der ZIP-Datei und startet den Import."""
        zip_path = filedialog.askopenfilename(
            title="Backup-Datei öffnen",
            filetypes=[("ZIP-Archive", "*.zip")]
        )
        if not zip_path:
            return

        success, message = self.controller.import_all_data(zip_path)
        
        dialog_title = "Import erfolgreich" if success else "Importfehler"
        final_message = f"{message}\n\nDie Daten wurden aktualisiert." if success else message
        CustomMessagebox(title=dialog_title, message=final_message).get_choice()

        if success:
            self.app.reload_all_data()

