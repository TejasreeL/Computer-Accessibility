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
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 12))
        self.style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'))
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.configure('Red.TButton', foreground='red')
        self.style.configure('Green.TButton', foreground='green')
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', font=('Helvetica', 12))
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Voice & Eye Control System", 
            style='Title.TLabel'
        )
        self.title_label.pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Control tab
        self.control_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.control_tab, text="Controls")
        
        # Command tab
        self.command_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.command_tab, text="Command Log")
        
        # Voice commands tab
        self.voice_help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.voice_help_tab, text="Voice Commands")
        
        # Control buttons frame
        self.control_frame = ttk.Frame(self.control_tab)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        # Voice control button
        self.voice_btn = ttk.Button(
            self.control_frame,
            text="Start Voice Control",
            command=self.toggle_voice_control,
            style='Green.TButton'
        )
        self.voice_btn.pack(side=tk.LEFT, expand=True, padx=10)
        
        # Eye control button
        self.eye_btn = ttk.Button(
            self.control_frame,
            text="Start Eye Tracking",
            command=self.toggle_eye_control,
            style='Green.TButton'
        )
        self.eye_btn.pack(side=tk.LEFT, expand=True, padx=10)
        
        # Status frame
        self.status_frame = ttk.Frame(self.control_tab)
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Voice control status
        self.voice_status = tk.StringVar(value="Voice Control: Stopped")
        self.voice_label = ttk.Label(
            self.status_frame,
            textvariable=self.voice_status,
            font=('Helvetica', 12)
        )
        self.voice_label.pack(anchor=tk.W, pady=5)
        
        # Eye control status
        self.eye_status = tk.StringVar(value="Eye Tracking: Stopped")
        self.eye_label = ttk.Label(
            self.status_frame,
            textvariable=self.eye_status,
            font=('Helvetica', 12)
        )
        self.eye_label.pack(anchor=tk.W, pady=5)
        
        # Command log in command tab
        self.log_text = tk.Text(
            self.command_tab,
            height=30,
            width=100,
            state=tk.DISABLED,
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar for log
        self.scrollbar = ttk.Scrollbar(self.log_text)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.log_text.yview)
        
        # Voice commands help in voice help tab
        self.help_text = tk.Text(
            self.voice_help_tab,
            height=30,
            width=100,
            state=tk.DISABLED,
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Populate voice commands help
        self.populate_voice_commands_help()
        
        # Variables to track running processes
        self.voice_process = None
        self.eye_process = None
        self.voice_running = False
        self.eye_running = False
        
        # Queue for capturing output
        self.output_queue = queue.Queue()
        
        # Start checking the output queue periodically
        self.root.after(100, self.check_output_queue)
    
    def populate_voice_commands_help(self):
        help_content = """Available Voice Commands:

1. Mouse Movement:
   - "move to X Y" - Move mouse to coordinates X Y
   - "go left/right/up/down N" - Move mouse N pixels in direction
   - Example: "go left 50" or "go up twenty"

2. Mouse Clicks:
   - "left click" - Left mouse click
   - "right click" - Right mouse click
   - "double click" - Double left click
   - "hold left/right" - Hold mouse button
   - "release left/right" - Release mouse button
   - "scroll up/down N" - Scroll N steps

3. Keyboard Control:
   - "type this TEXT" - Type the specified text
   - "hold key KEY" - Hold down a key
   - "release key KEY" - Release a key
   - "press key KEY" - Press and release a key
   - "use shortcut KEY1 KEY2..." - Press key combination
     (Example: "use shortcut ctrl s")

4. System Control:
   - "quit program" - Exit the application

Note: Numbers can be spoken as words (e.g., "twenty") or digits (e.g., "20")
"""
        self.help_text.config(state=tk.NORMAL)
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