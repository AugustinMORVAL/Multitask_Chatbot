import streamlit as st
from app import ChatbotManager, UIComponents, DocumentProcessor
from config import load_config
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = "true"

st.set_page_config(
    page_title="Chat with Groq",
    page_icon="img/logo.png",
    initial_sidebar_state="expanded"
)
st.title("💬 Chat with Groq")
# Load configuration
config = load_config()

# Initialize components
ui = UIComponents(config)
processor = DocumentProcessor()

# Sidebar
with st.sidebar:
    st.logo("img/logo.png")
    st.title("Chat Settings")
    api_keys = ui.enter_api_key()
    st.subheader("Model")
    model = st.selectbox("Select a model", config['models'])
    st.subheader("**Database**")
    external_database = ui.create_database_connection()
    database_details = ui.create_database_details()

# Page content
upload_destination = st.radio(
    "Choose where to store your documents:",
    options=["Local Storage", "Connected Database"],
    disabled=not st.session_state.external_database,
    help="Store documents locally for temporary use, or in the connected database for persistence"
)

if upload_destination == "Local Storage":
    local_uploaded_files = ui.create_file_uploader("Upload documents to local storage")
else:
    if st.session_state.external_database:
        external_uploaded_files = ui.create_file_uploader("Upload documents to database")
    else:
        st.warning("Please connect to a database first to upload files there.")

chatbot_manager = ChatbotManager(api_keys=api_keys, model=model, config=config)
ui.create_chat_interface(chatbot_manager)
