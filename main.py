import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("test button")
root.geometry("300x200")

# Define the button action
def on_button_click():
    print("Button clicked!")

# Add the button to the window
button = tk.Button(root, text="test button", command=on_button_click)
button.pack(pady=50)

# Run the application
root.mainloop()