# Computer Accessibility System for the Disabled

A Python-based accessibility system that allows disabled users to control their computer using **eye tracking** as the replacement to a mouse and **voice commands** as the replacement to a keyboard — no mouse or keyboard required. It includes a smart **NLP module** that converts natural free-form speech into executable system commands, making it intuitive and hands-free.

---

## 💡 Features
### 👁️ Eye Tracking (Mouse Control)
- Move the mouse cursor with your gaze
- Left click and right click with left wink and right wink respectively
### 🗣️ Voice Command Categories
- Voice commands for mouse movement and clicks, like `move` and `scroll up`
- Voice commands for keyboard control, like `type this TEXT` and `hold key KEY`
### 🤖 NLP Module
Interprets flexible natural language into executable commands.  
For example:
- `"i want to type in capitals"` → `hold shift key`
- `"can you press escape"` → `press key esc`

---

## 🛠 Tech Stack
- **Python**
- **Vosk** – Offline speech recognition
- **OpenCV** – Webcam feed and image processing
- **Mediapipe** – Facial/eye landmark detection
- **Tkinter** – GUI
---

## ⚙️ How to Run

### 1. Create a Virtual Environment
- Run the following command `python -m venv venv`
- Activate it on Windows: `venv\Scripts\activate`
- Activate it on macOS/Linux: `source venv/bin/activate`
### 2. Install Dependencies
- Run the following command `pip install -r requirements.txt`
### 3. Download & Place Vosk Model
- Download "vosk-model-en-in-0.5" model from https://alphacephei.com/vosk/models
- Extract it and place the folder in the root directory
### 4. Set Gemini API Key (Optional for NLP)
- Create a file named .env in the root directory of the project
- Add the following line to it: `GEMINI_API="api key"`
### 5. Run the Application
- Run the following code `python integrated.py`
