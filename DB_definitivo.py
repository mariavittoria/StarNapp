import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("Database_proj.db")
cursor = conn.cursor()
#cursor.execute("DROP TABLE IF EXISTS Patients_Ok;")
# ========== CREAZIONE TABELLE ==========

cursor.execute("""
CREATE TABLE IF NOT EXISTS Patients (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Surname TEXT NOT NULL,
    dateOfBirth DATE,
    height REAL CHECK(height > 0),
    weight REAL CHECK(weight > 0),
    age INT,
    Gender CHAR(1) CHECK(Gender IN ('M', 'F', 'O')),
    Nationality TEXT DEFAULT 'Italian',
    ClinicalHistory TEXT,
    PatientID TEXT NOT NULL UNIQUE,
    PatientPassword TEXT,
    PhoneNumber TEXT UNIQUE,
    DoctorID TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Questionnaire (
    QuestID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Date DATE,
    Q1 INTEGER, 
    Q2 INTEGER, 
    Nota2 TEXT, 
    Q3 INTEGER, 
    Q4 INTEGER, 
    Q5 INTEGER, 
    Q6 INTEGER, 
    Q7 INTEGER,
    Q8 INTEGER, 
    Q9 TEXT, 
    Q10 INTEGER, 
    Q11 TEXT, 
    Q12 INTEGER, 
    Q13 TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Doctors (
    Name TEXT NOT NULL,
    Surname TEXT NOT NULL,
    dateOfBirth DATE,
    doctorID TEXT PRIMARY KEY,
    hospital TEXT,
    DoctorPassword TEXT,
    PhoneNumber TEXT UNIQUE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    doctor_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'available',
    patient_id TEXT,
    patient_name TEXT,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(doctorID),
    FOREIGN KEY (patient_id) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Notifications (
    NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT,
    PatientName TEXT,
    Type TEXT,
    Message TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    IsRead BOOLEAN DEFAULT 0,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Drugs (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Note TEXT,
    StartDate DATE,
    EndDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Therapy (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Note TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Indexes (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Date DATE,
    ValueAHI REAL,
    ValueODI REAL,
    MeanSpO2 REAL,
    MinSpO2 REAL,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS OSA_Patients (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Name TEXT NOT NULL,
    Surname TEXT NOT NULL,
    Date DATE,
    AHI INTEGER,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Possible_Follow_Up_Patients (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Name TEXT NOT NULL,
    Surname TEXT NOT NULL,
    Date DATE,
    Days_since_last_OSA INTEGER,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Follow_Up_Patients (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Name TEXT NOT NULL,
    Surname TEXT NOT NULL,
    Date DATE,
    SpO2_min INTEGER,
    ODI INTEGER,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Seven_days_patients_ok (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Name TEXT NOT NULL,
    Surname TEXT NOT NULL,
    Date DATE,
    Days_since_last_OSA INTEGER,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS SupportMessages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    user_type TEXT,
    message TEXT,
    date TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS LastNotificationTime (
    PatientID TEXT PRIMARY KEY,
    LastNotification DATETIME,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);
""")

# ========== INSERIMENTO DATI ==========

# Doctors
cursor.executemany("""
INSERT OR IGNORE INTO Doctors (Name, Surname, doctorID, DoctorPassword, dateOfBirth, hospital, PhoneNumber)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    ("Mario", "Rossi", "DOC001", "password123", "1980-01-01", "Ospedale San Giovanni", "1234567890"),
    ("Anna", "Vincentelli", "DOC002", "password345", "1970-01-01", "Ospedale Galeazzi", "1234567777"),
    ("Lorenzo", "Esposito", "DOC003", "pass789", "1985-06-15", "Ospedale Niguarda", "1234561111")
])

# Patients
cursor.executemany("""
INSERT OR IGNORE INTO Patients (Name, Surname, dateOfBirth, height, weight, Age, Gender, Nationality, ClinicalHistory, PatientID, PatientPassword, PhoneNumber, DoctorID)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ('Luca', 'Verdi', '1960-05-15', 1.75, 70, None, 'M', 'Italian', 'Ischemia', 'PAT001', 'password123', '1234567890', 'DOC001'),
    ('Lucia', 'Garofalo', '1956-06-15', 1.65, 60, None, 'F', 'Italian', 'None', 'PAT002', '345678', '1234567899', 'DOC001'),
    ('Marco', 'Verdi', '1952-03-22', 1.80, 85, None, 'M', 'Italian', 'Asthma', 'PAT003', 'pass333', '1234562222', 'DOC001'),
    ('Chiara', 'Neri', '1938-01-12', 1.68, 62, None, 'F', 'Italian', 'Stroke', 'PAT004', 'chiara90', '1234562233', 'DOC001'),
    ('Giorgio', 'Fontana', '1944-07-08', 1.82, 88, None, 'M', 'Italian', 'Hypertension', 'PAT005', 'giorgio85', '1234562244', 'DOC001'),
    ('Federica', 'Russo', '1947-10-22', 1.60, 55, None, 'F', 'Italian', 'None', 'PAT006', 'fede97', '1234562255', 'DOC001'),
    ('Valerio', 'Bassi', '1962-11-15', 1.75, 78, None, 'M', 'Italian', 'Diabete', 'PAT007', 'valbass80', '1234562266', 'DOC001'),
    ('Irene', 'Ferri', '1953-02-25', 1.70, 60, None, 'F', 'Italian', 'None', 'PAT008', 'irenef95', '1234562277', 'DOC001'),
    ('Marco', 'Esposito', '1956-06-16', 1.87, 90, None, 'M', 'Italian', 'Hypertension', 'PAT009', 'pass333', '1234562226', 'DOC001'),
    ('Angelo', 'Galli', '1986-04-26', 1.70, 80, None, 'M', 'Italian', 'Stroke', 'PAT010', 'pass333', '1234562228', 'DOC001'),
    ('Giulia', 'Conti', '1963-08-10', 1.68, 58, None, 'F', 'Italian', 'None', 'PAT011', 'giuly01', '1234562299', 'DOC001'),
    ('Davide', 'Rizzi', '1957-03-18', 1.78, 75, None, 'M', 'Italian', 'Seasonal Allergies', 'PAT012', 'davidr', '1234562300', 'DOC001'),
    ('Marta', 'De Luca', '1946-09-29', 1.66, 65, None, 'F', 'Italian', 'None', 'PAT013', 'marta89', '1234562301', 'DOC001'),
    ('Stefano', 'Barbieri', '1943-05-03', 1.85, 95, None, 'M', 'Italian', 'High blood pressure', 'PAT014', 'stefano75', '1234562302', 'DOC001'),
    ('Elena', 'Romano', '1947-12-01', 1.64, 59, None, 'F', 'Italian', 'None', 'PAT015', 'elena98', '1234562303', 'DOC001')
])

# Popola Appointments da 16 Maggio a 30 Giugno 2025
slot_times = ["08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30"]
doctors = [("DOC001", "Mario Rossi")]
appointments = []
start_date = datetime(2025, 5, 16).date()
end_date = datetime(2025, 6, 30).date()
current_date = start_date

while current_date <= end_date:
    if current_date.weekday() < 5:
        for doctor_id, doctor_name in doctors:
            for slot in slot_times:
                appointments.append((current_date.isoformat(), slot, doctor_id, doctor_name, 'available', None, None))
    current_date += timedelta(days=1)

# Slot prenotati
booked_slots = [
    ("2025-06-12", "09:30", "DOC001", "Mario Rossi", "booked", "PAT001", "Luca Bianchi"),
    ("2025-06-09", "14:30", "DOC001", "Mario Rossi", "booked", "PAT002", "Lucia Garofalo"),
    ("2025-05-27", "08:30", "DOC001", "Mario Rossi", "booked", "PAT003", "Marco Verdi"),
    ("2025-06-04", "13:30", "DOC001", "Mario Rossi", "booked", "PAT004", "Chiara Neri"),
    ("2025-05-30", "11:30", "DOC001", "Mario Rossi", "booked", "PAT005", "Giorgio Fontana"),
    ("2025-06-10", "10:30", "DOC001", "Mario Rossi", "booked", "PAT006", "Federica Russo"),
    ("2025-05-29", "15:30", "DOC001", "Mario Rossi", "booked", "PAT007", "Valerio Bassi"),
    ("2025-06-03", "16:30", "DOC001", "Mario Rossi", "booked", "PAT008", "Irene Ferri"),
    ("2025-05-22", "12:30", "DOC001", "Mario Rossi", "booked", "PAT009", "Marco Esposito"),
    ("2025-06-05", "08:30", "DOC001", "Mario Rossi", "booked", "PAT010", "Angelo Galli"),
    ("2025-06-06", "09:30", "DOC001", "Mario Rossi", "booked", "PAT011", "Giulia Conti"),
    ("2025-05-30", "10:30", "DOC001", "Mario Rossi", "booked", "PAT012", "Davide Rizzi"),
    ("2025-06-03", "11:30", "DOC001", "Mario Rossi", "booked", "PAT013", "Marta De Luca"),
    ("2025-06-03", "14:30", "DOC001", "Mario Rossi", "booked", "PAT014", "Stefano Barbieri"),
    ("2025-06-06", "15:30", "DOC001", "Mario Rossi", "booked", "PAT015", "Elena Romano"),
    ("2025-06-09", "09:30", "DOC001", "Mario Rossi", "booked", "PAT001", "Luca Bianchi"),
    ("2025-05-28", "14:30", "DOC001", "Mario Rossi", "booked", "PAT002", "Lucia Garofalo"),
    ("2025-05-30", "09:30", "DOC001", "Mario Rossi", "booked", "PAT003", "Marco Verdi"),
    ("2025-06-04", "11:30", "DOC001", "Mario Rossi", "booked", "PAT004", "Chiara Neri"),
    ("2025-05-30", "16:30", "DOC001", "Mario Rossi", "booked", "PAT005", "Giorgio Fontana"),
    ("2025-06-11", "09:30", "DOC001", "Mario Rossi", "booked", "PAT006", "Federica Russo"),
    ("2025-05-29", "14:30", "DOC001", "Mario Rossi", "booked", "PAT007", "Valerio Bassi"),
    ("2025-06-03", "08:30", "DOC001", "Mario Rossi", "booked", "PAT008", "Irene Ferri"),
    ("2025-05-29", "12:30", "DOC001", "Mario Rossi", "booked", "PAT009", "Marco Esposito"),
    ("2025-06-05", "16:30", "DOC001", "Mario Rossi", "booked", "PAT010", "Angelo Galli"),
    ("2025-06-06", "11:30", "DOC001", "Mario Rossi", "booked", "PAT011", "Giulia Conti"),
    ("2025-05-30", "11:30", "DOC001", "Mario Rossi", "booked", "PAT012", "Davide Rizzi"),
    ("2025-06-03", "15:30", "DOC001", "Mario Rossi", "booked", "PAT013", "Marta De Luca"),
    ("2025-06-03", "10:30", "DOC001", "Mario Rossi", "booked", "PAT014", "Stefano Barbieri"),
    ("2025-06-08", "15:30", "DOC001", "Mario Rossi", "booked", "PAT015", "Elena Romano"),

]
for date, time_slot, doc_id, doctor_name, status, pat_id, pat_name in booked_slots:
    appointments.append((date, time_slot, doc_id, doctor_name, status, pat_id, pat_name))


cursor.executemany("""
INSERT OR IGNORE INTO Appointments (date, time, doctor_id, doctor_name, status, patient_id, patient_name)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", appointments)

# Inserimento Drugs
drugs = [
    ("PAT001", "Paracetamolo 500mg 2 volte al giorno", "2025-04-20", "2025-04-27"),
    ("PAT002", "Ibuprofene al bisogno", "2025-04-21", "2025-04-25"),
    ("PAT003", "Salbutamolo spray 2 puff al bisogno", "2025-04-22", "2025-04-30"),
    ("PAT001", "Atorvastatina (Lipitor)", "2025-05-20", "2025-10-30"),
    ("PAT001","Clopidogrel","2025-05-20","2025-10-30")
]
cursor.executemany("""
INSERT OR IGNORE INTO Drugs (PatientID, Note, StartDate, EndDate)
VALUES (?, ?, ?, ?)
""", drugs)

# Inserimento Therapy
therapies = [
    ("PAT001", "Auto-adjusting CPAP (Auto-CPAP) with a range of 6-12 cmH₂O. Physiotherapy is recommended for mobility and light breathing exercises."),
    ("PAT002", "CPAP 9 cmH₂O. Nasal spray (fluticasone) to improve CPAP tolerance (1 spray per nostril in the evening)."),
    ("PAT003", "CPAP 6 cmH₂O. Use of an oral appliance (MAD) fitted by a sleep dentist is recommended."),
    ("PAT010", "CPAP 10 cmH₂O")
]
cursor.executemany("""
INSERT OR IGNORE INTO Therapy (PatientID, Note)
VALUES (?, ?)
""", therapies)

# Inserimento Indexes
indexes = [
    ("PAT001", "2025-05-26", 11, 4.1, 95.2, 88.5),
    ("PAT001", "2025-05-27", 10, 3.5, 96.0, 89.0),
    ("PAT001", "2025-05-28", 7, 4.1, 95.0, 87.0),
    ("PAT001", "2025-05-29", 12, 4.0, 93.5, 89.7),
    ("PAT011", "2025-05-25", 14, 8.7, 92.0, 89.3),
    ("PAT011", "2025-05-27", 8, 1.8, 96.5, 90.0),
    ("PAT011", "2025-05-28", 9, 0.7, 93.5, 90.0),
    ("PAT009", "2025-05-26", 10, 1.5, 92.5, 90.0),
    ("PAT009", "2025-05-23", 11.5, 1.5, 92.5, 90.0),
    ("PAT009", "2025-05-24", 12.5, 1.5, 93.5, 89.0),
    ("PAT009", "2025-05-25", 11.5, 1.5, 94.5, 90.0),
    ("PAT009", "2025-05-26", 10.3, 1.5, 96.5, 90.0),
    ("PAT009", "2025-05-27", 10.01, 1.5, 97.5, 90.0),
    ("PAT009", "2025-05-28", 8.7, 1.5, 96.5, 90.0),
    ("PAT009", "2025-05-29", 9, 1.5, 96.5, 90.0),
    ("PAT010", "2025-05-24", 6.4, 1.5, 96.5, 90.0),
    ("PAT010", "2025-05-25", 7, 1, 97.5, 90.0),
    ("PAT010", "2025-05-26", 3, 1.5, 98.5, 90.0),
    ("PAT010", "2025-05-27", 6, 7, 97.5, 90.0),
    ("PAT010", "2025-05-28", 6.5, 8, 96.5, 90.0),
    ("PAT010", "2025-05-29", 5, 15, 98.5, 90.0)
]
cursor.executemany("""
INSERT OR IGNORE INTO Indexes (PatientID, Date, ValueAHI, ValueODI, MeanSpO2, MinSpO2)
VALUES (?, ?, ?, ?, ?, ?)
""", indexes)

# Inserimento Questionnaire
questionnaires = [
    ("PAT001", "2025-05-25", 2, 1, "CPAP noise kept me awake", 0, 0, 0, 0, 0, 1, "None", 0, "", 1, "72"),
    ("PAT001", "2025-04-26", 0, 1, "", 1, 1, 0, 1, 0, 1, "None", 0, "", 1, "75"),
    ("PAT002", "2025-04-21", 3, 0, "Had trouble falling asleep", 1, 1, 1, 0, 2, 1, "Forgot to take medication", 1, "Can I increase the use of nasal spray?", 0, "")
]
cursor.executemany("""
INSERT OR IGNORE INTO Questionnaire (PatientID, Date, Q1, Q2, Nota2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", questionnaires)

# Inserimento Notifications
notifications = [
    ("PAT001", "Luca Bianchi", "REMINDER", "Remember to turn on your device tonight!", "2025-05-19 08:00:00", 0),
    ("PAT002", "Lucia Garofalo", "DOCTOR_ALERT", "Book a visit with you doctor", "2025-05-20 09:00:00", 0)
]
cursor.executemany("""
INSERT OR IGNORE INTO Notifications (PatientID, PatientName, Type, Message, Timestamp, IsRead)
VALUES (?, ?, ?, ?, ?, ?)
""", notifications)


# OSA_Patients
osa_patients = [
    ("PAT001", "Luca", "Verdi", "2025-04-20", 12),
    ("PAT002", "Anna", "Greco", "2025-02-25", 14),
    ("PAT009", "Marco", "Esposito", "2025-01-10", 9),
    ("PAT010", "Angelo", "Galli", "2024-08-18", 5),
    ("PAT011", "Giulia", "Conti", "2024-10-21", 9)
]
cursor.executemany("""
INSERT OR IGNORE INTO OSA_Patients (PatientID, Name, Surname, Date, AHI)
VALUES (?, ?, ?, ?, ?)
""", osa_patients)

# Possible_Follow_Up_Patients
possible_follow_up = [
    ("PAT004", "Chiara", "Neri", "2025-03-04", 85),
    ("PAT007", "Valerio", "Bassi", "2025-02-27", 90),
    ("PAT008", "Irene", "Ferri", "2025-04-25", 92)
]
cursor.executemany("""
INSERT OR IGNORE INTO Possible_Follow_Up_Patients (PatientID, Name, Surname, Date, Days_since_last_OSA)
VALUES (?, ?, ?, ?, ?)
""", possible_follow_up)

# Follow_Up_Patients
follow_up_patients = [
    ("PAT006", "Federica", "Russo", "2025-04-21", 89, 2),
    ("PAT012", "Davide", "Rizzi", "2025-04-21", 90, 4),
    ("PAT014", "Stefano", "Barbieri", "2025-04-21", 91, 1)
]
cursor.executemany("""
INSERT OR IGNORE INTO Follow_Up_Patients (PatientID, Name, Surname, Date, SpO2_min, ODI)
VALUES (?, ?, ?, ?, ?, ?)
""", follow_up_patients)

# Seven_days_patients_ok
seven_ok = [
    ("PAT003", "Marco", "Verdi", "2025-03-21", 7),
    ("PAT005", "Giorgio", "Fontana", "2025-02-15", 10),
    ("PAT013", "Marta", "De Luca", "2025-05-05", 12),
    ("PAT015", "Elena", "Romano", "2024-06-04", 8)
]
cursor.executemany("""
INSERT OR IGNORE INTO Seven_days_patients_ok (PatientID, Name, Surname, Date, Days_since_last_OSA)
VALUES (?, ?, ?, ?, ?)
""", seven_ok)

# Remove duplicate entries and invalid patient IDs from Indexes
cursor.execute("DELETE FROM Indexes WHERE PatientID = 'PAT021'")
cursor.execute("""
    DELETE FROM Indexes 
    WHERE rowid NOT IN (
        SELECT MIN(rowid) 
        FROM Indexes 
        GROUP BY PatientID, Date
    )
""")

conn.commit()
conn.close()
