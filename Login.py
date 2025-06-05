import customtkinter as ctk
import sqlite3
import os
from PIL import Image
import tkinter.ttk as ttk
from datetime import datetime

print("Login.py loaded")

class AppProg:
    def __init__(self):
        self.user = ""
        self.conn = None
        self.cursor = None
        self.setup_database()

        ctk.set_appearance_mode("light")

        self.root = ctk.CTk()
        self.root.title("StarNapp | Login")
        self.root.geometry("500x900")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.configure(fg_color="#2C5234")
        
        self.setup_login()
        self.root.mainloop()

    def setup_database(self):
        try:
            self.conn = sqlite3.connect("Database_proj.db")
            self.cursor = self.conn.cursor()
            # Test the connection
            self.cursor.execute("SELECT 1")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            self.root.destroy()

    def setup_login(self):
        try:
            image_path = os.path.join("images", "logo.png")
            logo_image = Image.open(image_path)
            logo_image = logo_image.resize((300, 300), Image.Resampling.LANCZOS)
            self.logo_photo = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(200, 200)
            )
            
            logo_label = ctk.CTkLabel(
                self.root,
                image=self.logo_photo,
                text="",
                fg_color="transparent"
            )
            logo_label.pack(pady=(30, 0))
        except Exception as e:
            print(f"Error loading logo: {e}")

        self.login_frame = ctk.CTkFrame(
            self.root,
            width=800,
            height=600,
            corner_radius=15,
            fg_color="#FFFFFF"
        )
        self.login_frame.pack(pady=(20, 50), padx=50)

        title = ctk.CTkLabel(
            self.login_frame,
            text="Login",
            font=("Arial", 32, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=(40, 40))

        self.role_option = ctk.CTkOptionMenu(
            self.login_frame,
            values=["Doctor", "Patient"],
            width=350,
            height=45,
            fg_color="#A8DAB5",
            text_color="#046A38",
            button_color="#046A38",
            button_hover_color="#009639",
            dropdown_fg_color="#A8DAB5",
            dropdown_text_color="#046A38",
            dropdown_hover_color="#92D6B5",
            font=("Arial", 14)
        )
        self.role_option.set("Doctor")
        self.role_option.pack(pady=25)

        self.email_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="ID",
            width=350,
            height=45,
            fg_color="#A8DAB5",
            text_color="#046A38",
            placeholder_text_color="#046A38",
            font=("Arial", 14)
        )
        self.email_entry.pack(pady=25)

        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Password",
            show="*",
            width=350,
            height=45,
            fg_color="#A8DAB5",
            text_color="#046A38",
            placeholder_text_color="#046A38",
            font=("Arial", 14)
        )
        self.password_entry.pack(pady=25)

        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            command=self.login,
            width=250,

            fg_color="#046A38",
            text_color="white",
            hover_color="#009639",
            font=("Arial", 16, "bold")
        )
        self.login_button.pack(pady=40)

        self.message_label = ctk.CTkLabel(
            self.login_frame,
            text="",
            font=("Arial", 14),
            text_color="#046A38"
        )
        self.message_label.pack(pady=(10, 0))

    def login(self):
        user_id = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_option.get()

        # Update eta pazienti
        self.cursor.execute("SELECT PatientID, dateOfBirth FROM Patients")
        patients = self.cursor.fetchall()
        for pid, dob in patients:
            new_age = self.calcola_eta(dob)
            self.cursor.execute("UPDATE Patients SET age = ? WHERE PatientID = ?", (new_age, pid))
        self.conn.commit()

        if not user_id or not password:
            self.message_label.configure(text="Please fill in all fields", text_color="red")
            return

        try:
            if role == "Doctor":
                self.cursor.execute(
                    "SELECT * FROM Doctors WHERE doctorID = ? AND DoctorPassword = ?", 
                    (user_id, password)
                )
                result = self.cursor.fetchone()
                
                if result:
                    # Update eta pazienti
                    self.cursor.execute("SELECT PatientID, dateOfBirth FROM Patients")
                    patients = self.cursor.fetchall()
                    for pid, dob in patients:
                        new_age = self.calcola_eta(dob)
                        self.cursor.execute("UPDATE Patients SET age = ? WHERE PatientID = ?", (new_age, pid))
                    self.conn.commit()
                    
                    self.user_id = user_id
                    self.message_label.configure(text="Doctor login successful", text_color="green")
                    self.go_to_home_doctor()
                else:
                    self.message_label.configure(text="Invalid doctor credentials", text_color="red")

            elif role == "Patient":
                self.cursor.execute(
                    "SELECT * FROM Patients WHERE PatientID = ? AND PatientPassword = ?", 
                    (user_id, password)
                )
                result = self.cursor.fetchone()
                
                if result:
                    self.user_id = user_id
                    self.message_label.configure(text="Patient login successful", text_color="green")
                    self.go_to_home_patient()
                else:
                    self.message_label.configure(text="Invalid patient credentials", text_color="red")

        except sqlite3.Error as e:
            self.message_label.configure(text=f"Database error: {str(e)}", text_color="red")
        except Exception as e:
            self.message_label.configure(text=f"An error occurred: {str(e)}", text_color="red")

    def go_to_home_doctor(self):
        try:
            from doctor_main_view import DoctorMainView
            doctor_window = DoctorMainView(self.user_id)
            self.root.withdraw()
            doctor_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(doctor_window))
            doctor_window.mainloop()
        except Exception as e:
            self.message_label.configure(text=f"Error loading doctor interface: {str(e)}", text_color="red")
            self.root.deiconify()

    def go_to_home_patient(self):
        try:
            from patient_main_view import PatientMainView
            patient_window = PatientMainView(self.user_id)
            self.root.withdraw()
            
            patient_window.update_idletasks()
            patient_window.deiconify()
            patient_window.lift()
            patient_window.focus_force()
            
            patient_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(patient_window))
            patient_window.mainloop()
        except Exception as e:
            self.message_label.configure(text=f"Error loading patient interface: {str(e)}", text_color="red")
            self.root.deiconify()

    def on_closing(self, window=None):
        if window:
            window.destroy()
        if self.conn:
            self.conn.close()
        self.root.destroy()

    def __del__(self):
        if self.conn:
            self.conn.close()

    @staticmethod
    def calcola_eta(dob_str):
        """Calculate age from date of birth string."""
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

if __name__ == "__main__":
    AppProg()