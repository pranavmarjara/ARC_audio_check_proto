# Hindi Speech Intelligibility Test

A grammar-constrained Hindi speech intelligibility scoring system using Vosk (Kaldi backend).

## How it works
- Phonetically balanced Hindi word list
- Automatic speech recognition
- Compares spoken vs expected words
- Produces a Z-score (0–100)

## Run locally
1. Install Python deps:
   pip install vosk jiwer

2. Download model:
   https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip

3. Convert audio to 16kHz mono wav

4. Run:
   python score_z.py

## Download Hindi ASR Model
Download and extract inside the project folder:

https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip

After extracting, you should have:

vosk-model-small-hi-0.22/   

## Example Output

===== SESSION RESULT =====
Words tested : 15
Correct      : 15
Session Z score : 100.00
