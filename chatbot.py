import os
from dotenv import load_dotenv
import streamlit as st
from app import ChatbotManager, UIComponents, PDFManager
from config import load_config

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
config = load_config()

chatbot_manager = ChatbotManager(GROQ_API_KEY, config['models'])
pdf_manager = PDFManager()
ui = UIComponents(config)

# UI Setup
st.logo("img/logo-Cyy6uKYt.png")
st.title("ChatBot")
st.markdown("Nice to see you again!")

# Sidebar
model, system_prompt, temperature, max_tokens, reset_conversation, parameters = ui.create_sidebar()

# Upload file
files_uploaded = ui.create_file_uploader()

# Chat Interface
ui.create_chat_interface(chatbot_manager, pdf_manager, model, system_prompt, temperature, max_tokens, reset_conversation, parameters)
