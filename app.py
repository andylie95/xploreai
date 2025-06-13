import streamlit as st
import requests
import os
import uuid

# Replace with your Azure credentials
AZURE_SPEECH_KEY = "BRRbY8UCM2yzJWOE6ASgfthbGU7RRS9cWmjtJVCP6iOPcBkmR8bQJQQJ99BFACqBBLyXJ3w3AAAYACOGJGiM"
AZURE_REGION = "southeastasia"  # e.g., "southeastasia"

# Transcribe audio using Azure Speech-to-Text
def transcribe_audio(file_path):
    endpoint = f"https://{AZURE_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000"
    }
    params = {"language": "en-US"}

    try:
        with open(file_path, "rb") as audio_file:
            response = requests.post(endpoint, headers=headers, params=params, data=audio_file)
            result = response.json()
            return result.get("DisplayText", "❌ Transcription failed or unclear audio.")
    except Exception as e:
        return f"❌ Error occurred: {str(e)}"

# Streamlit App UI
st.set_page_config(page_title="Meeting Transcriber", page_icon="📝")
st.title("📝 XploreAI – Azure Meeting Transcriber")
st.write("Upload a **WAV file (mono, 16kHz)** and get a real-time transcript using Azure Speech-to-Text.")

uploaded_file = st.file_uploader("🎙️ Upload WAV audio", type=["wav"])

if uploaded_file:
    st.audio(uploaded_file, format='audio/wav')

    if st.button("Transcribe"):
        with st.spinner("⏳ Transcribing with Azure Speech Service..."):
            temp_filename = f"temp_{uuid.uuid4()}.wav"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.read())

            transcript = transcribe_audio(temp_filename)
            os.remove(temp_filename)

        st.subheader("📄 Transcription Result")
        st.success(transcript)
