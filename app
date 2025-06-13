import streamlit as st
import requests
import os
import uuid
from pydub import AudioSegment

# 👇 FILL IN YOUR OWN AZURE STT CREDENTIALS HERE
AZURE_SPEECH_KEY = "BRRbY8UCM2yzJWOE6ASgfthbGU7RRS9cWmjtJVCP6iOPcBkmR8bQJQQJ99BFACqBBLyXJ3w3AAAYACOGJGiM"        # example: "a6b7c8d9e0f1234567890abcd1234567f"
AZURE_REGION = "southeastasia"           # example: "southeastasia"

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
        return "❌ Could not read the response. Check your API key or file format."

def convert_audio_to_wav(uploaded_file):
    temp_input = f"input_{uuid.uuid4()}.mp3"
    temp_output = f"output_{uuid.uuid4()}.wav"
    with open(temp_input, "wb") as f:
        f.write(uploaded_file.read())

    sound = AudioSegment.from_file(temp_input)
    sound = sound.set_channels(1).set_frame_rate(16000)
    sound.export(temp_output, format="wav")
    os.remove(temp_input)

    return temp_output

# Streamlit UI
st.set_page_config(page_title="Meeting Transcriber", page_icon="📝")
st.title("📝 Azure Meeting Transcriber")
st.write("Upload a meeting audio file (MP3 or WAV) to get the transcription.")

uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav"])

if uploaded_file:
    st.audio(uploaded_file, format='audio/mp3')

    if st.button("Transcribe"):
        with st.spinner("Transcribing..."):
            wav_path = convert_audio_to_wav(uploaded_file)
            transcript = transcribe_audio(wav_path)
            os.remove(wav_path)

        st.subheader("📄 Transcription Result")
        st.success(transcript)
