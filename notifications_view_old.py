import customtkinter as ctk
import sqlite3
import datetime
from tkinter import ttk

class NotificationsView(ctk.CTkFrame):
    def __init__(self, parent_frame, user_id, user_type):
        super().__init__(parent_frame)
        self.pack(fill="both", expand=True)
        
        self.user_id = user_id
        self.user_type = user_type
        
        # Configure the frame with light blue-green background
        self.configure(fg_color="#E8F5F2")
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="Questionnaire Answers", 
            font=("Arial", 24, "bold"), 
            text_color="#046A38"
        )
        title.pack(pady=20)
        
        # Create table frame with white background and rounded corners
        table_frame = ctk.CTkFrame(self, fg_color="E8F5F2", corner_radius=10)
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Configure grid weights for different column widths
        for i in range(5):
            table_frame.grid_columnconfigure(1, weight=1)
            table_frame.grid_columnconfigure(1, weight=1)
            table_frame.grid_columnconfigure(1, weight=3)
            table_frame.grid_columnconfigure(1, weight=3)
            table_frame.grid_columnconfigure(1, weight=3)

            # Headers with light blue-green background
        headers = ["Date", "Patient ID", "Problems with the therapy", "Note for the doctor", "Reason of bad sleep"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                table_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="white",
                fg_color="#73C8AE",
                corner_radius=5,
                height=40  # Fixed height for headers
            )
            header_label.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")

        for i, (date, patient_id, problems_with_the_therapy, note_for_the_doctor, reason_of_bad_sleep) in enumerate(drugs, start=1):
            bg_color = "#F2F2F2" if i % 2 == 0 else "white"
            # data
            date_label = ctk.CTkLabel(
                table_frame,
                text=,
                font=("Arial", 12),
                text_color="#046A38",
                fg_color=bg_color,
                anchor="center",
                height=40
                )
            date_label.grid(row=i, column=0, padx=2, pady=2, sticky="nsew")

            # patient id
            start_label = ctk.CTkLabel(
                table_frame,
                text=start_date,
                font=("Arial", 12),
                text_color="#046A38",
                fg_color=bg_color,
                anchor="center",
                height=40
                )
            start_label.grid(row=i, column=1, padx=2, pady=2, sticky="nsew")

                    # problems with the therapy
                    end_label = ctk.CTkLabel(
                        table_frame,
                        text=end_date,
                        font=("Arial", 12),
                        text_color="#046A38",
                        fg_color=bg_color,
                        anchor="center",
                        height=40
                    )
                    end_label.grid(row=i, column=2, padx=2, pady=2, sticky="nsew")
            # note for the doctor
                    end_label = ctk.CTkLabel(
                        table_frame,
                        text=end_date,
                        font=("Arial", 12),
                        text_color="#046A38",
                        fg_color=bg_color,
                        anchor="center",
                        height=40
                    )
                    end_label.grid(row=i, column=2, padx=2, pady=2, sticky="nsew")
            # reason of bad sleep
                    end_label = ctk.CTkLabel(
                        table_frame,
                        text=end_date,
                        font=("Arial", 12),
                        text_color="#046A38",
                        fg_color=bg_color,
                        anchor="center",
                        height=40
                    )
                    end_label.grid(row=i, column=2, padx=2, pady=2, sticky="nsew")


        # Load questionnaire responses
        self.load_responses()

    def load_responses(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            # Get questionnaire responses for the doctor's patients
            cursor.execute("""
                SELECT q.Date, q.PatientID, q.Q9, q.Q11, q.Nota2
                FROM Questionnaire q
                JOIN Patients p ON q.PatientID = p.PatientID
                WHERE p.DoctorID = ?
                ORDER BY q.Date DESC
            """, (self.user_id,))
            
            responses = cursor.fetchall()
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Insert responses
            for response in responses:
                # Format the date
                try:
                    date_obj = datetime.datetime.strptime(response[0], "%Y-%m-%d %H:%M:%S")
                    formatted_date = date_obj.strftime("%B %d, %Y at %H:%M")
                except:
                    formatted_date = response[0]
                
                self.tree.insert("", "end", values=(
                    formatted_date,
                    response[1],  # PatientID
                    response[2],  # Q9
                    response[3],  # Q11
                    response[4]   # Nota2
                ))
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close() 