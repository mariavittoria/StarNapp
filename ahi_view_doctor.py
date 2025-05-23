import sqlite3
import datetime
import customtkinter as ctk

# matplotlib
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class AHIViewDoctor(ctk.CTkFrame):
    def __init__(self, master, patient_id, patient_name="Unknown Patient", go_back_callback=None):
        super().__init__(master, corner_radius=10, fg_color="#f4f9ff")
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.go_back_callback = go_back_callback
        self.grid(row=0, column=0, sticky="nsew")
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#f4f9ff")
        self.main_frame.pack(fill="both", expand=True)
        self.show_ahi()

    def get_indexes_data(self):
        import sqlite3
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Date, ValueAHI FROM Indexes WHERE PatientID = ? ORDER BY Date DESC", (self.patient_id,))
        data = cursor.fetchall()
        conn.close()
        return data

    def show_ahi(self):
        data = self.get_indexes_data()
        last_night_value = data[0][1] if data else "N/A"

        # Clear main_frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Add back button
        back_btn = ctk.CTkButton(
            self.main_frame,
            text="\u2190 Back",
            width=100,
            fg_color="#204080",
            command=self.go_back
        )
        back_btn.pack(anchor="w", padx=20, pady=20)

        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=7)
        seven_days_data = [value for date_str, value in data if datetime.date.fromisoformat(date_str) >= seven_days_ago]
        seven_days_mean = round(sum(seven_days_data) / len(seven_days_data), 2) if seven_days_data else "N/A"

        ctk.CTkLabel(self.main_frame, text="AHI", font=("Arial", 24, "bold"), text_color="#204080").pack(pady=(10, 5))
        ctk.CTkLabel(self.main_frame, text=f"Last Night Value: {last_night_value}", font=("Arial", 16), text_color="#102040").pack(pady=5)
        ctk.CTkLabel(self.main_frame, text=f"7 Days Mean: {seven_days_mean}", font=("Arial", 16), text_color="#102040").pack(pady=5)

        plot_frame = ctk.CTkFrame(self.main_frame, height=350, width=800, fg_color="white")
        plot_frame.pack(pady=20)

        if data:
            dates = [datetime.datetime.strptime(date_str, "%Y-%m-%d").date() for date_str, _ in data]
            values = [value for _, value in data]

            fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)
            ax.plot(dates, values, marker="o", markersize=5, linewidth=2, color="#3366cc")
            ax.set_title("AHI values over time", fontsize=13, fontweight="bold")
            ax.set_xlabel("Date", fontsize=10)
            ax.set_ylabel("AHI", fontsize=10)
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