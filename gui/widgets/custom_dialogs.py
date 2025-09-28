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
        # NEU: Mindestgröße für den Frame festlegen, um das Fenster zu vergrößern
        main_frame.configure(width=500, height=250)
        
        # Schriftgröße und Zeilenumbruch für die Nachricht angepasst
        ctk.CTkLabel(main_frame, text=message, wraplength=450, justify="center", font=ctk.CTkFont(size=16)).pack(padx=20, pady=(20, 15), expand=True)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(padx=20, pady=(10, 20), fill="x", side="bottom")
        
        # Buttons zentrieren, wenn es weniger als 3 sind
        num_buttons = len(buttons)
        if num_buttons < 3:
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(num_buttons + 1, weight=1)

        for i, button_text in enumerate(buttons):
            # Buttons bekommen etwas mehr Platz und Höhe
            btn = ctk.CTkButton(button_frame, text=button_text, command=lambda choice=button_text: self._set_choice(choice), height=35)
            btn.grid(row=0, column=i + 1, padx=10, pady=5, sticky="ew")

        # Fenster zentrieren, nachdem die Mindestgröße wirksam wurde
        self.after(50, self._center_window)

    def _center_window(self):
        """Zentriert das Fenster auf dem Bildschirm."""
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