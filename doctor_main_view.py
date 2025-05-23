import customtkinter
import os
from PIL import Image
import sqlite3
import tkinter.ttk as ttk
from OSA_Patients import OSAPatientsView  


class DoctorMainView(customtkinter.CTk):
    def __init__(self, user_id):
        super().__init__()
        
        self.user_id = user_id
        self.doctor_name = self.get_doctor_name(user_id)


        self.title("Doctor Main View")
        self.geometry("900x700")

        # Layout setup
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = customtkinter.CTkFrame(self, corner_radius=0, fg_color="#A8DAB5")  # Light green background
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.doctor_label = customtkinter.CTkLabel(
            self.sidebar, 
            text=f"🧑‍⚕️ {self.doctor_name}", 
            font=("Arial", 16, "bold"),
            text_color="#046A38"  # Dark green text
        )
        self.doctor_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Bottoni sidebar
        buttons = [
            ("OSA patients", self.go_to_OSA_Patients),
            ("Follow up patients", self.go_to_follow_up),
            ("Possible Follow up", self.go_to_possible_follow_up),
            ("7 Days OK Patients ", self.go_to_7_days_ok),
            ("Visits", self.go_to_visits),
        ]
        self.sidebar_buttons = []  # Store buttons for selection state
        for i, (text, command) in enumerate(buttons):
            btn = customtkinter.CTkButton(
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

        # Main content
        self.main_view = customtkinter.CTkFrame(self, fg_color="#E8F5F2")  # Light blue-green background
        self.main_view.grid(row=0, column=1, sticky="nsew")
        self.main_view.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Carica vista iniziale
        self.switch_main_view(self.go_to_OSA_Patients)

    def switch_main_view(self, content_function):
        for widget in self.main_view.winfo_children():
            widget.destroy()
        
        # Create container with light blue-green background
        container = customtkinter.CTkFrame(self.main_view, fg_color="#E8F5F2")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Call the content function with the container
        content_function(container)

    def get_osa_patients(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM OSA_Patients")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return column_names, rows

    def get_doctor_name(self, user_id) :
            conn = sqlite3.connect("Database_proj.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Name, Surname FROM Doctors WHERE doctorID = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            return f"{result[0]} {result[1]}" if result else "Unknown Doctor"

    def go_to_OSA_Patients(self, container=None):
        if container is None:
            container = self.main_view
            
        from OSA_Patients import OSAPatientsView
        OSAPatientsView(container, self.user_id)

    def go_to_possible_follow_up(self, container=None):
        if container is None:
            container = self.main_view
            
        from Possible_Follow_Up_Patients import PossibleFollowUpPatientsView
        PossibleFollowUpPatientsView(container, self.user_id)

    def go_to_follow_up(self, container=None):
        if container is None:
            container = self.main_view
            
        from Follow_Up_Patients import FollowUpPatientsView
        FollowUpPatientsView(container, self.user_id)
    
    def go_to_visits(self, container=None):
        if container is None:
            container = self.main_view
            
        from VisitDoctorView import VisitDoctorView
        VisitDoctorView(container, self.user_id)

    def go_to_7_days_ok(self, container=None):
        if container is None:
            container = self.main_view
            
        from Seven_Days_ok_patients import Seven_Days_Ok_PatientsView
        Seven_Days_Ok_PatientsView(container, self.user_id)

    def select_sidebar_button(self, text, command):
        # Reset all buttons to default style
        for btn in self.sidebar_buttons:
            btn.configure(
                fg_color="transparent",
                text_color="#046A38"  # Dark green text
            )
        
        # Find and highlight the selected button
        for btn in self.sidebar_buttons:
            if btn.cget("text") == text:
                btn.configure(
                    fg_color="#046A38",  # Dark green background
                    text_color="white"  # White text
                )
                break
        
        # Execute the command
        self.switch_main_view(command)

if __name__ == "__main__":
    app = DoctorMainView(user_id="DOC001")
    app.mainloop()