# db_ui.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from temple_db import authenticate_user, get_role, create_tables, add_employee, create_employee_login
from staff_dashboard import staff_dashboard
from manager_dashboard import manager_dashboard

class LoginUI:
    def __init__(self, root):
        self.root = root
        root.title("Temple Management System - Login")

        # fullscreen / large window
        try:
            root.state('zoomed')  # windows / some platforms
        except:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            root.geometry(f"{screen_w}x{screen_h}+0+0")

        root.configure(bg="#f0f8ff")

        # top header with exit on right
        header = tk.Frame(root, bg="#f0f8ff")
        header.pack(fill="x", pady=(10,0))

        title = tk.Label(header, text="Temple Management System", font=("Arial", 24, "bold"), bg="#f0f8ff")
        title.pack(side="left", padx=20)

        exit_btn = tk.Button(header, text="X", bg="#ef5350", fg="white", font=("Arial", 10, "bold"),
                             relief="flat", width=4, command=self.exit_app)
        exit_btn.pack(side="right", padx=12, pady=6)

        # center card
        card = tk.Frame(root, bg="white", bd=2, relief="groove")
        card.place(relx=0.5, rely=0.45, anchor="center", width=480, height=360)

        lbl = tk.Label(card, text="Sign in to your account", font=("Arial", 16, "bold"), bg="white")
        lbl.pack(pady=(18,8))

        tk.Label(card, text="Username:", bg="white", anchor="w").pack(fill="x", padx=28)
        self.username_entry = tk.Entry(card, font=("Arial", 12))
        self.username_entry.pack(fill="x", padx=28, pady=6)

        tk.Label(card, text="Password:", bg="white", anchor="w").pack(fill="x", padx=28)
        self.password_entry = tk.Entry(card, show="*", font=("Arial", 12))
        self.password_entry.pack(fill="x", padx=28, pady=6)

        tk.Label(card, text="Role:", bg="white", anchor="w").pack(fill="x", padx=28, pady=(6,0))
        self.role_var = tk.StringVar(value="Staff")
        role_frame = tk.Frame(card, bg="white")
        role_frame.pack(pady=6)
        tk.Radiobutton(role_frame, text="Staff", variable=self.role_var, value="Staff", bg="white").pack(side="left", padx=8)
        tk.Radiobutton(role_frame, text="Manager", variable=self.role_var, value="Manager", bg="white").pack(side="left", padx=8)

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(pady=(10,16))
        tk.Button(btn_frame, text="Login", command=self.login_action, bg="#81c784", width=12).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Sign Up", command=self.signup_ui, bg="#4fc3f7", width=12).pack(side="left", padx=8)

    def exit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    def login_action(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        if not username or not password:
            messagebox.showerror("Error", "Username and password required"); return
        if not authenticate_user(username, password):
            messagebox.showerror("Error", "Invalid credentials"); return
        user_role = get_role(username)
        if not user_role or user_role.lower() != role.lower():
            messagebox.showerror("Error", f"Invalid {role} login."); return
        # open dashboard
        if role.lower() == "staff":
            staff_dashboard(self.root, username)
        else:
            manager_dashboard(self.root, username)

    def signup_ui(self):
        win = tk.Toplevel(self.root)
        win.title("Sign Up")
        win.configure(bg="#f5f5f5")
        win.geometry("600x480")

        tk.Label(win, text="Sign Up", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(pady=12)
        form = tk.Frame(win, bg="#f5f5f5"); form.pack(pady=8, padx=12, fill="x")

        tk.Label(form, text="Name:", bg="#f5f5f5").grid(row=0, column=0, sticky="w"); name = tk.Entry(form); name.grid(row=0,column=1,sticky="ew", padx=8, pady=6)
        tk.Label(form, text="Email:", bg="#f5f5f5").grid(row=1, column=0, sticky="w"); email = tk.Entry(form); email.grid(row=1,column=1,sticky="ew", padx=8, pady=6)
        tk.Label(form, text="Role (Staff/Manager):", bg="#f5f5f5").grid(row=2, column=0, sticky="w"); role = tk.Entry(form); role.grid(row=2,column=1,sticky="ew", padx=8, pady=6)
        tk.Label(form, text="Username:", bg="#f5f5f5").grid(row=3, column=0, sticky="w"); username = tk.Entry(form); username.grid(row=3,column=1,sticky="ew", padx=8, pady=6)
        tk.Label(form, text="Password:", bg="#f5f5f5").grid(row=4, column=0, sticky="w"); password = tk.Entry(form, show="*"); password.grid(row=4,column=1,sticky="ew", padx=8, pady=6)

        form.columnconfigure(1, weight=1)

        def do_signup():
            n = name.get().strip(); e = email.get().strip(); r = role.get().strip() or "Staff"
            u = username.get().strip(); p = password.get()
            if not (n and u and p):
                messagebox.showerror("Error", "Name, username, password required"); return
            emp_id = add_employee(n, r, "", e)
            create_employee_login(emp_id, u, p, r)
            messagebox.showinfo("Success", "Signup complete. You can now login.")
            win.destroy()

        tk.Button(win, text="Sign Up", command=do_signup, bg="#81c784", width=14).pack(pady=12)
        
    # scrollable_frame.py





if __name__ == "__main__":
    create_tables()
    from temple_db import demo_seed
    demo_seed()
    root = tk.Tk()
    app = LoginUI(root)
    root.mainloop()