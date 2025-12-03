# staff_dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import date
import os

from temple_db import (
    get_employee_id, get_all_worship_types, add_devotee, issue_pooja_ticket,
    get_all_stages, book_stage, record_donation, add_donor,
    get_stage_bookings_by_employee, get_issued_tickets_by_employee,
    get_last_ticket_by_employee, get_connection, get_all_festivals, get_festivals_by_month
)

from pdf_utils import (
    generate_ticket_pdf, generate_donation_receipt, generate_stage_booking_receipt,
    generate_festival_calendar_pdf, get_rate
)
from datetime import datetime
from temple_db import is_stage_available

# ----------------------------
# Scrollable Frame Component
# ----------------------------
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # Canvas
        self.canvas = tk.Canvas(self, bg="#f0f8ff", highlightthickness=0)

        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        # Frame inside canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Create window inside canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure canvas scroll
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Pack everything
        self.canvas.pack(side="top", fill="both", expand=True)
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")

        # Mouse wheel scroll bindings
        self.scrollable_frame.bind("<Enter>", self._bind_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_mousewheel)

        # Click-and-drag scrolling
        self.canvas.bind("<ButtonPress-1>", self._scroll_start)
        self.canvas.bind("<B1-Motion>", self._scroll_move)

    # Vertical scroll with mouse wheel, horizontal with Shift + wheel
    def _bind_mousewheel(self, event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if event.state & 0x1:  # Shift key is pressed
            self.canvas.xview_scroll(-1 * (event.delta // 120), "units")
        else:
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # Click-and-drag horizontal & vertical scroll
    def _scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)


# ----------------------------
# Card Component
# ----------------------------
def make_card(parent, icon, title, subtitle, command, bg="#ffffff"):
    card = tk.Frame(parent, bg=bg, bd=1, relief="raised", padx=12, pady=12)
    card.grid_propagate(False)
    card.columnconfigure(0, weight=1)

    tk.Label(card, text=icon, font=("Arial", 22), bg=bg).grid(row=0, column=0, sticky="n")
    tk.Label(card, text=title, font=("Arial", 12, "bold"), bg=bg).grid(row=1, column=0, pady=(8, 0))
    tk.Label(card, text=subtitle, font=("Arial", 9), bg=bg, fg="#555").grid(row=2, column=0, pady=(4, 0))
    tk.Button(card, text="Open", command=command, bg="#1976d2", fg="white").grid(row=3, column=0, pady=(10, 0), sticky="ew")

    return card


# ----------------------------
# Staff Dashboard
# ----------------------------
def staff_dashboard(root, username):

    # Clear window
    for w in root.winfo_children():
        w.destroy()

    # Setup window
    root.title("Temple Management System - Staff")
    try:
        root.state('zoomed')
    except:
        root.geometry("1200x700")

    root.configure(bg="#f0f8ff")

    # User details
    staff_id = get_employee_id(username)
    staff_name = username

    # ---------------- Header ----------------
    header = tk.Frame(root, bg="#f0f8ff")
    header.pack(fill="x", padx=12, pady=10)

    tk.Label(
        header, text=f"{staff_name} • Staff",
        font=("Arial", 14, "bold"), bg="#f0f8ff"
    ).pack(side="left", padx=12)

    tk.Button(header, text="X", bg="#ef5350", fg="white",
              command=root.destroy).pack(side="right", padx=12)

    # ---------------- Scrollable Grid Area ----------------
    scroll_area = ScrollableFrame(root)
    scroll_area.pack(fill="both", expand=True, padx=20, pady=8)

    grid_frame = tk.Frame(scroll_area.scrollable_frame, bg="#f0f8ff")
    grid_frame.pack(fill="both", expand=True)

    cols = 3
    for c in range(cols):
        grid_frame.columnconfigure(c, weight=1, uniform="c")

    # ======================================================
    #                STAFF ACTION FUNCTIONS
    # ======================================================

    # ---- Issue Ticket ----
    def issue_ticket_ui():
        win = tk.Toplevel(root)
        win.title("Issue Ticket")
        win.geometry("420x520")
        win.configure(bg="#f5f5f5")

        tk.Label(win, text="Devotee Name:", bg="#f5f5f5").pack(pady=4)
        devotee_name = tk.Entry(win)
        devotee_name.pack(fill="x", padx=10)

        tk.Label(win, text="Contact:", bg="#f5f5f5").pack(pady=4)
        contact = tk.Entry(win)
        contact.pack(fill="x", padx=10)

        tk.Label(win, text="Worship Type:", bg="#f5f5f5").pack(pady=4)
        worship_types = get_all_worship_types()
        worship_cb = ttk.Combobox(win, values=[wt[1] for wt in worship_types])
        worship_cb.pack(fill="x", padx=10)

        tk.Label(win, text="Number of Tickets:", bg="#f5f5f5").pack(pady=4)
        num_tickets = tk.Entry(win)
        num_tickets.pack(fill="x", padx=10)

        tk.Label(win, text="Transaction Type:", bg="#f5f5f5").pack(pady=4)
        transaction_type = tk.Entry(win)
        transaction_type.pack(fill="x", padx=10)

        total_price_label = tk.Label(win, text="Total Price: 0.00", bg="#f5f5f5", font=("Arial", 12, "bold"))
        total_price_label.pack(pady=8)

        # Auto-calc total price
        def update_total(*args):
            worship_name = worship_cb.get()
            try:
                num = int(num_tickets.get() or 0)
            except ValueError:
                num = 0

            rate = next((wt[2] for wt in worship_types if wt[1] == worship_name), 0.0)
            total_price_label.config(text=f"Total Price: {num * rate:.2f}")

        worship_cb.bind("<<ComboboxSelected>>", update_total)
        num_tickets.bind("<KeyRelease>", update_total)

        # Submit
        def submit():
            name = devotee_name.get().strip()
            contact_value = contact.get().strip()
            worship = worship_cb.get().strip()

            try:
                num = int(num_tickets.get() or 1)
            except:
                num = 1

            ttype = transaction_type.get().strip()

            if not (name and worship):
                messagebox.showerror("Error", "Devotee name and worship type required")
                return

            devotee_id = add_devotee(name, contact_value)
            rate = next((wt[2] for wt in worship_types if wt[1] == worship), 0.0)
            total_amount = num * rate

            ticket_id = issue_pooja_ticket(
                staff_id, devotee_id, worship,
                date.today().isoformat(), num, total_amount, ttype
            )

            messagebox.showinfo("Success", f"Ticket #{ticket_id} issued!\nTotal: {total_amount:.2f}")
            generate_ticket_pdf(ticket_id)

            win.destroy()

        tk.Button(win, text="Submit Ticket", command=submit, bg="#81c784").pack(pady=10)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # ---- Book Stage ----
    def book_stage_ui():
        win = tk.Toplevel(root)
        win.title("Book Stage")
        win.geometry("520x480")
        win.configure(bg="#f5f5f5")

        tk.Label(win, text="Select Stage:", bg="#f5f5f5").pack(pady=6)
        stages = get_all_stages()
        stage_cb = ttk.Combobox(win, values=[f"{s[1]} ({s[2] or ''})" for s in stages])
        stage_cb.pack(fill="x", padx=10)

        tk.Label(win, text="Event Name:", bg="#f5f5f5").pack(pady=6)
        event_entry = tk.Entry(win); event_entry.pack(fill="x", padx=10)

        tk.Label(win, text="Booking Date (YYYY-MM-DD):", bg="#f5f5f5").pack(pady=6)
        date_entry = tk.Entry(win); date_entry.pack(fill="x", padx=10)

        tk.Label(win, text="Start Time (HH:MM):", bg="#f5f5f5").pack(pady=6)
        start_entry = tk.Entry(win); start_entry.pack(fill="x", padx=10)

        tk.Label(win, text="End Time (HH:MM):", bg="#f5f5f5").pack(pady=6)
        end_entry = tk.Entry(win); end_entry.pack(fill="x", padx=10)

        def submit():
            selected = stage_cb.get()
            if not selected:
                messagebox.showerror("Error", "Select a stage")
                return

            stage_name = selected.split(" (")[0]
            stage_obj = next((s for s in stages if s[1] == stage_name), None)

            if not stage_obj:
                messagebox.showerror("Error", "Stage not found")
                return

            stage_id = stage_obj[0]
            stage_location = stage_obj[2]

            event_name = event_entry.get().strip()
            booking_date = date_entry.get().strip()
            start_time = start_entry.get().strip()
            end_time = end_entry.get().strip()

            if not (event_name and booking_date and start_time and end_time):
                messagebox.showerror("Error", "All fields are required")
                return

            book_stage(stage_id, staff_id, event_name, booking_date, start_time, end_time, status="confirmed")

            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT StageBookingID FROM StageBookings ORDER BY StageBookingID DESC LIMIT 1")
            bid_row = cur.fetchone(); conn.close()

            bid = bid_row[0] if bid_row else None

            messagebox.showinfo("Success", f"Stage '{stage_name}' booked!")

            if bid:
                generate_stage_booking_receipt(
                    bid, stage_name, stage_location, event_name,
                    booking_date, start_time, end_time, staff_name
                )

            win.destroy()

        tk.Button(win, text="Book Stage", command=submit, bg="#81c784").pack(pady=12)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # ---- My Stage Bookings ----
    def view_stage_bookings():
        win = tk.Toplevel(root)
        win.title("Your Stage Bookings")
        win.geometry("820x420")
        win.configure(bg="#fafafa")

        tree = ttk.Treeview(win, columns=("BookingID","Event","Date","Start","End","Status"), show="headings")

        for col in ("BookingID","Event","Date","Start","End","Status"):
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        rows = get_stage_bookings_by_employee(staff_id)
        for r in rows:
            tree.insert("", "end", values=r)

        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # ---- Record Donation ----
    def record_donation_ui():
        win = tk.Toplevel(root)
        win.title("Record Donation")
        win.geometry("420x320")
        win.configure(bg="#f5f5f5")

        tk.Label(win, text="Donor Name:", bg="#f5f5f5").pack(pady=6)
        donor_name = tk.Entry(win); donor_name.pack(fill="x", padx=10)

        tk.Label(win, text="Amount:", bg="#f5f5f5").pack(pady=6)
        amount = tk.Entry(win); amount.pack(fill="x", padx=10)

        tk.Label(win, text="Donation Type:", bg="#f5f5f5").pack(pady=6)
        dtype = tk.Entry(win); dtype.pack(fill="x", padx=10)

        def submit():
            dname = donor_name.get().strip() or "Anonymous"
            try:
                amt = float(amount.get())
            except:
                messagebox.showerror("Error", "Invalid amount")
                return

            donor_id = add_donor(dname)

            record_donation(
                staff_id, donor_id, date.today().isoformat(),
                dtype.get().strip(), amt
            )

            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT DonationsID FROM Donations ORDER BY DonationsID DESC LIMIT 1")
            row = cur.fetchone(); conn.close()

            did = row[0] if row else None

            messagebox.showinfo("Success", "Donation recorded")

            if did:
                generate_donation_receipt(did, dname, dtype.get().strip(), amt, date.today().isoformat(), staff_name)

            win.destroy()

        tk.Button(win, text="Record Donation", command=submit, bg="#81c784").pack(pady=10)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # ---- My Tickets ----
    def view_tickets():
        win = tk.Toplevel(root)
        win.title("Issued Tickets")
        win.geometry("700x420")
        win.configure(bg="#fafafa")

        tree = ttk.Treeview(win, columns=("TicketID","Worship","Date","Tickets","Total"), show="headings")

        for col in ("TicketID","Worship","Date","Tickets","Total"):
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        rows = get_issued_tickets_by_employee(staff_id)

        for t in rows:
            tid, worship, dstr, num, amt = t

            if not amt or amt == 0:
                amt = (num or 0) * (get_rate(worship) or 0.0)

            tree.insert("", "end", values=(tid, worship, dstr, num, f"{amt:.2f}"))

        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # ---- Festival Calendar ----
    def view_festival():
        win = tk.Toplevel(root)
        win.title("Festival Calendar")
        win.geometry("600x450")
        win.configure(bg="#f5f5f5")

        tree = ttk.Treeview(win, columns=("ID","Name","Date","Notes"), show="headings")

        for col in ("ID","Name","Date","Notes"):
            tree.heading(col, text=col)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for fest in get_all_festivals():
            tree.insert("", "end", values=fest)

        def print_month():
            month = simpledialog.askinteger("Month", "Enter month (1-12)")
            year = simpledialog.askinteger("Year", "Enter year (e.g., 2025)")

            if not (month and year):
                messagebox.showerror("Error", "Month and year required")
                return

            monthly = get_festivals_by_month(year, month)
            generate_festival_calendar_pdf(monthly, year, month)

            messagebox.showinfo("Printed", "Festival calendar PDF generated.")

        tk.Button(win, text="Print Monthly Calendar", command=print_month, bg="#4fc3f7").pack(pady=6)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # ---- Last Receipt ----
    def view_last_receipt():
        last = get_last_ticket_by_employee(staff_id)
        if not last:
            messagebox.showinfo("Info", "No recent ticket found")
            return
        generate_ticket_pdf(last[0])

    # ---- Sign Out ----
    def signout():
        for w in root.winfo_children():
            w.destroy()

        from db_ui import LoginUI
        LoginUI(root)

    #stage slots
    

    def book_stage_ui():
        win = tk.Toplevel(root)
        win.title("Book Stage")
        win.geometry("520x520")
        win.configure(bg="#f5f5f5")

        tk.Label(win, text="Select Booking Date (YYYY-MM-DD):", bg="#f5f5f5").pack(pady=4)
        date_entry = tk.Entry(win); date_entry.pack(fill="x", padx=10)

        tk.Label(win, text="Start Time (HH:MM):", bg="#f5f5f5").pack(pady=4)
        start_entry = tk.Entry(win); start_entry.pack(fill="x", padx=10)

        tk.Label(win, text="End Time (HH:MM):", bg="#f5f5f5").pack(pady=4)
        end_entry = tk.Entry(win); end_entry.pack(fill="x", padx=10)

        tk.Label(win, text="Select Stage:", bg="#f5f5f5").pack(pady=4)
        stages = get_all_stages()
        stage_cb = ttk.Combobox(win, values=[s[1] for s in stages])
        stage_cb.pack(fill="x", padx=10)

        tk.Label(win, text="Event Name:", bg="#f5f5f5").pack(pady=4)
        event_entry = tk.Entry(win); event_entry.pack(fill="x", padx=10)

        status_label = tk.Label(win, text="", bg="#f5f5f5", fg="red")
        status_label.pack(pady=4)

        def check_availability(*args):
            selected_stage = stage_cb.get()
            selected_date = date_entry.get()
            start = start_entry.get()
            end = end_entry.get()
            if not (selected_stage and selected_date and start and end):
                status_label.config(text="")
                return
            stage_obj = next((s for s in stages if s[1] == selected_stage), None)
            if stage_obj:
                available = is_stage_available(stage_obj[0], selected_date, start, end)
                status_label.config(
                    text=f"{selected_stage} is {'AVAILABLE' if available else 'OCCUPIED'}"
                )

        stage_cb.bind("<<ComboboxSelected>>", check_availability)
        date_entry.bind("<KeyRelease>", check_availability)
        start_entry.bind("<KeyRelease>", check_availability)
        end_entry.bind("<KeyRelease>", check_availability)

        def submit():
            selected_stage = stage_cb.get()
            stage_obj = next((s for s in stages if s[1] == selected_stage), None)
            if not stage_obj:
                messagebox.showerror("Error", "Select a stage")
                return

            selected_date = date_entry.get()
            start = start_entry.get()
            end = end_entry.get()
            event_name = event_entry.get().strip()

            if not is_stage_available(stage_obj[0], selected_date, start, end):
                messagebox.showerror("Error", "Stage is occupied for this slot")
                return

            try:
                book_stage(stage_obj[0], staff_id, event_name, selected_date, start, end, status='confirmed')
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

            messagebox.showinfo("Success", f"Stage '{selected_stage}' booked!")
            win.destroy()

        tk.Button(win, text="Book Stage", command=submit, bg="#81c784").pack(pady=12)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)
    
    
    # ======================================================
    #                    DASHBOARD CARDS
    # ======================================================
    cards = [
        ("🎟️", "Issue Tickets", "Create & print tickets", issue_ticket_ui),
        ("🏟️", "Book Stage", "Reserve stages & print receipt", book_stage_ui),
        ("📅", "My Bookings", "Your bookings", view_stage_bookings),
        ("💰", "Record Donation", "Log & receipt donation", record_donation_ui),
        ("📋", "My Tickets", "Tickets issued by you", view_tickets),
        ("🧾", "Last Receipt", "Open most recent receipt", view_last_receipt),
        ("📅", "Festival Calendar", "View & print", view_festival),
        ("📊", "Stage Dashboard", "View availability", book_stage_ui),
        ("🔒", "Sign Out", "Return to login", signout),
    ]

    # Grid layout
    r, c = 0, 0
    for icon, title, subtitle, cmd in cards:
        card = make_card(grid_frame, icon, title, subtitle, cmd, bg="white")
        card.config(width=340, height=140)
        card.grid(row=r, column=c, padx=12, pady=12, sticky="nsew")

        c += 1
        if c >= cols:
            c = 0
            r += 1

    # ---------------- Footer Sign Out ----------------
    footer = tk.Frame(root, bg="#f0f8ff")
    footer.pack(fill="x", pady=8)

    tk.Button(
        footer, text="Sign Out", command=signout,
        bg="#ef5350", fg="white", font=("Arial", 12, "bold")
    ).pack(side="right", padx=12, pady=8)