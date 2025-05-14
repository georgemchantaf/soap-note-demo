import streamlit as st
from openai import OpenAI
import tempfile
import os
from streamlit_mic_recorder import mic_recorder

# === 🔐 Password Gate ===
st.set_page_config(page_title="AI SOAP Assistant", layout="wide")
st.title("🔐 AI SOAP Assistant - Physician Access")

password = st.text_input("Enter password to access the app", type="password")
if password != st.secrets["ACCESS_CODE"]:
    st.warning("Access restricted. Please enter the correct password.")
    st.stop()

# === ✅ OpenAI Client Setup ===
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === ✅ Transcription (Whisper) ===
def transcribe_openai(audio_path):
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    return transcript.text

# === ✅ SOAP Generation (GPT-4) ===
def generate_soap_openai(transcript):
    prompt = f"""
You are a medical documentation assistant in STRICT SCRIBE MODE.

- Generate a SOAP note based only on this transcript.
- Write it in English.
- Do NOT invent or infer anything not explicitly said.
- Use this format:

Subjective:
- Chief Complaint (CC):
- History of Present Illness (HPI):
- Past Medical History (PMH):

Objective:
- Allergies:
- Vital Signs:
- Physical Exam:
- Diagnostic Results:

Assessment:
- Primary Diagnosis:
- Differential Diagnoses:

Plan:
- Treatment:
- Medications Prescribed:
- Follow-up Instructions:

Transcript:
'''{transcript}'''
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

# === 🎙️ Audio Recorder ===
st.subheader("🎙️ Record Consultation Summary")
audio_bytes = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", use_container_width=True)

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes["bytes"])
        audio_path = tmp.name

    # Transcribe
    with st.spinner("Transcribing with Whisper API..."):
        try:
            transcript = transcribe_openai(audio_path)
            st.session_state["transcript"] = transcript
            st.success("✅ Transcription complete")
        except Exception:
            st.error("Transcription failed. Please try again later.")
        finally:
            os.unlink(audio_path)

# === ✍️ Transcript Box (Manual or Auto-filled) ===
st.subheader("📝 Transcript")
transcript_input = st.text_area("Transcribed Text", st.session_state.get("transcript", ""), height=250)

# === 🧠 Generate SOAP Note ===
if st.button("Generate SOAP Note"):
    with st.spinner("Generating SOAP note using GPT-4..."):
        try:
            soap_note = generate_soap_openai(transcript_input)
            st.session_state["soap_note"] = soap_note
            st.success("✅ SOAP note ready")
        except Exception:
            st.error("SOAP generation failed. Please try again later.")

# === 📄 SOAP Sections ===
if st.session_state.get("soap_note"):
    st.subheader("📄 Detailed SOAP Note (Review Each Field)")
    soap_fields = [
        "Chief Complaint (CC):",
        "History of Present Illness (HPI):",
        "Past Medical History (PMH):",
        "Allergies:",
        "Vital Signs:",
        "Physical Exam:",
        "Diagnostic Results:",
        "Primary Diagnosis:",
        "Differential Diagnoses:",
        "Treatment:",
        "Medications Prescribed:",
        "Follow-up Instructions:"
    ]

    for field in soap_fields:
        if field in st.session_state["soap_note"]:
            section = st.session_state["soap_note"].split(field)[1].split("\n")[0].strip()
            st.text_area(field.strip(" :"), section, height=100)
