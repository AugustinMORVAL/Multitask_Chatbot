import streamlit as st
from app import ChatbotManager, UIComponents
from config import load_config
import os
from dotenv import load_dotenv

load_dotenv()

# Add this line after load_dotenv()
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

# Sidebar
with st.sidebar:
    st.logo("img/logo.png")
    st.title("Chat Settings")
    api_keys = ui.enter_api_key()
    st.subheader("Model")
    model = st.selectbox("Select a model", config['models'])
    st.subheader("**Database**")
    external_database = ui.create_database_connection()

# Main content
chatbot_manager = ChatbotManager(api_keys=api_keys, model=model, config=config, db_path=external_database)
ui.create_chat_interface(chatbot_manager)
