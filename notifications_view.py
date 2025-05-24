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
        table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        table_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Create Treeview with custom style
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="white",
            foreground="#046A38",
            fieldbackground="white",
            rowheight=30
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#A8DAB5",  # Light green background for headers
            foreground="#046A38",  # Dark green text
            relief="flat",
            font=("Arial", 10, "bold")
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#A8DAB5")]  # Keep the same color when hovering
        )

        # Create Treeview
        self.tree = ttk.Treeview(
            table_frame,
            style="Custom.Treeview",
            columns=("Date", "Patient ID", "Problems with the therapy", "Note for the doctor", "Reason of bad sleep"),
            show="headings"
        )

        # Configure columns
        self.tree.heading("Date", text="Date", anchor="center")
        self.tree.heading("Patient ID", text="Patient ID", anchor="center")
        self.tree.heading("Problems with the therapy", text="Problems with the therapy", anchor="center")
        self.tree.heading("Note for the doctor", text="Note for the doctor", anchor="center")
        self.tree.heading("Reason of bad sleep", text="Reason of bad sleep", anchor="center")

        # Set column widths
        self.tree.column("Date", width=150, anchor="center")
        self.tree.column("Patient ID", width=100, anchor="center")
        self.tree.column("Problems with the therapy", width=200, anchor="center")
        self.tree.column("Note for the doctor", width=200, anchor="center")
        self.tree.column("Reason of bad sleep", width=200, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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