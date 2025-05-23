import sqlite3
import datetime 
from datetime import date
import customtkinter as ctk
from PIL import Image


class PatientMainView(ctk.CTk):
    def __init__(self, patient_id):
        super().__init__()

        self.patient_id = patient_id
        self.answers = {}
        self.questionnaire_done = self.check_if_questionnaire_done()

        if self.questionnaire_done:
            self.load_answers_from_db()

        self.patient_name = self.get_patient_name(patient_id)
        self.notification_count = self.get_notification_count()
        self.current_start_date = datetime.date.today() + datetime.timedelta(days=1)
        self.selected_date = None
        self.selected_time = None
        self.slot_buttons = {}

        self.title(f"Patient Dashboard - {self.patient_name}")
        self.geometry("900x600")
        self.center_window()

        # Layout principale
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#A8DAB5")  # Light green background
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)  # This will push the logo to the bottom

        self.profile_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text=f"👤 {self.patient_name}", 
            font=("Arial", 16, "bold"),
            text_color="#046A38"  # Dark green text
        )
        self.profile_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Sidebar buttons
        buttons = [
            ("Home", self.show_home),
            ("Visual Data", self.show_visual_data),
            (f"Notifications ({self.notification_count})", self.show_notifications)
        ]
        self.sidebar_buttons = []  # Store buttons for selection state
        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                self.sidebar_frame, 
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
            
            # Set Home button as selected by default
            if text == "Home":
                btn.configure(
                    fg_color="#046A38",  # Dark green background
                    text_color="white"  # White text
                )

        # Add logo at the bottom of sidebar
        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open("logo.png"),
                dark_image=Image.open("logo.png"),
                size=(100, 100)
            )
            logo_label = ctk.CTkLabel(
                self.sidebar_frame,
                image=logo_image,
                text=""
            )
            logo_label.grid(row=5, column=0, padx=20, pady=20, sticky="sw")
        except Exception as e:
            print(f"Error loading logo: {e}")

        # Support Button below the logo
        support_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Request Support",
            height=40,
            command=self.contact_support,
            fg_color="transparent",
            text_color="#046A38",
            hover_color="#92D6B5",
            corner_radius=0
        )
        support_button.grid(row=6, column=0, padx=10, pady=(10, 10), sticky="ew")

        # Main frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="white")  # White background
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.question_text_map = {
            "Q1": "How many times did you wake up during the night?",
            "Q2": "Did you sleep well?",
            "Nota2": "Please describe what was wrong:",
            "Q3": "Have you encountered any problems with night measurements?",
            "Q4": "What kind of problems did you have?",
            "Q5": "Do you want to receive a daily reminder?",
            "Q6": "Is technical support needed?",
            "Q7": "Did you have any sleep apneas and if so, how many?",
            "Q8": "Did you follow the therapy?",
            "Q9": "What went wrong?",
            "Q10": "Do you want to insert a note for the doctor?",
            "Q11": "Insert your note:",
            "Q12": "Did you weigh yourself today?",
            "Q13": "Insert your weight:"
        }

        self.show_home()

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

            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS SupportMessages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT,
                    message TEXT,
                    date TEXT
                )
            """)

            # Insert the support message
            cursor.execute("""
                INSERT INTO SupportMessages (patient_id, message, date)
                VALUES (?, ?, ?)
            """, (self.patient_id, message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            # Create notification for the support request
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message)
                VALUES (?, ?, 'SUPPORT', ?)
            """, (self.patient_id, self.patient_name, "You have sent a support request"))

            conn.commit()
            self.update_notification_count()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    def center_window(self):
        w = 900
        h = 600
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

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
        command()

    def show_home(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Main container with light blue-green background
        container = ctk.CTkFrame(self.main_frame, fg_color="#E8F5F2")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Top section with title and questionnaire status
        top_frame = ctk.CTkFrame(container, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(top_frame, text="Welcome to your Patient Portal", font=("Arial", 24, "bold"), text_color="#046A38")
        title.pack(pady=20)

        if self.questionnaire_done:
            button_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            button_frame.pack(pady=5)

            self.questionnaire_button = ctk.CTkButton(
                button_frame, 
                text="✔️ Questionnaire completed", 
                width=220, 
                state="disabled", 
                fg_color="#046A38",
                text_color="white"
            )
            self.questionnaire_button.pack(side="left", padx=(0, 5))

            self.answers_container = ctk.CTkFrame(container, fg_color="transparent")
            self.answers_container.pack_forget()

            self.answers_scroll_canvas = ctk.CTkCanvas(self.answers_container, bg="#E8F5F2", highlightthickness=0)
            self.answers_scroll_canvas.pack(side="left", fill="both", expand=True)

            scrollbar = ctk.CTkScrollbar(self.answers_container, orientation="vertical", command=self.answers_scroll_canvas.yview)
            scrollbar.pack(side="right", fill="y")

            self.answers_scroll_canvas.configure(yscrollcommand=scrollbar.set)

            self.answers_frame_inner = ctk.CTkFrame(self.answers_container, fg_color="transparent")
            self.answers_scroll_canvas.create_window((0, 0), window=self.answers_frame_inner, anchor="nw")

            def on_frame_configure(event):
                self.answers_scroll_canvas.configure(scrollregion=self.answers_scroll_canvas.bbox("all"))

            self.answers_frame_inner.bind("<Configure>", on_frame_configure)

            for key, answer in self.answers.items():
                if key in ["PatientID", "Date", "QuestID"]:  # Skip QuestID
                    continue
                question = self.question_text_map.get(key, key)
                answer_frame = ctk.CTkFrame(self.answers_frame_inner, fg_color="#FFFFFF", corner_radius=10)
                answer_frame.pack(fill="x", padx=30, pady=8)
                
                # Question in bold
                question_label = ctk.CTkLabel(
                    answer_frame, 
                    text=question,
                    anchor="w", 
                    justify="left", 
                    wraplength=800,
                    font=("Arial", 14, "bold"),
                    text_color="#046A38"
                )
                question_label.pack(anchor="w", padx=20, pady=(15, 5))
                
                # Answer in regular weight
                answer_label = ctk.CTkLabel(
                    answer_frame, 
                    text=f"Answer: {answer}",
                    anchor="w", 
                    justify="left", 
                    wraplength=800,
                    font=("Arial", 14),
                    text_color="#102040"
                )
                answer_label.pack(anchor="w", padx=20, pady=(0, 15))

            def toggle_answers():
                if self.answers_container.winfo_ismapped():
                    self.answers_container.pack_forget()
                    self.toggle_btn.configure(text="⬇️")
                else:
                    self.answers_container.pack(pady=10, fill="both", expand=True)
                    self.toggle_btn.configure(text="⬆️")

            self.toggle_btn = ctk.CTkButton(
                button_frame, 
                text="⬇️", 
                width=40, 
                command=toggle_answers, 
                fg_color="#73C8AE",  # Light blue-green
                text_color="white"
            )
            self.toggle_btn.pack(side="left")

        else:
            self.questionnaire_button = ctk.CTkButton(
                container, 
                text="Questionnaire", 
                width=250, 
                command=self.open_questionnaire, 
                fg_color="#73C8AE",  # Light blue-green
                text_color="white"
            )
            self.questionnaire_button.pack(pady=15)

        self.visits_button = ctk.CTkButton(
            container, 
            text="Visits", 
            width=250, 
            command=self.open_visits, 
            fg_color="#73C8AE",  # Light blue-green
            text_color="white"
        )
        self.visits_button.pack(pady=15)

        self.medication_button = ctk.CTkButton(
            container, 
            text="Medication", 
            width=250, 
            command=self.open_medication, 
            fg_color="#73C8AE",  # Light blue-green
            text_color="white"
        )
        self.medication_button.pack(pady=15)

    def show_visual_data(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create and show the indexes view
        from patient_indexes_view import PatientIndexes
        indexes_view = PatientIndexes(
            self.main_frame,
            patient_id=self.patient_id,
            patient_name=self.patient_name
        )
        indexes_view.pack(fill="both", expand=True)

    def open_questionnaire(self):
        self.current_question_index = 0
        self.answers = {}
        self.questions = [
            {"key": "Q1", "text": "How many times did you wake up during the night?", "type": "choice", "options": ["0", "1", "2", "3", "4", "5+"]},
            {"key": "Q2", "text": "Did you sleep well?", "type": "choice", "options": ["Yes", "No"]},
            {"key": "Nota2", "text": "Please describe what was wrong:", "type": "text", "conditional_on": {"key": "Q2", "value": "No"}},
            {"key": "Q3", "text": "Have you encountered any problems with night measurements?", "type": "choice", "options": ["Yes", "No"]},
            {"key": "Q4", "text": "What kind of problems did you have?", "type": "choice", "options": ["I forgot to turn on the device", "The device doesn't work", "I had problems with the application of the sensors"], "conditional_on": {"key": "Q3", "value": "Yes"}},
            {"key": "Q5", "text": "Do you want to receive a daily reminder?", "type": "choice", "options": ["Yes", "No"], "conditional_on": {"key": "Q4", "value": "I forgot to turn on the device"}},
            {"key": "Q6", "text": "Is technical support needed?", "type": "choice", "options": ["Yes", "No"], "conditional_on_any": {"key": "Q4", "values": ["The device doesn't work", "I had problems with the application of the sensors"]}},
            {"key": "Q7", "text": "Did you have any sleep apneas and if so, how many?", "type": "choice", "options": ["0", "1", "2", "3", "4", "5+"], "conditional_on_any": {"key": "Q4", "values": ["The device doesn't work", "I had problems with the application of the sensors"]}},
            {"key": "Q8", "text": "Did you follow the therapy?", "type": "choice", "options": ["Yes", "No"]},
            {"key": "Q9", "text": "What went wrong?", "type": "text", "conditional_on": {"key": "Q8", "value": "No"}},
            {"key": "Q10", "text": "Do you want to insert a note for the doctor?", "type": "choice", "options": ["Yes", "No"]},
            {"key": "Q11", "text": "Insert your note:", "type": "text", "conditional_on": {"key": "Q10", "value": "Yes"}},
            {"key": "Q12", "text": "Did you weigh yourself today?", "type": "choice", "options": ["No change in weight", "I didn't get weighed today", "Yes, I want to insert my weight"]},
            {"key": "Q13", "text": "Insert your weight:", "type": "text", "conditional_on": {"key": "Q12", "value": "Yes, I want to insert my weight"}},
        ]
        self.show_question()

    def show_question(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if self.current_question_index >= len(self.questions):
            label = ctk.CTkLabel(
                self.main_frame, 
                text="Thanks for completing the questionnaire!", 
                font=("Arial", 20, "bold"),
                text_color="#046A38"  # Dark green text
            )
            label.pack(pady=40)
            self.save_answers_to_db()
            return

        q = self.questions[self.current_question_index]

        cond = q.get("conditional_on")
        cond_any = q.get("conditional_on_any")
        if cond and self.answers.get(cond["key"]) != cond["value"]:
            self.current_question_index += 1
            self.show_question()
            return
        elif cond_any and self.answers.get(cond_any["key"]) not in cond_any["values"]:
            self.current_question_index += 1
            self.show_question()
            return

        # Create a scrollable frame for the questionnaire
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Question label with dark green color and proper wrapping
        label = ctk.CTkLabel(
            scroll_frame, 
            text=q["text"], 
            font=("Arial", 18, "bold"),
            text_color="#046A38",  # Dark green text
            wraplength=600  # Adjust this value based on your window size
        )
        label.pack(pady=(30, 50))

        self.answer_var = ctk.StringVar()
        self.answer_var.set(self.answers.get(q["key"], ""))

        # Create a frame for options to better control layout
        options_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=40)

        if q["type"] == "choice":
            for opt in q["options"]:
                btn = ctk.CTkRadioButton(
                    options_frame, 
                    text=opt, 
                    variable=self.answer_var, 
                    value=opt,
                    fg_color="#73C8AE",  # Light blue-green
                    text_color="#046A38",  # Dark green text
                    hover_color="#92D6B5",  # Light green hover
                    border_color="#046A38",  # Dark green border
                    font=("Arial", 14)  # Slightly smaller font
                )
                btn.pack(anchor="w", pady=5)
        elif q["type"] == "text":
            entry = ctk.CTkEntry(
                options_frame, 
                textvariable=self.answer_var, 
                width=400,
                height=50,
                fg_color="white",
                border_color="#73C8AE",
                text_color="#046A38",
                font=("Arial", 14)
            )
            entry.pack(pady=10)

        self.error_label = ctk.CTkLabel(
            scroll_frame, 
            text="", 
            text_color="red", 
            font=("Arial", 12)
        )
        self.error_label.pack(pady=10)

        # Navigation buttons in a separate frame
        nav = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        nav.pack(pady=20)

        if self.current_question_index > 0:
            back_btn = ctk.CTkButton(
                nav, 
                text="Back", 
                command=self.previous_question, 
                fg_color="#3498db",  # Light blue
                text_color="white",
                hover_color="#2980b9",  # Darker blue on hover
                width=120,
                height=35
            )
            back_btn.grid(row=0, column=0, padx=10)

        next_btn = ctk.CTkButton(
            nav, 
            text="Next", 
            command=self.next_question,
            fg_color="#73C8AE",  # Light blue-green
            text_color="white",
            hover_color="#92D6B5",  # Light green hover
            width=120,
            height=35
        )
        next_btn.grid(row=0, column=1, padx=10)

    def next_question(self):
        answer = self.answer_var.get()
        if not answer.strip():
            self.error_label.configure(text="Please answer before continuing.")
            return
        q = self.questions[self.current_question_index]
        self.answers[q["key"]] = answer
        self.current_question_index += 1
        self.show_question()

    def previous_question(self):
        self.current_question_index = max(0, self.current_question_index - 1)
        self.show_question()

    def save_answers_to_db(self):
        conn = sqlite3.connect("Database_proj.db")
        c = conn.cursor()
        values = {"PatientID": self.patient_id, "Date": datetime.date.today().isoformat(), **self.answers}
        columns = ', '.join(values.keys())
        placeholders = ', '.join('?' for _ in values)
        sql = f"INSERT INTO Questionnaire ({columns}) VALUES ({placeholders})"
        c.execute(sql, tuple(values.values()))
        conn.commit()

        apnea = self.answers.get("Q7")
        therapy = self.answers.get("Q8")
        note = self.answers.get("Q11")

        notify_medico = any([
            note and note.strip(),
            apnea and apnea.isdigit() and int(apnea) > 1,
            therapy == "No"
        ])

        if notify_medico:
            # Create notification for doctor
            message = "New questionnaire response requires attention"
            c.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message)
                VALUES (?, ?, 'QUESTIONNAIRE', ?)
            """, (self.patient_id, self.patient_name, message))
            conn.commit()
            self.update_notification_count()

        if self.answers.get("Q5") == "Yes":
            self.schedule_daily_reminder()

        conn.close()
        self.questionnaire_done = True
        self.load_answers_from_db()
        self.show_home()

    def update_notification_count(self):
        """Update the notification count and button text"""
        self.notification_count = self.get_notification_count()
        # Update the notification button text
        for btn in self.sidebar_buttons:
            if "Notifications" in btn.cget("text"):
                btn.configure(text=f"Notifications ({self.notification_count})")
                break

    def load_answers_from_db(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Questionnaire WHERE PatientID = ? ORDER BY Date DESC LIMIT 1", (self.patient_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            self.answers = dict(zip(columns, row))
        conn.close()

    def check_if_questionnaire_done(self):
        today = date.today().isoformat()
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM Questionnaire 
            WHERE PatientID = ? AND Date = ?
            ORDER BY Date DESC 
            LIMIT 1
        """, (self.patient_id, today))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def open_visits(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Center the main frame content
        # Main container with light blue-green background
        #container = ctk.CTkFrame(self.main_frame, fg_color="#E8F5F2")  # Light blue-green background
        #container.pack(fill="both", expand=True, padx=20, pady=20)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(self.main_frame, text="Visits", font=("Arial", 24, "bold"), text_color="#046A38")
        title.grid(row=0, column=0, columnspan=2, pady=40)

        # Create a frame for buttons to center them
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, columnspan=2, pady=20)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        book_button = ctk.CTkButton(button_frame, text="Book a visit", width=150, fg_color="#046A38", command=self.book_visit)
        book_button.grid(row=0, column=0, padx=20)

        check_button = ctk.CTkButton(button_frame, text="Check appointments", width=150, fg_color="#046A38", command=self.check_appointment)
        check_button.grid(row=0, column=1, padx=20)

    def book_visit(self):
        self.render_booking_interface()

    def render_booking_interface(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Create main container frame
        container_frame = ctk.CTkFrame(self.main_frame, fg_color="#E8F5F2")
        container_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(container_frame, fg_color="#E8F5F2")
        scroll_frame.pack(fill="both", expand=True)

        # Close button row (above title/nav row)
        close_frame = ctk.CTkFrame(scroll_frame, fg_color="#E8F5F2")
        close_frame.pack(fill="x")

        close_button = ctk.CTkButton(close_frame, text="✕", width=30, fg_color="red", command=self.open_visits)
        close_button.pack(side="right", padx=10, pady=(5, 15))

        # Title + navigation frame
        title_nav_frame = ctk.CTkFrame(scroll_frame, fg_color="#E8F5F2")
        title_nav_frame.pack(fill="x", pady=(0, 20))

        title_nav_frame.grid_columnconfigure(0, weight=1)
        title_nav_frame.grid_columnconfigure(1, weight=2)
        title_nav_frame.grid_columnconfigure(2, weight=1)

        left_arrow = ctk.CTkButton(title_nav_frame, text="←", width=30, command=self.go_left_week)
        left_arrow.grid(row=0, column=0, padx=10, sticky="w")

        title = ctk.CTkLabel(title_nav_frame, text="Book your Visit", font=("Arial", 20, "bold"), text_color="#046A38")
        title.grid(row=0, column=1, sticky="n")

        right_arrow = ctk.CTkButton(title_nav_frame, text="→", width=30, command=self.go_right_week)
        right_arrow.grid(row=0, column=2, padx=10, sticky="e")

        # Create a frame for the calendar grid
        calendar_frame = ctk.CTkFrame(scroll_frame, fg_color="#E8F5F2")
        calendar_frame.pack(fill="both", expand=True, padx=20)

        self.slot_buttons.clear()

        # Show only weekdays (Monday to Friday)
        days = []
        current_date = self.current_start_date
        while len(days) < 5:  # We want 5 weekdays
            if current_date.weekday() < 5:  # 0-4 are Monday to Friday
                days.append(current_date)
            current_date += datetime.timedelta(days=1)

        slots = self.get_available_slots(days[0], days[-1])

        # Configure grid weights for equal column widths
        for i in range(5):
            calendar_frame.grid_columnconfigure(i, weight=1)

        # Headers
        for i, date in enumerate(days):
            day_label = ctk.CTkLabel(
                calendar_frame,
                text=date.strftime("%A\n%d %b"),
                font=("Arial", 12, "bold"),
                text_color="#046A38"
            )
            day_label.grid(row=0, column=i, pady=(10, 20), padx=10)

        # Time slots
        max_slots = max(len(slots.get(date.isoformat(), [])) for date in days)
        for row in range(max_slots):
            for col, date in enumerate(days):
                day_slots = slots.get(date.isoformat(), [])
                if row < len(day_slots):
                    time = day_slots[row]
                    # Split time and doctor name
                    time_str, _, doctor_name = time.partition(" - Dr. ")
                    
                    # Create a frame for the time slot button
                    slot_frame = ctk.CTkFrame(calendar_frame, fg_color="#E8F5F2")
                    slot_frame.grid(row=row + 1, column=col, pady=5, padx=10)
                    
                    # Time button
                    time_btn = ctk.CTkButton(
                        slot_frame,
                        text=time_str,
                        width=120,
                        height=35,
                        fg_color="white",
                        text_color="black",
                        #hover_color="#e0e0e0",
                        command=lambda d=date, t=time: self.select_slot(d, t)
                    )
                    time_btn.pack(pady=(0, 2))
                    
                    # Doctor name label
                    doctor_label = ctk.CTkLabel(
                        slot_frame,
                        text=f"Dr. {doctor_name}",
                        font=("Arial", 10),
                        text_color="black"
                    )
                    doctor_label.pack()
                    
                    self.slot_buttons[(date, time)] = time_btn

        # Confirm button at the bottom
        confirm_frame = ctk.CTkFrame(scroll_frame, fg_color="#E8F5F2")
        confirm_frame.pack(fill="x", pady=20)

        confirm_btn = ctk.CTkButton(
            confirm_frame,
            text="Confirm",
            width=120,
            fg_color="#046A38",
            text_color="white",
            command=self.confirm_booking
        )
        confirm_btn.pack(side="right", padx=20)

    def go_left_week(self):
        self.current_start_date -= datetime.timedelta(days=7)
        self.render_booking_interface()

    def go_right_week(self):
        self.current_start_date += datetime.timedelta(days=7)
        self.render_booking_interface()

    def get_available_slots(self, start_date, end_date):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        slots = {}

        cursor.execute("""
            SELECT date, time, doctor_name
            FROM Appointments
            WHERE status = 'available'
                AND doctor_id = 'DOC001'
              AND date BETWEEN ? AND ?
            ORDER BY date, time
        """, (start_date.isoformat(), end_date.isoformat()))

        for date, time, doctor in cursor.fetchall():
            slots.setdefault(date, []).append(f"{time} - Dr. {doctor}")

        conn.close()
        return slots

    def select_slot(self, date, time_label):
        # Reset all buttons to default style
        for btn in self.slot_buttons.values():
            btn.configure(
                fg_color="white",
                text_color="black"
            )

        self.selected_date = date
        self.selected_time = time_label
        selected_btn = self.slot_buttons.get((date, time_label))
        if selected_btn:
            selected_btn.configure(
                fg_color="#3498db",
                text_color="white"
            )

    def confirm_booking(self):
        if not self.selected_date or not self.selected_time:
            error_label = ctk.CTkLabel(self.main_frame, text="Please select a time slot first", text_color="red")
            error_label.grid(row=21, column=0, columnspan=7, pady=5)
            return

        # Split doctor from time
        time, _, doctor_name = self.selected_time.partition(" - Dr. ")

        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Appointments
            SET patient_id = ?, patient_name = ?, status = 'booked'
            WHERE date = ? AND time = ? AND doctor_name = ? AND status = 'available'
        """, (self.patient_id, self.patient_name, self.selected_date.isoformat(), time, doctor_name))

        conn.commit()
        conn.close()

        # Clear the main frame and show confirmation
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        confirmation_text = f"You confirmed your appointment with Dr. {doctor_name} on {self.selected_date.strftime('%A, %d %B')} at {time}"
        confirmation_label = ctk.CTkLabel(self.main_frame, text=confirmation_text, font=("Arial", 16),fg_color="#046A38")
        confirmation_label.pack(pady=50)

        back_button = ctk.CTkButton(self.main_frame, text="Back to Visits", command=self.open_visits)
        back_button.pack(pady=20)

    def check_appointment(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.main_frame,
            text="Your Appointments",
            font=("Arial", 20, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=10)

        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.main_frame, fg_color="#E8F5F2")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Configure column weights once
        weights = [3, 1, 2, 1]
        for i, w in enumerate(weights):
            table_frame.grid_columnconfigure(i, weight=w)

        # Create headers
        headers = ["Date", "Time", "Doctor", "Actions"]
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

        # Get appointments from database
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT date, time, doctor_name
                FROM Appointments
                WHERE patient_id = ? AND status = 'booked'
                ORDER BY date ASC, time ASC
            """, (self.patient_id,))
            
            appointments = cursor.fetchall()
            
            if not appointments:
                no_appointments = ctk.CTkLabel(
                    table_frame,
                    text="No appointments found",
                    font=("Arial", 14)
                )
                no_appointments.grid(row=1, column=0, columnspan=4, pady=20)
            else:
                # Display appointments
                for i, (date, time, doctor) in enumerate(appointments, start=1):
                    appt_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
                    today = datetime.date.today()

                    if appt_date < today:
                        continue

                    if appt_date - today == datetime.timedelta(days=1):
                        self.create_notification(date, time, doctor)

                    formatted_date = appt_date.strftime("%A, %d %B %Y")

                    # Alternate background color
                    bg_color = "#F2F2F2" if i % 2 == 0 else "white"

                    # Date
                    date_label = ctk.CTkLabel(
                        table_frame,
                        text=formatted_date,
                        font=("Arial", 12),
                        text_color="#046A38",
                        fg_color=bg_color,
                        anchor="center",
                        height=40  # Fixed height for rows
                    )
                    date_label.grid(row=i, column=0, padx=2, pady=2, sticky="nsew")

                    # Time
                    time_label = ctk.CTkLabel(
                        table_frame,
                        text=time,
                        font=("Arial", 12),
                        text_color="#046A38",
                        fg_color=bg_color,
                        anchor="center",
                        height=40  # Fixed height for rows
                    )
                    time_label.grid(row=i, column=1, padx=2, pady=2, sticky="nsew")

                    # Doctor
                    doctor_label = ctk.CTkLabel(
                        table_frame,
                        text=f"Dr. {doctor}",
                        font=("Arial", 12),
                        text_color="#046A38",
                        fg_color=bg_color,
                        anchor="center",
                        height=40  # Fixed height for rows
                    )
                    doctor_label.grid(row=i, column=2, padx=2, pady=2, sticky="nsew")

                    # Delete button
                    delete_btn = ctk.CTkButton(
                        table_frame,
                        text="Delete",
                        width=40,
                        height=40,  # Fixed height for buttons
                        fg_color="#FF6B6B",
                        text_color="white",
                        command=lambda d=date, t=time, doc=doctor: self.delete_appointment(d, t, doc)
                    )
                    delete_btn.grid(row=i, column=3, padx=2, pady=2, sticky="nsew")

        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(table_frame, text=f"Error loading appointments: {str(e)}", text_color="red")
            error_label.grid(row=1, column=0, columnspan=4, pady=20)
        finally:
            conn.close()

        # Add back button
        back_button = ctk.CTkButton(self.main_frame, text="Back to Visits", command=self.open_visits)
        back_button.pack(pady=20)

    def delete_appointment(self, date, time, doctor):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            # Update appointment status back to available
            cursor.execute("""
                UPDATE Appointments
                SET patient_id = NULL, patient_name = NULL, status = 'available'
                WHERE date = ? AND time = ? AND doctor_name = ? AND patient_id = ?
            """, (date, time, doctor, self.patient_id))
            
            conn.commit()
            
            # Create notification for cancellation
            message = f"Your appointment with Dr. {doctor} on {date} at {time} has been cancelled"
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message)
                VALUES (?, ?, 'CANCELLATION', ?)
            """, (self.patient_id, self.patient_name, message))
            
            conn.commit()
            self.update_notification_count()
            
            # Refresh the appointments view
            self.check_appointment()
            
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(self.main_frame, text=f"Error cancelling appointment: {str(e)}", text_color="red")
            error_label.pack(pady=20)
        finally:
            conn.close()

    def create_notification(self, date, time, doctor):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        # Check if notification already exists
        cursor.execute("""
            SELECT 1 FROM Notifications 
            WHERE PatientID = ? AND Type = 'REMINDER' 
            AND Message LIKE ?
        """, (self.patient_id, f"%{date}%"))
        
        if not cursor.fetchone():
            message = f"Reminder: You have an appointment tomorrow ({date}) at {time} with Dr. {doctor}"
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message)
                VALUES (?, ?, 'REMINDER', ?)
            """, (self.patient_id, self.patient_name, message))
            
            conn.commit()
        
        conn.close()

    def open_medication(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self.main_frame, text="Medication Management", font=("Arial", 20, "bold"), text_color="#046A38")
        title.pack(pady=20)

        # Create buttons frame
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)

        # Modify Drugs button
        modify_drugs_button = ctk.CTkButton(
            buttons_frame,
            text="Modify Saved Drugs",
            fg_color="#046A38",
            width=200,
            command=self.show_drugs_table
        )
        modify_drugs_button.pack(side="left", padx=20)

        # View Therapy button
        view_therapy_button = ctk.CTkButton(
            buttons_frame,
            text="View Therapy",
            fg_color="#046A38",
            width=200,
            command=self.show_therapy
        )
        view_therapy_button.pack(side="left", padx=20)


    def show_drugs_table(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.main_frame,
            text="Your Medications",
            font=("Arial", 20, "bold"),
            text_color="#046A38"
        )
        title.pack(pady=10)

        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.main_frame, fg_color="#E8F5F2")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Configure grid weights for equal column widths
        for i in range(4):
            table_frame.grid_columnconfigure(i, weight=1)

        # Headers with light blue-green background
        headers = ["Drug Information", "Start Date", "End Date", "Actions"]
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

        # Get drugs from database
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT ID, Note, StartDate, EndDate
                FROM Drugs
                WHERE PatientID = ?
                ORDER BY StartDate DESC
            """, (self.patient_id,))
            
            drugs = cursor.fetchall()
            
            if not drugs:
                no_drugs_label = ctk.CTkLabel(table_frame, text="No medications found", font=("Arial", 14), text_color="#046A38")
                no_drugs_label.grid(row=1, column=0, columnspan=4, pady=20)
            else:
                for i, (drug_id, note, start_date, end_date) in enumerate(drugs, start=1):
                    bg_color = "#F2F2F2" if i % 2 == 0 else "white"
                    
                    # Drug info
                    note_label = ctk.CTkLabel(
                        table_frame,
                        text=note,
                        font=("Arial", 12),
                        text_color="#046A38",
                        fg_color=bg_color,
                        anchor="center",
                        height=40
                    )
                    note_label.grid(row=i, column=0, padx=2, pady=2, sticky="nsew")

                    # Data inizio
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

                    # Data fine
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

                    # Pulsanti Azioni (Edit / Delete)
                    actions_frame = ctk.CTkFrame(table_frame, fg_color=bg_color)
                    actions_frame.grid(row=i, column=3, padx=2, pady=2, sticky="nsew")

                    actions_frame.grid_columnconfigure((0, 1), weight=1) 

                    edit_btn = ctk.CTkButton(
                        actions_frame,
                        text="Edit",
                        width=60,
                        height=30,
                        fg_color="#73C8AE",
                        text_color="white",
                        command=lambda d=drug_id, n=note, s=start_date, e=end_date: self.edit_drug(d, n, s, e)
                    )
                    edit_btn.grid(row=0, column=0, padx=5, pady=5)

                    delete_btn = ctk.CTkButton(
                        actions_frame,
                        text="Delete",
                        width=60,
                        height=30,
                        fg_color="#FF6B6B",
                        text_color="white",
                        command=lambda d=drug_id: self.delete_drug(d)
                    )
                    delete_btn.grid(row=0, column=1, padx=5, pady=5)
                
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(table_frame, text=f"Error loading medications: {str(e)}", text_color="red")
            error_label.grid(row=1, column=0, columnspan=4, pady=20)
        finally:
            conn.close()

        # Add new drug button
        add_button = ctk.CTkButton(
            self.main_frame,
            text="Add New Medication",
            width=200,
            fg_color="#046A38",
            text_color="white",
            command=lambda: self.edit_drug(None, "", "", "")
        )
        add_button.pack(pady=20)

        # Back button
        back_button = ctk.CTkButton(self.main_frame, text="Back to Medication", command=self.open_medication)
        back_button.pack(pady=20)

    def edit_drug(self, drug_id, note, start_date, end_date):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.main_frame,
            text="Edit Medication" if drug_id else "Add New Medication",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=20)

        # Create form frame
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#E8F5F2")
        form_frame.pack(padx=40, pady=20, fill="both", expand=True)

        # Note label and text box
        note_label = ctk.CTkLabel(form_frame, text="Drug Information:", font=("Arial", 14), text_color="#046A38")
        note_label.pack(pady=(20, 5))
        
        self.note_text = ctk.CTkTextbox(form_frame, width=400, height=100, fg_color="white")
        self.note_text.pack(pady=10)
        if note:
            self.note_text.insert("1.0", note)

        # Date frame
        date_frame = ctk.CTkFrame(form_frame, fg_color="#E8F5F2")
        date_frame.pack(pady=20)

        # Start date
        start_label = ctk.CTkLabel(date_frame, text="Start Date:", font=("Arial", 14), text_color="#046A38")
        start_label.grid(row=0, column=0, padx=20, pady=10)
        
        self.start_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD", fg_color="white")
        self.start_date.grid(row=0, column=1, padx=20, pady=10)
        if start_date:
            self.start_date.insert(0, start_date)

        # End date
        end_label = ctk.CTkLabel(date_frame, text="End Date:", font=("Arial", 14), text_color="#046A38")
        end_label.grid(row=1, column=0, padx=20, pady=10)
        
        self.end_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD", fg_color="white")
        self.end_date.grid(row=1, column=1, padx=20, pady=10)
        if end_date:
            self.end_date.insert(0, end_date)

        # Error label
        self.error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        self.error_label.pack(pady=10)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)

        # Back button (now first)
        back_button = ctk.CTkButton(
            buttons_frame,
            text="Back",
            width=120,
            command=self.show_drugs_table
        )
        back_button.pack(side="left", padx=10)

        # Save button (now second)
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save",
            width=120,
            command=lambda: self.save_drug(drug_id)
        )
        save_button.pack(side="left", padx=10)

    def save_drug(self, drug_id):
        note = self.note_text.get("1.0", "end-1c").strip()
        start_date = self.start_date.get().strip()
        end_date = self.end_date.get().strip()

        if not note or not start_date or not end_date:
            self.error_label.configure(text="Please fill in all fields")
            return

        try:
            # Validate dates
            start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            
            if end < start:
                self.error_label.configure(text="End date cannot be before start date")
                return
                
        except ValueError:
            self.error_label.configure(text="Invalid date format. Use YYYY-MM-DD")
            return

        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            if drug_id:  # Update existing drug
                cursor.execute("""
                    UPDATE Drugs
                    SET Note = ?, StartDate = ?, EndDate = ?
                    WHERE ID = ? AND PatientID = ?
                """, (note, start_date, end_date, drug_id, self.patient_id))
            else:  # Insert new drug
                cursor.execute("""
                    INSERT INTO Drugs (PatientID, Note, StartDate, EndDate)
                    VALUES (?, ?, ?, ?)
                """, (self.patient_id, note, start_date, end_date))
            
            conn.commit()
            
            # Create notification for the change
            action = "updated" if drug_id else "added"
            message = f"Your medication has been {action}. Please check your medication list."
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message)
                VALUES (?, ?, 'MEDICATION', ?)
            """, (self.patient_id, self.patient_name, message))
            conn.commit()
            self.update_notification_count()
            
            self.show_drugs_table()  # Return to table view
            
        except sqlite3.Error as e:
            self.error_label.configure(text=f"Error saving data: {str(e)}")
        finally:
            conn.close()

    def delete_drug(self, drug_id):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            # Get drug info before deleting
            cursor.execute("SELECT Note FROM Drugs WHERE ID = ? AND PatientID = ?", (drug_id, self.patient_id))
            drug_info = cursor.fetchone()
            
            if drug_info:
                # Delete the drug
                cursor.execute("""
                    DELETE FROM Drugs
                    WHERE ID = ? AND PatientID = ?
                """, (drug_id, self.patient_id))
                
                conn.commit()
                
                # Create notification for deletion
                message = f"Your medication '{drug_info[0]}' has been removed from your list."
                cursor.execute("""
                    INSERT INTO Notifications (PatientID, PatientName, Type, Message)
                    VALUES (?, ?, 'MEDICATION', ?)
                """, (self.patient_id, self.patient_name, message))
                conn.commit()
                self.update_notification_count()
                
                self.show_drugs_table()  # Refresh the table
            else:
                raise sqlite3.Error("Medication not found")
            
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(self.main_frame, text=f"Error deleting medication: {str(e)}", text_color="red")
            error_label.pack(pady=20)
        finally:
            conn.close()

    def show_therapy(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self.main_frame, text="Your Therapy", font=("Arial", 20, "bold"), text_color="#046A38")
        title.pack(pady=20)

        # Create therapy display frame
        therapy_frame = ctk.CTkFrame(self.main_frame, fg_color="#E8F5F2")
        therapy_frame.pack(padx=40, pady=20, fill="both", expand=True)

        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT Note
                FROM Therapy
                WHERE PatientID = ?
                ORDER BY ID DESC
                LIMIT 1
            """, (self.patient_id,))
            
            result = cursor.fetchone()
            
            if result:
                therapy_text = result[0]
                therapy_label = ctk.CTkLabel(
                    therapy_frame,
                    text=therapy_text,
                    font=("Arial", 14),
                    wraplength=600,
                    justify="left",
                    text_color="#046A38"
                )
                therapy_label.pack(padx=20, pady=20)
            else:
                no_therapy_label = ctk.CTkLabel(
                    therapy_frame,
                    text="No therapy information available",
                    font=("Arial", 14),
                    text_color="#046A38"
                )
                no_therapy_label.pack(pady=20)
                
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                therapy_frame,
                text=f"Error loading therapy: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)
        finally:
            conn.close()

        # Back button
        back_button = ctk.CTkButton(self.main_frame, text="Back to Medication", command=self.open_medication)
        back_button.pack(pady=20)

    def get_notification_count(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM Notifications 
            WHERE PatientID = ? AND IsRead = 0
        """, (self.patient_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def show_notifications(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Main container with light blue-green background
        container = ctk.CTkFrame(self.main_frame, fg_color="#E8F5F2")
        container.pack(fill="both", expand=True, padx=20, pady=20)


        # Create frames for unread and read notifications
        unread_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10)
        unread_frame.pack(padx=40, pady=(5, 5), fill="x")  # meno spazio sotto

        unread_title = ctk.CTkLabel(
            unread_frame,
            text="New Notifications",
            font=("Arial", 16, "bold"),
            text_color="#046A38"
        )
        unread_title.pack(pady=5)

        unread_scroll = ctk.CTkScrollableFrame(unread_frame, fg_color="white")
        unread_scroll.pack(padx=10, pady=5, fill="x")

        read_frame = ctk.CTkFrame(container, fg_color="white", corner_radius=10)
        read_frame.pack(padx=40, pady=(0, 20), fill="both", expand=True)

        read_title = ctk.CTkLabel(
            read_frame,
            text="Previous Notifications",
            font=("Arial", 16, "bold"),
            text_color="#046A38"
        )
        read_title.pack(pady=10)

        read_scroll = ctk.CTkScrollableFrame(read_frame, fg_color="white", height=80)
        read_scroll.pack(padx=10, pady=5, fill="x")

        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            # Get unread notifications
            cursor.execute("""
                SELECT Message, Timestamp, Type
                FROM Notifications
                WHERE PatientID = ? AND IsRead = 0
                ORDER BY Timestamp DESC
            """, (self.patient_id,))
            
            unread_notifications = cursor.fetchall()
            
            if not unread_notifications:
                no_unread = ctk.CTkLabel(
                    unread_scroll, 
                    text="No new notifications", 
                    font=("Arial", 14),
                    text_color="#046A38"
                )
                no_unread.pack(pady=20)
            else:
                for message, timestamp, type in unread_notifications:
                    notification_frame = ctk.CTkFrame(
                        unread_scroll,
                        fg_color="#E8F5F2",
                        corner_radius=10
                    )
                    notification_frame.pack(fill="x", padx=10, pady=5)
                    
                    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    formatted_time = timestamp.strftime("%d %B %Y, %H:%M")
                    
                    type_icon = "🔔" if type == "REMINDER" else "📋"
                    content = f"{type_icon} {message}\n{formatted_time}"
                    
                    notification_label = ctk.CTkLabel(
                        notification_frame,
                        text=content,
                        font=("Arial", 12),
                        justify="left",
                        wraplength=600,
                        text_color="#046A38"
                    )
                    notification_label.pack(padx=10, pady=5, anchor="w")

            # Get read notifications
            cursor.execute("""
                SELECT Message, Timestamp, Type
                FROM Notifications
                WHERE PatientID = ? AND IsRead = 1
                ORDER BY Timestamp DESC
            """, (self.patient_id,))
            
            read_notifications = cursor.fetchall()
            
            if not read_notifications:
                no_read = ctk.CTkLabel(
                    read_scroll, 
                    text="No previous notifications", 
                    font=("Arial", 14),
                    text_color="#046A38"
                )
                no_read.pack(pady=20)
            else:
                for message, timestamp, type in read_notifications:
                    notification_frame = ctk.CTkFrame(
                        read_scroll,
                        fg_color="#F5F5F5",
                        corner_radius=10
                    )
                    notification_frame.pack(fill="x", padx=10, pady=5)
                    
                    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    formatted_time = timestamp.strftime("%d %B %Y, %H:%M")
                    
                    type_icon = "🔔" if type == "REMINDER" else "📋"
                    content = f"{type_icon} {message}\n{formatted_time}"
                    
                    notification_label = ctk.CTkLabel(
                        notification_frame,
                        text=content,
                        font=("Arial", 14),
                        justify="left",
                        wraplength=600,
                        text_color="#046A38"
                    )
                    notification_label.pack(padx=10, pady=5, anchor="w")
            
            # Mark notifications as read
            cursor.execute("""
                UPDATE Notifications
                SET IsRead = 1
                WHERE PatientID = ? AND IsRead = 0
            """, (self.patient_id,))
            conn.commit()
            
            # Update notification count
            self.update_notification_count()
            
        except sqlite3.Error as e:
            error_label = ctk.CTkLabel(
                container, 
                text=f"Error loading notifications: {str(e)}", 
                text_color="red"
            )
            error_label.pack(pady=20)
        finally:
            conn.close()

    def get_patient_name(self, patient_id):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Name, Surname FROM Patients WHERE PatientID = ?", (patient_id,))
        result = cursor.fetchone()
        conn.close()
        return f"{result[0]} {result[1]}" if result else "Unknown Patient"

    def notify_doctor(self):
        print(f"[NOTIFICA AL MEDICO] Il paziente {self.patient_name} ha inserito dati critici.")

    def schedule_daily_reminder(self):
        conn = sqlite3.connect("Database_proj.db")
        cursor = conn.cursor()
        
        try:
            # Create a notification for the daily reminder
            message = "Ricorda di accendere il dispositivo per la notte."
            cursor.execute("""
                INSERT INTO Notifications (PatientID, PatientName, Type, Message, Timestamp)
                VALUES (?, ?, 'REMINDER', ?, datetime('now', '21:00:00'))
            """, (self.patient_id, self.patient_name, message))
            
            conn.commit()
            self.update_notification_count()
            
        except sqlite3.Error as e:
            print(f"Error scheduling reminder: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    app = PatientMainView(patient_id="PAT001")
    app.mainloop() 