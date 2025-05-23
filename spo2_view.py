import sqlite3
import datetime
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class SpO2ViewDoctor(ctk.CTk):
    def __init__(self, patient_id, patient_name="Unknown Patient"):
        super().__init__()
        self.patient_id = patient_id
        self.patient_name = patient_name

        self.title(f"SpO2 - {self.patient_name}")
        self.geometry("800x600")
        self.center_window()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#f4f9ff")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.show_spo2()

        self.mainloop()

    def center_window(self):
        w = 800
        h = 600
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def get_indexes_data(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Date, MeanSpO2 FROM Indexes WHERE PatientID = ? ORDER BY Date DESC", (self.patient_id,))
        data = cursor.fetchall()
        conn.close()
        return data

    def show_spo2(self):
        data = self.get_indexes_data()
        last_night_value = data[0][1] if data else "N/A"

        # Add back button
        back_btn = ctk.CTkButton(
            self.main_frame,
            text="← Back",
            width=100,
            fg_color="#204080",
            command=self.go_back
        )
        back_btn.pack(anchor="w", padx=10, pady=20)
        
        today = datetime.date(2025, 4, 21)  # finto oggi
        seven_days_ago = today - datetime.timedelta(days=7)
        seven_days_data = [value for date_str, value in data if datetime.date.fromisoformat(date_str) >= seven_days_ago]
        seven_days_mean = round(sum(seven_days_data) / len(seven_days_data), 2) if seven_days_data else "N/A"

        ctk.CTkLabel(self.main_frame, text="SpO₂", font=("Arial", 24, "bold"), text_color="#204080").pack(pady=(10, 5))
        ctk.CTkLabel(self.main_frame, text=f"Last Night Value: {last_night_value}", font=("Arial", 16), text_color="#102040").pack(pady=5)
        ctk.CTkLabel(self.main_frame, text=f"7 Days Mean: {seven_days_mean}", font=("Arial", 16), text_color="#102040").pack(pady=5)

        plot_frame = ctk.CTkFrame(self.main_frame, height=350, width=800, fg_color="white")
        plot_frame.pack(pady=20)

        dates = [datetime.datetime.strptime(date_str, "%Y-%m-%d").date() for date_str, value in data]
        values = [value for date_str, value in data]

        fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)
        ax.plot(dates, values, marker="o", markersize=5, linewidth=2, color="#3366cc")
        ax.set_title("SpO₂ values over time", fontsize=13, fontweight="bold")
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("SpO₂", fontsize=10)
        ax.set_ylim(min(values) - 0.5, max(values) + 0.5)
        ax.set_xticks(dates)
        ax.grid(True, linestyle='--', linewidth=0.4, color='lightgray')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
        fig.autofmt_xdate(rotation=30)

        for x, y in zip(dates, values):
            ax.text(x, y + 0.2, f"{y:.1f}", ha='center', fontsize=8, color='black')

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def go_back(self):
            if self.go_back_callback:
                self.go_back_callback()