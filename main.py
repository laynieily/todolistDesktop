import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

############## DATABASE ###################
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

############## Main App Window #################
root = tk.Tk()
root.title("To Do List (Desktop)")
root.geometry("500x500")
root.configure(bg="lightgray")

########### Frame container ############
container = tk.Frame(root)
container.pack(fill="both", expand=True)

frames = {}

########### Navigation bar ##############
nav_frame = tk.Frame(root, bg="blue")
nav_frame.pack(fill="x")

def show_frame(name):
    frame = frames.get(name)
    if frame:
        frame.tkraise()

######### Create Frame ################
create_frame = tk.Frame(container, bg="white")
frames["create"] = create_frame
create_frame.place(relwidth=1, relheight=1)

tk.Label(create_frame, text="Create Task", font=("Arial", 14, "bold")).pack(pady=10)

entries = {}

for label in ["Task Id", "Title", "Description", "Due Date (DD/MM/YYYY)", "Alarm Days"]:
    tk.Label(create_frame, text=label).pack()
    entry = tk.Entry(create_frame, width=40)
    entry.pack(pady=3)
    entries[label] = entry

def save_task():
    task_id = entries["Task Id"].get().strip()
    title = entries["Title"].get().strip()
    description = entries["Description"].get().strip()
    due_date = entries["Due Date (DD/MM/YYYY)"].get().strip()
    alarm_days = entries["Alarm Days"].get().strip()

    if not task_id or not title or not due_date or not alarm_days:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        datetime.strptime(due_date, "%m/%d/%Y")
        alarm_days = int(alarm_days)
    except ValueError:
        messagebox.showerror("Error", "Invalid date or alarm format.")
        return

    try:
        cursor.execute("INSERT INTO tasks (task_id, title, description, due_date, alarm_days) VALUES (?, ?, ?, ?, ?)",
                       (task_id, title, description, due_date, alarm_days))
        conn.commit()
        messagebox.showinfo("Success", "Task added successfully!")
        for entry in entries.values():
            entry.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Task ID already exists.")

tk.Button(create_frame, text="Save Task", command=save_task, bg="green", fg="white").pack(pady=10)

##### Read Frame ########
read_frame = tk.Frame(container, bg="white")
frames["read"] = read_frame
read_frame.place(relwidth=1, relheight=1)

read_header = tk.Label(read_frame, text="Your Tasks", font=("Arial", 14, "bold"))
read_header.pack(pady=10)

task_display_frame = tk.Frame(read_frame, bg="white")
task_display_frame.pack(fill="both", expand=True)

def load_tasks():
    for widget in task_display_frame.winfo_children():
        widget.destroy()

    cursor.execute("SELECT task_id, title, description, due_date, alarm_days FROM tasks")
    tasks = cursor.fetchall()

    if not tasks:
        tk.Label(task_display_frame, text="No tasks found.", font=("Arial", 10), bg="white").pack(pady=10)
    else:
        for task in tasks:
            text = f"📌 {task[0]} - {task[1]}\n📝 {task[2]}\n📅 Due: {task[3]} | 🔔 {task[4]} days before"
            tk.Label(task_display_frame, text=text, justify="left", anchor="w",
                     font=("Arial", 10), bg="white", relief="groove", padx=10, pady=5).pack(fill="x", pady=4, padx=10)

def show_read():
    load_tasks()
    show_frame("read")

######## Update Frame ###########
update_frame = tk.Frame(container, bg="white")
frames["update"] = update_frame
update_frame.place(relwidth=1, relheight=1)

tk.Label(update_frame, text="Update Task", font=("Arial", 14, "bold")).pack(pady=10)

update_entries = {}
for label in ["Old Task ID", "New Task ID", "Title", "Description", "Due Date (DD/MM/YYYY)", "Alarm Days"]:
    tk.Label(update_frame, text=label).pack()
    entry = tk.Entry(update_frame, width=40)
    entry.pack(pady=3)
    update_entries[label] = entry

def update_task():
    try:
        old_id = int(update_entries["Old Task ID"].get().strip())
        new_id = int(update_entries["New Task ID"].get().strip())
        title = update_entries["Title"].get().strip()
        description = update_entries["Description"].get().strip()
        due_date = update_entries["Due Date (DD/MM/YYYY)"].get().strip()
        alarm_days = int(update_entries["Alarm Days"].get().strip())
        datetime.strptime(due_date, "%m/%d/%Y")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid data.")
        return

    try:
        cursor.execute("""
            UPDATE tasks 
            SET task_id=?, title=?, description=?, due_date=?, alarm_days=?
            WHERE task_id=?
        """, (new_id, title, description, due_date, alarm_days, old_id))
        conn.commit()
        if cursor.rowcount == 0:
            messagebox.showerror("Error", "Task not found.")
        else:
            messagebox.showinfo("Success", "Task updated successfully!")
            for entry in update_entries.values():
                entry.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "New Task ID already exists.")

tk.Button(update_frame, text="Update Task", command=update_task, bg="blue", fg="white").pack(pady=10)

########## Delete Frame ##########
delete_frame = tk.Frame(container, bg="white")
frames["delete"] = delete_frame
delete_frame.place(relwidth=1, relheight=1)

tk.Label(delete_frame, text="Delete Task", font=("Arial", 14, "bold")).pack(pady=10)
tk.Label(delete_frame, text="Task ID to Delete").pack()
delete_entry = tk.Entry(delete_frame, width=20)
delete_entry.pack(pady=5)

def delete_task():
    task_id = delete_entry.get().strip()
    if not task_id.isdigit():
        messagebox.showerror("Error", "Please enter a valid Task ID.")
        return

    cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    conn.commit()
    if cursor.rowcount > 0:
        messagebox.showinfo("Success", f"Task {task_id} deleted.")
        delete_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Task not found.")

tk.Button(delete_frame, text="Delete Task", command=delete_task, bg="red", fg="white").pack(pady=10)

############# Navigation Buttons ################
tk.Button(nav_frame, text="Create", width=15, command=lambda: show_frame("create")).pack(side="left", padx=5, pady=5)
tk.Button(nav_frame, text="Read", width=15, command=show_read).pack(side="left", padx=5, pady=5)
tk.Button(nav_frame, text="Update", width=15, command=lambda: show_frame("update")).pack(side="left", padx=5, pady=5)
tk.Button(nav_frame, text="Delete", width=15, command=lambda: show_frame("delete")).pack(side="left", padx=5, pady=5)

############# Start with Create Frame ##########
show_frame("create")
root.mainloop()
conn.close()
