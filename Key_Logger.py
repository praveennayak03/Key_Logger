import tkinter as tk
from tkinter import messagebox, scrolledtext
from pynput.keyboard import Key, Listener
import threading
import datetime
import os
from PIL import Image, ImageTk   # for background image support

keys = []
listener = None
log_filename = None
running = False


def format_key(key):
    if hasattr(key, 'char') and key.char is not None:
        return key.char
    else:
        return f"[{key.name}]" if hasattr(key, "name") else str(key)


def on_press(key):
    global keys
    keys.append(key)
    save_to_file(key)
    update_preview(key)


def save_to_file(key):
    global log_filename
    k = format_key(key)
    with open(log_filename, 'a') as f:
        f.write(k + " ")


def update_preview(key):
    k = format_key(key)
    preview_box.config(state="normal")
    preview_box.insert(tk.END, k + " ")
    preview_box.see(tk.END)
    preview_box.config(state="disabled")


def on_release(key):
    if key == Key.esc:
        return False


def start_tracking():
    global listener, log_filename, keys, running
    if running:
        messagebox.showinfo("Keyboard Monitor", "Already tracking!")
        return
    running = True
    keys = []

    if not os.path.exists("activity_logs"):
        os.makedirs("activity_logs")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join("activity_logs", f"activity_{timestamp}.txt")

    status_label.config(text=f"Tracking to: {log_filename}", fg="blue")
    preview_box.config(state="normal")
    preview_box.delete(1.0, tk.END)
    preview_box.config(state="disabled")

    listener = Listener(on_press=on_press, on_release=on_release)
    threading.Thread(target=listener.start, daemon=True).start()


def stop_tracking():
    global listener, running
    if listener and running:
        listener.stop()
        running = False
        status_label.config(text="Tracking stopped", fg="red")
        messagebox.showinfo("Keyboard Monitor", "Keyboard tracking stopped.")


def open_logs():
    if os.name == "nt":
        os.startfile("activity_logs")
    elif os.name == "posix":
        os.system("open activity_logs" if "darwin" in os.sys.platform else "xdg-open activity_logs")
    else:
        messagebox.showinfo("Logs", "Logs saved in 'activity_logs' folder.")


# ---------------- UI ----------------
root = tk.Tk()
root.title("⌨ Keyboard Activity Monitor")
root.geometry("650x520")

# ---- Load Background Image (update the path here) ----
bg_image_path = "background.jpg"   # 👈 change this to your image path
bg_image = Image.open(bg_image_path)
bg_image = bg_image.resize((1920, 1080))   # fit window size
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a label for background
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Use a frame for content (to sit on top of background)
frame = tk.Frame(root, bg="white", bd=2, relief="groove")
frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)

title_label = tk.Label(frame, text="⌨ Keyboard Activity Monitor", font=("Arial", 22, "bold"), bg="white")
title_label.pack(pady=20)

start_btn = tk.Button(frame, text="▶ Start Tracking", command=start_tracking, width=20, height=2,
                      bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
start_btn.pack(pady=10)

stop_btn = tk.Button(frame, text="⏹ Stop Tracking", command=stop_tracking, width=20, height=2,
                     bg="#F44336", fg="white", font=("Arial", 14, "bold"))
stop_btn.pack(pady=10)

log_btn = tk.Button(frame, text="📂 Open Activity Logs", command=open_logs, width=20, height=2,
                    bg="#2196F3", fg="white", font=("Arial", 14, "bold"))
log_btn.pack(pady=10)

status_label = tk.Label(frame, text="Not tracking", font=("Arial", 12), fg="gray", bg="white")
status_label.pack(pady=10)

preview_label = tk.Label(frame, text="Recent Key Activity:", font=("Arial", 12, "italic"), bg="white")
preview_label.pack()

preview_box = scrolledtext.ScrolledText(frame, width=70, height=10, font=("Courier", 12), state="disabled")
preview_box.pack(pady=10)

footer = tk.Label(frame, text="Project: Keyboard Activity Monitor • ESC to stop listener",
                  font=("Arial", 9), fg="gray", bg="white")
footer.pack(side="bottom", pady=5)

root.mainloop()
