import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import os
import sys
import queue
import time

class ControlInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice & Eye Control System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f9f9f9")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure('TFrame', background='#f9f9f9')
        self.style.configure('TLabel', background='#f9f9f9', font=('Segoe UI', 12))
        self.style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#333')
        self.style.configure('Section.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#555')
        self.style.configure('TButton', font=('Segoe UI', 12), padding=10)
        self.style.configure('Red.TButton', foreground='white', background='#d9534f')
        self.style.map('Red.TButton', background=[('active', '#c9302c')])
        self.style.configure('Green.TButton', foreground='white', background='#5cb85c')
        self.style.map('Green.TButton', background=[('active', '#4cae4c')])
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 12, 'bold'))

        # Main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        self.title_label = ttk.Label(self.main_frame, text="🎯 Voice & Eye Control Dashboard", style='Title.TLabel')
        self.title_label.pack(pady=(0, 20))

        # Notebook tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.control_tab = ttk.Frame(self.notebook)
        self.command_tab = ttk.Frame(self.notebook)
        self.voice_help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.control_tab, text="🕹️ Controls")
        self.notebook.add(self.command_tab, text="📜 Command Log")
        self.notebook.add(self.voice_help_tab, text="🎤 Voice Commands Help")

        # --- Control Panel ---
        self.control_frame = ttk.Frame(self.control_tab)
        self.control_frame.pack(fill=tk.X, pady=15)

        self.voice_btn = ttk.Button(self.control_frame, text="▶️ Start Voice Control", command=self.toggle_voice_control, style='Green.TButton')
        self.voice_btn.pack(side=tk.LEFT, expand=True, padx=10)

        self.eye_btn = ttk.Button(self.control_frame, text="👁️ Start Eye Tracking", command=self.toggle_eye_control, style='Green.TButton')
        self.eye_btn.pack(side=tk.LEFT, expand=True, padx=10)

        ttk.Label(self.control_tab, text="System Status", style="Section.TLabel").pack(anchor=tk.W, padx=10, pady=(20, 5))
        self.status_frame = ttk.Frame(self.control_tab)
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        self.voice_status = tk.StringVar(value="🛑 Voice Control: Stopped")
        self.voice_label = ttk.Label(self.status_frame, textvariable=self.voice_status)
        self.voice_label.pack(anchor=tk.W, pady=5)

        self.eye_status = tk.StringVar(value="🛑 Eye Tracking: Stopped")
        self.eye_label = ttk.Label(self.status_frame, textvariable=self.eye_status)
        self.eye_label.pack(anchor=tk.W, pady=5)

        # --- Command Log ---
        self.log_text = tk.Text(self.command_tab, height=30, width=100, state=tk.DISABLED, font=('Consolas', 10), wrap=tk.WORD, bg="#fcfcfc")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.scrollbar = ttk.Scrollbar(self.log_text)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.log_text.yview)

        # --- Voice Help ---
        self.help_text = tk.Text(self.voice_help_tab, height=30, width=100, state=tk.DISABLED, font=('Segoe UI', 11), wrap=tk.WORD, bg="#fcfcfc")
        self.help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.populate_voice_commands_help()

        # State tracking
        self.voice_process = None
        self.eye_process = None
        self.voice_running = False
        self.eye_running = False
        self.output_queue = queue.Queue()
        self.root.after(100, self.check_output_queue)

    def populate_voice_commands_help(self):
        help_content = """🧠 **Available Voice Commands**

            🎯 **Mouse Movement**
            • "move to X Y" – Move mouse to specific coordinates  
            • "go left/right/up/down N" – Move mouse N pixels  
            (Example: "go left 50" or "go up twenty")

            🖱️ **Mouse Clicks**
            • "left click", "right click", "double click"  
            • "hold/release left/right"  
            • "scroll up/down N"

            ⌨️ **Keyboard Control**
            • "type this TEXT" – Type out text  
            • "press key KEY" – Press a key (e.g., Enter)  
            • "hold key KEY", "release key KEY"  
            • "use shortcut KEY1 KEY2 ..." (e.g., "ctrl s")

            ⚙️ **System Control**
            • "quit program" – Exit the application

            ℹ️ *Tip:* You can speak numbers as words or digits ("twenty" = "20")
        """
        self.help_text.config(state=tk.NORMAL)
        self.help_text.delete(1.0, tk.END)
        self.help_text.insert(tk.END, help_content)
        self.help_text.config(state=tk.DISABLED)
    
    def toggle_voice_control(self):
        if self.voice_running:
            self.stop_voice_control()
        else:
            self.start_voice_control()
    
    def toggle_eye_control(self):
        if self.eye_running:
            self.stop_eye_control()
        else:
            self.start_eye_control()
    
    def start_voice_control(self):
        self.log_message("Starting voice control...")
        self.voice_running = True
        self.voice_status.set("Voice Control: Running")
        self.voice_btn.config(text="Stop Voice Control", style='Red.TButton')
        
        # Start voice control in a separate thread
        voice_thread = threading.Thread(
            target=self.run_voice_script, 
            daemon=True
        )
        voice_thread.start()
    
    def stop_voice_control(self):
        self.log_message("Stopping voice control...")
        self.voice_running = False
        self.voice_status.set("Voice Control: Stopped")
        self.voice_btn.config(text="Start Voice Control", style='Green.TButton')
        
        if self.voice_process:
            self.voice_process.terminate()
    
    def start_eye_control(self):
        self.log_message("Starting eye tracking...")
        self.eye_running = True
        self.eye_status.set("Eye Tracking: Running")
        self.eye_btn.config(text="Stop Eye Tracking", style='Red.TButton')
        
        # Start eye control in a separate thread
        eye_thread = threading.Thread(
            target=self.run_eye_script, 
            daemon=True
        )
        eye_thread.start()
    
    def stop_eye_control(self):
        self.log_message("Stopping eye tracking...")
        self.eye_running = False
        self.eye_status.set("Eye Tracking: Stopped")
        self.eye_btn.config(text="Start Eye Tracking", style='Green.TButton')
        
        if self.eye_process:
            self.eye_process.terminate()
    
    def run_voice_script(self):
        try:
            # Get the path to the current Python interpreter
            python_exe = sys.executable
            
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(script_dir, "voice2.py")
            
            # Check if the script exists
            if not os.path.exists(script_path):
                self.log_message(f"Error: voice2.py not found in {script_dir}")
                return
            
            # Run the script with stdout and stderr piped
            self.voice_process = subprocess.Popen(
                [python_exe, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Start threads to capture output
            threading.Thread(
                target=self.read_output,
                args=(self.voice_process.stdout,),
                daemon=True
            ).start()
            
            threading.Thread(
                target=self.read_output,
                args=(self.voice_process.stderr,),
                daemon=True
            ).start()
            
        except Exception as e:
            self.log_message(f"Error running voice control: {str(e)}")
    
    def run_eye_script(self):
        try:
            # Get the path to the current Python interpreter
            python_exe = sys.executable
            
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(script_dir, "eyetracking.py")
            
            # Check if the script exists
            if not os.path.exists(script_path):
                self.log_message(f"Error: eyetracking.py not found in {script_dir}")
                return
            
            # Run the script
            self.eye_process = subprocess.Popen([python_exe, script_path])
            
            
        except Exception as e:
            self.log_message(f"Error running eye tracking: {str(e)}")
    
    def read_output(self, pipe):
        try:
            for line in iter(pipe.readline, ''):
                if line.strip():
                    self.output_queue.put(line)
            pipe.close()
        except ValueError:
            # Pipe was closed
            pass
    
    def check_output_queue(self):
        try:
            while True:
                line = self.output_queue.get_nowait()
                self.log_message(line.strip())
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_output_queue)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)
    
    def on_closing(self):
        if self.voice_running:
            self.stop_voice_control()
        if self.eye_running:
            self.stop_eye_control()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ControlInterface(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()