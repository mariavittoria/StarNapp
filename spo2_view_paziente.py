import sqlite3
import datetime
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys
import subprocess

class SpO2ViewPaziente(ctk.CTkFrame):
    def __init__(self, parent_frame, patient_id, patient_name, go_back_callback, is_doctor=False):
        super().__init__(parent_frame)
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.go_back_callback = go_back_callback
        self.is_doctor = is_doctor
        self.pack(fill="both", expand=True)
        
        # Configure the frame with light blue-green background
        self.configure(fg_color="#E8F5F2")
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_spo2()

    def is_follow_up_patient(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Follow_Up_Patients WHERE PatientID = ?", (self.patient_id,))
        result = cursor.fetchone() is not None
        conn.close()
        return result

    def get_indexes_data(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Date, MeanSpO2 FROM Indexes WHERE PatientID = ? AND MeanSpO2 IS NOT NULL ORDER BY Date DESC", (self.patient_id,))
        data = cursor.fetchall()
        conn.close()
        return data

    def show_spo2(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Add back button first
        back_btn = ctk.CTkButton(
            self,
            text="← Back",
            width=100,
            fg_color="#204080",
            command=self.go_back
        )
        back_btn.pack(anchor="w", padx=20, pady=(10, 5))

        # Add title below back button
        title = ctk.CTkLabel(
            self,
            text="SpO2 Trend",
            font=("Arial", 24, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=(0, 20))

        data = self.get_indexes_data()

        if not data:
            no_data_label = ctk.CTkLabel(
                self,
                text="No SpO2 data available",
                font=("Arial", 16),
                text_color="#046A38"
            )
            no_data_label.pack(pady=20)
            return

        # Calculate last night value and 7-day mean
        last_night = data[0][1] if data else None
        seven_day_mean = sum(row[1] for row in data[:7]) / min(len(data), 7) if data else None
        thirty_day_mean = sum(row[1] for row in data[:30]) / min(len(data), 30) if data and self.is_follow_up_patient() else None

        # Create a frame for the values
        values_frame = ctk.CTkFrame(self, fg_color="#E8F5F2", corner_radius=10)
        values_frame.pack(pady=(0,5))

        # Create a frame for the stats with white background
        stats_frame = ctk.CTkFrame(values_frame, fg_color="white", corner_radius=8)
        stats_frame.pack(pady=(5,0), padx=10)

        # Last night value
        last_night_label = ctk.CTkLabel(
            stats_frame,
            text="Last Night Mean:",
            font=("Arial", 12),
            text_color="#046A38"
        )
        last_night_label.grid(row=0, column=0, padx=(10, 5), pady=5)

        last_night_value = ctk.CTkLabel(
            stats_frame,
            text=f"{last_night:.1f}",
            font=("Arial", 12, "bold"),
            text_color="#046A38"
        )
        last_night_value.grid(row=0, column=1, padx=(0, 20), pady=5)

        # 7-day mean
        mean_label = ctk.CTkLabel(
            stats_frame,
            text="7-Day Mean:",
            font=("Arial", 12),
            text_color="#046A38"
        )
        mean_label.grid(row=1, column=0, padx=(10, 5), pady=5)

        mean_value = ctk.CTkLabel(
            stats_frame,
            text=f"{seven_day_mean:.1f}",
            font=("Arial", 12, "bold"),
            text_color="#046A38"
        )
        mean_value.grid(row=1, column=1, padx=(0, 20), pady=5)

        # Add 30-day mean for follow-up patients
        if self.is_follow_up_patient() and thirty_day_mean is not None:
            thirty_day_label = ctk.CTkLabel(
                stats_frame,
                text="30-Day Mean:",
                font=("Arial", 12),
                text_color="#046A38"
            )
            thirty_day_label.grid(row=2, column=0, padx=(10, 5), pady=5)

            thirty_day_value = ctk.CTkLabel(
                stats_frame,
                text=f"{thirty_day_mean:.1f}",
                font=("Arial", 12, "bold"),
                text_color="#046A38"
            )
            thirty_day_value.grid(row=2, column=1, padx=(0, 20), pady=5)

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 5))  # Reduced height
        dates = [datetime.datetime.strptime(row[0], "%Y-%m-%d") for row in data]
        values = [row[1] for row in data]

        # For follow-up patients, limit to last 30 days
        if self.is_follow_up_patient():
            thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
            dates = [d for d in dates if d >= thirty_days_ago]
            values = values[:len(dates)]

        ax.plot(dates, values, marker='o', linestyle='-', color='#046A38')
        ax.set_xlabel("Date", color="#046A38")
        ax.set_ylabel("SpO2 Value (%)", color="#046A38")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_facecolor("#E8F5F2")
        fig.patch.set_facecolor("#E8F5F2")

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=15)

        # Add data labels above points
        for i, v in enumerate(values):
            ax.text(dates[i], v, f'{v:.1f}%', ha='center', va='bottom')

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self)
        fig.tight_layout()
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0,10))

        # Add PDF button for doctors
        if self.is_doctor:
            pdf_button = ctk.CTkButton(
            self,
            text="Open PDF Report",
            width=120,
            fg_color="#046A38",
            command=self.open_pdf
        )
            pdf_button.pack(pady=0)
           

    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()
        else:
            from patient_main_view import PatientMainView
            self.master.destroy()
            PatientMainView(patient_id=self.patient_id)

    def open_pdf(self):
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, "SpO2_report.pdf")
        
        try:
            if os.path.exists(pdf_path):
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                elif os.name == 'posix':  # macOS and Linux
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', pdf_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', pdf_path])
            else:
                # Show error message if PDF doesn't exist
                error_window = ctk.CTkToplevel(self)
                error_window.title("Error")
                error_window.geometry("300x150")
                
                # Center the error window
                x = self.winfo_rootx() + (self.winfo_width() // 2) - (300 // 2)
                y = self.winfo_rooty() + (self.winfo_height() // 2) - (150 // 2)
                error_window.geometry(f"+{x}+{y}")
                
                message = ctk.CTkLabel(
                    error_window,
                    text=f"PDF file not found at:\n{pdf_path}",
                    font=("Arial", 14),
                    text_color="red"
                )
                message.pack(pady=20)
                
                ok_button = ctk.CTkButton(
                    error_window,
                    text="OK",
                    command=error_window.destroy,
                    fg_color="#046A38"
                )
                ok_button.pack(pady=10)
        except Exception as e:
            # Show error message if there's an exception
            error_window = ctk.CTkToplevel(self)
            error_window.title("Error")
            error_window.geometry("300x150")
            
            # Center the error window
            x = self.winfo_rootx() + (self.winfo_width() // 2) - (300 // 2)
            y = self.winfo_rooty() + (self.winfo_height() // 2) - (150 // 2)
            error_window.geometry(f"+{x}+{y}")
            
            message = ctk.CTkLabel(
                error_window,
                text=f"Error opening PDF:\n{str(e)}",
                font=("Arial", 14),
                text_color="red"
            )
            message.pack(pady=20)
            
            ok_button = ctk.CTkButton(
                error_window,
                text="OK",
                command=error_window.destroy,
                fg_color="#046A38"
            )
            ok_button.pack(pady=10)
