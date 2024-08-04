import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
import base64
from pyannote.audio import Pipeline
import time
from pydub import AudioSegment

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

client = Groq(api_key=GROQ_API_KEY)
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN)

def transcript_audio(file, segments=None):
    with st.spinner('Writing transcript...'):
        if detect_speaker == "On":
            transcriptions = []
            for turn, _, speaker in segments:
                audio = AudioSegment.from_file(file)
                segment = audio[turn.start*1000:turn.end*1000]
                segmented_file = segment.export(format="wav")
                transcription = client.audio.transcriptions.create(
                    file=("file.wav", segmented_file.read()),
                    model="whisper-large-v3"
                )
                transcriptions.append((speaker, transcription.text))
            return "\n".join([f"{speaker}:\n {text}" for speaker, text in transcriptions])
        else:
            transcription = client.audio.transcriptions.create(
                file=file,
                model="whisper-large-v3"
            )
            return transcription.text

def diarization(uploaded_file):
    try:
        with st.spinner('Processing audio file...'):
            start_time = time.time()
            diarization = pipeline(uploaded_file)
            end_time = time.time()
            st.success(f'Audio file processed successfully in {end_time - start_time} seconds.')
    except Exception as e:
        st.error(f'Failed to process the audio file: {e}')
    segments = list(diarization.itertracks(yield_label=True))
    return segments

def chatbot_response(model, messages, temperature):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content

st.set_page_config(
    page_title="Audio Transcription",
    page_icon="🗎", 
    layout="centered"
)
st.logo("img/logo-Cyy6uKYt.png")
st.title("Audio Transcription")
st.markdown("Upload an audio file and click the **Transcript** button to see the transcription.")

# Sidebar section
st.sidebar.title("Powered by AIugustin")
st.sidebar.markdown('"Le plus fort de tous les hommes !" (derrière Vincent...)')
st.sidebar.image("img/IMG_20230618_142903_268.jpg")
model = st.sidebar.selectbox("Select a model", options=['gemma2-9b-it', 'gemma-7b-it', 'llama3-70b-8192', 'llama3-8b-8192', 'llama3-groq-70b-8192-tool-use-preview', 'llama3-groq-8b-8192-tool-use-preview', 'mixtral-8x7b-32768'])
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

# Options section
detect_speaker = st.radio("Speaker Detection", options=["On", "Off"], index=0)

# Main section
uploaded_file = st.file_uploader("Choose an audio file", type=["WAV", "MP3", "MP4", "M4A", "OGG", "OGA", "FLAC", "AAC", "WMA", "AMR"])

if uploaded_file is not None:
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "show_button" not in st.session_state:
        st.session_state.show_button = True
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if st.session_state.uploaded_file != uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.show_button = True
        st.session_state.transcript = None
        st.session_state.resume = None

    placeholder = st.empty()
    if st.session_state.show_button:
        if placeholder.button("Transcribe"):
            if detect_speaker == "On":
                segments = diarization(uploaded_file)
                st.write(segments)
            st.session_state.transcript = transcript_audio(uploaded_file, segments if detect_speaker == "On" else None)
            st.session_state.show_button = False
            placeholder.empty()   

    if st.session_state.show_button is False:
        if st.session_state.transcript is not None:
            if st.toggle('Show/Hide transcript', value=True):
                st.subheader("Transcript")
                st.markdown(st.session_state.transcript)
                # Download transcript button
                b64 = base64.b64encode(st.session_state.transcript.encode()).decode()
                href = f'<a href="data:file/txt;base64,{b64}" download="transcript.txt">Download Transcript</a>'
                st.markdown(href, unsafe_allow_html=True)

            if "resume" not in st.session_state:
                st.session_state.resume = None

            with st.form(key='analyze_form'):
                if not st.session_state.resume:
                    button_container = st.empty()
                    if button_container.form_submit_button("Analyze Transcript"):
                        system_prompt_content = """
                        You are a helpful assistant that analyzes and summarizes text.
                        You will be provided with a transcript of a conversation. Your task is to identify the main topics discussed, summarize the key points, and provide a brief analysis of the conversation.
                        Here is the transcript of the conversation:
                        """ + st.session_state.transcript
                        system_prompt = [{"role": "system", "content": system_prompt_content}]
                        with st.spinner('Analyzing transcript...'):
                            result = chatbot_response(model, system_prompt, temperature)
                        st.session_state.resume = result
                        button_container.empty()
                if st.session_state.resume:
                    st.markdown(st.session_state.resume)
                    if st.form_submit_button("Refresh"):
                        st.session_state.resume = None
                        st.session_state.messages = [] 
                        st.rerun()

            # Chatbot section
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Prompt to analyse audio transcription"):
                base = f'Here is the transcript that will serve as base for all your answers: {st.session_state.transcript}'
                st.session_state.messages.append({"role": "system", "content": base})
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                answer = chatbot_response(model, st.session_state.messages, temperature)
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    for chunk in answer:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                        time.sleep(0.005)
                    message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})