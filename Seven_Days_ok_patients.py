import customtkinter as ctk
import os
from PIL import Image
import sqlite3
from tkinter import ttk
from patient_indexes_view import PatientIndexes
from datetime import datetime

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
        headers = ["Patient ID", "Name", "Surname", "Days since last event", "Details"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                self.table_frame,
                text=header,    
                font=("Arial", 16, "bold"),
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
                FROM Seven_days_patients_ok o
                JOIN Patients p ON o.PatientID = p.PatientID
                WHERE p.DoctorID = ?
                ORDER BY o.Name, o.Surname
            """, (doctor_id,))
            
            patients = cursor.fetchall()
            
            if not patients:
                no_data_label = ctk.CTkLabel(
                    self.table_frame,
                    text="No seven days ok patients found",
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
                    font=("Arial", 14),
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
                    font=("Arial", 14),
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
                    font=("Arial", 14),
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
                    font=("Arial", 14),
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

    def show_patient_details(self, patient_id, name, surname):
        # Create a new window for patient options
        self.options_window = ctk.CTkToplevel()
        self.options_window.title(f"Patient Details - {name} {surname}")
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
        
        self.show_main_menu(patient_id, name, surname)

    def show_main_menu(self, patient_id, name, surname):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create main content frame
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left frame for buttons
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Title
        title = ctk.CTkLabel(
            left_frame,
            text=f"{name} {surname}",
            font=("Arial", 24, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=30)

        # Create a frame for buttons to center them
        button_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        # AHI button
        ahi_button = ctk.CTkButton(
            button_frame,
            text="AHI",
            width=200,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=lambda: self.open_ahi(patient_id, name, surname)
        )
        ahi_button.pack(pady=15)

        # ODI button
        odi_button = ctk.CTkButton(
            button_frame,
            text="ODI",
            width=200,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=lambda: self.open_odi(patient_id, name, surname)
        )
        odi_button.pack(pady=15)

        # SpO2 button
        spo2_button = ctk.CTkButton(
            button_frame,
            text="SpO₂",
            width=200,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=lambda: self.open_spo2(patient_id, name, surname)
        )
        spo2_button.pack(pady=15)

        # Actions frame
        actions_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        actions_frame.pack(pady=30)

        # Plan a Visit button
        self.visit_button = ctk.CTkButton(
            actions_frame,
            text="Plan a Visit",
            width=200,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=lambda pid=patient_id, n=name, s=surname: self.plan_visit(pid, n, s)
        )
        self.visit_button.pack(pady=15)

        # Check if button should be disabled
        self.check_visit_button_state(patient_id)

        # View/Modify Therapy button
        therapy_button = ctk.CTkButton(
            actions_frame,
            text="View/Modify Therapy",
            width=200,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=lambda: self.view_therapy(patient_id, name, surname)
        )
        therapy_button.pack(pady=15)

        # View Questionnaire button
        questionnaire_button = ctk.CTkButton(
            actions_frame,
            text="View Patient Questionnaire",
            width=200,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=lambda: self.view_questionnaire(patient_id, name, surname)
        )
        questionnaire_button.pack(pady=15)

        # Right frame for patient info
        right_frame = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=10, width=300)
        right_frame.pack(side="right", fill="y", expand=False, padx=(10, 0))
        right_frame.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents

        # Patient info header
        info_header = ctk.CTkFrame(right_frame, fg_color="#73C8AE", corner_radius=10)
        info_header.pack(fill="x", padx=10, pady=10)

        info_title = ctk.CTkLabel(
            info_header,
            text="Patient Information",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        info_title.pack(pady=10)

        # Get patient information from database
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT Name, Surname, dateOfBirth, height, weight, age, Gender, 
                       Nationality, ClinicalHistory, PhoneNumber
                FROM Patients
                WHERE PatientID = ?
            """, (patient_id,))
            
            patient_info = cursor.fetchone()
            
            if patient_info:
                # Create scrollable frame for patient info
                info_canvas = ctk.CTkCanvas(right_frame, bg="white", highlightthickness=0)
                info_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=info_canvas.yview)
                info_scrollable = ctk.CTkFrame(info_canvas, fg_color="white")
                
                info_scrollable.bind(
                    "<Configure>",
                    lambda e: info_canvas.configure(scrollregion=info_canvas.bbox("all"))
                )
                
                info_canvas.create_window((0, 0), window=info_scrollable, anchor="nw")
                info_canvas.configure(yscrollcommand=info_scrollbar.set)
                
                info_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                info_scrollbar.pack(side="right", fill="y", pady=10)
                
                # Display patient information
                fields = [
                    ("Name", patient_info[0]),
                    ("Surname", patient_info[1]),
                    ("Date of Birth", patient_info[2]),
                    ("Height", f"{float(patient_info[3]):.2f} m" if patient_info[3] else "N/A"),
                    ("Weight", f"{patient_info[4]} kg" if patient_info[4] else "N/A"),
                    ("Age", str(patient_info[5]) if patient_info[5] else "N/A"),
                    ("Gender", patient_info[6]),
                    ("Nationality", patient_info[7]),
                    ("Clinical History", patient_info[8] if patient_info[8] else "N/A"),
                    ("Phone Number", patient_info[9] if patient_info[9] else "N/A")
                ]
                
                for i, (field, value) in enumerate(fields):
                    field_frame = ctk.CTkFrame(info_scrollable, fg_color="white")
                    field_frame.pack(fill="x", padx=10, pady=5)
                    
                    field_label = ctk.CTkLabel(
                        field_frame,
                        text=f"{field}:",
                        font=("Arial", 14, "bold"),
                        text_color="#046A38",
                        anchor="w"
                    )
                    field_label.pack(side="left", padx=10)
                    
                    value_label = ctk.CTkLabel(
                        field_frame,
                        text=str(value),
                        font=("Arial", 14),
                        text_color="#046A38",
                        anchor="w"
                    )
                    value_label.pack(side="left", padx=10)
                
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                right_frame,
                text=f"Error loading patient information: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)
        finally:
            conn.close()

    def check_visit_button_state(self, patient_id):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM Notifications 
                WHERE PatientID = ? AND Type = 'visit' 
                AND datetime(CreationDate) > datetime('now', '-24 hours')
            """, (patient_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                self.visit_button.configure(
                    state="disabled",
                    fg_color="#CCCCCC",
                    hover_color="#CCCCCC"
                )
        except sqlite3.Error as e:
            print(f"Error checking notification state: {e}")
        finally:
            conn.close()

    def plan_visit(self, patient_id, name, surname):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        try:
            # Create notification for the visit request
            message = "The doctor requested a visit with you"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message, Timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, f"{name} {surname}", "VISIT_REQUEST", message, timestamp))
            
            # Update LastNotificationTime
            cursor.execute("""
                INSERT OR REPLACE INTO LastNotificationTime (PatientID, LastNotification)
                VALUES (?, ?)
            """, (patient_id, timestamp))
            
            conn.commit()
            
            # Disable the button
            self.visit_button.configure(
                state="disabled",
                fg_color="#CCCCCC",
                hover_color="#CCCCCC"
            )

            # Show success message
            success_label = ctk.CTkLabel(
                self.main_frame,
                text="Visit notification sent successfully!",
                font=("Arial", 16),
                text_color="#046A38"
            )
            success_label.pack(pady=20)

        except sqlite3.Error as e:
            print(f"Error sending notification: {e}")
        finally:
            conn.close()

    def open_ahi(self, patient_id, name, surname):
        from ahi_view_paziente import AHIViewPaziente
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        ahi_view = AHIViewPaziente(
            self.main_frame,
            patient_id=patient_id,
            patient_name=f"{name} {surname}",
            go_back_callback=lambda: self.show_main_menu(patient_id, name, surname),
            is_doctor=True
        )
        ahi_view.pack(fill="both", expand=True)

    def open_odi(self, patient_id, name, surname):
        from odi_view_paziente import ODIViewPaziente
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        odi_view = ODIViewPaziente(
            self.main_frame,
            patient_id=patient_id,
            patient_name=f"{name} {surname}",
            go_back_callback=lambda: self.show_main_menu(patient_id, name, surname)
        )
        odi_view.pack(fill="both", expand=True)

    def open_spo2(self, patient_id, name, surname):
        from spo2_view_paziente import SpO2ViewPaziente
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        spo2_view = SpO2ViewPaziente(
            self.main_frame,
            patient_id=patient_id,
            patient_name=f"{name} {surname}",
            go_back_callback=lambda: self.show_main_menu(patient_id, name, surname),
            is_doctor=True
        )
        spo2_view.pack(fill="both", expand=True)

    def view_therapy(self, patient_id, name, surname):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Add back button
        back_btn = ctk.CTkButton(
            self.main_frame,
            text="← Back",
            width=100,
            
            text_color="white",
            command=lambda: self.show_main_menu(patient_id, name, surname)
        )
        back_btn.pack(anchor="w", padx=20, pady=20)

        # Add title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Patient Therapy",
            font=("Arial", 24, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=20)

        # Create main content frame
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create table frame for drugs
        table_frame = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=10)
        table_frame.pack(fill="x", pady=(0, 20))

        # Table headers
        headers = ["Drug Information", "Start Date", "End Date"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                table_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="white",
                fg_color="#73C8AE",
                corner_radius=5,
                height=40,
                width=200,
                anchor="center"
            )
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

            if drugs:
                for i, (note, start_date, end_date) in enumerate(drugs, 1):
                    note_entry = ctk.CTkEntry(table_frame, width=300)
                    note_entry.insert(0, note)
                    note_entry.grid(row=i, column=0, padx=20, pady=5)

                    start_entry = ctk.CTkEntry(table_frame, width=150)
                    start_entry.insert(0, start_date)
                    start_entry.grid(row=i, column=1, padx=20, pady=5)

                    end_entry = ctk.CTkEntry(table_frame, width=150)
                    end_entry.insert(0, end_date)
                    end_entry.grid(row=i, column=2, padx=20, pady=5)

                    self.drug_entries.append((note_entry, start_entry, end_entry))

            # Add new drug button
            add_drug_btn = ctk.CTkButton(
                table_frame,
                text="+ Add New Drug",
                fg_color="#73C8AE",
                hover_color="#046A38",
                text_color="white",
                command=lambda: self.add_new_drug_row(table_frame)
            )
            add_drug_btn.grid(row=len(drugs) + 1, column=0, columnspan=3, pady=10, sticky="n")

        # Save button for drugs
            drug_save_btn = ctk.CTkButton(
                content_frame,
                text="Save Drugs",
                fg_color="#73C8AE",
                hover_color="#73C8AE",
                text_color="white",
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
            therapy_frame = ctk.CTkFrame(content_frame, fg_color="white", corner_radius=10)
            therapy_frame.pack(pady=20)

            therapy_label = ctk.CTkLabel(
                therapy_frame,
                text="Current Therapy:",
                font=("Arial", 14, "bold"),
                text_color="#046A38"
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
                text_color="white",
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

    def add_new_drug_row(self, table_frame):
        # Get the next row number
        next_row = len(self.drug_entries) + 1
        
        # Create new entries
        note_entry = ctk.CTkEntry(table_frame, width=300)
        note_entry.grid(row=next_row, column=0, padx=20, pady=5, sticky="w")
        
        start_entry = ctk.CTkEntry(table_frame, width=150)
        start_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        start_entry.grid(row=next_row, column=1, padx=20, pady=5, sticky="w")
        
        end_entry = ctk.CTkEntry(table_frame, width=150)
        end_entry.grid(row=next_row, column=2, padx=20, pady=5, sticky="w")
        
        # Add to entries list
        self.drug_entries.append((note_entry, start_entry, end_entry))
        
        # Move the "Add New Drug" button down
        for widget in table_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "+ Add New Drug":
                widget.grid(row=next_row + 1, column=0, columnspan=3, pady=10)

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
            success_label = ctk.CTkLabel(
                self.main_frame,
                text="Drugs saved successfully!",
                text_color="#046A38",
                font=("Arial", 14)
            )
            success_label.pack(pady=10)
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                self.main_frame,
                text=f"Error saving drugs: {e}",
                text_color="red"
            )
            error_label.pack(pady=10)
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
            success_label = ctk.CTkLabel(
                self.main_frame,
                text="Therapy saved successfully!",
                text_color="#046A38",
                font=("Arial", 14)
            )
            success_label.pack(pady=10)
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                self.main_frame,
                text=f"Error saving therapy: {e}",
                text_color="red"
            )
            error_label.pack(pady=10)
        finally:
            conn.close()

    def view_questionnaire(self, patient_id, name, surname):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Add back button
        back_btn = ctk.CTkButton(
            self.main_frame,
            text="← Back",
            width=100,
            text_color="white",
            command=lambda: self.show_main_menu(patient_id, name, surname)
        )
        back_btn.pack(anchor="w", padx=20, pady=20)

        # Add title
        title = ctk.CTkLabel(
            self.main_frame,
            text=f"Questionnaire - {name} {surname}",
            font=("Arial", 24, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=20)

        # Create main content frame
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create canvas and scrollbar
        canvas = ctk.CTkCanvas(content_frame, bg="#E8F5F2", highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
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

        # Question texts
        self.question_text_map = {
            "Q1": "How many times did you wake up during the night?",
            "Q2": "Did you sleep well?",
            "Nota2": "Please describe what was wrong:",
            "Q3": "Have you encountered any problems with night measurements?",
            "Q4": "What kind of problems did you have?",
            "Q5": "Do you want to receive a daily reminder?",
            "Q6": "Is technical support needed?",
            "Q7": "Did you have any sleep apneas and if so, how many?",
            "Q8": "Did you follow the therapy?",
            "Q9": "What went wrong?",
            "Q10": "Do you want to insert a note for the doctor?",
            "Q11": "Insert your note:",
            "Q12": "Did you weigh yourself today?",
            "Q13": "Insert your weight:"
        }

        self.answer_decoding_map = {
            "Q1": {
                0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5+"
            },
            "Q2": {
                0: "No",
                1: "Yes"
            },
            "Q3": {
                0: "No",
                1: "Yes"
            },
            "Q4": {
                0: "I forgot to turn on the device",
                1: "The device doesn't work",
                2: "I had problems with the application of the sensors"
            },
            "Q5": {
                0: "No",
                1: "Yes"
            },
            "Q6": {
                0: "No",
                1: "Yes"
            },
            "Q7": {
                0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5+"
            },
            "Q8": {
                0: "No",
                1: "Yes"
            },
            "Q10": {
                0: "No",
                1: "Yes"
            },
            "Q12": {
                0: "No change in weight",
                1: "I didn't get weighed today",
                2: "Yes, I want to insert my weight"
            }
        }
        
        # Load questionnaire responses
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT Date, Q1, Q2, Nota2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13
                FROM Questionnaire
                WHERE PatientID = ?
                ORDER BY Date DESC
            """, (patient_id,))
            
            responses = cursor.fetchall()
            
            if not responses:
                no_data_label = ctk.CTkLabel(
                    scrollable_frame,
                    text="No questionnaire responses found",
                    text_color="#046A38",
                    font=("Arial", 14)
                )
                no_data_label.pack(pady=20)
                return
            
            # Display responses
            for response in responses:
                date = response[0]
                
                # Create response frame
                response_frame = ctk.CTkFrame(scrollable_frame, fg_color="white", corner_radius=10)
                response_frame.pack(fill="x", padx=20, pady=10)
                
                # Date label
                date_label = ctk.CTkLabel(
                    response_frame,
                    text=f"Date: {date}",
                    font=("Arial", 16, "bold"),
                    text_color="#046A38"
                )
                date_label.pack(anchor="w", padx=20, pady=(20, 10))
                
                # Questions frame
                questions_frame = ctk.CTkFrame(response_frame, fg_color="transparent")
                questions_frame.pack(fill="x", padx=20, pady=10)
                
                # Display questions and answers
                for i, (key, value) in enumerate(zip(
                    ["Q1", "Q2", "Nota2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12", "Q13"],
                    response[1:]
                )):
                    if value is not None:
                        q_frame = ctk.CTkFrame(questions_frame, fg_color="#F2F2F2", corner_radius=5)
                        q_frame.pack(fill="x", pady=5)
                        
                        # Question text
                        q_label = ctk.CTkLabel(
                            q_frame,
                            text=self.question_text_map.get(key, key),
                            font=("Arial", 14, "bold"),
                            text_color="#046A38"
                        )
                        q_label.pack(anchor="w", padx=10, pady=5)
                        
                        # Decode and display answer
                        if key in self.answer_decoding_map:
                            decoded_answer = self.answer_decoding_map[key].get(value, value)
                        else:
                            decoded_answer = value
                            
                        answer_label = ctk.CTkLabel(
                            q_frame,
                            text=f"Answer: {decoded_answer}",
                            font=("Arial", 14),
                            text_color="#046A38"
                        )
                        answer_label.pack(anchor="w", padx=20, pady=(0, 5))
                
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                scrollable_frame,
                text=f"Error loading questionnaire responses: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)
        finally:
            conn.close()


if __name__ == "__main__":
    app = Seven_Days_Ok_PatientsView(user_id=1)  # oppure un altro id valido
    app.mainloop()

