import customtkinter as ctk
import os
from PIL import Image
import sqlite3
from tkinter import ttk
from patient_indexes_view import PatientIndexes

class Seven_Days_Ok_PatientsView(ctk.CTkFrame):
    def __init__(self, parent_frame, doctor_id):
        super().__init__(parent_frame)
        self.pack(fill="both", expand=True)
        
        # Configure the frame with light blue-green background
        self.configure(fg_color="#E8F5F2")
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="7 Days OK Patients", 
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
                FROM Seven_Days_Patients_ok
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

    def get_7_days_ok_patients(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Seven_days_patients_ok")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return column_names, rows


if __name__ == "__main__":
    app = Seven_Days_Ok_PatientsView(user_id=1)  # oppure un altro id valido
    app.mainloop()

