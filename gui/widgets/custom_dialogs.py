# gui/widgets/custom_dialogs.py
# -*- coding: utf-8 -*-
"""
Definiert benutzerdefinierte Dialogfenster, die zum Stil von CustomTkinter passen.
"""
import customtkinter as ctk

class CustomMessagebox(ctk.CTkToplevel):
    """
    Ein benutzerdefiniertes, blockierendes Dialogfenster,
    das die Standard-Messagebox ersetzt.
    """
    def __init__(self, title: str = "Dialog", message: str = "", buttons: list = None):
        super().__init__()

        if buttons is None:
            buttons = ["OK"]
        
        self.title(title)
        self.lift()  # Hebt das Fenster in den Vordergrund
        self.attributes("-topmost", True)  # Hält es über dem Hauptfenster
        self.grab_set()  # Blockiert das Hauptfenster

        self._choice = ""
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(main_frame, text=message, wraplength=300, justify="center").pack(padx=20, pady=(20, 10))

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(padx=20, pady=20, fill="x")
        
        for i, button_text in enumerate(buttons):
            button_frame.grid_columnconfigure(i, weight=1)
            btn = ctk.CTkButton(button_frame, text=button_text, command=lambda choice=button_text: self._set_choice(choice))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        # Zentriert das Fenster auf dem Bildschirm
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _set_choice(self, choice: str):
        """Setzt die Auswahl und schließt das Fenster."""
        self._choice = choice
        self.destroy()

    def get_choice(self) -> str:
        """Wartet, bis das Fenster geschlossen wird, und gibt die Auswahl zurück."""
        self.master.wait_window(self)
        return self._choice
