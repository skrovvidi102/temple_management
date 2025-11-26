# pdf_utils.py
from fpdf import FPDF, XPos, YPos
import os
import platform
import subprocess
from tkinter import messagebox
from datetime import datetime
from temple_db import get_connection, get_all_worship_types
import calendar

# ---------- PREVIEW + PRINT ----------
def preview_and_print(filename):
    system = platform.system()

    # Preview
    try:
        if system == "Darwin":
            subprocess.run(["open", filename])
        elif system == "Windows":
            os.startfile(filename)
        else:
            subprocess.run(["xdg-open", filename])
    except Exception as e:
        print("Preview error:", e)

    # Ask
    choice = messagebox.askyesno("Print", "Do you want to print this document?")
    if not choice:
        return

    # Print
    try:
        if system == "Windows":
            os.startfile(filename, "print")
        else:
            subprocess.run(["lp", filename])
    except Exception as e:
        print("Print error:", e)


# ---------- PDF base class ----------
class TicketPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Temple Management System", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")


# ---------- Helpers ----------
def get_rate(worship_name):
    types = get_all_worship_types()
    for wt in types:
        if wt[1] == worship_name:
            return wt[2]
    return 0.0


# ---------- Ticket PDF (reads DB inside) ----------
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
    # compute total dynamically if AmountPaid is null/zero
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


# ---------- Festival calendar (GRID) ----------
def generate_festival_calendar_pdf(festivals, year, month):
    """
    festivals: list of tuples (FestivalID, FestivalName, FestivalDate(YYYY-MM-DD), Notes)
    year: int
    month: int (1-12)
    Produces a month-grid calendar with festival names inside date cells.
    """
    # Map day -> list of festivals
    fest_map = {}
    for f in festivals:
        try:
            fdate = f[2]  # expecting 'YYYY-MM-DD'
            y, m, d = map(int, fdate.split("-"))
            if y == int(year) and m == int(month):
                fest_map.setdefault(d, []).append(f)
        except Exception:
            continue

    cal = calendar.Calendar(firstweekday=6)  # Sunday start (6) or change as needed
    month_days = cal.monthdayscalendar(int(year), int(month))  # list of weeks (each week list of 7 ints)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Festival Calendar - {calendar.month_name[int(month)]} {year}", ln=True, align="C")
    pdf.ln(6)

    # Grid layout
    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    cell_w = page_w / 7
    cell_h = 28  # adjust height

    # Weekday headers
    pdf.set_font("Helvetica", "B", 10)
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    x_start = pdf.get_x()
    for wd in weekdays:
        pdf.cell(cell_w, 8, wd, border=1, align="C")
    pdf.ln()

    # Weeks
    pdf.set_font("Helvetica", "", 9)
    for week in month_days:
        for day in week:
            if day == 0:
                pdf.cell(cell_w, cell_h, "", border=1)  # empty cell
            else:
                # build cell content: day number + festival names (short)
                lines = [str(day)]
                if day in fest_map:
                    for f in fest_map[day]:
                        # keep festival name short: limit to 30 chars per line
                        fname = f[1]
                        notes = f[3] or ""
                        lines.append(fname if len(fname) <= 30 else fname[:27] + "...")
                # draw cell text
                # first line bigger for day
                pdf.multi_cell(cell_w, 6, "\n".join(lines), border=1, align="L")
                
                x_right = pdf.get_x()
                y_current = pdf.get_y()
                
        pass

    # Simpler robust implementation: draw the grid row-by-row using cell and then write content in each cell using text positioning.
    pdf.add_page()  # create a clean page and draw grid manually

    # Title again on new page
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Festival Calendar - {calendar.month_name[int(month)]} {year}", ln=True, align="C")
    pdf.ln(6)

    # compute positions
    x0 = pdf.l_margin
    y0 = pdf.get_y()
    pdf.set_font("Helvetica", "", 9)
    # header row
    for wd in weekdays:
        pdf.rect(x0, y0, cell_w, 8)
        pdf.text(x0 + 2, y0 + 6, wd)
        x0 += cell_w
    y = y0 + 8

    # weeks
    for week in month_days:
        x = pdf.l_margin
        max_row_height = cell_h
        for day in week:
            pdf.rect(x, y, cell_w, cell_h)
            if day == 0:
                # nothing
                pass
            else:
                # day number
                pdf.set_xy(x + 2, y + 3)
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 4, str(day), ln=1)
                pdf.set_font("Helvetica", "", 9)
                # festival names
                if day in fest_map:
                    top = y + 8
                    pdf.set_xy(x + 2, top)
                    for f in fest_map[day]:
                        text = f[1]
                        # write limited lines
                        pdf.multi_cell(cell_w - 4, 4, text, border=0, align="L")
                        # move cursor down a bit automatically
            x += cell_w
        y += cell_h

    filename = f"festival_calendar_{year}_{month}.pdf"
    pdf.output(filename)

    preview_and_print(filename)
    return os.path.abspath(filename)


# ---------- Donation receipt (with DON- prefix) ----------
def generate_donation_receipt(donation_id, donor_name, donation_type, amount, donation_date, employee_name):
    # donation_id is numeric - we will create prefix DON-####
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


# ---------- Stage booking receipt (includes location) ----------
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