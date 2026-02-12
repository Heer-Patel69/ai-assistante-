import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

MODEL_SIZE = "base"   # perfect for 8GB RAM

model = WhisperModel(MODEL_SIZE, compute_type="int8")


def record_audio(filename="voice.wav", duration=5, fs=16000):
    print("🎙️ Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, recording)
    print("✅ Recording complete.")
    return filename


def transcribe_audio(file):
    segments, _ = model.transcribe(file)

    text = ""
    for segment in segments:
        text += segment.text

    return text.strip()
