import json
import csv
import wave
import os
from vosk import Model, KaldiRecognizer

print("SCRIPT STARTED")

MODEL_PATH = "vosk-model-small-hi-0.22"
AUDIO_DIR = "audio_16k"
REFERENCE_FILE = "references.csv"
SAMPLE_RATE = 16000

# Load grammar
with open("wordlist.txt", encoding="utf-8") as f:
    words = [w.strip() for w in f if w.strip()]

grammar = json.dumps(words, ensure_ascii=False)

print("Loading model...")
model = Model(MODEL_PATH)
print("Model loaded")

total = 0
correct = 0

with open(REFERENCE_FILE, encoding="utf-8") as ref:
    reader = csv.reader(ref)
    for wav_file, expected in reader:
        path = os.path.join(AUDIO_DIR, wav_file)

        print(f"\nProcessing {wav_file}")

        wf = wave.open(path, "rb")
        rec = KaldiRecognizer(model, SAMPLE_RATE, grammar)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())
        recognized = result.get("text", "").strip()

        print(f"Expected: {expected} | Got: {recognized}")

        total += 1
        if recognized == expected:
            correct += 1

print("\n===== SESSION RESULT =====")
print(f"Words tested : {total}")
print(f"Correct      : {correct}")
print(f"Session Z score : {(correct/total)*100:.2f}")
