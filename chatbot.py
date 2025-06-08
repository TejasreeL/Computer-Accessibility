import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API")
client = genai.Client(api_key=api_key)

def voice_assistant(voice):
    prompt = f"""
    I made a voice controlled command executor for windows system. The available voice commands are:
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
    From a given free speech, give me what command to execute.
    The voice input is : {voice}
    Give me the command required. Give just the command words, not anything extra, according to my commands. 
    For commands like scroll and move, give number as number, not words.
    If user says, i want to select a text, it means that the mouse key must be held, and vice versa.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text