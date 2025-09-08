import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Roothub Tech Space - Attendance System")
        self.root.geometry("1200x800")
        self.root.resizable(True, True) 
        
        # Theme variables
        self.is_dark_mode = False
        self.setup_themes()
        
        # File-based storage
        self.data_file = "roothub_attendance_records.txt"
        self.setup_file_storage()
        
        # Setup GUI
        self.setup_gui()
        self.apply_theme()
        
    def setup_themes(self):
        """Define light and dark theme colors"""
        self.light_theme = {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8fafc',
            'bg_accent': '#e2e8f0',
            'text_primary': '#1a202c',
            'text_secondary': '#4a5568',
            'button_primary': '#3182ce',
            'button_secondary': '#e2e8f0',
            'button_hover': '#2c5282',
            'success': '#38a169',
            'warning': '#d69e2e',
            'error': '#e53e3e'
        }
        
        self.dark_theme = {
            'bg_primary': '#1a202c',
            'bg_secondary': '#2d3748',
            'bg_accent': '#4a5568',
            'text_primary': '#f7fafc',
            'text_secondary': '#e2e8f0',
            'button_primary': '#4299e1',
            'button_secondary': '#4a5568',
            'button_hover': '#3182ce',
            'success': '#48bb78',
            'warning': '#ed8936',
            'error': '#f56565'
        }
        
        self.current_theme = self.light_theme
        
    def setup_file_storage(self):
        """Setup file-based storage system"""
        self.data_structure = {
            "users": {},
            "attendance": [],
            "next_attendance_id": 1
        }
        
        # Load existing data or create new file
        self.load_data()
        
    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data_structure = json.load(f)
                    # Ensure all required keys exist
                    if "next_attendance_id" not in self.data_structure:
                        self.data_structure["next_attendance_id"] = len(self.data_structure.get("attendance", [])) + 1
            else:
                self.save_data()  # Create initial file
        except Exception as e:
            messagebox.showerror("File Error", f"Error loading data file: {e}")
            
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data_structure, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            messagebox.showerror("File Error", f"Error saving data: {e}")
        
    def setup_gui(self):
        """Setup the main GUI components"""
        # Main container
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.setup_header()
        
        # Content area with notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Check-in tab
        self.checkin_frame = tk.Frame(self.notebook)
        self.notebook.add(self.checkin_frame, text="Check In/Out")
        self.setup_checkin_tab()
        
        # Records tab
        self.records_frame = tk.Frame(self.notebook)
        self.notebook.add(self.records_frame, text="View Records")
        self.setup_records_tab()
        
    def setup_header(self):
        """Setup the header with title and theme toggle"""
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo and title
        title_frame = tk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        self.title_label = tk.Label(
            title_frame,
            text="🏢 Roothub Tech Space",
            font=("Segoe UI", 24, "bold")
        )
        self.title_label.pack(anchor=tk.W)
        
        self.subtitle_label = tk.Label(
            title_frame,
            text="Attendance Management System",
            font=("Segoe UI", 12)
        )
        self.subtitle_label.pack(anchor=tk.W)
        
        # File info and theme toggle buttons
        buttons_frame = tk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        # File info button
        self.file_info_button = tk.Button(
            buttons_frame,
            text="📁 File Info",
            command=self.show_file_info,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        self.file_info_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Theme toggle button
        self.theme_button = tk.Button(
            buttons_frame,
            text="🌙 Dark Mode",
            command=self.toggle_theme,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        self.theme_button.pack(side=tk.LEFT)
        
    def setup_checkin_tab(self):
        """Setup the check-in/check-out tab"""
        # Create main container with padding
        container = tk.Frame(self.checkin_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Input form
        form_frame = tk.Frame(container)
        form_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Name field
        tk.Label(form_frame, text="Full Name:", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.name_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=30)
        self.name_entry.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(0, 15))
        
        # ID field
        tk.Label(form_frame, text="Student/Staff ID:", font=("Segoe UI", 12, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.id_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=30)
        self.id_entry.grid(row=3, column=0, sticky=tk.W+tk.E, pady=(0, 15))
        
        # Course field
        tk.Label(form_frame, text="Course/Department:", font=("Segoe UI", 12, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.course_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=30)
        self.course_entry.grid(row=5, column=0, sticky=tk.W+tk.E, pady=(0, 15))
        
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Current time display
        self.time_frame = tk.Frame(container)
        self.time_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.current_time_label = tk.Label(
            self.time_frame,
            text="",
            font=("Segoe UI", 14, "bold")
        )
        self.current_time_label.pack()
        
        # Update time every second
        self.update_time()
        
        # Buttons frame
        buttons_frame = tk.Frame(container)
        buttons_frame.pack(fill=tk.X)
        
        self.checkin_button = tk.Button(
            buttons_frame,
            text="📍 Check In",
            command=self.check_in,
            font=("Segoe UI", 14, "bold"),
            height=2,
            relief=tk.FLAT
        )
        self.checkin_button.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.checkout_button = tk.Button(
            buttons_frame,
            text="🚪 Check Out",
            command=self.check_out,
            font=("Segoe UI", 14, "bold"),
            height=2,
            relief=tk.FLAT
        )
        self.checkout_button.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        # Status display
        self.status_label = tk.Label(
            container,
            text="Ready to check in",
            font=("Segoe UI", 12),
            pady=20
        )
        self.status_label.pack()
        
    def setup_records_tab(self):
        """Setup the records viewing tab"""
        # Search frame
        search_frame = tk.Frame(self.records_frame)
        search_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(search_frame, text="Search by ID:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        search_button = tk.Button(
            search_frame,
            text="🔍 Search",
            command=self.search_records,
            font=("Segoe UI", 10),
            relief=tk.FLAT
        )
        search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_button = tk.Button(
            search_frame,
            text="🔄 Refresh",
            command=self.load_records,
            font=("Segoe UI", 10),
            relief=tk.FLAT
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        export_button = tk.Button(
            search_frame,
            text="📊 Export CSV",
            command=self.export_records,
            font=("Segoe UI", 10),
            relief=tk.FLAT
        )
        export_button.pack(side=tk.LEFT)
        
        # Records tree
        tree_frame = tk.Frame(self.records_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.records_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Name", "Course", "Date", "Time In", "Time Out", "Duration"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Configure scrollbars
        v_scrollbar.config(command=self.records_tree.yview)
        h_scrollbar.config(command=self.records_tree.xview)
        
        # Column headings
        self.records_tree.heading("ID", text="ID")
        self.records_tree.heading("Name", text="Name")
        self.records_tree.heading("Course", text="Course")
        self.records_tree.heading("Date", text="Date")
        self.records_tree.heading("Time In", text="Time In")
        self.records_tree.heading("Time Out", text="Time Out")
        self.records_tree.heading("Duration", text="Duration")
        
        # Column widths
        self.records_tree.column("ID", width=100)
        self.records_tree.column("Name", width=150)
        self.records_tree.column("Course", width=120)
        self.records_tree.column("Date", width=100)
        self.records_tree.column("Time In", width=120)
        self.records_tree.column("Time Out", width=120)
        self.records_tree.column("Duration", width=100)
        
        # Pack treeview and scrollbars
        self.records_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Load initial records
        self.load_records()
        
    def update_time(self):
        """Update the current time display"""
        current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M:%S %p")
        self.current_time_label.config(text=f"Current Time: {current_time}")
        self.root.after(1000, self.update_time)
        
    def check_in(self):
        """Handle check-in process"""
        name = self.name_entry.get().strip()
        user_id = self.id_entry.get().strip()
        course = self.course_entry.get().strip()
        
        if not all([name, user_id, course]):
            messagebox.showerror("Error", "Please fill in all fields!")
            return
            
        try:
            now = datetime.now()
            date_today = now.strftime("%Y-%m-%d")
            
            # Add or update user info
            self.data_structure["users"][user_id] = {
                "name": name,
                "course": course,
                "last_updated": now.isoformat()
            }
            
            # Create attendance record
            attendance_record = {
                "id": self.data_structure["next_attendance_id"],
                "user_id": user_id,
                "name": name,
                "course": course,
                "time_in": now.isoformat(),
                "time_out": None,
                "date": date_today
            }
            
            self.data_structure["attendance"].append(attendance_record)
            self.data_structure["next_attendance_id"] += 1
            
            # Save data to file
            self.save_data()
            
            # Update UI status
            self.status_label.config(text=f"Checked in as {name} at {now.strftime('%I:%M:%S %p')}")
            
            # Clear form
            self.name_entry.delete(0, tk.END)
            self.id_entry.delete(0, tk.END)
            self.course_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Successfully checked in at {now.strftime('%I:%M:%S %p')}")
            self.load_records() # Refresh the records view
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during check-in: {e}")
            
    def check_out(self):
        """Handle check-out process"""
        user_id = self.id_entry.get().strip()
        
        if not user_id:
            messagebox.showerror("Error", "Please enter your ID to check out!")
            return
            
        try:
            now = datetime.now()
            
            # Find the most recent active attendance record for this user
            found = False
            for record in reversed(self.data_structure["attendance"]):
                if record["user_id"] == user_id and record["time_out"] is None:
                    record["time_out"] = now.isoformat()
                    found = True
                    break
            
            if not found:
                messagebox.showwarning("Warning", "No active check-in session found for this ID.")
                return
            
            # Save data to file
            self.save_data()
            
            # Update UI status
            self.status_label.config(text=f"Checked out at {now.strftime('%I:%M:%S %p')}")
            
            # Clear form
            self.name_entry.delete(0, tk.END)
            self.id_entry.delete(0, tk.END)
            self.course_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Successfully checked out at {now.strftime('%I:%M:%S %p')}")
            self.load_records()  # Refresh records
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during check-out: {e}")
            
    def load_records(self):
        """Load attendance records into the treeview"""
        try:
            # Clear existing records
            for item in self.records_tree.get_children():
                self.records_tree.delete(item)
                
            # Sort records by date and time (newest first)
            sorted_records = sorted(
                self.data_structure["attendance"],
                key=lambda x: (x["date"], x["time_in"]),
                reverse=True
            )
                
            # Insert records into treeview
            for record in sorted_records:
                time_in = datetime.fromisoformat(record["time_in"])
                time_out = datetime.fromisoformat(record["time_out"]) if record["time_out"] else None
                
                # Calculate duration if checked out
                duration = ""
                if time_out:
                    delta = time_out - time_in
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    duration = f"{hours}h {minutes}m"
                else:
                    duration = "Still in"
                
                time_in_str = time_in.strftime('%I:%M:%S %p')
                time_out_str = time_out.strftime('%I:%M:%S %p') if time_out else ""
                
                self.records_tree.insert("", tk.END, values=(
                    record["user_id"],
                    record["name"],
                    record["course"],
                    record["date"],
                    time_in_str,
                    time_out_str,
                    duration
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading records: {e}")
            
    def search_records(self):
        """Search records by user ID"""
        search_id = self.search_entry.get().strip()
        if not search_id:
            self.load_records()
            return
            
        try:
            # Clear existing records
            for item in self.records_tree.get_children():
                self.records_tree.delete(item)
                
            # Filter and sort records
            filtered_records = [
                record for record in self.data_structure["attendance"]
                if search_id.lower() in record["user_id"].lower()
            ]
            
            sorted_records = sorted(
                filtered_records,
                key=lambda x: (x["date"], x["time_in"]),
                reverse=True
            )
                
            # Insert filtered records
            for record in sorted_records:
                time_in = datetime.fromisoformat(record["time_in"])
                time_out = datetime.fromisoformat(record["time_out"]) if record["time_out"] else None
                
                duration = ""
                if time_out:
                    delta = time_out - time_in
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    duration = f"{hours}h {minutes}m"
                else:
                    duration = "Still in"
                
                time_in_str = time_in.strftime('%I:%M:%S %p')
                time_out_str = time_out.strftime('%I:%M:%S %p') if time_out else ""
                
                self.records_tree.insert("", tk.END, values=(
                    record["user_id"],
                    record["name"],
                    record["course"],
                    record["date"],
                    time_in_str,
                    time_out_str,
                    duration
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error searching records: {e}")
    
    def export_records(self):
        """Export records to CSV file"""
        try:
            import csv
            from tkinter import filedialog
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Attendance Records"
            )
            
            if not filename:
                return
                
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Name', 'Course', 'Date', 'Time In', 'Time Out', 'Duration']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                # Sort records by date and time
                sorted_records = sorted(
                    self.data_structure["attendance"],
                    key=lambda x: (x["date"], x["time_in"]),
                    reverse=True
                )
                
                for record in sorted_records:
                    time_in = datetime.fromisoformat(record["time_in"])
                    time_out = datetime.fromisoformat(record["time_out"]) if record["time_out"] else None
                    
                    duration = ""
                    if time_out:
                        delta = time_out - time_in
                        hours, remainder = divmod(delta.seconds, 3600)
                        minutes, _ = divmod(remainder, 60)
                        duration = f"{hours}h {minutes}m"
                    else:
                        duration = "Still in"
                    
                    writer.writerow({
                        'ID': record["user_id"],
                        'Name': record["name"],
                        'Course': record["course"],
                        'Date': record["date"],
                        'Time In': time_in.strftime('%I:%M:%S %p'),
                        'Time Out': time_out.strftime('%I:%M:%S %p') if time_out else "",
                        'Duration': duration
                    })
                    
            messagebox.showinfo("Success", f"Records exported successfully to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting records: {e}")
    
    def show_file_info(self):
        """Show information about the data file"""
        try:
            file_size = os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0
            total_users = len(self.data_structure["users"])
            total_records = len(self.data_structure["attendance"])
            
            # Count active sessions
            active_sessions = sum(1 for record in self.data_structure["attendance"] if record["time_out"] is None)
            
            info_text = f"""Data File Information:
            
📁 File: {self.data_file}
📊 File Size: {file_size:,} bytes
👥 Total Users: {total_users}
📋 Total Records: {total_records}
🟢 Active Sessions: {active_sessions}

File Location: {os.path.abspath(self.data_file)}"""
            
            messagebox.showinfo("File Information", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error getting file info: {e}")
            
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = self.dark_theme if self.is_dark_mode else self.light_theme
        self.apply_theme()
        
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        theme = self.current_theme
        
        # Update theme button text
        self.theme_button.config(text="☀️ Light Mode" if self.is_dark_mode else "🌙 Dark Mode")
        
        # Main window and frames
        self.root.config(bg=theme['bg_secondary'])
        self.main_frame.config(bg=theme['bg_secondary'])
        
        # Header
        for widget in [self.title_label, self.subtitle_label]:
            widget.config(bg=theme['bg_secondary'], fg=theme['text_primary'])
            
        # Header buttons
        for button in [self.theme_button, self.file_info_button]:
            button.config(
                bg=theme['button_secondary'],
                fg=theme['text_primary'],
                activebackground=theme['button_hover'],
                activeforeground=theme['text_primary']
            )
        
        # Apply theme to all frames and widgets recursively
        self._apply_theme_recursive(self.checkin_frame, theme)
        self._apply_theme_recursive(self.records_frame, theme)
        
        # Special handling for main buttons
        self.checkin_button.config(
            bg=theme['success'],
            fg='white',
            activebackground=theme['success'],
            activeforeground='white'
        )
        
        self.checkout_button.config(
            bg=theme['warning'],
            fg='white',
            activebackground=theme['warning'],
            activeforeground='white'
        )
        
    def _apply_theme_recursive(self, widget, theme):
        """Recursively apply theme to widget and its children"""
        try:
            widget_class = widget.winfo_class()
            
            if widget_class in ['Frame', 'Toplevel']:
                widget.config(bg=theme['bg_primary'])
            elif widget_class == 'Label':
                widget.config(bg=theme['bg_primary'], fg=theme['text_primary'])
            elif widget_class == 'Entry':
                widget.config(
                    bg=theme['bg_secondary'],
                    fg=theme['text_primary'],
                    insertbackground=theme['text_primary'],
                    selectbackground=theme['button_primary'],
                    selectforeground='white'
                )
            elif widget_class == 'Button':
                if widget not in [self.checkin_button, self.checkout_button, self.theme_button, self.file_info_button]:
                    widget.config(
                        bg=theme['button_primary'],
                        fg='white',
                        activebackground=theme['button_hover'],
                        activeforeground='white'
                    )
        except tk.TclError:
            pass
            
        # Apply to children
        for child in widget.winfo_children():
            self._apply_theme_recursive(child, theme)

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    try:
        app = AttendanceSystem(root)
        
        # Center the window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()