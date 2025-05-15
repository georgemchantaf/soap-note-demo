import streamlit as st
from streamlit_mic_recorder import mic_recorder
import tempfile
import os

st.set_page_config(page_title="🎙️ Mic Test", layout="centered")
st.title("🎙️ iPhone Microphone Test")

st.markdown("Test if the microphone works properly on iPhone or Android **before using GPT**.")

# Record audio from mic
audio_bytes = mic_recorder(
    start_prompt="Start Recording",
    stop_prompt="Stop Recording",
    use_container_width=True
)

if audio_bytes:
    st.success("✅ Recording complete! Listen and download below:")

    # 1. Playback
    st.audio(audio_bytes["bytes"], format="audio/wav")

    # 2. Save audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes["bytes"])
        audio_path = tmp_file.name

    # 3. Download button
    with open(audio_path, "rb") as f:
        st.download_button("⬇️ Download WAV", f, file_name="iphone_mic_test.wav")

    st.info("If playback is short or silent, your device mic might be restricted.")
else:
    st.warning("🎙️ Waiting for input. Tap 'Start Recording' above.")
