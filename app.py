import streamlit as st
import requests
import os
import uuid
import datetime

# === Azure Credentials ===
AZURE_SPEECH_KEY = "BRRbY8UCM2yzJWOE6ASgfthbGU7RRS9cWmjtJVCP6iOPcBkmR8bQJQQJ99BFACqBBLyXJ3w3AAAYACOGJGiM"
AZURE_SPEECH_REGION = "southeastasia"
AZURE_TRANSLATOR_KEY = "8770f1a53459427d897f18904336bf9b"
AZURE_TRANSLATOR_REGION = "southeastasia"

# === Transcribe Function ===
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
            return result.get("DisplayText", "❌ Transcription failed or unclear audio. / Transkripsi gagal atau audio tidak jelas.")
    except Exception as e:
        return f"❌ Transcription error: {str(e)}"

# === Translate Function ===
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

# === Page Setup ===
st.set_page_config(page_title="Xplore AI Meeting Transcribe", page_icon="🎤")
st.title("🎤 Xplore AI Meeting Transcribe")
st.markdown("""
**Upload your meeting audio and choose your output format.**  
Unggah rekaman rapat Anda dan pilih format hasil yang diinginkan.
""")

# === File Upload ===
uploaded_file = st.file_uploader(
    "📤 Upload a `.wav` file (16kHz mono recommended) / Unggah file `.wav` (disarankan 16kHz mono)",
    type=["wav"]
)

if uploaded_file:
    st.audio(uploaded_file, format='audio/wav')

    st.markdown("### 🔧 Choose Option / Pilih Opsi")

    col1, col2 = st.columns(2)
    with col1:
        transcribe_button = st.button("📝 Transcribe (English Only) / Hanya Bahasa Inggris")
    with col2:
        translate_button = st.button("🌐 Transcribe + Translate to Indonesian / Terjemahkan ke Bahasa Indonesia")

    if transcribe_button or translate_button:
        with st.spinner("⏳ Processing... / Sedang diproses..."):
            temp_filename = f"temp_{uuid.uuid4()}.wav"
            with open(temp_filename, "wb") as f:
                f.write(uploaded_file.read())

            transcript = transcribe_audio(temp_filename)
            translation = translate_text(transcript) if translate_button else ""
            os.remove(temp_filename)

            st.session_state.chat_history.append({
                "transcript": transcript,
                "translation": translation,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })

# === Display Chat History ===
if st.session_state.chat_history:
    st.divider()
    st.subheader("💬 Transcript Log / Riwayat Transkrip")

    for msg in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(f"**🕒 {msg['timestamp']}**")
            st.markdown(f"**🗣️ English:** {msg['transcript']}")
            if msg["translation"]:
                st.markdown(f"**🌐 Indonesian:** {msg['translation']}")

    # === Export Option ===
    st.divider()
    full_text = ""
    for msg in st.session_state.chat_history:
        full_text += f"[{msg['timestamp']}]\nEN: {msg['transcript']}\n"
        if msg["translation"]:
            full_text += f"ID: {msg['translation']}\n"
        full_text += "\n"

    filename = f"xploreai_transcript_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    st.download_button(
        "📄 Download Transcript as .txt / Unduh Hasil sebagai .txt",
        full_text,
        file_name=filename,
        mime="text/plain"
    )
