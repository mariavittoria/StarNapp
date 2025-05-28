import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
import calendar
from tkcalendar import Calendar

class VisitDoctorView(ctk.CTkFrame):
    def __init__(self, parent_frame, doctor_id):
        super().__init__(parent_frame)
        self.pack(fill="both", expand=True)
        self.doctor_id = doctor_id
        
        # Initialize current date to next available weekday
        self.current_date = datetime.now()
        while self.current_date.weekday() >= 5:  # Skip weekends
            self.current_date += timedelta(days=1)
        
        # Configure the frame with light blue-green background
        self.configure(fg_color="#E8F5F2")
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="Visits Management", 
            font=("Arial", 24, "bold"), 
            text_color="#046A38"
        )
        title.pack(pady=20)
        
        # Create buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        # View Calendar button
        calendar_btn = ctk.CTkButton(
            buttons_frame,
            text="View Calendar",
            width=250,
            height=50,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            font=("Arial", 16),
            command=self.show_calendar
        )
        calendar_btn.pack(pady=15)
        
        # Fix a Visit button
        fix_visit_btn = ctk.CTkButton(
            buttons_frame,
            text="Fix an appointment",
            width=250,
            height=50,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            font=("Arial", 16),
            command=self.show_patient_list
        )
        fix_visit_btn.pack(pady=15)

    def show_calendar(self):
        # Create a new window for the calendar
        self.calendar_window = ctk.CTkToplevel(self)
        self.calendar_window.title("Visit Calendar")
        self.calendar_window.geometry("1200x800")
        
        # Create main frame
        main_frame = ctk.CTkFrame(self.calendar_window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create navigation frame
        nav_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        # Previous day button
        prev_btn = ctk.CTkButton(
            nav_frame,
            text="←",
            width=150,
            height=30,
            fg_color="#046A38",
            hover_color="#1f6aa5",
            text_color="white",
            command=lambda: self.navigate_days(-1)
        )
        prev_btn.pack(side="left", padx=10)
        
        # Next day button
        next_btn = ctk.CTkButton(
            nav_frame,
            text="→",
            width=150,
            height=30,
            fg_color="#046A38",
            hover_color="#1f6aa5",
            text_color="white",
            command=lambda: self.navigate_days(1)
        )
        next_btn.pack(side="right", padx=10)
        
        # Create days frame
        self.days_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.days_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure grid weights for centering
        self.days_frame.grid_columnconfigure(0, weight=1)
        self.days_frame.grid_columnconfigure(1, weight=1)
        self.days_frame.grid_columnconfigure(2, weight=1)
        self.days_frame.grid_columnconfigure(3, weight=1)
        self.days_frame.grid_columnconfigure(4, weight=1)
        
        # Show initial 5 days
        self.show_five_days()

    def show_five_days(self):
        # Clear existing days
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        
        # Create grid for 5 days
        current_day = self.current_date
        days_shown = 0
        col = 0
        
        while days_shown < 5:
            # Skip weekends
            if current_day.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                current_day += timedelta(days=1)
                continue
            
            day_frame = ctk.CTkFrame(self.days_frame, fg_color="white", corner_radius=10)
            day_frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
            
            # Day header
            day_label = ctk.CTkLabel(
                day_frame,
                text=current_day.strftime("%A\n%d %B"),
                font=("Arial", 16, "bold"),
                text_color="#046A38"
            )
            day_label.pack(pady=10)
            
            # Create time slots
            time_slots = [
                "08:30", "09:30", "10:30", "11:30", "12:30",
                "13:30", "14:30", "15:30", "16:30"
            ]
            
            for time in time_slots:
                # Check if slot is booked and get patient info
                is_booked, patient_name, patient_surname = self.get_slot_info(current_day.strftime("%Y-%m-%d"), time)
                
                # Create slot button
                slot_btn = ctk.CTkButton(
                    day_frame,
                    text=time,
                    width=100,
                    height=50,
                    font=("Arial", 16),
                    fg_color="#73C8AE" if not is_booked else "#CCCCCC",
                    hover_color="#046A38" if not is_booked else "#999999",
                    text_color="white",
                    command=lambda d=current_day.strftime("%Y-%m-%d"), t=time, n=patient_name, s=patient_surname, b=is_booked: 
                        self.show_appointment_details(d, t, n, s) if b else None
                )
                slot_btn.pack(pady=5)
            
            current_day += timedelta(days=1)
            days_shown += 1
            col += 1

    def navigate_days(self, days):
        # Move to next/previous day
        self.current_date += timedelta(days=days)
        
        # If we land on a weekend, keep moving until we find a weekday
        while self.current_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
            self.current_date += timedelta(days=1 if days > 0 else -1)
        
        self.show_five_days()

    def check_if_slot_booked(self, date, time):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT a.status, p.Name, p.Surname
                FROM Appointments a
                JOIN Patients p ON a.patient_id = p.PatientID
                WHERE a.doctor_id = ? AND a.date = ? AND a.time = ?
            """, (self.doctor_id, date, time))
            
            result = cursor.fetchone()
            return result and result[0] == "booked"
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()

    def get_slot_info(self, date, time):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT a.status, p.Name, p.Surname
                FROM Appointments a
                JOIN Patients p ON a.patient_id = p.PatientID
                WHERE a.doctor_id = ? AND a.date = ? AND a.time = ?
            """, (self.doctor_id, date, time))
            
            result = cursor.fetchone()
            if result and result[0] == "booked":
                return True, result[1], result[2]
            return False, None, None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False, None, None
        finally:
            conn.close()

    def show_appointment_details(self, date, time, name, surname):
        # Create details frame in the calendar window
        details_frame = ctk.CTkFrame(self.calendar_window, fg_color="white", corner_radius=10)
        details_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Add close button in top right corner
        close_btn = ctk.CTkButton(
            details_frame,
            text="✕",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#FF9999",
            text_color="#046A38",
            command=details_frame.destroy
        )
        close_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)
        
        # Patient info
        info_label = ctk.CTkLabel(
            details_frame,
            text=f"Patient: {name} {surname}\nDate: {date}\nTime: {time}",
            font=("Arial", 14),
            text_color="black"
        )
        info_label.pack(pady=20)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            details_frame,
            text="Delete Appointment",
            width=200,
            height=40,
            fg_color="#FF9999",
            hover_color="#FF6666",
            text_color="white",
            command=lambda: self.delete_appointment(date, time, details_frame)
        )
        delete_btn.pack(pady=20)

    def delete_appointment(self, date, time, frame):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM Appointments
                WHERE doctor_id = ? AND date = ? AND time = ?
            """, (self.doctor_id, date, time))
            
            conn.commit()
            
            # Remove details frame
            frame.destroy()
            
            # Refresh calendar
            self.show_five_days()
            
            # Show success message
            success_label = ctk.CTkLabel(
                self.calendar_window,
                text="Appointment deleted successfully!",
                font=("Arial", 14),
                text_color="#046A38"
            )
            success_label.place(relx=0.5, rely=0.1, anchor="center")
            
            # Remove success message after 2 seconds
            self.calendar_window.after(2000, success_label.destroy)
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def send_notification_to_patient(self, patient_id, name, surname):
        # Check if 24 hours have passed since last notification
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            # Get last notification time
            cursor.execute("""
                SELECT LastNotification 
                FROM LastNotificationTime 
                WHERE PatientID = ?
            """, (patient_id,))
            
            result = cursor.fetchone()
            current_time = datetime.now()
            
            if result:
                last_notification = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
                time_diff = current_time - last_notification
                
                # If less than 24 hours have passed, show error and return
                if time_diff.total_seconds() < 24 * 3600:
                    error_window = ctk.CTkToplevel(self)
                    error_window.title("Error")
                    error_window.geometry("300x150")
                    
                    remaining_hours = int((24 * 3600 - time_diff.total_seconds()) / 3600)
                    error_label = ctk.CTkLabel(
                        error_window,
                        text=f"Please wait {remaining_hours} hours before sending another notification.",
                        font=("Arial", 14),
                        text_color="red"
                    )
                    error_label.pack(pady=20)
                    
                    # Close error window after 2 seconds
                    error_window.after(2000, error_window.destroy)
                    return
            
            # Create notification for the patient
            message = "The doctor requested a visit with you"
            timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message, Timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, f"{name} {surname}", "visit_request", message, timestamp))
            
            # Update or insert last notification time
            cursor.execute("""
                INSERT OR REPLACE INTO LastNotificationTime (PatientID, LastNotification)
                VALUES (?, ?)
            """, (patient_id, timestamp))
            
            conn.commit()
            
            # Show success message
            success_window = ctk.CTkToplevel(self)
            success_window.title("Success")
            success_window.geometry("300x150")
            
            success_label = ctk.CTkLabel(
                success_window,
                text="Notification sent successfully!",
                font=("Arial", 14),
                text_color="#046A38"
            )
            success_label.pack(pady=20)
            
            # Close success window after 2 seconds
            success_window.after(2000, success_window.destroy)
            
            # Update button appearance
            self.update_notify_button(patient_id)
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def update_notify_button(self, patient_id):
        # Find the notify button for this patient and update its appearance
        for widget in self.patient_window.winfo_children():
            if isinstance(widget, ctk.CTkFrame):  # This is the table frame
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkFrame):  # This is a row frame
                        for button in child.winfo_children():
                            if isinstance(button, ctk.CTkButton) and button.cget("text") == "Notify":
                                # Check if button should be disabled
                                conn = sqlite3.connect("Database_proj.db")
                                cursor = conn.cursor()
                                try:
                                    cursor.execute("""
                                        SELECT LastNotification 
                                        FROM LastNotificationTime 
                                        WHERE PatientID = ?
                                    """, (patient_id,))
                                    
                                    result = cursor.fetchone()
                                    if result:
                                        last_notification = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
                                        time_diff = datetime.now() - last_notification
                                        
                                        if time_diff.total_seconds() < 24 * 3600:
                                            button.configure(
                                                fg_color="#CCCCCC",  # Grey color
                                                hover_color="#999999",
                                                state="disabled"
                                            )
                                        else:
                                            button.configure(
                                                fg_color="#73C8AE",
                                                hover_color="#046A38",
                                                state="normal"
                                            )
                                finally:
                                    conn.close()
                                return

    def show_patient_list(self):
        # Create a new window for the patient list
        self.patient_window = ctk.CTkToplevel(self)
        self.patient_window.title("Fix an appointment")
        self.patient_window.geometry("1000x600")
        
        # Create main frame
        main_frame = ctk.CTkFrame(self.patient_window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create canvas and scrollbar
        canvas = ctk.CTkCanvas(main_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
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
        table_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)
        
        # Configure grid
        for i in range(5):
            table_frame.grid_columnconfigure(i, weight=1)

        headers = ["Patient ID", "Name", "Surname", "Source", "Action"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                table_frame,
                text=header,    
                font=("Arial", 16, "bold"),
                text_color="white",
                fg_color="#73C8AE",
                corner_radius=5,
                height=40
            )
            header_label.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")

        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()

        sources = {
            "Seven_days_patients_ok": "7-Day OK",
            "Follow_Up_Patients": "Follow-Up",
            "Possible_Follow_Up_Patients": "Possible Follow-Up",
            "OSA_Patients": "OSA"
        }

        all_patients = []
        
        try:
            # Get patients from each source
            for source, display_name in sources.items():
                cursor.execute(f"SELECT PatientID, Name, Surname FROM {source}")
                patients = cursor.fetchall()
                for patient in patients:
                    all_patients.append((patient[0], patient[1], patient[2], display_name))
            
            # Sort patients by name
            all_patients.sort(key=lambda x: (x[1], x[2]))
            
            # Display patients
            for i, (patient_id, Name, Surname, source) in enumerate(all_patients, start=1):
                # Alternate background color
                bg_color = "#F2F2F2" if i % 2 == 0 else "white"
                
                # Patient ID
                id_label = ctk.CTkLabel(
                    table_frame,
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
                    table_frame,
                    text=Name,
                    font=("Arial", 14),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                name_label.grid(row=i, column=1, padx=2, pady=2, sticky="nsew")
                
                # Surname
                surname_label = ctk.CTkLabel(
                    table_frame,
                    text=Surname,
                    font=("Arial", 14),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                surname_label.grid(row=i, column=2, padx=2, pady=2, sticky="nsew")
                
                # Source
                source_label = ctk.CTkLabel(
                    table_frame,
                    text=source,
                    font=("Arial", 14),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                source_label.grid(row=i, column=3, padx=2, pady=2, sticky="nsew")
                
                # Action buttons frame
                action_frame = ctk.CTkFrame(table_frame, fg_color=bg_color)
                action_frame.grid(row=i, column=4, padx=2, pady=2, sticky="nsew")
                
                # Check if notification is on cooldown
                cursor.execute("""
                    SELECT LastNotification 
                    FROM LastNotificationTime 
                    WHERE PatientID = ?
                """, (patient_id,))
                
                result = cursor.fetchone()
                button_enabled = True
                button_color = "#73C8AE"
                hover_color = "#046A38"
                
                if result:
                    last_notification = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
                    time_diff = datetime.now() - last_notification
                    
                    if time_diff.total_seconds() < 24 * 3600:
                        button_enabled = False
                        button_color = "#CCCCCC"
                        hover_color = "#999999"

                notify_btn = ctk.CTkButton(
                    action_frame,
                    text="Notify",
                    width=100,
                    height=40,
                    font=("Arial", 16),
                    fg_color=button_color,
                    hover_color=hover_color,
                    text_color="white",
                    state="normal" if button_enabled else "disabled",
                    command=lambda pid=patient_id, name=Name, surname=Surname: self.send_notification_to_patient(pid, name, surname)
                )
                notify_btn.pack(padx=5, pady=5)
                
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(table_frame, text=f"Error loading patients: {str(e)}", text_color="red")
            error_label.grid(row=1, column=0, columnspan=5, pady=20)

        finally:
            conn.close()

