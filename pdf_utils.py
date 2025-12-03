# pdf_utils.py
from fpdf import FPDF, XPos, YPos
import os
import platform
import subprocess
from tkinter import messagebox
from datetime import datetime
from temple_db import (
    get_connection, get_all_worship_types
)
import calendar

# ------------------ TEMPLE NAME ------------------
def get_temple_name():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT TempleName FROM TempleInfo LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else "Temple Name Not Set"
    finally:
        conn.close()

# ---------- PREVIEW + PRINT ----------
def preview_and_print(filename):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", filename])
        elif system == "Windows":
            os.startfile(filename)
        else:
            subprocess.run(["xdg-open", filename])
    except Exception as e:
        print("Preview error:", e)

    choice = messagebox.askyesno("Print", "Do you want to print this document?")
    if not choice:
        return

    try:
        if system == "Windows":
            os.startfile(filename, "print")
        else:
            subprocess.run(["lp", filename])
    except Exception as e:
        print("Print error:", e)

# ---------- PDF base class with logo ----------
class TicketPDF(FPDF):
    logo_path = "/Users/sakethkrovvidi/Desktop/project code/Neutral Elegant Minimalist Jewelry Logo.png"  # replace with your logo path

    def header(self):
        # Add logo above the title
        if os.path.exists(self.logo_path):
            logo_width = 40
            x = (self.w - logo_width) / 2
            self.image(self.logo_path, x=x, y=8, w=logo_width)

        # Temple name dynamically
        temple_name = get_temple_name()

        # Title below logo
        self.set_y(8 + 40 + 4)  # top margin + logo height + padding
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, temple_name, ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", align="C")

# ---------- Helpers ----------
def get_rate(worship_name):
    types = get_all_worship_types()
    for wt in types:
        if wt[1] == worship_name:
            return wt[2]
    return 0.0

# ---------- Ticket PDF ----------
def generate_ticket_pdf(ticket_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT P.PoojaTicketID, D.Name, D.Contact, P.WorshipType, P.Date,
               P.NumberOfTickets, P.AmountPaid, P.TransactionType, E.Name
        FROM PoojaTicket P
        LEFT JOIN Devotee D ON P.DevoteeID = D.DevoteeID
        LEFT JOIN Employee E ON P.EmployeeID = E.EmployeeID
        WHERE P.PoojaTicketID = ?
    """, (ticket_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"No ticket found with ID {ticket_id}")

    ticket_id, devotee_name, contact, worship_type, date_str, num_tickets, total_amount, trans_type, employee_name = row

    pdf = TicketPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def row_field(label, value):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(50, 8, label, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(value or "N/A"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"Pooja Ticket - #{ticket_id}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(4)

    row_field("Devotee Name:", devotee_name)
    row_field("Contact:", contact)
    row_field("Worship Type:", worship_type)
    row_field("Date:", date_str)
    row_field("Tickets Issued:", num_tickets)
    rate = get_rate(worship_type)
    computed_total = (num_tickets or 0) * (rate or 0.0)
    total_to_show = (total_amount if (total_amount and total_amount > 0) else computed_total)
    row_field("Rate (per ticket):", f"{rate:.2f}")
    row_field("Total Price:", f"{total_to_show:.2f}")
    row_field("Transaction Type:", trans_type)
    row_field("Issued By:", employee_name)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, " Thank you for your devotion! ", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    output_dir = "generated_tickets"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"ticket_{ticket_id}.pdf")
    pdf.output(filename)

    preview_and_print(filename)
    return os.path.abspath(filename)

# ---------- Festival calendar ----------
def generate_festival_calendar_pdf(festivals, year, month):
    fest_map = {}
    for f in festivals:
        try:
            fdate = f[2]
            y, m, d = map(int, fdate.split("-"))
            if y == int(year) and m == int(month):
                fest_map.setdefault(d, []).append(f)
        except Exception:
            continue

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(int(year), int(month))

    pdf = TicketPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Festival Calendar - {calendar.month_name[int(month)]} {year}", ln=True, align="C")
    pdf.ln(6)

    # Grid layout
    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    cell_w = page_w / 7
    cell_h = 28

    # Weekday headers
    pdf.set_font("Helvetica", "B", 10)
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    x_start = pdf.get_x()
    for wd in weekdays:
        pdf.cell(cell_w, 8, wd, border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for week in month_days:
        x = pdf.l_margin
        for day in week:
            pdf.rect(x, pdf.get_y(), cell_w, cell_h)
            if day != 0:
                pdf.set_xy(x + 2, pdf.get_y() + 3)
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 4, str(day), ln=1)
                if day in fest_map:
                    pdf.set_font("Helvetica", "", 9)
                    top = pdf.get_y()
                    pdf.set_xy(x + 2, top)
                    for f in fest_map[day]:
                        pdf.multi_cell(cell_w - 4, 4, f[1][:27] + ("..." if len(f[1]) > 27 else ""), border=0, align="L")
            x += cell_w
        pdf.ln(cell_h)

    filename = f"festival_calendar_{year}_{month}.pdf"
    pdf.output(filename)
    preview_and_print(filename)
    return os.path.abspath(filename)

# ---------- Donation receipt ----------
def generate_donation_receipt(donation_id, donor_name, donation_type, amount, donation_date, employee_name):
    prefix = f"DON-{int(donation_id):04d}"
    pdf = TicketPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Donation Receipt", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(4)

    def r(label, value):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(50, 8, label, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(value or "N/A"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    r("Receipt No.:", prefix)
    r("Donor Name:", donor_name)
    r("Donation Type:", donation_type)
    r("Amount:", f"{amount:.2f}")
    r("Date:", donation_date)
    r("Recorded By:", employee_name)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Thank you for your generous support!", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    output_dir = "generated_receipts"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"donation_{donation_id}.pdf")
    pdf.output(filename)
    preview_and_print(filename)
    return os.path.abspath(filename)

# ---------- Stage booking receipt ----------
def generate_stage_booking_receipt(booking_id, stage_name, stage_location, event_name, booking_date, start_time, end_time, employee_name):
    pdf = TicketPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Stage Booking Receipt", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(4)

    def r(label, value):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(50, 8, label, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(value or "N/A"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    r("Booking ID:", booking_id)
    r("Stage Name:", stage_name)
    r("Stage Location:", stage_location)
    r("Event Name:", event_name)
    r("Booking Date:", booking_date)
    r("Time:", f"{start_time} - {end_time}")
    r("Booked By:", employee_name)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Booking Confirmed!", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    output_dir = "generated_receipts"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"booking_{booking_id}.pdf")
    pdf.output(filename)
    preview_and_print(filename)
    return os.path.abspath(filename)