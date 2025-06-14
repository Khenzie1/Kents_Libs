import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import speech_recognition as sr
import pyttsx3
import PyPDF2
from reportlab.pdfgen import canvas
import threading
import os
import pyaudio
from PIL import Image, ImageTk
import time

class ModernUI(ttk.Style):
    def __init__(self):
        super().__init__()
        self.theme_use('clam')
        
        # Define colors
        self.primary = "#4a86e8"
        self.secondary = "#7c9fc9"
        self.bg = "#f5f7fa"
        self.light_bg = "#ffffff"
        self.text = "#333333"
        self.success = "#4caf50"
        self.warning = "#ff9800"
        self.error = "#f44336"
        
        # Configure styles
        self.configure('TFrame', background=self.bg)
        self.configure('TLabelframe', background=self.bg, bordercolor=self.secondary)
        self.configure('TLabelframe.Label', background=self.bg, foreground=self.primary, font=('Segoe UI', 11, 'bold'))
        self.configure('TLabel', background=self.bg, foreground=self.text, font=('Segoe UI', 10))
        
        # Buttons
        self.configure('TButton', background=self.primary, foreground='white', font=('Segoe UI', 10))
        self.map('TButton', background=[('active', self.secondary), ('disabled', '#cccccc')])
        
        # Progress bar
        self.configure('Horizontal.TProgressbar', background=self.primary, troughcolor=self.bg)
        
        # Custom styles
        self.configure('Success.TLabel', background=self.bg, foreground=self.success)
        self.configure('Warning.TLabel', background=self.bg, foreground=self.warning)
        self.configure('Error.TLabel', background=self.bg, foreground=self.error)
        
        # Primary button
        self.configure('Primary.TButton', background=self.primary, foreground='white', font=('Segoe UI', 10, 'bold'))
        self.map('Primary.TButton', background=[('active', self.secondary), ('disabled', '#cccccc')])
        
        # Secondary button
        self.configure('Secondary.TButton', background='white', foreground=self.primary, bordercolor=self.primary)
        self.map('Secondary.TButton', foreground=[('active', self.secondary)], bordercolor=[('active', self.secondary)])

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Modal Converter System")
        self.root.attributes("-fullscreen", True)
        # self.root.geometry("950x700")
        
        # Set icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
        # Apply modern styling
        self.style = ModernUI()
        self.root.configure(bg=self.style.bg)
        
        # Initialize engines
        self.speech_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        
        # Create header
        self.create_header()
        
        # Create tabs
        self.create_tabs()
        
        # Create status bar
        self.create_status_bar()
        
        # Setup each tab
        self.setup_voice_to_text()
        self.setup_text_to_voice()
        self.setup_pdf_to_voice()
        self.setup_voice_to_pdf()
        
        # Animation variables
        self.recording = False
        self.recording_frames = ["🔴", "⭕"]
        self.recording_frame_index = 0
        
    def create_header(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text="Multi-Modal Converter System", 
                               font=('Segoe UI', 16, 'bold'), foreground=self.style.primary)
        title_label.pack(side="left", padx=10)
        
        # Exit button
        exit_btn = ttk.Button(header_frame, text="Exit", style="Secondary.TButton", cursor="hand2", 
                             command=self.root.destroy)
        exit_btn.pack(side="right", padx=10)
    
    def create_tabs(self):
        # Create style for tabs
        self.style.configure('TNotebook.Tab', background=self.style.bg, padding=[15, 5], font=('Segoe UI', 10))
        self.style.map('TNotebook.Tab', background=[('selected', self.style.primary)], 
                      foreground=[('selected', 'white')])
        
        self.tab_control = ttk.Notebook(self.root, cursor="hand2")
        
        self.voice_to_text_tab = ttk.Frame(self.tab_control)
        self.text_to_voice_tab = ttk.Frame(self.tab_control)
        self.pdf_to_voice_tab = ttk.Frame(self.tab_control)
        self.voice_to_pdf_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.voice_to_text_tab, text="Voice to Text")
        self.tab_control.add(self.text_to_voice_tab, text="Text to Voice")
        self.tab_control.add(self.pdf_to_voice_tab, text="PDF to Voice")
        self.tab_control.add(self.voice_to_pdf_tab, text="Voice to PDF")
        
        self.tab_control.pack(expand=1, fill="both", padx=20, pady=10)
        
    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_voice_to_text(self):
        frame = ttk.LabelFrame(self.voice_to_text_tab, text="Convert your speech to text (en)", cursor="hand2")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        instruction_label = ttk.Label(frame, text="Click 'Record' and speak clearly to convert your voice to text.")
        instruction_label.pack(pady=(10, 5))
        
        # Progressbar for visual feedback during recording
        self.vtt_progress = ttk.Progressbar(frame, orient="horizontal", length=100, mode="indeterminate")
        
        # Text area with custom styling
        self.vtt_text = scrolledtext.ScrolledText(frame, width=70, height=15, 
                                                font=('Segoe UI', 11), bg='white', fg=self.style.text)
        self.vtt_text.pack(padx=20, pady=10, fill="both", expand=True)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        
        # Record button with custom styling
        self.record_btn = ttk.Button(btn_frame, text="Record", style="Primary.TButton", command=self.record_audio)
        self.record_btn.pack(side="left", padx=10)
        
        # Options dropdown
        self.record_time = tk.StringVar(value="")
        time_options = ttk.Combobox(btn_frame, textvariable=self.record_time, width=5, 
                                   values=["3", "5", "10", "15", "30"])
        time_options.pack(side="left", padx=2)
        ttk.Label(btn_frame, text="seconds").pack(side="left", padx=(2, 15))
        
        # Save and clear buttons
        self.save_text_btn = ttk.Button(btn_frame, text="Save Text", command=self.save_text)
        self.save_text_btn.pack(side="left", padx=10)
        
        self.clear_vtt_btn = ttk.Button(btn_frame, text="Clear", 
                                      command=lambda: self.vtt_text.delete(1.0, tk.END))
        self.clear_vtt_btn.pack(side="left", padx=10)
        
        # Status with icon
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        self.vtt_status_icon = ttk.Label(status_frame, text="🟢")
        self.vtt_status_icon.pack(side="left", padx=(0, 5))
        
        self.status_vtt = ttk.Label(status_frame, text="Ready")
        self.status_vtt.pack(side="left")
    
    def setup_text_to_voice(self):
        frame = ttk.LabelFrame(self.text_to_voice_tab, text="Convert text to speech (en)", cursor="hand2")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        instruction_label = ttk.Label(frame, text="Enter text below and click 'Speak Text' to hear it.")
        instruction_label.pack(pady=(10, 5))
        
        # Voice settings
        voice_frame = ttk.Frame(frame)
        voice_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(voice_frame, text="Voice:").pack(side="left", padx=5)
        self.voice_var = tk.StringVar(value="Default")
        self.voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_var, width=15, state="readonly")
        self.voice_combo.pack(side="left", padx=5)
        
        ttk.Label(voice_frame, text="Speed:").pack(side="left", padx=(15, 5))
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(voice_frame, textvariable=self.speed_var, width=10, 
                                  values=["Slow", "Normal", "Fast"], state="readonly")
        speed_combo.pack(side="left", padx=5)
        speed_combo.bind("<<ComboboxSelected>>", self.change_speech_rate)
        
        # Populate voice combobox
        self.load_voices()
        
        # Text area
        self.ttv_text = scrolledtext.ScrolledText(frame, width=70, height=15, 
                                                font=('Segoe UI', 11), bg='white', fg=self.style.text)
        self.ttv_text.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Progress bar for speech
        self.ttv_progress = ttk.Progressbar(frame, orient="horizontal", mode="indeterminate")
        self.ttv_progress.pack(fill="x", padx=20, pady=(0, 10), ipady=2)
        self.ttv_progress.pack_forget()  # Hide initially
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        
        self.speak_btn = ttk.Button(btn_frame, text="Speak Text", style="Primary.TButton", command=self.speak_text)
        self.speak_btn.pack(side="left", padx=10)
        
        self.stop_speak_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_speaking)
        self.stop_speak_btn.pack(side="left", padx=10)
        self.stop_speak_btn.config(state="disabled")
        
        self.save_audio_btn = ttk.Button(btn_frame, text="Save as Audio", command=self.save_audio)
        self.save_audio_btn.pack(side="left", padx=10)
        
        self.clear_ttv_btn = ttk.Button(btn_frame, text="Clear", 
                                      command=lambda: self.ttv_text.delete(1.0, tk.END))
        self.clear_ttv_btn.pack(side="left", padx=10)
        
        # Status with icon
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        self.ttv_status_icon = ttk.Label(status_frame, text="🟢")
        self.ttv_status_icon.pack(side="left", padx=(0, 5))
        
        self.status_ttv = ttk.Label(status_frame, text="Ready")
        self.status_ttv.pack(side="left")
    
    def setup_pdf_to_voice(self):
        frame = ttk.LabelFrame(self.pdf_to_voice_tab, text="Convert PDF to speech (en)", cursor="hand2")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        instruction_label = ttk.Label(frame, text="Select a PDF file, and convert its text to speech.")
        instruction_label.pack(pady=(10, 5))
        
        # File selection
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(file_frame, text="PDF File:").pack(side="left", padx=5)
        self.pdf_path_var = tk.StringVar()
        pdf_entry = ttk.Entry(file_frame, textvariable=self.pdf_path_var, width=50, state="readonly")
        pdf_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.select_pdf_btn = ttk.Button(file_frame, text="Browse...", command=self.select_pdf)
        self.select_pdf_btn.pack(side="left", padx=5)
        
        # PDF Preview with custom border
        preview_frame = ttk.Frame(frame, borderwidth=1, relief="solid")
        preview_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.pdf_content = scrolledtext.ScrolledText(preview_frame, width=70, height=12, 
                                                 font=('Segoe UI', 11), bg='white', fg=self.style.text)
        self.pdf_content.pack(padx=1, pady=1, fill="both", expand=True)
        
        # Reading settings
        settings_frame = ttk.Frame(frame)
        settings_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(settings_frame, text="Speed:").pack(side="left", padx=5)
        speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(settings_frame, textvariable=speed_var, width=10, 
                                  values=["Slow", "Normal", "Fast"], state="readonly")
        speed_combo.pack(side="left", padx=5)
        
        ttk.Label(settings_frame, text="Page Range:").pack(side="left", padx=(15, 5))
        self.page_range = ttk.Entry(settings_frame, width=15)
        self.page_range.pack(side="left", padx=5)
        ttk.Label(settings_frame, text="(e.g., 1-5, blank for all)").pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        
        self.speak_pdf_btn = ttk.Button(btn_frame, text="Speak PDF", style="Primary.TButton", command=self.speak_pdf)
        self.speak_pdf_btn.pack(side="left", padx=10)
        self.speak_pdf_btn.config(state="disabled")
        
        self.stop_pdf_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_speaking)
        self.stop_pdf_btn.pack(side="left", padx=10)
        self.stop_pdf_btn.config(state="disabled")
        
        self.save_pdf_audio_btn = ttk.Button(btn_frame, text="Save as Audio", command=self.save_pdf_audio)
        self.save_pdf_audio_btn.pack(side="left", padx=10)
        self.save_pdf_audio_btn.config(state="disabled")
        
        # Status with progress
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        self.pdf_status_icon = ttk.Label(status_frame, text="⚪")
        self.pdf_status_icon.pack(side="left", padx=(0, 5))
        
        self.status_pdf = ttk.Label(status_frame, text="Select a PDF file to begin")
        self.status_pdf.pack(side="left")
    
    def setup_voice_to_pdf(self):
        frame = ttk.LabelFrame(self.voice_to_pdf_tab, text="Create PDF from voice (en)", cursor="hand2")
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        instruction_label = ttk.Label(frame, text="Record your voice and convert it to a PDF document.")
        instruction_label.pack(pady=(10, 5))
        
        # Document settings
        settings_frame = ttk.Frame(frame)
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        # Title entry with label in a single row
        title_frame = ttk.Frame(settings_frame)
        title_frame.pack(fill="x", pady=5)
        
        ttk.Label(title_frame, text="PDF Title:", width=12).pack(side="left", padx=5)
        self.pdf_title = ttk.Entry(title_frame, width=40)
        self.pdf_title.pack(side="left", padx=5, fill="x", expand=True)
        
        # Author frame
        author_frame = ttk.Frame(settings_frame)
        author_frame.pack(fill="x", pady=5)
        
        ttk.Label(author_frame, text="Author:", width=12).pack(side="left", padx=5)
        self.pdf_author = ttk.Entry(author_frame, width=40)
        self.pdf_author.pack(side="left", padx=5, fill="x", expand=True)
        
        # Content area with a border and title
        content_frame = ttk.LabelFrame(frame, text="Document Content")
        content_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.pdf_text = scrolledtext.ScrolledText(content_frame, width=70, height=12, 
                                               font=('Segoe UI', 11), bg='white', fg=self.style.text)
        self.pdf_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Progress bar for recording
        self.vtpdf_progress = ttk.Progressbar(frame, orient="horizontal", mode="indeterminate")
        self.vtpdf_progress.pack(fill="x", padx=20, pady=(0, 10), ipady=2)
        self.vtpdf_progress.pack_forget()  # Hide initially
        
        # Button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=15)
        
        record_frame = ttk.Frame(btn_frame)
        record_frame.pack(side="left", padx=10)
        
        self.record_for_pdf_btn = ttk.Button(record_frame, text="Record", 
                                           style="Primary.TButton", command=self.record_for_pdf)
        self.record_for_pdf_btn.pack(side="left")
        
        self.record_duration = tk.StringVar(value="5")
        time_options = ttk.Combobox(record_frame, textvariable=self.record_duration, 
                                   width=5, values=["3", "5", "10", "15", "30"])
        time_options.pack(side="left", padx=2)
        ttk.Label(record_frame, text="seconds").pack(side="left", padx=2)
        
        self.create_pdf_btn = ttk.Button(btn_frame, text="Create PDF", command=self.create_pdf)
        self.create_pdf_btn.pack(side="left", padx=10)
        
        self.preview_pdf_btn = ttk.Button(btn_frame, text="Preview", command=self.preview_pdf)
        self.preview_pdf_btn.pack(side="left", padx=10)
        
        self.clear_pdf_btn = ttk.Button(btn_frame, text="Clear", 
                                      command=lambda: self.pdf_text.delete(1.0, tk.END))
        self.clear_pdf_btn.pack(side="left", padx=10)
        
        # Status with icon
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill="x", padx=20, pady=5)
        
        self.vtpdf_status_icon = ttk.Label(status_frame, text="🟢")
        self.vtpdf_status_icon.pack(side="left", padx=(0, 5))
        
        self.status_vtpdf = ttk.Label(status_frame, text="Ready")
        self.status_vtpdf.pack(side="left")
    
    def load_voices(self):
        """Load available voices from pyttsx3"""
        voices = self.speech_engine.getProperty('voices')
        voice_names = ["Default"]
        
        for voice in voices:
            voice_names.append(voice.name)
        
        self.voice_combo['values'] = voice_names
        
        # Listen for voice changes
        self.voice_combo.bind("<<ComboboxSelected>>", self.change_voice)
    
    def change_voice(self, event=None):
        """Change the voice of the speech engine"""
        voice_name = self.voice_var.get()
        
        if voice_name == "Default":
            return
        
        voices = self.speech_engine.getProperty('voices')
        
        for voice in voices:
            if voice.name == voice_name:
                self.speech_engine.setProperty('voice', voice.id)
                break
    
    def change_speech_rate(self, event=None):
        """Change the speech rate"""
        speed = self.speed_var.get()
        
        if speed == "Slow":
            self.speech_engine.setProperty('rate', 125)
        elif speed == "Normal":
            self.speech_engine.setProperty('rate', 175)
        elif speed == "Fast":
            self.speech_engine.setProperty('rate', 225)
    
    def record_audio(self):
        def record():
            self.recording = True
            self.update_status_with_animation("vtt", "Recording...")
            self.record_btn.config(state="disabled")
            self.vtt_progress.pack(fill="x", padx=20, pady=(0, 10), ipady=2)
            self.vtt_progress.start(10)
            
            try:
                # Get recording duration
                record_time = int(self.record_time.get())
                
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    self.status_bar.config(text="Listening... Speak now.")
                    audio = self.recognizer.listen(source, timeout=record_time)
                
                self.status_bar.config(text="Processing speech...")
                text = self.recognizer.recognize_google(audio)
                self.vtt_text.insert(tk.END, text + "\n")
                self.update_status("vtt", "Done recording", "success")
            except sr.UnknownValueError:
                self.update_status("vtt", "Could not understand audio", "error")
            except sr.RequestError:
                self.update_status("vtt", "Could not request results", "error")
            except Exception as e:
                self.update_status("vtt", f"Error: {str(e)}", "error")
            finally:
                self.record_btn.config(state="normal")
                self.vtt_progress.stop()
                self.vtt_progress.pack_forget()
                self.recording = False
                self.status_bar.config(text="Ready")
        
        threading.Thread(target=record).start()
    
    def save_text(self):
        text = self.vtt_text.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, "w") as file:
                file.write(text)
            self.update_status("vtt", f"Saved to {os.path.basename(file_path)}", "success")
            self.status_bar.config(text=f"File saved: {file_path}")
    
    def speak_text(self):
        def speak():
            text = self.ttv_text.get(1.0, tk.END).strip()
            
            if not text:
                self.update_status("ttv", "No text to speak", "warning")
                return
                
            self.update_status("ttv", "Speaking...", "warning")
            self.speak_btn.config(state="disabled")
            self.stop_speak_btn.config(state="normal")
            self.ttv_progress.pack(fill="x", padx=20, pady=(0, 10), ipady=2)
            self.ttv_progress.start(10)
            
            try:
                self.speech_engine.say(text)
                self.speech_engine.runAndWait()
                self.update_status("ttv", "Done speaking", "success")
            except Exception as e:
                self.update_status("ttv", f"Error: {str(e)}", "error")
            finally:
                self.speak_btn.config(state="normal")
                self.stop_speak_btn.config(state="disabled")
                self.ttv_progress.stop()
                self.ttv_progress.pack_forget()
        
        threading.Thread(target=speak).start()
    
    def stop_speaking(self):
        """Stop the speech engine"""
        try:
            self.speech_engine.stop()
            self.update_status("ttv", "Speech stopped", "warning")
            self.speak_btn.config(state="normal")
            self.stop_speak_btn.config(state="disabled")
            self.ttv_progress.stop()
            self.ttv_progress.pack_forget()
        except:
            pass
    
    def save_audio(self):
        text = self.ttv_text.get(1.0, tk.END).strip()
        
        if not text:
            self.update_status("ttv", "No text to save as audio", "warning")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3", 
            filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav")]
        )
        
        if file_path:
            self.update_status("ttv", "Saving audio...", "warning")
            self.status_bar.config(text="Saving audio file...")
            
            try:
                # Using pyttsx3 to save to file
                self.speech_engine.save_to_file(text, file_path)
                self.speech_engine.runAndWait()
                
                self.update_status("ttv", f"Saved to {os.path.basename(file_path)}", "success")
                self.status_bar.config(text=f"Audio saved: {file_path}")
            except Exception as e:
                self.update_status("ttv", f"Error: {str(e)}", "error")
    
    def select_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        
        if file_path:
            self.pdf_path_var.set(file_path)
            self.status_bar.config(text=f"Selected PDF: {file_path}")
            
            try:
                self.pdf_status_icon.config(text="⏳")
                self.status_pdf.config(text="Loading PDF...")
                self.root.update_idletasks()
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += f"--- Page {page_num + 1} ---\n"
                        text += page.extract_text() + "\n\n"
                    
                    self.pdf_content.delete(1.0, tk.END)
                    self.pdf_content.insert(tk.END, text)
                
                self.update_status("pdf", f"PDF loaded: {os.path.basename(file_path)} ({len(pdf_reader.pages)} pages)", "success")
                self.speak_pdf_btn.config(state="normal")
                self.save_pdf_audio_btn.config(state="normal")
            except Exception as e:
                self.update_status("pdf", f"Error: {str(e)}", "error")
    
    def speak_pdf(self):
        def speak():
            self.speak_pdf_btn.config(state="disabled")
            self.stop_pdf_btn.config(state="normal")
            self.update_status("pdf", "Speaking...", "warning")
            
            text = self.pdf_content.get(1.0, tk.END)
            
            try:
                self.speech_engine.say(text)
                self.speech_engine.runAndWait()
                self.update_status("pdf", "Done speaking", "success")
            except Exception as e:
                self.update_status("pdf", f"Error: {str(e)}", "error")
            finally:
                self.speak_pdf_btn.config(state="normal")
                self.stop_pdf_btn.config(state="disabled")
        
        threading.Thread(target=speak).start()
    
    def save_pdf_audio(self):
        text = self.pdf_content.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3", 
            filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav")]
        )
        
        if file_path:
            self.update_status("pdf", "Saving audio...", "warning")
            self.status_bar.config(text="Saving audio file...")
            
            try:
                # Using pyttsx3 to save to file
                self.speech_engine.save_to_file(text, file_path)
                self.speech_engine.runAndWait()
                self.update_status("pdf", f"Saved to {os.path.basename(file_path)}", "success")
                self.status_bar.config(text=f"Audio saved: {file_path}")
            except Exception as e:
                self.update_status("pdf", f"Error: {str(e)}", "error")
    
    def record_for_pdf(self):
        def record():
            self.recording = True
            self.update_status_with_animation("vtpdf", "Recording...")
            self.record_for_pdf_btn.config(state="disabled")
            self.vtpdf_progress.pack(fill="x", padx=20, pady=(0, 10), ipady=2)
            self.vtpdf_progress.start(10)
            
            try:
                # Get recording duration
                record_time = int(self.record_duration.get())
                
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    self.status_bar.config(text="Listening... Speak now.")
                    audio = self.recognizer.listen(source, timeout=record_time)
                
                self.status_bar.config(text="Processing speech...")
                text = self.recognizer.recognize_google(audio)
                self.pdf_text.insert(tk.END, text + "\n")
                self.update_status("vtpdf", "Done recording", "success")
            except sr.UnknownValueError:
                self.update_status("vtpdf", "Could not understand audio", "error")
            except sr.RequestError:
                self.update_status("vtpdf", "Could not request results", "error")
            except Exception as e:
                self.update_status("vtpdf", f"Error: {str(e)}", "error")
            finally:
                self.record_for_pdf_btn.config(state="normal")
                self.vtpdf_progress.stop()
                self.vtpdf_progress.pack_forget()
                self.recording = False
                self.status_bar.config(text="Ready")
        
        threading.Thread(target=record).start()
    
    def create_pdf(self):
        title = self.pdf_title.get()
        author = self.pdf_author.get()
        content = self.pdf_text.get(1.0, tk.END)
        
        if not title:
            self.update_status("vtpdf", "Please enter a title for the PDF", "warning")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("vtpdf", "Creating PDF...", "warning")
                self.status_bar.config(text="Creating PDF file...")
                
                c = canvas.Canvas(file_path)
                
                # Add document info
                c.setTitle(title)
                if author:
                    c.setAuthor(author)
                
                # Add fancy header
                c.setFillColorRGB(0.29, 0.53, 0.91)  # Use the primary color
                c.rect(0, 780, 595, 70, fill=True)
                
                c.setFillColorRGB(1, 1, 1)  # White text
                c.setFont("Helvetica-Bold", 22)
                c.drawString(50, 810, title)
                
                if author:
                    c.setFont("Helvetica-Italic", 12)
                    c.drawString(50, 790, f"Author: {author}")
                
                # Add date
                import datetime
                today = datetime.datetime.now().strftime("%B %d, %Y")
                c.setFont("Helvetica", 10)
                c.drawString(450, 790, today)
                
                # Add content
                c.setFillColorRGB(0, 0, 0)  # Black text
                c.setFont("Helvetica", 12)
                text_object = c.beginText(50, 740)
                
                # Add line by line, handling overflow
                for line in content.split('\n'):
                    text_object.textLine(line)
                
                c.drawText(text_object)
                
                # Add page number
                c.setFont("Helvetica", 9)
                c.drawString(280, 20, "Page 1")
                
                c.save()
                
                self.update_status("vtpdf", f"PDF saved: {os.path.basename(file_path)}", "success")
                self.status_bar.config(text=f"PDF created: {file_path}")
            except Exception as e:
                self.update_status("vtpdf", f"Error creating PDF: {str(e)}", "error")
    
    def preview_pdf(self):
        """Create a preview of the PDF"""
        title = self.pdf_title.get() or "Untitled Document"
        content = self.pdf_text.get(1.0, tk.END).strip()
        
        if not content:
            self.update_status("vtpdf", "No content to preview", "warning")
            return
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Preview: {title}")
        preview_window.geometry("600x800")
        preview_window.configure(bg="white")
        
        # Add scrollable canvas
        preview_canvas = tk.Canvas(preview_window, bg="white")
        scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=preview_canvas.yview)
        
        preview_frame = ttk.Frame(preview_canvas, style='TFrame')
        preview_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        preview_canvas.pack(side="left", fill="both", expand=True)
        
        # Create preview content
        preview_canvas.create_window((0, 0), window=preview_frame, anchor="nw")
        
        # Header
        header_frame = ttk.Frame(preview_frame, style='TFrame')
        header_frame.pack(fill="x", padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text=title, font=('Segoe UI', 18, 'bold'), 
                              foreground=self.style.primary)
        title_label.pack(anchor="w")
        
        author = self.pdf_author.get()
        if author:
            author_label = ttk.Label(header_frame, text=f"Author: {author}", 
                                   font=('Segoe UI', 10, 'italic'))
            author_label.pack(anchor="w", pady=(0, 10))
        
        # Date
        import datetime
        today = datetime.datetime.now().strftime("%B %d, %Y")
        date_label = ttk.Label(header_frame, text=today, font=('Segoe UI', 9))
        date_label.pack(anchor="e")
        
        # Divider
        ttk.Separator(preview_frame, orient='horizontal').pack(fill='x', padx=20, pady=10)
        
        # Content
        content_frame = ttk.Frame(preview_frame, style='TFrame')
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Text widget with content
        text_widget = tk.Text(content_frame, wrap="word", font=('Segoe UI', 11), 
                            bg="white", borderwidth=0, height=30)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")  # Make read-only
        
        # Update canvas scroll region
        preview_frame.update_idletasks()
        preview_canvas.config(scrollregion=preview_canvas.bbox("all"))
    
    def update_status(self, tab, message, status_type="normal"):
        """Update status message with type (normal, success, warning, error)"""
        icon = "🟢"  # Default
        
        if status_type == "success":
            icon = "✅"
            getattr(self, f"status_{tab}").config(style="Success.TLabel")
        elif status_type == "warning":
            icon = "⚠️"
            getattr(self, f"status_{tab}").config(style="Warning.TLabel")
        elif status_type == "error":
            icon = "❌"
            getattr(self, f"status_{tab}").config(style="Error.TLabel")
        else:
            getattr(self, f"status_{tab}").config(style="TLabel")
            
        getattr(self, f"{tab}_status_icon").config(text=icon)
        getattr(self, f"status_{tab}").config(text=message)
    
    def update_status_with_animation(self, tab, message):
        """Update status with animation for ongoing processes"""
        if not self.recording:
            return
            
        icons = ["⏺️", "🔴"]
        getattr(self, f"{tab}_status_icon").config(text=icons[self.recording_frame_index])
        getattr(self, f"status_{tab}").config(text=message, style="Warning.TLabel")
        
        self.recording_frame_index = (self.recording_frame_index + 1) % len(icons)
        self.root.after(500, lambda: self.update_status_with_animation(tab, message))
    
    # Add dialog to confirm exit
    def confirm_exit(self):
        if tk.messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
    
    # Add dark mode toggle
    def toggle_dark_mode(self):
        if self.dark_mode:
            # Switch to light mode
            self.style.bg = "#f5f7fa"
            self.style.light_bg = "#ffffff"
            self.style.text = "#333333"
            self.root.configure(bg=self.style.bg)
        else:
            # Switch to dark mode
            self.style.bg = "#2d2d30"
            self.style.light_bg = "#1e1e1e"
            self.style.text = "#ffffff"
            self.root.configure(bg=self.style.bg)
            
        self.dark_mode = not self.dark_mode
        # Would need to update all widgets' styles here

if __name__ == "__main__":
    root = tk.Tk()
    # Set app icon if available
    try:
        root.iconphoto(True, tk.PhotoImage(file="app_icon.png"))
    except:
        pass
        
    # Add window close protocol
    root.protocol("WM_DELETE_WINDOW", lambda: app.confirm_exit())
    
    app = ConverterApp(root)
    
    # Center window on screen
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    position_right = int(root.winfo_screenwidth()/2 - window_width/2)
    position_down = int(root.winfo_screenheight()/2 - window_height/2)
    root.geometry(f"+{position_right}+{position_down}")
    
    root.mainloop()