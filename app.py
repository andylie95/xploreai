import streamlit as st
import requests
import os
import uuid
import tempfile
import datetime

# === Azure Credentials ===
AZURE_SPEECH_KEY = "BRRbY8UCM2yzJWOE6ASgfthbGU7RRS9cWmjtJVCP6iOPcBkmR8bQJQQJ99BFACqBBLyXJ3w3AAAYACOGJGiM"
AZURE_SPEECH_REGION = "southeastasia"
AZURE_TRANSLATOR_KEY = "8770f1a53459427d897f18904336bf9b"
AZURE_TRANSLATOR_REGION = "southeastasia"

# === STT Function ===
def transcribe_audio(file_path):
    endpoint = f"https://{AZURE_SPEECH_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
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
        return f"❌ Transcription error: {str(e)}"

# === Translation Function ===
def translate_text(text, target_lang="id"):
    url = f"https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to={target_lang}"
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-Type": "application/json"
    }
    body = [{"text": text}]

    try:
        response = requests.post(url, headers=headers, json=body)
        result = response.json()
        return result[0]["translations"][0]["text"]
    except Exception as e:
        return f"❌ Translation error: {str(e)}"

# === Initialize Session State ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === UI Layout ===
st.set_page_config(page_title="XploreAI Chat Transcriber", page_icon="💬")
st.title("💬 XploreAI – Chat-style Meeting Transcriber")
st.write("Upload or record short audio clips. Each clip becomes a message with transcript and translation.")

mode = st.radio("Input mode", ["Upload .wav", "Record from mic"])

if mode == "Upload .wav":
    uploaded_file = st.file_uploader("📤 Upload short .wav file", type=["wav"])
    if uploaded_file:
        st.audio(uploaded_file, format='audio/wav')
        if st.button("➕ Add to Chat"):
            with st.spinner("Processing..."):
                temp_filename = f"temp_{uuid.uuid4()}.wav"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.read())

                transcript = transcribe_audio(temp_filename)
                translation = translate_text(transcript)
                os.remove(temp_filename)

                st.session_state.chat_history.append({
                    "transcript": transcript,
                    "translation": translation,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })

elif mode == "Record from mic":
    audio_data = st.audio_recorder("🎙️ Record now", key="mic_rec")
    if audio_data is not None:
        st.audio(audio_data, format="audio/wav")
        if st.button("➕ Add to Chat (Mic)"):
            with st.spinner("Processing..."):
                temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_audio_file.write(audio_data.getvalue())
                temp_audio_file.close()

                transcript = transcribe_audio(temp_audio_file.name)
                translation = translate_text(transcript)
                os.remove(temp_audio_file.name)

                st.session_state.chat_history.append({
                    "transcript": transcript,
                    "translation": translation,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })

# === Display Chat History ===
st.divider()
st.subheader("🧾 Chat Log")

for msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(f"**🕒 {msg['timestamp']}**")
        st.markdown(f"**EN:** {msg['transcript']}")
        st.markdown(f"**ID:** {msg['translation']}")

# === Export Chat Log ===
if st.session_state.chat_history:
    full_text = ""
    for msg in st.session_state.chat_history:
        full_text += f"[{msg['timestamp']}]\nEN: {msg['transcript']}\nID: {msg['translation']}\n\n"

    filename = f"chat_transcript_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    st.download_button("📄 Download Full Chat Log", full_text, file_name=filename, mime="text/plain")
