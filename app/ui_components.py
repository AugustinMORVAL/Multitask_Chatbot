import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.runnables import RunnableConfig

class UIComponents:
    def __init__(self, config):
        self.config = config

    def enter_api_key(self):
        with st.sidebar.expander("Enter API Keys"):
            if "groq_api_key" in st.secrets:
                groq_api_key = st.secrets.groq_api_key
            else:
                groq_api_key = st.sidebar.text_input("Groq API Key", type="password")
                if not groq_api_key:
                    st.info("Enter a Groq API Key to continue")
                    st.stop()
            
            if "sarpapi_api_key" in st.secrets:
                sarpapi_api_key = st.secrets.sarpapi_api_key
            else:
                sarpapi_api_key = st.sidebar.text_input("SarpAPI Key", type="password", help="Enter your SerpAPI key to enable advanced web search tools")
            
            return {
                "groq_api_key": groq_api_key,
                "sarpapi_api_key": sarpapi_api_key
            }

    def create_chat_interface(self, chatbot_manager):
        output_container = st.empty()
        user_input = st.chat_input("Type your message here...")

        if user_input:
            output_container = output_container.container()
            output_container.chat_message("user").write(user_input)

            answer_container = output_container.chat_message("assistant", avatar="🦜")
            st_callback = StreamlitCallbackHandler(answer_container)
            cfg = RunnableConfig()
            cfg["callbacks"] = [st_callback]

            try:
                # Get the response and simulate the callback
                answer = chatbot_manager.get_response(user_input, cfg)
                answer_container.write(answer["output"])
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.stop()

    def clear_chat_history(self):
        if st.sidebar.button("Clear Chat History"):
            st.session_state.clear()
            st.sidebar.success("Chat history cleared!")

