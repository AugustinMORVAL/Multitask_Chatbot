import streamlit as st
from app import ChatbotManager, UIComponents, DocumentProcessor
from config import load_config
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize or reset session state variables."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.error_count = 0
        st.session_state.last_error = None
        st.session_state.successful_queries = 0
        st.session_state.chat_started = False

def load_configuration():
    """Load and validate configuration."""
    try:
        config = load_config()
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        st.error("⚠️ Failed to load application configuration. Please check the logs.")
        st.stop()

def setup_components(config):
    """Initialize application components."""
    try:
        ui = UIComponents(config)
        logger.info("UI components initialized")
        return ui
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        st.error("⚠️ Failed to initialize application components. Please refresh the page.")
        st.stop()

def main():
    """Main application entry point."""
    try:
        initialize_session_state()
        
        config = load_configuration()
        
        ui = setup_components(config)
        
        with st.sidebar:
            try:
                api_keys = ui.enter_api_key()
                
                st.title("🔌 **Database Connection**")
                external_database = ui.create_database_connection()
                database_details = ui.create_database_details()
            except Exception as e:
                logger.error(f"Sidebar setup error: {e}")
                st.error("⚠️ Failed to setup sidebar components.")
                return
        
        st.title("💬 Your personal AI assistant")
        st.markdown("Powered by Groq")
        
        try:
            chatbot_manager = ChatbotManager(api_keys=api_keys, config=config)
            ui.create_chat_interface(chatbot_manager)
            
            if not st.session_state.chat_started:
                st.session_state.chat_started = True
                logger.info("Chat interface initialized successfully")
                
        except Exception as e:
            logger.error(f"Chatbot initialization error: {e}")
            st.error("⚠️ Failed to initialize chatbot. Please check your API keys and try again.")
            st.session_state.error_count += 1
            st.session_state.last_error = str(e)
            if st.session_state.error_count >= 3:
                st.warning("⚠️ Multiple errors occurred. Please refresh the page or contact support.")
            st.stop()

    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("⚠️ An unexpected error occurred. Please refresh the page.")
        st.stop()

if __name__ == "__main__":
    main()
