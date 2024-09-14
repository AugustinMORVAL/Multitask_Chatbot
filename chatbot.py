import os
from dotenv import load_dotenv
import streamlit as st
from app import ChatbotManager, create_sidebar, create_chat_interface, create_file_uploader, PDFManager
from config import load_config

# Load environment
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
config = load_config()

chatbot_manager = ChatbotManager(GROQ_API_KEY, config['models'])
pdf_manager = PDFManager()

# UI Setup
st.logo("img/logo-Cyy6uKYt.png")
st.title("ChatBot")
st.markdown("Nice to see you again!")

# Sidebar
model, temperature, system_prompt, reset_conversation, parameters = create_sidebar(config)

# Upload file
uploaded_file, _ = create_file_uploader()

if uploaded_file:
    pdf_manager.process_pdf(uploaded_file)
    st.success(f"Processed PDF: {uploaded_file.name}")

# Chat Interface
create_chat_interface(chatbot_manager, pdf_manager, model, temperature, system_prompt, reset_conversation, parameters)
