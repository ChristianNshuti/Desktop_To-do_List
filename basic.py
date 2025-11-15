import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json, os

TASKS_FILE = "tasks.json"
tasks = {}

# ------------------ Load & Save Logic ------------------
def load_tasks():
    global tasks
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r") as f:
                tasks = json.load(f)
        except:
            tasks = {}
    refresh_display()

def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

# ------------------ UI Refresh ------------------
def refresh_display():
    for widget in tasks_frame.winfo_children():
        widget.destroy()

    filter_mode = filter_var.get()
    search_query = search_var.get().lower().strip()
    sorted_tasks = sorted(tasks.items(), key=lambda item: item[1]["due"])

    if search_query == "search tasks...":
        search_query = ""

    for task, info in sorted_tasks:
        done = info["done"]
        due = info["due"]
        priority = info.get("priority", "Low")

        # FILTERING
        if search_query and search_query not in task.lower():
            continue
        if filter_mode == "Completed" and not done:
            continue
        if filter_mode == "Pending" and done:
            continue

        # TASK CARD ----
        card = tk.Frame(tasks_frame, bg=("#2c2c2c" if is_dark else "#ffffff"), bd=0, highlightthickness=0)
        card.pack(fill="x", pady=7, padx=10)

        title_row = tk.Frame(card, bg=card["bg"])
        title_row.pack(fill="x")

        title_label = tk.Label(
            title_row,
            text=("✔ " + task) if done else task,
            font=("Segoe UI", 12, "bold"),
            bg=card["bg"],
            fg=("#b3ffb3" if done else "#00a2ff")
        )
        title_label.pack(side="left")

        # PRIORITY BADGE
        color_map = {"Low": "#32cd32", "Medium": "#ffae42", "High": "#ff4c4c"}
        pr_badge = tk.Label(
            title_row,
            text=priority,
            font=("Segoe UI", 10, "bold"),
            bg=color_map[priority],
            fg="white",
            padx=8,
            pady=2
        )
        pr_badge.pack(side="right")

        # Sub info
        tk.Label(
            card,
            text=f"Due: {due}",
            font=("Segoe UI", 10),
            bg=card["bg"],
            fg=("#cccccc" if is_dark else "#555555")
        ).pack(anchor="w")

        # BUTTON ROW
        row = tk.Frame(card, bg=card["bg"])
        row.pack(anchor="e")

        btn_style = {"bg": "#444", "fg": "white", "activebackground": "#666", "cursor": "hand2"}

        tk.Button(row, text="Toggle", command=lambda t=task: toggle_done(t), **btn_style).pack(side="left", padx=4)
        tk.Button(row, text="Delete", command=lambda t=task: delete_task(t), **btn_style).pack(side="left", padx=4)

# ------------------ Task Functions ------------------
def add_task():
    task = task_entry.get().strip()
    due_date = date_entry.get_date().strftime("%Y-%m-%d")
    priority = priority_var.get()

    if not task:
        messagebox.showwarning("Warning", "Enter a task.")
        return

    tasks[task] = {"done": False, "due": due_date, "priority": priority}
    save_tasks()
    refresh_display()
    task_entry.delete(0, tk.END)

def delete_task(task):
    del tasks[task]
    save_tasks()
    refresh_display()

def toggle_done(task):
    tasks[task]["done"] = not tasks[task]["done"]
    save_tasks()
    refresh_display()

# ------------------ Theme Toggle ------------------
is_dark = False

def toggle_theme():
    global is_dark
    is_dark = not is_dark
    apply_theme()

def apply_theme():
    bg = "#1c1c1c" if is_dark else "#f4f4f4"
    fg = "white" if is_dark else "black"
    entry_bg = "#303030" if is_dark else "#ffffff"

    root.config(bg=bg)
    left_panel.config(bg=bg)
    right_panel.config(bg=bg)
    tasks_canvas.config(bg=bg)
    tasks_frame.config(bg=bg)

    for w in [task_entry, search_entry]:
        w.config(bg=entry_bg, fg=fg, insertbackground=fg)

    theme_btn.config(text=("☀ Light Mode" if is_dark else "🌙 Dark Mode"))
    refresh_display()

# ------------------ MAIN UI ------------------
root = tk.Tk()
root.title("Ultra Modern To-Do App")
root.geometry("880x600")
root.config(bg="#f4f4f4")

# Layout: Left menu + Right content
left_panel = tk.Frame(root, width=250, bg="#eaeaea")
left_panel.pack(side="left", fill="y")

right_panel = tk.Frame(root, bg="#f4f4f4")
right_panel.pack(side="right", fill="both", expand=True)

# Left Panel Content -------------------------
tk.Label(left_panel, text="📌 Add Task", font=("Segoe UI", 16, "bold"), bg="#eaeaea").pack(pady=12)

task_entry = tk.Entry(left_panel, font=("Segoe UI", 12), width=22)
task_entry.pack(pady=10, ipady=5)

# Date picker
tk.Label(left_panel, text="Due Date:", bg="#eaeaea").pack()
date_entry = DateEntry(left_panel, width=18)
date_entry.pack(pady=5)

# Priority dropdown
priority_var = tk.StringVar(value="Low")
tk.Label(left_panel, text="Priority:", bg="#eaeaea").pack()
priority_menu = ttk.Combobox(left_panel, state="readonly", width=17, textvariable=priority_var,
                             values=["Low", "Medium", "High"])
priority_menu.pack(pady=5)

# Add button
add_btn = tk.Button(left_panel, text="➕ Add Task", width=18, bg="#0078ff", fg="white",
                    activebackground="#005fcc", cursor="hand2", command=add_task)
add_btn.pack(pady=10, ipady=3)

# Theme toggle
theme_btn = tk.Button(left_panel, text="🌙 Dark Mode", width=18, bg="#444", fg="white",
                      activebackground="#666", cursor="hand2", command=toggle_theme)
theme_btn.pack(pady=20, ipady=3)

# FILTER + SEARCH
tk.Label(left_panel, text="Search", bg="#eaeaea").pack()

search_var = tk.StringVar()
search_entry = tk.Entry(left_panel, textvariable=search_var, width=22)
search_entry.insert(0, "search tasks...")
search_entry.pack(pady=5, ipady=4)

search_var.trace_add("write", lambda *_: refresh_display())

tk.Label(left_panel, text="Filter", bg="#eaeaea").pack()
filter_var = tk.StringVar(value="All")
filter_menu = ttk.Combobox(left_panel, textvariable=filter_var, state="readonly",
                           values=["All", "Completed", "Pending"], width=17)
filter_menu.pack(pady=5)
filter_menu.bind("<<ComboboxSelected>>", lambda e: refresh_display())

# RIGHT SIDE: Scrollable Task Area ------------------
tasks_canvas = tk.Canvas(right_panel, bg="#f4f4f4", highlightthickness=0)
tasks_canvas.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=tasks_canvas.yview)
scrollbar.pack(side="right", fill="y")

tasks_canvas.configure(yscrollcommand=scrollbar.set)

tasks_frame = tk.Frame(tasks_canvas, bg="#f4f4f4")
tasks_canvas.create_window((0, 0), window=tasks_frame, anchor="nw")

def update_scroll(event):
    tasks_canvas.configure(scrollregion=tasks_canvas.bbox("all"))

tasks_frame.bind("<Configure>", update_scroll)

# Load & run
load_tasks()
root.mainloop()
