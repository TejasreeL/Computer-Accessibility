import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

# Load the Vosk model
model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

# Create a queue to receive audio chunks
q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called when new audio data is available."""
    if status:
        print("⚠️", status)
    q.put(bytes(indata))

# Start the audio stream
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("🎙️ Live Transcription (press Ctrl+C to stop):\n")

    try:
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result.get("text"):
                    print("You said:", result["text"])
            else:
                partial = json.loads(recognizer.PartialResult())
                # Optional: print partial results for more real-time feedback
                # print("...", partial.get("partial"))

    except KeyboardInterrupt:
        print("\n🛑 Transcription stopped.")