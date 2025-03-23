#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced GUI Tool: Add Criminal to Database
- Tkinter GUI
- SQLite database with robust table creation
- Safe image file handling (sanitized filenames)
- Additional image validation with Pillow
- User-friendly status updates
"""

import os
import sqlite3
import shutil
import uuid
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

# --- Paths ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'criminals.db')
FACES_DIR = os.path.join(BASE_DIR, 'criminal_faces')
os.makedirs(FACES_DIR, exist_ok=True)

# --- DB Init (Robust) ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS criminals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                image_path TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# --- Core Logic (Enhanced) ---
def add_criminal_record(name: str, image_path: str) -> bool:
    if not name or not image_path:
        messagebox.showerror("Missing Info", "Please provide both a name and an image.")
        return False

    if not os.path.exists(image_path) or not image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        messagebox.showerror("Invalid Image", "File must be a valid image (JPG, PNG).")
        return False

    # Additional image verification
    try:
        img = Image.open(image_path)
        img.verify()
    except Exception:
        messagebox.showerror("Invalid Image", "Selected file is corrupted or not a valid image.")
        return False

    # Sanitize filename
    safe_name = re.sub(r'[^A-Za-z0-9_-]', '_', name)
    unique_filename = f"{safe_name}_{uuid.uuid4().hex[:8]}{os.path.splitext(image_path)[1]}"
    dest_path = os.path.join(FACES_DIR, unique_filename)

    try:
        shutil.copyfile(image_path, dest_path)
        rel_path = os.path.relpath(dest_path, BASE_DIR)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO criminals (name, image_path) VALUES (?, ?)", (name, rel_path))
            conn.commit()

        messagebox.showinfo("Success", f"✅ {name} added successfully!")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add record: {e}")
        return False

# --- GUI Setup (Improved UX) ---
def launch_gui():
    root = tk.Tk()
    root.title("Add Criminal to Database")
    root.geometry("400x280")
    root.resizable(False, False)

    selected_image_path = tk.StringVar()
    status_message = tk.StringVar()

    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            selected_image_path.set(file_path)

    def on_submit():
        name = name_entry.get().strip()
        path = selected_image_path.get()
        if add_criminal_record(name, path):
            status_message.set(f"Last added: {name}")
            name_entry.delete(0, tk.END)
            selected_image_path.set("")

    # UI Layout
    tk.Label(root, text="Criminal Name:", font=("Arial", 12)).pack(pady=10)
    name_entry = tk.Entry(root, width=40)
    name_entry.pack()

    tk.Label(root, text="Select Image File:", font=("Arial", 12)).pack(pady=10)
    browse_button = tk.Button(root, text="Browse", command=browse_file)
    browse_button.pack()

    tk.Label(root, textvariable=selected_image_path, wraplength=350, fg="blue").pack(pady=5)

    submit_button = tk.Button(root, text="Add to Database", command=on_submit, bg="green", fg="white")
    submit_button.pack(pady=10)

    # Status Message
    status_label = tk.Label(root, textvariable=status_message, font=("Arial", 10), fg="purple")
    status_label.pack(pady=5)

    root.mainloop()

if __name__ == '__main__':
    launch_gui()
