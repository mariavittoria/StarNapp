# patient_indexes_view.py
import customtkinter as ctk
import sqlite3
import datetime

class PatientIndexes(ctk.CTkFrame):
    def __init__(self, parent, patient_id, patient_name="Unknown Patient"):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        self.patient_id = patient_id
        self.patient_name = patient_name

        # Configure the frame with light blue-green background
        self.configure(fg_color="#E8F5F2")
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_indexes()

    def show_indexes(self):
        for widget in self.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self, text="Select an Index", font=("Arial", 28, "bold"), text_color="#046A38")
        title.pack(pady=30)

        # Create a frame for buttons to center them
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)

        # AHI button
        ahi_button = ctk.CTkButton(
            button_frame,
            text="AHI - Apnea Hypoapnea Index",
            width=330,
            height=50,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            font=("Arial", 16),
            command=self.open_ahi
        )
        ahi_button.pack(pady=15)

        # ODI button
        odi_button = ctk.CTkButton(
            button_frame,
            text="ODI - Oxygen Desaturation Index",
            width=330,
            height=50,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            font=("Arial", 16),
            command=self.open_odi
        )
        odi_button.pack(pady=15)

        # SpO2 button
        spo2_button = ctk.CTkButton(
            button_frame,
            text="SpO₂ - Oxygen Saturation",
            width=330,
            height=50,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            font=("Arial", 16),
            command=self.open_spo2
        )
        spo2_button.pack(pady=15)

    def go_back(self):
        from patient_main_view import PatientMainView
        self.master.destroy()
        PatientMainView(patient_id=self.patient_id)

    def open_ahi(self):
        from ahi_view_paziente import AHIViewPaziente
        for widget in self.winfo_children():
            widget.destroy()
        ahi_view = AHIViewPaziente(
            self,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_indexes
        )
        ahi_view.pack(fill="both", expand=True)

    def open_odi(self):
        from odi_view_paziente import ODIViewPaziente
        for widget in self.winfo_children():
            widget.destroy()
        odi_view = ODIViewPaziente(
            self,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_indexes
        )
        odi_view.pack(fill="both", expand=True)

    def open_spo2(self):
        from spo2_view_paziente import SpO2ViewPaziente
        for widget in self.winfo_children():
            widget.destroy()
        spo2_view = SpO2ViewPaziente(
            self,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_indexes
        )
        spo2_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    PatientIndexes(parent=None)
