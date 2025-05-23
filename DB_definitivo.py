import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("Database_proj.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS Patiens_Ok;")
# ========== CREAZIONE TABELLE ==========

cursor.execute("""
CREATE TABLE IF NOT EXISTS Patients (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Surname TEXT NOT NULL,
    dateOfBirth DATE,
    height REAL CHECK(height > 0),
    weight REAL CHECK(weight > 0),
    Age INTEGER CHECK(Age > 0),
    Gender CHAR(1) CHECK(Gender IN ('M', 'F', 'O')),
    Nationality TEXT DEFAULT 'Italian',
    ClinicalHistory TEXT,
    PatientID TEXT NOT NULL UNIQUE,
    PatientPassword TEXT,
    PhoneNumber TEXT UNIQUE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Questionnaire (
    QuestID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID TEXT NOT NULL,
    Date DATE,
    Q1 INTEGER, Q2 INTEGER, Nota2 TEXT, Q3 INTEGER, Q4 INTEGER, Q5 INTEGER, Q6 INTEGER, Q7 INTEGER,
    Q8 INTEGER, Q9 TEXT, Q10 INTEGER, Q11 TEXT, Q12 INTEGER, Q13 TEXT
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
INSERT OR IGNORE INTO Patients (Name, Surname, dateOfBirth, height, weight, Age, Gender, Nationality, ClinicalHistory, PatientID, PatientPassword, PhoneNumber)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ("Luca", "Bianchi", "2000-05-15", 1.75, 70, 33, "M", "Italiano", "Nessuna", "PAT001", "password123", "1234567890"),
    ("Lucia", "Garofalo", "2004-06-15", 1.65, 60, 25, "F", "Italiano", "Nessuna", "PAT002", "345678", "1234567899"),
    ("Marco", "Verdi", "1992-03-22", 1.80, 85, 32, "M", "Italiano", "Asma lieve", "PAT003", "pass333", "1234562222"),
    ("Marco", "Esposito", "1956-06-16", 1.87, 90, 30, "M", "Italiano", "Osa moderata", "PAT009", "pass333", "1234562226"),
    ("Angelo", "Galli", "1992-04-26", 1.70, 80, 30, "M", "Italiano", "Osa moderata", "PAT010", "pass333", "1234562228")
])


# Popola Appointments da 16 Maggio a 16 Giugno 2025
slot_times = ["08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30"]
doctors = [("DOC001", "Mario Rossi"), ("DOC002", "Anna Vincentelli")]
appointments = []
start_date = datetime(2025, 5, 16).date()
end_date = datetime(2025, 6, 16).date()
current_date = start_date

while current_date <= end_date:
    if current_date.weekday() < 5:
        for doctor_id, doctor_name in doctors:
            for slot in slot_times:
                appointments.append((current_date.isoformat(), slot, doctor_id, doctor_name, 'available', None, None))
    current_date += timedelta(days=1)

# Slot prenotati
booked_slots = [
    ("2025-05-19", "08:30", "DOC001", "Mario Rossi", "booked", "PAT001", "Luca Bianchi"),
    ("2025-05-23", "13:30", "DOC001", "Mario Rossi", "booked", "PAT002", "Lucia Garofalo"),
]
for date, time_slot, doc_id, doctor_name, status, pat_id, pat_name in booked_slots:
    appointments.append((date, time_slot, doc_id, doctor_name, status, pat_id, pat_name))


cursor.executemany("""
INSERT INTO Appointments (date, time, doctor_id, doctor_name, status, patient_id, patient_name)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", appointments)

# Inserimento Drugs
drugs = [
    ("PAT001", "Paracetamolo 500mg 2 volte al giorno", "2025-04-20", "2025-04-27"),
    ("PAT002", "Ibuprofene al bisogno", "2025-04-21", "2025-04-25"),
    ("PAT003", "Salbutamolo spray 2 puff al bisogno", "2025-04-22", "2025-04-30")
]
cursor.executemany("""
INSERT OR IGNORE INTO Drugs (PatientID, Note, StartDate, EndDate)
VALUES (?, ?, ?, ?)
""", drugs)

# Inserimento Therapy
therapies = [
    ("PAT001", "Monitoraggio continuo con eventuale follow-up dopo 10 giorni"),
    ("PAT002", "Controllo pressorio settimanale"),
    ("PAT003", "Controllo asma trimestrale"),
    ("PAT010", "CPAP_350_x7_gg")
]
cursor.executemany("""
INSERT OR IGNORE INTO Therapy (PatientID, Note)
VALUES (?, ?)
""", therapies)

# Inserimento Indexes
indexes = [
    ("PAT001", "2025-04-20", 5.2, 4.1, 95.2, 88.5),
    ("PAT001", "2025-04-19", 6.0, 3.5, 96.0, 89.0),
    ("PAT001", "2025-04-18", 5.3, 4.1, 95.0, 87.0),
    ("PAT001", "2025-04-17", 5.5, 4.0, 95.5, 90.0),
    ("PAT002", "2025-04-21", 12.4, 8.7, 92.0, 84.3),
    ("PAT010", "2025-04-22", 2.5, 1.8, 96.5, 90.0),
    ("PAT011", "2025-04-22", 4.5, 0.7, 96.5, 90.0),
    ("PAT021", "2025-04-22", 7.5, 1.3, 96.5, 90.0),
    ("PAT009", "2025-04-24", 0.5, 1.5, 96.5, 90.0),
    ("PAT009", "2025-04-24", 0.5, 1.5, 96.5, 90.0),
    ("PAT009", "2025-04-25", 0.5, 1.5, 96.5, 90.0),
    ("PAT009", "2025-04-26", 0.5, 1.5, 96.5, 90.0),
    ("PAT009", "2025-04-27", 0.5, 1.5, 96.5, 90.0),
    ("PAT009", "2025-04-28", 0.5, 1.5, 96.5, 90.0),
    ("PAT009", "2025-04-29", 0.5, 1.5, 96.5, 90.0),
    ("PAT009", "2025-04-30", 0.5, 1.5, 96.5, 90.0),
    ("PAT010", "2025-04-24", 0.5, 1.5, 96.5, 90.0),
    ("PAT010", "2025-04-25", 1, 1, 96.5, 90.0),
    ("PAT010", "2025-04-26", 1.2, 1.5, 96.5, 90.0),
    ("PAT010", "2025-04-27", 0.8, 7, 96.5, 90.0),
    ("PAT010", "2025-04-28", 4, 8, 96.5, 90.0),
    ("PAT010", "2025-04-29", 10, 15, 96.5, 90.0)
]
cursor.executemany("""
INSERT OR IGNORE INTO Indexes (PatientID, Date, ValueAHI, ValueODI, MeanSpO2, MinSpO2)
VALUES (?, ?, ?, ?, ?, ?)
""", indexes)

# Inserimento Questionnaire
#questionnaires = [
#    ("PAT001", "2025-04-20", 1, 2, "Nota2 esempio", 3, 4, 5, 6, 7, 8, "Q9 esempio", 10, "Q11 esempio", 12, "Q13 esempio"),
#    ("PAT002", "2025-04-21", 2, 3, "Nota2 esempio", 4, 5, 6, 7, 8, 9, "Q9 esempio", 11, "Q11 esempio", 13, "Q13 esempio")
#]

#cursor.executemany("""
#INSERT OR IGNORE INTO Questionnaire (PatientID, Date, Q1, Q2, Nota2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13)
#VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#""", questionnaires)

# Inserimento Notifications
notifications = [
    ("PAT001", "Luca Bianchi", "REMINDER", "Ricorda di prendere la terapia", "2025-05-19 08:00:00", 0),
    ("PAT002", "Lucia Garofalo", "DOCTOR_ALERT", "Contatta il tuo medico per un follow-up", "2025-05-20 09:00:00", 0)
]
cursor.executemany("""
INSERT OR IGNORE INTO Notifications (PatientID, PatientName, Type, Message, Timestamp, IsRead)
VALUES (?, ?, ?, ?, ?, ?)
""", notifications)


# OSA_Patients
osa_patients = [
    ("PAT010", "Angelo", "Galli", "2025-01-01", 17),
    ("PAT011", "Francesca", "Colombo", "2025-01-01", 19),
    ("PAT021", "Roberto", "Ferrari", "2025-01-01", 15)
]
cursor.executemany("""
INSERT OR IGNORE INTO OSA_Patients (PatientID, Name, Surname, Date, AHI)
VALUES (?, ?, ?, ?, ?)
""", osa_patients)

# Possible_Follow_Up_Patients
possible_follow_up = [
    ("PAT009", "Marco", "Esposito", "2025-01-01", 90),
    ("PAT030", "Luca", "Greco", "2025-01-01", 94),
    ("PAT041", "Elena", "Conti", "2025-01-01", 97)
]
cursor.executemany("""
INSERT OR IGNORE INTO Possible_Follow_Up_Patients (PatientID, Name, Surname, Date, Days_since_last_OSA)
VALUES (?, ?, ?, ?, ?)
""", possible_follow_up)

# Follow_Up_Patients
follow_up_patients = [
    ("PAT019", "Davide", "De Luca", "2025-01-01", 96, 2),
    ("PAT024", "Martina", "Rinaldi", "2025-01-01", 97, 3),
    ("PAT032", "Alessandra", "Romano", "2025-01-01", 92, 12)
]
cursor.executemany("""
INSERT OR IGNORE INTO Follow_Up_Patients (PatientID, Name, Surname, Date, SpO2_min, ODI)
VALUES (?, ?, ?, ?, ?, ?)
""", follow_up_patients)

# Seven_days_patients_ok
seven_ok = [
    ("PAT017", "Elena", "Moretti", "2025-01-01", 7),
    ("PAT033", "Franco", "Lombardi", "2025-01-01", 7),
    ("PAT052", "James", "Anderson", "2025-01-01", 8),
    ("PAT025", "Chen", "Wei", "2025-01-01", 11)
]
cursor.executemany("""
INSERT OR IGNORE INTO Seven_days_patients_ok (PatientID, Name, Surname, Date, Days_since_last_OSA)
VALUES (?, ?, ?, ?, ?)
""", seven_ok)

conn.commit()
conn.close()
