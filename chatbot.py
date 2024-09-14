import os
from dotenv import load_dotenv
import streamlit as st
from app import ChatbotManager, create_sidebar, create_chat_interface
from config import load_config

# Load environment variables and configuration
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
config = load_config()

# Initialize ChatbotManager
chatbot_manager = ChatbotManager(GROQ_API_KEY, config['models'])

# UI Setup
st.logo("img/logo-Cyy6uKYt.png")
st.title("ChatBot")
st.markdown("Nice to see you again!")

# Sidebar
model, temperature, system_prompt, reset_conversation, parameters = create_sidebar(config)

# Chat Interface
create_chat_interface(chatbot_manager, model, temperature, system_prompt, reset_conversation, parameters)