import sqlite3 # for database
import os  #for system access
import hashlib  #password
import binascii  #password
from datetime import date  

DB_FILENAME = "temple_management.db"

# ---------------------------
# Password hashing
# ---------------------------
def hash_password(password: str, salt: bytes = None, iterations: int = 100_000):
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return binascii.hexlify(salt).decode(), binascii.hexlify(pwd_hash).decode()
# verifing password

def verify_password(stored_salt_hex: str, stored_hash_hex: str, provided_password: str, iterations: int = 100_000):
    salt = binascii.unhexlify(stored_salt_hex.encode())
    verify_hash = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, iterations)
    return binascii.hexlify(verify_hash).decode() == stored_hash_hex

# ---------------------------
# Connection
# ---------------------------
def get_connection(db_file=DB_FILENAME):
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ---------------------------
# Create tables (single place)
# ---------------------------
def create_tables(db_file=DB_FILENAME):
    conn = get_connection(db_file)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Employee (
        EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Role TEXT,
        ContactNumber TEXT,
        EmailID TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS EmployeeLogin (
        LoginID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmployeeID INTEGER UNIQUE NOT NULL,
        Username TEXT UNIQUE NOT NULL,
        PasswordSalt TEXT NOT NULL,
        PasswordHash TEXT NOT NULL,
        Role TEXT,
        LastLogin TEXT,
        FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS WorshipTypes (
        WorshipID INTEGER PRIMARY KEY AUTOINCREMENT,
        WorshipName TEXT UNIQUE NOT NULL,
        Rate REAL DEFAULT 0.0
    );

    CREATE TABLE IF NOT EXISTS Devotee (
        DevoteeID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Contact TEXT
    );

    CREATE TABLE IF NOT EXISTS PoojaTicket (
        PoojaTicketID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmployeeID INTEGER,
        DevoteeID INTEGER,
        WorshipType TEXT,
        Date TEXT NOT NULL,
        NumberOfTickets INTEGER DEFAULT 1,
        AmountPaid REAL DEFAULT 0.0,
        TransactionType TEXT,
        FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID),
        FOREIGN KEY (DevoteeID) REFERENCES Devotee(DevoteeID)
    );

    CREATE TABLE IF NOT EXISTS Stage (
        StageID INTEGER PRIMARY KEY AUTOINCREMENT,
        StageName TEXT NOT NULL,
        Location TEXT,
        Capacity INTEGER,
        AvailabilityStatus TEXT DEFAULT 'available'
    );

    CREATE TABLE IF NOT EXISTS StageBookings (
        StageBookingID INTEGER PRIMARY KEY AUTOINCREMENT,
        StageID INTEGER,
        EmployeeID INTEGER,
        EventName TEXT,
        BookingDate TEXT,
        StartTime TEXT,
        EndTime TEXT,
        Status TEXT DEFAULT 'confirmed',
        FOREIGN KEY (StageID) REFERENCES Stage(StageID) ON DELETE CASCADE,
        FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Donor (
        DonorID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Donations (
        DonationsID INTEGER PRIMARY KEY AUTOINCREMENT,
        EmployeeID INTEGER,
        DonorID INTEGER,
        DonationDate TEXT,
        DonationType TEXT,
        Amount REAL,
        FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID),
        FOREIGN KEY (DonorID) REFERENCES Donor(DonorID)
    );
    
    
    CREATE TABLE IF NOT EXISTS FestivalCalendar (
        FestivalID INTEGER PRIMARY KEY AUTOINCREMENT,
        FestivalName TEXT NOT NULL,
        FestivalDate TEXT NOT NULL,
        Notes TEXT
    );
    
    
    """)
    conn.commit()
    conn.close()
    print(f"Database and tables created (or verified) in {db_file}")

# ---------------------------
# Employee functions
# ---------------------------
def add_employee(name, role=None, contact=None, email=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Employee (Name, Role, ContactNumber, EmailID) VALUES (?, ?, ?, ?)",
                (name, role, contact, email))
    conn.commit()
    emp_id = cur.lastrowid
    conn.close()
    return emp_id

def create_employee_login(employee_id, username, password, role=None):
    salt_hex, hash_hex = hash_password(password)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO EmployeeLogin (EmployeeID, Username, PasswordSalt, PasswordHash, Role) VALUES (?, ?, ?, ?, ?)",
                (employee_id, username, salt_hex, hash_hex, role))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT PasswordSalt, PasswordHash FROM EmployeeLogin WHERE Username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    salt, hash_ = row
    return verify_password(salt, hash_, password)

def get_employee_id(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT EmployeeID FROM EmployeeLogin WHERE Username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_role(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT Role FROM EmployeeLogin WHERE Username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_employees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT EmployeeID, Name, Role, EmailID FROM Employee")
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_employee_by_id(employee_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM EmployeeLogin WHERE EmployeeID=?", (employee_id,))
    cur.execute("DELETE FROM Employee WHERE EmployeeID=?", (employee_id,))
    conn.commit()
    conn.close()

# ---------------------------
# Worship functions
# ---------------------------
def add_worship_type(name, rate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO WorshipTypes (WorshipName, Rate) VALUES (?, ?)", (name, rate))
    conn.commit()
    conn.close()

def update_worship_rate(worship_id, new_rate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE WorshipTypes SET Rate=? WHERE WorshipID=?", (new_rate, worship_id))
    conn.commit()
    conn.close()

def get_all_worship_types():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT WorshipID, WorshipName, Rate FROM WorshipTypes")
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------------------
# Devotee & Tickets
# ---------------------------
def add_devotee(name, contact=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Devotee (Name, Contact) VALUES (?, ?)", (name, contact))
    conn.commit()
    did = cur.lastrowid
    conn.close()
    return did

def issue_pooja_ticket(employee_id, devotee_id, worship_type, date_str, number_of_tickets=1, amount_paid=0.0, transaction_type=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO PoojaTicket (EmployeeID, DevoteeID, WorshipType, Date, NumberOfTickets, AmountPaid, TransactionType) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (employee_id, devotee_id, worship_type, date_str, number_of_tickets, amount_paid, transaction_type))
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id

def get_issued_tickets_by_employee(employee_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT PoojaTicketID, WorshipType, Date, NumberOfTickets, AmountPaid FROM PoojaTicket WHERE EmployeeID=?", (employee_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_last_ticket_by_employee(employee_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT PoojaTicketID FROM PoojaTicket WHERE EmployeeID=? ORDER BY PoojaTicketID DESC LIMIT 1", (employee_id,))
    row = cur.fetchone()
    conn.close()
    return row

# ---------------------------
# Stage (CRUD)
# ---------------------------
def add_stage(stage_name, location=None, capacity=0, availability_status='available'):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Stage (StageName, Location, Capacity, AvailabilityStatus) VALUES (?, ?, ?, ?)",
                (stage_name, location, capacity, availability_status))
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid

def update_stage(stage_id, stage_name=None, location=None, capacity=None, availability_status=None):
    conn = get_connection()
    cur = conn.cursor()
    fields = []
    values = []
    if stage_name is not None:
        fields.append("StageName=?"); values.append(stage_name)
    if location is not None:
        fields.append("Location=?"); values.append(location)
    if capacity is not None:
        fields.append("Capacity=?"); values.append(capacity)
    if availability_status is not None:
        fields.append("AvailabilityStatus=?"); values.append(availability_status)
    if not fields:
        conn.close(); return
    values.append(stage_id)
    cur.execute(f"UPDATE Stage SET {', '.join(fields)} WHERE StageID=?", values)
    conn.commit()
    conn.close()

def delete_stage(stage_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Stage WHERE StageID=?", (stage_id,))
    conn.commit()
    conn.close()

def get_all_stages():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT StageID, StageName, Location, Capacity, AvailabilityStatus FROM Stage")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_stage_id_by_name(stage_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT StageID FROM Stage WHERE StageName=?", (stage_name,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def get_stage_bookings_by_employee(employee_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT EventName, BookingDate, StartTime, EndTime, Status FROM StageBookings WHERE EmployeeID=?", (employee_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_stage_bookings(stage_id=None, date_str=None):
    conn = get_connection()
    cur = conn.cursor()
    q = "SELECT StageBookingID, StageID, EmployeeID, EventName, BookingDate, StartTime, EndTime, Status FROM StageBookings WHERE 1=1"
    params = []
    if stage_id:
        q += " AND StageID=?"
        params.append(stage_id)
    if date_str:
        q += " AND BookingDate=?"
        params.append(date_str)
    q += " ORDER BY BookingDate, StartTime"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def book_stage(stage_id, employee_id, event_name, booking_date, start_time, end_time, status='confirmed'):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM StageBookings
        WHERE StageID=? AND BookingDate=? AND Status IN ('confirmed','approved')
          AND NOT (EndTime <= ? OR StartTime >= ?)
    """, (stage_id, booking_date, start_time, end_time))
    conflict = cur.fetchone()
    if conflict:
        conn.close()
        raise Exception("Stage not available for the requested slot.")
    cur.execute("INSERT INTO StageBookings (StageID, EmployeeID, EventName, BookingDate, StartTime, EndTime, Status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (stage_id, employee_id, event_name, booking_date, start_time, end_time, status))
    conn.commit()
    conn.close()

# ---------------------------
# Donations
# ---------------------------
def add_donor(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Donor (Name) VALUES (?)", (name,))
    conn.commit()
    did = cur.lastrowid
    conn.close()
    return did

def record_donation(employee_id, donor_id, donation_date, donation_type, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Donations (EmployeeID, DonorID, DonationDate, DonationType, Amount) VALUES (?, ?, ?, ?, ?)",
                (employee_id, donor_id, donation_date, donation_type, amount))
    conn.commit()
    conn.close()

def get_all_donations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(E.Name,'') AS EmployeeName, COALESCE(D.Name,'') AS DonorName, Donations.DonationDate, Donations.DonationType, Donations.Amount
        FROM Donations
        LEFT JOIN Employee E ON Donations.EmployeeID = E.EmployeeID
        LEFT JOIN Donor D ON Donations.DonorID = D.DonorID
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------------------
# Festival Calendar
# ---------------------------
def add_festival(name, date_str, notes=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO FestivalCalendar (FestivalName, FestivalDate, Notes) VALUES (?, ?, ?)",
        (name, date_str, notes)
    )
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid

def update_festival(festival_id, name=None, date_str=None, notes=None):
    conn = get_connection()
    cur = conn.cursor()
    fields = []
    values = []
    if name: fields.append("FestivalName=?"); values.append(name)
    if date_str: fields.append("FestivalDate=?"); values.append(date_str)
    if notes: fields.append("Notes=?"); values.append(notes)
    values.append(festival_id)
    if fields:
        cur.execute(f"UPDATE FestivalCalendar SET {', '.join(fields)} WHERE FestivalID=?", values)
    conn.commit()
    conn.close()

def delete_festival(festival_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM FestivalCalendar WHERE FestivalID=?", (festival_id,))
    conn.commit()
    conn.close()

def get_all_festivals():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT FestivalID, FestivalName, FestivalDate, Notes FROM FestivalCalendar ORDER BY FestivalDate")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_festivals_by_month(year, month):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT FestivalID, FestivalName, FestivalDate, Notes FROM FestivalCalendar "
        "WHERE strftime('%Y', FestivalDate)=? AND strftime('%m', FestivalDate)=? ORDER BY FestivalDate",
        (str(year), f"{int(month):02d}")
    )
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------------------
# Demo helper (optional)
# ---------------------------
def demo_seed():
    # create tables and add a manager account if none exists
    create_tables()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) FROM Employee")
    if cur.fetchone()[0] == 0:
        emp_id = add_employee("Admin", "Manager", "000", "admin@example.com")
        create_employee_login(emp_id, "admin", "admin123", "Manager")
    conn.close()

if __name__ == "__main__":
    create_tables()
    demo_seed()