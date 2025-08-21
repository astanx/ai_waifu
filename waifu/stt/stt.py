from faster_whisper import WhisperModel
import os
import speech_recognition as sr
from . import config

def stt():
    r = sr.Recognizer()
    r.pause_threshold = 0.8   # seconds of silence before stopping listening
    r.energy_threshold = 300  # adjust if background noise is high

    with sr.Microphone() as source:
        print("Speak now (will stop after a pause)...")
        audio = r.listen(source)  # listens until pause

        # Save audio to file
        with open(config.audio_path, "wb") as f:
            f.write(audio.get_wav_data())
    # Run on CPU with INT8
    model = WhisperModel(config.model_size, device="cpu", compute_type="int8")

    # or run on GPU with FP16
    #model = WhisperModel(model_size, device="cuda", compute_type="float16")
    # or run on GPU with INT8
    # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")


    segments, info = model.transcribe(config.audio_path, beam_size=5)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    text = " ".join([segment.text for segment in segments])
    
    print(f"Transcribed text: {text}")

    os.remove(config.audio_path)
    return text