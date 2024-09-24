import streamlit as st
from app import ChatbotManager, UIComponents
from config import load_config
# from pathlib import Path

# Set up Streamlit page
st.set_page_config(page_title="Chat with Groq", page_icon="🦜", layout="wide", initial_sidebar_state="expanded")

# Load configuration
config = load_config()

# Initialize components
# db_path = (Path(__file__).parent / "Chinook.db").absolute()
ui = UIComponents(config)
api_keys = ui.enter_api_key()
model = st.sidebar.selectbox("Select a model", config['models'])
chatbot_manager = ChatbotManager(api_keys=api_keys, model=model, config=config)

"# 🦜🔗 Chat with Groq"

# Create chat interface
ui.create_chat_interface(chatbot_manager)

# Clear chat history
ui.clear_chat_history()
