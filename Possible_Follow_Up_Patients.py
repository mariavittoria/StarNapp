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

        # Create canvas and scrollbar
        canvas = ctk.CTkCanvas(table_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        
        # Configure canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure canvas to expand with window
        def configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", configure_canvas)
        
        # Configure scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create table frame inside scrollable frame
        self.table_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True)
        
        # Configure grid
        for i in range(5):
            self.table_frame.grid_columnconfigure(i, weight=1)

        # Headers
        headers = ["Patient ID", "Name", "Surname", "Says since last episode", "Details"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                self.table_frame,
                text=header,    
                font=("Arial", 14, "bold"),
                text_color="white",
                fg_color="#73C8AE",
                corner_radius=5,
                height=40
            )
            header_label.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")

        # Load patients
        self.load_patients(doctor_id)

    def load_patients(self, doctor_id):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT o.PatientID, o.Name, o.Surname, o.Days_since_last_OSA
                FROM Possible_Follow_Up_Patients o
                JOIN Patients p ON o.PatientID = p.PatientID
                ORDER BY o.Name, o.Surname
            """, (doctor_id,))
            
            patients = cursor.fetchall()
            
            if not patients:
                no_data_label = ctk.CTkLabel(
                    self.table_frame,
                    text="No possible follow up patients found",
                    text_color="#046A38",
                    font=("Arial", 14)
                )
                no_data_label.grid(row=1, column=0, columnspan=5, pady=20)
                return
            
            # Display patients
            for i, (patient_id, name, surname, days) in enumerate(patients, start=1):
                # Alternate background color
                bg_color = "#F2F2F2" if i % 2 == 0 else "white"
                
                # Patient ID
                id_label = ctk.CTkLabel(
                    self.table_frame,
                    text=patient_id,
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                id_label.grid(row=i, column=0, padx=2, pady=2, sticky="nsew")
                
                # Name
                name_label = ctk.CTkLabel(
                    self.table_frame,
                    text=name,
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                name_label.grid(row=i, column=1, padx=2, pady=2, sticky="nsew")
                
                # Surname
                surname_label = ctk.CTkLabel(
                    self.table_frame,
                    text=surname,
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                surname_label.grid(row=i, column=2, padx=2, pady=2, sticky="nsew")
                
                # Days since last OSA
                days_label = ctk.CTkLabel(
                    self.table_frame,
                    text=str(days) if days is not None else "-",
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                days_label.grid(row=i, column=3, padx=2, pady=2, sticky="nsew")
                
                # Actions frame
                action_frame = ctk.CTkFrame(self.table_frame, fg_color=bg_color)
                action_frame.grid(row=i, column=4, padx=2, pady=2, sticky="nsew")
                
                # View Details button
                details_btn = ctk.CTkButton(
                    action_frame,
                    text="View Details",
                    width=100,
                    height=30,
                    fg_color="#73C8AE",
                    hover_color="#046A38",
                    text_color="white",
                    command=lambda pid=patient_id, n=name, s=surname: self.show_patient_details(pid, n, s)
                )
                details_btn.pack(padx=5, pady=5)
                
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                self.table_frame,
                text=f"Error loading patients: {str(e)}",
                text_color="red"
            )
            error_label.grid(row=1, column=0, columnspan=5, pady=20)
        finally:
            conn.close()

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

