import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
import base64
import time

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def transcript_audio(file):
    with st.spinner('Writing transcript...'):
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3"
        )
        return transcription.text

# Sidebar section
st.sidebar.title("Powered by AIugustin")
# st.sidebar.markdown('"Le plus fort de tous les hommes !" (derrière Vincent...)')
# st.sidebar.image("img/IMG_20230618_142903_268.jpg")
model = st.sidebar.selectbox("Select a model", options=['gemma2-9b-it', 'gemma-7b-it', 'llama3-70b-8192', 'llama3-8b-8192', 'llama3-groq-70b-8192-tool-use-preview', 'llama3-groq-8b-8192-tool-use-preview', 'mixtral-8x7b-32768'])
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

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
            st.session_state.transcript = transcript_audio(uploaded_file)
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