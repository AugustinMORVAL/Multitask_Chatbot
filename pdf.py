import streamlit as st
import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
import time

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

models = {
    "Gemma Model 2 - 9B": "gemma2-9b-it",
    "Gemma Model - 7B": "gemma-7b-it",
    # "LLaMA 3.1 - 70B": "llama-3.1-70b-versatile",
    # "LLaMA 3.1 - 8B": "llama-3.1-8b-instant",
    "LLaMA 3 - 70B": "llama3-70b-8192",
    "LLaMA 3 - 8B": "llama3-8b-8192",
    "Mixtral - 8x7B": "mixtral-8x7b-32768",
    "Whisper Large V3": "whisper-large-v3"
}

llm = ChatGroq(model_name=models["Gemma Model 2 - 9B"], temperature=0.1, api_key=GROQ_API_KEY)

def load_file(file):
    with st.spinner("Loading and processing the file..."): 
        try:
            pdf_reader = PdfReader(file)
            formatted_document = ""
            for page in pdf_reader.pages:
                formatted_document += page.extract_text()

            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(formatted_document)

            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

            store = FAISS.from_texts(chunks, embeddings)

            return store
        except PdfReadError:
            raise ValueError("The uploaded file is not a valid PDF.")
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")

def get_response(model, store, query):
    if not isinstance(store, FAISS):
        raise st.error("The 'store' variable must be an instance of the FAISS class.")
    
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=store.as_retriever())
    response = qa.invoke(query)
    return response
    
st.title("PDF Chatbot")
model = st.selectbox("Select a model:", list(models.keys()), key="selected_model")
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
reset_conversation = st.button("Reset Conversation")

# Initialize a history for the chat
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = None

# Reset conversation history when the button is clicked
if reset_conversation:
    st.session_state.messages = []

if uploaded_file is not None:

    st.session_state.context = load_file(uploaded_file)
    st.session_state.messages.append({"role": "system", "content": st.session_state.context})

    # Display chat messages from history when the application is restarted
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Get user prompt
    if prompt := st.chat_input("Ask me anything about the file"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        answer = get_response(model, st.session_state.context, prompt)["result"]

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
