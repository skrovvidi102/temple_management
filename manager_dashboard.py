# manager_dashboard.py
# manager_dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from temple_db import (
    get_all_worship_types, add_worship_type, update_worship_rate,
    add_employee, create_employee_login, get_all_employees,
    delete_employee_by_id, get_stage_bookings, get_all_donations,
    get_issued_tickets_by_employee, get_all_stages, add_stage, update_stage, delete_stage,
    get_connection, get_all_festivals, add_festival, update_festival, delete_festival,get_festivals_by_month
)
from pdf_utils import generate_ticket_pdf, generate_donation_receipt, generate_stage_booking_receipt, generate_festival_calendar_pdf, get_rate
from datetime import date
import os
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import csv
from tkinter import filedialog



# small helper to create a "card button"
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
    # clear previous widgets
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
    grid_frame = tk.Frame(root, bg="#f0f8ff")
    grid_frame.pack(fill="both", expand=True, padx=20, pady=8)

    # grid: 3 columns
    cols = 3
    for c in range(cols):
        grid_frame.columnconfigure(c, weight=1, uniform="c")

    # --------------- features as cards ---------------
    # Manage Worship Types
    def manage_worship():
        # reuse your existing modal from prior code (kept concise)
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

    # Sign out
    def signout():
        for w in root.winfo_children(): w.destroy()
        from db_ui import LoginUI
        LoginUI(root)

    # place cards in grid (3 columns)
    cards = [
        ("🛕", "Manage Worship", "Add/update worship types", manage_worship),
        ("👥", "Manage Employees", "Add/delete employee accounts", manage_employees),
        ("🏟️", "Manage Stages", "Add/update stages & capacity", manage_stages),
        ("📅", "Stage Bookings", "View all stage bookings", view_stage_bookings),
        ("🎟️", "Issued Tickets", "View all issued tickets", view_tickets),
        ("💰", "Donations", "View all donations", view_donations),
        ("📅", "Festival Calendar", "Add/edit festival dates", manage_festival),
        ("🖨️", "Export Tickets", "Export tickets to CSV", export_tickets),
        ("🖨️", "Export Bookings", "Export bookings to CSV", export_stage_bookings),
        ("🖨️", "Export Festivals", "Export festival calendar", export_festivals),
        ("🖨️", "Export Donations", "Export donations", export_donations),
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