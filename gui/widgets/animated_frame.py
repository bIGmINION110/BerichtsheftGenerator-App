# gui/widgets/animated_frame.py
# -*- coding: utf-8 -*-
"""
Ein CTkFrame mit eingebauter Animationslogik.
"""
import customtkinter as ctk

class AnimatedFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def slide_in(self):
        """Animiert das Frame von rechts ins Bild."""
        self.place(relx=1.0, rely=0, relwidth=1, relheight=1)
        self._animate_slide(1.0)

    def _animate_slide(self, current_relx):
        """Die eigentliche Animationsschleife."""
        if current_relx > 0:
            current_relx -= 0.04  # Geschwindigkeit der Animation
            self.place(relx=max(current_relx, 0), rely=0, relwidth=1, relheight=1)
            self.after(10, lambda: self._animate_slide(current_relx))
        else:
            self.place(relx=0, rely=0, relwidth=1, relheight=1)