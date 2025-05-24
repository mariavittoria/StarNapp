import customtkinter as ctk
import sqlite3
from datetime import datetime
import tkinter.ttk as ttk

class NotificationsView(ctk.CTkFrame):
    def __init__(self, parent_frame, user_id, user_type):
        super().__init__(parent_frame)
        self.pack(fill="both", expand=True)
        
        # Configure the frame with light blue-green background
        self.configure(fg_color="#E8F5F2")
        
        # Title
        title = ctk.CTkLabel(
            self, 
            text="Patient Questionnaire Responses", 
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
        for i in range(5):  # Changed back to 5 columns
            self.table_frame.grid_columnconfigure(i, weight=1)

        # Headers
        headers = ["Date", "Patient ID", "Nota 2", "Q9", "Q11"]
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

        # Load questionnaire responses
        self.load_responses(user_id)

    def load_responses(self, doctor_id):
        conn = None
        try:
            conn = sqlite3.connect("Database_proj.db")
            cursor = conn.cursor()
            
            # First, verify the doctor exists
            cursor.execute("SELECT doctorID FROM Doctors WHERE doctorID = ?", (doctor_id,))
            if not cursor.fetchone():
                error_label = ctk.CTkLabel(
                    self.table_frame,
                    text=f"Error: Doctor ID {doctor_id} not found",
                    text_color="red"
                )
                error_label.grid(row=1, column=0, columnspan=5, pady=20)
                return

            # Get questionnaire responses for the doctor's patients
            query = """
                SELECT 
                    q.Date,
                    p.PatientID,
                    q.Nota2,
                    q.Q9,
                    q.Q11
                FROM Questionnaire q
                JOIN Patients p ON q.PatientID = p.PatientID
                WHERE p.DoctorID = ?
                AND (
                    q.Nota2 IS NOT NULL 
                    OR q.Q9 IS NOT NULL 
                    OR q.Q11 IS NOT NULL
                )
                ORDER BY q.Date DESC
            """
            
            cursor.execute(query, (doctor_id,))
            responses = cursor.fetchall()
            
            if not responses:
                no_data_label = ctk.CTkLabel(
                    self.table_frame,
                    text="No questionnaire responses found for your patients",
                    text_color="#046A38",
                    font=("Arial", 14)
                )
                no_data_label.grid(row=1, column=0, columnspan=5, pady=20)
                return
            
            # Display responses
            for i, (date, patient_id, nota2, q9, q11) in enumerate(responses, start=1):
                # Skip if all fields are empty
                if nota2 is None and q9 is None and q11 is None:
                    continue
                
                # Format date
                try:
                    formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
                except ValueError:
                    formatted_date = date  # Use original date if parsing fails
                
                # Alternate background color
                bg_color = "#F2F2F2" if i % 2 == 0 else "white"
                
                # Date
                date_label = ctk.CTkLabel(
                    self.table_frame,
                    text=formatted_date,
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                date_label.grid(row=i, column=0, padx=2, pady=2, sticky="nsew")
                
                # Patient ID
                patient_label = ctk.CTkLabel(
                    self.table_frame,
                    text=patient_id,
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                patient_label.grid(row=i, column=1, padx=2, pady=2, sticky="nsew")
                
                # Nota 2
                nota2_label = ctk.CTkLabel(
                    self.table_frame,
                    text=str(nota2) if nota2 is not None else "-",
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                nota2_label.grid(row=i, column=2, padx=2, pady=2, sticky="nsew")
                
                # Q9
                q9_label = ctk.CTkLabel(
                    self.table_frame,
                    text=str(q9) if q9 is not None else "-",
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                q9_label.grid(row=i, column=3, padx=2, pady=2, sticky="nsew")
                
                # Q11
                q11_label = ctk.CTkLabel(
                    self.table_frame,
                    text=str(q11) if q11 is not None else "-",
                    font=("Arial", 12),
                    text_color="#046A38",
                    fg_color=bg_color,
                    anchor="center",
                    height=40
                )
                q11_label.grid(row=i, column=4, padx=2, pady=2, sticky="nsew")
                
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                self.table_frame,
                text=f"Database error: {str(e)}",
                text_color="red"
            )
            error_label.grid(row=1, column=0, columnspan=5, pady=20)
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.table_frame,
                text=f"Error: {str(e)}",
                text_color="red"
            )
            error_label.grid(row=1, column=0, columnspan=5, pady=20)
        finally:
            if conn:
                conn.close() 