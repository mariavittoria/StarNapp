import customtkinter
import os
from PIL import Image
import sqlite3
import tkinter.ttk as ttk
import datetime

class VisitDoctorView(customtkinter.CTk):
    def __init__(self, parent_frame, user_id):
        # Titolo
        title = customtkinter.CTkLabel(parent_frame, text="Visits Management", font=("Arial", 20, "bold"), text_color="black")
        title.grid(row=0, column=0, columnspan=2, pady=20)

        # Frame per i bottoni
        button_frame = customtkinter.CTkFrame(parent_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)

        # Bottoni
        fix_visit_btn = customtkinter.CTkButton(
            button_frame,
            text="Fix Visit",
            width=200,
            height=40,
            
        )
        fix_visit_btn.grid(row=0, column=0, padx=20, pady=10)

        view_appointment_btn = customtkinter.CTkButton(
            button_frame,
            text="View Appointment",
            width=200,
            height=40,
            command=self.view_appointment
        )
        view_appointment_btn.grid(row=1, column=0, padx=20, pady=10)

   