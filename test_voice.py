from voice_input import record_audio, transcribe_audio

file = record_audio()
text = transcribe_audio(file)

print("You said:", text)
