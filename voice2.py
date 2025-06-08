import pyautogui as pag
from typing import List
import sounddevice as sd
import queue
import json
import re
from vosk import Model, KaldiRecognizer
import functools
print = functools.partial(print, flush=True)  # Force immediate output
from chatbot import voice_assistant

# ========================== COMMAND FUNCTIONS ==========================

word_to_number_map = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100
}

def word_to_number(word: str) -> int:
    if word.isdigit():
        return int(word)
    
    word = word.lower().strip()
    parts = re.split(r"[\s-]+", word)
    total = 0
    current = 0
    
    for part in parts:
        if part in word_to_number_map:
            val = word_to_number_map[part]
            if val == 100 and current != 0:
                current *= 100
            else:
                current += val
        else:
            return None  # Unrecognized word
    return total + current

def move_mouse_to(x: int, y: int) -> None:
    pag.moveTo(x, y, duration=1)

def click_mouse(button: str = "left") -> None:
    pag.click(button=button)

def double_click_mouse() -> None:
    pag.doubleClick()

def hold_mouse(button: str = "left") -> None:
    pag.mouseDown(button=button)

def release_mouse(button: str = "left") -> None:
    pag.mouseUp(button=button)

def move_mouse_relative(direction: str, distance: int) -> None:
    if direction == "up":
        pag.moveRel(0, -distance, duration=1)
    elif direction == "down":
        pag.moveRel(0, distance, duration=1)
    elif direction == "left":
        pag.moveRel(-distance, 0, duration=1)
    elif direction == "right":
        pag.moveRel(distance, 0, duration=1)

def scroll_mouse(direction: str, amount: int) -> None:
    pag.scroll(amount if direction == "up" else -amount)

def hold_key(key: str) -> None:
    pag.keyDown(key)

def release_key(key: str) -> None:
    pag.keyUp(key)

def press_key(key: str) -> None:
    pag.press(key)

def use_shortcut(keys: List[str]) -> None:
    pag.hotkey(*keys)

def type_this(text: str) -> None:
    pag.typewrite(text, interval=0.05)

def quit_program() -> None:
    print("You said: quit program. Now quitting...")
    quit()

# ========================== SPEECH PARSING ==========================

def correct_key_names(keys: List[str]) -> List[str]:
    joined = " ".join(keys)
    replacements = {
        "control": "ctrl",
        "page down": "pagedown",
        "page up": "pageup",
        "volume down": "volumedown",
        "volume up": "volumeup",
        "print screen": "printscreen"
    }
    for word, replacement in replacements.items():
        joined = joined.replace(word, replacement)
    return joined.split()

def execute_command(words: List[str]):
    words = correct_key_names(words)
    x, y = pag.position()

    try:
        if words[0] == "move" and words[1] == "to":
            move_mouse_to(int(words[2]), int(words[3]))
        elif words[0] == "go":
            amount = word_to_number(words[2])
            if amount is not None:
                move_mouse_relative(words[1], amount)
            else:
                print("Invalid number:", words[2])

        elif words[0] == "double" and words[1] == "click":
            double_click_mouse()
        elif words[1] == "click":
            click_mouse(button=words[0])
        elif words[0] == "hold" and words[1] in ["left", "middle", "right"]:
            hold_mouse(words[1])
        elif words[0] == "release" and words[1] in ["left", "middle", "right"]:
            release_mouse(words[1])
        elif words[0] == "scroll":
            amount = word_to_number(words[2])
            if amount is not None:
                scroll_mouse(words[1], amount)
            else:
                print("Invalid number:", words[2])
            scroll_mouse(words[1], int(words[2]))
        elif words[0] == "type" and words[1] == "this":
            type_this(" ".join(words[2:]))
        elif words[0] == "hold" and words[1] == "key":
            hold_key(words[2])
        elif words[0] == "release" and words[1] == "key":
            release_key(words[2])
        elif words[0] == "press" and words[1] == "key":
            press_key(words[2])
        elif words[0] == "use" and words[1] == "shortcut":
            use_shortcut(words[2:])
        elif words[0] == "quit" and words[1] == "program":
            quit_program()
        else:
            print("Unrecognized command:", " ".join(words))
    except Exception as e:
        print("Error executing command:", e)

# ========================== VOSK SETUP ==========================

model = Model("vosk-model-en-in-0.5")
recognizer = KaldiRecognizer(model, 16000)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

# ========================== MAIN LOOP ==========================

if __name__ == "__main__":
    pag.FAILSAFE = False
    print("Voice control active. Speak a command...")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        try:
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        print("You said:", text)
                        parsed = text.split()
                        if len(parsed) > 3:
                            print("Sending to voice assistant for processing...")
                            try:
                                command = voice_assistant(text)
                                print("Voice assistant response:", command)
                                parsed = command.strip().split()
                            except Exception as e:
                                print("Error getting response from voice assistant:", e)
                                continue
                        if len(parsed) >= 2:
                            execute_command(parsed)
                        else:
                            print("Incomplete or invalid command.")
        except KeyboardInterrupt:
            print("\n Voice control terminated.")
