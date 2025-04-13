import whisper
import sounddevice as sd
import numpy as np
import queue
import threading

# Parameters
SAMPLERATE = 16000
BLOCKSIZE = 1024
CHANNELS = 1

# Queue to collect audio chunks
audio_queue = queue.Queue()

# Whisper model
model = whisper.load_model("large")

def audio_callback(indata, frames, time, status):
    """This function is called for each audio block from the mic."""
    if status:
        print(status)
    audio_queue.put(indata.copy())

def transcribe_stream():
    """Continuously transcribe chunks from the queue."""
    print("🔴 Live transcription started (Ctrl+C to stop)...\n")
    buffer = np.empty((0, CHANNELS), dtype=np.float32)

    try:
        while True:
            chunk = audio_queue.get()
            buffer = np.concatenate((buffer, chunk))

            # Every 5 seconds of audio (approx.)
            if len(buffer) >= SAMPLERATE * 5:
                # Whisper expects mono float32 numpy array
                audio_data = buffer.flatten()
                result = model.transcribe(audio_data, fp16=False, language="en")
                print("You said:", result["text"].strip())
                buffer = np.empty((0, CHANNELS), dtype=np.float32)

    except KeyboardInterrupt:
        print("\n🛑 Transcription stopped.")

# Start audio stream
stream = sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS,
                        blocksize=BLOCKSIZE, dtype='float32',
                        callback=audio_callback)

with stream:
    transcribe_thread = threading.Thread(target=transcribe_stream)
    transcribe_thread.start()
    transcribe_thread.join()