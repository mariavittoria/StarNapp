import customtkinter as ctk
import os
from PIL import Image
import sqlite3
from tkinter import ttk
from patient_indexes_view import PatientIndexes

class Seven_Days_Ok_PatientsView(ctk.CTkFrame):
    def __init__(self, parent_frame, user_id):
        super().__init__(parent_frame)
        self.pack(fill="both", expand=True)
        
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
            background="#73C8AE",
            foreground="white",
            relief="flat"
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#73C8AE")]
        )

        # Get data from database
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Seven_Days_Ok_Patients")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()

        # Create Treeview
        self.tree = ttk.Treeview(
            table_frame,
            style="Custom.Treeview",
            columns=column_names,
            show="headings"
        )

        # Configure columns
        for col in column_names:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Insert data
        for row in rows:
            self.tree.insert("", "end", values=row)

        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_double_click)

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

