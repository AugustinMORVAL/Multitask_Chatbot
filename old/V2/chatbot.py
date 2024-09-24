import os
from dotenv import load_dotenv
import streamlit as st
from app import ChatbotManager, UIComponents, PDFManager
from config import load_config

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
config = load_config()

chatbot_manager = ChatbotManager(GROQ_API_KEY, config)
pdf_manager = PDFManager()
ui = UIComponents(config)

st.set_page_config(page_title="ChatBot", 
                   page_icon="img/logo-Cyy6uKYt.png",
                   layout="wide",
                   )

# UI Setup
st.logo("img/logo-Cyy6uKYt.png")
st.title("ChatBot")
st.markdown("Nice to see you again!")

# Sidebar
model, system_prompt, temperature, max_tokens, cot_reflection, show_cot_process, reset_conversation, parameters = ui.create_sidebar()

# Chat Interface
ui.create_chat_interface(chatbot_manager, pdf_manager, model, system_prompt, temperature, max_tokens, cot_reflection, show_cot_process, reset_conversation, parameters)
