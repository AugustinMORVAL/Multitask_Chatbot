import os
from dotenv import load_dotenv
import streamlit as st
from app import ChatbotManager, UIComponents, PDFManager
from config import load_config

# Load environment
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
config = load_config()

chatbot_manager = ChatbotManager(GROQ_API_KEY, config['models'])
pdf_manager = PDFManager()
ui = UIComponents()

# UI Setup
st.logo("img/logo-Cyy6uKYt.png")
st.title("ChatBot")
st.markdown("Nice to see you again!")

# Sidebar
model, system_prompt, temperature, max_tokens, reset_conversation, parameters = ui.create_sidebar(config)

# Upload file
uploaded_file, _ = ui.create_file_uploader()

if uploaded_file:
    pdf_manager.process_pdf(uploaded_file)
    st.success(f"Processed PDF: {uploaded_file.name}")

# Chat Interface
ui.create_chat_interface(chatbot_manager, pdf_manager, model, system_prompt, temperature, max_tokens, reset_conversation, parameters)
