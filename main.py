import tkinter as tk
from tkinter import messagebox  # Uncommented this
import sqlite3
from datetime import datetime

# Initialize the database
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        alarm_days INTEGER,
        completed INTEGER DEFAULT 0
    )
""")
conn.commit()

# Create the main window
root = tk.Tk()
root.title("To Do List (Desktop)")
root.geometry("300x200")
root.configure(bg="grey")


# Define the button actions
def create_action():
    create_window = tk.Toplevel(root)
    create_window.title("Create Task")
    create_window.geometry("350x350")

    #Create Task Id
    tk.Label(create_window, text="Task Id:").pack()
    task_id_entry = tk.Entry(create_window, width=40)
    task_id_entry.pack(pady=5)

    # Task Title
    tk.Label(create_window, text="Task Title:").pack()
    title_entry = tk.Entry(create_window, width=40)
    title_entry.pack(pady=5)
    # Task Description
    tk.Label(create_window, text="Task Description:").pack()
    description_entry = tk.Entry(create_window, width=40)
    description_entry.pack(pady=5)
    # Due Date
    tk.Label(create_window, text="Due Date (DD/MM/YYYY):").pack()
    due_date_entry = tk.Entry(create_window, width=20)
    due_date_entry.pack(pady=5)
    # Alarm Days Before Due Date
    tk.Label(create_window, text="Alarm:").pack()
    alarm_days_entry = tk.Entry(create_window, width=10)
    alarm_days_entry.pack(pady=5)

    # Saving Task
    def save_task():
        task_id = task_id_entry.get()
        title = title_entry.get()
        description = description_entry.get().strip()  # Fixed this
        due_date = due_date_entry.get()
        alarm_days = alarm_days_entry.get()


        if not task_id or not title or not due_date or not alarm_days:
            messagebox.showerror("Error", "Task Id, Title, Due Date, and Alarm are required!", parent=create_window)
            return
        try:
            datetime.strptime(due_date, "%d/%m/%Y")  # Fixed the format
            alarm_days = int(alarm_days)  # Check if alarm is a number
        except ValueError:
            messagebox.showerror("Error", "Invalid Date or Alarm!", parent=create_window)
            return
        
        cursor.execute("INSERT INTO tasks (task_id, title, description, due_date, alarm_days) VALUES (?, ?, ?, ?, ?)", 
                       (task_id, title, description, due_date, alarm_days))  # Fixed table name
        conn.commit()

        messagebox.showinfo("Success", "Task added successfully!", parent=create_window)
        create_window.destroy()  # Close the window after saving

    submit_button = tk.Button(create_window, text="Save Task", command=save_task, width=20, bg="green", fg="white")
    submit_button.pack(pady=10)

def read_action():
    read_window = tk.Toplevel(root)
    read_window.title("My Tasks")
    read_window.geometry("400x400")

    tk.Label(read_window, text="Your Tasks", font=("Arial", 12, "bold")).pack(pady=5)

    cursor.execute("SELECT task_id, title, description, due_date, alarm_days FROM tasks")
    tasks = cursor.fetchall()

    if not tasks:
        tk.Label(read_window, text="No tasks found.", font=("Arial", 10)).pack(pady=10)
    else:
        for task in tasks:
            task_text = f"📌 {task[0]}\n📌 {task[1]}\n📝 {task[2]}\n📅 Due: {task[3]}\n🔔 Notify: {task[4]} days before\n"
            tk.Label(read_window, text=task_text, font=("Arial", 10), justify="left", padx=10, pady=5, relief="ridge").pack(fill="both", padx=10, pady=2)

def update_action():
    update_window = tk.Toplevel(root)
    update_window.title("Update Task")
    update_window.geometry("350x400")

    # Step 1: Enter existing task ID
    tk.Label(update_window, text="*Existing Task ID:").pack()
    old_task_id_entry = tk.Entry(update_window, width=40)
    old_task_id_entry.pack(pady=5)

    # Step 2: Enter new details (including new task ID)
    tk.Label(update_window, text="*New Task ID:").pack()
    new_task_id_entry = tk.Entry(update_window, width=40)
    new_task_id_entry.pack(pady=5)

    tk.Label(update_window, text="*New Task Title:").pack()
    title_entry = tk.Entry(update_window, width=40)
    title_entry.pack(pady=5)

    tk.Label(update_window, text="New Task Description:").pack()
    description_entry = tk.Text(update_window, width=40, height=5)
    description_entry.pack(pady=5)

    tk.Label(update_window, text="*New Due Date (DD/MM/YYYY):").pack()
    due_date_entry = tk.Entry(update_window, width=20)
    due_date_entry.pack(pady=5)

    tk.Label(update_window, text="*New Alarm (days before due date):").pack()
    alarm_days_entry = tk.Entry(update_window, width=10)
    alarm_days_entry.pack(pady=5)

    def save_updates():
        old_task_id = old_task_id_entry.get().strip()
        new_task_id = new_task_id_entry.get().strip()
        title = title_entry.get().strip()
        description = description_entry.get("1.0", tk.END).strip()
        due_date = due_date_entry.get().strip()
        alarm_days = alarm_days_entry.get().strip()

        # Check required fields
        if not old_task_id or not new_task_id or not title or not due_date or not alarm_days:
            messagebox.showerror("Error", "All fields with * are required!", parent=update_window)
            return

        try:
            datetime.strptime(due_date, "%d/%m/%Y")
            alarm_days = int(alarm_days)
            old_task_id = int(old_task_id)
            new_task_id = int(new_task_id)
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Make sure IDs, date, and alarm are correct.", parent=update_window)
            return

        # Try to update
        try:
            cursor.execute("""
                UPDATE tasks 
                SET task_id = ?, title = ?, description = ?, due_date = ?, alarm_days = ?
                WHERE task_id = ?
            """, (new_task_id, title, description, due_date, alarm_days, old_task_id))
            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showerror("Error", f"No task found with ID {old_task_id}.", parent=update_window)
            else:
                messagebox.showinfo("Success", "Task updated successfully!", parent=update_window)
                update_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"Task ID {new_task_id} already exists. Choose a different one.", parent=update_window)

    update_button = tk.Button(update_window, text="Update Task", command=save_updates, width=20, bg="blue", fg="white")
    update_button.pack(pady=10)


def delete_action():
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Task")
    delete_window.geometry("300x150")

    # Task ID Entry
    tk.Label(delete_window, text="Enter Task ID to Delete:").pack(pady=5)
    task_id_entry = tk.Entry(delete_window, width=20)
    task_id_entry.pack(pady=5)

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

    delete_button = tk.Button(delete_window, text="Delete Task", command=confirm_delete, width=20, bg="red", fg="white")
    delete_button.pack(pady=10)

# Add the buttons to the window
create_button = tk.Button(root, text="Create Task", command=create_action, width=20, bg="green", fg="white")
create_button.pack(pady=10)

read_button = tk.Button(root, text="Read", command=read_action, width=20, bg="orange", fg="white")
read_button.pack(pady=10)

update_button = tk.Button(root, text="Update", command=update_action, width=20, bg="blue", fg="white")
update_button.pack(pady=10)

delete_button = tk.Button(root, text="Delete", command=delete_action, width=20, bg="red", fg="white")
delete_button.pack(pady=10)

# Run the application
root.mainloop()

# Close database connection when done
conn.close()