# A Smart To-Do List GUI with Canvas Integration

The Smart To-Do List is a Python-based productivity assistant built with Tkinter that allows users to manage tasks through a clean graphical interface. Designed for students and busy professionals, SmartTask makes it easy to add, edit, and complete tasks — and includes a unique integration with the University of Maryland's ELMS (Canvas) system to automatically import assignments.

### Features

- ** Task Management:**  
  Add tasks with a natural date/time format (e.g., `06-15-2025 04:30 PM`), edit descriptions or due dates, and mark tasks as completed with one click.

- ** Intuitive GUI Interface:**  
  Built with Python’s Tkinter, the interface displays tasks with color-coded urgency indicators:
  - Red: Due within 24 hours  
  - Orange: Due within 7 days  
  - Green: More than a week away  
  - Gray: Overdue

- ** Canvas Assignment Sync (Optional):**  
  Users can enter their Canvas API token and instantly sync upcoming assignments from active courses on ELMS (Canvas). The app filters only current semester courses and prevents duplicate imports.

- ** Auto-Sorting:**  
  Tasks are automatically sorted by due date to help users prioritize what's next.

- ** Local Persistence:**  
  All tasks are stored in a local JSON file (`tasks.json`) so that data is preserved between sessions.

### Technologies Used
- `Python 3.11`
- `Tkinter` for GUI
- `requests` for Canvas API calls
- `datetime` for parsing and formatting due dates
- `json` and `os` for file management

### Canvas API Integration
To enable Canvas syncing, users can generate a personal access token from their UMD ELMS account and paste it into the app. The app then:
- Connects to the Canvas REST API
- Retrieves current active courses (filtered by term)
- Imports only assignments with due dates
- Avoids duplicating previously synced assignments

> **Note:** UMD student credentials are never stored or accessed — only Canvas access tokens are used in memory during sync.

---

### Inspiration
SmartTask was inspired by the need for a unified platform that combines personal task management with automated school assignment syncing. Instead of switching between a planner, to-do list, and Canvas, students can use a single app to stay on top of everything.

---

### Future Improvements
- Deploy as a web app for cross-platform access
- User accounts and cloud sync
- Google Calendar integration
- Task difficulty levels and prioritization AI
