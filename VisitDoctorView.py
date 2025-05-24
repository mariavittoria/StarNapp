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
            width=200,
            height=40,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=self.show_calendar
        )
        calendar_btn.pack(pady=15)
        
        # Fix a Visit button
        fix_visit_btn = ctk.CTkButton(
            buttons_frame,
            text="Fix an appointment",
            width=200,
            height=40,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=self.show_patient_list
        )
        fix_visit_btn.pack(pady=15)

    def show_calendar(self):
        # Create a new window for the calendar
        calendar_window = ctk.CTkToplevel(self)
        calendar_window.title("Visit Calendar")
        calendar_window.geometry("1200x800")
        
        # Create main frame
        main_frame = ctk.CTkFrame(calendar_window, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create navigation frame
        nav_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        # Previous day button
        prev_btn = ctk.CTkButton(
            nav_frame,
            text="← Previous Day",
            width=150,
            height=30,
            fg_color="#73C8AE",
            hover_color="#046A38",
            text_color="white",
            command=lambda: self.navigate_days(-1)
        )
        prev_btn.pack(side="left", padx=10)
        
        # Next day button
        next_btn = ctk.CTkButton(
            nav_frame,
            text="Next Day →",
            width=150,
            height=30,
            fg_color="#73C8AE",
            hover_color="#046A38",
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
        
        # Initialize current date
        self.current_date = datetime.now()
        
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
                font=("Arial", 14, "bold"),
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
                    height=30,
                    fg_color="#73C8AE" if not is_booked else "#CCCCCC",
                    hover_color="#046A38" if not is_booked else "#999999",
                    text_color="white",
                    command=lambda d=current_day.strftime("%Y-%m-%d"), t=time, n=patient_name, s=patient_surname: 
                        self.show_appointment_details(d, t, n, s) if is_booked else None
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
        # Create details window
        details_window = ctk.CTkToplevel(self)
        details_window.title("Appointment Details")
        details_window.geometry("400x200")
        
        # Patient info
        info_label = ctk.CTkLabel(
            details_window,
            text=f"Patient: {name} {surname}\nDate: {date}\nTime: {time}",
            font=("Arial", 14),
            text_color="#046A38"
        )
        info_label.pack(pady=20)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            details_window,
            text="Delete Appointment",
            width=200,
            height=40,
            fg_color="#FF9999",
            hover_color="#FF6666",
            text_color="white",
            command=lambda: self.delete_appointment(date, time, details_window)
        )
        delete_btn.pack(pady=20)

    def delete_appointment(self, date, time, window):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM Appointments
                WHERE doctor_id = ? AND date = ? AND time = ?
            """, (self.doctor_id, date, time))
            
            conn.commit()
            
            # Close details window
            window.destroy()
            
            # Refresh calendar
            self.show_five_days()
            
            # Show success message
            success_window = ctk.CTkToplevel(self)
            success_window.title("Success")
            success_window.geometry("300x150")
            
            success_label = ctk.CTkLabel(
                success_window,
                text="Appointment deleted successfully!",
                font=("Arial", 14),
                text_color="#046A38"
            )
            success_label.pack(pady=20)
            
            # Close success window after 2 seconds
            success_window.after(2000, success_window.destroy)
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def show_patient_list(self):
        # Create a new window for the patient list
        patient_window = ctk.CTkToplevel(self)
        patient_window.title("Select Patient for Visit")
        patient_window.geometry("1000x600")
        
        # Create table frame
        table_frame = ctk.CTkFrame(patient_window, fg_color="white", corner_radius=10)
        table_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Create Treeview with custom style
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="white",
            foreground="#046A38",
            fieldbackground="white",
            rowheight=40
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#A8DAB5",
            foreground="#046A38",
            relief="flat",
            font=("Arial", 10, "bold")
        )
        
        # Create Treeview
        self.tree = ttk.Treeview(
            table_frame,
            style="Custom.Treeview",
            columns=("Patient ID", "Name", "Surname", "Type", "Actions"),
            show="headings"
        )
        
        # Configure columns
        self.tree.heading("Patient ID", text="Patient ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Surname", text="Surname")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Actions", text="Actions")
        
        # Set column widths
        self.tree.column("Patient ID", width=100, anchor="center")
        self.tree.column("Name", width=200, anchor="center")
        self.tree.column("Surname", width=200, anchor="center")
        self.tree.column("Type", width=150, anchor="center")
        self.tree.column("Actions", width=250, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load patients
        self.load_patients()

    def load_patients(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            # Get all patients with their types
            cursor.execute("""
                SELECT p.PatientID, p.Name, p.Surname,
                    CASE 
                        WHEN o.PatientID IS NOT NULL THEN 'OSA'
                        WHEN s.PatientID IS NOT NULL THEN '7 Days OK'
                        WHEN f.PatientID IS NOT NULL THEN 'Follow Up'
                        WHEN pf.PatientID IS NOT NULL THEN 'Possible Follow Up'
                        ELSE 'Unknown'
                    END as Type
                FROM Patients p
                LEFT JOIN OSA_Patients o ON p.PatientID = o.PatientID
                LEFT JOIN Seven_Days_Patients_ok s ON p.PatientID = s.PatientID
                LEFT JOIN Follow_Up_Patients f ON p.PatientID = f.PatientID
                LEFT JOIN Possible_Follow_Up_Patients pf ON p.PatientID = pf.PatientID
                WHERE p.DoctorID = ?
            """, (self.doctor_id,))
            
            patients = cursor.fetchall()
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Insert patients with action buttons
            for patient in patients:
                patient_id, name, surname, patient_type = patient
                self.tree.insert("", "end", values=(patient_id, name, surname, patient_type, ""))
                
                # Create buttons frame
                buttons_frame = ctk.CTkFrame(self.tree, fg_color="transparent")
                buttons_frame.pack()
                
                # Create notification button
                notify_btn = ctk.CTkButton(
                    buttons_frame,
                    text="Send Notification",
                    width=150,
                    height=30,
                    fg_color="#73C8AE",
                    hover_color="#046A38",
                    text_color="white",
                    command=lambda pid=patient_id, n=name, s=surname: self.send_notification(pid, n, s)
                )
                notify_btn.pack(side="left", padx=5)
                
                # Get the item ID
                item_id = self.tree.get_children()[-1]
                
                # Set the buttons frame in the tree
                self.tree.set(item_id, "Actions", buttons_frame)
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

    def send_notification(self, patient_id, name, surname):
        # Create notification for the patient
        message = "The doctor requested a visit with you"
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message, Timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (patient_id, f"{name} {surname}", "visit_request", message, timestamp))
            
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
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()