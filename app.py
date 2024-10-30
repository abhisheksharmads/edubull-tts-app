import os
import streamlit as st
import requests
from pathlib import Path
import uuid

# Determine the absolute path of the logo
logo_path = Path("edubull-icon.png").resolve()

# Check if the file exists at that path
if logo_path.is_file():
    st.image(str(logo_path), width=100)  # Display the logo if found
else:
    st.warning("Logo image not found at the specified path.")

# Access the OpenAI API key from Streamlit Secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Define the directory to save the generated MP3 file
# Use the current working directory for deployment compatibility
save_directory = Path("audio_files")
save_directory.mkdir(parents=True, exist_ok=True)

def generate_speech(text, model="tts-1", voice="alloy"):
    """
    Makes a direct REST API call to OpenAI's TTS API to generate speech.
    Generates a unique filename for each request.
    """
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "voice": voice,
        "input": text
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    # Generate a unique filename
    unique_filename = f"speech_{uuid.uuid4().hex}.mp3"
    file_path = save_directory / unique_filename

    # Check if the response is in audio format
    if response.headers.get('Content-Type', '').startswith('audio'):
        with open(file_path, "wb") as audio_file:
            for chunk in response.iter_content(chunk_size=8192):
                audio_file.write(chunk)
        return file_path
    else:
        st.error("The response is not in MP3 format.")
        st.write("Response details:", response.text)  # Debugging information
        return None

# Streamlit App Layout
st.title("EduBull's Text-to-Speech Generator")
st.write("Enter your text prompt below to generate speech using OpenAI's TTS API.")

# Text input
prompt = st.text_area("Enter Prompt", "The quick brown fox jumped over the lazy dog.")

# Model and Voice options
model = st.selectbox("Select Model", ["tts-1", "tts-1-hd"])
voice = st.selectbox("Select Voice", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])

# Generate button
if st.button("Generate Audio"):
    if prompt.strip():
        with st.spinner("Generating audio..."):
            audio_path = generate_speech(prompt, model=model, voice=voice)
            if audio_path:
                st.success("Audio generated successfully!")
                
                # Play the audio file
                with open(audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3")
                
                # Provide a download button with the unique filename
                st.download_button(
                    label="Download MP3",
                    data=audio_bytes,
                    file_name=audio_path.name,
                    mime="audio/mpeg"
                )
    else:
        st.warning("Please enter a valid prompt.")
