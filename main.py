import tkinter as tk
#from tkinter import massagebox
import sqlite3
from datetime import datetime

# Initialize the data base
conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

# Define the button actions
def create_action():
    create_window = tk.Toplevel(root)
    create_window.title("Create Task")
    create_window.geometry("350x350")
    #Task Title
    tk.Label(create_window, text="Task Title:").pack()
    title_entry = tk.Entry(create_window, width=40)
    title_entry.pack(pady=5)
    #Task Description
    tk.Label(create_window, text="Task Description:").pack()
    description_entry = tk.Entry(create_window, width=40)
    description_entry.pack(pady=5)
    #Due Date
    tk.Label(create_window, text="Due Date (DD/MM/YYYY):").pack()
    due_date_entry = tk.Entry(create_window, width=20)
    due_date_entry.pack(pady=5)
    #Alarm Days Before Due Date
    tk.Label(create_window, text="Alarm:").pack()
    alarm_days_entry = tk.Entry(create_window, width=10)
    alarm_days_entry.pack(pady=5)

    #Saving Taks
    def save_task():
        title = title_entry.get()
        description = description_entry.get("1.0", tk.END).strip()
        due_date = due_date_entry.get()
        alarm_days = alarm_days_entry.get()

        if not title or not due_date or not alarm_days:
            tk.messagebox.showerror("Error", "Title, Due Date, and Alarm are required!", parent=create_window)
            return
        try:
            datetime.strptime(due_date, "%d/%m/#Y") #Check the format
            alarm_days = int(alarm_days) #Check if alarm is a number
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid Date or Alarm!", parent=create_window)
            return
        
        cursor.execute("INSERT INTO task (title, description, due_date, alarm_days_before) VALUES (?, ?, ?, ?)", (title, description, due_date, alarm_days))
        conn.commit()

        tk.messagebox.showinfo("Sucess", "Task added successfully!", parent=create_window)
        create_window.destroy() #close the window after saving

    submit_button = tk.Button(create_window, text="Save Task", command=save_task, width=20, bg="green", fg="white")
    submit_button.pack(pady=10)

def read_action():
    print("Read button clicked!")

def update_action():
    print("Update button clicked!")

def delete_action():
    print("Delete button clicked!")

# Add the buttons to the window
##Create Task Button
create_button = tk.Button(root, text="Create Task", command=create_action, width=20, bg="green", fg="white")
create_button.pack(pady=10)

read_button = tk.Button(root, text="Read", command=read_action, width=20)
read_button.pack(pady=10)

update_button = tk.Button(root, text="Update", command=update_action, width=20)
update_button.pack(pady=10)

delete_button = tk.Button(root, text="Delete", command=delete_action, width=20)
delete_button.pack(pady=10)

# Run the application
root.mainloop()

# Close database connection when done
conn.close()