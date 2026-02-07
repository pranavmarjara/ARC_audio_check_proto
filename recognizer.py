import wave
import json
import os
from vosk import Model, KaldiRecognizer

# ---- Lazy load model (critical for Streamlit) ----
_model = None

def get_model():
    global _model
    if _model is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-hi-0.22")
        _model = Model(MODEL_PATH)
    return _model


def recognize_audio(file_path, grammar_words):
    model = get_model()

    wf = wave.open(file_path, "rb")
    rec = KaldiRecognizer(model, 16000, json.dumps(grammar_words))
    rec.SetWords(True)

    result_text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_text += res.get("text", "") + " "

    final = json.loads(rec.FinalResult())
    result_text += final.get("text", "")

    return result_text.strip()
