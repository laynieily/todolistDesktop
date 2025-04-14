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

try:
    cursor.execute("ALTER TABLE users ADD COLUMN password TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass



cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id     INTEGER,
        title       TEXT NOT NULL,
        description TEXT,
        due_date    TEXT,
        alarm_days  INTEGER,
        status      TEXT DEFAULT 'Not started',
        assigned_to TEXT,
        PRIMARY KEY(task_id AUTOINCREMENT)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username    TEXT,
        password    TEXT NOT NULL,
        role        TEXT NOT NULL CHECK(role IN ('assigner', 'assignee')),
        PRIMARY KEY(username)
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
    window.geometry("500x500")
    window.configure(bg="#C6EBF1")
    window.grab_set()

    tk.Label(window, text="Login", font=("", 20), bg="#C6EBF1").pack(pady=20)

    tk.Label(window, text="Username:", bg="#C6EBF1").pack(pady=5)
    user_entry = tk.Entry(window)
    user_entry.pack(pady=5)

    tk.Label(window, text="Password:", bg="#C6EBF1").pack(pady=5)
    pass_entry = tk.Entry(window, show="*")
    pass_entry.pack(pady=5)

    def login():
        global username, role
        user = user_entry.get().strip().lower()
        pwd = pass_entry.get()

        cursor.execute("SELECT password, role FROM users WHERE username = ?", (user,))
        result = cursor.fetchone()

        if result and result[0] == pwd:
            username = user
            role = result[1]
            messagebox.showinfo("Welcome", f"Logged in as {role}.", parent=window)
            window.destroy()
            root.deiconify()
            load_main_ui()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=window)

    def open_signup_window():
        signup_win = tk.Toplevel(window)
        signup_win.title("Sign Up")
        signup_win.geometry("450x450")
        signup_win.configure(bg="#EAF9FF")
        signup_win.grab_set()

        tk.Label(signup_win, text="Sign Up", font=("", 18), bg="#EAF9FF").pack(pady=20)

        tk.Label(signup_win, text="Username:", bg="#EAF9FF").pack(pady=5)
        new_user_entry = tk.Entry(signup_win)
        new_user_entry.pack(pady=5)

        tk.Label(signup_win, text="Password:", bg="#EAF9FF").pack(pady=5)
        new_pass_entry = tk.Entry(signup_win, show="*")
        new_pass_entry.pack(pady=5)

        tk.Label(signup_win, text="Confirm Password:", bg="#EAF9FF").pack(pady=5)
        confirm_pass_entry = tk.Entry(signup_win, show="*")
        confirm_pass_entry.pack(pady=5)

        tk.Label(signup_win, text="Role:", bg="#EAF9FF").pack(pady=5)
        role_var = tk.StringVar(value="assigner")  #default to assigner
        role_menu = tk.OptionMenu(signup_win, role_var, "assigner", "assignee")

        role_menu.pack(pady=5)


        def signup():
            new_user = new_user_entry.get().strip().lower()
            new_pass = new_pass_entry.get()
            confirm_pass = confirm_pass_entry.get()
            selected_role = role_var.get()

            if not new_user or not new_pass or not confirm_pass or not selected_role:
                messagebox.showerror("Error", "All fields are required.", parent=signup_win)
                return

            if new_pass != confirm_pass:
                messagebox.showerror("Error", "Passwords do not match.", parent=signup_win)
                return

            try:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_user, new_pass, selected_role))
                conn.commit()
                messagebox.showinfo("Success", "User registered. You can now log in.", parent=signup_win)
                signup_win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists.", parent=signup_win)

        tk.Button(signup_win, text="Sign Up", command=signup, bg="green", fg="white").pack(pady=20)

    tk.Button(window, text="Login", command=login, bg="blue", fg="white").pack(pady=10)
    tk.Button(window, text="Sign Up", command=open_signup_window).pack(pady=5)

    def handle_close():
        conn.close()
        root.destroy()

    window.protocol("WM_DELETE_WINDOW", handle_close)
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
    create_window.geometry("450x450")

    cursor.execute("SELECT DISTINCT username FROM users WHERE role = 'assignee'")
    assignees = [row[0] for row in cursor.fetchall()]


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

    # Assignee dropdown
    tk.Label(create_window, text="Assign To (assignee):").pack()
    assigned_to_var = tk.StringVar(create_window)
    if assignees:
        assigned_to_var.set(assignees[0])
    tk.OptionMenu(create_window, assigned_to_var, assigned_to_var.get(), *assignees).pack(pady=5)


    def save_task():
        #Gets the user input for each option
        task_id = task_id_entry.get()
        title = title_entry.get()
        description = description_entry.get()
        due_date = due_date_entry.get()
        alarm_days = alarm_days_entry.get()
        assigned_to = assigned_to_var.get()

        #Handles error if no input was detected
        if not title or not task_id or not due_date or not alarm_days or not assigned_to:
            messagebox.showerror("Error", "Please fill all required fields.", parent=create_window)
            return
        try:
            datetime.strptime(due_date, "%d/%m/%Y")
            alarm_days = int(alarm_days)
        except ValueError:
            messagebox.showerror("Error", "Invalid date or alarm value.", parent=create_window)
            return

        cursor.execute("""
            INSERT INTO tasks (task_id, title, description, due_date, alarm_days, assigned_to)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task_id, title, description, due_date, alarm_days, assigned_to))
        conn.commit()
        messagebox.showinfo("Success", f"Task assigned to {assigned_to}!", parent=create_window)
        create_window.destroy()

    tk.Button(create_window, text="Create Task", command=save_task, bg="green", fg="white").pack(pady=10)

# ---------- This function allows the user(assignee) to see the task and update its logic ----------
def read_action():
    read_window = tk.Toplevel(root)
    read_window.title("My Tasks")
    read_window.geometry("450x500")

    if role == "assignee":
        cursor.execute("""
            SELECT task_id, title, description, due_date, alarm_days, status FROM tasks WHERE assigned_to = ?
        """, (username,))
    else:
        cursor.execute("""
            SELECT task_id, title, description, due_date, alarm_days, status, assigned_to FROM tasks
        """)
        
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
            tk.Label(frame, text=f"👤 Assigned To: {task[6]}").pack(anchor="w")

# ---------- This function allows users(assigners) to update the task logic ----------
def update_action():
    update_window = tk.Toplevel(root)
    update_window.title("Update Task")
    update_window.geometry("450x450")

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
root.geometry("400x400")
root.configure(bg="grey")
root.withdraw()

login_signup()

root.mainloop()
conn.close()
