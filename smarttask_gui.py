import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os

TASKS_FILE = "tasks.json"

class SmartTaskGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartTask GUI")

        # Input fields
        tk.Label(root, text="Task Description:").grid(row=0, column=0, sticky="w")
        self.task_entry = tk.Entry(root, width=40)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Due Date (MM-DD-YYYY HH:MM AM/PM):").grid(row=1, column=0, sticky="w")
        self.due_entry = tk.Entry(root, width=40)
        self.due_entry.grid(row=1, column=1, padx=5, pady=5)

        # Add Task Button
        tk.Button(root, text="Add Task", command=self.add_task).grid(row=2, column=0, columnspan=2, pady=10)
        # Add Sync Button separately
        tk.Button(root, text="Sync UMD ELMS Assignments", command=self.sync_canvas_assignments)\
        .grid(row=3, column=0, columnspan=2, pady=(0, 10))

        # Task list display frame
        self.task_frame = tk.Frame(root)
        self.task_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")
        self.root.rowconfigure(4, weight=1)
        self.root.columnconfigure(1, weight=1)

        # Scrollable canvas inside the task frame
        self.canvas = tk.Canvas(self.task_frame)
        self.scrollbar = tk.Scrollbar(self.task_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.load_tasks()
        self.display_tasks()

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []

    def save_tasks(self):
        with open(TASKS_FILE, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def add_task(self):
        desc = self.task_entry.get().strip()
        due_str = self.due_entry.get().strip()

        if not desc or not due_str:
            messagebox.showwarning("Input Error", "Both fields are required.")
            return

        try:
            # Expect MM-DD-YYYY HH:MM AM/PM
            due = datetime.strptime(due_str, "%m-%d-%Y %I:%M %p")
        except ValueError:
            messagebox.showerror("Date Error", "Use format MM-DD-YYYY HH:MM AM/PM (e.g., 06-15-2025 04:30 PM)")
            return

        task = {
            "description": desc,
            "due": due.isoformat(),
            "created": datetime.now().isoformat()
        }

        self.tasks.append(task)
        self.save_tasks()
        self.task_entry.delete(0, tk.END)
        self.due_entry.delete(0, tk.END)
        self.display_tasks()

    def complete_task(self, index):
        del self.tasks[index]
        self.save_tasks()
        self.display_tasks()

    def edit_task(self, index):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")

        tk.Label(edit_window, text="Description:").grid(row=0, column=0)
        desc_entry = tk.Entry(edit_window, width=40)
        desc_entry.insert(0, self.tasks[index]["description"])
        desc_entry.grid(row=0, column=1)

        tk.Label(edit_window, text="Due Date (MM-DD-YYYY HH:MM AM/PM):").grid(row=1, column=0)
        due_entry = tk.Entry(edit_window, width=40)
        due_entry.insert(0, datetime.fromisoformat(self.tasks[index]["due"]).strftime("%m-%d-%Y %I:%M %p"))
        due_entry.grid(row=1, column=1)

        def save_changes():
            new_desc = desc_entry.get().strip()
            new_due_str = due_entry.get().strip()
            try:
                new_due = datetime.strptime(new_due_str, "%m-%d-%Y %I:%M %p")
                self.tasks[index]["description"] = new_desc
                self.tasks[index]["due"] = new_due.isoformat()
                self.save_tasks()
                self.display_tasks()
                edit_window.destroy()
            except ValueError:
                messagebox.showerror("Format Error", "Please use MM-DD-YYYY HH:MM AM/PM format.")

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=2, column=0, columnspan=2, pady=10)

    def display_tasks(self):
        # Clear old widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Sort tasks by due date
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: datetime.fromisoformat(t["due"]).replace(tzinfo=None)
        )

        for i, task in enumerate(sorted_tasks):
            desc = task["description"]
            due_dt = datetime.fromisoformat(task["due"])
            due_str = due_dt.strftime("%m-%d-%Y %I:%M %p")
            time_left = due_dt - datetime.now(due_dt.tzinfo)
            color = get_due_color(time_left)

            # Task label with colored due date
            task_label = tk.Label(
                self.scrollable_frame,
                text=f"{desc} — due {due_str}",
                anchor="w",
                fg=color
            )
            task_label.grid(row=i, column=0, sticky="w", padx=5, pady=2)

            # Action buttons
            tk.Button(self.scrollable_frame, text="Task Complete", command=lambda i=i: self.complete_task(i)).grid(row=i, column=1, padx=5)
            tk.Button(self.scrollable_frame, text="Edit Task", command=lambda i=i: self.edit_task(i)).grid(row=i, column=2, padx=5)
    
    def sync_canvas_assignments(self):
        import requests
        from datetime import timezone

        API_URL = "https://umd.instructure.com/api/v1"
        TOKEN = "1133~8MfFL9t6uXvxzk6PeCaJHKaZ6XCnVM8ywz4JGWkUYRvGeJWWuRHAEUEzQh9JhHHW"
        headers = {"Authorization": f"Bearer {TOKEN}"}

        try:
            terms_resp = requests.get(f"{API_URL}/accounts/self/terms/current", headers=headers)
            current_term_id = terms_resp.json().get("id")

            courses_resp = requests.get(f"{API_URL}/courses?enrollment_state=active&per_page=100", headers=headers)
            courses = courses_resp.json()
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to fetch term or courses: {e}")
            return

        new_tasks = 0
        for course in courses:
            if course.get("enrollment_term_id") != current_term_id:
                continue

            try:
                assgn_resp = requests.get(f"{API_URL}/courses/{course['id']}/assignments?per_page=100", headers=headers)
                assignments = assgn_resp.json()
                for a in assignments:
                    if a.get("due_at"):
                        desc = f"[{course['name']}] {a['name']}"
                        due = datetime.fromisoformat(a["due_at"].replace("Z", "+00:00")).astimezone()

                        if not any(t["description"] == desc for t in self.tasks):
                            self.tasks.append({
                                "description": desc,
                                "due": due.isoformat(),
                                "created": datetime.now().isoformat()
                            })
                            new_tasks += 1
            except Exception:
                continue

        self.save_tasks()
        self.display_tasks()
        messagebox.showinfo("Sync Complete", f"Imported {new_tasks} assignments from Canvas.")




def get_due_color(time_left):
    if time_left.total_seconds() < 0:
        return "gray"      # overdue
    elif time_left.total_seconds() < 86400:
        return "red"       # due within 24 hours
    elif time_left.total_seconds() < 604800:
        return "orange"    # due within 7 days
    else:
        return "green"     # more than 7 days away

def run_gui():
    root = tk.Tk()
    app = SmartTaskGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()


def get_due_color(time_left):
    if time_left.total_seconds() < 0:
        return "gray"  # overdue
    elif time_left.total_seconds() < 86400:
        return "red"   # < 1 day
    elif time_left.total_seconds() < 604800:
        return "orange"  # < 7 days
    else:
        return "green"

def run_gui():
    root = tk.Tk()
    app = SmartTaskGUI(root)
    root.mainloop()

# Only run directly if called standalone
if __name__ == "__main__":
    run_gui()
