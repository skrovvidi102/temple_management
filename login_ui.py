# login_ui.py
import tkinter as tk
from tkinter import messagebox
from temple_db import authenticate_user, get_role
from db_ui import manager_ui
from staff_dashboard import staff_dashboard

def login_ui():
    root = tk.Tk()
    root.title("Temple Management System - Login")
    root.geometry("400x250")

    tk.Label(root, text="Username:").pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    tk.Label(root, text="Password:").pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    def login_action():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Enter username and password.")
            return
        if authenticate_user(username, password):
            role = get_role(username)
            messagebox.showinfo("Success", f"Login successful! Role: {role}")
            if role.lower() == "manager":
                manager_ui(root)
            else:
                staff_dashboard(root, username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(root, text="Login", command=login_action).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    login_ui()