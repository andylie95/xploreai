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

    with open(file_path, "rb") as audio_file:
        response = requests.post(endpoint, headers=headers, params=params, data=audio_file)

    try:
        result = response.json()
        return result.get("DisplayText", "❌ Transcription failed or unclear audio.")
