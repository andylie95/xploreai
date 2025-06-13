import streamlit as st
import requests
import os
import uuid
import subprocess

# 👇 REPLACE with your actual Azure credentials
AZURE_SPEECH_KEY = "BRRbY8UCM2yzJWOE6ASgfthbGU7RRS9cWmjtJVCP6iOPcBkmR8bQJQQJ99BFACqBBLyXJ3w3AAAYACOGJGiM"
AZURE_REGION = "southeastasia"  # e.g., "southeastasia"

# Function to transcribe audio using Azure STT
def transcribe_audio(file_path):
    endpoint = f"https://{AZURE_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000"
    }
    params = {"language": "en-US"}

    with open(file_path, "rb") as audio_file:
        response = requests.post(endpoint, headers=headers, params=params, data=audio_file)

    try:
        result = response.json()
        return result.get("DisplayText", "❌ Transcription failed or unclear audio.")
    except Exception:
        return "❌ Could not parse the response. Check API key or audio format."

# Function to convert uploaded MP3/WAV to standard mono 16kHz WAV
def convert_audio_to_wav(uploaded_file):
    temp_input = f"input_{uuid.uuid4()}.mp3"
    temp_output = f"output_{uuid.uuid4()}.wav"

    with open(temp_input, "wb") as f:
        f.write(uploaded_file.read())

    # Use ffmpeg to convert audio to mono WAV at 16kHz
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_input,
        "-ac", "1", "-ar", "16000", temp_output
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(temp_input)
    return temp_output

# Streamlit UI
st.set_page_config(page_title="Meeting Transcriber", page_icon="📝")
st.title("📝 XploreAI – Azure Meeting Transcriber")
st.write("Upload a meeting audio file (MP3 or WAV) and get the transcription using Azure Speech-to-Text.")

uploaded_file = st.file_uploader("🎙️ Choose a meeting audio file", type=["mp3", "wav"])

if uploaded_file:
    st.audio(uploaded_file, format='audio/mp3')

    if st.button("Transcribe"):
        with st.spinner("Transcribing with Azure Speech Service..."):
            wav_path = convert_audio_to_wav(uploaded_file)
            transcript = transcribe_audio(wav_path)
            os.remove(wav_path)

        st.subheader("📄 Transcription Result")
        st.success(transcript)
