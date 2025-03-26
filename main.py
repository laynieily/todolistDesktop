import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("To Do List (WEB)")
root.geometry("300x300")

# Define the button actions
def create_action():
    print("Create button clicked!")

def read_action():
    print("Read button clicked!")

def update_action():
    print("Update button clicked!")

def delete_action():
    print("Delete button clicked!")

# Add the buttons to the window
create_button = tk.Button(root, text="Create", command=create_action, width=20)
create_button.pack(pady=10)

read_button = tk.Button(root, text="Read", command=read_action, width=20)
read_button.pack(pady=10)

update_button = tk.Button(root, text="Update", command=update_action, width=20)
update_button.pack(pady=10)

delete_button = tk.Button(root, text="Delete", command=delete_action, width=20)
delete_button.pack(pady=10)

# Run the application
root.mainloop()