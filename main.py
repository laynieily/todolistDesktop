import tkinter as tk
from tkinter import messagebox
import sqlite3

# Connect to SQLite DB
conn = sqlite3.connect("task_manager.db")
cursor = conn.cursor()

# Create tables
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

# Tkinter windows
root = tk.Tk()
root.title("To Do List App")
root.state('zoomed')
root.configure(bg="#cce7ff")

frames = {}

def show_frame(name):
    for f in frames.values():
        f.pack_forget()
    frames[name].pack(fill="both", expand=True)

# ---------- LOGIN/SIGNUP ----------
def login_signup():
    global login_window, username_entry, password_entry, selected_role
    login_window = tk.Toplevel()
    login_window.title("To Do List App")
    login_window.state('zoomed')
    login_window.configure(bg="#cce7ff")

    center_frame = tk.Frame(login_window)
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    for i in range(4):
        center_frame.rowconfigure(1, weight=1)
        center_frame.columnconfigure(1, weight=1)

    tk.Label(center_frame, text="Login/Sign Up", font=("", 20)).grid(row=0, column=0, sticky='w', padx=10, pady=5)

    tk.Label(center_frame, text="Username").grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
    username_entry = tk.Entry(center_frame, width=30)
    username_entry.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)

    tk.Label(center_frame, text="Password").grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
    password_entry = tk.Entry(center_frame, show="*", width=30)
    password_entry.grid(row=2, column=1, sticky='nsew', padx=10, pady=5)

    options = ["Assigner", "Assignee"]
    selected_role = tk.StringVar()
    selected_role.set("Select Role")

    dropDown = tk.Menubutton(center_frame, textvariable=selected_role, relief=tk.GROOVE)
    dropDown.menu = tk.Menu(dropDown, tearoff=0)
    dropDown["menu"] = dropDown.menu

    for option in options:
        dropDown.menu.add_radiobutton(label=option, variable=selected_role, value=option)

    dropDown.grid(row=3, column=1, sticky='nsew', padx=10, pady=5)

    tk.Button(center_frame, text="Login", command=login, bg="#4CAF50", fg="white").grid(row=4, column=0, columnspan=2, pady=10)
    tk.Button(center_frame, text="Sign Up", command=signup).grid(row=5, column=0, columnspan=2)


def login():
    global current_user, current_role
    username = username_entry.get()
    password = password_entry.get()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        current_user = user[0]
        current_role = user[2]
        messagebox.showinfo("Success", f"Welcome {current_user}!")
        login_window.destroy()
        root.deiconify()
        root.state('zoomed')
        render_menu()
        show_read()
    else:
        messagebox.showerror("Error", "Invalid credentials")

def signup():
    username = username_entry.get()
    password = password_entry.get()
    role = selected_role.get().lower()  
    if role not in ['assigner', 'assignee']:
        messagebox.showerror("Error", "Role must be 'assigner' or 'assignee'")
        return
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, password, role))
        conn.commit()
        messagebox.showinfo("Success", "User registered!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")


# ----- Logout --------
def logout():
    root.withdraw()
    login_signup()

# ---------- CREATE TASK ----------
create_frame = tk.Frame(root, bg="#cce7ff")
frames["create"] = create_frame

tk.Label(create_frame, text="Create Task", font=("Helvetica", 16), bg="#f2f2f2").pack(pady=10)

def add_labeled_entry(parent, label_text):
    tk.Label(parent, text=label_text, bg="#f2f2f2").pack(anchor="w", padx=10)
    entry = tk.Entry(parent, width=50)
    entry.pack(pady=2)
    return entry

title_entry = add_labeled_entry(create_frame, "Title")
description_entry = add_labeled_entry(create_frame, "Description")
due_date_entry = add_labeled_entry(create_frame, "Due Date (MM/DD/YYYY)")
alarm_days_entry = add_labeled_entry(create_frame, "Alarm Days Before Due")
assigned_to_entry = add_labeled_entry(create_frame, "Assign To (username)")

def add_task():
    try:
        alarm_days = int(alarm_days_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Alarm Days must be a number")
        return

    cursor.execute("INSERT INTO tasks (title, description, due_date, alarm_days, assigned_to) VALUES (?, ?, ?, ?, ?)",
                   (title_entry.get(), description_entry.get(), due_date_entry.get(),
                    alarm_days, assigned_to_entry.get()))
    conn.commit()
    messagebox.showinfo("Success", "Task created!")
    for e in [title_entry, description_entry, due_date_entry, alarm_days_entry, assigned_to_entry]:
        e.delete(0, tk.END)

tk.Button(create_frame, text="Add Task", command=add_task, bg="#2196F3", fg="white").pack(pady=10)

# ---------- READ TASK ----------
read_frame = tk.Frame(root, bg="#cce7ff")
frames["read"] = read_frame

tk.Label(read_frame, text="All Tasks", font=("Helvetica", 16), bg="#f2f2f2").pack(pady=10)
task_listbox = tk.Listbox(read_frame, width=80)
task_listbox.pack(pady=5)

def show_read():
    show_frame("read")
    task_listbox.delete(0, tk.END)

    if current_role == "assignee":
        cursor.execute("SELECT * FROM tasks WHERE assigned_to=?", (current_user,))
    else:
        cursor.execute("SELECT * FROM tasks")

    for row in cursor.fetchall():
        task_listbox.insert(tk.END, f"ID {row[0]} | {row[1]} | {row[2]} | Due: {row[3]} | Assigned to: {row[6]} | Status: {row[5]}")

# ---------- UPDATE TASK ----------
update_frame = tk.Frame(root, bg="#cce7ff")
frames["update"] = update_frame

tk.Label(update_frame, text="Update Task Status", font=("Helvetica", 16), bg="#f2f2f2").pack(pady=10)

update_id_entry = add_labeled_entry(update_frame, "Task ID")
new_status_entry = add_labeled_entry(update_frame, "New Status")

def update_task():
    try:
        task_id = int(update_id_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Task ID must be an integer")
        return

    cursor.execute("UPDATE tasks SET status=? WHERE task_id=?", (new_status_entry.get(), task_id))
    if cursor.rowcount == 0:
        messagebox.showerror("Error", "Task ID not found.")
    else:
        conn.commit()
        messagebox.showinfo("Success", "Task updated!")
        update_id_entry.delete(0, tk.END)
        new_status_entry.delete(0, tk.END)

tk.Button(update_frame, text="Update", command=update_task, bg="#ff9800", fg="white").pack(pady=10)

# ---------- DELETE TASK ----------
delete_frame = tk.Frame(root, bg="#f2f2f2")
frames["delete"] = delete_frame

tk.Label(delete_frame, text="Delete Task", font=("Helvetica", 16), bg="#f2f2f2").pack(pady=10)

delete_entry = add_labeled_entry(delete_frame, "Task ID")

def delete_task():
    try:
        task_id = int(delete_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Task ID must be an integer")
        return

    cursor.execute("DELETE FROM tasks WHERE task_id=?", (task_id,))
    if cursor.rowcount == 0:
        messagebox.showerror("Error", "Task not found.")
    else:
        conn.commit()
        messagebox.showinfo("Success", "Task deleted!")
        delete_entry.delete(0, tk.END)

tk.Button(delete_frame, text="Delete Task", command=delete_task, bg="red", fg="white").pack(pady=10)

# ---------- MAIN INTERFACE ----------
menu_frame = tk.Frame(root, bg="#ddd")
menu_frame.pack(pady=10)

def render_menu():
    for widget in menu_frame.winfo_children():
        widget.destroy()

    if current_role == "assigner":
        tk.Button(menu_frame, text="Create Task", command=lambda: show_frame("create")).pack(side="left", padx=5)
        tk.Button(menu_frame, text="View Tasks", command=show_read).pack(side="left", padx=5)
        tk.Button(menu_frame, text="Delete Task", command=lambda: show_frame("delete")).pack(side="left", padx=5)
    if current_role == "assignee":
        tk.Button(menu_frame, text="View Tasks", command=show_read).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Update Task", command=lambda: show_frame("update")).pack(side="left", padx=5)
    tk.Button(menu_frame, text="Logout", command=logout, bg="gray", fg="white").pack(side="left", padx=5)

# ---------- Start the App ----------
root.withdraw()
login_signup()
root.mainloop()
