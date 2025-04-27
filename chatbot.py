from google import genai

client = genai.Client(api_key="AIzaSyD0HaHYv6a2Ee9QzI2yP5YPXtUa_oNrR_k")
def voice_assistant(voice):
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="""Available Voice Commands:
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
    The voice input is :""" + voice + "Give me the command required. Give just the command words, not anything extra, according to my commands. for commands like scroll and move, give number as number, not words"
    )
    return response.text