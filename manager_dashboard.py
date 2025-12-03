import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from temple_db import (
    get_all_worship_types, add_worship_type, update_worship_rate,
    add_employee, create_employee_login, get_all_employees,
    delete_employee_by_id, get_stage_bookings, get_all_donations,
    get_issued_tickets_by_employee, get_all_stages, add_stage, update_stage, delete_stage,
    get_connection, get_all_festivals, add_festival, update_festival, delete_festival,get_festivals_by_month,get_stage_availability_for_date
)
from pdf_utils import generate_ticket_pdf, generate_donation_receipt, generate_stage_booking_receipt, generate_festival_calendar_pdf, get_rate
from datetime import date
import os
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import csv
from tkinter import filedialog
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates

#scroll framework
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

# manager_dashboard.py

def make_card(parent, icon, title, subtitle, command, bg="#ffffff"):
    card = tk.Frame(parent, bg=bg, bd=1, relief="raised", padx=12, pady=12)
    card.grid_propagate(False)
    card.columnconfigure(0, weight=1)
    icon_lbl = tk.Label(card, text=icon, font=("Arial", 22), bg=bg)
    icon_lbl.grid(row=0, column=0, sticky="n")
    title_lbl = tk.Label(card, text=title, font=("Arial", 12, "bold"), bg=bg)
    title_lbl.grid(row=1, column=0, pady=(8,0))
    sub_lbl = tk.Label(card, text=subtitle, font=("Arial", 9), bg=bg, fg="#555")
    sub_lbl.grid(row=2, column=0, pady=(4,0))
    btn = tk.Button(card, text="Open", command=command, bg="#1976d2", fg="white")
    btn.grid(row=3, column=0, pady=(10,0), sticky="ew")
    return card

def manager_dashboard(root, username):
    for w in root.winfo_children(): w.destroy()

    root.title("Temple Management System - Manager")
    try:
        root.state('zoomed')
    except:
        root.geometry("1200x700")
    root.configure(bg="#f0f8ff")

    # Top header area
    header = tk.Frame(root, bg="#f0f8ff")
    header.pack(fill="x", padx=12, pady=10)
    profile = tk.Label(header, text=f"{username} • Manager", font=("Arial", 14, "bold"), bg="#f0f8ff")
    profile.pack(side="left", padx=12)
    exit_btn = tk.Button(header, text="X", bg="#ef5350", fg="white", command=lambda: root.destroy())
    exit_btn.pack(side="right", padx=12)

    # Grid container
    scroll_area = ScrollableFrame(root)
    scroll_area.pack(fill="both", expand=True, padx=20, pady=8)

    grid_frame = tk.Frame(scroll_area.scrollable_frame, bg="#f0f8ff")
    grid_frame.pack(fill="both", expand=True)

    # grid: 3 columns
    cols = 3
    for c in range(cols):
        grid_frame.columnconfigure(c, weight=1, uniform="c")

    # --------------- features as cards ---------------
    # Manage Worship Types
    def manage_worship():
        
        win = tk.Toplevel(root)
        win.title("Manage Worship Types"); win.geometry("480x420"); win.configure(bg="#f5f5f5")
        tree = ttk.Treeview(win, columns=("ID", "Name", "Rate"), show="headings")
        for col in ("ID", "Name", "Rate"): tree.heading(col, text=col); tree.column(col, width=140)
        tree.pack(fill="both", expand=True, padx=10, pady=6)
        def refresh():
            for r in tree.get_children(): tree.delete(r)
            for wt in get_all_worship_types(): tree.insert("", "end", values=wt)
        refresh()
        tk.Label(win, text="Name:", bg="#f5f5f5").pack(); name = tk.Entry(win); name.pack(fill="x", padx=10)
        tk.Label(win, text="Rate:", bg="#f5f5f5").pack(); rate = tk.Entry(win); rate.pack(fill="x", padx=10)
        def add_new():
            n = name.get().strip()
            try: r = float(rate.get() or 0)
            except: messagebox.showerror("Error","Invalid rate"); return
            if not n: messagebox.showerror("Error","Name required"); return
            add_worship_type(n, r); refresh(); name.delete(0, tk.END); rate.delete(0, tk.END)
            messagebox.showinfo("Success", f"Worship '{n}' added.")
        def update_rate_btn():
            sel = tree.selection()
            if not sel: messagebox.showerror("Error","Select type"); return
            row = tree.item(sel[0])['values']; wid = row[0]
            try: newr = float(rate.get() or row[2])
            except: messagebox.showerror("Error","Invalid rate"); return
            update_worship_rate(wid, newr); refresh(); messagebox.showinfo("Success","Rate updated")
        tk.Button(win, text="Add Worship", command=add_new, bg="#81c784").pack(pady=6)
        tk.Button(win, text="Update Selected Rate", command=update_rate_btn, bg="#ffd54f").pack(pady=6)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # Manage Employees
    def manage_employees():
        win = tk.Toplevel(root); win.title("Manage Employees"); win.geometry("800x520"); win.configure(bg="#f5f5f5")
        tree = ttk.Treeview(win, columns=("ID", "Name", "Role", "Email"), show="headings")
        for col in ("ID","Name","Role","Email"): tree.heading(col, text=col); tree.column(col, width=150)
        tree.pack(fill="both", expand=True, padx=8, pady=6)
        def refresh():
            for r in tree.get_children(): tree.delete(r)
            for emp in get_all_employees(): tree.insert("", "end", values=emp)
        refresh()
        form = tk.Frame(win, bg="#f5f5f5"); form.pack(fill="x", padx=12, pady=6)
        tk.Label(form, text="Name:", bg="#f5f5f5").grid(row=0, column=0, sticky="w"); name = tk.Entry(form); name.grid(row=0,column=1,padx=6,pady=2)
        tk.Label(form, text="Role (Staff/Manager):", bg="#f5f5f5").grid(row=1, column=0, sticky="w"); role = tk.Entry(form); role.grid(row=1,column=1,padx=6,pady=2)
        tk.Label(form, text="Email:", bg="#f5f5f5").grid(row=2, column=0, sticky="w"); email = tk.Entry(form); email.grid(row=2,column=1,padx=6,pady=2)
        tk.Label(form, text="Username:", bg="#f5f5f5").grid(row=3, column=0, sticky="w"); username = tk.Entry(form); username.grid(row=3,column=1,padx=6,pady=2)
        tk.Label(form, text="Password:", bg="#f5f5f5").grid(row=4, column=0, sticky="w"); password = tk.Entry(form, show="*"); password.grid(row=4,column=1,padx=6,pady=2)
        def add_new():
            n = name.get().strip(); r = role.get().strip() or "Staff"; e = email.get().strip(); u = username.get().strip(); p = password.get()
            if not (n and u and p): messagebox.showerror("Error","Name, username and password required"); return
            emp_id = add_employee(n, r, "", e); create_employee_login(emp_id, u, p, r)
            refresh(); name.delete(0,tk.END); role.delete(0,tk.END); email.delete(0,tk.END); username.delete(0,tk.END); password.delete(0,tk.END)
            messagebox.showinfo("Success", f"Employee '{n}' added.")
        def delete_selected():
            sel = tree.selection()
            if not sel: messagebox.showerror("Error","Select an employee"); return
            row = tree.item(sel[0])['values']
            if messagebox.askyesno("Confirm", f"Delete {row[1]}?"):
                delete_employee_by_id(row[0]); refresh(); messagebox.showinfo("Deleted", f"{row[1]} deleted.")
        tk.Button(win, text="Add Employee", command=add_new, bg="#81c784").pack(pady=6)
        tk.Button(win, text="Delete Selected Employee", command=delete_selected, bg="#ef5350").pack(pady=6)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # Manage Stages
    def manage_stages():
        win = tk.Toplevel(root); win.title("Manage Stages"); win.geometry("760x520"); win.configure(bg="#f5f5f5")
        tree = ttk.Treeview(win, columns=("ID","StageName","Location","Capacity","Availability"), show="headings")
        for col in ("ID","StageName","Location","Capacity","Availability"): tree.heading(col, text=col); tree.column(col,width=120)
        tree.pack(fill="both", expand=True, padx=8, pady=6)
        def refresh():
            for r in tree.get_children(): tree.delete(r)
            for st in get_all_stages(): tree.insert("", "end", values=st)
        refresh()
        form = tk.Frame(win, bg="#f5f5f5"); form.pack(fill="x", padx=12, pady=6)
        tk.Label(form, text="Stage Name:", bg="#f5f5f5").grid(row=0,column=0,sticky="w"); sname = tk.Entry(form); sname.grid(row=0,column=1,padx=6,pady=2)
        tk.Label(form, text="Location:", bg="#f5f5f5").grid(row=1,column=0,sticky="w"); sloc = tk.Entry(form); sloc.grid(row=1,column=1,padx=6,pady=2)
        tk.Label(form, text="Capacity:", bg="#f5f5f5").grid(row=2,column=0,sticky="w"); scap = tk.Entry(form); scap.grid(row=2,column=1,padx=6,pady=2)
        tk.Label(form, text="Availability:", bg="#f5f5f5").grid(row=3,column=0,sticky="w"); savail = tk.Entry(form); savail.grid(row=3,column=1,padx=6,pady=2)
        def add_new():
            add_stage(sname.get().strip() or "Stage", sloc.get().strip(), int(scap.get() or 0), savail.get().strip() or "available"); refresh(); messagebox.showinfo("Success","Stage added.")
        def update_selected():
            sel = tree.selection()
            if not sel: messagebox.showerror("Error","Select a stage"); return
            row = tree.item(sel[0])['values']; sid = row[0]
            update_stage(sid, sname.get() or row[1], sloc.get() or row[2], int(scap.get() or row[3]), savail.get() or row[4]); refresh(); messagebox.showinfo("Success","Stage updated.")
        def delete_selected():
            sel = tree.selection()
            if not sel: messagebox.showerror("Error","Select a stage"); return
            row = tree.item(sel[0])['values']
            if messagebox.askyesno("Confirm", f"Delete stage '{row[1]}'?"):
                delete_stage(row[0]); refresh(); messagebox.showinfo("Deleted","Stage deleted.")
        tk.Button(win, text="Add Stage", command=add_new, bg="#81c784").pack(pady=6)
        tk.Button(win, text="Update Selected", command=update_selected, bg="#ffd54f").pack(pady=6)
        tk.Button(win, text="Delete Selected", command=delete_selected, bg="#ef5350").pack(pady=6)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # View Stage Bookings
    def view_stage_bookings():
        win = tk.Toplevel(root); win.title("Stage Bookings"); win.geometry("820x480"); win.configure(bg="#fafafa")
        tree = ttk.Treeview(win, columns=("BookingID","StageID","EmployeeID","Event","Date","Start","End","Status"), show="headings")
        for col in ("BookingID","StageID","EmployeeID","Event","Date","Start","End","Status"): tree.heading(col, text=col); tree.column(col,width=100)
        tree.pack(fill="both", expand=True, padx=8, pady=6)
        rows = get_stage_bookings()
        for row in rows: tree.insert("", "end", values=row)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)
        
    def manage_stage_bookings():
        win = tk.Toplevel(root)
        win.title("Stage Availability & Bookings")
        win.geometry("900x500")
        win.configure(bg="#f5f5f5")

        tk.Label(win, text="Select Date (YYYY-MM-DD):", bg="#f5f5f5").pack(pady=6)
        date_entry = tk.Entry(win)
        date_entry.pack(fill="x", padx=12)

        tree = ttk.Treeview(win, columns=("StageID","StageName","Location","Capacity","Availability"), show="headings")
        for col in ("StageID","StageName","Location","Capacity","Availability"):
            tree.heading(col, text=col)
            tree.column(col, width=140)
        tree.pack(fill="both", expand=True, padx=12, pady=8)

        def load_availability():
            selected_date = date_entry.get().strip()
            if not selected_date:
                messagebox.showerror("Error", "Enter a date")
                return
            for r in tree.get_children(): tree.delete(r)
            stages = get_stage_availability_for_date(selected_date)
            for s in stages: tree.insert("", "end", values=s)

        tk.Button(win, text="Check Availability", command=load_availability, bg="#4fc3f7").pack(pady=6)

        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # View Issued Tickets
    def view_tickets():
        win = tk.Toplevel(root); win.title("All Issued Tickets"); win.geometry("900x520"); win.configure(bg="#fafafa")
        tree = ttk.Treeview(win, columns=("Employee","TicketID","Worship","Date","Tickets","Total"), show="headings")
        for col in ("Employee","TicketID","Worship","Date","Tickets","Total"): tree.heading(col, text=col); tree.column(col,width=140)
        tree.pack(fill="both", expand=True, padx=8, pady=6)
        for emp in get_all_employees():
            emp_id, emp_name = emp[0], emp[1]
            tickets = get_issued_tickets_by_employee(emp_id)
            for t in tickets:
                if len(t) >= 5:
                    tid, worship, dstr, num, amt = t[0], t[1], t[2], t[3], t[4]
                    if not amt or amt == 0:
                        amt = (num or 0) * (get_rate(worship) or 0.0)
                    tree.insert("", "end", values=(emp_name, tid, worship, dstr, num, f"{amt:.2f}"))
                else:
                    tree.insert("", "end", values=(emp_name,) + tuple(t))
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # View Donations
    def view_donations():
        win = tk.Toplevel(root); win.title("Donations"); win.geometry("900x520"); win.configure(bg="#fafafa")
        tree = ttk.Treeview(win, columns=("Employee","Donor","Date","Type","Amount","DonationID"), show="headings")
        for col in ("Employee","Donor","Date","Type","Amount","DonationID"): tree.heading(col, text=col); tree.column(col,width=140)
        tree.pack(fill="both", expand=True, padx=8, pady=6)
        for row in get_all_donations():
            tree.insert("", "end", values=row)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # Manage Festival Calendar
    def manage_festival():
        win = tk.Toplevel(root); win.title("Festival Calendar"); win.geometry("700x520"); win.configure(bg="#f5f5f5")
        tree = ttk.Treeview(win, columns=("ID","Name","Date","Notes"), show="headings")
        for col in ("ID","Name","Date","Notes"): tree.heading(col, text=col); tree.column(col, width=150)
        tree.pack(fill="both", expand=True, padx=8, pady=6)
        def refresh():
            for r in tree.get_children(): tree.delete(r)
            for f in get_all_festivals(): tree.insert("", "end", values=f)
        refresh()
        frame = tk.Frame(win, bg="#f5f5f5"); frame.pack(fill="x", padx=8, pady=6)
        tk.Label(frame, text="Name:", bg="#f5f5f5").grid(row=0,column=0); name_e = tk.Entry(frame); name_e.grid(row=0,column=1,padx=6)
        tk.Label(frame, text="Date (YYYY-MM-DD):", bg="#f5f5f5").grid(row=1,column=0); date_e = tk.Entry(frame); date_e.grid(row=1,column=1,padx=6)
        tk.Label(frame, text="Notes:", bg="#f5f5f5").grid(row=2,column=0); notes_e = tk.Entry(frame); notes_e.grid(row=2,column=1,padx=6)
        def addf(): add_festival(name_e.get(), date_e.get(), notes_e.get()); refresh()
        def updf(): 
            sel = tree.selection()
            if not sel: return
            row = tree.item(sel[0])['values']
            update_festival(row[0], name_e.get() or row[1], date_e.get() or row[2], notes_e.get() or row[3]); refresh()
        def delf():
            sel = tree.selection()
            if not sel: return
            row = tree.item(sel[0])['values']; delete_festival(row[0]); refresh()
        tk.Button(win, text="Add", command=addf, bg="#81c784").pack(pady=4)
        tk.Button(win, text="Update", command=updf, bg="#ffd54f").pack(pady=4)
        tk.Button(win, text="Delete", command=delf, bg="#ef5350").pack(pady=4)
        tk.Button(win, text="Back", command=win.destroy, bg="#e0e0e0").pack(side="bottom", pady=8)

    # Printing CSV helpers
    def export_to_csv(data, headers, default_filename="export.csv"):
        if not data:
            messagebox.showinfo("Info", "No data to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_filename,
                                            filetypes=[("CSV files", "*.csv")])
        if not path: return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        messagebox.showinfo("Exported", f"CSV saved to {path}")

    def export_tickets():
        data = []
        for emp in get_all_employees():
            emp_id, emp_name = emp[0], emp[1]
            tickets = get_issued_tickets_by_employee(emp_id)
            for t in tickets:
                tid, worship, dstr, num, amt = t
                if not amt or amt == 0:
                    amt = (num or 0) * (get_rate(worship) or 0.0)
                data.append((emp_name, tid, worship, dstr, num, f"{amt:.2f}"))
        export_to_csv(data, ["Employee","TicketID","Worship","Date","Tickets","Total"], "tickets.csv")

    def export_stage_bookings():
        rows = get_stage_bookings()
        data = []
        conn = get_connection(); cur = conn.cursor()
        for r in rows:
            booking_id, stage_id, emp_id, event_name, bdate, stime, etime, status = r
            cur.execute("SELECT StageName, Location FROM Stage WHERE StageID=?", (stage_id,))
            srow = cur.fetchone()
            stage_name = srow[0] if srow else "Unknown"
            stage_location = srow[1] if srow and len(srow)>1 else ""
            data.append((booking_id, stage_name, stage_location, emp_id, event_name, bdate, stime, etime, status))
        conn.close()
        export_to_csv(data, ["BookingID","StageName","Location","EmployeeID","EventName","Date","StartTime","EndTime","Status"], "stage_bookings.csv")

    def export_festivals():
        data = get_all_festivals()
        export_to_csv(data, ["FestivalID","FestivalName","FestivalDate","Notes"], "festivals.csv")

    def export_donations():
        data = get_all_donations()
        export_to_csv(data, ["Employee","Donor","Date","DonationType","Amount","DonationID"], "donations.csv")
        
    

    def open_analytics_window():
        win = tk.Toplevel(root)
        win.title("Analytics & Reports")
        try:
            win.state('zoomed')
        except:
            win.geometry("1000x700")
        win.configure(bg="#f5f5f5")

        # Top: filters frame
        filt_frame = tk.Frame(win, bg="#f5f5f5", pady=8)
        filt_frame.pack(fill="x", padx=12)

        # Year dropdown (last 5 years)
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year-4, current_year+1)]
        tk.Label(filt_frame, text="Year:", bg="#f5f5f5").pack(side="left", padx=(4,2))
        year_var = tk.StringVar(value=str(current_year))
        year_cb = ttk.Combobox(filt_frame, values=years, textvariable=year_var, width=8, state="readonly")
        year_cb.pack(side="left", padx=6)

        # Month dropdown (All + 1..12)
        months = ["All"] + [datetime(2000, m, 1).strftime("%B") for m in range(1,13)]
        tk.Label(filt_frame, text="Month:", bg="#f5f5f5").pack(side="left", padx=(12,2))
        month_var = tk.StringVar(value="All")
        month_cb = ttk.Combobox(filt_frame, values=months, textvariable=month_var, width=12, state="readonly")
        month_cb.pack(side="left", padx=6)

        # Metric selector
        metrics = ["Monthly Budget", "Tickets", "Staff Activity", "Bookings"]
        tk.Label(filt_frame, text="Metric:", bg="#f5f5f5").pack(side="left", padx=(12,2))
        metric_var = tk.StringVar(value=metrics[0])
        metric_cb = ttk.Combobox(filt_frame, values=metrics, textvariable=metric_var, width=18, state="readonly")
        metric_cb.pack(side="left", padx=6)

        # Buttons: Generate, Export CSV, Export PDF, Close
        btn_frame = tk.Frame(filt_frame, bg="#f5f5f5")
        btn_frame.pack(side="right")
        generate_btn = tk.Button(btn_frame, text="Generate", bg="#1976d2", fg="white", width=12)
        generate_btn.grid(row=0, column=0, padx=6)
        export_csv_btn = tk.Button(btn_frame, text="Export CSV", bg="#4caf50", fg="white", width=12)
        export_csv_btn.grid(row=0, column=1, padx=6)
        export_pdf_btn = tk.Button(btn_frame, text="Export PDF", bg="#6a1b9a", fg="white", width=12)
        export_pdf_btn.grid(row=0, column=2, padx=6)
        tk.Button(btn_frame, text="Close", command=win.destroy, bg="#ef5350", fg="white", width=10).grid(row=0, column=3, padx=6)

        # Middle: charts area (two plots stacked)
        chart_frame = tk.Frame(win, bg="#f5f5f5")
        chart_frame.pack(fill="both", expand=True, padx=12, pady=8)

      
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            has_tkagg = True
        except Exception:
            has_tkagg = False

        fig_main = plt.Figure(figsize=(9,4))
        ax_bar = fig_main.add_subplot(121)
        ax_line = fig_main.add_subplot(122)

        canvas_widget = None
        if has_tkagg:
            canvas = FigureCanvasTkAgg(fig_main, master=chart_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill="both", expand=True)
        else:
            
            placeholder = tk.Label(chart_frame, text="Charts will open in external windows (tkagg not available).", bg="#f5f5f5")
            placeholder.pack(fill="both", expand=True)

        # Data store for export
        last_table_rows = []
        last_table_headers = []

        def compute_month_key(date_str):
            
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
            except:
                return date_str

        def aggregate_by_month_year(rows, date_index, value_index):
            """
            rows: iterable of DB rows
            date_index: position of date string in row
            value_index: position of numeric value to sum (or None for count)
            returns dict key->value where key is "YYYY-MM"
            """
            agg = defaultdict(float)
            for r in rows:
                dstr = r[date_index]
                key = compute_month_key(dstr)
                if value_index is None:
                    agg[key] += 1
                else:
                    try:
                        agg[key] += float(r[value_index] or 0)
                    except:
                        agg[key] += 0
            return agg

        def build_time_series_from_agg(agg, selected_year, selected_month):
            """
            Returns (x_labels, y_vals) filtered by year (month ignored if selected_month='All').
            Always include all 12 months for line graph.
            """
            if selected_month != "All":
                
                items = sorted(agg.items())
                labels = []
                vals = []
                for k, v in items:
                    y, m = k.split("-")
                    if str(y) != str(selected_year):
                        continue
                    mon_num = datetime.strptime(selected_month, "%B").month
                    if int(m) != mon_num:
                        continue
                    labels.append(k)
                    vals.append(v)
                return labels, vals
            else:
                # All months: 1..12
                labels = []
                vals = []
                for m in range(1, 13):
                    key = f"{selected_year}-{m:02d}"
                    labels.append(key)
                    vals.append(agg.get(key, 0))  # 0 if no data for month
                return labels, vals
        
        def generate_report():
            nonlocal last_table_rows, last_table_headers
            sel_year = year_var.get()
            sel_month = month_var.get()
            metric = metric_var.get()

            # Reset plots
            ax_bar.clear()
            ax_line.clear()
            last_table_rows = []
            last_table_headers = []

            if metric == "Monthly Budget":
                # Treat donations as budget/income
                donations = get_all_donations()  
              
                agg = aggregate_by_month_year(donations, 2, 4)
                labels, vals = build_time_series_from_agg(agg, sel_year, sel_month)
                last_table_headers = ["Month", "DonationsTotal"]
                last_table_rows = list(zip(labels, [f"{v:.2f}" for v in vals]))

                if not labels:
                    messagebox.showinfo("Info", "No data for selected filters."); return

                # bar and line
                ax_bar.bar(labels, vals)
                ax_bar.set_title("Monthly Donations (Budget)")
                ax_bar.set_xticklabels(labels, rotation=45, ha="right")
                ax_bar.set_ylabel("Amount")

                ax_line.plot(labels, vals, marker="o")
                ax_line.set_title("Trend")
                ax_line.set_xticklabels(labels, rotation=45, ha="right")

            elif metric == "Tickets":
                
                agg = defaultdict(float)
                for emp in get_all_employees():
                    emp_id = emp[0]
                    tickets = get_issued_tickets_by_employee(emp_id)  
                    for t in tickets:
                        try:
                            dstr = t[2]
                            amt = float(t[4] or 0)
                            key = compute_month_key(dstr)
                            agg[key] += amt
                        except:
                            continue
                labels, vals = build_time_series_from_agg(agg, sel_year, sel_month)
                last_table_headers = ["Month", "TicketRevenue"]
                last_table_rows = list(zip(labels, [f"{v:.2f}" for v in vals]))

                if not labels:
                    messagebox.showinfo("Info", "No ticket data for selected filters."); return

                ax_bar.bar(labels, vals)
                ax_bar.set_title("Monthly Ticket Revenue")
                ax_bar.set_xticklabels(labels, rotation=45, ha="right")
                ax_bar.set_ylabel("Revenue")

                ax_line.plot(labels, vals, marker="o")
                ax_line.set_title("Ticket Revenue Trend")
                ax_line.set_xticklabels(labels, rotation=45, ha="right")

            # Get all employees
            elif metric == "Staff Activity":
                all_emps = get_all_employees()  
                staff_counts = {emp[1]: 0 for emp in all_emps}  

                for emp in all_emps:
                    emp_id, emp_name = emp[0], emp[1]
                    tickets = get_issued_tickets_by_employee(emp_id)
                    for t in tickets:
                        try:
                            dstr = t[2]
                            if sel_year and dstr[:4] != sel_year:
                                continue
                            if sel_month != "All":
                                mon_num = datetime.strptime(sel_month, "%B").month
                                if int(dstr[5:7]) != mon_num:
                                    continue
                            staff_counts[emp_name] += int(t[3] or 1)
                        except:
                            continue

                # Now staff_counts has all staff, 0 if no activity
                items = sorted(staff_counts.items(), key=lambda x: x[0])  
                last_table_headers = ["Staff", "TicketsIssued"]
                last_table_rows = [(k, str(v)) for k, v in items]

                # Plot
                names = [it[0] for it in items]
                counts = [it[1] for it in items]
                ax_bar.clear()
                ax_line.clear()
                ax_bar.bar(names, counts)
                ax_bar.set_title("Staff Tickets Issued")
                ax_bar.set_xticklabels(names, rotation=45, ha="right")
                ax_bar.set_ylabel("Tickets Issued")

                ax_line.plot(names, counts, marker="o")
                ax_line.set_title("Staff Activity Trend")
                ax_line.set_xticklabels(names, rotation=45, ha="right")

                if not items:
                    messagebox.showinfo("Info", "No staff activity for selected filters."); return

                names = [it[0] for it in items]
                counts = [it[1] for it in items]
                ax_bar.bar(names, counts)
                ax_bar.set_title("Staff Tickets Issued")
                ax_bar.set_xticklabels(names, rotation=45, ha="right")
                ax_bar.set_ylabel("Tickets Issued")

                ax_line.plot(names, counts, marker="o")
                ax_line.set_title("Staff Activity Trend")
                ax_line.set_xticklabels(names, rotation=45, ha="right")

            elif metric == "Bookings":
                # Monthly count of stage bookings
                bookings = get_stage_bookings()
                
                agg = defaultdict(int)
                for b in bookings:
                    try:
                        dstr = b[4]
                        key = compute_month_key(dstr)
                        agg[key] += 1
                    except:
                        continue
                labels, vals = build_time_series_from_agg(agg, sel_year, sel_month)
                last_table_headers = ["Month", "BookingsCount"]
                last_table_rows = list(zip(labels, [str(v) for v in vals]))

                if not labels:
                    messagebox.showinfo("Info", "No bookings for selected filters."); return

                ax_bar.bar(labels, vals)
                ax_bar.set_title("Monthly Stage Bookings")
                ax_bar.set_xticklabels(labels, rotation=45, ha="right")
                ax_bar.set_ylabel("Bookings")

                ax_line.plot(labels, vals, marker="o")
                ax_line.set_title("Booking Trend")
                ax_line.set_xticklabels(labels, rotation=45, ha="right")

            else:
                messagebox.showerror("Error", "Unknown metric"); return

            fig_main.tight_layout()
            if has_tkagg:
                canvas.draw()
            else:
                plt.show()

        def export_csv():
            nonlocal last_table_rows, last_table_headers
            if not last_table_rows:
                messagebox.showinfo("Info", "No data to export. Generate report first.")
                return
            p = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="analytics_export.csv",
                                            filetypes=[("CSV files", "*.csv")])
            if not p:
                return
            with open(p, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(last_table_headers)
                writer.writerows(last_table_rows)
            messagebox.showinfo("Exported", f"CSV saved to {p}")

        def export_pdf():
            
            if not any([len(ax_bar.lines) or len(ax_bar.patches) or len(ax_line.lines) or len(ax_line.patches)]):
                # attempt generate
                generate_report()
            p = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="analytics_report.pdf",
                                            filetypes=[("PDF files", "*.pdf")])
            if not p:
                return
            # Create a PDF with current matplotlib figure
            try:
                with PdfPages(p) as pdf:
                    pdf.savefig(fig_main)
                messagebox.showinfo("Exported", f"PDF saved to {p}")
            except Exception as e:
                messagebox.showerror("Error", f"PDF export failed: {e}")

        # wire buttons
        generate_btn.config(command=generate_report)
        export_csv_btn.config(command=export_csv)
        export_pdf_btn.config(command=export_pdf)

        # --- Bottom: small table preview of last_table_rows ---
        table_frame = tk.Frame(win, bg="#ffffff", bd=1, relief="sunken")
        table_frame.pack(fill="x", padx=12, pady=(8,12))

        table_lbl = tk.Label(table_frame, text="Preview (Generate first then export)", bg="#ffffff")
        table_lbl.pack(anchor="w", padx=8, pady=6)

        preview_tree = ttk.Treeview(table_frame, show="headings", height=6)
        preview_tree.pack(fill="x", padx=8, pady=(0,8))

        def refresh_preview():
            preview_tree.delete(*preview_tree.get_children())
            preview_tree["columns"] = last_table_headers
            for col in last_table_headers:
                preview_tree.heading(col, text=col); preview_tree.column(col, width=120)
            for r in last_table_rows:
                preview_tree.insert("", "end", values=r)

        # refresh preview whenever generate is called by wrapping generate_report
        orig_generate = generate_btn.cget("command")
        def wrapped_generate():
            generate_report()
            refresh_preview()
        generate_btn.config(command=wrapped_generate)

    # end of analytics window
    def update_temple_name_ui():
        new_name = simpledialog.askstring("Update Temple Name", "Enter new temple name:")
        if new_name:
            from temple_db import update_temple_name
            update_temple_name(new_name)
            messagebox.showinfo("Success", f"Temple name updated to '{new_name}'!")

    # Sign out
    def signout():
        for w in root.winfo_children(): w.destroy()
        from db_ui import LoginUI
        LoginUI(root)


    cards = [
        ("🛕", "Manage Worship", "Add/update worship types", manage_worship),
        ("👥", "Manage Employees", "Add/delete employee accounts", manage_employees),
        ("🏟️", "Manage Stages", "Add/update stages & capacity", manage_stages),
        ("📅", "Stage Bookings", "View all stage bookings", view_stage_bookings),
        ("🗓️", "Stage Availability", "Check stage status by date", manage_stage_bookings),
        ("🎟️", "Issued Tickets", "View all issued tickets", view_tickets),
        ("💰", "Donations", "View all donations", view_donations),
        ("📅", "Festival Calendar", "Add/edit festival dates", manage_festival),
        ("🖨️", "Export Festivals", "Export festival calendar", export_festivals),
        ("📊", "Analytics & Reports", "View monthly dashboards", open_analytics_window),
        ("🏛️", "Temple Name", "Update temple name", update_temple_name_ui),
        ("🔒", "Sign Out", "Return to Login", signout),
    ]

    r = 0; c = 0
    for icon, title, subtitle, cmd in cards:
        card = make_card(grid_frame, icon, title, subtitle, cmd, bg="white")
        card.config(width=340, height=140)
        card.grid(row=r, column=c, padx=12, pady=12, sticky="nsew")
        c += 1
        if c >= cols:
            c = 0; r += 1
            


    # footer sign out
    footer = tk.Frame(root, bg="#f0f8ff")
    footer.pack(fill="x", pady=8)
    tk.Button(footer, text="Sign Out", command=signout, bg="#ef5350", fg="white", font=("Arial", 12, "bold")).pack(side="right", padx=12, pady=8)