import customtkinter as ctk
import os
from PIL import Image
import sqlite3
import tkinter.ttk as ttk
from OSA_Patients import OSAPatientsView  
import datetime


class DoctorMainView(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        
        self.user_id = user_id
        self.doctor_name = self.get_doctor_name(user_id)


        self.title("Doctor Main View")
        self.geometry("1200x800")

        # Layout setup
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color="#A8DAB5")  # Light green background
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_rowconfigure(8, weight=1)  # Changed back to 8 for proper spacing

        self.doctor_label = ctk.CTkLabel(
            self.sidebar, 
            text=f"🧑‍⚕️ {self.doctor_name}", 
            font=("Arial", 16, "bold"),
            text_color="#046A38"  # Dark green text
        )
        self.doctor_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Bottoni sidebar
        buttons = [
            ("OSA patients", self.go_to_OSA_Patients),
            ("7 Days OK Patients", self.go_to_7_days_ok),
            ("Follow up patients", self.go_to_follow_up),
            ("Possible Follow up", self.go_to_possible_follow_up),
            ("Visits", self.go_to_visits),
            ("Notifications", self.show_notifications)
        ]
        
        self.sidebar_buttons = []  # Store buttons for selection state
        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                height=40,
                command=lambda t=text, c=command: self.select_sidebar_button(t, c),
                fg_color="transparent",
                text_color="#046A38",  # Dark green text
                hover_color="#92D6B5",  # Light green hover
                corner_radius=0
            )
            btn.grid(row=i + 1, column=0, padx=10, pady=5, sticky="ew")
            self.sidebar_buttons.append(btn)
            
            # Set OSA patients button as selected by default
            if text == "OSA patients":
                btn.configure(
                    fg_color="#046A38",  # Dark green background
                    text_color="white"  # White text
                )

        # Add logo at the bottom of sidebar
        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open(os.path.join("images", "logo.png")),
                dark_image=Image.open(os.path.join("images", "logo.png")),
                size=(100, 100)
            )
            logo_label = ctk.CTkLabel(
                self.sidebar,
                image=logo_image,
                text=""
            )
            logo_label.grid(row=7, column=0, padx=20, pady=(260,0), sticky="s")
        except Exception as e:
            # Fallback to text if logo fails to load
            logo_label = ctk.CTkLabel(
                self.sidebar,
                text="StarNapp",
                font=("Arial", 20, "bold"),
                text_color="#046A38"
            )
            logo_label.grid(row=7, column=0, padx=20, pady=20, sticky="s")

        # Support Button below the logo
        support_button = ctk.CTkButton(
            self.sidebar,
            text="Request Support",
            height=40,
            command=self.contact_support,
            fg_color="transparent",
            text_color="#046A38",
            hover_color="#92D6B5",
            corner_radius=0
        )
        support_button.grid(row=8, column=0, padx=10, pady=(5,20), sticky="s")

        # Main content frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#E8F5F2")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Load initial view
        self.go_to_OSA_Patients()

    def select_sidebar_button(self, text, command):
        # Reset all buttons to default state
        for btn in self.sidebar_buttons:
            btn.configure(
                fg_color="transparent",
                text_color="#046A38"
            )
        
        # Set selected button state
        for btn in self.sidebar_buttons:
            if btn.cget("text") == text:
                btn.configure(
                    fg_color="#046A38",
                    text_color="white"
                )
                break
        
        # Execute the command
        command()

    def contact_support(self):
        support_window = ctk.CTkToplevel(self)
        support_window.title("Contact Support")
        support_window.geometry("400x300")
        support_window.configure(fg_color="#E8F5F2")
        
        label = ctk.CTkLabel(
            support_window, 
            text="Write your message below:", 
            font=("Arial", 14),
            text_color="#046A38"
        )
        label.pack(pady=10)

        message_entry = ctk.CTkTextbox(
            support_window, 
            height=150, 
            wrap="word",
            fg_color="white"
        )
        message_entry.pack(padx=20, pady=10, fill="both", expand=True)

        def send_message():
            message = message_entry.get("1.0", "end").strip()
            if message:
                self.save_support_message(message)
                support_window.destroy()

        send_button = ctk.CTkButton(
            support_window, 
            text="Send", 
            command=send_message,
            fg_color="#046A38",
            text_color="white"
        )
        send_button.pack(pady=10)

    def save_support_message(self, message):
        try:
            conn = sqlite3.connect("Database_proj.db")
            cursor = conn.cursor()

            # Insert the support message
            cursor.execute("""
                INSERT INTO SupportMessages (user_id, user_type, message, date)
                VALUES (?, ?, ?, ?)
            """, (self.user_id, "doctor", message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving support message: {e}")

    def show_notifications(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
            
        # Create notifications view
        from notification_view import NotificationsView
        notifications_view = NotificationsView(
            self.main_frame,
            user_id=self.user_id,
            user_type="doctor"
        )
        notifications_view.pack(fill="both", expand=True)

    def get_doctor_name(self, user_id) :
            conn = sqlite3.connect("Database_proj.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Name, Surname FROM Doctors WHERE doctorID = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            return f"{result[0]} {result[1]}" if result else "Unknown Doctor"

    def go_to_OSA_Patients(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create OSA patients view
        from OSA_Patients import OSAPatientsView
        osa_view = OSAPatientsView(self.main_frame, self.user_id)
        osa_view.pack(fill="both", expand=True)

    def go_to_possible_follow_up(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create possible follow up view
        from Possible_Follow_Up_Patients import PossibleFollowUpPatientsView
        follow_up_view = PossibleFollowUpPatientsView(self.main_frame, self.user_id)
        follow_up_view.pack(fill="both", expand=True)

    def go_to_follow_up(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create follow up view
        from Follow_Up_Patients import FollowUpPatientsView
        follow_up_view = FollowUpPatientsView(self.main_frame, self.user_id)
        follow_up_view.pack(fill="both", expand=True)
    
    def go_to_visits(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create visits view
        from VisitDoctorView import VisitDoctorView
        visits_view = VisitDoctorView(self.main_frame, self.user_id)
        visits_view.pack(fill="both", expand=True)

    def go_to_7_days_ok(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create 7 days ok view
        from Seven_Days_ok_patients import Seven_Days_Ok_PatientsView
        seven_days_view = Seven_Days_Ok_PatientsView(self.main_frame, self.user_id)
        seven_days_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = DoctorMainView(user_id="DOC001")
    app.mainloop()