import tkinter as tk
from tkinter import messagebox,ttk
from tkcalendar import DateEntry
import json,os
from datetime import datetime

TASKS_FILE = "tasks.json"


tasks = {}
def load_tasks():
    global tasks
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE,"r") as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                tasks={}
    else:
        tasks = {}
    refresh_listbox()

def save_tasks():
    with open(TASKS_FILE,"w") as f:
        json.dump(tasks,f,indent=4)

def refresh_listbox():
    task_listbox.delete(0,tk.END)
    filter_mode = filter_var.get()
    search_query= search_var.get().lower().strip()
    sorted_tasks = sorted(tasks.items(), key=lambda item: (
        item[1]["due"] == "",
        item[1]["due"]
    ))
    
    if search_query == "search tasks...":
        search_query = ""

    for task, info in sorted_tasks:
        done = info["done"]
        due = info.get("due","No date")



        if search_query and search_query not in task.lower():
            continue
        if filter_mode == "Completed" and not done:
            continue
        if filter_mode == "Pending" and done:
            continue

        due = info.get("due","")
        display_text = f"✅ {task} (Due: {due})" if done else f"{task} (Due: {due})"
        task_listbox.insert(tk.END,display_text)

def add_task():
    task = task_entry.get().strip()
    due_date = due_date_entry.get_date().strftime("%Y-%m-%d")

    if task:
        tasks[task] = {"done":False,"due":due_date}
        task_entry.delete(0,tk.END)
        save_tasks()
        refresh_listbox()
    else:
        messagebox.showwarning("Warning","Please enter a task!")

def delete_task():
    try:
        selected = task_listbox.curselection()[0]
        text = task_listbox.get(selected)
        task = text.split(" (Due:")[0].replace("✅ ","")
        del tasks[task]
        save_tasks()
        refresh_listbox()
    except IndexError:
        messagebox.showwarning("Warning","Please select a task to delete!")

def toggle_done():
    try:
        selected = task_listbox.curselection()[0]
        text = task_listbox.get(selected)
        task = text.split(" (Due")[0].replace("✅ ","")
        tasks[task]["done"] = not tasks[task]["done"]
        save_tasks()
        refresh_listbox()
    except IndexError:
        messagebox.showwarning("Warning","Please select a task to mark completed!")

is_dark_mode = False
def toggle_theme():
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    if is_dark_mode:
        root.config(bg="#222")
        task_entry.config(bg="#333",fg="white",insertbackground="white")
        task_listbox.config(bg="#333",fg="white",selectbackground="#555")
        search_entry.config(bg="#333",fg="white",insertbackground="white")
        for btn in buttons:
            btn.config(bg="#444",fg="white",activebackground="#555")
        filter_menu.config(background="#333",foreground="white")
        toggle_button.config(text="☀️ Light Mode",bg="#444",fg="white")
    else:
        root.config(bg="#f5f5f5")
        task_entry.config(bg="white",fg="black",insertbackground="black")
        task_listbox.config(bg="white",fg="black",selectbackground="#dcdcdc")
        search_entry.config(bg="white",fg="black",insertbackground="black")
        for btn in buttons:
            btn.config(bg="#e0e0e0",fg="black",activebackground="#ccc")
        filter_menu.config(background="white",foreground="black")
        toggle_button.config(text="🌙 Dark Mode", bg="#e0e0e0",fg="black")


root = tk.Tk()
root.title("To-Do List App")
root.geometry("450x650")
root.config(bg="#f5f5f5")

title=tk.Label(root,text="My To-Do List",font=("Arial",18,"bold"),bg="#f5f5f5")
title.pack(pady=10)

task_entry = tk.Entry(root,width = 30,font=("Arial",12))
task_entry.pack(pady=10)

due_label =tk.Label(root,text="Due Date:", font=("Arial",10), bg="#f5f5f5")
due_label.pack()
due_date_entry= DateEntry(root,width=18,background="darkblue",foreground="white", borderwidth=2)
due_date_entry.pack(pady=5)

search_var = tk.StringVar()
search_entry = tk.Entry(root,textvariable=search_var,width=30,font=("Arial",12),fg="grey")
search_entry.pack(pady=5)
search_entry.insert(0,"Search tasks...")

def on_entry_click(event):
    if search_entry.get() == "Search tasks...":
        search_entry.delete(0,tk.END)
        search_entry.config(fg="black")

def on_focus_out(event):
    if not search_entry.get():
        search_entry.insert(0,"Search tasks...")
        search_entry.config(fg="grey")

search_entry.bind("<FocusIn>",on_entry_click)
search_entry.bind("<FocusOut>",on_focus_out)

filter_var = tk.StringVar(value="All")
filter_menu = ttk.Combobox(root,textvariable=filter_var,values=["All","Completed","Pending"],state="readonly")
filter_menu.pack(pady=5)
filter_menu.bind("<<ComboboxSelected>>",lambda e: refresh_listbox())

add_button = tk.Button(root,text="Add Task",width=15,command=add_task)
delete_button = tk.Button(root,text="Delete Task",width=15,command=delete_task)
done_button = tk.Button(root,text="Mark Done/Undo",width=15,command=toggle_done)
buttons = [add_button,delete_button,done_button]
for btn in buttons:
    btn.pack(pady=5)

task_listbox = tk.Listbox(root,width=50,height=15,selectmode=tk.SINGLE)
task_listbox.pack(pady=15)

search_var.trace_add("write",lambda *args: refresh_listbox())

toggle_button = tk.Button(root,text="🌙 Dark Mode",width=15,command=toggle_theme)
toggle_button.pack(pady=10)

load_tasks()
root.mainloop()

