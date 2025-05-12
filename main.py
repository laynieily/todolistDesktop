import tkinter as tk
from tkinter import messagebox
import sqlite3

# ——— Global state ———
current_user = None
current_role = None

# ——— DB setup ———
conn = sqlite3.connect("task_manager.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        alarm_days INTEGER,
        status TEXT DEFAULT 'Not started',
        assigned_to TEXT
    )
""")
conn.commit()

# ——— Tkinter root ———
root = tk.Tk()
root.title("To Do List App")
root.state('zoomed')
root.configure(bg="#cce7ff")

frames = {}
def show_frame(name):
    for f in frames.values():
        f.pack_forget()
    frames[name].pack(fill="both", expand=True)

# ——— LOGIN / SIGNUP ———
def login_signup():
    global login_window, username_entry, password_entry, selected_role
    login_window = tk.Toplevel(root)
    login_window.title("Login / Sign Up")
    login_window.state('zoomed')
    login_window.configure(bg="#cce7ff")

    center = tk.Frame(login_window, bg="#cce7ff")
    center.place(relx=0.5, rely=0.5, anchor="center")

    # Header
    tk.Label(center, text="Login / Sign Up", font=("", 20), bg="#cce7ff")\
        .grid(row=0, column=0, columnspan=2, pady=10)

    # Username
    tk.Label(center, text="Username", bg="#cce7ff")\
        .grid(row=1, column=0, sticky="e", padx=5, pady=5)
    username_entry = tk.Entry(center, width=30)
    username_entry.grid(row=1, column=1, padx=5, pady=5)

    # Password
    tk.Label(center, text="Password", bg="#cce7ff")\
        .grid(row=2, column=0, sticky="e", padx=5, pady=5)
    password_entry = tk.Entry(center, show="*", width=30)
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    # Role dropdown
    tk.Label(center, text="Role", bg="#cce7ff")\
        .grid(row=3, column=0, sticky="e", padx=5, pady=5)
    options = ["Assigner", "Assignee"]
    selected_role = tk.StringVar(value="Select Role")
    drop = tk.Menubutton(center, textvariable=selected_role, relief="groove")
    drop.menu = tk.Menu(drop, tearoff=0)
    drop["menu"] = drop.menu
    for opt in options:
        drop.menu.add_radiobutton(label=opt, variable=selected_role, value=opt)
    drop.grid(row=3, column=1, padx=5, pady=5)

    # Buttons
    tk.Button(center, text="Login", command=login, bg="#4CAF50", fg="white")\
        .grid(row=4, column=0, pady=10)
    tk.Button(center, text="Sign Up", command=signup, bg="#2196F3", fg="white")\
        .grid(row=4, column=1, pady=10)

def login():
    global current_user, current_role
    u = username_entry.get().strip()
    p = password_entry.get()
    cursor.execute("SELECT username,role FROM users WHERE username=? AND password=?", (u, p))
    row = cursor.fetchone()
    if not row:
        return messagebox.showerror("Error", "Invalid credentials")
    current_user, current_role = row
    messagebox.showinfo("Success", f"Welcome, {current_user}!")
    login_window.destroy()
    root.deiconify()
    render_menu()
    show_frame("read")

def signup():
    u = username_entry.get().strip()
    p = password_entry.get()
    role_sel = selected_role.get()
    if role_sel == "Select Role":
        return messagebox.showerror("Error", "Please select a role")
    role = role_sel.lower()
    if role not in ("assigner","assignee"):
        return messagebox.showerror("Error", "Invalid role")
    try:
        cursor.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", (u,p,role))
        conn.commit()
    except sqlite3.IntegrityError:
        return messagebox.showerror("Error", "Username already exists")
    messagebox.showinfo("Success", "Registration complete!")

# ——— LOGOUT ———
def logout():
    root.withdraw()
    login_signup()

# ——— CREATE TASK FRAME ———
create_frame = tk.Frame(root, bg="#cce7ff")
frames["create"] = create_frame

# 1) Center container inside create_frame
inner = tk.Frame(create_frame, bg="#cce7ff")
inner.place(relx=0.5, rely=0.5, anchor="center")

# 2) Single header (in inner) with grid()
tk.Label(inner, text="Create Task", font=("Helvetica",16), bg="#cce7ff")\
    .grid(row=0, column=0, columnspan=2, pady=(0,20))

def add_labeled_entry(parent, text, row):
    tk.Label(parent, text=text, bg="#cce7ff")\
        .grid(row=row, column=0, sticky="e", padx=5, pady=5)
    ent = tk.Entry(parent, width=50)
    ent.grid(row=row, column=1, padx=5, pady=5)
    return ent

title_entry       = add_labeled_entry(inner, "Title",                  1)
description_entry = add_labeled_entry(inner, "Description",            2)
due_date_entry    = add_labeled_entry(inner, "Due Date (MM/DD/YYYY)",  3)
alarm_days_entry  = add_labeled_entry(inner, "Alarm Days Before Due",  4)
assigned_to_entry = add_labeled_entry(inner, "Assign To (username)",   5)

# 4) add task button
tk.Button(inner, text="Add Task", command=add_labeled_entry, bg="#2196F3", fg="white")\
    .grid(row=6, column=0, columnspan=2, pady=(20,0))


# ——— READ TASK FRAME ———
read_frame = tk.Frame(root, bg="#cce7ff")
frames["read"] = read_frame

inner = tk.Frame(read_frame, bg="#cce7ff")
inner.place(relx=0.5, rely=0.5, anchor="center")

# Pack header and listbox inside read_frame
tk.Label(inner, text="All Tasks", font=("Helvetica",16), bg="#cce7ff")\
    .pack(pady=10)
task_listbox = tk.Listbox(inner, width=80)
task_listbox.pack(pady=5)

def show_read():
    task_listbox.delete(0, tk.END)
    if current_role == "assignee":
        cursor.execute("SELECT * FROM tasks WHERE assigned_to=?", (current_user,))
    else:
        cursor.execute("SELECT * FROM tasks")
    for row in cursor.fetchall():
        task_listbox.insert(tk.END,
            f"🆔 {row[0]} | 🧾 {row[1]} | 📅 Due: {row[3]} | 👤 Assigned: {row[6]} | 📌 Status: {row[5]}"
        )
    show_frame("read")


# ——— UPDATE TASK FRAME ———
update_frame = tk.Frame(root, bg="#cce7ff")
frames["update"] = update_frame

inner = tk.Frame(update_frame, bg="#cce7ff")
inner.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(inner, text="Update Task Status", font=("Helvetica",16), bg="#cce7ff")\
    .grid(row=0, column=0, columnspan=2, pady=10)

update_id_entry  = add_labeled_entry(inner, "Task ID",   1)
new_status_entry = add_labeled_entry(inner, "New Status",2)

def update_task():
    try:
        tid = int(update_id_entry.get())
    except ValueError:
        return messagebox.showerror("Error","Task ID must be an integer")
    cursor.execute("UPDATE tasks SET status=? WHERE task_id=?", (new_status_entry.get(),tid))
    if cursor.rowcount==0:
        return messagebox.showerror("Error","No such Task ID")
    conn.commit()
    messagebox.showinfo("Success","Task status updated")
    update_id_entry.delete(0,tk.END)
    new_status_entry.delete(0,tk.END)

tk.Button(inner, text="Update", command=update_task, bg="#ff9800", fg="white")\
    .grid(row=3, column=0, columnspan=2, pady=10)

# ——— DELETE TASK FRAME ———
delete_frame = tk.Frame(root, bg="#cce7ff")
delete_frame.place(relx=0.5, rely=0.5, anchor="center")
frames["delete"] = delete_frame

inner = tk.Frame(delete_frame, bg="#cce7ff")
inner.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(inner, text="Delete Task", font=("Helvetica",16), bg="#cce7ff")\
    .grid(row=0, column=0, columnspan=2, pady=(0,20))

delete_entry = add_labeled_entry(inner, "Task ID", 1)

def delete_task():
    try:
        tid = int(delete_entry.get())
    except ValueError:
        return messagebox.showerror("Error","Task ID must be an integer")
    cursor.execute("DELETE FROM tasks WHERE task_id=?", (tid,))
    if cursor.rowcount==0:
        return messagebox.showerror("Error","No such Task ID")
    conn.commit()
    messagebox.showinfo("Success","Task deleted")
    delete_entry.delete(0,tk.END)

tk.Button(inner, text="Delete Task", command=delete_task, bg="red", fg="white")\
    .grid(row=2, column=0, columnspan=2, pady=10)

# ——— MAIN MENU ———
menu_frame = tk.Frame(root, bg="#ddd")
menu_frame.pack(pady=10)

def render_menu():
    root.state('zoomed')          # zoom in for every frame
    for widget in menu_frame.winfo_children():
        widget.destroy()


    if current_role == "assigner":
        tk.Button(menu_frame, text="Create Task", command=lambda: show_frame("create"), bg = "blue", fg="white")\
            .pack(side="left", padx=5)
        tk.Button(menu_frame, text="View Tasks",  command=show_read, bg = "green", fg="white")\
            .pack(side="left", padx=5)
        tk.Button(menu_frame, text="Delete Task", command=lambda: show_frame("delete"), bg ="red", fg="white")\
            .pack(side="left", padx=5)

    if current_role == "assignee":
        tk.Button(menu_frame, text="View Tasks", command=show_read)\
            .pack(side="left", padx=5)

    tk.Button(menu_frame, text="Update Task", command=lambda: show_frame("update"), bg="orange", fg="white")\
        .pack(side="left", padx=5)
    tk.Button(menu_frame, text="Logout", command=logout, bg="gray", fg="white")\
        .pack(side="left", padx=5)

# ——— Start the app ———
root.withdraw()
login_signup()
root.mainloop()
