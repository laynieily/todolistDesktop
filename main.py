import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta
import threading

# Initialize the database
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        notify_days INTEGER,
        completed INTEGER DEFAULT 0
    )
""")
conn.commit()

# Create the main window
root = tk.Tk()
root.title("To Do List (Desktop)")
root.geometry("300x200")

# Define the button actions
def check_notifications():
    today = datetime.today().date()
    cursor.execute("SELECT title, due_date, notify_days FROM tasks")
    tasks = cursor.fetchall()

    for title, due_date, notify_days in tasks:
        try:
            task_date = datetime.strptime(due_date, "%d/%m/%Y").date()
            notify_date = task_date - timedelta(days=notify_days)

            if today >= notify_date:
                messagebox.showinfo("Reminder!", f"Task '{title}' is due soon on {due_date}!", parent=root)

        except ValueError:
            continue  # Ignore invalid dates

    threading.Timer(86400, check_notifications).start()  # Run again the check every 24 hours

# Function to open the "Create Task" window
def create_action():
    create_window = tk.Toplevel(root)
    create_window.title("Create Task")
    create_window.geometry("350x350")

    # Task Title
    tk.Label(create_window, text="Task Title:").pack()
    title_entry = tk.Entry(create_window, width=40)
    title_entry.pack(pady=5)

    # Task Description
    tk.Label(create_window, text="Task Description:").pack()
    description_entry = tk.Text(create_window, height=2, width=40)
    description_entry.pack(pady=5)

    # Due Date
    tk.Label(create_window, text="Due Date (DD/MM/YYYY):").pack()
    due_date_entry = tk.Entry(create_window, width=20)
    due_date_entry.pack(pady=5)

    # Notification Days Before Due Date
    tk.Label(create_window, text="Notify me (days before due date):").pack()
    notify_days_entry = tk.Entry(create_window, width=10)
    notify_days_entry.pack(pady=5)

    # Function to save the task
    def save_task():
        title = title_entry.get().strip()
        description = description_entry.get("1.0", tk.END).strip()
        due_date = due_date_entry.get().strip()
        notify_days = notify_days_entry.get().strip()

        if not title or not due_date or not notify_days:
            messagebox.showerror("Error", "Title, Due Date, and Notify Days are required!", parent=create_window)
            return

        try:
            datetime.strptime(due_date, "%d/%m/%Y")  # Validate date format
            notify_days = int(notify_days)  # Ensure notify days is a number
        except ValueError:
            messagebox.showerror("Error", "Invalid Date or Notify Days!", parent=create_window)
            return

        cursor.execute("INSERT INTO tasks (title, description, due_date, notify_days) VALUES (?, ?, ?, ?)", 
                       (title, description, due_date, notify_days))
        conn.commit()

        messagebox.showinfo("Success", "Task added successfully!", parent=create_window)
        create_window.destroy()  # Close the window after saving

    submit_button = tk.Button(create_window, text="Save Task", command=save_task, width=20, bg="green", fg="white")
    submit_button.pack(pady=10)

# Function to read all tasks
def read_action():
    read_window = tk.Toplevel(root)
    read_window.title("My Tasks")
    read_window.geometry("400x400")

    tk.Label(read_window, text="Your Tasks", font=("Arial", 12, "bold")).pack(pady=5)

    cursor.execute("SELECT title, description, due_date, notify_days FROM tasks")
    tasks = cursor.fetchall()

    if not tasks:
        tk.Label(read_window, text="No tasks found.", font=("Arial", 10)).pack(pady=10)
    else:
        for task in tasks:
            task_text = f"📌 {task[0]}\n📝 {task[1]}\n📅 Due: {task[2]}\n🔔 Notify: {task[3]} days before\n"
            tk.Label(read_window, text=task_text, font=("Arial", 10), justify="left", padx=10, pady=5, relief="ridge").pack(fill="both", padx=10, pady=2)


def update_action():
    print("Update button clicked!")

def delete_action():
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Task")
    delete_window.geometry("400x300")

    tk.Label(delete_window, text="Select a task to delete:", font=("Arial", 12, "bold")).pack(pady=5)

    cursor.execute("SELECT id, title, due_date FROM tasks")
    all_tasks = cursor.fetchall()

    if not all_tasks:
        tk.Label(delete_window, text="No tasks found.", font=("Arial", 10)).pack(pady=10)
        return
    
    task_listbox = tk.Listbox(delete_window, width=50, height=10)
    task_listbox.pack(pady=5)

    for task in all_tasks:
        task_listbox.insert(tk.END, f"{task[0]} - {task[1]} (Due: {task[2]})")

    def confirm_delete():
        selected_task = task_listbox.curselection()
        if not selected_task:
            messagebox.showerror("Error", "Please select a task to delete.", parent=delete_window)
            return
        
        task_index = selected_task[0]
        task_id = all_tasks[task_index][0]
        task_title = all_tasks[task_index][1]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{task_title}'?", parent=delete_window)
        if confirm:
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            messagebox.showinfo("Task Deleted", f"'{task_title}' has been deleted.", parent=delete_window)
            delete_window.destroy()
    delete_button = tk.Button(delete_window, text="Delete Task", command=confirm_delete, width=20, bg="red", fg="white")
    delete_button.pack(pady=10)

# Buttons in the Main window
create_button = tk.Button(root, text="Create Task", command=create_action, width=20, bg="green", fg="white")
create_button.pack(pady=10)

read_button = tk.Button(root, text="Read", command=read_action, width=20)
read_button.pack(pady=10)

update_button = tk.Button(root, text="Update", command=update_action, width=20)
update_button.pack(pady=10)

delete_button = tk.Button(root, text="Delete", command=delete_action, width=20, bg="red", fg="white")
delete_button.pack(pady=10)

check_notifications()

root.mainloop()
conn.close()  # Close the database connection when done (update)


