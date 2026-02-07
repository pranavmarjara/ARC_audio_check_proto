import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import sounddevice as sd
import soundfile as sf
import json
import uuid
import wave
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
from recognizer import recognize_audio


def record_audio(duration=3, fs=16000):
    sd.default.samplerate = fs
    sd.default.channels = 1
    sd.default.dtype = 'int16'

    # FORCE WSL MICROPHONE
    sd.default.device = 2  # RDPSource index from pactl

    audio = sd.rec(int(duration * fs))
    sd.wait()
    return audio.flatten()
st.set_page_config(layout="wide")

# ---------- DARK THEME ----------
st.markdown("""
<style>
.stApp { background:#0e0f11; color:#f5f5f5; }
.bigword { font-size:80px; text-align:center; margin-top:60px; margin-bottom:60px; }
.stButton>button {
    height:70px;
    font-size:20px;
    background:#1c1d21;
    color:white;
    border-radius:12px;
    border:1px solid #3a3a3a;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOAD WORDS ----------
with open("word_list.json","r",encoding="utf-8") as f:
    WORDS=json.load(f)

if "index" not in st.session_state:
    st.session_state.index=0
    st.session_state.correct=0
    st.session_state.results=[]
    st.session_state.audio_bytes=None

# ---------- FINISHED ----------
if st.session_state.index>=len(WORDS):
    total=len(WORDS)
    correct=st.session_state.correct
    wer=1-(correct/total)
    z=100-(wer*100)

    st.title("Session Complete")
    st.write(f"Z score: {z:.2f}")
    st.stop()

word=WORDS[st.session_state.index]
st.markdown(f"<div class='bigword'>{word}</div>",unsafe_allow_html=True)

# ---------- AUDIO RECEIVER ----------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames=[]

    def recv_audio(self,frame):
        self.frames.append(frame.to_ndarray())
        return frame

ctx=webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio":True,"video":False},
)

# ---------- SAVE RECORDING ----------
if st.button("Accept & Next"):

    if ctx.audio_processor and len(ctx.audio_processor.frames) > 0:

        import numpy as np
        import wave

        # ---- freeze audio buffer ----
        audio_frames = ctx.audio_processor.frames.copy()
        ctx.audio_processor.frames.clear()

        audio = np.concatenate(audio_frames, axis=0)
        import librosa

        # resample 48k → 16k for Vosk
        audio = librosa.resample(audio.astype(float), orig_sr=48000, target_sr=16000)
        audio = audio.astype("int16")
        filename = f"recordings/{uuid.uuid4()}.wav"

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(audio.tobytes())

        predicted = recognize_audio(filename, WORDS)

        if predicted == word:
            st.session_state.correct += 1

        st.session_state.results.append({
            "expected": word,
            "predicted": predicted
        })

        st.session_state.index += 1
        st.rerun()

    else:
        st.warning("No audio captured — speak before pressing Accept")
