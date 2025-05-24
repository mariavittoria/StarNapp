import customtkinter as ctk
import os
from PIL import Image
import sqlite3
from tkinter import ttk
from patient_indexes_view import PatientIndexes

class PossibleFollowUpPatientsView(ctk.CTkFrame):
    def __init__(self, parent_frame, doctor_id):
        super().__init__(parent_frame)
        self.pack(fill="both", expand=True)
        
        # Configure the frame with light blue-green background
        self.configure(fg_color="#E8F5F2")
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="Possible Follow Up Patients", 
            font=("Arial", 24, "bold"), 
            text_color="#046A38"
        )
        title.pack(pady=20)
        
        # Create table frame with white background and rounded corners
        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Create Treeview with custom style
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="white",
            foreground="#046A38",
            fieldbackground="white",
            rowheight=30
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#A8DAB5",  # Light green background for headers
            foreground="#046A38",  # Dark green text
            relief="flat",
            font=("Arial", 10, "bold")
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#A8DAB5")]  # Keep the same color when hovering
        )

        # Create Treeview
        self.tree = ttk.Treeview(
            table_frame,
            style="Custom.Treeview",
            columns=("Patient ID", "Name", "Surname"),
            show="headings"
        )

        # Configure columns
        self.tree.heading("Patient ID", text="Patient ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Surname", text="Surname")

        # Set column widths and center text
        self.tree.column("Patient ID", width=100, anchor="center")
        self.tree.column("Name", width=150, anchor="center")
        self.tree.column("Surname", width=150, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load data
        self.load_patients(doctor_id)

    def load_patients(self, doctor_id):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT PatientID, Name, Surname
                FROM Possible_Follow_Up_Patients
                ORDER BY Date DESC
            """)
            
            patients = cursor.fetchall()
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Insert patients
            for patient in patients:
                self.tree.insert("", "end", values=patient)
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def on_double_click(self, event):
        # Get selected item
        item = self.tree.selection()[0]
        values = self.tree.item(item)['values']
        
        # Extract patient info
        self.patient_id = values[0]  # Assuming PatientID is the first column
        self.patient_name = f"{values[1]} {values[2]}"  # Assuming Name and Surname are the second and third columns
        
        # Create a new window for patient options
        self.options_window = ctk.CTkToplevel()
        self.options_window.title(f"Patient Options - {self.patient_name}")
        self.options_window.geometry("800x500")
        
        # Center the window
        w = 800
        h = 500
        x = (self.options_window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.options_window.winfo_screenheight() // 2) - (h // 2)
        self.options_window.geometry(f"{w}x{h}+{x}+{y}")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.options_window, corner_radius=10, fg_color="#E8F5F2")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.show_main_menu()

    def get_possible_follow_up_patients(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Possible_Follow_Up_Patients")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return column_names, rows

    def show_main_menu(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # PATIENT TRENDS
        title = ctk.CTkLabel(self.main_frame, text="Patient Trends", font=("Arial", 24, "bold"), text_color="#046A38")
        title.pack(pady=(40, 20))
        
        # Add trend buttons frame
        trends_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        trends_frame.pack(pady=20)
        
        # Trend buttons - Green theme
        # AHI button
        ahi_button = ctk.CTkButton(
            trends_frame,
            text="AHI trend",
            width=200,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            command=self.open_ahi
        )
        ahi_button.pack(pady=15)

        # ODI button
        odi_button = ctk.CTkButton(
            trends_frame,
            text="ODI trend",
            width=200,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            command=self.open_odi
        )
        odi_button.pack(pady=15)

        # SpO2 button
        spo2_button = ctk.CTkButton(
            trends_frame,
            text="SpO₂ trend",
            width=200,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            command=self.open_spo2
        )
        spo2_button.pack(pady=15)
        
        # Add action buttons frame
        actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        actions_frame.pack(pady=(40, 20))
        
        # Action buttons - Light blue theme
        visit_btn = ctk.CTkButton(
            actions_frame,
            text="Plan a Visit with the Patient",
            width=250,
            fg_color="#4A90E2",  # Light blue
            hover_color="#2C5282",  # Darker blue
            text_color="white",
            command=lambda: self.plan_visit(self.patient_id, self.patient_name)
        )
        visit_btn.pack(pady=15)
        
        therapy_btn = ctk.CTkButton(
            actions_frame,
            text="View/Modify Therapy",
            width=250,
            fg_color="#4A90E2",  # Light blue
            hover_color="#2C5282",  # Darker blue
            text_color="white",
            command=lambda: self.view_therapy(self.patient_id)
        )
        therapy_btn.pack(pady=15)

    def open_ahi(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create AHI view
        from ahi_view_doctor import AHIViewDoctor
        ahi_view = AHIViewDoctor(
            self.main_frame,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_main_menu
        )
        ahi_view.pack(fill="both", expand=True)

    def open_odi(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create ODI view
        from odi_view_doctor import ODIViewDoctor
        odi_view = ODIViewDoctor(
            self.main_frame,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_main_menu
        )
        odi_view.pack(fill="both", expand=True)

    def open_spo2(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create SpO2 view
        from spo2_view_doctor import SpO2ViewDoctor
        spo2_view = SpO2ViewDoctor(
            self.main_frame,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_main_menu
        )
        spo2_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = PossibleFollowUpPatientsView(user_id=1)  # oppure un altro id valido
    app.mainloop()

