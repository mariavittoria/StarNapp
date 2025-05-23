import sqlite3
import datetime
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class ODIViewPaziente(ctk.CTkFrame):
    def __init__(self, parent, patient_id, patient_name, go_back_callback=None):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.go_back_callback = go_back_callback

        # Configure the frame with light blue-green background
        self.configure(fg_color="#E8F5F2")
        self.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_odi()

    def get_indexes_data(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Date, ValueODI FROM Indexes WHERE PatientID = ? AND ValueODI IS NOT NULL ORDER BY Date DESC", (self.patient_id,))
        data = cursor.fetchall()
        conn.close()
        return data

    def show_odi(self):
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
        back_btn.pack(anchor="w", padx=20, pady=(20, 10))

        # Add title below back button
        title = ctk.CTkLabel(
            self,
            text="ODI Trend",
            font=("Arial", 24, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=(0, 20))

        # Get ODI data
        data = self.get_indexes_data()

        if not data:
            no_data_label = ctk.CTkLabel(
                self,
                text="No ODI data available",
                font=("Arial", 16),
                text_color="#046A38"
            )
            no_data_label.pack(pady=20)
            return

        # Calculate last night value and 7-day mean
        last_night = data[0][1] if data else None
        seven_day_mean = sum(row[1] for row in data[:7]) / min(len(data), 7) if data else None

        # Create a frame for the values
        values_frame = ctk.CTkFrame(self, fg_color="#E8F5F2", corner_radius=10)
        values_frame.pack(pady=10)

        # Create a frame for the stats with white background
        stats_frame = ctk.CTkFrame(values_frame, fg_color="white", corner_radius=8)
        stats_frame.pack(pady=5, padx=10)

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

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 5))  # Reduced height
        dates = [datetime.datetime.strptime(row[0], "%Y-%m-%d") for row in data]
        values = [row[1] for row in data]

        ax.plot(dates, values, marker='o', linestyle='-', color='#046A38')
        ax.set_xlabel("Date", color="#046A38")
        ax.set_ylabel("ODI Value", color="#046A38")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_facecolor("#E8F5F2")
        fig.patch.set_facecolor("#E8F5F2")

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)

        # Add data labels above points
        for i, v in enumerate(values):
            ax.text(dates[i], v, f'{v:.1f}', ha='center', va='bottom')

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()
        else:
            from patient_main_view import PatientMainView
            self.master.destroy()
            PatientMainView(patient_id=self.patient_id)
