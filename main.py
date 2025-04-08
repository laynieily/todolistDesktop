import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# ---------- Database storage section ----------
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

#This is to show that there are no tasks in the database for the user to read, instead of an error in the terminal
try:
    cursor.execute("""
        ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'Not started'
    """)
    conn.commit()
except sqlite3.OperationalError:
    pass

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        alarm_days INTEGER,
        status TEXT DEFAULT 'Not started'
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        role TEXT NOT NULL CHECK(role IN ('assigner', 'assignee'))
    )
""")

conn.commit()

# ---------- Variables for the user (can be accesed from anywhere) (no password logic yet)----------
username = None
role = None

# ---------- The login/signup page (first page you see) ----------
def login_signup():
    window = tk.Toplevel(root)
    window.title("Task Manager")
    window.geometry("350x350")
    window.configure(bg="#C6EBF1")
    window.grab_set()

    #Shows the starting window which is the login/signup for the user to acces the tasks
    tk.Label(window, text="Login or Sign Up", font=("", 24), bg="#C6EBF1" ).pack(pady=20)

    tk.Label(window, text="Username:", bg="#C6EBF1").pack(pady=5)
    user_entry = tk.Entry(window)
    user_entry.pack(pady=5)

    tk.Label(window, text="Role (assigner/assignee):", bg="#C6EBF1").pack(pady=5)
    role_entry = tk.Entry(window)
    role_entry.pack(pady=5)

    #If user is not signed in, the signup stores their username in the database
    def signup():
        user = user_entry.get().strip().lower()
        r = role_entry.get().strip().lower()
        if not user or r not in ["assigner", "assignee"]:
            messagebox.showerror("Invalid", "Enter a username and valid role.", parent=window)
            return
        try:
            cursor.execute("INSERT INTO users (username, role) VALUES (?, ?)", (user, r))
            conn.commit()
            messagebox.showinfo("Success", "User registered. You can now log in.", parent=window)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.", parent=window)

    #If user is already signed up, looks for the username in the database and see if it matches 
    #(When logging in the user doesn't need to also input their role, just username)
    def login():
        global username, role
        user = user_entry.get().strip().lower()
        cursor.execute("SELECT role FROM users WHERE username = ?", (user,))
        result = cursor.fetchone()
        if result:
            username = user
            role = result[0]
            messagebox.showinfo("Welcome", f"Logged in as {role}.", parent=window)
            window.destroy()
            root.deiconify()
            load_main_ui()
        else:
            #Handles error if user is either not signed up or misspelled
            messagebox.showerror("Login Failed", "User not found. Please sign up first.", parent=window)

    #For the user to make an 'account' and then login 
    tk.Button(window, text="Login", command=login).pack(pady=10)
    tk.Button(window, text="Sign Up", command=signup).pack(pady=10)

    #Had to make a seperate function for the login window to close since the program would still run even though the window was closed
    def handle_close():
        #If the login/signup window is manually closed (x), exit the program
        conn.close()
        root.destroy()

    window.protocol("WM_DELETE_WINDOW", handle_close)

    #Makes the root (UI) window wait to pop up after the user logins
    root.wait_window(window)


# ---------- Signout logic for the signout button to go back to the login/signup window to be able to go in between different user roles ----------
def sign_out():
    global username, role
    username = None
    role = None
    root.withdraw()
    login_signup()

# ---------- The (reorganzied) UI buttons the user sees whether they are an assignee or assigner ----------
def load_main_ui():
    for widget in root.winfo_children():
        widget.destroy()

    if role == "assigner":
        tk.Button(root, text="Create Task", command=create_action, bg="green", fg="white", width=20).pack(pady=10)
        tk.Button(root, text="View Task(s)", command=read_action, bg="orange", fg="white", width=20).pack(pady=10)
        tk.Button(root, text="Update Task", command=update_action, bg="blue", fg="white", width=20).pack(pady=10)
        tk.Button(root, text="Delete Task", command=delete_action, bg="red", fg="white", width=20).pack(pady=10)

    if role == "assignee":
        tk.Button(root, text="View & Update Task(s)", command=read_action, bg="orange", fg="white", width=20).pack(pady=10)

    tk.Button(root, text="Sign Out", command=sign_out, bg="gray", fg="white", width=20).pack(pady=5)

# ---------- This function creates the task and its logic ----------
def create_action():
    create_window = tk.Toplevel(root)
    create_window.title("Create Task")
    create_window.geometry("350x350")

    #Shows the Task ID entry
    tk.Label(create_window, text="Task ID:").pack()
    task_id_entry = tk.Entry(create_window, width=40)
    task_id_entry.pack(pady=5)

    #Shows the Task Title entry
    tk.Label(create_window, text="Task Title:").pack()
    title_entry = tk.Entry(create_window, width=40)
    title_entry.pack(pady=5)

    #Shows the Task Description entry
    tk.Label(create_window, text="Task Description:").pack()
    description_entry = tk.Entry(create_window, width=40)
    description_entry.pack(pady=5)

    #Shows the Due Date entry
    tk.Label(create_window, text="Due Date (DD/MM/YYYY):").pack()
    due_date_entry = tk.Entry(create_window, width=20)
    due_date_entry.pack(pady=5)

    #Shows the Alarm entry
    tk.Label(create_window, text="Alarm (days before):").pack()
    alarm_days_entry = tk.Entry(create_window, width=10)
    alarm_days_entry.pack(pady=5)

    def save_task():
        #Gets the user input for each option
        task_id = task_id_entry.get()
        title = title_entry.get()
        description = description_entry.get()
        due_date = due_date_entry.get()
        alarm_days = alarm_days_entry.get()

        #Handles error if no input was detected
        if not title or not task_id or not due_date or not alarm_days:
            messagebox.showerror("Error", "Please fill all required fields.", parent=create_window)
            return
        try:
            datetime.strptime(due_date, "%d/%m/%Y")
            alarm_days = int(alarm_days)
        except ValueError:
            messagebox.showerror("Error", "Invalid date or alarm value.", parent=create_window)
            return

        cursor.execute("""
            INSERT INTO tasks (task_id, title, description, due_date, alarm_days)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, title, description, due_date, alarm_days))
        conn.commit()
        messagebox.showinfo("Success", "Task added!", parent=create_window)
        create_window.destroy()

    tk.Button(create_window, text="Create Task", command=save_task, bg="green", fg="white").pack(pady=10)

# ---------- This function allows the user(assignee) to see the task and update its logic ----------
def read_action():
    read_window = tk.Toplevel(root)
    read_window.title("My Tasks")
    read_window.geometry("450x500")

    cursor.execute("SELECT task_id, title, description, due_date, alarm_days, status FROM tasks")
    tasks = cursor.fetchall()

    if not tasks:
        tk.Label(read_window, text="No tasks found.").pack()
        return

    #Shows the user their tasks
    for task in tasks:
        frame = tk.Frame(read_window, relief="ridge", borderwidth=2, padx=5, pady=5)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(frame, text=f"📌 ID: {task[0]}").pack(anchor="w")
        tk.Label(frame, text=f"📝 {task[1]}").pack(anchor="w")
        tk.Label(frame, text=f"Desc: {task[2]}").pack(anchor="w")
        tk.Label(frame, text=f"📅 Due: {task[3]} | 🔔 {task[4]} days").pack(anchor="w")

        #Disables status update for assigner role
        if role == "assignee":
            status_var = tk.StringVar(value=task[5])
            status_menu = tk.OptionMenu(frame, status_var, "Not started", "In progress", "Completed")
            status_menu.pack(pady=5)

            def update_status(task_id=task[0], var=status_var):
                new_status = var.get()
                cursor.execute("UPDATE tasks SET status = ? WHERE task_id = ?", (new_status, task_id))
                conn.commit()
                messagebox.showinfo("Updated", f"Task {task_id} status updated to '{new_status}'")

            tk.Button(frame, text="Update Status", command=update_status).pack()
        else:
            #This just shows the current status without the option to change it for the assigner
            tk.Label(frame, text=f"⏳ Status: {task[5]}").pack(anchor="w")

# ---------- This function allows users(assigners) to update the task logic ----------
def update_action():
    update_window = tk.Toplevel(root)
    update_window.title("Update Task")
    update_window.geometry("350x350")

    #Shows the Existing Task ID entry
    tk.Label(update_window, text="Existing Task ID:").pack()
    old_task_id_entry = tk.Entry(update_window, width=40)
    old_task_id_entry.pack(pady=5)

    #Shows the New Task ID entry
    tk.Label(update_window, text="New Task ID:").pack()
    new_task_id_entry = tk.Entry(update_window, width=40)
    new_task_id_entry.pack(pady=5)

    #Shows the New Task Title entry
    tk.Label(update_window, text="New Task Title:").pack()
    title_entry = tk.Entry(update_window, width=40)
    title_entry.pack(pady=5)

    #Shows the New Task Description entry
    tk.Label(update_window, text="New Task Description:").pack()
    description_entry = tk.Entry(update_window, width=40)
    description_entry.pack(pady=5)

    #Shows the New Due Date entry
    tk.Label(update_window, text="New Due Date (DD/MM/YYYY):").pack()
    due_date_entry = tk.Entry(update_window, width=20)
    due_date_entry.pack(pady=5)

    #Shows the New Alarm entry
    tk.Label(update_window, text="New Alarm (days before):").pack()
    alarm_days_entry = tk.Entry(update_window, width=10)
    alarm_days_entry.pack(pady=5)

    def save_updates():
        #Gets the user input for each option
        old_task_id = old_task_id_entry.get().strip()
        new_task_id = new_task_id_entry.get().strip()
        title = title_entry.get().strip()
        description = description_entry.get().strip()
        due_date = due_date_entry.get().strip()
        alarm_days = alarm_days_entry.get().strip()

        #Handles error if no user input was detected
        if not old_task_id or not new_task_id or not title or not due_date or not alarm_days:
            messagebox.showerror("Error", "All fields are required!", parent=update_window)
            return

        try:
            datetime.strptime(due_date, "%d/%m/%Y")
            alarm_days = int(alarm_days)
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Make sure date and alarm are correct.", parent=update_window)
            return

        cursor.execute("""
            UPDATE tasks
            SET task_id = ?, title = ?, description = ?, due_date = ?, alarm_days = ?
            WHERE task_id = ?
        """, (new_task_id, title, description, due_date, alarm_days, old_task_id))
        conn.commit()

        if cursor.rowcount == 0:
            messagebox.showerror("Error", "Task ID not found.", parent=update_window)
        else:
            messagebox.showinfo("Success", "Task updated successfully!", parent=update_window)
            update_window.destroy()

    tk.Button(update_window, text="Update Task", command=save_updates, bg="blue", fg="white").pack(pady=10)

# ---------- This function allows users (assigners) to delete the task and its logic ----------
def delete_action():
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Task")
    delete_window.geometry("300x150")

    #Makes deleting a task easier by just asking for an ID if maybe tasks have the same name
    tk.Label(delete_window, text="Enter Task ID to Delete:").pack(pady=5)
    task_id_entry = tk.Entry(delete_window, width=20)
    task_id_entry.pack(pady=5)

    #Handles error if no user input was detected
    def confirm_delete():
        task_id = task_id_entry.get()
        if not task_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Task ID!", parent=delete_window)
            return

        cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        conn.commit()

        if cursor.rowcount > 0:
            messagebox.showinfo("Success", f"Task with ID {task_id} deleted successfully!", parent=delete_window)
        else:
            messagebox.showerror("Error", f"No task found with ID {task_id}.", parent=delete_window)

        delete_window.destroy()

    tk.Button(delete_window, text="Delete Task", command=confirm_delete, bg="red", fg="white").pack(pady=10)

# ---------- Starts the the window with the main UI ----------
root = tk.Tk()
root.title("To Do List (Desktop)")
root.geometry("350x350")
root.configure(bg="grey")
root.withdraw()

login_signup()

root.mainloop()
conn.close()
