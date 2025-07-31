import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import json
import csv
import os
from pathlib import Path

class ModernStyle:
    """Custom styling for the modern UI"""
    
    # Color palette matching the HTML design
    COLORS = {
        'primary': '#075e54',
        'secondary': '#128c7e', 
        'accent': '#25d366',
        'background': '#f0f0f0',
        'card_bg': '#ffffff',
        'text_primary': '#333333',
        'text_secondary': '#666666',
        'border': '#dee2e6',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8'
    }

class WhatsAppEngagementUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WATRHC WhatsApp Engagement Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg=ModernStyle.COLORS['background'])
        
        # Initialize data
        self.contacts_data = [
            {'Name': 'John Doe', 'Phone': '+234 801 234 5678', 'Labels': 'WATRHC, Python Learner', 'Last Contact': '2025-07-30', 'Status': 'Active'},
            {'Name': 'Jane Smith', 'Phone': '+234 802 345 6789', 'Labels': 'WATRHC, UI/UX Learner', 'Last Contact': '2025-07-29', 'Status': 'Active'},
            {'Name': 'Mike Johnson', 'Phone': '+234 803 456 7890', 'Labels': 'WATRHC, Data Science, Follow-up', 'Last Contact': 'Never', 'Status': 'Inactive'}
        ]
        self.scheduled_messages = []
        self.message_log = [
            {'Timestamp': '2025-07-31 09:15:23', 'Type': 'DM', 'Recipient': 'John Doe', 'Message': 'Hi John! 👋🏼 Welcome to the RootHub Community...', 'Status': '✅ Sent'},
            {'Timestamp': '2025-07-31 09:14:45', 'Type': 'Group', 'Recipient': 'Python Class A', 'Message': '🌟 Good morning Python learners! Today\'s tip...', 'Status': '✅ Sent'},
            {'Timestamp': '2025-07-31 09:13:12', 'Type': 'DM', 'Recipient': 'Jane Smith', 'Message': 'Hi Jane! Just checking in from the RootHub...', 'Status': '⏳ Pending'},
            {'Timestamp': '2025-07-31 09:12:01', 'Type': 'DM', 'Recipient': 'Mike Johnson', 'Message': 'Hey Mike! 📚 Don\'t forget about today\'s...', 'Status': '❌ Failed'}
        ]
        
        self.setup_styles()
        self.create_header()
        self.create_main_container()
        self.create_status_bar()
        
    def setup_styles(self):
        """Configure custom styles for modern look"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Header style
        self.style.configure('Header.TFrame', 
                           background=ModernStyle.COLORS['primary'])
        
        self.style.configure('Header.TLabel', 
                           background=ModernStyle.COLORS['primary'],
                           foreground='white',
                           font=('Segoe UI', 18, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           background=ModernStyle.COLORS['primary'],
                           foreground='white',
                           font=('Segoe UI', 10))
        
        # Tab styles to match the HTML design
        self.style.configure('Modern.TNotebook', 
                           background=ModernStyle.COLORS['card_bg'],
                           borderwidth=0)
        
        self.style.configure('Modern.TNotebook.Tab',
                           background='#f8f9fa',
                           foreground=ModernStyle.COLORS['text_primary'],
                           padding=[20, 12],
                           font=('Segoe UI', 10, 'normal'))
        
        self.style.map('Modern.TNotebook.Tab',
                      background=[('selected', ModernStyle.COLORS['card_bg']),
                                ('active', '#e9ecef')])
        
        # Button styles
        self.style.configure('Modern.TButton',
                           background=ModernStyle.COLORS['accent'],
                           foreground='white',
                           font=('Segoe UI', 9, 'bold'),
                           borderwidth=0,
                           focuscolor='none',
                           padding=(15, 8))
        
        self.style.map('Modern.TButton',
                      background=[('active', ModernStyle.COLORS['secondary'])])
        
        # Secondary button
        self.style.configure('Secondary.TButton',
                           background='#6c757d',
                           foreground='white',
                           font=('Segoe UI', 9, 'bold'),
                           borderwidth=0,
                           focuscolor='none',
                           padding=(15, 8))
        
        # Danger button
        self.style.configure('Danger.TButton',
                           background=ModernStyle.COLORS['danger'],
                           foreground='white',
                           font=('Segoe UI', 9, 'bold'),
                           borderwidth=0,
                           focuscolor='none',
                           padding=(15, 8))
        
        # Frame styles
        self.style.configure('Card.TFrame',
                           background=ModernStyle.COLORS['card_bg'],
                           relief='flat',
                           borderwidth=1,
                           lightcolor=ModernStyle.COLORS['border'],
                           darkcolor=ModernStyle.COLORS['border'])
        
        # Label styles
        self.style.configure('SectionTitle.TLabel',
                           background=ModernStyle.COLORS['card_bg'],
                           foreground=ModernStyle.COLORS['primary'],
                           font=('Segoe UI', 12, 'bold'))
        
        self.style.configure('StatNumber.TLabel',
                           background=ModernStyle.COLORS['card_bg'],
                           foreground=ModernStyle.COLORS['primary'],
                           font=('Segoe UI', 24, 'bold'))
        
        self.style.configure('StatLabel.TLabel',
                           background=ModernStyle.COLORS['card_bg'],
                           foreground=ModernStyle.COLORS['text_secondary'],
                           font=('Segoe UI', 9))
        
        # Treeview styles
        self.style.configure('Modern.Treeview',
                           background=ModernStyle.COLORS['card_bg'],
                           foreground=ModernStyle.COLORS['text_primary'],
                           fieldbackground=ModernStyle.COLORS['card_bg'],
                           borderwidth=0,
                           font=('Segoe UI', 9))
        
        self.style.configure('Modern.Treeview.Heading',
                           background='#f8f9fa',
                           foreground=ModernStyle.COLORS['primary'],
                           font=('Segoe UI', 10, 'bold'),
                           borderwidth=1,
                           relief='flat')
    
    def create_header(self):
        """Create the beautiful header section"""
        header_frame = tk.Frame(self.root, bg=ModernStyle.COLORS['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Create gradient effect with multiple frames
        gradient_frame = tk.Frame(header_frame, bg=ModernStyle.COLORS['primary'])
        gradient_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(gradient_frame, 
                              text="🚀 WATRHC WhatsApp Engagement Assistant",
                              bg=ModernStyle.COLORS['primary'],
                              fg='white',
                              font=('Segoe UI', 18, 'bold'))
        title_label.pack(pady=(15, 5))
        
        # Subtitle
        subtitle_label = tk.Label(gradient_frame,
                                 text="Automate community engagement for 530+ learners across 11 tracks",
                                 bg=ModernStyle.COLORS['primary'],
                                 fg='white',
                                 font=('Segoe UI', 10))
        subtitle_label.pack()
    
    def create_main_container(self):
        """Create the main content area with tabs"""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=ModernStyle.COLORS['background'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create notebook with modern styling
        self.notebook = ttk.Notebook(main_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # Create all tabs
        self.create_contacts_tab()
        self.create_dm_automation_tab()
        self.create_group_scheduler_tab()
        self.create_logs_tab()
        self.create_settings_tab()
    
    def create_card_frame(self, parent, title):
        """Create a modern card-style frame"""
        card = tk.Frame(parent, bg=ModernStyle.COLORS['card_bg'], 
                       relief='flat', bd=1,
                       highlightbackground=ModernStyle.COLORS['border'],
                       highlightthickness=1)
        
        if title:
            title_frame = tk.Frame(card, bg=ModernStyle.COLORS['card_bg'])
            title_frame.pack(fill='x', padx=20, pady=(15, 0))
            
            title_label = tk.Label(title_frame, text=title,
                                  bg=ModernStyle.COLORS['card_bg'],
                                  fg=ModernStyle.COLORS['primary'],
                                  font=('Segoe UI', 12, 'bold'))
            title_label.pack(anchor='w')
            
            # Add underline
            separator = tk.Frame(title_frame, height=2, 
                               bg=ModernStyle.COLORS['accent'])
            separator.pack(fill='x', pady=(5, 15))
        
        return card
    
    def create_contacts_tab(self):
        """Create the contacts management tab"""
        contacts_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['background'])
        self.notebook.add(contacts_frame, text="📱 Contacts & Labels")
        
        # Import section
        import_card = self.create_card_frame(contacts_frame, "Import Contacts")
        import_card.pack(fill='x', pady=(0, 15))
        
        button_frame = tk.Frame(import_card, bg=ModernStyle.COLORS['card_bg'])
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(button_frame, text="📄 Import from CSV", 
                  style='Modern.TButton',
                  command=self.import_contacts_csv).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="📊 Import from Google Sheets", 
                  style='Modern.TButton',
                  command=self.import_google_sheets).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="➕ Add Contact Manually", 
                  style='Modern.TButton',
                  command=self.add_contact_manual).pack(side='left')
        
        # Contacts overview
        overview_card = self.create_card_frame(contacts_frame, "Contacts Overview")
        overview_card.pack(fill='both', expand=True)
        
        # Create treeview for contacts
        tree_frame = tk.Frame(overview_card, bg=ModernStyle.COLORS['card_bg'])
        tree_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        columns = ('Name', 'Phone', 'Labels', 'Last Contact', 'Status')
        self.contacts_tree = ttk.Treeview(tree_frame, columns=columns, 
                                         show='headings', style='Modern.Treeview')
        
        # Configure columns
        for col in columns:
            self.contacts_tree.heading(col, text=col)
            self.contacts_tree.column(col, width=150, anchor='w')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', 
                                   command=self.contacts_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', 
                                   command=self.contacts_tree.xview)
        
        self.contacts_tree.configure(yscrollcommand=v_scrollbar.set,
                                    xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.contacts_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        
        # Action buttons
        action_frame = tk.Frame(tree_frame, bg=ModernStyle.COLORS['card_bg'])
        action_frame.pack(side='right', fill='y', padx=(10, 0))
        
        ttk.Button(action_frame, text="✏️ Edit", 
                  style='Modern.TButton',
                  command=self.edit_contact).pack(pady=5, fill='x')
        ttk.Button(action_frame, text="🏷️ Labels", 
                  style='Secondary.TButton',
                  command=self.manage_labels).pack(pady=5, fill='x')
        ttk.Button(action_frame, text="🗑️ Delete", 
                  style='Danger.TButton',
                  command=self.delete_contact).pack(pady=5, fill='x')
        
        # Populate with sample data
        self.refresh_contacts_display()
    
    def create_dm_automation_tab(self):
        """Create the DM automation tab"""
        dm_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['background'])
        self.notebook.add(dm_frame, text="💬 DM Automation")
        
        # Message templates card
        template_card = self.create_card_frame(dm_frame, "Message Templates")
        template_card.pack(fill='x', pady=(0, 15))
        
        template_content = tk.Frame(template_card, bg=ModernStyle.COLORS['card_bg'])
        template_content.pack(fill='x', padx=20, pady=(0, 20))
        
        # Template selection
        tk.Label(template_content, text="Select Template:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(template_content, textvariable=self.template_var,
                                     values=['Welcome Message', 'Check-in Message', 
                                            'Course Reminder', 'Follow-up', 'Custom'],
                                     font=('Segoe UI', 10))
        template_combo.pack(fill='x', pady=(0, 15))
        template_combo.bind('<<ComboboxSelected>>', self.load_template)
        
        # Message content
        tk.Label(template_content, text="Message Content:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.message_text = tk.Text(template_content, height=6, wrap='word',
                                   font=('Segoe UI', 10),
                                   bg=ModernStyle.COLORS['card_bg'],
                                   fg=ModernStyle.COLORS['text_primary'],
                                   relief='solid', bd=1)
        self.message_text.pack(fill='x', pady=(0, 10))
        
        # Set default message
        default_msg = "Hi {name}! 👋🏼 Welcome to the RootHub Community! I'm Hannah, your community manager. I'm here to support you on your {track} learning journey. Feel free to reach out if you have any questions!"
        self.message_text.insert('1.0', default_msg)
        
        # Personalization buttons
        personalization_frame = tk.Frame(template_content, bg=ModernStyle.COLORS['card_bg'])
        personalization_frame.pack(fill='x')
        
        tk.Label(personalization_frame, text="Personalization:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(side='left')
        
        tag_btn1 = tk.Button(personalization_frame, text="Add {name}",
                           bg='#e3f2fd', fg='#2196f3',
                           font=('Segoe UI', 9), relief='solid', bd=1,
                           padx=10, pady=5,
                           command=lambda: self.insert_placeholder('{name}'))
        tag_btn1.pack(side='left', padx=(10, 5))
        
        tag_btn2 = tk.Button(personalization_frame, text="Add {track}",
                           bg='#e3f2fd', fg='#2196f3',
                           font=('Segoe UI', 9), relief='solid', bd=1,
                           padx=10, pady=5,
                           command=lambda: self.insert_placeholder('{track}'))
        tag_btn2.pack(side='left', padx=5)
        
        # Target audience card
        target_card = self.create_card_frame(dm_frame, "Target Audience")
        target_card.pack(fill='x', pady=(0, 15))
        
        target_content = tk.Frame(target_card, bg=ModernStyle.COLORS['card_bg'])
        target_content.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(target_content, text="Send to contacts with labels:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.labels_var = tk.StringVar()
        labels_combo = ttk.Combobox(target_content, textvariable=self.labels_var,
                                   values=['WATRHC', 'UI/UX Learner', 'Python Learner',
                                          'Data Science', 'Follow-up', 'No Response'],
                                   font=('Segoe UI', 10))
        labels_combo.pack(fill='x')
        
        # Send options card
        send_card = self.create_card_frame(dm_frame, "Send Options")
        send_card.pack(fill='x')
        
        send_content = tk.Frame(send_card, bg=ModernStyle.COLORS['card_bg'])
        send_content.pack(fill='x', padx=20, pady=(0, 20))
        
        delay_frame = tk.Frame(send_content, bg=ModernStyle.COLORS['card_bg'])
        delay_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(delay_frame, text="Delay between messages (seconds):",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(side='left')
        
        self.delay_var = tk.StringVar(value="45")
        delay_spinbox = tk.Spinbox(delay_frame, from_=30, to=300, 
                                  textvariable=self.delay_var, width=10,
                                  font=('Segoe UI', 10))
        delay_spinbox.pack(side='left', padx=(10, 0))
        
        # Send buttons
        button_frame = tk.Frame(send_content, bg=ModernStyle.COLORS['card_bg'])
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="📋 Preview Recipients", 
                  style='Secondary.TButton',
                  command=self.preview_recipients).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="📤 Send Now", 
                  style='Modern.TButton',
                  command=self.send_dm_now).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="⏰ Schedule for Later", 
                  style='Secondary.TButton',
                  command=self.schedule_dm).pack(side='left')
    
    def create_group_scheduler_tab(self):
        """Create the group scheduler tab"""
        scheduler_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['background'])
        self.notebook.add(scheduler_frame, text="👥 Group Scheduler")
        
        # Group selection card
        group_card = self.create_card_frame(scheduler_frame, "Select Group")
        group_card.pack(fill='x', pady=(0, 15))
        
        group_content = tk.Frame(group_card, bg=ModernStyle.COLORS['card_bg'])
        group_content.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(group_content, text="WhatsApp Group:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.group_var = tk.StringVar()
        group_combo = ttk.Combobox(group_content, textvariable=self.group_var,
                                  values=['Python Class A', 'Python Class B', 
                                         'UI/UX Design Track', 'Data Science Track',
                                         'Digital Marketing', 'General Announcements'],
                                  font=('Segoe UI', 10))
        group_combo.pack(fill='x')
        
        # Message content card
        message_card = self.create_card_frame(scheduler_frame, "Message Content")
        message_card.pack(fill='both', expand=True, pady=(0, 15))
        
        message_content = tk.Frame(message_card, bg=ModernStyle.COLORS['card_bg'])
        message_content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(message_content, text="Message Type:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.group_msg_type = tk.StringVar()
        type_combo = ttk.Combobox(message_content, textvariable=self.group_msg_type,
                                 values=['Daily Tip', 'Weekly Quiz', 'Motivational Message',
                                        'Course Update', 'Custom'],
                                 font=('Segoe UI', 10))
        type_combo.pack(fill='x', pady=(0, 15))
        
        tk.Label(message_content, text="Message:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.group_message_text = tk.Text(message_content, height=8, wrap='word',
                                         font=('Segoe UI', 10),
                                         bg=ModernStyle.COLORS['card_bg'],
                                         fg=ModernStyle.COLORS['text_primary'],
                                         relief='solid', bd=1)
        self.group_message_text.pack(fill='both', expand=True)
        
        # Set default group message
        default_group_msg = """🌟 Good morning Python learners! 

Today's tip: Remember that practice makes perfect. Try to code for at least 30 minutes today, even if it's just reviewing yesterday's concepts.

💪 You've got this! Keep pushing forward on your learning journey.

#PythonTip #KeepLearning #RootHubCommunity"""
        self.group_message_text.insert('1.0', default_group_msg)
        
        # Schedule options card
        schedule_card = self.create_card_frame(scheduler_frame, "Schedule Options")
        schedule_card.pack(fill='x')
        
        schedule_content = tk.Frame(schedule_card, bg=ModernStyle.COLORS['card_bg'])
        schedule_content.pack(fill='x', padx=20, pady=(0, 20))
        
        # Date and time row
        datetime_frame = tk.Frame(schedule_content, bg=ModernStyle.COLORS['card_bg'])
        datetime_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(datetime_frame, text="Date:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(side='left')
        
        self.schedule_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(datetime_frame, textvariable=self.schedule_date,
                             font=('Segoe UI', 10), width=12)
        date_entry.pack(side='left', padx=(10, 30))
        
        tk.Label(datetime_frame, text="Time:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(side='left')
        
        self.schedule_time = tk.StringVar(value="09:00")
        time_entry = tk.Entry(datetime_frame, textvariable=self.schedule_time,
                             font=('Segoe UI', 10), width=8)
        time_entry.pack(side='left', padx=(10, 0))
        
        # Recurring options
        recurring_frame = tk.Frame(schedule_content, bg=ModernStyle.COLORS['card_bg'])
        recurring_frame.pack(fill='x', pady=(0, 15))
        
        self.recurring_var = tk.BooleanVar()
        recurring_check = tk.Checkbutton(recurring_frame, text="Recurring message",
                                        variable=self.recurring_var,
                                        bg=ModernStyle.COLORS['card_bg'],
                                        fg=ModernStyle.COLORS['text_primary'],
                                        font=('Segoe UI', 10))
        recurring_check.pack(side='left')
        
        tk.Label(recurring_frame, text="Frequency:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(side='left', padx=(20, 10))
        
        self.frequency_var = tk.StringVar()
        frequency_combo = ttk.Combobox(recurring_frame, textvariable=self.frequency_var,
                                      values=['Daily', 'Weekly', 'Monthly'],
                                      width=15, font=('Segoe UI', 10))
        frequency_combo.pack(side='left')
        
        # Schedule button
        ttk.Button(schedule_content, text="📅 Schedule Message", 
                  style='Modern.TButton',
                  command=self.schedule_group_message).pack(pady=(0, 10))
    
    def create_logs_tab(self):
        """Create the logs and analytics tab"""
        logs_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['background'])
        self.notebook.add(logs_frame, text="📊 Logs & Analytics")
        
        # Statistics cards
        stats_frame = tk.Frame(logs_frame, bg=ModernStyle.COLORS['background'])
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Create 4 stat cards in a grid
        stats_data = [
            ("530", "Total Contacts"),
            ("47", "Messages Sent Today"),
            ("12", "Scheduled Messages"),
            ("89%", "Engagement Rate")
        ]
        
        for i, (number, label) in enumerate(stats_data):
            stat_card = tk.Frame(stats_frame, bg=ModernStyle.COLORS['card_bg'],
                               relief='flat', bd=1,
                               highlightbackground=ModernStyle.COLORS['border'],
                               highlightthickness=1)
            stat_card.pack(side='left', fill='both', expand=True, 
                          padx=(0, 15) if i < 3 else (0, 0))
            
            # Add colored left border
            border = tk.Frame(stat_card, bg=ModernStyle.COLORS['accent'], width=4)
            border.pack(side='left', fill='y')
            
            content = tk.Frame(stat_card, bg=ModernStyle.COLORS['card_bg'])
            content.pack(side='left', fill='both', expand=True, padx=20, pady=20)
            
            number_label = tk.Label(content, text=number,
                                   bg=ModernStyle.COLORS['card_bg'],
                                   fg=ModernStyle.COLORS['primary'],
                                   font=('Segoe UI', 24, 'bold'))
            number_label.pack()
            
            label_label = tk.Label(content, text=label,
                                  bg=ModernStyle.COLORS['card_bg'],
                                  fg=ModernStyle.COLORS['text_secondary'],
                                  font=('Segoe UI', 9))
            label_label.pack()
        
        # Message log card
        log_card = self.create_card_frame(logs_frame, "Message Log")
        log_card.pack(fill='both', expand=True)
        
        log_content = tk.Frame(log_card, bg=ModernStyle.COLORS['card_bg'])
        log_content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Log treeview
        log_columns = ('Timestamp', 'Type', 'Recipient', 'Message Preview', 'Status')
        self.log_tree = ttk.Treeview(log_content, columns=log_columns, 
                                    show='headings', style='Modern.Treeview')
        
        # Configure log columns
        for col in log_columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150, anchor='w')
        
        # Log scrollbar
        log_scrollbar = ttk.Scrollbar(log_content, orient='vertical', 
                                     command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=log_scrollbar.set)
        
        # Pack log treeview
        self.log_tree.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Export buttons
        export_frame = tk.Frame(log_content, bg=ModernStyle.COLORS['card_bg'])
        export_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        ttk.Button(export_frame, text="📄 Export Log to CSV", 
                  style='Modern.TButton',
                  command=self.export_log).pack(side='left', padx=(0, 10))
        ttk.Button(export_frame, text="🗑️ Clear Log", 
                  style='Danger.TButton',
                  command=self.clear_log).pack(side='left')
        
        # Populate log with sample data
        self.refresh_log_display()
    
    def create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = tk.Frame(self.notebook, bg=ModernStyle.COLORS['background'])
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # WhatsApp Web settings card
        whatsapp_card = self.create_card_frame(settings_frame, "WhatsApp Web Settings")
        whatsapp_card.pack(fill='x', pady=(0, 15))
        
        whatsapp_content = tk.Frame(whatsapp_card, bg=ModernStyle.COLORS['card_bg'])
        whatsapp_content.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(whatsapp_content, text="Browser:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.browser_var = tk.StringVar(value="Chrome")
        browser_combo = ttk.Combobox(whatsapp_content, textvariable=self.browser_var,
                                    values=['Chrome', 'Firefox', 'Edge'],
                                    font=('Segoe UI', 10))
        browser_combo.pack(fill='x', pady=(0, 15))
        
        tk.Label(whatsapp_content, text="Wait time for page load (seconds):",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.wait_time_var = tk.StringVar(value="10")
        wait_spinbox = tk.Spinbox(whatsapp_content, from_=5, to=30, 
                                 textvariable=self.wait_time_var,
                                 font=('Segoe UI', 10))
        wait_spinbox.pack(fill='x')
        
        # Automation settings card
        automation_card = self.create_card_frame(settings_frame, "Automation Settings")
        automation_card.pack(fill='x', pady=(0, 15))
        
        automation_content = tk.Frame(automation_card, bg=ModernStyle.COLORS['card_bg'])
        automation_content.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(automation_content, text="Default delay between messages (seconds):",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.default_delay_var = tk.StringVar(value="45")
        delay_spinbox = tk.Spinbox(automation_content, from_=30, to=300, 
                                  textvariable=self.default_delay_var,
                                  font=('Segoe UI', 10))
        delay_spinbox.pack(fill='x', pady=(0, 15))
        
        tk.Label(automation_content, text="Maximum messages per session:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        
        self.max_messages_var = tk.StringVar(value="50")
        max_spinbox = tk.Spinbox(automation_content, from_=10, to=200, 
                                textvariable=self.max_messages_var,
                                font=('Segoe UI', 10))
        max_spinbox.pack(fill='x')
        
        # Data management card
        data_card = self.create_card_frame(settings_frame, "Data Management")
        data_card.pack(fill='x')
        
        data_content = tk.Frame(data_card, bg=ModernStyle.COLORS['card_bg'])
        data_content.pack(fill='x', padx=20, pady=(0, 20))
        
        button_frame = tk.Frame(data_content, bg=ModernStyle.COLORS['card_bg'])
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="🔄 Backup Data", 
                  style='Modern.TButton',
                  command=self.backup_data).pack(fill='x', pady=5)
        ttk.Button(button_frame, text="📥 Restore Data", 
                  style='Secondary.TButton',
                  command=self.restore_data).pack(fill='x', pady=5)
        ttk.Button(button_frame, text="🗑️ Reset All Data", 
                  style='Danger.TButton',
                  command=self.reset_data).pack(fill='x', pady=5)
        
        # Save settings button
        save_frame = tk.Frame(settings_frame, bg=ModernStyle.COLORS['background'])
        save_frame.pack(fill='x', pady=20)
        
        ttk.Button(save_frame, text="💾 Save Settings", 
                  style='Modern.TButton',
                  command=self.save_settings).pack()
    
    def create_status_bar(self):
        """Create the bottom status bar"""
        status_frame = tk.Frame(self.root, bg='#343a40', height=35)
        status_frame.pack(side='bottom', fill='x')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, 
                                    text="Ready to engage with your community! 🚀",
                                    bg='#343a40', fg='white',
                                    font=('Segoe UI', 9))
        self.status_label.pack(side='left', padx=20, pady=8)
        
        self.connection_label = tk.Label(status_frame, 
                                        text="WhatsApp: Disconnected ❌",
                                        bg='#343a40', fg='#dc3545',
                                        font=('Segoe UI', 9))
        self.connection_label.pack(side='right', padx=20, pady=8)
    
    # Event handlers and utility methods
    def insert_placeholder(self, placeholder):
        """Insert placeholder text at cursor position"""
        try:
            cursor_pos = self.message_text.index(tk.INSERT)
            self.message_text.insert(cursor_pos, placeholder)
        except:
            self.message_text.insert('end', placeholder)
    
    def load_template(self, event=None):
        """Load predefined message templates"""
        templates = {
            'Welcome Message': "Hi {name}! 👋🏼 Welcome to the RootHub Community! I'm Hannah, your community manager. I'm here to support you on your {track} learning journey. Feel free to reach out if you have any questions!",
            'Check-in Message': "Hi {name}! 👋🏼 Just checking in from the RootHub Community. How's your {track} learning journey going so far? Any challenges I can help you with?",
            'Course Reminder': "Hey {name}! 📚 Don't forget about today's {track} session. Looking forward to seeing your progress!",
            'Follow-up': "Hi {name}! 🤔 I noticed you haven't been active lately in our {track} community. Everything okay? I'm here if you need any support!",
        }
        
        selected = self.template_var.get()
        if selected in templates:
            self.message_text.delete('1.0', 'end')
            self.message_text.insert('1.0', templates[selected])
    
    def refresh_contacts_display(self):
        """Refresh the contacts treeview with data"""
        # Clear existing items
        for item in self.contacts_tree.get_children():
            self.contacts_tree.delete(item)
        
        # Add sample data
        for contact in self.contacts_data:
            self.contacts_tree.insert('', 'end', values=(
                contact['Name'],
                contact['Phone'],
                contact['Labels'],
                contact['Last Contact'],
                contact['Status']
            ))
    
    def refresh_log_display(self):
        """Refresh the log treeview with data"""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        # Add sample data
        for log_entry in self.message_log:
            # Truncate message preview
            message_preview = log_entry['Message']
            if len(message_preview) > 50:
                message_preview = message_preview[:50] + "..."
                
            self.log_tree.insert('', 'end', values=(
                log_entry['Timestamp'],
                log_entry['Type'],
                log_entry['Recipient'],
                message_preview,
                log_entry['Status']
            ))
    
    # Button event handlers
    def import_contacts_csv(self):
        """Import contacts from CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    imported_count = 0
                    for row in reader:
                        # Ensure required fields exist
                        contact = {
                            'Name': row.get('Name', ''),
                            'Phone': row.get('Phone', ''),
                            'Labels': row.get('Labels', ''),
                            'Last Contact': row.get('Last Contact', 'Never'),
                            'Status': row.get('Status', 'Active')
                        }
                        self.contacts_data.append(contact)
                        imported_count += 1
                
                self.refresh_contacts_display()
                self.update_status(f"Successfully imported {imported_count} contacts!")
                messagebox.showinfo("Success", f"Imported {imported_count} contacts from CSV")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
    
    def import_google_sheets(self):
        """Placeholder for Google Sheets integration"""
        messagebox.showinfo("Google Sheets", "Google Sheets integration will be implemented in the next version!")
    
    def add_contact_manual(self):
        """Open dialog to add contact manually"""
        self.open_contact_dialog()
    
    def open_contact_dialog(self, contact=None):
        """Open contact add/edit dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Contact" if not contact else "Edit Contact")
        dialog.geometry("450x350")
        dialog.configure(bg=ModernStyle.COLORS['card_bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Main content frame
        content_frame = tk.Frame(dialog, bg=ModernStyle.COLORS['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_text = "Add New Contact" if not contact else "Edit Contact"
        title_label = tk.Label(content_frame, text=title_text,
                              bg=ModernStyle.COLORS['card_bg'],
                              fg=ModernStyle.COLORS['primary'],
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Form fields
        fields = []
        
        # Name field
        tk.Label(content_frame, text="Name:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        name_var = tk.StringVar(value=contact.get('Name', '') if contact else '')
        name_entry = tk.Entry(content_frame, textvariable=name_var, 
                             font=('Segoe UI', 10))
        name_entry.pack(fill='x', pady=(0, 15))
        fields.append(('Name', name_var))
        
        # Phone field
        tk.Label(content_frame, text="Phone:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        phone_var = tk.StringVar(value=contact.get('Phone', '') if contact else '')
        phone_entry = tk.Entry(content_frame, textvariable=phone_var, 
                              font=('Segoe UI', 10))
        phone_entry.pack(fill='x', pady=(0, 15))
        fields.append(('Phone', phone_var))
        
        # Labels field
        tk.Label(content_frame, text="Labels (comma-separated):",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        labels_var = tk.StringVar(value=contact.get('Labels', '') if contact else '')
        labels_entry = tk.Entry(content_frame, textvariable=labels_var, 
                               font=('Segoe UI', 10))
        labels_entry.pack(fill='x', pady=(0, 15))
        fields.append(('Labels', labels_var))
        
        # Status field
        tk.Label(content_frame, text="Status:",
                bg=ModernStyle.COLORS['card_bg'],
                fg=ModernStyle.COLORS['text_primary'],
                font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 5))
        status_var = tk.StringVar(value=contact.get('Status', 'Active') if contact else 'Active')
        status_combo = ttk.Combobox(content_frame, textvariable=status_var,
                                   values=['Active', 'Inactive', 'Blocked'],
                                   font=('Segoe UI', 10))
        status_combo.pack(fill='x', pady=(0, 20))
        fields.append(('Status', status_var))
        
        def save_contact():
            # Validate required fields
            if not name_var.get().strip():
                messagebox.showwarning("Validation Error", "Name is required!")
                return
            
            new_contact = {}
            for field_name, field_var in fields:
                new_contact[field_name] = field_var.get().strip()
            
            new_contact['Last Contact'] = contact.get('Last Contact', 'Never') if contact else 'Never'
            
            if contact:
                # Edit existing contact
                try:
                    index = self.contacts_data.index(contact)
                    self.contacts_data[index] = new_contact
                    self.update_status("Contact updated successfully!")
                except ValueError:
                    messagebox.showerror("Error", "Contact not found!")
                    return
            else:
                # Add new contact
                self.contacts_data.append(new_contact)
                self.update_status("New contact added successfully!")
            
            self.refresh_contacts_display()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg=ModernStyle.COLORS['card_bg'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                              bg='#6c757d', fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              padx=20, pady=8,
                              relief='flat', bd=0,
                              command=cancel)
        cancel_btn.pack(side='right', padx=(10, 0))
        
        save_btn = tk.Button(button_frame, text="Save Contact",
                            bg=ModernStyle.COLORS['accent'], fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            padx=20, pady=8,
                            relief='flat', bd=0,
                            command=save_contact)
        save_btn.pack(side='right')
        
        # Focus on name field
        name_entry.focus_set()
    
    def edit_contact(self):
        """Edit selected contact"""
        selection = self.contacts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a contact to edit.")
            return
        
        item = self.contacts_tree.item(selection[0])
        contact_name = item['values'][0]
        
        # Find the contact in our data
        contact = None
        for c in self.contacts_data:
            if c['Name'] == contact_name:
                contact = c
                break
        
        if contact:
            self.open_contact_dialog(contact)
        else:
            messagebox.showerror("Error", "Contact not found!")
    
    def delete_contact(self):
        """Delete selected contact"""
        selection = self.contacts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a contact to delete.")
            return
        
        item = self.contacts_tree.item(selection[0])
        contact_name = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{contact_name}'?"):
            # Remove from data
            self.contacts_data = [c for c in self.contacts_data if c['Name'] != contact_name]
            self.refresh_contacts_display()
            self.update_status(f"Contact '{contact_name}' deleted successfully!")
    
    def manage_labels(self):
        """Placeholder for label management"""
        messagebox.showinfo("Labels", "Advanced label management feature coming soon!")
    
    def preview_recipients(self):
        """Preview recipients for DM campaign"""
        label_filter = self.labels_var.get()
        if not label_filter:
            messagebox.showwarning("No Filter", "Please select a label filter first.")
            return
        
        # Filter contacts by label
        recipients = []
        for contact in self.contacts_data:
            if label_filter.lower() in contact.get('Labels', '').lower():
                recipients.append(contact)
        
        if not recipients:
            messagebox.showinfo("No Recipients", f"No contacts found with label '{label_filter}'.")
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Recipients Preview - '{label_filter}' Label")
        preview_window.geometry("600x400")
        preview_window.configure(bg=ModernStyle.COLORS['card_bg'])
        preview_window.transient(self.root)
        
        # Center the window
        preview_window.update_idletasks()
        x = (preview_window.winfo_screenwidth() - preview_window.winfo_width()) // 2
        y = (preview_window.winfo_screenheight() - preview_window.winfo_height()) // 2
        preview_window.geometry(f"+{x}+{y}")
        
        # Content
        content_frame = tk.Frame(preview_window, bg=ModernStyle.COLORS['card_bg'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(content_frame, 
                              text=f"Recipients for '{label_filter}' Label",
                              bg=ModernStyle.COLORS['card_bg'],
                              fg=ModernStyle.COLORS['primary'],
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Recipients list
        list_frame = tk.Frame(content_frame, bg=ModernStyle.COLORS['card_bg'])
        list_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        recipients_listbox = tk.Listbox(list_frame, 
                                       yscrollcommand=scrollbar.set,
                                       font=('Segoe UI', 10),
                                       bg=ModernStyle.COLORS['card_bg'],
                                       fg=ModernStyle.COLORS['text_primary'])
        recipients_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=recipients_listbox.yview)
        
        for contact in recipients:
            recipients_listbox.insert('end', f"{contact['Name']} - {contact['Phone']}")
        
        # Summary
        summary_label = tk.Label(content_frame, 
                                text=f"Total Recipients: {len(recipients)}",
                                bg=ModernStyle.COLORS['card_bg'],
                                fg=ModernStyle.COLORS['primary'],
                                font=('Segoe UI', 12, 'bold'))
        summary_label.pack(pady=20)
        
        # Close button
        tk.Button(content_frame, text="Close",
                 bg=ModernStyle.COLORS['accent'], fg='white',
                 font=('Segoe UI', 10, 'bold'),
                 padx=20, pady=8,
                 relief='flat', bd=0,
                 command=preview_window.destroy).pack()
    
    def send_dm_now(self):
        """Start DM sending process"""
        if not self.message_text.get('1.0', 'end').strip():
            messagebox.showwarning("No Message", "Please enter a message to send.")
            return
        
        if not self.labels_var.get():
            messagebox.showwarning("No Target", "Please select a label filter.")
            return
        
        result = messagebox.askyesno("Confirm Send", 
                                    "This will start sending DMs to all contacts with the selected label. Continue?")
        if result:
            self.update_status("DM automation started! This may take a while...")
            messagebox.showinfo("DM Automation", 
                               "DM sending has started! Check the logs tab for progress updates.\n\n" +
                               "Note: Actual WhatsApp integration needs to be implemented.")
    
    def schedule_dm(self):
        """Schedule DM for later"""
        messagebox.showinfo("Schedule DM", "DM scheduling feature will be implemented with APScheduler!")
    
    def schedule_group_message(self):
        """Schedule group message"""
        if not self.group_var.get():
            messagebox.showwarning("No Group", "Please select a WhatsApp group.")
            return
        
        if not self.group_message_text.get('1.0', 'end').strip():
            messagebox.showwarning("No Message", "Please enter a message to schedule.")
            return
        
        scheduled_msg = {
            'group': self.group_var.get(),
            'message': self.group_message_text.get('1.0', 'end').strip(),
            'date': self.schedule_date.get(),
            'time': self.schedule_time.get(),
            'recurring': self.recurring_var.get(),
            'frequency': self.frequency_var.get() if self.recurring_var.get() else None,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.scheduled_messages.append(scheduled_msg)
        self.update_status(f"Message scheduled for {scheduled_msg['group']} on {scheduled_msg['date']} at {scheduled_msg['time']}")
        messagebox.showinfo("Success", 
                           f"Message scheduled for '{scheduled_msg['group']}' on {scheduled_msg['date']} at {scheduled_msg['time']}")
    
    def export_log(self):
        """Export message log to CSV"""
        if not self.message_log:
            messagebox.showinfo("No Data", "No log entries to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Message Log",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    fieldnames = ['Timestamp', 'Type', 'Recipient', 'Message', 'Status']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.message_log)
                
                self.update_status("Log exported successfully!")
                messagebox.showinfo("Success", f"Log exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export log: {str(e)}")
    
    def clear_log(self):
        """Clear all log entries"""
        if not self.message_log:
            messagebox.showinfo("No Data", "Log is already empty.")
            return
        
        if messagebox.askyesno("Confirm Clear", "This will delete all log entries. Continue?"):
            self.message_log.clear()
            self.refresh_log_display()
            self.update_status("Message log cleared successfully!")
    
    def backup_data(self):
        """Backup all application data"""
        data = {
            'contacts': self.contacts_data,
            'scheduled_messages': self.scheduled_messages,
            'message_log': self.message_log,
            'settings': {
                'browser': self.browser_var.get(),
                'wait_time': self.wait_time_var.get(),
                'default_delay': self.default_delay_var.get(),
                'max_messages': self.max_messages_var.get()
            },
            'backup_date': datetime.now().isoformat()
        }
        
        file_path = filedialog.asksaveasfilename(
            title="Backup Application Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                
                self.update_status("Data backup completed successfully!")
                messagebox.showinfo("Success", f"Data backed up to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to backup data: {str(e)}")
    
    def restore_data(self):
        """Restore application data from backup"""
        file_path = filedialog.askopenfilename(
            title="Restore Application Data",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                # Restore data
                self.contacts_data = data.get('contacts', [])
                self.scheduled_messages = data.get('scheduled_messages', [])
                self.message_log = data.get('message_log', [])
                
                # Restore settings if available
                settings = data.get('settings', {})
                if settings:
                    self.browser_var.set(settings.get('browser', 'Chrome'))
                    self.wait_time_var.set(settings.get('wait_time', '10'))
                    self.default_delay_var.set(settings.get('default_delay', '45'))
                    self.max_messages_var.set(settings.get('max_messages', '50'))
                
                # Refresh displays
                self.refresh_contacts_display()
                self.refresh_log_display()
                
                backup_date = data.get('backup_date', 'Unknown')
                self.update_status("Data restoration completed successfully!")
                messagebox.showinfo("Success", f"Data restored from backup created on {backup_date}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore data: {str(e)}")
    
    def reset_data(self):
        """Reset all application data"""
        result = messagebox.askyesno("Confirm Reset", 
                                    "This will permanently delete ALL data including:\n" +
                                    "• All contacts\n" +
                                    "• All scheduled messages\n" +
                                    "• All message logs\n\n" +
                                    "This action cannot be undone. Continue?")
        
        if result:
            # Confirm again
            final_confirm = messagebox.askyesno("Final Confirmation", 
                                              "Are you absolutely sure? This will delete everything!")
            if final_confirm:
                # Reset all data
                self.contacts_data.clear()
                self.scheduled_messages.clear()
                self.message_log.clear()
                
                # Reset to default settings
                self.browser_var.set("Chrome")
                self.wait_time_var.set("10")
                self.default_delay_var.set("45")
                self.max_messages_var.set("50")
                
                # Clear all input fields
                self.template_var.set("")
                self.labels_var.set("")
                self.group_var.set("")
                self.group_msg_type.set("")
                self.message_text.delete('1.0', 'end')
                self.group_message_text.delete('1.0', 'end')
                
                # Refresh displays
                self.refresh_contacts_display()
                self.refresh_log_display()
                
                self.update_status("All data has been reset to defaults!")
                messagebox.showinfo("Reset Complete", "All application data has been reset successfully!")
    
    def save_settings(self):
        """Save application settings"""
        settings = {
            'browser': self.browser_var.get(),
            'wait_time': self.wait_time_var.get(),
            'default_delay': self.default_delay_var.get(),
            'max_messages': self.max_messages_var.get(),
            'last_saved': datetime.now().isoformat()
        }
        
        try:
            # Create settings directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            with open('data/settings.json', 'w', encoding='utf-8') as file:
                json.dump(settings, file, indent=2)
            
            self.update_status("Settings saved successfully!")
            messagebox.showinfo("Success", "Settings have been saved!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self):
        """Load application settings"""
        try:
            if os.path.exists('data/settings.json'):
                with open('data/settings.json', 'r', encoding='utf-8') as file:
                    settings = json.load(file)
                
                # Apply loaded settings
                self.browser_var.set(settings.get('browser', 'Chrome'))
                self.wait_time_var.set(settings.get('wait_time', '10'))
                self.default_delay_var.set(settings.get('default_delay', '45'))
                self.max_messages_var.set(settings.get('max_messages', '50'))
                
        except Exception as e:
            print(f"Warning: Could not load settings: {e}")
    
    def auto_save_data(self):
        """Automatically save data periodically"""
        try:
            os.makedirs('data', exist_ok=True)
            
            # Save contacts
            with open('data/contacts.json', 'w', encoding='utf-8') as file:
                json.dump(self.contacts_data, file, indent=2, ensure_ascii=False)
            
            # Save scheduled messages
            with open('data/scheduled_messages.json', 'w', encoding='utf-8') as file:
                json.dump(self.scheduled_messages, file, indent=2, ensure_ascii=False)
            
            # Save message log (keep only last 1000 entries to prevent file from getting too large)
            recent_logs = self.message_log[-1000:] if len(self.message_log) > 1000 else self.message_log
            with open('data/message_log.json', 'w', encoding='utf-8') as file:
                json.dump(recent_logs, file, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Auto-save failed: {e}")
        
        # Schedule next auto-save in 5 minutes
        self.root.after(300000, self.auto_save_data)
    
    def load_data_on_startup(self):
        """Load data when application starts"""
        try:
            # Load contacts
            if os.path.exists('data/contacts.json'):
                with open('data/contacts.json', 'r', encoding='utf-8') as file:
                    loaded_contacts = json.load(file)
                    if loaded_contacts:  # Only replace if we loaded actual data
                        self.contacts_data = loaded_contacts
            
            # Load scheduled messages
            if os.path.exists('data/scheduled_messages.json'):
                with open('data/scheduled_messages.json', 'r', encoding='utf-8') as file:
                    self.scheduled_messages = json.load(file)
            
            # Load message log
            if os.path.exists('data/message_log.json'):
                with open('data/message_log.json', 'r', encoding='utf-8') as file:
                    loaded_logs = json.load(file)
                    if loaded_logs:  # Only replace if we loaded actual data
                        self.message_log = loaded_logs
            
            # Load settings
            self.load_settings()
            
        except Exception as e:
            print(f"Warning: Could not load data on startup: {e}")
    
    def update_status(self, message):
        """Update the status bar with a message"""
        self.status_label.config(text=message)
        # Reset to default message after 5 seconds
        self.root.after(5000, lambda: self.status_label.config(text="Ready to engage with your community! 🚀"))
    
    def simulate_whatsapp_connection(self):
        """Simulate WhatsApp connection status (placeholder)"""
        # This would be replaced with actual WhatsApp Web connection logic
        import random
        
        def update_connection_status():
            statuses = [
                ("WhatsApp: Connected ✅", '#28a745'),
                ("WhatsApp: Disconnected ❌", '#dc3545'),
                ("WhatsApp: Connecting... ⏳", '#ffc107')
            ]
            status_text, color = random.choice(statuses)
            self.connection_label.config(text=status_text, fg=color)
            
            # Update again in 10-30 seconds
            self.root.after(random.randint(10000, 30000), update_connection_status)
        
        # Start the simulation
        self.root.after(2000, update_connection_status)
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Save data before closing
            self.auto_save_data()
            print("Data saved successfully before closing.")
        except Exception as e:
            print(f"Error saving data on close: {e}")
        
        # Close the application
        self.root.destroy()


class WhatsAppAutomationEngine:
    """
    Placeholder class for the actual WhatsApp automation engine
    This would integrate with Selenium WebDriver for WhatsApp Web automation
    """
    
    def __init__(self, ui_reference):
        self.ui = ui_reference
        self.driver = None
        self.is_connected = False
        self.message_queue = []
    
    def initialize_webdriver(self, browser='Chrome'):
        """Initialize Selenium WebDriver for chosen browser"""
        # Placeholder for WebDriver initialization
        print(f"Initializing {browser} WebDriver for WhatsApp Web...")
        # from selenium import webdriver
        # from selenium.webdriver.chrome.options import Options
        # 
        # options = Options()
        # options.add_argument("--user-data-dir=./whatsapp_session")
        # self.driver = webdriver.Chrome(options=options)
        pass
    
    def connect_to_whatsapp_web(self):
        """Connect to WhatsApp Web"""
        # Placeholder for WhatsApp Web connection
        print("Connecting to WhatsApp Web...")
        # self.driver.get("https://web.whatsapp.com")
        pass
    
    def send_direct_message(self, contact_name, message):
        """Send a direct message to a contact"""
        # Placeholder for DM sending logic
        print(f"Sending DM to {contact_name}: {message[:50]}...")
        # Implement actual Selenium automation here
        pass
    
    def send_group_message(self, group_name, message):
        """Send a message to a group"""
        # Placeholder for group message logic
        print(f"Sending group message to {group_name}: {message[:50]}...")
        # Implement actual Selenium automation here
        pass
    
    def get_contact_labels(self, contact_name):
        """Extract labels for a contact from WhatsApp Business"""
        # Placeholder for label extraction
        print(f"Getting labels for {contact_name}...")
        return []
    
    def add_message_to_queue(self, message_type, recipient, message, delay=45):
        """Add message to sending queue"""
        queue_item = {
            'type': message_type,
            'recipient': recipient,
            'message': message,
            'delay': delay,
            'timestamp': datetime.now(),
            'status': 'queued'
        }
        self.message_queue.append(queue_item)
        print(f"Added {message_type} to {recipient} to queue")
    
    def process_message_queue(self):
        """Process queued messages with proper delays"""
        # Placeholder for queue processing with delays
        print(f"Processing {len(self.message_queue)} messages in queue...")
        # Implement actual message sending with delays here
        pass


def main():
    """Main application entry point"""
    # Create the main window
    root = tk.Tk()
    
    # Create the application
    app = WhatsAppEngagementUI(root)
    
    # Load data on startup
    app.load_data_on_startup()
    
    # Start auto-save routine
    app.auto_save_data()
    
    # Start WhatsApp connection simulation
    app.simulate_whatsapp_connection()
    
    # Handle window closing properly
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center the window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - root.winfo_width()) // 2
    y = (screen_height - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    # Start the application
    print("🚀 WATRHC WhatsApp Engagement Assistant Started!")
    print("Ready to help you manage your community of 530+ learners!")
    root.mainloop()


if __name__ == "__main__":
    main()
