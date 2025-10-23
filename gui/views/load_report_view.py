# gui/views/load_report_view.py
# -*- coding: utf-8 -*-
"""
Defines the view for loading an existing report.
"""
import customtkinter as ctk
import logging
from tkinter import Menu
from typing import Dict, Any, List
from ..widgets.accessible_widgets import AccessibleCTkButton
from core import config
from tkinter import messagebox

logger = logging.getLogger(__name__)

class LoadReportView(ctk.CTkFrame):
    """View for selecting and loading a saved report."""

    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.data_manager = app_logic.data_manager

        self.reports: Dict[str, Any] = {}
        self.report_frames: List[ctk.CTkFrame] = []
        self.current_focus_index = 0

        self._create_widgets()

    def on_show(self):
        """Called when the view becomes visible. Reloads the report list."""
        self.reports = self.data_manager.lade_berichte()
        self._populate_report_list()
        if self.report_frames:
            self.after(100, lambda: self.report_frames[0].focus_set())

    def _create_widgets(self):
        """Creates the UI elements of the view."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)

        AccessibleCTkButton(
            action_frame,
            text="Delete All Reports",
            fg_color=config.ERROR_COLOR,
            hover_color=config.ERROR_HOVER_COLOR,
            command=self._delete_all_reports,
            accessible_text="Deletes all saved reports after confirmation.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        ).pack(side="right", padx=10, pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Saved Reports")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _populate_report_list(self):
        """Fills the list with available reports."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.report_frames = []

        if not self.reports:
            ctk.CTkLabel(self.scroll_frame, text="No reports found to load.").pack(pady=10)
            return

        sorted_reports = sorted(self.reports.items(), key=lambda item: item[0], reverse=True)

        for key, report_data in sorted_reports:
            frame = ctk.CTkFrame(self.scroll_frame)
            frame.pack(fill="x", padx=5, pady=5)
            frame.grid_columnconfigure(0, weight=1)

            frame.report_id = key
            frame.report_data = report_data

            self.report_frames.append(frame)

            try:
                nr = report_data.get("fortlaufende_nr", "?")
                kw = report_data.get("kalenderwoche", "?")
                jahr = report_data.get("jahr", "?")
                name = report_data.get("name_azubi", "Unknown")

                label_text = f"No. {nr} - CW {kw}/{jahr} ({name})"
                label = ctk.CTkLabel(frame, text=label_text, justify="left", font=ctk.CTkFont(size=14))
                label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

                # Bind events to the entire frame and the label
                for widget in (frame, label):
                    widget.bind("<Button-1>", lambda event, data=report_data: self._load_report(data))
                    widget.bind("<Button-3>", lambda event, report_id=key: self._show_context_menu(event, report_id))
                    widget.bind("<Return>", lambda event, data=report_data: self._load_report(data))
                    widget.bind("<Delete>", lambda event, report_id=key: self._delete_report(report_id))
                    widget.bind("<FocusIn>", lambda event, f=frame: self._on_focus_in(f))
                    widget.bind("<FocusOut>", lambda event, f=frame: self._on_focus_out(f))

            except Exception as e:
                logger.warning(f"Error displaying report '{key}': {e}")
                ctk.CTkLabel(frame, text=f"Corrupt entry: {key}", text_color="orange").grid(row=0, column=0, padx=10, pady=5, sticky="w")

    def _show_context_menu(self, event, report_id):
        """Shows a context menu for loading or deleting a report."""
        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label="Load", command=lambda: self._load_report(self.reports[report_id]))
        context_menu.add_command(label="Delete", command=lambda: self._delete_report(report_id))
        context_menu.tk_popup(event.x_root, event.y_root)

    def _on_focus_in(self, widget: ctk.CTkFrame):
        """Highlights the frame when it receives focus."""
        widget.configure(fg_color=config.HOVER_COLOR)
        self.scroll_frame._parent_canvas.yview_moveto(widget.winfo_y() / self.scroll_frame._parent_canvas.winfo_height())

    def _on_focus_out(self, widget: ctk.CTkFrame):
        """Resets the frame color when it loses focus."""
        widget.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

    def _navigate_reports(self, event):
        """Enables navigation with arrow keys."""
        if not self.winfo_viewable() or not self.report_frames:
            return

        if event.keysym == "Down":
            self.current_focus_index = (self.current_focus_index + 1) % len(self.report_frames)
        elif event.keysym == "Up":
            self.current_focus_index = (self.current_focus_index - 1 + len(self.report_frames)) % len(self.report_frames)
        else:
            return

        self.report_frames[self.current_focus_index].focus_set()

    def _load_report(self, report_data: Dict[str, Any]):
        """Calls the method in the main app to load the data into the GUI."""
        logger.info(f"Loading report No. {report_data.get('fortlaufende_nr', '?')} into GUI.")
        self.app.get_berichtsheft_view_reference().load_report_data_into_ui(report_data)
        self.app.show_view("berichtsheft", run_on_show=False)

    def _delete_report(self, report_id: str):
        """Deletes a report from the database with an animation."""
        if messagebox.askyesno("Confirm Deletion", f"Do you really want to delete the report with ID '{report_id}'?"):
            frame_to_delete = next((f for f in self.report_frames if hasattr(f, 'report_id') and f.report_id == report_id), None)

            def perform_delete():
                if self.app.controller.delete_bericht(report_id):
                    self.on_show()  # Reloads the list
                else:
                    messagebox.showerror("Error", "Could not delete the report.")

            if frame_to_delete:
                self.app.animation_manager.delete_animation(frame_to_delete, remove_callback=perform_delete)
            else:
                perform_delete()

    def _delete_all_reports(self):
        """Deletes all reports after confirmation."""
        if messagebox.askyesno("Delete All Reports", "Are you sure you want to permanently delete ALL saved reports?"):
            if self.app.controller.loesche_alle_berichte():
                messagebox.showinfo("Success", "All reports have been deleted.")
                self.on_show()
            else:
                messagebox.showerror("Error", "An error occurred while deleting the reports.")