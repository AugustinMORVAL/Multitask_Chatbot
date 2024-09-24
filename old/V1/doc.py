import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
import time
import PyPDF2
import fitz
from PIL import Image

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

client = Groq(api_key=GROQ_API_KEY)
    
def chatbot_response(model, messages, temperature):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content

def display_pdfs(uploaded_files):
    preview = []
    doc = fitz.open(stream=uploaded_files.read(), filetype="pdf")
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        preview.append(img)
    return preview

st.logo("img/logo-Cyy6uKYt.png")
uploaded_files = st.file_uploader(label="Upload your file", type = ["pdf"])

# Sidebar section
st.sidebar.title("Powered by AIugustin")
model = st.sidebar.selectbox("Select a model", options=['gemma2-9b-it', 'gemma-7b-it', 'llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768'])
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1, help="Controls the randomness of the model's responses. A value of 0 means that the model will always choose the most likely response, while a value of 1 means that the model will choose a response randomly from the distribution of possible responses.")
reset_conversation = st.sidebar.button("Reset Conversation")

if uploaded_files is not None:

    files = display_pdfs(uploaded_files)

    st.sidebar.title("Uploaded File")
    for file in files:
        st.sidebar.image(file, use_column_width=True)

        pdf_file = PyPDF2.PdfReader(uploaded_files)
        text = ""
        for page in pdf_file.pages:
            text += page.extract_text()

    st.sidebar.title("Uploaded File")
    for file in files:
        st.sidebar.image(file, use_column_width=True)

    # Reset conversation history when the button is clicked
    if reset_conversation:
        st.session_state.messages = []

    st.title("ChatBot")
    st.markdown("Nice to see you again!")

    # Initialize a history for the chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "context" not in st.session_state:
        st.session_state.context = None

    # Display chat messages from history when the application is restarted
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Give context to the chatbot
    system_prompt_content = """
    You are a helpful assistant that analyzes Pdf files.
    You will be provided with a text extracted from the pdf file. You need to understand the content of the text and answer questions about it.
    Here is the text extracted from the pdf file:
    """ + text
    st.session_state.messages.append({"role": "system", "content": system_prompt_content})

    # Get user prompt
    if prompt := st.chat_input("Ask me anything about the file"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        answer = chatbot_response(model, st.session_state.messages, temperature)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            # Simulate stream of response with milliseconds delay
            for chunk in answer:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.005)
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})