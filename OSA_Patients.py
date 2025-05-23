import customtkinter as ctk
import os
from PIL import Image
import sqlite3
from tkinter import ttk
from patient_indexes_view import PatientIndexes
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from ahi_view_doctor import AHIViewDoctor

class OSAPatientsView(ctk.CTkFrame):
    def __init__(self, parent_frame, user_id):
        super().__init__(parent_frame)
        self.pack(fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="OSA Patients", 
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
            rowheight=50  # Increased row height to accommodate doctor name
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

        # Get data from database with doctor information
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.*, d.Name as DoctorName, d.Surname as DoctorSurname 
            FROM OSA_Patients o
            LEFT JOIN Patients p ON o.PatientID = p.PatientID
            LEFT JOIN Doctors d ON p.DoctorID = d.doctorID
        """)
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

        # Insert data with doctor information
        for row in rows:
            # Create a custom text that includes the doctor's name
            values = list(row)
            doctor_name = f"{values[-2]} {values[-1]}" if values[-2] and values[-1] else "No doctor assigned"
            values[2] = f"{values[2]}\nAssigned doctor: {doctor_name}"  # Add doctor name under patient name
            self.tree.insert("", "end", values=values[:-2])  # Exclude the doctor name columns

        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        # Get selected item
        item = self.tree.selection()[0]
        values = self.tree.item(item)['values']
        
        # Extract patient info
        self.patient_id = values[0]  # Assuming PatientID is the second column
        self.patient_name = f"{values[1]} {values[2]}"  # Assuming Name and Surname are the third and fourth columns
        
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

    def show_main_menu(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text=f"Patient: {self.patient_name}",
            font=("Arial", 24, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=30)

        # Create a frame for buttons to center them
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        # AHI button
        ahi_button = ctk.CTkButton(
            button_frame,
            text="AHI",
            width=200,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            command=self.open_ahi
        )
        ahi_button.pack(pady=15)

        # ODI button
        odi_button = ctk.CTkButton(
            button_frame,
            text="ODI",
            width=200,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            command=self.open_odi
        )
        odi_button.pack(pady=15)

        # SpO2 button
        spo2_button = ctk.CTkButton(
            button_frame,
            text="SpO₂",
            width=200,
            fg_color="#73C8AE",  # Light green
            hover_color="#046A38",  # Dark green
            text_color="white",
            command=self.open_spo2
        )
        spo2_button.pack(pady=15)

        # Actions frame
        actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        actions_frame.pack(pady=30)

        # Plan a Visit button
        visit_button = ctk.CTkButton(
            actions_frame,
            text="Plan a Visit",
            width=200,
            fg_color="#4A90E2",  # Light blue
            hover_color="#2C5282",  # Darker blue
            text_color="white",
            command=self.plan_visit
        )
        visit_button.pack(pady=15)

        # View/Modify Therapy button
        therapy_button = ctk.CTkButton(
            actions_frame,
            text="View/Modify Therapy",
            width=200,
            fg_color="#4A90E2",  # Light blue
            hover_color="#2C5282",  # Darker blue
            text_color="white",
            command=self.view_therapy
        )
        therapy_button.pack(pady=15)

    def open_ahi(self):
        from ahi_view_doctor import AHIViewDoctor
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        ahi_view = AHIViewDoctor(
            self.main_frame,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_main_menu
        )
        ahi_view.pack(fill="both", expand=True)

    def open_odi(self):
        from odi_view_doctor import ODIViewDoctor
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        odi_view = ODIViewDoctor(
            self.main_frame,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_main_menu
        )
        odi_view.pack(fill="both", expand=True)

    def open_spo2(self):
        from spo2_view_doctor import SpO2ViewDoctor
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        spo2_view = SpO2ViewDoctor(
            self.main_frame,
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            go_back_callback=self.show_main_menu
        )
        spo2_view.pack(fill="both", expand=True)

    def plan_visit(self, patient_id, patient_name):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Add back button
        back_btn = ctk.CTkButton(
            self.main_frame,
            text="← Back",
            width=100,
            fg_color="#204080",
            command=self.show_main_menu
        )
        back_btn.pack(anchor="w", padx=20, pady=20)

        # Add title
        title = ctk.CTkLabel(self.main_frame, text="Plan Visit", font=("Arial", 24, "bold"), text_color="#204080")
        title.pack(pady=20)

        # Create form frame
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(pady=20)

        # Date selection
        date_label = ctk.CTkLabel(form_frame, text="Select Date:", font=("Arial", 14))
        date_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        date_entry = ctk.CTkEntry(form_frame, width=200)
        date_entry.grid(row=0, column=1, padx=20, pady=10)
        date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        # Time selection
        time_label = ctk.CTkLabel(form_frame, text="Select Time:", font=("Arial", 14))
        time_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        time_entry = ctk.CTkEntry(form_frame, width=200)
        time_entry.grid(row=1, column=1, padx=20, pady=10)
        time_entry.insert(0, "09:00")

        # Doctor selection
        doctor_label = ctk.CTkLabel(form_frame, text="Select Doctor:", font=("Arial", 14))
        doctor_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        doctor_entry = ctk.CTkEntry(form_frame, width=200)
        doctor_entry.grid(row=2, column=1, padx=20, pady=10)
        doctor_entry.insert(0, "Dr. Smith")

        # Submit button
        submit_btn = ctk.CTkButton(
            form_frame,
            text="Schedule Visit",
            width=200,
            fg_color="#9b59b6",
            command=lambda: self.schedule_visit(
                patient_id,
                patient_name,
                date_entry.get(),
                time_entry.get(),
                doctor_entry.get()
            )
        )
        submit_btn.grid(row=3, column=0, columnspan=2, pady=20)

    def schedule_visit(self, patient_id, patient_name, date, time, doctor):
        # Add to appointments table
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Appointments (date, time, doctor_name, status, patient_id, patient_name)
                VALUES (?, ?, ?, 'booked', ?, ?)
            """, (date, time, doctor, patient_id, patient_name))
            
            # Create notification for patient
            message = f"New appointment scheduled with {doctor} on {date} at {time}"
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message)
                VALUES (?, ?, 'APPOINTMENT', ?)
            """, (patient_id, patient_name, message))
            
            conn.commit()
            
            # Show success message
            success_label = ctk.CTkLabel(
                self.main_frame,
                text="Visit scheduled successfully!",
                font=("Arial", 16),
                text_color="green"
            )
            success_label.pack(pady=20)
            
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                self.main_frame,
                text=f"Error scheduling visit: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)
        finally:
            conn.close()

    def view_therapy(self, patient_id):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Add back button
        back_btn = ctk.CTkButton(
            self.main_frame,
            text="← Back",
            width=100,
            fg_color="#204080",
            command=self.show_main_menu
        )
        back_btn.pack(anchor="w", padx=20, pady=20)

        # Add title
        title = ctk.CTkLabel(self.main_frame, text="Patient Therapy", font=("Arial", 24, "bold"), text_color="#204080")
        title.pack(pady=20)

        # Create main content frame
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create table frame for drugs
        table_frame = ctk.CTkFrame(content_frame)
        table_frame.pack(fill="x", pady=(0, 20))

        # Table headers
        headers = ["Drug Information", "Start Date", "End Date"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(table_frame, text=header, font=("Arial", 14, "bold"))
            label.grid(row=0, column=i, padx=20, pady=10, sticky="w")

        # Get drugs from database
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()

        self.drug_entries = []

        try:
            cursor.execute("""
                SELECT Note, StartDate, EndDate
                FROM Drugs
                WHERE PatientID = ?
                ORDER BY StartDate DESC
            """, (patient_id,))
        
            drugs = cursor.fetchall()

            if not drugs:
                no_drugs_label = ctk.CTkLabel(table_frame, text="No medications found", font=("Arial", 14))
                no_drugs_label.grid(row=1, column=0, columnspan=3, pady=20)
            else:
                for i, (note, start_date, end_date) in enumerate(drugs, 1):
                    note_entry = ctk.CTkEntry(table_frame, width=300)
                    note_entry.insert(0, note)
                    note_entry.grid(row=i, column=0, padx=20, pady=5, sticky="w")

                    start_entry = ctk.CTkEntry(table_frame, width=150)
                    start_entry.insert(0, start_date)
                    start_entry.grid(row=i, column=1, padx=20, pady=5, sticky="w")

                    end_entry = ctk.CTkEntry(table_frame, width=150)
                    end_entry.insert(0, end_date)
                    end_entry.grid(row=i, column=2, padx=20, pady=5, sticky="w")

                    self.drug_entries.append((note_entry, start_entry, end_entry))

        # Save button for drugs
            drug_save_btn = ctk.CTkButton(
                content_frame,
                text="Save Drugs",
                fg_color="#6ba37f",
                width=200,
                command=lambda: self.save_drugs(patient_id)
            )
            drug_save_btn.pack(pady=10)

        # Get current therapy
            cursor.execute("""
                SELECT ID, Note
                FROM Therapy
                WHERE PatientID = ?
            """, (patient_id,))
            
            current_therapy = cursor.fetchone()
            self.current_therapy_id = current_therapy[0] if current_therapy else None

        # Create therapy input frame
            therapy_frame = ctk.CTkFrame(content_frame)
            therapy_frame.pack(fill="x", pady=20)

            therapy_label = ctk.CTkLabel(
                therapy_frame,
                text="Current Therapy:",
                font=("Arial", 14, "bold")
            )
            therapy_label.pack(anchor="w", padx=20, pady=(20, 10))

            # Therapy text input
            self.therapy_text = ctk.CTkTextbox(
                therapy_frame,
                height=100,
                width=600,
                font=("Arial", 12)
            )
            self.therapy_text.pack(padx=20, pady=10)

            if current_therapy:
                self.therapy_text.insert("1.0", current_therapy[1])

            # Save button for therapy
            save_btn = ctk.CTkButton(
                therapy_frame,
                text="Save Therapy",
                width=200,
                fg_color="#b76ba3",
                command=lambda: self.save_therapy(patient_id)
            )
            save_btn.pack(pady=20)

        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                content_frame,
                text=f"Error loading data: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)
        finally:
            conn.close()

    def save_therapy(self, patient_id):
        new_note = self.therapy_text.get("1.0", "end-1c")
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        try:
            if self.current_therapy_id:
                cursor.execute("""
                    UPDATE Therapy SET Note = ? WHERE ID = ?
                """, (new_note, self.current_therapy_id))
            else:
                cursor.execute("""
                    INSERT INTO Therapy (PatientID, Note) VALUES (?, ?)
                """, (patient_id, new_note))
            
            conn.commit()
            ctk.CTkLabel(self.main_frame, text="Therapy saved!", text_color="green").pack()
        except sqlite3.Error as e:
            ctk.CTkLabel(self.main_frame, text=f"Error saving therapy: {e}", text_color="red").pack()
        finally:
            conn.close()

    def get_osa_patients(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM OSA_Patients")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return column_names, rows
    
    def save_drugs(self, patient_id):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Drugs WHERE PatientID = ?", (patient_id,))
            
            for note_entry, start_entry, end_entry in self.drug_entries:
                note = note_entry.get()
                start = start_entry.get()
                end = end_entry.get()
                cursor.execute("""
                    INSERT INTO Drugs (PatientID, Note, StartDate, EndDate)
                    VALUES (?, ?, ?, ?)
                """, (patient_id, note, start, end))

            conn.commit()
            ctk.CTkLabel(self.main_frame, text="Drugs saved!", text_color="green").pack()
        except sqlite3.Error as e:
            ctk.CTkLabel(self.main_frame, text=f"Error saving drugs: {e}", text_color="red").pack()
        finally:
            conn.close()


if __name__ == "__main__":
    app = OSAPatientsView(container=None, doctor_id=1)  # oppure un altro id valido
    app.mainloop()

